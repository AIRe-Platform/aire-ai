import json, os
from typing import Annotated, AsyncIterator

from fastapi import (
    FastAPI, 
    Depends, 
    Header, 
    Query, 
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
from aire.models.auth import AireToken, AireScope
from aire.models.user import AireUser
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.services.memory import store_pdf, store_markdown
from aire.bot.default import DefaultBot
from aire.chains.chat_abstract import ChatAbstractChain
from aire.chains.chat_keywords import ChatKeywordChain
from aire.chains.chat_summary import ChatSummaryChain
from helpers.temp_files import create_temporary_file

app = FastAPI(
    docs_url="/api/swagger/ui",
    openapi_url="/api/swagger.json"
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

async def get_current_user(authorization: Annotated[str | None, Header()] = None):
    no_user_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        if authorization != None:
            return get_user(platform, authorization)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise no_user_exception
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise no_user_exception
    return


@app.get("/api/bot", 
         description="List available bots",
         tags=["Chatbot"],
         response_description="List of bots")
async def get_bots(token: Annotated[AireToken, Depends(verify_token)]) -> list[AireChatbotInfo]:

    if not AireScope.ChatCompletion in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return [
        AireChatbotInfo(name="default", description="Default chat bot")
    ]


@app.post("/api/bot/{bot_name}/stream", 
          description="Stream completion",
          tags=["Chatbot"],
          response_description="Returns a stream of events",
          response_class=Response)
async def stream_bot(bot_name: str, 
                     input: AireChatInput,
                     token: Annotated[AireToken, Depends(verify_token)],
                     user: Annotated[AireUser | None, Depends(get_current_user)]):
    
    if not AireScope.ChatCompletion in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    match bot_name:
        case "default":
            bot = DefaultBot
        case _:
            return Response(status_code=404)
        
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


@app.post("/api/chat/abstract",
          name="Chat abstract (summary and keywords)",
          description="Generate abstract from a chat",
          tags=["Chat Processing"],
          response_description="Returns the generated abstract")
async def chat_abstract(
    input: AireChatInput,
    token: Annotated[AireToken, Depends(verify_token)]
    ) -> AireChatAbstract:

    if not AireScope.ChatSummary in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    context = AireChatContext(input=input)
    return ChatAbstractChain.invoke(context)


@app.post("/api/chat/summary", 
          description="Summarize chat",
          tags=["Chat Processing"],
          response_description="Returns the summary as a string")
async def chat_summary(
    input: AireChatInput,
    token: Annotated[AireToken, Depends(verify_token)]
    ) -> str:

    if not AireScope.ChatSummary in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    context = AireChatContext(input=input)
    return ChatSummaryChain.invoke(context)


@app.post("/api/chat/keywords", 
          description="Pick keywords from a chat",
          tags=["Chat Processing"],
          response_description="Returns a list of keywords")
async def chat_keywords(
    input: AireChatInput,              
    token: Annotated[AireToken, Depends(verify_token)],
    regen: Annotated[bool, Query(
        description="Set to true if you wish to add randomness to the response"
        )] = False) -> list[str]:
    
    if not AireScope.ChatSummary in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    context = AireChatContext(input=input, regen=regen)
    return ChatKeywordChain.invoke(context)


@app.post("/api/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Documents"])
async def embed_document(
    document: UploadFile,
    token: Annotated[AireToken, Depends(verify_token)]) -> Response:

    if not AireScope.ChatEmbeddings in token.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if document.size > 1024 * 16:
        return Response(status_code=400, 
                        content="The file is too large. The file must be 16 MB max.")
    
    if document.content_type == "application/pdf":
        handler = store_pdf
    elif document.content_type == "text/markdown":
        handler = store_markdown
    else:
       return Response(status_code=415, content="Unsupported file type")
    
    path = None
    try:
        path = await create_temporary_file(document)
        if path == None:
            raise Exception("Failed to store uploaded file")
        handler(path)
        status = 204
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
        status = 422
    finally:
        if path != None: path.unlink()

    return Response(status_code=status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
