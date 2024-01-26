import json

from langchain.schema.messages import (
    HumanMessage, 
    SystemMessage
)
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda

from ..models.chat import AireChatContext
from ..llm import ChatModel

def __user_summary_prompt(ctx: AireChatContext) -> str:
    
    if ctx.user == None:
        summary = "No details available. You may ask relevant information from the user."
        if ctx.input.ui_lang != None:
            summary += f" The locale is '{ctx.input.ui_lang}'"
        return summary
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

        prompt = [
            SystemMessage(content="Summarize the user information from the following object"),
            HumanMessage(content=data)
        ]

        model_parser = ChatModel(temperature=0) | StrOutputParser()
        return model_parser.invoke(prompt)

UserSummaryChain = RunnableLambda(__user_summary_prompt)
