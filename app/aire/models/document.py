from pydantic import BaseModel

class AireDocumentMetadata(BaseModel):
    source: str | None
    language: str | None
    relevance: float | None

