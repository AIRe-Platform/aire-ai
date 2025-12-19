# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
from aire.models.chat import AireChatContext
from aire.models.platform import AireModuleType

MODULE_ID = os.getenv("AIRE_MODULE_ID", "")

def get_module_setting_str(ctx: AireChatContext, setting: str, default: str | None = None) -> str | None:
    var = default
    try:
        module = ctx.platform.get_module(AireModuleType.AI, MODULE_ID)
        if module != None and module.settings != None:
            value = module.settings.get(setting, default)
            if isinstance(value, str):
                var = value
    except AttributeError:
        pass
    return var

def get_module_setting_int(ctx: AireChatContext, setting: str, default: int | None = None) -> int | None:
    var = default
    try:
        module = ctx.platform.get_module(AireModuleType.AI, MODULE_ID)
        if module != None and module.settings != None:
            value = module.settings.get(setting, default)
            if isinstance(value, int):
                var = value
    except AttributeError:
        pass
    return var

def get_module_setting_bool(ctx: AireChatContext, setting: str, default: bool | None = None) -> bool | None:
    var = default
    try:
        module = ctx.platform.get_module(AireModuleType.AI, MODULE_ID)
        if module != None and module.settings != None:
            value = module.settings.get(setting, default)
            if isinstance(value, bool):
                var = value
    except AttributeError:
        pass
    return var
