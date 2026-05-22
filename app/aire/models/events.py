# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from enum import Enum
from typing import Optional
from .content import AireContentMetadata
from .documents import AireDocumentSearchResult
from .questionnaire import AireQuestionnaireMetadata
from .keyword import AireKeyword
from .reminder import AireReminder

class AireEvent(str, Enum):
    """Chatbot event types"""
    Message = "message"
    Keywords = "keywords"
    TokenStats = "token-stats"
    Reminder = "reminder"
    Questionnaire = "questionnaire"
    ContentSuggestions = "content-suggestions"
    DocumentResults = "document-results"
    AgentSwitch = "agent-switch"
    Error = "error"
    End = "end"

class AireAgentSwitchEvent(BaseModel):
    """Agent switch event"""
    agent: str

class AireKeywordEvent(BaseModel):
    """Theme/keyword tagging event"""
    themes: list[AireKeyword]

class AireTokenStatsEvent(BaseModel):
    """Token statistics event"""
    total_tokens: Optional[int]
    input_tokens: Optional[int]
    output_tokens: Optional[int]

class AireReminderEvent(BaseModel):
    """Reminder event"""
    reminder: AireReminder

class AireQuestionnaireEvent(BaseModel):
    """Questionnaire event"""
    search: str
    results: list[AireQuestionnaireMetadata]

class AireContentEvent(BaseModel):
    """Content suggestions event"""
    search: str
    results: list[AireContentMetadata]

class AireDocumentResultEvent(BaseModel):
    """Document search event"""
    search: str
    results: list[AireDocumentSearchResult]
