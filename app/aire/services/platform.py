# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os
import httpx
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from ..models.platform import AirePlatformConfiguration

def hash_key(id: str):
    return hashkey(id)

cache = TTLCache(maxsize=1, ttl=1800)

@cached(cache=cache, key=hash_key)
async def get_platform_config_async(id: str) -> AirePlatformConfiguration:
    base = os.getenv("AIRE_SERVICE_BASE")
    key = os.getenv("AIRE_SERVICE_KEY")
    
    if base == None or key == None:
        raise RuntimeError("Missing AIRe service configuration")
    
    url = base + "/v1/config/" + id + "/internal"
    headers = {
        "Aire-Service-Key": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    if response.status_code == 200:
        return AirePlatformConfiguration.model_validate(response.json())
    else:
        raise RuntimeError("Failed to request platform configuration")


