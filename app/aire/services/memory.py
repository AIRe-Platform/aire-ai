# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import requests
import os
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from pydantic import parse_obj_as
from ..models.keyword import AireKeyword
from ..models.event import AireScheduledEvent;
from ..models.platform import (
    AirePlatformConfiguration, 
    AireModuleType,
    AireModule
)
from ..models.auth import AireAuth;

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

def post_event(svc: AireModule, auth: AireAuth, event: AireScheduledEvent) -> AireScheduledEvent:
    url = svc.endpoint + "/v1/events"
    headers = {
        "Authorization": "Bearer " + auth.token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(url=url, headers=headers, json=event.dict())

    if response.status_code == 200:
        return AireScheduledEvent.parse_obj(response.json())
    else:
        raise RuntimeError("Failed to add event")
    