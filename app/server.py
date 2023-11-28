from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from langserve import add_routes
from models import AireChatbot
from default_bot import DefaultBot

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

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/api/bot", description="List available bots")
async def get_bots() -> list[AireChatbot]:
    return [
        AireChatbot(name="default", description="Default chat bot")
    ]

add_routes(
    app, 
    DefaultBot, 
    path="/api/bot/default")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
