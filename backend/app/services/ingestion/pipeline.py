"""
SIP Intelligence — Document Ingestion Pipeline Orchestrator
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Document, DocumentStatus, FileType, Page
from app.models.jobs import ProcessingJob, ProcessingJobStatus, ProcessingJobType

logger = structlog.get_logger()


class IngestionPipeline:
    """Orchestrates document processing based on file type."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_document(self, document_id: str) -> bool:
        """Main entry point — dispatch to the correct processor."""
        doc_uuid = uuid.UUID(document_id)

        result = await self.db.execute(
            select(Document).where(Document.id == doc_uuid)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            logger.error("Document not found", document_id=document_id)
            return False

        # Create processing job
        job = ProcessingJob(
            document_id=doc.id,
            job_type=ProcessingJobType.DOCUMENT_INGESTION.value,
            status=ProcessingJobStatus.RUNNING.value,
            started_at=datetime.now(timezone.utc),
            correlation_id=str(uuid.uuid4()),
        )
        self.db.add(job)

        doc.status = DocumentStatus.PROCESSING
        await self.db.flush()

        try:
            processor = self._get_processor(doc.file_type)
            pages_data = await processor.process(doc)

            # Store extracted pages
            for page_data in pages_data:
                page = Page(
                    document_id=doc.id,
                    page_number=page_data["page_number"],
                    width=page_data.get("width"),
                    height=page_data.get("height"),
                    text_content=page_data.get("text", ""),
                    has_images=page_data.get("has_images", False),
                    has_tables=page_data.get("has_tables", False),
                    render_path=page_data.get("render_path"),
                    ocr_text=page_data.get("ocr_text"),
                    ocr_confidence=page_data.get("ocr_confidence"),
                )
                self.db.add(page)

            doc.status = DocumentStatus.COMPLETED
            job.status = ProcessingJobStatus.COMPLETED.value
            job.progress_pct = 100.0
            job.completed_at = datetime.now(timezone.utc)

            logger.info(
                "Document processed successfully",
                document_id=document_id,
                pages=len(pages_data),
            )
            await self.db.flush()
            return True

        except Exception as e:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)[:2000]
            job.status = ProcessingJobStatus.FAILED.value
            job.error_message = str(e)[:2000]
            job.completed_at = datetime.now(timezone.utc)
            await self.db.flush()

            logger.error(
                "Document processing failed",
                document_id=document_id,
                error=str(e),
            )
            return False

    def _get_processor(self, file_type: FileType):
        """Return the appropriate processor for the file type."""
        from app.services.ingestion.pdf_processor import PdfProcessor
        from app.services.ingestion.image_processor import ImageProcessor
        from app.services.ingestion.cad_processor import CadProcessor
        from app.services.ingestion.office_processor import OfficeProcessor

        processors = {
            FileType.PDF: PdfProcessor,
            FileType.PNG: ImageProcessor,
            FileType.JPG: ImageProcessor,
            FileType.JPEG: ImageProcessor,
            FileType.DXF: CadProcessor,
            FileType.DWG: CadProcessor,
            FileType.XLSX: OfficeProcessor,
            FileType.XLS: OfficeProcessor,
            FileType.CSV: OfficeProcessor,
            FileType.DOCX: OfficeProcessor,
            FileType.DOC: OfficeProcessor,
        }
        cls = processors.get(file_type)
        if not cls:
            raise ValueError(f"No processor for file type: {file_type}")
        return cls()

