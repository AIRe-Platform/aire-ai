from pathlib import Path
from langchain.vectorstores.pgvector import PGVector
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..llm import EmbeddingsModel
from ..models.survey import AireSurvey

class BaseVectorStore:
    store: PGVector

    def __init__(self, store: PGVector):
        self.store = store

    def retriever(self):
        return self.store.as_retriever()
    
    def similarity_search(self, query: str):
        return self.store.similarity_search(query)

class DocumentVectorStore(BaseVectorStore):
    def __init__(self):
        super().__init__(
            PGVector.from_existing_index(EmbeddingsModel(), collection_name="documents")
        )
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True)

    def add_documents(self, docs: list[Document], source: str | None):
        if source != None:
            for d in docs: 
                d.metadata["source"] = source

        splits = self.splitter.split_documents(docs)
        ids = self.store.add_documents(splits)
        print(f"Added documents: {ids}")

    def add_pdf(self, filepath: Path, source: str | None):
        loader = PyPDFLoader(file_path=filepath.as_posix())
        docs = loader.load_and_split()
        self.add_documents(docs, source)

    def add_markdown(self, filepath: Path, source: str | None):
        loader = UnstructuredMarkdownLoader(file_path=filepath.as_posix())
        docs = loader.load()
        self.add_documents(docs, source)


class SurveyVectorStore(BaseVectorStore):
    def __init__(self):
        super().__init__(
            PGVector.from_existing_index(EmbeddingsModel(), collection_name="surveys")
        )

    def add_survey(self, survey: AireSurvey):
        # TODO: Crawl through the survey, pick keywords, and contruct document from those
        # TODO: Mark the survey id as source of the documents
        # TODO: Store vectors
        pass

    def query_keywords(self, keywords: list[str]) -> list[str]:
        # TODO: Perform similarity search with the keywords
        # TODO: Retrieve the keyword document
        # TODO: Read survey id from the document metadata
        # TODO: Return survey ID or retrieve it from the DB?
        return []
