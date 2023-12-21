from langchain.schema.runnable import RunnableParallel
from .chat_keywords import ChatKeywordChain
from .chat_summary import ChatSummaryChain

ChatAbstractChain = RunnableParallel(
    summary=ChatSummaryChain,
    keywords=ChatKeywordChain
)
