from server import app
from errors import *
from utils.auth import *
from utils.temp_files import create_temporary_file

from aire.models.chat import *
from aire.models.questionnaire import *
from aire.models.document import *

from bot.default import *
from bot.vector_stores import DocumentVectorStore, QuestionnaireVectorStore

from typing import Annotated
from fastapi import Depends, Query, Body, status, UploadFile
from fastapi.responses import Response
from langchain_core.documents import Document

class DocumentQueryResponse(BaseModel):
    documents: list[Document]

class QuestionnaireQueryResponse(BaseModel):
    results: list[AireDocumentMetadata]

class EmbedResponse(BaseModel):
    ids: list[str]

@app.get("/embeddings/document",
         description="Find documents using similarity search",
         tags=["Documents"],
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
        
    store = DocumentVectorStore()
    docs = store.similarity_search(query)
    return DocumentQueryResponse(documents=docs)


@app.post("/embeddings/document",
          description="Create embeddings and store a PDF or Markdown document",
          tags=["Documents"],
          response_model=EmbedResponse)
async def embed_document(
    document: UploadFile,
    is_service: Annotated[bool, Depends(check_service_key)],
    auth: Annotated[AireAuth | None, Depends(verify_token)]) -> Response:

    if not is_service:
        if auth == None:
            raise UNAUTH_EXCEPTION
        if not AireScope.DocumentWrite in auth.scopes:
            raise FORBIDDEN_EXCEPTION

    if document.size > 1024 * 16:
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
        ids = handler(path)
    except BaseException as ex:
        print(f"Failed to process document: {ex}")
    finally:
        if path != None: path.unlink()

    if ids != None:
        return EmbedResponse(ids=ids)
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.delete("/embeddings/document/{id}",
            description="Delete a document",
            tags=["Documents"])
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
          description="Create a document of the questionnaire for keyword searches",
          tags=["Questionnaires"],
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
         tags=["Questionnaires"],
         response_description="Returns matching questionnaire IDs in the order of relevance",
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
            description="Delete a questionnaire",
            tags=["Questionnaires"])
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
