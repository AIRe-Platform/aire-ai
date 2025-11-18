# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
from typing import Optional
from azure.cosmos import CosmosClient, PartitionKey
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores.azure_cosmos_db_no_sql import PreFilter, Condition
from langchain_community.vectorstores import AzureCosmosDBNoSqlVectorSearch #! Deprecated
#from langchain_azure_ai.vectorstores import AzureCosmosDBNoSqlVectorSearch #! Vector search mappings currently broken

from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.markdown  import UnstructuredMarkdownLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain_community.document_loaders.odt import UnstructuredODTLoader

from llm import EmbeddingsModel
from aire.models.questionnaire import AireQuestionnaire, AireQuestionnaireMetadata
from aire.models.content import AireContent, AireContentMetadata, AireContentType
from aire.models.documents import AireDocumentSearchResult, AireDocumentMetadata
from pathlib import Path

AZURE_COSMOS_DB_CONNECTION_STRING = os.getenv("AZURE_COSMOS_DB_CONNECTION_STRING", "")

class BaseVectorStore:
    store: AzureCosmosDBNoSqlVectorSearch

    def __init__(self, database: str, collection: str):
        self.store = AzureCosmosDBNoSqlVectorSearch(
            cosmos_client=CosmosClient.from_connection_string(AZURE_COSMOS_DB_CONNECTION_STRING),
            embedding=EmbeddingsModel(),
            database_name=database,
            container_name=collection,
            vector_embedding_policy={
                "vectorEmbeddings": [
                    {
                        "path": "/embedding",
                        "dataType": "float32",
                        "distanceFunction": "cosine",
                        "dimensions": 1536,
                    }
                ]
            },
            indexing_policy={
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": '/"_etag"/?'}],
                "vectorIndexes": [{"path": "/embedding", "type": "diskANN"}],
                "fullTextIndexes": [{"path": "/text"}],
            },
            cosmos_container_properties={ 
                "partition_key": PartitionKey(path="/id") 
            },
            cosmos_database_properties={},
            full_text_search_enabled=True,
            full_text_policy={
                "defaultLanguage": "en-US",
                "fullTextPaths": [{"path": "/text", "language": "en-US"}],
            },
            #? Add these when transitioning to langchain_azure_ai
            #? The text_field mapping is currently broken with the newer package
            # vector_search_fields={
            #     "text_field": "text",
            #     "embedding_field": "embedding"
            # }
        )
    
    def similarity_search(self, query: str, prefilter: Optional[PreFilter] = None):
        return self.store.similarity_search(query, pre_filter=prefilter)
    
    def similarity_search_by_relevance(self, query: str, count: int = 1, prefilter: Optional[PreFilter] = None):
        results = self.store.similarity_search_with_score(query, count, pre_filter=prefilter)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def add_documents(self, docs: list[Document]) -> list[str]:
        ids = self.store.add_documents(docs)
        return ids
    
    def remove_document(self, id: str):
        try:
            self.store.delete([id])
        except:
            pass
        

