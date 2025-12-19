# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, UTC
from aire.models.chat import AireChatContext
from aire.models.documents import AireDocumentMetadata
from aire.models.chat import AireChatContext
from aire.models.user import AireUser

__context_prompt_template = """
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

def create_context_prompt(ctx: AireChatContext) -> str:
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

    return __context_prompt_template.format(            
        user_summary=__generate_user_context(ctx),
        language=language,
        current_time=datetime.now(UTC).isoformat(),
        keywords=keywords,
        documents=documents)


def __summary_from_profile(user: AireUser) -> str:
    summary = ""

    if user.first_name != None:
        summary += f"\nFirst name: {user.first_name}"

    if user.last_name != None:
        summary += f"\nLast name: {user.last_name}"

    if user.year_of_birth != None:
        summary += f"\nYear_of_birth: {user.year_of_birth}"

    if user.gender != None:
        summary += f"\nGender: {user.gender.value}"

    if user.country != None:
        summary += f"\nCountry: {user.country}"

    if user.bio != None:
        summary += f"\nBiography: {user.bio}"

    return summary


def __generate_user_context(ctx: AireChatContext) -> str:
    summary = ""

    if ctx.user != None:
        summary = __summary_from_profile(ctx.user)

    if len(summary) == 0:
        summary += """
        The user has not provided any information about themselves.
        You may ask them about their age and occupation.
        """
    else:
        summary += "\nYou may ask the user for any relevant background information."

    return summary
