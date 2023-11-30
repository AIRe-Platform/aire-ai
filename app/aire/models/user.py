from pydantic import BaseModel
from enum import Enum

class AireUserServiceCredentials(BaseModel):
    name: str
    token: str

class AireUserGender(str, Enum):
    Male = "male"
    Female = "female"
    Other = "other"

class AireUser(BaseModel):
    uuid: str
    email: str
    first_name: str | None
    last_name: str | None
    gender: AireUserGender | None
    age: int | None
    language: str | None
    country: str | None
    bio: str | None
    connected_services: list[AireUserServiceCredentials] | None
