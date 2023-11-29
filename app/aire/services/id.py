import requests
import os
from ..models.platform import (
    AirePlatformConfiguration, 
    AireModuleType
)
from ..models.user import AireUser

def get_user(conf: AirePlatformConfiguration, token: str):
    base = os.getenv("AIRE_SERVICE_BASE")
    key = os.getenv("AIRE_SERVICE_KEY")

    if base == None or key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    svc_url = conf.platform.modules.get(AireModuleType.ID)
    if svc_url == None:
        raise RuntimeError("ID Module is not configured")
    
    url = svc_url + "/v1/user"
    headers = {
        "Aire-Service-Key": f"{key}",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        json = response.json()
        return AireUser.parse_obj(json)
    else:
        raise RuntimeError("Failed to get user data")
