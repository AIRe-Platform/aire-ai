import os
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableLambda
from ..models.chat import AireChatSummary, AireChatInput

llm = OpenAI(temperature=0, 
             base_url=os.getenv("OPENAI_API_BASE"))

list_parser = CommaSeparatedListOutputParser()
format_instructions = list_parser.get_format_instructions()

def __chat_summarize(input: AireChatInput) -> str:
    history = ChatMessageHistory(messages=input.toChatMessages())
    memory = ConversationSummaryBufferMemory(chat_memory=history, llm=llm)
    return memory.predict_new_summary(memory.chat_memory.messages, "")

def __chat_keyword_prompt(input: AireChatInput) -> list[str]:
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
    return list_parser.parse(output)[:6]


def __summary(input: AireChatInput) -> AireChatSummary:
    chat_summary_chain = RunnableLambda(__chat_summarize)
    chat_keyword_chain = RunnableLambda(__chat_keyword_prompt)
    
    chains = RunnableParallel(
        summary=chat_summary_chain, 
        keywords=chat_keyword_chain)
    result = chains.invoke(input)

    return AireChatSummary(summary=result["summary"], keywords=result["keywords"])

ChatSummaryChain = RunnableLambda(__summary)
