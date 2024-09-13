# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import requests
import os
import json
import ast
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

def post_event(event_data):
    key = os.getenv("AIRE_SERVICE_KEY")

    if key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    url = "http://172.22.176.1:7073/api" + "/v1/events"
    # url = svc.endpoint + "/v1/keywords"
    token = "Bearer " + "TODO: get token from ID service here." # TODO: get token from ID service
    headers = {
        "Authorization": token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # json_data = json.dumps(event_data)
    # print(json_data)

    # response = requests.post(url=url, headers=headers, data=json_data)
    response = requests.post(url=url, headers=headers, data="{ 'trigger_timestamp': 123456789, 'content': {'message': 'test'} }") # TODO: send real json

    if response.status_code == 200:
        json = response.json()
        return json
    else:
        raise RuntimeError("Failed to add event")