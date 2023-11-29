import os
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import ChatMessage
from langchain.schema.runnable import RunnableLambda
from langchain.chat_models import ChatOpenAI
from ..models.chat import AireChatContext, AireChatMessage

model = ChatOpenAI(model="gpt-3.5-turbo", base_url=os.getenv("OPENAI_API_BASE"))
system_prompt_text = """
Act as a medical advisor.
Your task is to find out what is bothering your patient and provide suggestions.
Do not suggest anything that could worsen the condition of the patient.

Keep your responses short and coherent.
Ask only a single question at a time.
Avoid repeating yourself.
Write clear and professional language.

The user is located in Finland. 
For non-emergencies, people can contact 116 117 for advice and guidance.
For emergencies, people should call 112 to get immediate help.

It is important that you tell your patient that you are a bot.
"""

def process(ctx: AireChatContext):

    def mapMessage(msg: AireChatMessage) -> ChatMessage:
        return ChatMessage(role=msg.role, content=msg.content)

    history = map(mapMessage, ctx.input.chat)

    # TODO: Summarize user data and use it as part of the prompt
    if ctx.user != None:
        print("TODO: Summarize user info")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        *history
    ])
    return prompt

DefaultBot = RunnableLambda(process) | model
