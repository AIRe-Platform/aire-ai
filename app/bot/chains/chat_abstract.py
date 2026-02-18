# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from langchain_core.runnables import RunnableParallel
from .chat_keywords import ChatKeywordChain
from .chat_summary import ChatSummaryChain

ChatAbstractChain = RunnableParallel(
    summary=ChatSummaryChain,
    keywords=ChatKeywordChain
)
