# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from langchain_core.messages.tool import ToolCall
from aire.models.reminder import AireReminder, AireReminderContent
from aire.models.chat import AireChatContext
from aire.models.events import AireEvent, AireReminderEvent
from aire.models.auth import AireScope
from aire.services.memory import create_reminder
from .callable_tool import CallableTool

__tool_name = "create_reminder"
__tool_description = {
    "type": "function",
    "function": {
        "name": __tool_name,
        "description": "Schedule reminders",
        "parameters": {
            "type": "object",
            "properties": {
                "date_and_time": {
                    "type": "string",
                    "description": "ISO Date Time formatted string"
                },
                "subject": {
                    "type": "string",
                    "description": "The subject or content of the reminder."
                }
            },
            "required": ["date_and_time", "subject"]
        }
    }
}

def __create_reminder_call(ctx: AireChatContext, date_and_time: str, subject: str) -> AireReminderEvent | None:
    timestamp = datetime.fromisoformat(date_and_time).timestamp()
    content = AireReminderContent(message=subject)    
    reminder = AireReminder(trigger_timestamp=int(timestamp), content=content, chat_id=ctx.input.chat_id)

    agent = ctx.current_agent()
    if agent == None:
        return None
    
    memory = next(iter(ctx.platform.get_agent_memories(agent)), None)
    if memory == None:
        return None
    
    reminder = create_reminder(memory, ctx.auth, reminder)
    return AireReminderEvent(reminder=reminder)


def __create_reminder(ctx: AireChatContext, call: ToolCall) -> AireReminderEvent | None:
    if call.get("name") != __tool_name:
        return None
    
    if not AireScope.ContentRead in ctx.auth.scopes:
        return None
    
    args = call.get("args")
    datetime = args.get("date_and_time")
    subject = args.get("subject")

    if datetime == None or subject == None:
        return None

    return __create_reminder_call(ctx, datetime, subject)


ReminderTool = CallableTool(
    name=__tool_name,
    descriptor=__tool_description,
    event_type=AireEvent.Reminder,
    prompt_gen=None,
    handler=__create_reminder
)
