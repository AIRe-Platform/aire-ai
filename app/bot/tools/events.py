# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from langchain_core.messages.tool import ToolCall
from aire.models.event import AireScheduledEvent, AireEventContent
from aire.models.chat import AireChatContext
from aire.models.platform import AireModuleType
from aire.services.memory import post_event

create_scheduled_event_tool = {
    "type": "function",
    "function": {
        "name": "create_scheduled_event",
        "description": "Schedule events and reminders",
        "parameters": {
            "type": "object",
            "properties": {
                "date_and_time": {
                    "type": "string",
                    "description": "ISO Date Time formatted string"
                },
                "subject": {
                    "type": "string",
                    "description": "The subject or content of the reminder event."
                }
            },
            "required": ["date_and_time", "subject"]
        }
    }
}

def _create_scheduled_event(ctx: AireChatContext, date_and_time: str, subject: str) -> AireScheduledEvent:
    print(f"Scheduled event '{subject}' at {date_and_time}")

    timestamp = datetime.fromisoformat(date_and_time).timestamp()
    content = AireEventContent(message=subject)
    event = AireScheduledEvent(trigger_timestamp=timestamp, content=content)

    memory = ctx.platform.platform.modules.get(AireModuleType.Memory)
    if memory != None:
        event = post_event(memory, ctx.auth, event)

    return event


def handle_event_tool_call(ctx: AireChatContext, call: ToolCall):
    if call.get("name") == "create_scheduled_event":
        args = call.get("args")
        return _create_scheduled_event(ctx, args.get("date_and_time"), args.get("subject"))
    else:
        return None
    