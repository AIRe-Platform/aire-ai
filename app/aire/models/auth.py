# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from enum import Enum
from pydantic import BaseModel
from typing import Optional
from .user import AireRole, AireUserServiceCredentials

class AireScope(str, Enum):
    """Access scopes"""

    ChatCompletion = "chat-completion"
    ChatSummary = "chat-summary"
    ChatTokenCount = "chat-token-count"

    DocumentRead = "document-read"
    DocumentWrite = "document-write"
    DocumentDelete = "document-delete"

    QuestionnaireRead = "questionnaire-read"
    QuestionnaireWrite = "questionnaire-write"
    QuestionnaireDelete = "questionnaire-delete"

    ContentRead = "content-read",
    ContentWrite = "content-write",
    ContentDelete = "content-delete",

    EventRead = "event-read"
    EventWrite = "event-write"
    EventDelete = "event-delete"

    ExperimentalCustomPrompt = "experimental-custom-prompt"


class AireAuth(BaseModel):
    """User token payload"""

    subject: Optional[str] = None
    role: AireRole | str = AireRole.User
    scopes: list[str]
    user_key: Optional[str] = None
    connected_services: Optional[list[AireUserServiceCredentials]] = None
    token: Optional[str] = None
