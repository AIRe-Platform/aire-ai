from langserve.schema import CustomUserType
from langchain.schema.messages import ChatMessage
from pydantic import BaseModel
from .user import AireUser

class AireChatMessage(CustomUserType):
    """A chat meesage"""

    role: str
    content: str

class AireChatInput(CustomUserType):
    """This class containst the information about a chat"""

    chat: list[AireChatMessage]
    ui_lang: str | None

    def toChatMessages(cls) -> list[ChatMessage]:
        return list(map(lambda msg: ChatMessage(role=msg.role, content=msg.content), cls.chat))

class AireChatbotInfo(BaseModel):
    """Details a chatbot"""

    name: str
    description: str

class AireChatContext(CustomUserType):
    """The context for the chat"""

    input: AireChatInput
    user: AireUser | None

class AireChatAbstract(BaseModel):
    """Contains the abstract generated from chat messages."""
    
    summary: str
    keywords: list[str]
    