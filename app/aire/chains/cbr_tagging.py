from langchain.chains import create_tagging_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnableLambda
from ..models.chat import AireChatContext
from ..models.cbr import CBR_KEYWORDS
from ..llm import ChatModel

class CbrTags(BaseModel):
    keywords: str = Field(..., 
                          enum=CBR_KEYWORDS,
                          description="Describes what CBR topics could relate to the discussion, separated by commas. If no topics apply, this is empty.")

def __cbr_tagging_chain(ctx: AireChatContext):
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return list[str]()

    llm = ChatModel(temperature=0.0)
    chain = create_tagging_chain_pydantic(CbrTags, llm)
    output = chain.invoke(messages)
    
    model: CbrTags = output['text']
    keywords = map(lambda x: x.strip(), model.keywords.split(","))
    return list(filter(lambda x: len(x) > 0, keywords))

CbrTaggingChain = RunnableLambda(__cbr_tagging_chain)
