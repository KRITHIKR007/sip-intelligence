"""
SIP Intelligence — Celery Background Tasks
"""
from __future__ import annotations

import asyncio
import uuid
import structlog
from app.workers.celery_app import celery_app
from app.db.session import async_session_factory
from app.services.ingestion.pipeline import IngestionPipeline

logger = structlog.get_logger()

def _run_async(coro):
    return asyncio.run(coro)

@celery_app.task(name="app.workers.tasks.process_document_task", bind=True)
def process_document_task(self, document_id: str):
    logger.info("Executing process_document_task", document_id=document_id, task_id=self.request.id)
    async def _execute():
        async with async_session_factory() as session:
            pipeline = IngestionPipeline(session)
            success = await pipeline.process_document(document_id)
            await session.commit()
            return success
    return _run_async(_execute())

@celery_app.task(name="app.workers.tasks.run_validation_task", bind=True)
def run_validation_task(self, job_id: str):
    logger.info("Executing run_validation_task", job_id=job_id)
    async def _execute():
        from app.models.validation import ValidationJob, JobStatus
        from app.services.validation.rule_engine import RuleEngine
        from sqlalchemy import select
        from datetime import datetime, timezone

        async with async_session_factory() as session:
            result = await session.execute(
                select(ValidationJob).where(ValidationJob.id == uuid.UUID(job_id))
            )
            job = result.scalar_one_or_none()
            if not job:
                return False
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            await session.flush()

            engine = RuleEngine(session)
            findings = await engine.run_validation(job.document_id)

            job.rules_run = len(findings)
            job.findings_count = sum(1 for f in findings if f.status in ["FAIL", "REVIEW_REQUIRED"])
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            await session.commit()
            return True
    return _run_async(_execute())

@celery_app.task(name="app.workers.tasks.generate_embeddings_task", bind=True)
def generate_embeddings_task(self, document_id: str):
    logger.info("Generating embeddings for document", document_id=document_id)
    return True

