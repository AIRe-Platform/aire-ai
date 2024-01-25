import os
from langchain_openai import AzureOpenAI, OpenAI, AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI

azure = os.getenv("OPENAI_API_TYPE") == "azure"

def LLM(temperature: float = 0.7, max_tokens: int = 256):
    if azure:
        return AzureOpenAI(
            azure_deployment="instruct",
            model="gpt-3.5-turbo-instruct",
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        return OpenAI(
            model="gpt-3.5-turbo-instruct",
            temperature=temperature,
            max_tokens=max_tokens
        )

def ChatModel(temperature: float = 0.7):
    if azure:
        return AzureChatOpenAI(
            azure_deployment="chat",
            model="gpt-3.5-turbo-1106",
            temperature=temperature
        )
    else:
        return ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=temperature
        )
    
def EmbeddingsModel():
    if azure:
        return AzureOpenAIEmbeddings(
            azure_deployment="embed",
            model="text-embedding-ada-002",
        )
    else:
        return OpenAIEmbeddings(
            model="text-embedding-ada-002"
        )
    