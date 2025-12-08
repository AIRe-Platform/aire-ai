# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from enum import Enum
from .content import AireContentMetadata
from .documents import AireDocumentSearchResult
from .questionnaire import AireQuestionnaireMetadata

class AireEvent(str, Enum):
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
    AgentSwitch = "agent-switch"
    End = "end"

class AireAgentSwitchEvent(BaseModel):
    """Agent switch event"""
    agent: str

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
