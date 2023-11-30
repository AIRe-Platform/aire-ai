import os
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.schema.messages import ChatMessage
from langchain.schema.runnable import RunnableLambda
from langchain.chat_models import ChatOpenAI
from ..models.chat import AireChatContext, AireChatMessage
from ..chains.user_context import summarize_user_context

model = ChatOpenAI(model="gpt-3.5-turbo", base_url=os.getenv("OPENAI_API_BASE"))
system_prompt_text = """
Act as a medical advisor.
Your task is to find out what is bothering your patient and provide suggestions.
Do not suggest anything that could worsen the condition of the patient.

Here's a summary of your patient:
{user_summary}
"""
system_prompt_template = SystemMessagePromptTemplate.from_template(system_prompt_text)

def process(ctx: AireChatContext):

    def mapMessage(msg: AireChatMessage) -> ChatMessage:
        return ChatMessage(role=msg.role, content=msg.content)

    history = map(mapMessage, ctx.input.chat)

    if ctx.user != None:
        print("TODO: Summarize user info")
        user_summary = summarize_user_context(ctx.user, model)
    else:
        user_summary = "No user summary available, you may ask relevant information from the user."

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template.format(user_summary=user_summary),
        *history
    ])
    return prompt

DefaultBot = RunnableLambda(process) | model
