from pydantic import BaseModel
from enum import Enum

class AireModuleType(str, Enum):
    AI = "ai"
    ID = "id"
    Memory = "memory"

class AireModuleAccess(str, Enum):
    Public = "public"
    Service = "service"
    Private = "private"

class AireModule(BaseModel):
    type: AireModuleType
    endpoint: str
    access: AireModuleAccess
    token: str | None

class AireService(BaseModel):
    name: str

class AirePlatform(BaseModel):
    name: str
    modules: dict[AireModuleType, AireModule]

class AirePlatformConfiguration(BaseModel):
    platform: AirePlatform
    services: list[AireService]
