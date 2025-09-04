# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langserve.schema import CustomUserType
from langchain_core.messages import ChatMessage
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Sequence
from .user import AireUser
from .documents import AireDocumentMetadata
from .questionnaire import AireQuestionnaireAnswer
from .platform import AirePlatformConfiguration
from .auth import AireAuth
from .keyword import AireKeyword

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
    DocumentResults = "document-results"
    End = "end"


class AireChatMessage(BaseModel):
    """A chat message"""
    role: str
    content: Optional[str] = None
    timestamp: Optional[int] = None
    rating: Optional[int] = None
    question: Optional[AireQuestionnaireAnswer] = None


class AireChatInputContext(BaseModel):
    """Additional chat context"""
    language: Optional[str] = None
    themes: Optional[list[AireKeyword]] = None
    documents: Optional[list[AireDocumentMetadata]] = None


class AireChatInput(BaseModel):
    """This class containst the information about a chat"""
    chat_id: Optional[str] = None
    chat: list[AireChatMessage]
    context: Optional[AireChatInputContext] = None

    def to_chat_messages(self) -> Sequence[ChatMessage]:
        messages = filter(lambda msg: msg.content != None, self.chat)
        return list(map(lambda msg: ChatMessage(role=msg.role, content=msg.content or ""), messages))
    
    def inject_system_message(self, content: str):
        message = AireChatMessage(role="system", content=content)
        self.chat.append(message)


class AireChatbotInfo(BaseModel):
    """Details a chatbot"""
    name: str
    description: str


class AireChatContext(CustomUserType):
    """The context for the chat"""
    input: AireChatInput
    user: Optional[AireUser] = None
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
    