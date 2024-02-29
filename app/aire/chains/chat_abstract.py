from langchain.schema.runnable import RunnableParallel
# from .chat_keywords import ChatKeywordChain
from .chat_summary import ChatSummaryChain
from .cbr_tagging import CbrTaggingChain

ChatAbstractChain = RunnableParallel(
    summary=ChatSummaryChain,
    keywords=CbrTaggingChain
)
