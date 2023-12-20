from langserve.schema import CustomUserType
from langchain.schema.messages import ChatMessage
from pydantic import BaseModel
from .user import AireUser

class AireChatMessage(CustomUserType):
    role: str
    content: str

class AireChatInput(CustomUserType):
    chat: list[AireChatMessage]
    ui_lang: str | None

    def toChatMessages(cls) -> list[ChatMessage]:
        return list(map(lambda msg: ChatMessage(role=msg.role, content=msg.content), cls.chat))

class AireChatbotInfo(BaseModel):
    name: str
    description: str

class AireChatContext(CustomUserType):
    input: AireChatInput
    user: AireUser | None

class AireChatSummary(BaseModel):
    summary: str
    keywords: list[str]
    