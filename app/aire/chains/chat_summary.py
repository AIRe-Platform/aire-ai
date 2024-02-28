from langchain.llms.openai import OpenAI
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.schema.runnable import RunnableLambda
from ..models.chat import AireChatContext
from ..llm import LLM

llm_summary = LLM(temperature=0)

def __chat_summary(ctx: AireChatContext) -> str:
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return ""
    history = ChatMessageHistory(messages=messages)
    memory = ConversationSummaryBufferMemory(chat_memory=history, llm=llm_summary)
    return memory.predict_new_summary(memory.chat_memory.messages, "").strip("\n ")

ChatSummaryChain = RunnableLambda(__chat_summary)
