# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pydantic import BaseModel
from enum import Enum
from typing import Optional

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
    experimental_custom_prompt: Optional[str] = None


class AireUser(BaseModel):
    """User account details"""
    
    uuid: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[AireUserGender] = None
    year_of_birth: Optional[int] = None
    language: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    connected_services: Optional[list[AireUserServiceCredentials]] = None
    preferences: Optional[AireUserPreferences] = None
    summary: Optional[str] = None


class AireRole(str, Enum):
    """User roles"""

    User = "user"
    Admin = "admin"

