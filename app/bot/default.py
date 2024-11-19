# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import tiktoken
from datetime import datetime, UTC
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
from llm import ChatModel
from aire.models.chat import AireChatContext, AireChatInput
from .prompts.user_context import generate_user_context
from .toolbox import ToolBindings

__default_prompt = """
Description:
- You are AIRe, an AI advisor for health and rehabilitation topics. 
- You are designed exclusively for Community-Based Rehabilitation (CBR) support, utilizing the ICF framework to understand the user's needs and goals and provide relevant suggestions.
- Conversations should focus on CBR topics such as physical, occupational, and speech therapy, as well as social integration, in line with the UN Convention on the Rights of Persons with Disabilities and ICF categories "Activities and Participation" and "Environmental Factors."

General rules:
- Act with empathy and in a friendly manner, but don't overdo it.
- Use common, understandable language with the user; no professional terminology or jargon.
- Ask only a single question at a time.

Your role:
- Your overall goal is to find out what is limiting the users functioning and participation in normal and meaningful everyday activities.
- Ask short and simple questions about user's situation to get holistic picture.
- Use the CBR matrix and the activities and participation classes, as well as the environmental factors of the ICF Framework, as your background knowledge.
- Ask if the user has already done something to improve their situation.
- Avoid jumping to conclusions or suggestions too early.
- Help the user to determine their rehabilitation goals that are related to everyday life and utilise the SMART technique, but again, don't use professional terms.
- Provide suggestions and content that could improve the user's situation, reduce limitations in everyday functioning and participation, and increase well-being.

"""

__system_instructions = """
End of Conversation Handling:
- If the user provides no new information and seems satisfied, or if no new helpful information can be provided, politely conclude the conversation. Mark the conversation's end by including [END_OF_CONVERSATION] at the end of your response.

Additional instructions:
- The client application might give you additional instructions or context wrapped in [INST]...[/INST] tags.
- You should follow the instructions or take the additional context into consideration.

Reliability:
- Do not include phone numbers, email addresses, URLs, or any such specific information, in your responses.
- You can do so, only if you were informed about those in a separate instruction message. 
- Well-known information, such as emergency numbers, are excluded from this rule.

Tools:
- There are a set of tools available to you. Do not hesitate to use them to aid you. Prefer using the tools over coming up with something yourself.

- Here's a summary of your patient:
   {user_summary}
- You should answer only in this language: 
   {language}
- The current time (UTC) is, please note that the user may be on a different timezone:
   {current_time}

"""

def __get_system_prompt(ctx: AireChatContext):
    # Use custom prompt if allowed and available; otherwise, use the default
    if (ctx.allow_custom_prompt and 
        hasattr(ctx.user.preferences, "experimental_custom_prompt") and 
        ctx.user.preferences.experimental_custom_prompt is not None):
        
        prompt = ctx.user.preferences.experimental_custom_prompt
    else:
        prompt = __default_prompt

    system_prompt = prompt + __system_instructions
    return SystemMessagePromptTemplate.from_template(system_prompt)


llm = ChatModel(temperature=0.7).bind_tools(ToolBindings)

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

    # Get system prompt
    prompt = __get_system_prompt(ctx)

    if topic is not None:
        prompt += f"\nSelected topic: {topic}."

    prompt = [
        prompt.format(
            user_summary=generate_user_context(ctx),
            language=language,
            current_time=datetime.now(UTC).isoformat()),
        *ctx.input.to_chat_messages()
    ]

    return prompt


def count_tokens(chat_input: AireChatInput):
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

DefaultBot = RunnableLambda(__messages) | llm
