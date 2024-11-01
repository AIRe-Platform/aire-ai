# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel
from typing import Callable, Any
from aire.models.chat import AireChatEvent, AireChatContext
from langchain_core.messages.tool import ToolCall

class CallableTool(BaseModel):
    name: str
    descriptor: dict
    event_type: AireChatEvent
    handler: Callable[[AireChatContext, ToolCall], Any]
