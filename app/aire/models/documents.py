# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from typing import Optional

class AireDocumentMetadata(BaseModel):
    """Document metadata"""
    title: Optional[str] = None
    source: Optional[str] = None
    filename: Optional[str] = None
    lang: Optional[str] = None
    copyright: Optional[str] = None
    url: Optional[str] = None
    

class AireDocumentSearchResult(BaseModel):
    """Document search result (RAG)"""
    id: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[AireDocumentMetadata] = None
    relevance: Optional[float] = None
