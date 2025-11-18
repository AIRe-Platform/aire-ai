# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
from llm import ChatModel
from aire.models.chat import AireChatContext
from .toolbox import create_bindings
from .prompts.agent_prompt import create_agent_prompt
from .prompts.personality_prompt import create_personality_prompt
from .prompts.context_prompt import create_context_prompt
from .prompts.system_instructions import SYSTEM_INSTRUCTIONS_PROMPT

__system_prompt_template = """
{personality_prompt}
{agent_prompt}
{system_instructions}
{context_prompt}
"""

llm = ChatModel(temperature=0.7)

def __messages(ctx: AireChatContext):
    prompt = None

    system_prompt = SystemMessagePromptTemplate.from_template(__system_prompt_template)
    personality_prompt = create_personality_prompt(ctx)
    agent_prompt = create_agent_prompt(ctx)
    context_prompt = create_context_prompt(ctx)

    prompt = [
        system_prompt.format(
            personality_prompt=personality_prompt,
            agent_prompt=agent_prompt,
            system_instructions=SYSTEM_INSTRUCTIONS_PROMPT,
            context_prompt=context_prompt),
        *ctx.input.to_chat_messages()
    ]

    return prompt

def __tools(ctx: AireChatContext):
    agent = ctx.current_agent()
    toolbox: list[dict] = []
    if agent != None:
        toolbox = create_bindings(agent.tools)
    return toolbox

def __default_bot(ctx: AireChatContext):
    llm_tools = __tools(ctx)
    return RunnableLambda(__messages) | llm.bind_tools(llm_tools)

DefaultBot = RunnableLambda(__default_bot)
