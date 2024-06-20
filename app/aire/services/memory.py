import requests
import os
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from pydantic import parse_obj_as
from ..models.keyword import AireKeyword
from ..models.platform import (
    AirePlatformConfiguration, 
    AireModuleType
)

def hash_key(conf: AirePlatformConfiguration):
    return hashkey(conf.platform.name)

@cached(cache=TTLCache(maxsize=1, ttl=1800), key=hash_key)
def get_keywords(conf: AirePlatformConfiguration):
    key = os.getenv("AIRE_SERVICE_KEY")

    if key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    svc = conf.platform.modules.get(AireModuleType.Memory)
    if svc == None:
        raise RuntimeError("Memory Module is not configured")
    
    url = svc.endpoint + "/v1/keywords"
    headers = {
        "Aire-Service-Key": key,
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        json = response.json()    
        keywords = parse_obj_as(list[AireKeyword], json)
        return list(map(lambda x: x.value, keywords))
    else:
        raise RuntimeError("Failed to get keywords")