class DocumentVectorStore(BaseVectorStore):
    def __init__(self, database: str):
        super().__init__(database, "documents")
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True)
        
    def __convert_document_to_search_result(self, doc: Document, relevance: float) -> AireDocumentSearchResult:
        return AireDocumentSearchResult(
            id=doc.id,
            relevance=relevance,
            content=doc.page_content,
            metadata=AireDocumentMetadata.model_validate(doc.metadata))
    
    def add_file(self, loader: BaseLoader, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        docs = loader.load_and_split(self.splitter)
        if metadata == None:
            metadata = AireDocumentMetadata(filename=filepath.name)
        for d in docs:
            d.metadata = metadata.model_dump()
        return self.add_documents(docs)

    def add_pdf(self, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        loader = PyPDFLoader(file_path=filepath.as_posix())
        return self.add_file(loader, filepath, metadata)

    def add_markdown(self, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        loader = UnstructuredMarkdownLoader(file_path=filepath.as_posix())
        return self.add_file(loader, filepath, metadata)
    
    def add_plain_text(self, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        loader = TextLoader(file_path=filepath, autodetect_encoding=True)
        return self.add_file(loader, filepath, metadata)
    
    def add_word_document(self, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        loader = UnstructuredWordDocumentLoader(filepath)
        return self.add_file(loader, filepath, metadata)
    
    def add_odt_document(self, filepath: Path, metadata: AireDocumentMetadata | None) -> list[str]:
        loader = UnstructuredODTLoader(filepath)
        return self.add_file(loader, filepath, metadata)
    
    def query(self, search: str, max_items: int = 8, min_relevance: float = 0.0) -> list[AireDocumentSearchResult]:
        results = self.similarity_search_by_relevance(search, max_items)

        if min_relevance > 0.0:
            results = filter(lambda x: x[1] >= min_relevance, results)

        documents = list(map(lambda x: self.__convert_document_to_search_result(x[0], x[1]), results))
        return documents
    
    def query_from_doc(self, source_id: str, search: str, max_items: int = 8, min_relevance: float = 0.0) -> list[AireDocumentSearchResult]:
        prefilter = PreFilter(conditions=[Condition(property="metadata.source", operator="$eq", value=source_id)])
        results = self.similarity_search_by_relevance(search, max_items, prefilter)

        if min_relevance > 0.0:
            results = filter(lambda x: x[1] >= min_relevance, results)

        documents = list(map(lambda x: self.__convert_document_to_search_result(x[0], x[1]), results))
        return documents


class QuestionnaireVectorStore(BaseVectorStore):
    def __init__(self, database: str):
        super().__init__(database, "questionnaires")

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

    def query_keywords(self, keywords: list[str]) -> list[AireQuestionnaireMetadata]:
        # Perform similarity search with the keywords and retrieve document
        query = " ".join(list(set(keywords)))
        return self.query(query)

    
    def query(self, search: str, max_items: int = 8, min_relevance: float = 0.0) -> list[AireQuestionnaireMetadata]:
        results = self.similarity_search_by_relevance(search, max_items)

        if min_relevance > 0.0:
            results = filter(lambda x: x[1] >= min_relevance, results)

        # Read questionnaire id from the document metadata
        questionnaires = list(map(lambda x: AireQuestionnaireMetadata(
            id=x[0].metadata["source"], 
            language=x[0].metadata["language"],
            relevance=x[1])
        , results))

        return questionnaires


class ContentVectorStore(BaseVectorStore):
    def __init__(self, database: str):
        super().__init__(database, "content")

    def add_content(self, content: AireContent) -> str | None:
        embedding = ""

        if content.name != None:
            embedding += content.name + "\n"

        keywords = ""
        if content.keywords != None:
            keywords = ",".join(content.keywords)
            embedding += " ".join(content.keywords) + "\n"

        if content.description != None:
            embedding += content.description + "\n"

        embedding = embedding.strip()
        if len(embedding) == 0:
            return None

        # Create a document of the keywords and mark the questionnaire id as source of the documents
        # Store it in the vector store
        doc = Document(page_content=embedding)
        doc.metadata = {
            "source": content.id,
            "type": content.type,
            "keywords": keywords
        }

        ids = self.add_documents([doc])
        return ids[0]

    def query(self, search: str, max_items: int = 8, min_relevance: float = 0.0) -> list[AireContentMetadata]:
        results = self.similarity_search_by_relevance(search, max_items)

        if min_relevance > 0.0:
            results = filter(lambda x: x[1] >= min_relevance, results)

        def convert(doc: Document, relevance: float) -> AireContentMetadata:
            keywords: str = doc.metadata["keywords"]
            return AireContentMetadata(
                id=doc.metadata["source"],
                type=AireContentType(doc.metadata["type"]),
                keywords=keywords.split(","),
                relevance=relevance)

        content = list(map(lambda x: convert(x[0], x[1]), results))
        return content
