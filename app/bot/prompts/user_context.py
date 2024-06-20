from aire.models.chat import AireChatContext, AireChatInputContext
from aire.models.user import AireUser

def summary_from_chat_context(context: AireChatInputContext | None) -> str:
    summary = ""

    if context != None:
        if context.age != None:
            summary += f"\nThe user is {context.age} years old."
            
        if context.occupation != None:
            summary += f"\nThe user's occupation is {context.occupation}."

    return summary


def summary_from_profile(user: AireUser) -> str:
    summary = ""

    if user.first_name != None:
        summary += f"\nFirst name: {user.first_name}"

    if user.last_name != None:
        summary += f"\nLast name: {user.last_name}"

    if user.age != None:
        summary += f"\nAge: {user.age}"

    if user.gender != None:
        summary += f"\nGender: {user.gender.value}"

    if user.country != None:
        summary += f"\nCountry: {user.country}"

    if user.bio != None:
        summary += f"\nBiography: {user.bio}"

    return summary


def generate_user_context(ctx: AireChatContext) -> str:
    summary = ""

    if ctx.user == None:
        summary = summary_from_chat_context(ctx.input.context)
    else:
        summary = summary_from_profile(ctx.user)

    if len(summary) == 0:
        summary += """
        The user has not provided any information about themselves.
        You may ask them about their age and occupation.
        """
    else:
        summary += "\nYou may ask the user for any relevant background information."

    return summary
