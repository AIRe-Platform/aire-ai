# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from aire.models.chat import AireChatContext
from .tools.agent_switch_tool import AgentSwitchTool
from .tools.reminders import ReminderTool
from .tools.questionnaire_query import QuestionnaireQueryTool
from .tools.content_query import ContentQueryTool
from .tools.keyword_tagging import KeywordTaggingTool
from .tools.document_search import DocumentSearchTool

Toolbox = {
    AgentSwitchTool.name: AgentSwitchTool,
    ReminderTool.name: ReminderTool,
    QuestionnaireQueryTool.name: QuestionnaireQueryTool,
    ContentQueryTool.name: ContentQueryTool,
    KeywordTaggingTool.name: KeywordTaggingTool,
    DocumentSearchTool.name: DocumentSearchTool
}

def create_tool_bindings(ctx: AireChatContext) -> list[dict]:
    """Create a list of tool descriptors to bind with LLM"""
    agent = ctx.current_agent()
    bindings: list[dict] = []

    if agent != None:
        for tool_name in agent.tools:
            config = agent.tools[tool_name]
            tool = Toolbox.get(tool_name, None)
            if tool != None and config.enabled == True:
                bindings.append(tool.descriptor)

    return bindings

def create_tool_prompts(ctx: AireChatContext) -> str:
    """Create a list of tool descriptors to bind with LLM"""
    agent = ctx.current_agent()
    prompts: list[str] = []

    if agent != None:
        for tool_name in agent.tools:
            config = agent.tools[tool_name]
            tool = Toolbox.get(tool_name, None)
            if tool != None and tool.prompt_gen != None and config.enabled == True:
                prompt = tool.prompt_gen(ctx)
                if prompt != None:
                    prompts.append(prompt)

    return "\n".join(prompts)