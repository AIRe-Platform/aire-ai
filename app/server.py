import json, os
from typing import Annotated, AsyncIterator
from fastapi import (
    FastAPI, 
    Depends, 
    Header, 
    Query, 
    Body,
    UploadFile, 
    HTTPException, 
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response
from sse_starlette import EventSourceResponse;
from langserve.serialization import WellKnownLCSerializer
from aire.models.chat import (
    AireChatbotInfo, 
    AireChatInput,
    AireChatContext,
    AireChatAbstract
)
from aire.auth.jwt import verify_token
from aire.models.auth import AireAuth, AireScope
from aire.models.user import AireUser
from aire.models.survey import AireSurvey
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.services.memory import DocumentVectorStore, SurveyVectorStore
from aire.bot.default import DefaultBot
from aire.chains.chat_abstract import ChatAbstractChain
from aire.chains.chat_keywords import ChatKeywordChain
from aire.chains.chat_summary import ChatSummaryChain
from helpers.temp_files import create_temporary_file

app = FastAPI(
    root_path="/api",
    docs_url="/swagger/ui",
    openapi_url="/swagger.json"
)

def openapi_docs():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="AIRe AI Module",
        version="0.1.0",
        description="This is the documentation of the AIRe AI API.",
        openapi_version="3.0.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = openapi_docs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

serializer = WellKnownLCSerializer()
platform = get_platform_config()

UNAUTH_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authorization required",
    headers={"WWW-Authenticate": "Bearer"}
)
FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied"
)
BAD_REQUEST_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad request"
)
UNSUPPORTED_MEDIA_EXCEPTION = HTTPException(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    detail="Unsupported media type"
)
SERVICE_KEY = os.getenv("AIRE_SERVICE_KEY")

def check_service_key(aire_service_key: Annotated[str | None, Header()] = None):
    if SERVICE_KEY == None:
        raise RuntimeError("AIRE_SERVICE_KEY environment value is missing")
    return aire_service_key == SERVICE_KEY

def get_current_user(authorization: Annotated[str | None, Header()] = None):
    try:
        if authorization != None:
            return get_user(platform, authorization)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise FORBIDDEN_EXCEPTION
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise FORBIDDEN_EXCEPTION
    return


@app.get("/bot", 
         description="List available bots",
         tags=["Chatbot"],
         response_description="List of bots")
async def get_bots(auth: Annotated[AireAuth | None, Depends(verify_token)]) -> list[AireChatbotInfo]:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    return [
        AireChatbotInfo(name="default", description="Default chat bot")
    ]


@app.post("/bot/{bot_name}/stream", 
          description="Stream completion",
          tags=["Chatbot"],
          response_description="Returns a stream of events",
          response_class=Response)
async def stream_bot(bot_name: str, 
                     input: AireChatInput,
                     auth: Annotated[AireAuth | None, Depends(verify_token)],
                     user: Annotated[AireUser | None, Depends(get_current_user)]):
    
    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    match bot_name:
        case "default":
            bot = DefaultBot
        case _:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        
    context = AireChatContext(input=input, user=user)

    async def stream() -> AsyncIterator[dict]:
        try:
            iter = bot.astream(context)
            async for chunk in iter:
                yield {
                    "event": "data",
                    "data": serializer.dumps(chunk).decode("utf-8")
                }
            yield { "event": "end" }
        except BaseException as ex:
            print(f"Error: {ex}")
            yield {
                "event": "error",
                "data": json.dumps({ 
                    "status_code": 500, 
                    "message": "Internal Server Error"
                })
            }

    return EventSourceResponse(stream())


@app.post("/chat/abstract",
          name="Chat abstract (summary and keywords)",
          description="Generate abstract from a chat",
          tags=["Chat Processing"],
          response_description="Returns the generated abstract")
async def chat_abstract(
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]
    ) -> AireChatAbstract:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    context = AireChatContext(input=input)
    return ChatAbstractChain.invoke(context)


@app.post("/chat/summary", 
          description="Summarize chat",
          tags=["Chat Processing"],
          response_description="Returns the summary as a string")
async def chat_summary(
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]
    ) -> str:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    context = AireChatContext(input=input)
    return ChatSummaryChain.invoke(context)


@app.post("/chat/keywords", 
          description="Pick keywords from a chat",
          tags=["Chat Processing"],
          response_description="Returns a list of keywords")
async def chat_keywords(
    input: AireChatInput,              
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    regen: Annotated[bool, Query(
        description="Set to true if you wish to add randomness to the response"
        )] = False) -> list[str]:
    
    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    context = AireChatContext(input=input, regen=regen)
    return ChatKeywordChain.invoke(context)


@app.post("/embeddings/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Documents"])
async def embed_document(
    document: UploadFile,
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]) -> Response:

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentEmbedding in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    if document.size > 1024 * 16:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, 
                        content="The file is too large. The file must be 16 MB max.")
    
    store = DocumentVectorStore()
    
    if document.content_type == "application/pdf":
        handler = store.add_pdf
    elif document.content_type == "text/markdown":
        handler = store.add_markdown
    else:
        raise UNSUPPORTED_MEDIA_EXCEPTION
    
    path = None
    try:
        path = await create_temporary_file(document)
        if path == None:
            raise Exception("Failed to store uploaded file")
        handler(path)
        code = status.HTTP_204_NO_CONTENT
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
    finally:
        if path != None: path.unlink()

    return Response(status_code=code)


@app.post("/embeddings/survey",
          description="Create embeddings and store vectors in vector store",
          tags=["Surveys"])
async def embed_survey(
    survey: Annotated[AireSurvey, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.SurveyEmbedding in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = SurveyVectorStore()
    store.add_survey(survey)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/embeddings/survey",
         description="Query surveys",
         tags=["Embeddings"],
         response_description="Returns matching survey IDs in the order of relevance")
async def query_survey(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query()] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.SurveyQuery in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = SurveyVectorStore()
    store.query_keywords(query.split(","))

    # TODO: Return survey ID

    return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
