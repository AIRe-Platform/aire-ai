# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from langchain_core.messages.tool import ToolCall
from aire.models.reminder import AireReminder, AireReminderContent
from aire.models.chat import AireChatContext
from aire.models.platform import AireModuleType
from aire.services.memory import create_reminder

create_reminder_tool = {
    "type": "function",
    "function": {
        "name": "create_reminder",
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

def _create_reminder(ctx: AireChatContext, date_and_time: str, subject: str) -> AireReminder:
    timestamp = datetime.fromisoformat(date_and_time).timestamp()
    content = AireReminderContent(message=subject)
    reminder = AireReminder(trigger_timestamp=timestamp, content=content, chat_id=ctx.input.chat_id)

    memory = ctx.platform.platform.modules.get(AireModuleType.Memory)
    if memory != None:
        event = create_reminder(memory, ctx.auth, reminder)

    return event


def handle_reminder_call(ctx: AireChatContext, call: ToolCall):
    if call.get("name") == "create_reminder":
        args = call.get("args")
        return _create_reminder(ctx, args.get("date_and_time"), args.get("subject"))
    else:
        return None
    