"""
SIP Intelligence — Office Document Processor (Excel, CSV, Word)
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class OfficeProcessor:
    """Process Excel, CSV, and Word documents."""

    async def process(self, document) -> list[dict[str, Any]]:
        from app.models.documents import FileType

        content = await self._get_bytes(document)

        if document.file_type in (FileType.XLSX, FileType.XLS):
            return await self._process_excel(content, document)
        elif document.file_type == FileType.CSV:
            return await self._process_csv(content, document)
        elif document.file_type in (FileType.DOCX, FileType.DOC):
            return await self._process_word(content, document)
        else:
            raise ValueError(f"Unsupported office format: {document.file_type}")

    async def _process_excel(self, content: bytes, document) -> list[dict[str, Any]]:
        """Process Excel files using openpyxl."""
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        pages = []

        for idx, sheet_name in enumerate(wb.sheetnames):
            ws = wb[sheet_name]
            rows_text = []
            for row in ws.iter_rows(values_only=True):
                row_str = " | ".join(str(cell) if cell is not None else "" for cell in row)
                if row_str.strip(" |"):
                    rows_text.append(row_str)

            pages.append({
                "page_number": idx + 1,
                "width": None,
                "height": None,
                "text": f"Sheet: {sheet_name}\n" + "\n".join(rows_text),
                "has_images": False,
                "has_tables": True,
                "render_path": None,
                "ocr_text": None,
                "ocr_confidence": None,
            })

        return pages

    async def _process_csv(self, content: bytes, document) -> list[dict[str, Any]]:
        """Process CSV files using pandas."""
        import pandas as pd

        df = pd.read_csv(io.BytesIO(content))
        text_lines = [" | ".join(str(v) for v in df.columns)]
        for _, row in df.iterrows():
            text_lines.append(" | ".join(str(v) for v in row))

        return [{
            "page_number": 1,
            "width": None,
            "height": None,
            "text": "\n".join(text_lines),
            "has_images": False,
            "has_tables": True,
            "render_path": None,
            "ocr_text": None,
            "ocr_confidence": None,
        }]

    async def _process_word(self, content: bytes, document) -> list[dict[str, Any]]:
        """Process Word documents using python-docx."""
        from docx import Document as DocxDocument

        doc = DocxDocument(io.BytesIO(content))
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                prefix = ""
                if para.style and para.style.name.startswith("Heading"):
                    level = para.style.name.replace("Heading ", "")
                    prefix = f"[H{level}] "
                paragraphs.append(prefix + para.text)

        # Extract tables
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text for cell in row.cells)
                if row_text.strip(" |"):
                    table_texts.append(row_text)

        full_text = "\n".join(paragraphs)
        if table_texts:
            full_text += "\n\n[Tables]\n" + "\n".join(table_texts)

        return [{
            "page_number": 1,
            "width": None,
            "height": None,
            "text": full_text,
            "has_images": False,
            "has_tables": len(doc.tables) > 0,
            "render_path": None,
            "ocr_text": None,
            "ocr_confidence": None,
        }]

    async def _get_bytes(self, document) -> bytes:
        try:
            from app.services.storage import storage_service
            from app.core.config import settings
            return await storage_service.download_bytes(
                settings.minio_bucket_documents, document.storage_path
            )
        except Exception:
            local = Path("uploads") / document.storage_path
            if local.exists():
                return local.read_bytes()
            raise

