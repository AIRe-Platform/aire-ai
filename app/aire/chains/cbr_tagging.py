from langchain.chains import create_tagging_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnableLambda
from ..models.chat import AireChatContext
from ..models.cbr import CBR_KEYWORDS
from ..llm import ChatModel

class CbrTags(BaseModel):
    keywords: str = Field(..., 
                          enum=CBR_KEYWORDS,
                          description="Describes what CBR topics could relate to the discussion, separated by commas.")

def __cbr_tagging_chain(ctx: AireChatContext):
    llm = ChatModel(temperature=0.0)
    chain = create_tagging_chain_pydantic(CbrTags, llm)
    messages = ctx.input.to_chat_messages()
    output = chain.invoke(messages)
    model: CbrTags = output['text']
    keywords = map(lambda x: x.strip(), model.keywords.split(","))
    return list(keywords)

CbrTaggingChain = RunnableLambda(__cbr_tagging_chain)
