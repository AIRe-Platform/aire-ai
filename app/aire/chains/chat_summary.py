import os
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.output_parsers import CommaSeparatedListOutputParser
from ..models.chat import AireChatSummary, AireChatInput

llm = OpenAI(temperature=0, 
             base_url=os.getenv("OPENAI_API_BASE"))

parser = CommaSeparatedListOutputParser()
format_instructions = parser.get_format_instructions()

keyword_prompt = PromptTemplate(
    template="Extract maximum of 5 keywords related to symptoms from the following text:\n<START>{summary}<END>\n{format_instructions}",
    input_variables=["summary"],
    partial_variables={"format_instructions": format_instructions})

def summarize_chat(input: AireChatInput) -> AireChatSummary:
    history = ChatMessageHistory(messages=input.toChatMessages())
    memory = ConversationSummaryBufferMemory(chat_memory=history, llm=llm)
    summary = memory.predict_new_summary(memory.chat_memory.messages, "")

    keywords_input = keyword_prompt.format(summary=summary)
    keywords_output = llm(keywords_input)
    keywords = parser.parse(keywords_output)

    return AireChatSummary(summary=summary, keywords=keywords)
