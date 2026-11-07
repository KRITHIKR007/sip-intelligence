"""
SIP Intelligence — Processing Job and Audit Models
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessingJobType(str, enum.Enum):
    DOCUMENT_INGESTION = "DOCUMENT_INGESTION"
    TEXT_EXTRACTION = "TEXT_EXTRACTION"
    OCR = "OCR"
    EMBEDDING_GENERATION = "EMBEDDING_GENERATION"
    SYMBOL_DETECTION = "SYMBOL_DETECTION"
    ENTITY_EXTRACTION = "ENTITY_EXTRACTION"
    GRAPH_BUILD = "GRAPH_BUILD"
    VALIDATION = "VALIDATION"
    COMPARISON = "COMPARISON"
    REPROCESSING = "REPROCESSING"


class ProcessingJobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProcessingJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "processing_jobs"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[ProcessingJobType] = mapped_column(String(64), nullable=False)
    status: Mapped[ProcessingJobStatus] = mapped_column(String(32), default=ProcessingJobStatus.PENDING.value)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    worker_id: Mapped[Optional[str]] = mapped_column(String(255))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)


class AuditLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "sip"}

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class ModelRegistry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "model_registry"
    __table_args__ = {"schema": "sip"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    model_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024))
    config: Mapped[Optional[dict]] = mapped_column(JSON)
    embedding_dim: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)
    loaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

