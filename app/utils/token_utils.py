# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tiktoken
from aire.models.chat import AireChatInput

def count_tokens(model: str | None, chat_input: AireChatInput):
    encoding = tiktoken.encoding_for_model(model or "gpt-4o")
    tokens_per_message = 4

    chat_messages = chat_input.to_chat_messages()

    num_tokens = 0
    for message in chat_messages:
        if isinstance(message.content, str):
            num_tokens += len(encoding.encode(message.content))
            num_tokens += len(encoding.encode(message.role))
            num_tokens += tokens_per_message
    return num_tokens
