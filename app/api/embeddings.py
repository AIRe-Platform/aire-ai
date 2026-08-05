# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from server import app
from errors import *
from utils.auth import *
from utils.temp_files import create_temporary_file

from aire.models.chat import *
from aire.models.questionnaire import *
from aire.models.content import *
from aire.models.documents import *

from bot.default import *
from bot.vector_stores import (
    DocumentVectorStore, 
    QuestionnaireVectorStore,
    ContentVectorStore
)

from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, Query, Body, File, Form, status, UploadFile
from fastapi.responses import Response

class DocumentQueryResponse(BaseModel):
    results: list[AireDocumentSearchResult]

class QuestionnaireQueryResponse(BaseModel):
    results: list[AireQuestionnaireMetadata]

class ContentQueryResponse(BaseModel):
    results: list[AireContentMetadata]

class EmbedResponse(BaseModel):
    ids: list[str]

@app.get("/embeddings/{database}/document",
         description="Find documents using similarity search",
         tags=["Document embeddings"],
         response_model=DocumentQueryResponse)
async def query_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str,
    query: Annotated[str | None, Query(description="Query")] = None,
    lang: Annotated[str | None, Query(description="Language")] = None,
    relevance: Annotated[float, Query()] = 0):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    if query == None:
        raise BAD_REQUEST_EXCEPTION

    store = DocumentVectorStore(database)
    results = store.query(query, lang, min_relevance=relevance)
    return DocumentQueryResponse(results=results)

@app.get("/embeddings/{database}/document/{id}",
         description="Search document using similarity search",
         tags=["Document embeddings"],
         response_model=DocumentQueryResponse)
async def search_from_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str,
    id: str,
    search: Annotated[str | None, Query()] = None,
    relevance: Annotated[float, Query()] = 0):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    if search == None:
        raise BAD_REQUEST_EXCEPTION
    
    store = DocumentVectorStore(database)
    results = store.query_from_doc(id, search, max_items=8, min_relevance=relevance)

    return DocumentQueryResponse(results=results)

@app.post("/embeddings/{database}/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Document embeddings"],
          response_model=EmbedResponse)
async def embed_document(
    document: Annotated[UploadFile, File()],
    metadata: Annotated[str, Form()],
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str):
    
    if not is_service:
        raise UNAUTH_EXCEPTION

    if document.size == None or document.size > 1024 * 1024 * 32:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, 
                        content="The file is too large. The file must be 32 MB max.")
    
    store = DocumentVectorStore(database)
    doc_metadata = AireDocumentMetadata.model_validate_json(metadata)
    
    if document.content_type == "application/pdf":
        handler = store.add_pdf
    elif document.content_type == "text/markdown":
        handler = store.add_markdown
    elif document.content_type == "text/plain":
        handler = store.add_plain_text
    elif document.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        handler = store.add_word_document
    else:
        raise UNSUPPORTED_MEDIA_EXCEPTION
    
    path = None
    ids: list[str] | None = None

    try:
        path = await create_temporary_file(document)
        if path == None:
            raise Exception("Failed to store uploaded file")
        ids = handler(path, doc_metadata)
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
    finally:
        if path != None: path.unlink()

    if ids != None:
        return EmbedResponse(ids=ids)
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.delete("/embeddings/{database}/document/{id}",
            description="Delete document embedding",
            tags=["Document embeddings"])
async def delete_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    id: str,
    database: str):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    store = DocumentVectorStore(database)
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Questionnaire embeddings
# ------------------------

@app.post("/embeddings/{database}/questionnaire",
          description="Create an embedding for a questionnaire",
          tags=["Questionnaire embeddings"],
          response_description="Returns a document ID for the created embedding",
          response_model=EmbedResponse)
async def embed_survey(
    questionnaire: Annotated[AireQuestionnaire, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    store = QuestionnaireVectorStore(database)
    id = store.add_questionnaire(questionnaire)
    return EmbedResponse(ids=[id])


@app.get("/embeddings/{database}/questionnaire",
         description="Perform similarity search using keywords to find questionnaires",
         tags=["Questionnaire embeddings"],
         response_description="Returns matching questionnaires' metadata in the order of relevance",
         response_model=QuestionnaireQueryResponse)
async def query_questionnaire(
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str,
    query: Annotated[str | None, Query()] = None,
    lang: Annotated[str | None, Query()] = None,
    relevance: Annotated[float, Query()] = 0):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = QuestionnaireVectorStore(database)
    results = store.query_keywords(query.split(","), lang, relevance)
    return QuestionnaireQueryResponse(results=results)


@app.delete("/embeddings/{database}/questionnaire/{id}",
            description="Delete questionnaire embedding",
            tags=["Questionnaire embeddings"])
async def delete_survey(
    is_service: Annotated[bool, Depends(check_service_key)],
    id: str,
    database: str):
    
    if not is_service:
        raise UNAUTH_EXCEPTION

    store = QuestionnaireVectorStore(database)
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Content embeddings
# ------------------

@app.post("/embeddings/{database}/content",
          description="Create an embedding for content",
          tags=["Content embeddings"],
          response_description="Returns a document ID for the created embedding",
          response_model=EmbedResponse)
async def embed_content(
    content: Annotated[AireContent, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    store = ContentVectorStore(database)
    id = store.add_content(content)

    if id == None:
        raise BAD_REQUEST_EXCEPTION
    
    return EmbedResponse(ids=[id])


@app.get("/embeddings/{database}/content",
         description="Perform similarity search to find content",
         tags=["Content embeddings"],
         response_description="Returns matching contents' metadata in the order of relevance",
         response_model=ContentQueryResponse)
async def query_content(
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str,
    query: Annotated[str | None, Query()] = None,
    lang: Annotated[str | None, Query()] = None,
    relevance: Annotated[float, Query()] = 0):

    if not is_service:
        raise UNAUTH_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = ContentVectorStore(database)
    results = store.query(query, lang, min_relevance=relevance)
    return ContentQueryResponse(results=results)


@app.delete("/embeddings/{database}/content/{id}",
            description="Delete content embeddings",
            tags=["Content embeddings"])
async def delete_content(
    is_service: Annotated[bool, Depends(check_service_key)],
    database: str,
    id: str):
    
    if not is_service:
        raise UNAUTH_EXCEPTION

    store = ContentVectorStore(database)
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
