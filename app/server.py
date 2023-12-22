import json
from typing import Annotated, AsyncIterator

from fastapi import FastAPI, Header
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
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.bot.default import DefaultBot
from aire.chains.chat_abstract import ChatAbstractChain
from aire.chains.chat_keywords import ChatKeywordChain
from aire.chains.chat_summary import ChatSummaryChain

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

@app.get("/api/bot", 
         description="List available bots",
         response_description="List of bots")
async def get_bots() -> list[AireChatbotInfo]:
    return [
        AireChatbotInfo(name="default", description="Default chat bot")
    ]

@app.post("/api/bot/{bot_name}/stream", 
          description="Stream completion",
          response_description="Returns a stream of events",
          response_class=Response)
async def stream_bot(bot_name: str, 
                     input: AireChatInput,
                     authorization: Annotated[str | None, Header()] = None):

    match bot_name:
        case "default":
            bot = DefaultBot
        case _:
            return Response(status_code=404)
        
    context = AireChatContext(input=input)
    print(f"Auth: {authorization}")
    
    try:
        if authorization != None:
            context.user = get_user(platform, authorization)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        return Response(status_code=401)

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
          description="Generate abstract from a chat",
          response_description="Returns the generated abstract")
async def chat_abstract(input: AireChatInput) -> AireChatAbstract:
    return ChatAbstractChain.invoke(input)

@app.post("/api/chat/summary", 
          description="Summarize chat",
          response_description="Returns the summary as a string")
async def chat_summary(input: AireChatInput) -> str:
    return ChatSummaryChain.invoke(input)

@app.post("/api/chat/keywords", 
          description="Pick keywords from a chat",
          response_description="Returns a list of keywords")
async def chat_keywords(input: AireChatInput) -> list[str]:
    return ChatKeywordChain.invoke(input)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
