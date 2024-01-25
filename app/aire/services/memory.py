import os
from pathlib import Path
from langchain.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..llm import EmbeddingsModel

store = PGVector.from_existing_index(EmbeddingsModel(), 
                                     collection_name="documents",
                                     connection_string=os.getenv("PGVECTOR_CONNECTION_STRING"))

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
