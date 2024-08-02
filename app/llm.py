import os
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI

AZURE_OPENAI = os.getenv("OPENAI_API_TYPE") == "azure"

# Azure deployments
AZURE_DEFAULT_DEPLOYMENT_NAME = os.getenv("AZURE_DEFAULT_DEPLOYMENT", "chat")
AZURE_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o")
AZURE_EMBEDDINGS_DEPLOYMENT_NAME = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT_NAME", "embed")

# Models
LLM_DEFAULT_MODEL_NAME = os.getenv("LLM_DEFAULT_MODEL_NAME", "gpt-3.5-turbo-1106")
LLM_CHAT_MODEL_NAME = os.getenv("LLM_CHAT_MODEL_NAME", "gpt-4o")
LLM_EMBEDDINGS_MODEL_NAME = os.getenv("LLM_EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")

def DefaultModel(temperature: float = 0.0, max_tokens: int = 256):
    """Model for general tasks such as summarization and tagging"""
    if AZURE_OPENAI:
        return AzureChatOpenAI(
            azure_deployment=AZURE_DEFAULT_DEPLOYMENT_NAME,
            model=LLM_DEFAULT_MODEL_NAME,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        return ChatOpenAI(
            model=LLM_DEFAULT_MODEL_NAME,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
def ChatModel(temperature: float = 0.7):
    """Model for chatting"""
    if AZURE_OPENAI:
        return AzureChatOpenAI(
            azure_deployment=AZURE_CHAT_DEPLOYMENT_NAME,
            model=LLM_CHAT_MODEL_NAME,
            temperature=temperature
        )
    else:
        return ChatOpenAI(
            model=LLM_CHAT_MODEL_NAME,
            temperature=temperature
        )
    
def EmbeddingsModel():
    """Model for embeddings, RAG"""
    if AZURE_OPENAI:
        return AzureOpenAIEmbeddings(
            azure_deployment=AZURE_EMBEDDINGS_DEPLOYMENT_NAME,
            model=LLM_EMBEDDINGS_MODEL_NAME,
        )
    else:
        return OpenAIEmbeddings(
            model=LLM_EMBEDDINGS_MODEL_NAME
        )
    