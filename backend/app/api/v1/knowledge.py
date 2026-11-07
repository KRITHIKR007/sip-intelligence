"""
SIP Intelligence — Knowledge Search, Symbol Catalog, Models, Feedback & Admin APIs
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.engineering import SymbolCatalogEntry
from app.models.jobs import AuditLog, ModelRegistry
from app.models.users import Department, User
from app.schemas import (
    AuditLogResponse,
    DepartmentCreate,
    DepartmentResponse,
    FeedbackCreate,
    ModelRegistryResponse,
    PaginatedResponse,
    SymbolCatalogResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

# ---------------------------------------------------------------------------
# Knowledge
# ---------------------------------------------------------------------------
knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@knowledge_router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
):
    """Search across the knowledge base using hybrid retrieval."""
    return {
        "query": q,
        "results": [],
        "message": "Upload and process documents to populate the knowledge base.",
    }


@knowledge_router.get("/symbols", response_model=list[SymbolCatalogResponse])
async def list_symbols(
    category: str | None = None,
    search: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List symbol catalog entries."""
    query = select(SymbolCatalogEntry).order_by(SymbolCatalogEntry.sno)
    if category:
        query = query.where(SymbolCatalogEntry.category == category)
    if search:
        query = query.where(
            SymbolCatalogEntry.name.ilike(f"%{search}%")
            | SymbolCatalogEntry.description.ilike(f"%{search}%")
        )
    result = await db.execute(query)
    entries = result.scalars().all()

    # If DB is empty, load from JSON catalog
    if not entries:
        catalog_path = Path("data/symbols/symbols_catalog.json")
        if catalog_path.exists():
            data = json.loads(catalog_path.read_text())
            return [
                SymbolCatalogResponse(
                    id=uuid.uuid4(),
                    sno=s["sno"],
                    name=s["name"],
                    function=s.get("function", ""),
                    description=s["description"],
                    category=s["category"],
                    criticality=s["criticality"],
                    image_path=s.get("image_file"),
                    page_ref=s.get("page"),
                )
                for s in data.get("symbols", [])
            ]
    return entries


@knowledge_router.get("/symbols/{symbol_id}", response_model=SymbolCatalogResponse)
async def get_symbol(
    symbol_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SymbolCatalogEntry).where(SymbolCatalogEntry.id == symbol_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return entry


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
models_router = APIRouter(prefix="/models", tags=["Models"])


@models_router.get("", response_model=list[ModelRegistryResponse])
async def list_models(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelRegistry).order_by(ModelRegistry.name))
    models = result.scalars().all()
    if not models:
        # Return default model info
        return [
            ModelRegistryResponse(
                id=uuid.uuid4(), name="BGE-M3", version="1.0",
                model_type="TEXT_EMBEDDING", embedding_dim=1024, is_active=True,
            ),
            ModelRegistryResponse(
                id=uuid.uuid4(), name="SigLIP2", version="1.0",
                model_type="VISUAL_EMBEDDING", embedding_dim=768, is_active=True,
            ),
            ModelRegistryResponse(
                id=uuid.uuid4(), name="BGE Reranker v2 M3", version="1.0",
                model_type="RERANKER", is_active=True,
            ),
            ModelRegistryResponse(
                id=uuid.uuid4(), name="YOLO11", version="pretrained",
                model_type="DETECTOR", is_active=True,
            ),
            ModelRegistryResponse(
                id=uuid.uuid4(), name="Seq2Vec", version="experimental",
                model_type="SEQ2VEC", embedding_dim=256, is_active=False,
            ),
            ModelRegistryResponse(
                id=uuid.uuid4(), name="R-GCN", version="experimental",
                model_type="RGCN", embedding_dim=256, is_active=False,
            ),
        ]
    return models


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
feedback_router = APIRouter(prefix="/feedback", tags=["Feedback"])


@feedback_router.post("", status_code=201)
async def submit_feedback(
    body: FeedbackCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    log = AuditLog(
        user_id=uuid.UUID(user_id),
        action="FEEDBACK_SUBMITTED",
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        details={"rating": body.rating, "comment": body.comment, "correction": body.correction},
    )
    db.add(log)
    return {"status": "received"}


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
admin_router = APIRouter(prefix="/admin", tags=["Administration"])


@admin_router.get("/users", response_model=list[UserResponse])
async def list_users(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@admin_router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    body: UserCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import get_password_hash

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=get_password_hash(body.password),
        role=body.role,
        department_id=body.department_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@admin_router.put("/users/{uid}", response_model=UserResponse)
async def update_user(
    uid: uuid.UUID,
    body: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    await db.flush()
    await db.refresh(user)
    return user


@admin_router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Department).order_by(Department.name))
    return result.scalars().all()


@admin_router.post("/departments", response_model=DepartmentResponse, status_code=201)
async def create_department(
    body: DepartmentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    dept = Department(name=body.name, description=body.description)
    db.add(dept)
    await db.flush()
    await db.refresh(dept)
    return dept


@admin_router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func

    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    if action:
        query = query.where(AuditLog.action == action)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=max(1, -(-total // page_size)),
    )

