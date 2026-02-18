# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from server import app
from errors import *
from utils.auth import *
from utils.token_utils import count_tokens

from bot.default import llm as DefaultLLM
from bot.chains.chat_abstract import (
    ChatAbstractChain, ChatSummaryChain, ChatKeywordChain
)
from aire.models.chat import (
    AireChatInput, 
    AireChatAbstract, 
    AireChatContext,
    AireChatStats
)
from aire.services.platform import get_platform_config

from typing import Annotated
from fastapi import Depends, Query, status
from fastapi.responses import Response

@app.post("/chat/abstract",
          name="Chat abstract (summary and keywords)",
          description="Generate abstract from a chat",
          tags=["Chat Processing"],
          response_description="Returns the generated abstract",
          response_model=AireChatAbstract)
async def chat_abstract(
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes or auth.platform == None:
        raise FORBIDDEN_EXCEPTION
    
    platform = get_platform_config(auth.platform)
    context = AireChatContext(input=input, platform=platform, auth=auth)
    return ChatAbstractChain.invoke(context)


@app.post("/chat/summary", 
          description="Summarize chat",
          tags=["Chat Processing"],
          response_description="Returns the summary as a string")
async def chat_summary(
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]
    ) -> str:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes or auth.platform == None:
        raise FORBIDDEN_EXCEPTION
    
    platform = get_platform_config(auth.platform)
    context = AireChatContext(input=input, platform=platform, auth=auth)
    return ChatSummaryChain.invoke(context)


@app.post("/chat/keywords", 
          description="Pick keywords from a chat",
          tags=["Chat Processing"],
          response_description="Returns a list of keywords")
async def chat_keywords(
    input: AireChatInput,              
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    regen: Annotated[bool, Query(
        description="Set to true if you wish to add randomness to the response"
        )] = False) -> list[str]:
    
    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatSummary in auth.scopes or auth.platform == None:
        raise FORBIDDEN_EXCEPTION
    
    platform = get_platform_config(auth.platform)
    context = AireChatContext(input=input, regen=regen, platform=platform, auth=auth)
    keywords = ChatKeywordChain.invoke(context)
    return list(map(lambda x: x.value, keywords or []))


@app.post("/chat/{bot_name}/stats", 
         description="Get statistics for a chat",
         tags=["Chat Processing"],
         response_description="Returns token count",
         response_model=AireChatStats)
async def chat_tokens(
    bot_name: str, 
    input: AireChatInput,
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    match bot_name:
        case "default":
            return AireChatStats(token_count=count_tokens(DefaultLLM.model_name, input))
        case _:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
     