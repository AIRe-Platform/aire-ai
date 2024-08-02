from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory.prompt import SUMMARY_PROMPT
from langchain.schema.runnable import RunnableLambda
from aire.models.chat import AireChatContext
from llm import DefaultModel

llm_summary = DefaultModel(temperature=0, max_tokens=256)
summary_prompt = """Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

Current summary:
{summary}

New lines of conversation:
{new_lines}

Language:
Use the same language the conversation is written in.

New summary:"""

def __chat_summary(ctx: AireChatContext) -> str:
    messages = ctx.input.to_chat_messages()
    if len(messages) < 1:
        return ""
    
    prompt = SUMMARY_PROMPT
    prompt.template = summary_prompt

    history = ChatMessageHistory(messages=messages)
    memory = ConversationSummaryBufferMemory(chat_memory=history, llm=llm_summary, prompt=prompt)
    return memory.predict_new_summary(memory.chat_memory.messages, "").strip("\n ")

ChatSummaryChain = RunnableLambda(__chat_summary)
