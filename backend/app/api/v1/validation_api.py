"""
SIP Intelligence — Validation API
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.validation import (
    JobStatus,
    ValidationJob,
    ValidationResult,
    ValidationRule,
)
from app.schemas import (
    ValidationJobResponse,
    ValidationResultResponse,
    ValidationRuleResponse,
    ValidationRunRequest,
)

router = APIRouter(prefix="/validation", tags=["Validation"])


@router.get("/rules", response_model=list[ValidationRuleResponse])
async def list_rules(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all configured validation rules."""
    result = await db.execute(
        select(ValidationRule).where(ValidationRule.is_active == True).order_by(ValidationRule.name)
    )
    return result.scalars().all()


@router.post("/run", response_model=ValidationJobResponse, status_code=201)
async def run_validation(
    body: ValidationRunRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Run validation rules against a document."""
    job = ValidationJob(
        document_id=body.document_id,
        triggered_by=uuid.UUID(user_id),
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Queue async processing
    try:
        from app.workers.tasks import run_validation_task
        run_validation_task.delay(str(job.id))
    except Exception:
        # Run synchronously if worker unavailable
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)

        # Get applicable rules
        rule_query = select(ValidationRule).where(ValidationRule.is_active == True)
        if body.rule_ids:
            rule_query = rule_query.where(ValidationRule.id.in_(body.rule_ids))
        rules = (await db.execute(rule_query)).scalars().all()

        job.rules_run = len(rules)
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        await db.flush()

    return job


@router.get("/{job_id}", response_model=ValidationJobResponse)
async def get_validation_job(
    job_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ValidationJob).where(ValidationJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Validation job not found")
    return job


@router.get("/{job_id}/results", response_model=list[ValidationResultResponse])
async def get_validation_results(
    job_id: uuid.UUID,
    severity: str | None = None,
    status_filter: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(ValidationResult, ValidationRule)
        .join(ValidationRule, ValidationResult.rule_id == ValidationRule.id)
        .where(ValidationResult.job_id == job_id)
    )
    if severity:
        query = query.where(ValidationRule.severity == severity)
    if status_filter:
        query = query.where(ValidationResult.status == status_filter)

    result = await db.execute(query)
    rows = result.all()

    return [
        ValidationResultResponse(
            id=vr.id,
            rule_name=rule.name,
            status=vr.status.value,
            severity=rule.severity.value,
            expected_value=vr.expected_value,
            observed_value=vr.observed_value,
            evidence=vr.evidence,
            entity_id=vr.entity_id,
            reviewed_by=vr.reviewed_by,
            review_notes=vr.review_notes,
        )
        for vr, rule in rows
    ]

