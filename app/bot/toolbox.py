# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Callable
from aire.models.chat import AireChatEvent
from .tools.reminders import ReminderTool
from .tools.questionnaire_query import QuestionnaireQueryTool
from .tools.content_query import ContentQueryTool
from .tools.keyword_tagging import KeywordTaggingTool

class CallableTool:
    name: str
    descriptor: dict
    event: AireChatEvent
    call: Callable


ToolBindings = [
    ReminderTool.descriptor, 
    QuestionnaireQueryTool.descriptor, 
<<<<<<< HEAD
    #ContentQueryTool.descriptor,
=======
#    ContentQueryTool.descriptor,
>>>>>>> 47da66af00c21537426870647b12112d93df01db
    KeywordTaggingTool.descriptor
]

Toolbox = {
    ReminderTool.name: ReminderTool,
    QuestionnaireQueryTool.name: QuestionnaireQueryTool,
    #ContentQueryTool.name: ContentQueryTool,
    KeywordTaggingTool.name: KeywordTaggingTool
}
