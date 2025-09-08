# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.chat import AireChatContext, AireChatEvent
from aire.models.documents import AireDocumentSearchEvent
from aire.models.auth import AireScope
from bot.vector_stores import DocumentVectorStore
from .callable_tool import CallableTool

__store = DocumentVectorStore()

__tool_name = "search_documents"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": """
            Search document store for additional knowledge.
            You may also use document ID to search the content of a particular document.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Search string"
                },
                "document_id": {
                    "type": "string",
                    "description": "Document ID as lower-case GUID"
                },
            },
            "required": ["search"]
        }
    }
}


def __document_search(ctx: AireChatContext, call: ToolCall) -> AireDocumentSearchEvent | None:
    if call.get("name") != __tool_name:
        return None
    
    if not AireScope.ContentRead in ctx.auth.scopes:
        return None
    
    args = call.get("args")
    search = args.get("search")
    document_id = args.get("document_id")

    if search == None:
        return None
    
    if document_id == None:
        results = __store.query(search, 4, 0.75)
    else:
        results = __store.query_from_doc(document_id, search, 2, 0.75)

    return AireDocumentSearchEvent(search=search, results=results)
    

DocumentSearchTool = CallableTool(
    name=__tool_name, 
    descriptor=__tool_description, 
    event_type=AireChatEvent.DocumentResults,
    handler=__document_search
)
