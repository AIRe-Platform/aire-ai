from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    root_path="/api",
    docs_url="/swagger/ui",
    openapi_url="/swagger.json"
)

def openapi_docs():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        version="0.1.0",
        title="AIRe AI Module",
        description="This is the reference implementation of the AIRe AI module.",
        openapi_version="3.0.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = openapi_docs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

from api.bot import *
from api.chat import *
from api.embeddings import *
from api.questionnaires import *

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
