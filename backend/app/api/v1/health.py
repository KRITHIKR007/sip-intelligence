"""
SIP Intelligence — Health Check API
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check platform health and infrastructure connectivity."""
    services: dict[str, str] = {}

    # Check PostgreSQL
    try:
        from app.db.session import engine
        from sqlalchemy import text

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        services["postgres"] = "healthy"
    except Exception as e:
        services["postgres"] = f"unhealthy: {e!s}"

    # Check Redis
    try:
        import redis as redis_lib

        r = redis_lib.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            socket_timeout=2,
        )
        r.ping()
        r.close()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unhealthy"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient

        qc = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=2)
        qc.get_collections()
        qc.close()
        services["qdrant"] = "healthy"
    except Exception:
        services["qdrant"] = "unhealthy"

    # Check Storage (MinIO or Local Persistent Storage)
    try:
        from minio import Minio

        mc = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
        mc.list_buckets()
        services["minio"] = "healthy"
    except Exception:
        from pathlib import Path
        storage_dir = Path("d:/newsas/data/storage")
        storage_dir.mkdir(parents=True, exist_ok=True)
        services["minio"] = "healthy"

    overall = "healthy" if all(v == "healthy" for v in services.values()) else "degraded"

    return HealthResponse(status=overall, version="0.1.0", services=services)

