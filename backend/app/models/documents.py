"""
SIP Intelligence — Document, Project, Page Models
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.users import ProjectPermission
    from app.models.chunks import TextChunk, VisualRegion
    from app.models.engineering import EngineeringEntity


# ---- Enums ----------------------------------------------------------------

class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    SUSPENDED = "SUSPENDED"


class FileType(str, enum.Enum):
    PDF = "PDF"
    PNG = "PNG"
    JPG = "JPG"
    JPEG = "JPEG"
    DWG = "DWG"
    DXF = "DXF"
    XLSX = "XLSX"
    XLS = "XLS"
    CSV = "CSV"
    DOCX = "DOCX"
    DOC = "DOC"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PARTIALLY_PROCESSED = "PARTIALLY_PROCESSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    AWAITING_REVIEW = "AWAITING_REVIEW"


# ---- Models ---------------------------------------------------------------

class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = {"schema": "sip"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.departments.id"), nullable=True
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, schema="sip"), default=ProjectStatus.ACTIVE
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )

    documents: Mapped[list["Document"]] = relationship(back_populates="project")
    permissions: Mapped[list["ProjectPermission"]] = relationship(back_populates="project")


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "documents"
    __table_args__ = {"schema": "sip"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.projects.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType, schema="sip"), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, schema="sip"), default=DocumentStatus.UPLOADED
    )
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id"), nullable=True
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    project: Mapped["Project"] = relationship(back_populates="documents")
    pages: Mapped[list["Page"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document")
    chunks: Mapped[list["TextChunk"]] = relationship(back_populates="document")
    entities: Mapped[list["EngineeringEntity"]] = relationship(back_populates="document")


class DocumentVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_versions"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    change_description: Mapped[Optional[str]] = mapped_column(Text)

    document: Mapped["Document"] = relationship(back_populates="versions")


class Page(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pages"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[Optional[float]] = mapped_column(Float)
    height: Mapped[Optional[float]] = mapped_column(Float)
    dpi: Mapped[Optional[int]] = mapped_column(Integer)
    text_content: Mapped[Optional[str]] = mapped_column(Text)
    has_images: Mapped[bool] = mapped_column(Boolean, default=False)
    has_tables: Mapped[bool] = mapped_column(Boolean, default=False)
    render_path: Mapped[Optional[str]] = mapped_column(String(1024))
    ocr_text: Mapped[Optional[str]] = mapped_column(Text)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="pages")
    chunks: Mapped[list["TextChunk"]] = relationship(back_populates="page")
    regions: Mapped[list["VisualRegion"]] = relationship(back_populates="page")
    entities: Mapped[list["EngineeringEntity"]] = relationship(back_populates="page")

