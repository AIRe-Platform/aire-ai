# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Callable
from aire.models.events import AireEvent
from aire.models.agent import AireAgentToolConfig
from .tools.reminders import ReminderTool
from .tools.questionnaire_query import QuestionnaireQueryTool
from .tools.content_query import ContentQueryTool
from .tools.keyword_tagging import KeywordTaggingTool
from .tools.document_search import DocumentSearchTool

class CallableTool:
    name: str
    descriptor: dict
    event: AireEvent
    call: Callable

Toolbox = {
    ReminderTool.name: ReminderTool,
    QuestionnaireQueryTool.name: QuestionnaireQueryTool,
    ContentQueryTool.name: ContentQueryTool,
    KeywordTaggingTool.name: KeywordTaggingTool,
    DocumentSearchTool.name: DocumentSearchTool
}

def create_bindings(tools: dict[str, AireAgentToolConfig]) -> list[dict]:
    """Create a list of tool descriptors to bind with LLM"""
    bindings: list[dict] = []
    for tool_name in tools:
        config = tools[tool_name]
        tool = Toolbox.get(tool_name, None)
        if tool != None and config.enabled == True:
            bindings.append(tool.descriptor)
    return bindings
