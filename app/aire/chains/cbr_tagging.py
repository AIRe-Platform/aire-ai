from langchain.chains import create_tagging_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnableLambda
from langchain.output_parsers import CommaSeparatedListOutputParser
from ..models.chat import AireChatContext
from ..models.cbr import CBR_KEYWORDS
from ..llm import ChatModel

class CbrTags(BaseModel):
    keywords: str = Field(..., 
                          enum=CBR_KEYWORDS,
                          description="Describes what CBR topics could relate to the discussion, separated by commas and spaces")

def __cbr_tagging_chain(ctx: AireChatContext):
    llm = ChatModel(temperature=0.0)
    chain = create_tagging_chain_pydantic(CbrTags, llm)
    messages = ctx.input.to_chat_messages()
    output = chain.invoke(messages)
    model: CbrTags = output['text']
    parser = CommaSeparatedListOutputParser()
    return parser.parse(model.keywords)

CbrTaggingChain = RunnableLambda(__cbr_tagging_chain)
