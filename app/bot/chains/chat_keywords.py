# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from aire.models.chat import AireChatContext
from aire.services.memory import get_keywords
from llm import DefaultModel

prompt = ChatPromptTemplate.from_template("""
Extract the keywords describing the topic of the following conversation.

Important: 
Use keywords sparingly, prefer to use as few as possible.
If unsure, leave keywords empty.
When you tag the conversation with a keyword, you have to be absolutely sure it is correct!

Conversation:
{input}
"""
)

def __keyword_tagging_chain(ctx: AireChatContext):
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return list[str]()
    
    class Keywords(BaseModel):
        keywords: str = Field(..., 
            enum=get_keywords(ctx.platform),
            description="Keywords describing the topic of the conversation. Empty if no suitable keywords are found.")

    llm = DefaultModel(temperature=0.0).with_structured_output(Keywords)
    chain = prompt | llm
    output = chain.invoke({"input": messages})
    keywords = map(lambda x: x.strip(), output.keywords.split(","))
    return list(filter(lambda x: len(x) > 0, keywords))

ChatKeywordChain = RunnableLambda(__keyword_tagging_chain)
