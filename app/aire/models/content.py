# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class AireContentType(str, Enum):
    """Content types"""
    URL = "url"
    Image = "image"
    Video = "video"
    Document = "document"


class AireContent(BaseModel):
    """Content model"""
    id: str
    type: AireContentType
    name: Optional[str] = None
    description: Optional[str] = None
    hidden: Optional[bool] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    views: Optional[int] = None
    score: Optional[int] = None
    thumbs_up: Optional[int] = None
    thumbs_down: Optional[int] = None
    modified: Optional[datetime] = None
    keywords: Optional[list[str]] = None
    file_name: Optional[str] = None
    thumbnail_file_name: Optional[str] = None
    

class AireContentMetadata(BaseModel):
    """Content embedding metadata"""

    id: Optional[str] = None
    type: Optional[AireContentType] = None
    keywords: Optional[list[str]] = None
    relevance: Optional[float] = None
