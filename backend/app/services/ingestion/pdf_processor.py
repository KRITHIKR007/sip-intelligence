"""
SIP Intelligence — PDF Document Processor
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class PdfProcessor:
    """Extract text, pages, tables and images from PDF documents."""

    async def process(self, document) -> list[dict[str, Any]]:
        """Process a PDF document and extract page-level data."""
        pages_data = []

        try:
            # Try to get document bytes
            content = await self._get_document_bytes(document)

            import fitz  # PyMuPDF

            pdf = fitz.open(stream=content, filetype="pdf")

            for page_num in range(len(pdf)):
                page = pdf[page_num]
                page_data = {
                    "page_number": page_num + 1,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "text": page.get_text("text"),
                    "has_images": len(page.get_images()) > 0,
                    "has_tables": False,
                    "render_path": None,
                    "ocr_text": None,
                    "ocr_confidence": None,
                }

                # Check if page is scanned (mostly images, little text)
                text = page_data["text"].strip()
                if len(text) < 50 and page_data["has_images"]:
                    # Page likely scanned — run OCR
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes("png")
                        ocr_result = await self._run_ocr(img_bytes)
                        page_data["ocr_text"] = ocr_result.get("text", "")
                        page_data["ocr_confidence"] = ocr_result.get("confidence", 0.0)
                        if not text:
                            page_data["text"] = page_data["ocr_text"]
                    except Exception as e:
                        logger.warning("OCR failed", page=page_num + 1, error=str(e))

                # Try table extraction with pdfplumber
                try:
                    import pdfplumber

                    with pdfplumber.open(io.BytesIO(content)) as plumber:
                        plumber_page = plumber.pages[page_num]
                        tables = plumber_page.extract_tables()
                        if tables:
                            page_data["has_tables"] = True
                            # Append table text to page text
                            for table in tables:
                                for row in table:
                                    row_text = " | ".join(
                                        str(cell) for cell in row if cell
                                    )
                                    if row_text:
                                        page_data["text"] += f"\n{row_text}"
                except Exception:
                    pass

                # Render page image
                try:
                    pix = page.get_pixmap(dpi=150)
                    render_dir = Path("uploads/renders") / str(document.id)
                    render_dir.mkdir(parents=True, exist_ok=True)
                    render_path = render_dir / f"page_{page_num + 1}.png"
                    pix.save(str(render_path))
                    page_data["render_path"] = str(render_path)
                except Exception as e:
                    logger.warning("Page render failed", page=page_num + 1, error=str(e))

                pages_data.append(page_data)

            pdf.close()
            logger.info("PDF processed", document_id=str(document.id), pages=len(pages_data))

        except Exception as e:
            logger.error("PDF processing error", error=str(e))
            raise

        return pages_data

    async def _get_document_bytes(self, document) -> bytes:
        """Retrieve document bytes from storage."""
        try:
            from app.services.storage import storage_service
            from app.core.config import settings
            return await storage_service.download_bytes(
                settings.minio_bucket_documents, document.storage_path
            )
        except Exception:
            # Fallback: try local path
            local = Path("uploads") / document.storage_path
            if local.exists():
                return local.read_bytes()
            raise FileNotFoundError(f"Cannot retrieve document: {document.storage_path}")

    async def _run_ocr(self, image_bytes: bytes) -> dict:
        """Run OCR on an image."""
        try:
            from app.services.ingestion.ocr_service import OcrService
            ocr = OcrService()
            return await ocr.process_image_bytes(image_bytes)
        except Exception:
            return {"text": "", "confidence": 0.0}

