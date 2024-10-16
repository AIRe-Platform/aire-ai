# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Optional
from pydantic import BaseModel

class AireReminderContent(BaseModel):
    message: str

class AireReminder(BaseModel):
    id: Optional[str]
    trigger_timestamp: int
    read_timestamp: Optional[int]
    content: AireReminderContent
