# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class AireContentType(str, Enum):
    """ Content types """

    URL = "url"
    Image = "image"
    Video = "video"
    Document = "document"


class AireContent(BaseModel):
    """ Content model """

    id: str
    type: AireContentType
    name: Optional[str]
    description: Optional[str]
    hidden: Optional[bool]
    url: Optional[str]
    thumbnail_url: Optional[str]
    views: Optional[int]
    score: Optional[int]
    thumbs_up: Optional[int]
    thumbs_down: Optional[int]
    modified: Optional[datetime]
    keywords: Optional[list[str]]
    file_name: Optional[str]
    thumbnail_file_name: Optional[str]


class AireContentMetadata(BaseModel):
    """ Content embedding metadata """

    id: str | None
    type: AireContentType | None
    keywords: list[str] | None
    relevance: float | None
