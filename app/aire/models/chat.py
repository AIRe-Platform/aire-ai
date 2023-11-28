from langserve.schema import CustomUserType
from pydantic import BaseModel

class AireChatMessage(CustomUserType):
    name: str
    content: str

class AireChatInput(CustomUserType):
    chat: list[AireChatMessage]

class AireChatbotInfo(BaseModel):
    name: str
    description: str
