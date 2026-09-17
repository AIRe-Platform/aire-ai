# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import httpx
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from .headers import get_svc_headers
from ..models.keyword import AireKeyword
from ..models.reminder import AireReminder
from ..models.platform import AireServiceModule
from ..models.auth import AireAuth;
from pydantic.type_adapter import TypeAdapter

def keywords_hash_key(svc: AireServiceModule, _: dict[str,str]):
    return hashkey(svc.module.id + svc.module.endpoint)

cache = TTLCache(maxsize=10, ttl=300)
    
@cached(cache=cache, key=keywords_hash_key)
async def _get_keywords_async_cached(svc: AireServiceModule, headers: dict[str,str]) -> list[AireKeyword]:
    url = svc.module.endpoint + "/v1/keywords"
    headers.update({
        "Accept": "application/json"
    })

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    if response.status_code == 200:
        adapter = TypeAdapter(list[AireKeyword])
        keywords = adapter.validate_python(response.json())
        return keywords
    else:
        raise RuntimeError("Failed to query keywords")


async def get_keywords_async(svc: AireServiceModule, auth: AireAuth) -> list[AireKeyword]:
    try:
        headers = get_svc_headers(svc, auth, None)
        return await _get_keywords_async_cached(svc, headers)
    except:
        return []

    
async def create_reminder_async(svc: AireServiceModule, auth: AireAuth, reminder: AireReminder) -> AireReminder:
    url = svc.module.endpoint + "/v1/reminder"
    headers = get_svc_headers(svc, auth, None)
    headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, json=reminder.model_dump())

    if response.status_code == 200:
        return AireReminder.model_validate(response.json())
    else:
        raise RuntimeError("Failed to create reminder")
    