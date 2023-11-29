import json;
from typing import Annotated, AsyncIterator
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    RedirectResponse, 
    Response
)
from sse_starlette import EventSourceResponse;
from langserve.serialization import WellKnownLCSerializer
from aire.models.chat import (
    AireChatbotInfo, 
    AireChatInput,
    AireChatContext
)
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.bot.default import DefaultBot

app = FastAPI(
    title="AIRe AI",
    version="0.1",
    description="AIRe AI Service Module"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

serializer = WellKnownLCSerializer()
platform = get_platform_config()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/api/bot", description="List available bots")
async def get_bots() -> list[AireChatbotInfo]:
    return [
        AireChatbotInfo(name="default", description="Default chat bot")
    ]

@app.post("/api/bot/{bot_name}/stream", description="Stream completion")
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
        except BaseException:
            yield {
                "event": "error",
                "data": json.dumps({ 
                    "status_code": 500, 
                    "message": "Internal Server Error"
                })
            }

    return EventSourceResponse(stream())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
