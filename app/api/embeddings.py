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

from bot.default import *
from bot.vector_stores import (
    DocumentVectorStore, 
    QuestionnaireVectorStore,
    ContentVectorStore
)

from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, Query, Body, status, UploadFile
from fastapi.responses import Response
from langchain_core.documents import Document

class DocumentQueryResponse(BaseModel):
    documents: list[Document]

class QuestionnaireQueryResponse(BaseModel):
    results: list[AireQuestionnaireMetadata]

class ContentQueryResponse(BaseModel):
    results: list[AireContentMetadata]

class EmbedResponse(BaseModel):
    ids: list[str]

@app.get("/embeddings/document",
         description="Find documents using similarity search",
         tags=["Document embeddings"],
         response_model=DocumentQueryResponse)
async def query_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query(description="Query")] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    if query == None:
        raise BAD_REQUEST_EXCEPTION
        
    store = DocumentVectorStore()
    docs = store.similarity_search(query)
    return DocumentQueryResponse(documents=docs)


@app.post("/embeddings/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Document embeddings"],
          response_model=EmbedResponse)
async def embed_document(
    document: UploadFile,
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentWrite in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    if document.size == None or document.size > 1024 * 16:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, 
                        content="The file is too large. The file must be 16 MB max.")
    
    store = DocumentVectorStore()
    
    if document.content_type == "application/pdf":
        handler = store.add_pdf
    elif document.content_type == "text/markdown":
        handler = store.add_markdown
    else:
        raise UNSUPPORTED_MEDIA_EXCEPTION
    
    path = None
    ids: list[str] | None = None

    try:
        path = await create_temporary_file(document)
        if path == None:
            raise Exception("Failed to store uploaded file")
        ids = handler(path, None)
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
    finally:
        if path != None: path.unlink()

    if ids != None:
        return EmbedResponse(ids=ids)
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.delete("/embeddings/document/{id}",
            description="Delete document embedding",
            tags=["Document embeddings"])
async def delete_document(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    id: str):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentDelete in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = DocumentVectorStore()
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Questionnaire embeddings
# ------------------------

@app.post("/embeddings/questionnaire",
          description="Create an embedding for a questionnaire",
          tags=["Questionnaire embeddings"],
          response_description="Returns a document ID for the created embedding",
          response_model=EmbedResponse)
async def embed_survey(
    questionnaire: Annotated[AireQuestionnaire, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireWrite in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = QuestionnaireVectorStore()
    id = store.add_questionnaire(questionnaire)
    return EmbedResponse(ids=[id])


@app.get("/embeddings/questionnaire",
         description="Perform similarity search using keywords to find questionnaires",
         tags=["Questionnaire embeddings"],
         response_description="Returns matching questionnaires' metadata in the order of relevance",
         response_model=QuestionnaireQueryResponse)
async def query_questionnaire(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query()] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = QuestionnaireVectorStore()
    results = store.query_keywords(query.split(","))
    return QuestionnaireQueryResponse(results=results)


@app.delete("/embeddings/questionnaire/{id}",
            description="Delete questionnaire embedding",
            tags=["Questionnaire embeddings"])
async def delete_survey(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    id: str):
    
    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.QuestionnaireDelete in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    store = QuestionnaireVectorStore()
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Content embeddings
# ------------------

@app.post("/embeddings/content",
          description="Create an embedding for content",
          tags=["Content embeddings"],
          response_description="Returns a document ID for the created embedding",
          response_model=EmbedResponse)
async def embed_content(
    content: Annotated[AireContent, Body()],
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.ContentWrite in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    store = ContentVectorStore()
    id = store.add_content(content)

    if id == None:
        raise BAD_REQUEST_EXCEPTION
    
    return EmbedResponse(ids=[id])


@app.get("/embeddings/content",
         description="Perform similarity search to find content",
         tags=["Content embeddings"],
         response_description="Returns matching contents' metadata in the order of relevance",
         response_model=ContentQueryResponse)
async def query_content(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    query: Annotated[str | None, Query()] = None):

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.ContentRead in auth.scopes:
            raise FORBIDDEN_EXCEPTION
        
    if query == None or len(query) == 0:
        raise BAD_REQUEST_EXCEPTION
    
    store = ContentVectorStore()
    results = store.query(query)
    return ContentQueryResponse(results=results)


@app.delete("/embeddings/content/{id}",
            description="Delete content embeddings",
            tags=["Content embeddings"])
async def delete_content(
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    id: str):
    
    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.ContentDelete in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    store = ContentVectorStore()
    store.remove_document(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
