"""
SIP Intelligence — Validation Models
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Severity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ValidationStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ValidationRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "validation_rules"
    __table_args__ = {"schema": "sip"}

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_types: Mapped[Optional[dict]] = mapped_column(JSON)
    source_standard: Mapped[Optional[str]] = mapped_column(String(512))
    standard_revision: Mapped[Optional[str]] = mapped_column(String(64))
    rule_version: Mapped[str] = mapped_column(String(32), default="1.0")
    preconditions: Mapped[Optional[dict]] = mapped_column(JSON)
    evaluation_logic: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, schema="sip"), default=Severity.MEDIUM
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    results: Mapped[list["ValidationResult"]] = relationship(back_populates="rule")


class ValidationResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "validation_results"
    __table_args__ = {"schema": "sip"}

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.validation_rules.id"), nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id"), nullable=False
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.engineering_entities.id"), nullable=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.validation_jobs.id"), nullable=True
    )
    status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus, schema="sip"), nullable=False
    )
    expected_value: Mapped[Optional[str]] = mapped_column(Text)
    observed_value: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_notes: Mapped[Optional[str]] = mapped_column(Text)

    rule: Mapped["ValidationRule"] = relationship(back_populates="results")


class ValidationJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "validation_jobs"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id"), nullable=False
    )
    triggered_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, schema="sip"), default=JobStatus.PENDING
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rules_run: Mapped[int] = mapped_column(Integer, default=0)
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

