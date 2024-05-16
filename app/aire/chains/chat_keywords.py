from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from ..models.chat import AireChatContext
from ..llm import ChatModel
from ..services.memory import get_keywords

prompt = ChatPromptTemplate.from_template(
    """
Extract the keywords describing the topic of the following conversation.

Only extract the keywords in the 'Keywords' function. Separate the keywords with commas.

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

    llm = ChatModel(temperature=0.0).with_structured_output(Keywords)
    chain = prompt | llm
    output = chain.invoke({"input": messages})
    keywords = map(lambda x: x.strip(), output.keywords.split(","))
    return list(filter(lambda x: len(x) > 0, keywords))

ChatKeywordChain = RunnableLambda(__keyword_tagging_chain)
