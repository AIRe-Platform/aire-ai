# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pydantic import BaseModel
from enum import Enum
from typing import Optional

class AireModuleType(str, Enum):
    """Module types"""
    
    AI = "ai"
    ID = "id"
    Memory = "memory"

class AireModuleAccess(str, Enum):
    """Module access levels"""

    Public = "public"
    Service = "service"
    Private = "private"

class AireModule(BaseModel):
    """Describes a platform module"""

    type: AireModuleType
    endpoint: str
    access: AireModuleAccess
    token: Optional[str] = None
    settings: Optional[dict] = None

class AireService(BaseModel):
    """Describes an external service"""

    name: str
    modules: Optional[list[AireModule]] = None

class AirePlatform(BaseModel):
    """Describes the platform's core modules"""

    name: str
    modules: dict[AireModuleType, AireModule]

class AirePlatformConfiguration(BaseModel):
    """Contains the configuration of the AIRe platform"""

    platform: AirePlatform
    services: list[AireService]
