import json
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain.chat_models.base import BaseChatModel
from ..models.user import AireUser

def summarize_user_context(user: AireUser, model: BaseChatModel):
    data = json.dumps(user.dict(include={
        "first_name",
        "last_name", 
        "age", 
        "gender", 
        "language", 
        "country", 
        "bio"
    }))
    print(f"User data: {data}")

    summary = model.invoke([
        SystemMessage(content="Summarize user info from the given JSON object."),
        HumanMessage(content=data)
    ])
    print(f"Summary: {summary}")

    return summary.content
