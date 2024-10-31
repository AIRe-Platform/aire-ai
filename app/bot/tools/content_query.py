# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.chat import AireChatContext, AireChatEvent
from aire.models.content import AireContentEvent
from aire.models.auth import AireScope
from bot.vector_stores import ContentVectorStore
from .callable_tool import CallableTool

__tool_name = "query_content"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": """
            Query content such as documents, images, videos, and websites.
            Use this tool to find useful resources that are shown as content suggestions to the user.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Search string"
                }
            },
            "required": ["search"]
        }
    }
}


def __content_query(ctx: AireChatContext, call: ToolCall) -> AireContentEvent | None:
    if call.get("name") != "query_content":
        return None
    
    if not AireScope.ContentRead in ctx.auth.scopes:
        return None
    
    args = call.get("args")
    search = args.get("search")
    results = ContentVectorStore().query(search, 4)

    return AireContentEvent(search=search, results=results)
    

ContentQueryTool = CallableTool(
    name=__tool_name, 
    descriptor=__tool_description, 
    event_type=AireChatEvent.ContentSuggestions,
    handler=__content_query
)
