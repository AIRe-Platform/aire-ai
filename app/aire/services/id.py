# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import requests
import os
from ..models.platform import (
    AirePlatformConfiguration, 
    AireModuleType
)
from ..models.user import AireUser

def get_user(conf: AirePlatformConfiguration, auth: str):
    key = os.getenv("AIRE_SERVICE_KEY")

    if key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    svc = conf.get_default_module(AireModuleType.ID)
    if svc == None:
        raise RuntimeError("ID Module is not configured")
    
    url = svc.endpoint + "/v1/user"
    headers = {
        "Aire-Service-Key": key,
        "Accept": "application/json",
        "Authorization": auth
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return AireUser.model_validate(response.json())
    else:
        raise RuntimeError("Failed to get user data")
