"""
SIP Intelligence Platform — FastAPI Main Application
"""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("Starting SIP Intelligence Platform", env=settings.app_env.value)

    # Ensure MinIO buckets exist
    try:
        from app.services.storage import storage_service
        await storage_service.ensure_buckets()
        logger.info("MinIO buckets verified")
    except Exception as e:
        logger.warning("MinIO not available", error=str(e))

    # Initialize Qdrant collections
    try:
        from app.services.embedding.vector_store import VectorStoreService
        vs = VectorStoreService()
        vs.ensure_collections()
        logger.info("Qdrant collections verified")
    except Exception as e:
        logger.warning("Qdrant not available", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down SIP Intelligence Platform")
    from app.db.session import engine
    await engine.dispose()


app = FastAPI(
    title="SIP Intelligence Platform",
    description=(
        "Multimodal Railway Signalling Plan Intelligence, Retrieval and "
        "Validation Platform. Provides document ingestion, symbol recognition, "
        "hybrid retrieval, engineering knowledge graph, drawing comparison, "
        "and standards-based validation for railway S&T engineering."
    ),
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- CORS (Permissive for local development & open model mode) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request ID Middleware ---
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": getattr(request.state, "request_id", "unknown")},
    )


# --- Include API Router ---
app.include_router(api_router)


# --- Root ---
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "SIP Intelligence Platform",
        "version": "0.1.0",
        "docs": "/api/docs",
    }

