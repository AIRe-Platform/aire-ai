import os
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from ..models.chat import AireChatContext
from ..chains.user_summary import UserSummaryChain

model = ChatOpenAI(
    model="gpt-3.5-turbo", 
    base_url=os.getenv("OPENAI_API_BASE"))

system_prompt_text = """
Act as a medical advisor.
Your task is to find out what is bothering your patient and provide suggestions.
Do not suggest anything that could worsen the condition of the patient.

Act with empathy and in a friendly manner.

Here's a summary of your patient:
{user_summary}
"""

def __messages(input: dict):
    ctx: AireChatContext = input["ctx"]

    print(f"User summary: {input['user_summary']}")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt_text),
        *ctx.input.toChatMessages()
    ])

    return prompt

DefaultBot = (
    { "user_summary": UserSummaryChain, "ctx": RunnablePassthrough() }
    | RunnableLambda(__messages)
    | model
)
