from enum import Enum
from pydantic import BaseModel
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

    ExperimentalCustomPrompt = "experimental-custom-prompt"


class AireAuth(BaseModel):
    """User token payload"""

    subject: str | None
    role: AireRole | str = AireRole.User
    scopes: list[str]
    user_key: str | None
    connected_services: list[AireUserServiceCredentials] | None
