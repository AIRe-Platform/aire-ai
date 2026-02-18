# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableLambda
from aire.models.chat import AireChatContext
from llm import DefaultModel

llm_summary = DefaultModel(temperature=0, max_tokens=None)
summary_prompt = """Progressively summarize the lines of conversation provided.

Conversation:
{messages}

Important:
Do not copy the conversation word by word.
Do not translate the messages from the original language.
Write the summary in the same language the messages are written in.
The summary must be anonymized. 
Do not include any information that could identify the user.

New summary:"""

def __chat_summary(ctx: AireChatContext) -> str:
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return ""
    
    system_prompt = SystemMessagePromptTemplate.from_template(summary_prompt)
    prompt = [ system_prompt.format(messages=messages) ]

    response = llm_summary.invoke(prompt)
    if not isinstance(response.content, str):
        return ""
    
    return response.content

ChatSummaryChain = RunnableLambda(__chat_summary)
