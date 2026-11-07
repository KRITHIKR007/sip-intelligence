"""
SIP Intelligence — Pydantic Schemas
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")


# ---- Pagination -----------------------------------------------------------

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


# ---- Auth -----------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---- User -----------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: str = "VIEWER"
    department_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    department_id: Optional[uuid.UUID] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Department -----------------------------------------------------------

class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Project --------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    department_id: Optional[uuid.UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    status: str
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}


# ---- Document -------------------------------------------------------------

class DocumentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    checksum_sha256: str
    status: str
    version: int
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress: float = 0.0
    error_message: Optional[str] = None


class PageResponse(BaseModel):
    id: uuid.UUID
    page_number: int
    width: Optional[float] = None
    height: Optional[float] = None
    text_content: Optional[str] = None
    has_images: bool = False
    has_tables: bool = False
    render_path: Optional[str] = None
    ocr_confidence: Optional[float] = None

    model_config = {"from_attributes": True}


# ---- Engineering Entity ---------------------------------------------------

class EntityResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    label: Optional[str] = None
    x: float
    y: float
    width: float
    height: float
    confidence: Optional[float] = None
    detection_model: Optional[str] = None
    page_number: Optional[int] = None
    attributes: Optional[dict] = None

    model_config = {"from_attributes": True}


class SymbolCatalogResponse(BaseModel):
    id: uuid.UUID
    sno: int
    name: str
    function: str
    description: str
    category: str
    criticality: str
    image_path: Optional[str] = None
    page_ref: Optional[int] = None

    model_config = {"from_attributes": True}


# ---- Validation -----------------------------------------------------------

class ValidationRunRequest(BaseModel):
    document_id: uuid.UUID
    rule_ids: Optional[list[uuid.UUID]] = None


class ValidationRuleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    source_standard: Optional[str] = None
    severity: str
    is_active: bool

    model_config = {"from_attributes": True}


class ValidationResultResponse(BaseModel):
    id: uuid.UUID
    rule_name: str
    status: str
    severity: str
    expected_value: Optional[str] = None
    observed_value: Optional[str] = None
    evidence: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    reviewed_by: Optional[uuid.UUID] = None
    review_notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ValidationJobResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    status: str
    rules_run: int = 0
    findings_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---- Chat -----------------------------------------------------------------

class ChatQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    project_id: Optional[uuid.UUID] = None
    document_ids: Optional[list[uuid.UUID]] = None
    query_type: Optional[str] = None


class SourceCitation(BaseModel):
    document_id: uuid.UUID
    document_name: str
    page_number: Optional[int] = None
    chunk_text: Optional[str] = None
    relevance_score: float = 0.0
    coordinates: Optional[dict] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = []
    query_type: str = "general"
    confidence: float = 0.0
    processing_time_ms: float = 0.0


# ---- Comparison -----------------------------------------------------------

class CompareRequest(BaseModel):
    drawing_id_a: uuid.UUID
    drawing_id_b: uuid.UUID


class ComparisonDiff(BaseModel):
    entity_type: str
    label: Optional[str] = None
    change_type: str  # ADDED, REMOVED, MODIFIED
    details: Optional[dict] = None


class ComparisonResponse(BaseModel):
    drawing_a_id: uuid.UUID
    drawing_b_id: uuid.UUID
    additions: list[ComparisonDiff] = []
    removals: list[ComparisonDiff] = []
    modifications: list[ComparisonDiff] = []
    summary: str = ""


# ---- Feedback -------------------------------------------------------------

class FeedbackCreate(BaseModel):
    resource_type: str  # "chat_response", "symbol_detection", "validation"
    resource_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    correction: Optional[dict] = None


# ---- Health ---------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    services: dict[str, str] = {}


# ---- Audit ----------------------------------------------------------------

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ---- Model Registry -------------------------------------------------------

class ModelRegistryResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    model_type: str
    embedding_dim: Optional[int] = None
    is_active: bool
    loaded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

