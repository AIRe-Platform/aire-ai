# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from aire.models.chat import AireChatContext

def create_agent_prompt(ctx: AireChatContext):
    agent = ctx.current_agent()
    if agent != None:
        return agent.prompt
    else:
        return ""
    
