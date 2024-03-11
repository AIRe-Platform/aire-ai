import json, os
from pydantic import BaseModel
from typing import Annotated, AsyncIterator
from fastapi import (
    FastAPI, Depends, Header, Query, Body,
    UploadFile, HTTPException, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response
from sse_starlette import EventSourceResponse;
from langchain.schema.document import Document
from langchain.schema.messages import ChatMessage
from langserve.serialization import WellKnownLCSerializer
from aire.models.chat import (
    AireChatbotInfo, 
    AireChatInput,
    AireChatContext,
    AireChatAbstract,
    AireChatStats
)
from aire.auth import (
    AireAuth, AireScope,
    verify_token, check_service_key
)
from aire.models.user import AireUser
from aire.models.questionnaire import (
    AireQuestionnaire, 
    AireQuestionnaireProcessingRequest,
    AireQuestionnaireResult
)
from aire.models.document import AireDocumentMetadata
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.services.memory import DocumentVectorStore, QuestionnaireVectorStore
from aire.bot.default import DefaultBot, count_tokens
from aire.chains.chat_abstract import ChatAbstractChain
from aire.chains.chat_summary import ChatSummaryChain
from aire.chains.cbr_tagging import CbrTaggingChain
from aire.chains.questionnaire import ProcessQuestionnaireChain
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

class DocumentQueryResponse(BaseModel):
    documents: list[Document]

class QuestionnaireQueryResponse(BaseModel):
    results: list[AireDocumentMetadata]

class EmbedResponse(BaseModel):
    ids: list[str]

# Utilities
# ---------

def get_current_user(authorization: Annotated[str | None, Header()] = None):
    platform = get_platform_config()
    
    try:
        if authorization != None:
            return get_user(platform, authorization)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise FORBIDDEN_EXCEPTION
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise FORBIDDEN_EXCEPTION
    return


# Chat bot
# --------

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
    input_token_count = count_tokens(input)

    # Generate keywords list every 5 messages
    gen_keywords = (len(input.to_chat_messages()) % 5 == 0)

    async def stream() -> AsyncIterator[dict]:
        try:
            output = ""
            iter = bot.astream(context)
            async for chunk in iter:
                buffer = serializer.dumpd(chunk)
                yield {
                    "event": "message",
                    "data": serializer.dumps(chunk).decode("utf-8")
                }

                if(buffer["content"]):
                    output += buffer["content"]

            bot_message = ChatMessage(role="assistant", content=output)
            bot_input = AireChatInput(chat=[bot_message])
            output_token_count = count_tokens(bot_input)
            yield { 
                "event": "token-count",
                "data": output_token_count + input_token_count
            }

            if gen_keywords:
                keywords = await CbrTaggingChain.ainvoke(context)
                yield { 
                    "event": "keywords",
                    "data": serializer.dumps(keywords).decode("utf-8")
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


# Chat processing
# ---------------

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
    return CbrTaggingChain.invoke(context)


@app.post("/chat/{bot_name}/stats", 
         description="Get statistics for a chat",
         tags=["Chat Processing"],
         response_description="Returns token count")
async def chat_tokens(
    bot_name: str, 
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]) -> AireChatStats:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    match bot_name:
        case "default":
            return AireChatStats(token_count=count_tokens(input))
        case _:
            return Response(status_code=status.HTTP_404_NOT_FOUND)


# Document embeddings
# -------------------

@app.get("/embeddings/document",
         description="Find documents using similarity search",
         tags=["Documents"],
         response_model=DocumentQueryResponse)
async def query_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query(description="Query")] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = DocumentVectorStore()
    docs = store.similarity_search(query)
    return DocumentQueryResponse(documents=docs)


@app.post("/embeddings/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Documents"],
          response_model=EmbedResponse)
async def embed_document(
    document: UploadFile,
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]) -> Response:

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentWrite in auth.scopes:
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
    ids: list[str] | None = None

    try:
        path = await create_temporary_file(document)
        if path == None:
            raise Exception("Failed to store uploaded file")
        ids = handler(path)
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
    finally:
        if path != None: path.unlink()

    if ids != None:
        return EmbedResponse(ids=ids)
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.delete("/embeddings/document/{id}",
            description="Delete a document",
            tags=["Documents"])
async def delete_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    id: str):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentDelete in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = DocumentVectorStore()
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Questionnaire embeddings
# ------------------------

@app.post("/embeddings/questionnaire",
          description="Create a document of the questionnaire for keyword searches",
          tags=["Questionnaires"],
          response_description="Returns a document ID for the created embedding",
          response_model=EmbedResponse)
async def embed_survey(
    questionnaire: Annotated[AireQuestionnaire, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireWrite in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = QuestionnaireVectorStore()
    id = store.add_questionnaire(questionnaire)
    return EmbedResponse(ids=[id])


@app.get("/embeddings/questionnaire",
         description="Perform similarity search using keywords to find questionnaires",
         tags=["Questionnaires"],
         response_description="Returns matching questionnaire IDs in the order of relevance",
         response_model=QuestionnaireQueryResponse)
async def query_questionnaire(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query()] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = QuestionnaireVectorStore()
    results = store.query_keywords(query.split(","))
    return QuestionnaireQueryResponse(results=results)


@app.delete("/embeddings/questionnaire/{id}",
            description="Delete a questionnaire",
            tags=["Questionnaires"])
async def delete_survey(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    id: str):
    
    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireDelete in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    store = QuestionnaireVectorStore()
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Questionnaire processing
# ------------------------

@app.post("/questionnaire-results",
          description="Process questionnaire results",
          tags=["Questionnaires"])
async def process_questionnaire(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    results: Annotated[AireQuestionnaireProcessingRequest, Body()]
) -> AireQuestionnaireResult:
    
    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    return ProcessQuestionnaireChain.invoke(results)


# ---------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
