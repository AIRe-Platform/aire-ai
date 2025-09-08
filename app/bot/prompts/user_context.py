# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from aire.models.chat import AireChatContext
from aire.models.user import AireUser


def summary_from_profile(user: AireUser) -> str:
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


def generate_user_context(ctx: AireChatContext) -> str:
    summary = ""

    if ctx.user != None:
        summary = summary_from_profile(ctx.user)

    if len(summary) == 0:
        summary += """
        The user has not provided any information about themselves.
        You may ask them about their age and occupation.
        """
    else:
        summary += "\nYou may ask the user for any relevant background information."

    return summary
