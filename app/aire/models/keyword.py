from pydantic import BaseModel

class AireKeyword(BaseModel):
    """Keyword"""
    value: str
    