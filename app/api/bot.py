# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from server import app
from errors import *
from utils.auth import *
from utils.current_user import get_current_user, get_platform_config

from bot.default import *
from bot.chains.chat_keywords import ChatKeywordChain
from bot.toolbox import Toolbox
from aire.models.chat import *

import json
from typing import Annotated, AsyncIterator
from fastapi import Depends, HTTPException, status
from fastapi.responses import Response
from langserve.serialization import WellKnownLCSerializer
from langchain_core.messages.tool import ToolCall, ToolCallChunk
from sse_starlette import EventSourceResponse;

serializer = WellKnownLCSerializer()


@app.get("/bot", 
         description="List available bots",
         tags=["Chatbot"],
         response_description="List of bots")
async def get_bots(auth: Annotated[AireAuth | None, Depends(verify_token)]) -> list[AireChatbotInfo]:

    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise FORBIDDEN_EXCEPTION
    
    return [
        AireChatbotInfo(name="default", description="Default chat bot")
    ]


@app.post("/bot/{bot_name}/stream", 
          description="Stream completion",
          tags=["Chatbot"],
          response_description="Returns a stream of events",
          response_class=Response)
async def stream_bot(bot_name: str, 
                     input: AireChatInput,
                     auth: Annotated[AireAuth | None, Depends(verify_token)],
                     user: Annotated[AireUser | None, Depends(get_current_user)]):
    
    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.ChatCompletion in auth.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    match bot_name:
        case "default":
            bot = DefaultBot
        case _:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        
    allow_prompt_override = AireScope.ExperimentalCustomPrompt in auth.scopes
    context = AireChatContext(
        input=input, 
        user=user, 
        allow_custom_prompt=allow_prompt_override,
        platform=get_platform_config(),
        auth=auth)
    input_token_count = count_tokens(input)

    has_keywords = input.context.keywords != None and len(input.context.keywords) > 0
    gen_keywords = len(input.to_chat_messages()) > 4 and not has_keywords

    async def stream() -> AsyncIterator[dict]:
        try:
            output = ""
            tool_called = False
            iter = bot.astream(context)
            tool_calls: list[ToolCallChunk] = []

            async for chunk in iter:
                buffer = serializer.dumpd(chunk)

                if(buffer["content"]):
                    output += buffer["content"]
                    yield {
                        "event": "message",
                        "data": serializer.dumps({ 
                            "type": buffer["type"], 
                            "content": buffer["content"]
                        }).decode("utf-8")
                    }

                if(buffer["tool_call_chunks"]):
                    tool_chunks: list[ToolCallChunk] = buffer["tool_call_chunks"]
                    for tool_chunk in tool_chunks:
                        index = tool_chunk["index"]

                        if len(tool_calls) <= index:
                            tool_calls.append(ToolCallChunk(id="", name="", args="", index=index))
                        tc: ToolCallChunk = tool_calls[index]

                        if tool_chunk["id"]:
                            tc["id"] += tool_chunk["id"]
                        if tool_chunk["name"]:
                            tc["name"] += tool_chunk["name"]
                        if tool_chunk["args"]:
                            tc["args"] += tool_chunk["args"]

            for complete_chunk in tool_calls:
                call = ToolCall(
                    id=complete_chunk["id"], 
                    name=complete_chunk["name"], 
                    args=json.loads(complete_chunk["args"]))
                
                if call.get("name") in Toolbox and not tool_called:
                    tool = Toolbox[call.get("name")]
                    call_result = tool.handler(context, call)
                    if call_result != None:
                        tool_called = True
                        yield { 
                            "event": tool.event_type.value, 
                            "data": serializer.dumps(call_result).decode("utf-8")
                        }

            bot_message = ChatMessage(role="assistant", content=output)
            bot_input = AireChatInput(chat=[bot_message])
            output_token_count = count_tokens(bot_input)
            yield { 
                "event": "token-count",
                "data": output_token_count + input_token_count
            }

            if gen_keywords and not tool_called:
                keywords = await ChatKeywordChain.ainvoke(context)
                if len(keywords) > 0:
                    yield { 
                        "event": "keywords",
                        "data": serializer.dumps(keywords).decode("utf-8")
                    }

            yield { "event": "end" }
        except BaseException as ex:
            print(f"Error: {ex}")
            yield {
                "event": "error",
                "data": json.dumps({ 
                    "status_code": 500, 
                    "message": "Internal Server Error"
                })
            }

    return EventSourceResponse(stream())
