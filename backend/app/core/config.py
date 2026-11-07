"""
SIP Intelligence Platform — Application Configuration
"""
from __future__ import annotations

import enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "SIP Intelligence"
    app_env: Environment = Environment.DEVELOPMENT
    app_debug: bool = True
    app_secret_key: str = "change-me-to-a-random-64-char-string"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_workers: int = 2
    app_log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # --- PostgreSQL ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "sip_user"
    postgres_password: str = "sip_dev_password"
    postgres_db: str = "sip_intelligence"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --- Qdrant ---
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334
    qdrant_api_key: str = ""

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "sip_dev_password"

    # --- Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    @property
    def celery_broker_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def celery_result_backend(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/1"

    # --- MinIO ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket_documents: str = "sip-documents"
    minio_bucket_processed: str = "sip-processed"
    minio_bucket_symbols: str = "sip-symbols"
    minio_bucket_exports: str = "sip-exports"
    minio_use_ssl: bool = False

    # --- OpenSearch ---
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_user: str = "admin"
    opensearch_password: str = "admin"
    opensearch_index_prefix: str = "sip"

    # --- ML Models ---
    text_embedding_model: str = "BAAI/bge-m3"
    text_embedding_dim: int = 1024
    text_embedding_device: str = "cpu"
    text_embedding_batch_size: int = 8

    visual_embedding_model: str = "google/siglip2-base-patch16-224"
    visual_embedding_device: str = "cpu"
    visual_embedding_batch_size: int = 4

    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "cpu"

    symbol_detector_model: str = "yolo11n"
    symbol_detector_confidence: float = 0.25
    symbol_classifier_model: str = "convnext_tiny"

    ocr_engine: str = "paddleocr"
    ocr_lang: str = "en"

    # --- Chunking ---
    chunk_size: int = 512
    chunk_overlap: int = 80

    # --- Retrieval ---
    retrieval_top_k: int = 50
    rerank_top_k: int = 10
    dense_weight: float = 0.30
    bm25_weight: float = 0.20
    visual_weight: float = 0.20
    structural_weight: float = 0.15
    graph_weight: float = 0.15

    # --- External AI Gateway ---
    cloud_ai_enabled: bool = False
    cloud_ai_provider: str = ""
    cloud_ai_api_key: str = ""
    cloud_ai_model: str = ""

    # --- Auth ---
    jwt_secret_key: str = "change-me-jwt-secret-key-64-chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60

    # --- File Upload ---
    max_upload_size_mb: int = 500
    allowed_extensions: str = "pdf,png,jpg,jpeg,dwg,dxf,xlsx,xls,csv,docx,doc"

    @property
    def allowed_extension_list(self) -> list[str]:
        return [e.strip().lower() for e in self.allowed_extensions.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    # --- Processing ---
    max_concurrent_jobs: int = 4
    job_timeout_seconds: int = 3600


settings = Settings()

