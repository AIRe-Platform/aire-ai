from enum import Enum
from pydantic import BaseModel
from .user import AireRole, AireUserServiceCredentials

class AireScope(str, Enum):
    """Access scopes"""

    ChatCompletion = "chat-completion"
    ChatSummary = "chat-summary"
    ChatEmbeddings = "chat-embeddings"
    ChatTokenCount = "chat-token-count"

AnonymousScopes = [AireScope.ChatCompletion, AireScope.ChatSummary]

class AireToken(BaseModel):
    """User token payload"""

    subject: str | None
    role: AireRole = AireRole.User
    scopes: list[str] = AnonymousScopes
    user_key: str | None
    connected_services: list[AireUserServiceCredentials] | None

