# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.auth import AireScope
from aire.models.chat import AireChatContext
from aire.models.events import AireEvent, AireQuestionnaireEvent
from aire.models.questionnaire import AireQuestionnaireMetadata
from aire.models.platform import AireModuleSetting
from bot.vector_stores import QuestionnaireVectorStore
from .callable_tool import CallableTool

__tool_name = "query_questionnaires"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": """
            Query questionnaires from database using similarity search.
            Questionnaires can help you assess the situation by providing curated forms
            that provide a set of logical steps. You will see the questions and answers after
            the user has filled the questionnaire.
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


def __query_questionnaires(ctx: AireChatContext, call: ToolCall) -> AireQuestionnaireEvent | None:
    if call.get("name") != __tool_name:
        return None
    
    if not AireScope.QuestionnaireRead in ctx.auth.scopes:
        return None

    args = call.get("args")
    search = args.get("search")
    agent = ctx.current_agent()

    if search == None or agent == None:
        return None
    
    memories = ctx.platform.get_agent_memories(agent)
    questionnaires: list[AireQuestionnaireMetadata] = []
    
    for svc in memories:
        if svc.settings != None:
            database = svc.settings.get(AireModuleSetting.VectorDatabaseName, None)
            if database != None:
                results = QuestionnaireVectorStore(database).query(search, 8)
                questionnaires.extend(results)

    return AireQuestionnaireEvent(search=search, results=questionnaires)


QuestionnaireQueryTool = CallableTool(
    name=__tool_name,
    descriptor=__tool_description,
    event_type=AireEvent.Questionnaire,
    prompt_gen=None,
    handler=__query_questionnaires
)
