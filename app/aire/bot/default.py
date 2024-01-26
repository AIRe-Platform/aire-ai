from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
from ..llm import ChatModel
from ..models.chat import AireChatContext
from ..chains.user_summary import UserSummaryChain

system_prompt_text = """
Act as a medical advisor.
Your task is to find out what is bothering your patient and provide suggestions.
Do not suggest anything that could worsen the condition of the patient.

Act with empathy and in a friendly manner.

Here's a summary of your patient:
{user_summary}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_text)

def __messages(ctx: AireChatContext):

    user_summary = UserSummaryChain.invoke(ctx)

    prompt = [
        system_prompt.format(user_summary=user_summary),
        *ctx.input.toChatMessages()
    ]

    return prompt

DefaultBot = RunnableLambda(__messages) | ChatModel()
