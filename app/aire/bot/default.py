from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
import tiktoken
from ..llm import ChatModel
from ..models.chat import AireChatContext, AireChatInput
from ..chains.user_summary import UserSummaryChain
from langchain_core.prompts import ChatPromptTemplate

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
        *ctx.input.to_chat_messages()
    ]

    return prompt

def token_count(chat_input: AireChatInput):

    model = "gpt-3.5-turbo-1106"
    encoding = tiktoken.encoding_for_model(model)

    chat_template = ChatPromptTemplate.from_messages(chat_input.to_chat_messages())
    messages_list = list(map(lambda msg: msg.content, chat_template.messages))
    list_token_values = encoding.encode_batch(messages_list)
    
    num_total_tokens = 0
    for list_item in list_token_values:
        num_tokens = len(list_item)
        num_total_tokens += num_tokens

    return num_total_tokens


DefaultBot = RunnableLambda(__messages) | ChatModel()
