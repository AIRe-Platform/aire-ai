from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnableLambda
from models import AireChatbot
import default_bot

app = FastAPI(
    title="AIRe AI",
    version="0.1",
    description="AIRe AI Service Module"
)
model = ChatOpenAI(model="gpt-3.5-turbo")

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
    RunnableLambda(default_bot.runnable) | model, 
    path="/api/bot/default")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
