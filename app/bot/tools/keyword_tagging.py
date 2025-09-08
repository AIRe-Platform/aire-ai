# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.chat import AireChatContext, AireChatEvent
from ..chains.chat_keywords import ChatKeywordChain
from .callable_tool import CallableTool

__tool_name = "keyword_tagging"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": """
            Detect keywords and themes in the conversation. Run this tool often.
        """,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def __gen_keywords(ctx: AireChatContext, call: ToolCall) -> list[str] | None:
    if call.get("name") != __tool_name:
        return None
    
    results = ChatKeywordChain.invoke(ctx)
    
    if results == None:
        return None
    
    return list(map(lambda x: x.value, results))


KeywordTaggingTool = CallableTool(
    name=__tool_name,
    descriptor=__tool_description,
    event_type=AireChatEvent.Keywords,
    handler=__gen_keywords
)
