# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import requests
import os
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from ..models.keyword import AireKeyword
from ..models.reminder import AireReminder
from ..models.platform import AireModule
from ..models.auth import AireAuth;
from pydantic.type_adapter import TypeAdapter

def keywords_hash_key(svc: AireModule):
    return hashkey(svc.endpoint)

cache = TTLCache(maxsize=1, ttl=300)

@cached(cache=cache, key=keywords_hash_key)
def get_keywords(svc: AireModule) -> list[AireKeyword]:
    key = os.getenv("AIRE_SERVICE_KEY")

    if key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    url = svc.endpoint + "/v1/keywords"
    headers = {
        "Aire-Service-Key": key,
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        adapter = TypeAdapter(list[AireKeyword])
        keywords = adapter.validate_python(response.json())
        return keywords
    else:
        raise RuntimeError("Failed to get keywords")
    

def create_reminder(svc: AireModule, auth: AireAuth, reminder: AireReminder) -> AireReminder:
    url = svc.endpoint + "/v1/reminder"
    headers = {
        "Authorization": "Bearer " + (auth.token or ""),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url=url, headers=headers, json=reminder.model_dump())
    if response.status_code == 200:
        return AireReminder.model_validate(response.json())
    else:
        raise RuntimeError("Failed to create reminder")
    