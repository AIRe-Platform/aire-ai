# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pydantic import BaseModel
from enum import Enum

class AireUserServiceCredentials(BaseModel):
    """Service credentials"""

    service_name: str
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
    year_of_birth: int | None
    language: str | None
    country: str | None
    bio: str | None
    connected_services: list[AireUserServiceCredentials] | None
    preferences: AireUserPreferences | None
    summary: str | None


class AireRole(str, Enum):
    """User roles"""

    User = "user"
    Admin = "admin"

