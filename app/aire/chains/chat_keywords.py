from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.schema.runnable import  RunnableLambda
from ..models.chat import AireChatContext
from ..llm import LLM

parser = CommaSeparatedListOutputParser()
format_instructions = parser.get_format_instructions()

def __chat_keywords(ctx: AireChatContext) -> list[str]:
    temperature = 0.0
    if ctx.regen: temperature = 0.2

    llm = LLM(
        temperature=temperature,
        max_tokens=24)

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
    
    messages = ChatPromptTemplate.from_messages(ctx.input.toChatMessages())
    prompt = keyword_prompt.format(messages=messages.format())

    output = llm(prompt)
    print(f"Raw keyword response:\n'{output}'")

    output = output.replace("\n", ", ").replace("Keywords", "")
    output = parser.parse(output)
    output = map(lambda x: x.strip("\" ,.:;-/\n1234567890#"), output)
    output = list(filter(lambda x: len(x) > 0, output))

    print(f"Processed keywords: {output}")

    return output

ChatKeywordChain = RunnableLambda(__chat_keywords)
