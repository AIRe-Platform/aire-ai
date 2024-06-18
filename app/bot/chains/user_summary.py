import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from aire.models.chat import AireChatContext, AireChatInputContext
from llm import ChatModel

def __user_summary_prompt(ctx: AireChatContext) -> str:
    summary = ""
    info: AireChatInputContext | None = ctx.input.context
    
    if ctx.user == None:
        user_info = ""
        
        if info != None:
            if info.language != None:
                summary += f"The user speaks {info.language}."

            if info.age != None:
                user_info += f" The user is {info.age} years old."
            if info.occupation != None:
                user_info += f" The user's occupation is {info.occupation}."
        
        if len(user_info) > 0:
            summary += user_info
        else:
            summary += """
            The user has not provided any information about themselves.
            You may ask them about their age and occupation.
            """

        summary += "\nYou may ask the user for any relevant background information"

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

        prompt = [
            SystemMessage(content="Summarize the user information from the following object"),
            HumanMessage(content=data)
        ]

        model_parser = ChatModel(temperature=0) | StrOutputParser()
        summary = model_parser.invoke(prompt)

    if info != None and info.topic != None:
        summary += f"\nThe user wants to speak about {info.topic}."

    return summary

UserSummaryChain = RunnableLambda(__user_summary_prompt)
