from langserve.schema import CustomUserType
from pydantic import BaseModel
from .user import AireUser

class AireChatMessage(CustomUserType):
    role: str
    content: str

class AireChatInput(CustomUserType):
    chat: list[AireChatMessage]
    ui_lang: str | None

class AireChatbotInfo(BaseModel):
    name: str
    description: str

class AireChatContext(CustomUserType):
    input: AireChatInput
    user: AireUser | None
    