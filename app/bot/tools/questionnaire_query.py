# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.auth import AireScope
from aire.models.chat import AireChatContext, AireChatEvent
from aire.models.questionnaire import AireQuestionnaireMetadata
from bot.vector_stores import QuestionnaireVectorStore
from .callable_tool import CallableTool

__tool_name = "query_questionnaires"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": "Query questionnaires from database using similarity search",
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

def __query_questionnaires(ctx: AireChatContext, call: ToolCall) -> list[AireQuestionnaireMetadata] | None:
    if call.get("name") != "query_questionnaires":
        return None
    
    if not AireScope.QuestionnaireRead in ctx.auth.scopes:
        return None

    args = call.get("args")
    search = args.get("search")

    return QuestionnaireVectorStore().query(search, 8)

QuestionnaireQueryTool = CallableTool(
    name=__tool_name,
    descriptor=__tool_description,
    event_type=AireChatEvent.Questionnaire,
    handler=__query_questionnaires
)
