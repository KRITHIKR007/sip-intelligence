"""
SIP Intelligence — Document Upload & Management API
"""
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.documents import Document, DocumentStatus, FileType, Page
from app.schemas import (
    DocumentResponse,
    DocumentStatusResponse,
    PageResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


def _resolve_file_type(filename: str) -> FileType:
    ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else ""
    try:
        return FileType(ext)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(t.value for t in FileType)}",
        )


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    project_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload a single document for processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate extension
    file_type = _resolve_file_type(file.filename)

    # Read content and compute checksum
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    checksum = hashlib.sha256(content).hexdigest()

    # Check for duplicate
    existing = await db.execute(
        select(Document).where(
            Document.project_id == project_id,
            Document.checksum_sha256 == checksum,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Duplicate file already exists in project")

    # Generate storage path
    doc_id = uuid.uuid4()
    safe_name = f"{doc_id}_{file.filename}"
    storage_path = f"documents/{project_id}/{safe_name}"

    # Store file via MinIO
    try:
        from app.services.storage import storage_service
        await storage_service.upload_bytes(
            settings.minio_bucket_documents, storage_path, content, file.content_type or "application/octet-stream"
        )
    except Exception:
        # Fallback: store locally for development
        local_path = Path("uploads") / str(project_id)
        local_path.mkdir(parents=True, exist_ok=True)
        (local_path / safe_name).write_bytes(content)

    doc = Document(
        id=doc_id,
        project_id=project_id,
        filename=safe_name,
        original_filename=file.filename,
        file_type=file_type,
        file_size=len(content),
        checksum_sha256=checksum,
        storage_path=storage_path,
        status=DocumentStatus.UPLOADED,
        uploaded_by=uuid.UUID(user_id),
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    # Queue processing task (non-blocking)
    try:
        from app.workers.tasks import process_document_task
        process_document_task.delay(str(doc.id))
        doc.status = DocumentStatus.QUEUED
        await db.flush()
    except Exception:
        pass  # Worker might not be running; doc stays UPLOADED

    return doc


@router.post("/bulk-upload", response_model=list[DocumentResponse], status_code=201)
async def bulk_upload(
    project_id: uuid.UUID = Form(...),
    files: list[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload multiple documents at once."""
    results = []
    for file in files:
        try:
            doc = await upload_document(
                project_id=project_id,
                file=file,
                user_id=user_id,
                db=db,
            )
            results.append(doc)
        except HTTPException:
            continue  # Skip problematic files, continue processing
    return results


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentStatusResponse(
        id=doc.id, status=doc.status.value, error_message=doc.error_message
    )


@router.get("/{document_id}/pages", response_model=list[PageResponse])
async def get_document_pages(
    document_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Page).where(Page.document_id == document_id).order_by(Page.page_number)
    )
    return result.scalars().all()


@router.post("/{document_id}/reprocess", response_model=DocumentStatusResponse)
async def reprocess_document(
    document_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = DocumentStatus.QUEUED
    doc.error_message = None
    doc.retry_count += 1
    await db.flush()

    try:
        from app.workers.tasks import process_document_task
        process_document_task.delay(str(doc.id))
    except Exception:
        pass

    return DocumentStatusResponse(id=doc.id, status=doc.status.value)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)

