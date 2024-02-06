from langserve.schema import CustomUserType
from langchain.schema.messages import ChatMessage
from pydantic import BaseModel
from .user import AireUser
from .survey import AireSurveyAnswer

class AireChatMessage(CustomUserType):
    """A chat message"""

    role: str
    content: str
    timestamp: int | None
    survey_answer: AireSurveyAnswer | None


class AireChatInputContext(CustomUserType):
    """Additional chat context"""

    age: int | None
    occupation: str | None
    topic: str | None
    language: str | None


class AireChatInput(CustomUserType):
    """This class containst the information about a chat"""

    chat: list[AireChatMessage]
    context: AireChatInputContext | None

    def to_chat_messages(self) -> list[ChatMessage]:
        return list(map(lambda msg: ChatMessage(role=msg.role, content=msg.content), self.chat))


class AireChatbotInfo(BaseModel):
    """Details a chatbot"""

    name: str
    description: str


class AireChatContext(CustomUserType):
    """The context for the chat"""

    input: AireChatInput
    user: AireUser | None = None
    regen: bool = False


class AireChatAbstract(BaseModel):
    """Contains the abstract generated from chat messages."""

    summary: str
    keywords: list[str]
    
