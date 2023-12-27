import os
from pathlib import Path
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

connection_string = os.getenv("PGVECTOR_CONNECTION_STRING")
embeddings = OpenAIEmbeddings(base_url=os.getenv("OPENAI_API_BASE"))

DOCUMENTS_COLLECTION = "documents"
store = PGVector.from_existing_index(embeddings, collection_name=DOCUMENTS_COLLECTION)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True)

def store_pdf(filePath: Path):
    loader = PyPDFLoader(file_path=filePath.as_posix())
    docs = loader.load_and_split()
    splits = splitter.split_documents(docs)
    ids = store.add_documents(splits)
    print(f"Added documents: {ids}")

def store_markdown(filepath: Path):
    loader = UnstructuredMarkdownLoader(file_path=filepath.as_posix())
    docs = loader.load()
    splits = splitter.split_documents(docs)
    ids = store.add_documents(splits)
    print(f"Added documents: {ids}")

def query_documents(question: str):
    return store.similarity_search(question)

def get_retriever():
    return store.as_retriever()
