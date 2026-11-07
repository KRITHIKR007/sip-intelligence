"""
SIP Intelligence — Text Chunk and Visual Region Models
"""
from __future__ import annotations

import enum
import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RegionType(str, enum.Enum):
    IMAGE = "IMAGE"
    TABLE = "TABLE"
    DIAGRAM = "DIAGRAM"
    SYMBOL = "SYMBOL"
    TEXT_BLOCK = "TEXT_BLOCK"


class TextChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "text_chunks"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.pages.id", ondelete="SET NULL"), nullable=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    start_char: Mapped[Optional[int]] = mapped_column(Integer)
    end_char: Mapped[Optional[int]] = mapped_column(Integer)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255))
    model_name: Mapped[Optional[str]] = mapped_column(String(255))
    model_version: Mapped[Optional[str]] = mapped_column(String(64))

    document = relationship("Document", back_populates="chunks")
    page = relationship("Page", back_populates="chunks")


class VisualRegion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "visual_regions"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.pages.id", ondelete="CASCADE"), nullable=False
    )
    region_type: Mapped[RegionType] = mapped_column(
        "region_type", String(50), nullable=False, default=RegionType.IMAGE.value
    )
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    crop_path: Mapped[Optional[str]] = mapped_column(String(1024))
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    page = relationship("Page", back_populates="regions")

