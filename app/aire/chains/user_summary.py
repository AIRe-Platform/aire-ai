import json

from langchain.schema.messages import (
    HumanMessage, 
    SystemMessage
)
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import ChatPromptTemplate

from ..models.chat import AireChatContext
from ..llm import ChatModel

def __user_summary_prompt(ctx: AireChatContext):
    if ctx.user == None:
        summary = "No details available. You may ask relevant information from the user."
        if ctx.input.ui_lang != None:
            summary += f" The locale is '{ctx.input.ui_lang}'"
    else:
        data = json.dumps(ctx.user.dict(include={
            "first_name",
            "last_name", 
            "age", 
            "gender", 
            "language", 
            "country", 
            "bio"
        }))
        print(f"User data: {data}")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="Summarize the user information from the following object"),
            HumanMessage(content=data)
        ])

        summary = prompt | ChatModel(temperature=0) | StrOutputParser()

    return summary

UserSummaryChain = RunnableLambda(__user_summary_prompt)
