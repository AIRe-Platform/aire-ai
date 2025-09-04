# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from aire.models.chat import AireChatContext
from aire.services.memory import get_keywords, AireKeyword
from llm import DefaultModel
from pydantic import BaseModel, Field

prompt = ChatPromptTemplate.from_template("""
Extract the keywords describing the topic of the following conversation.

Important: 
Pick only from the list of keywords provided below.
You may pick more than one keywords, separate the words with a comma.
If unsure, leave keywords empty.
                                          
List of keywords:
{keywords}

Conversation:
{input}
"""
)

def __keyword_tagging_chain(ctx: AireChatContext) -> list[AireKeyword]:
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return []
    
    keywords = get_keywords(ctx.platform)
    dictionary = {k.value: k for k in keywords}
    keyword_list = "\n".join(dictionary.keys())
    
    class Keywords(BaseModel):
        keywords: str = Field(..., 
                        description="Comma separated list of keywords describing the topic of the conversation. Empty if no suitable keywords are found.") # type: ignore

    llm = DefaultModel(temperature=0.0).with_structured_output(Keywords)
    chain = prompt | llm
    output = chain.invoke({"input": messages, "keywords": keyword_list})
    keyword_output = Keywords.model_validate(output)

    keyword_output_stripped = map(lambda x: x.strip(), keyword_output.keywords.split(","))
    keywords_valid = filter(lambda x: dictionary.get(x) != None, keyword_output_stripped)

    return list(map(lambda x: dictionary[x], keywords_valid))

ChatKeywordChain = RunnableLambda(__keyword_tagging_chain)
