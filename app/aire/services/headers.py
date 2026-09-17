# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from ..models.platform import (
    AireModuleAccess,
    AireServiceModule
)
from ..models.auth import AireAuth

def get_svc_headers(svc: AireServiceModule, auth: AireAuth | None, service_key: str | None) -> dict[str, str]:
    headers: dict[str, str] = {
        "Aire-Service-Target": svc.module.id
    }
    
    if service_key is not None:
        headers["Aire-Service-Key"] = service_key
    elif svc.module.access == AireModuleAccess.Service and svc.module.credentials != None:
        if svc.module.credentials.client_id != None:
            headers["Aire-Client-Id"] = svc.module.credentials.client_id
        if svc.module.credentials.client_secret != None:
            headers["Aire-Client-Secret"] = svc.module.credentials.client_secret
    else:
        token: str | None = None
        if auth != None:
            if svc.external == False:
                if auth != None and auth.token != None:
                    token = auth.token
            else:
                if auth.connected_services != None:
                    token = next(iter([x.token for x in auth.connected_services if x.service_name == svc.service_name]), None)

        if token != None:
            headers["Authorization"] = "Bearer " + token
        elif svc.module.access == AireModuleAccess.Private:
            raise RuntimeError("This module requires an access token")

    return headers

