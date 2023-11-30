import json;
from langchain.prompts import HumanMessagePromptTemplate;
from langchain.chat_models.base import BaseChatModel
from ..models.user import AireUser

template = HumanMessagePromptTemplate.from_template("Summarize user info from the following JSON: {json_str}")

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
    prompt = template.format(json_str=data)
    print(f"Prompt: {prompt}")

    summary = model.invoke([prompt])
    print(f"Summary: {summary}")

    return summary.content
