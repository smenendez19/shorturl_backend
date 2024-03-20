# ShortURL FastAPI Project

# Imports
import logging
import os

import uvicorn
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse, RedirectResponse
from sqlmodel import SQLModel

# Database
from app.db.database import engine

# Routers
from app.routes.shorturl.shorturl import router as shorturl_router

# Logging
logging.config.fileConfig(
    os.path.join(os.path.dirname(__file__), "config", "logging.conf"),
    disable_existing_loggers=False,
)

# Create SQLite database
SQLModel.metadata.create_all(engine)

tags_metadata = [
    {
        "name": "ShortURL",
        "description": "ShortURL Endpoints",
    }
]

app = FastAPI(
    title="FastAPI ShortURL",
    description="A ShortURL API built with FastAPI",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

origins = ["http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# Routers
app.include_router(shorturl_router)


@app.get("/docs", include_in_schema=True, tags=["Docs"])
async def get_documentation_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger ShortURL API Docs")


@app.get("/redoc", include_in_schema=True, tags=["Docs"])
async def get_documentation_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="Redoc ShortURL API Docs")


@app.get("/openapi.json", include_in_schema=True, tags=["Docs"])
async def get_openapi_definitions():
    return get_openapi(
        title="OpenAPI ShortURL API Docs",
        description="OpenAPI ShortURL API Docs",
        version="1.0.0",
        routes=app.routes,
        tags=tags_metadata,
    )


@app.get("/", tags=["Docs"], include_in_schema=False)
async def get_docs():
    """
    Access to documentation in /docs
    """
    return RedirectResponse(url="/docs/")


# Exceptions


# Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors_details = []
    # Check type error
    for error in exc.__dict__["_errors"]:
        errors_details.append({"msg": error["msg"], "loc": ".".join(error["loc"]), "type": error["type"]})
        logging.error(f"Validation error: {error}")
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": errors_details},
    )


# Main
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
