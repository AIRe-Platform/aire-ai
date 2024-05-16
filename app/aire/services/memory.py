from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.markdown  import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..llm import EmbeddingsModel
from ..models.questionnaire import AireQuestionnaire
from ..models.document import AireDocumentMetadata

class BaseVectorStore:
    store: PGVector

    def __init__(self, store: PGVector):
        self.store = store

    def retriever(self):
        return self.store.as_retriever()
    
    def similarity_search(self, query: str):
        return self.store.similarity_search(query)
    
    def add_documents(self, docs: list[Document]) -> list[str]:
        ids = self.store.add_documents(docs)
        return ids
    
    def remove_document(self, id: str):
        self.store.delete([id])

class DocumentVectorStore(BaseVectorStore):
    def __init__(self):
        super().__init__(
            PGVector.from_existing_index(EmbeddingsModel(), collection_name="documents")
        )
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True)

    def add_pdf(self, filepath: Path, source: str | None) -> list[str]:
        loader = PyPDFLoader(file_path=filepath.as_posix())
        docs = loader.load_and_split(self.splitter)
        if source != None:
            for d in docs:
                d.metadata["source"] = source
        return self.add_documents(docs)

    def add_markdown(self, filepath: Path, source: str | None) -> list[str]:
        loader = UnstructuredMarkdownLoader(file_path=filepath.as_posix())
        docs = loader.load_and_split(self.splitter)
        if source != None:
            for d in docs:
                d.metadata["source"] = source
        return self.add_documents(docs)


class QuestionnaireVectorStore(BaseVectorStore):
    def __init__(self):
        super().__init__(
            PGVector.from_existing_index(EmbeddingsModel(), collection_name="questionnaires")
        )

    def add_questionnaire(self, questionnaire: AireQuestionnaire) -> str:

        # Crawl through the survey, pick keywords and other queryable properties
        keywords = questionnaire.keywords
        for section in questionnaire.content:
            if section.keywords != None:
                keywords.extend(section.keywords)
            for question in section.questions:
                if question.keywords != None:
                    keywords.extend(question.keywords)

        keywords.append(questionnaire.name)
        keywords = list(set(keywords))
        content = " ".join(keywords)

        # Create a document of the keywords and mark the questionnaire id as source of the documents
        # Store it in the vector store
        doc = Document(page_content=content)
        doc.metadata = {
            "source": questionnaire.id,
            "language": questionnaire.lang
        }

        ids = self.add_documents([doc])
        if len(ids) != 1:
            raise RuntimeError("Unexpected count of IDs")
        return ids[0]

    def query_keywords(self, keywords: list[str]) -> list[AireDocumentMetadata]:
        # Perform similarity search with the keywords and retrieve document
        query = " ".join(list(set(keywords)))
        results = self.store.similarity_search_with_relevance_scores(query, 8)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Read questionnaire id from the document metadata
        questionnaires = list(map(lambda x: AireDocumentMetadata(
            source=x[0].metadata["source"], 
            language=x[0].metadata["language"],
            relevance=x[1])
        , results))
        return questionnaires
