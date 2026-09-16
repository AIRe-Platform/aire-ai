# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import requests
from .headers import get_svc_headers
from ..models.platform import (
    AirePlatformConfiguration, 
    AireModuleType
)
from ..models.auth import AireAuth
from ..models.user import AireUser

def get_user(conf: AirePlatformConfiguration, auth: AireAuth):    
    svc = conf.get_default_module(AireModuleType.ID)
    if svc == None:
        raise RuntimeError("ID Module is not configured")
    
    url = svc.module.endpoint + "/v1/user"
    headers = get_svc_headers(svc, auth, None)
    headers.update({
        "Accept": "application/json"
    })

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return AireUser.model_validate(response.json())
    else:
        raise RuntimeError("Failed to get user data")

