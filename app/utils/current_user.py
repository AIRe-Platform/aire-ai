import os
from typing import Annotated
from fastapi import Header
from aire.services.platform import get_platform_config
from aire.services.id import get_user
from errors import *

def get_current_user(authorization: Annotated[str | None, Header()] = None):
    platform = get_platform_config()
    
    try:
        if authorization != None:
            return get_user(platform, authorization)
    except BaseException as e:
        print(f"Could not retrieve user data: {e}")
        raise FORBIDDEN_EXCEPTION
    
    if os.getenv("ALLOW_ANONYMOUS_USERS") != "1":
        raise FORBIDDEN_EXCEPTION
    return
