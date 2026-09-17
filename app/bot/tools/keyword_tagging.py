# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.chat import AireChatContext
from aire.models.events import AireEvent, AireKeywordEvent
from aire.models.auth import AireScope
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

async def __tag_keywords(ctx: AireChatContext, call: ToolCall) -> AireKeywordEvent | None:
    if call.get("name") != __tool_name:
        return None

    if not AireScope.KeywordsRead in ctx.auth.scopes:
        return None
    
    results = await ChatKeywordChain.ainvoke(ctx)
    
    if results == None:
        return None
    
    return AireKeywordEvent(themes=results)


KeywordTaggingTool = CallableTool(
    name=__tool_name,
    descriptor=__tool_description,
    event_type=AireEvent.Keywords,
    prompt_gen=None,
    handler=__tag_keywords
)
