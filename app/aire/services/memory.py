import os
# from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings.openai import OpenAIEmbeddings
# from ..models.user import AireUser

connection_string = os.getenv("PGVECTOR_CONNECTION_STRING")
embeddings = OpenAIEmbeddings(base_url=os.getenv("OPENAI_API_BASE"))

# CHAT_HISTORY_COLLECTION = "chat_history"
# db = PGVector.from_existing_index(embeddings, 
#                                   collection_name=CHAT_HISTORY_COLLECTION)

# def retrieve_chat_history(user: AireUser):
#     raise NotImplementedError()

# TODO: Similarity search
# TODO: Adding documents for RAG
