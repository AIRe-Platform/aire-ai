# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from langchain_core.messages.tool import ToolCall
from aire.models.chat import AireChatContext
from aire.models.events import AireEvent, AireAgentSwitchEvent
from aire.models.auth import AireScope
from .callable_tool import CallableTool

__tool_name = "agent_switch"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": """
            Redirect user to the another assistant agent
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the agent"
                }
            },
            "required": ["name"]
        }
    }
}


def __agent_switch(ctx: AireChatContext, call: ToolCall) -> AireAgentSwitchEvent | None:
    if call.get("name") != __tool_name:
        return None
    
    if not AireScope.ContentRead in ctx.auth.scopes:
        return None
    
    args = call.get("args")
    name = args.get("name")

    current = ctx.current_agent()

    if name == None:
        return None
        
    if current != None and current.name == name:
        return None
    
    match = next(iter([x for x in ctx.platform.agents if x.name == name]), None)
    if match == None:
        return None

    return AireAgentSwitchEvent(agent=match.name)
    

AgentSwitchTool = CallableTool(
    name=__tool_name, 
    descriptor=__tool_description, 
    event_type=AireEvent.AgentSwitch,
    handler=__agent_switch
)
