# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os
from typing import Optional
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from aire.models.auth import AireAuth
from errors import *


def get_current_user(auth: Optional[AireAuth]  = None):    
    try:
        if auth != None and auth.token != None and auth.platform != None:
            platform = get_platform_config(auth.platform)
            return get_user(platform, auth.token)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise FORBIDDEN_EXCEPTION
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise UNAUTH_EXCEPTION
    return None
