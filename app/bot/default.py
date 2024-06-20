import tiktoken
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
from llm import ChatBotModel
from aire.models.chat import AireChatContext, AireChatInput
from .prompts.user_context import generate_user_context

system_prompt_text = """
Act as a medical advisor. 

Act with empathy and in a friendly manner.

Your task is to find out what is bothering your patient and provide suggestions.

Do not suggest anything that could worsen the condition of the patient.

Ask short and simple questions to get information about the nature of the condition.

Consider possible causes.

Do not jump into conclusions too early.

Ask only a single question at once.

Here's a summary of your patient:
{user_summary}

You should answer only in this language: {language}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_text)

def __messages(ctx: AireChatContext):
    language = None
    topic = None
    prompt = None

    try:
        language = ctx.input.context.language
    except AttributeError:
        pass
    
    if language == None:
        language = "English"


    try:
        topic = ctx.input.context.topic
    except AttributeError:
        pass
    

    if ctx.allow_custom_prompt:
        try:
            prompt = ctx.user.preferences.experimental_custom_prompt
        except AttributeError:
            pass

    if prompt == None:
        prompt = system_prompt

    if topic != None:
        prompt += f"\nThe user wants to speak about: {topic}."

    prompt = [
        prompt.format(
            user_summary=generate_user_context(ctx),
            language=language),
        *ctx.input.to_chat_messages()
    ]

    return prompt


def count_tokens(chat_input: AireChatInput):
    llm = ChatBotModel()
    model = llm.model_name
    encoding = tiktoken.encoding_for_model(model)
    tokens_per_message = 4

    chat_messages = chat_input.to_chat_messages()

    num_tokens = 0
    for message in chat_messages:
        num_tokens += len(encoding.encode(message.content))
        num_tokens += len(encoding.encode(message.role))
        num_tokens += tokens_per_message
    return num_tokens

DefaultBot = RunnableLambda(__messages) | ChatBotModel()