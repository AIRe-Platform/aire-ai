# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langserve.schema import CustomUserType
from langchain_core.messages import ChatMessage
from pydantic import BaseModel
from enum import Enum
from .user import AireUser
from .questionnaire import AireQuestionnaireAnswer
from .platform import AirePlatformConfiguration
from .auth import AireAuth

class AireChatEvent(str, Enum):
    """Chatbot event types"""
    Message = "message"
    Error = "error"
    Metadata = "metadata"
    Keywords = "keywords"
    TokenCount = "token-count"
    Reminder = "reminder"
    Questionnaire = "questionnaire"
    ContentSuggestions = "content-suggestions"
    End = "end"


class AireChatMessage(BaseModel):
    """A chat message"""

    role: str
    content: str | None
    timestamp: int | None
    rating: int | None
    question: AireQuestionnaireAnswer | None


class AireChatInputContext(BaseModel):
    """Additional chat context"""

    year_of_birth: int | None
    occupation: str | None
    topic: str | None
    language: str | None
    keywords: list[str] | None


class AireChatInput(BaseModel):
    """This class containst the information about a chat"""

    chat_id: str | None
    chat: list[AireChatMessage]
    context: AireChatInputContext | None

    def to_chat_messages(self) -> list[ChatMessage]:
        messages = filter(lambda msg: msg.content != None, self.chat)
        return list(map(lambda msg: ChatMessage(role=msg.role, content=msg.content), messages))


class AireChatbotInfo(BaseModel):
    """Details a chatbot"""

    name: str
    description: str


class AireChatContext(CustomUserType):
    """The context for the chat"""

    input: AireChatInput
    user: AireUser | None = None
    regen: bool = False
    allow_custom_prompt: bool = False
    platform: AirePlatformConfiguration
    auth: AireAuth


class AireChatAbstract(BaseModel):
    """Contains the abstract generated from chat messages."""

    summary: str
    keywords: list[str]
    

class AireChatStats(BaseModel):
    """Contains statistics for a chat log"""

    token_count: int
    