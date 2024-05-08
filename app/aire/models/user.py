from pydantic import BaseModel
from enum import Enum

class AireUserServiceCredentials(BaseModel):
    """Service credentials"""

    name: str
    token: str


class AireUserGender(str, Enum):
    """Genders"""

    Male = "male"
    Female = "female"
    Other = "other"


class AireUserPreferences(BaseModel):
    """User preferences"""

    # Requires access scope 'experimental-custom-prompt' to apply
    experimental_custom_prompt: str | None


class AireUser(BaseModel):
    """User account details"""
    
    uuid: str
    email: str | None
    first_name: str | None
    last_name: str | None
    gender: AireUserGender | None
    age: int | None
    language: str | None
    country: str | None
    bio: str | None
    connected_services: list[AireUserServiceCredentials] | None
    preferences: AireUserPreferences | None


class AireRole(str, Enum):
    """User roles"""

    User = "user"
    Admin = "admin"

