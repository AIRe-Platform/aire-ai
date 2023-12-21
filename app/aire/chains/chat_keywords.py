import os
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.schema.runnable import  RunnableLambda
from ..models.chat import AireChatInput

llm = OpenAI(
    temperature=0.5, 
    base_url=os.getenv("OPENAI_API_BASE"),
    max_tokens=24)

parser = CommaSeparatedListOutputParser()
format_instructions = parser.get_format_instructions()

def __chat_keywords(input: AireChatInput) -> list[str]:
    prompt_template = """
Extract keywords from the following conversation.

{format_instructions}

Conversation:
{messages}
"""    
    keyword_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["messages"],
        partial_variables={"format_instructions": format_instructions})
    
    messages = ChatPromptTemplate.from_messages(input.toChatMessages())
    prompt = keyword_prompt.format(messages=messages.format())

    output = llm(prompt)
    words = parser.parse(output)
    return list(
        map(lambda x: 
            x.replace("Keywords", "").strip("\" ,.:;-/\n"), 
            words)
    )

ChatKeywordChain = RunnableLambda(__chat_keywords)