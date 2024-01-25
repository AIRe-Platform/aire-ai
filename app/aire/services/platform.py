import requests
import os
from ..models.platform import AirePlatformConfiguration

def get_platform_config():
    base = os.getenv("AIRE_SERVICE_BASE")
    key = os.getenv("AIRE_SERVICE_KEY")

    if base == None or key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    url = base + "/v1/config/internal"
    headers = {
        "Aire-Service-Key": key,
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        json = response.json()
        return AirePlatformConfiguration.parse_obj(json)
    else:
        raise RuntimeError("Failed to request platform configuration")
    