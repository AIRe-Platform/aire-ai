from enum import Enum
from pydantic import BaseModel
from .user import AireRole, AireUserServiceCredentials

class AireScope(str, Enum):
    """Access scopes"""

    ChatCompletion = "chat-completion"
    ChatSummary = "chat-summary"
    ChatTokenCount = "chat-token-count"
    DocumentEmbedding = "document-embedding"
    SurveyEmbedding = "survey-embedding"
    SurveyQuery = "survey-query"

class AireAuth(BaseModel):
    """User token payload"""

    subject: str | None
    role: AireRole = AireRole.User
    scopes: list[str]
    user_key: str | None
    connected_services: list[AireUserServiceCredentials] | None

