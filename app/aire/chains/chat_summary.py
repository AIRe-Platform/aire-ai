import os
from langchain.llms.openai import OpenAI
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.schema.runnable import RunnableLambda
from ..models.chat import AireChatContext

llm_summary = OpenAI(
    temperature=0, 
    base_url=os.getenv("OPENAI_API_BASE"))

def __chat_summary(ctx: AireChatContext) -> str:
    history = ChatMessageHistory(messages=ctx.input.toChatMessages())
    memory = ConversationSummaryBufferMemory(chat_memory=history, llm=llm_summary)
    return memory.predict_new_summary(memory.chat_memory.messages, "").strip("\n ")

ChatSummaryChain = RunnableLambda(__chat_summary)
