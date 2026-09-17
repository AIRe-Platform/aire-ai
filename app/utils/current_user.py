# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os
from typing import Optional
from aire.services.platform import get_platform_config_async_cached
from aire.services.id import get_user_async
from aire.models.auth import AireAuth
from errors import *


async def get_current_user_async(auth: Optional[AireAuth]  = None):    
    try:
        if auth != None and auth.token != None and auth.platform != None:
            platform = await get_platform_config_async_cached(auth.platform)
            return await get_user_async(platform, auth)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise FORBIDDEN_EXCEPTION
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise UNAUTH_EXCEPTION
    return None
