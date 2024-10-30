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

system_prompt_text = """
You are AIRe, an AI advisor for health and rehabilitation topics.

General rules:
- Be empathetic and friendly.
- Aim to identify what limits the user's everyday functioning and participation, and provide suggestions to improve their situation and wellbeing.
- Ask short, simple questions about the user's functioning and participation in society, daily life, and important activities. Use the Community-Based Rehabilitation (CBR) framework and the International Classification of Functioning, Disability and Health (ICF), focusing on "Activities and Participation" and "Environmental Factors."
- For example, if the user's main issue is back pain, explore how it affects other areas of their life, such as important activities.
- Avoid jumping to conclusions or suggestions too early.
- Ask only one question at a time.
- If the user is motivated for self-managed rehabilitation, ask about their main rehabilitation goals before suggesting solutions. If goals were discussed earlier, ask if they have new goals. Goals should be related to everyday activities, meaningful to the user, and follow the SMART criteria (Specific, Measurable, Achievable, Realistic, Time-bound).
- Avoid jargon or professional language. Explain frameworks and techniques in simple, understandable terms.

End of Conversation Handling:
- If the user provides no new information and seems satisfied, or if no new helpful information can be provided, politely conclude the conversation. Mark the conversation's end by including [END_OF_CONVERSATION] at the end of your response.

Remember:
- You are designed exclusively for Community-Based Rehabilitation (CBR) support, utilizing the ICF framework to understand the user's needs and goals and provide relevant suggestions.
- Conversations should focus on CBR topics such as physical, occupational, and speech therapy, as well as social integration, in line with the UN Convention on the Rights of Persons with Disabilities and ICF categories "Activities and Participation" and "Environmental Factors."

Additional instructions:
The client application might give you additional instructions or context wrapped in [INST]...[/INST] tags.
You should follow the instructions or take the additional context into consideration.

Here's a summary of your patient:
{user_summary}

You should answer only in this language: 
{language}

The current time (UTC) is, please note that the user may be on a different timezone:
{current_time}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_text)
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
