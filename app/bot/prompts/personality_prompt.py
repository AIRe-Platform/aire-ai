# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from aire.models.chat import AireChatContext
from aire.models.platform import AireModuleType, AireModuleSetting

def create_personality_prompt(ctx: AireChatContext):
    personality_prompt = ""

    try:
        module = ctx.platform.get_default_module(AireModuleType.AI)
        if module != None and module.settings != None:
            personality_prompt = module.settings.get(AireModuleSetting.PersonalityPrompt, "")
    except AttributeError:
        pass

    if ctx.allow_custom_prompt:
        if ctx.user and ctx.user.preferences:
            if ctx.user.preferences.experimental_custom_prompt is not None:
                personality_prompt = ctx.user.preferences.experimental_custom_prompt
        
    return personality_prompt

