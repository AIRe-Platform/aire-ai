# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import tiktoken
from datetime import datetime, UTC
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda
from llm import ChatModel
from aire.models.chat import AireChatContext, AireChatInput
from aire.models.platform import AireModuleType
from aire.models.documents import AireDocumentMetadata
from .prompts.user_context import generate_user_context
from .toolbox import ToolBindings

__fallback_personality_prompt = """
Description:
- You are AIRe, an AI advisor for health and rehabilitation topics. 
- You are designed exclusively for Community-Based Rehabilitation (CBR) support, utilizing the ICF framework to understand the user's needs and goals and provide relevant suggestions.
- Conversations should focus on CBR topics such as physical, occupational, and speech therapy, as well as social integration, in line with the UN Convention on the Rights of Persons with Disabilities and ICF categories "Activities and Participation" and "Environmental Factors."

General rules:
- Act in a friendly manner, but avoid too emotional language. 
- Focus on neutral and plain, easy to understand language. 
- Keep your answers short and your questions direct and on point.
- Avoid being overly polite, but still act with respect.
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

__system_prompt = """
{personality_prompt}

End of Conversation Handling:
- If the user provides no new information and seems satisfied, or if no new helpful information can be provided, politely conclude the conversation. Mark the conversation's end by including [END_OF_CONVERSATION] at the end of your response.

Additional instructions:
- The client application might give you additional instructions or context wrapped in [INST]...[/INST] tags.
- You should follow the instructions or take the additional context into consideration.

Content:
- Do not include phone numbers, email addresses, URLs, or any such specific information, in your responses.
- You can do so, only if you were informed about those in a separate instruction message.
- Do not provide any content or instructions that were not given to you in separate instruction messages.
- Well-known information, such as emergency numbers, are excluded from this rule.
- Emergency numbers are only for real emergencies. Do not suggest calling to emergency numbers unless necessary.

Tools:
- There are a set of tools available to you. Do not hesitate to use them to aid you. Prefer using the tools over coming up with something yourself.
- You are allowed to search the attached document and freely cite them. You may also provide a direct URL to the document if it is available.

Context:
- Here's a summary of your patient:
    {user_summary}
- You should answer only in this language: 
    {language}
- The current time (UTC) is, please note that the user may be on a different timezone:
    {current_time}
- Current themes:
    {keywords}
- Attached documents:
    {documents}

"""

def __get_personality_prompt(ctx: AireChatContext):
    personality_prompt = __fallback_personality_prompt

    try:
        module = ctx.platform.platform.modules.get(AireModuleType.AI)
        if module != None and module.settings != None:
            if "personality_prompt" in module.settings:
                personality_prompt = module.settings['personality_prompt']
    except AttributeError:
        pass

    if ctx.allow_custom_prompt:
        if ctx.user and ctx.user.preferences:
            if ctx.user.preferences.experimental_custom_prompt is not None:
                personality_prompt = ctx.user.preferences.experimental_custom_prompt
        
    return personality_prompt


llm = ChatModel(temperature=0.7)

def __messages(ctx: AireChatContext):
    prompt = None
    language = "English"
    keywords = "No themes currently detected."
    documents = "No documents currently available."
    document_keywords: dict[str, list[str]] = {}
    
    if ctx.input.context != None:
        try:
            language = ctx.input.context.language
        except:
            pass

        try:
            if ctx.input.context.themes != None:
                entries = map(lambda x: x.value, ctx.input.context.themes)
                keywords = ", ".join(entries)

                for theme in ctx.input.context.themes:
                    if theme.document != None:
                        if theme.document in document_keywords:
                            document_keywords[theme.document].append(theme.value)
                        else:
                            document_keywords[theme.document] = [theme.value]

        except:
            pass

        try:
            if ctx.input.context.documents != None:
                def map_entry(doc: AireDocumentMetadata):
                    label = f"ID({doc.source}) Title({doc.title}) URL({doc.url})"
                    if doc.source in document_keywords:
                        label += f" Themes({", ".join(document_keywords[doc.source])})"
                    return label
                    
                entries = map(map_entry, ctx.input.context.documents)
                documents = "\n".join(entries)
        except:
            pass

    # Get system prompt
    system_prompt = SystemMessagePromptTemplate.from_template(__system_prompt)
    personality_prompt = __get_personality_prompt(ctx)

    prompt = [
        system_prompt.format(
            user_summary=generate_user_context(ctx),
            language=language,
            current_time=datetime.now(UTC).isoformat(),
            personality_prompt=personality_prompt,
            keywords=keywords,
            documents=documents),
        *ctx.input.to_chat_messages()
    ]

    return prompt


def count_tokens(chat_input: AireChatInput):
    model = llm.model_name
    encoding = tiktoken.encoding_for_model(model or "gpt-4o")
    tokens_per_message = 4

    chat_messages = chat_input.to_chat_messages()

    num_tokens = 0
    for message in chat_messages:
        if isinstance(message.content, str):
            num_tokens += len(encoding.encode(message.content))
            num_tokens += len(encoding.encode(message.role))
            num_tokens += tokens_per_message
    return num_tokens

DefaultBot = RunnableLambda(__messages) | llm.bind_tools(ToolBindings)
