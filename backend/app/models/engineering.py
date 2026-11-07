"""
SIP Intelligence — Engineering Entity, Attribute and Symbol Catalog Models
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime, Enum, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EntityType(str, enum.Enum):
    # Signals
    SIGNAL_2A_CL = "2A_CL"
    SIGNAL_3A_CL = "3A_CL"
    SIGNAL_4A_CL = "4A_CL"
    HOME = "HOME"
    STARTER = "STARTER"
    ADV_STARTER = "ADV_STARTER"
    DISTANT = "DISTANT"
    IBS = "IBS"
    AUTO = "AUTO"
    SEMI_AUTO = "SEMI_AUTO"
    CALL_ON = "CALL_ON"
    SHUNT = "SHUNT"
    PL_SHUNT = "PL_SHUNT"
    REPEATER = "REPEATER"
    ROUTE_IND = "ROUTE_IND"
    CO_ACT = "CO_ACT"
    GATE_SIG = "GATE_SIG"
    # Track and equipment
    POINT = "POINT"
    X_OVER = "X_OVER"
    TRAP = "TRAP"
    FPL = "FPL"
    FM = "FM"
    IRJ = "IRJ"
    TC = "TC"
    AC = "AC"
    DP = "DP"
    OVL = "OVL"
    CSR = "CSR"
    LC = "LC"
    CH = "CH"
    SPT = "SPT"
    LOC = "LOC"
    RR_EI = "RR_EI"
    GF = "GF"
    BUFFER = "BUFFER"
    SAND_HUMP = "SAND_HUMP"
    # Kavach
    KAVACH_N = "KAVACH_N"
    KAVACH_S = "KAVACH_S"
    KAVACH_T = "KAVACH_T"
    KAVACH_X = "KAVACH_X"
    KAVACH_D = "KAVACH_D"
    KAVACH_G = "KAVACH_G"
    KAVACH_L = "KAVACH_L"
    KAVACH_A = "KAVACH_A"
    TIN = "TIN"
    TAG_ID = "TAG_ID"
    MAIN_DUP = "MAIN_DUP"
    NOM_REV = "NOM_REV"
    SK_ID = "SK_ID"
    RFID_CHAINAGE = "RFID_CHAINAGE"
    # General
    BOARD = "BOARD"
    INDICATOR = "INDICATOR"
    TRACK = "TRACK"
    UNKNOWN = "UNKNOWN"


class EngineeringEntity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "engineering_entities"
    __table_args__ = {"schema": "sip"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.documents.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.pages.id", ondelete="SET NULL"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255))
    x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    width: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    detection_model: Mapped[Optional[str]] = mapped_column(String(255))
    classification_model: Mapped[Optional[str]] = mapped_column(String(255))
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.users.id"), nullable=True
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    attributes_json: Mapped[Optional[dict]] = mapped_column(JSON)
    source_coordinates: Mapped[Optional[dict]] = mapped_column(JSON)

    document = relationship("Document", back_populates="entities")
    page = relationship("Page", back_populates="entities")
    entity_attributes: Mapped[list["EntityAttribute"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )


class EntityAttribute(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "entity_attributes"
    __table_args__ = {"schema": "sip"}

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sip.engineering_entities.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(255))

    entity: Mapped["EngineeringEntity"] = relationship(back_populates="entity_attributes")


class SymbolCatalogEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "symbol_catalog"
    __table_args__ = {"schema": "sip"}

    sno: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    function: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    criticality: Mapped[str] = mapped_column(String(50), nullable=False)
    image_path: Mapped[Optional[str]] = mapped_column(String(1024))
    page_ref: Mapped[Optional[int]] = mapped_column(Integer)
    source_document: Mapped[Optional[str]] = mapped_column(String(512))
    width_px: Mapped[Optional[int]] = mapped_column(Integer)
    height_px: Mapped[Optional[int]] = mapped_column(Integer)

