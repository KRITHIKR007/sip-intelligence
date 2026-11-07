"""
SIP Intelligence — CAD Processor (DXF/DWG)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class CadProcessor:
    """Process CAD files — DXF via ezdxf, DWG via conversion adapter."""

    async def process(self, document) -> list[dict[str, Any]]:
        """Extract entities, layers, and text from CAD files."""
        from app.models.documents import FileType

        if document.file_type == FileType.DWG:
            return await self._process_dwg(document)

        return await self._process_dxf(document)

    async def _process_dxf(self, document) -> list[dict[str, Any]]:
        """Process DXF files using ezdxf."""
        content = await self._get_bytes(document)

        try:
            import ezdxf
            import io

            doc = ezdxf.read(io.BytesIO(content))
            msp = doc.modelspace()

            texts = []
            entities_info = []

            # Extract layers
            layers = [layer.dxf.name for layer in doc.layers]

            # Extract entities
            for entity in msp:
                entity_type = entity.dxftype()

                if entity_type == "TEXT":
                    texts.append(entity.dxf.text)
                    entities_info.append({
                        "type": "TEXT",
                        "text": entity.dxf.text,
                        "x": entity.dxf.insert.x,
                        "y": entity.dxf.insert.y,
                        "layer": entity.dxf.layer,
                    })
                elif entity_type == "MTEXT":
                    texts.append(entity.text)
                    entities_info.append({
                        "type": "MTEXT",
                        "text": entity.text,
                        "x": entity.dxf.insert.x,
                        "y": entity.dxf.insert.y,
                        "layer": entity.dxf.layer,
                    })
                elif entity_type == "INSERT":
                    # Block reference (potential symbol)
                    entities_info.append({
                        "type": "BLOCK_REF",
                        "block_name": entity.dxf.name,
                        "x": entity.dxf.insert.x,
                        "y": entity.dxf.insert.y,
                        "layer": entity.dxf.layer,
                        "scale_x": entity.dxf.xscale,
                        "scale_y": entity.dxf.yscale,
                    })
                elif entity_type in ("LINE", "POLYLINE", "LWPOLYLINE"):
                    entities_info.append({
                        "type": entity_type,
                        "layer": entity.dxf.layer,
                    })
                elif entity_type == "DIMENSION":
                    entities_info.append({
                        "type": "DIMENSION",
                        "layer": entity.dxf.layer,
                    })

            full_text = "\n".join(texts)

            return [{
                "page_number": 1,
                "width": None,
                "height": None,
                "text": full_text,
                "has_images": False,
                "has_tables": False,
                "render_path": None,
                "ocr_text": None,
                "ocr_confidence": None,
                "metadata": {
                    "layers": layers,
                    "entity_count": len(entities_info),
                    "text_count": len(texts),
                    "entities": entities_info[:100],  # Cap for storage
                },
            }]

        except Exception as e:
            logger.error("DXF processing failed", error=str(e))
            raise

    async def _process_dwg(self, document) -> list[dict[str, Any]]:
        """
        DWG processing requires an external ODA-based converter.
        This adapter attempts conversion if configured.
        """
        logger.warning(
            "DWG processing requires ODA File Converter. "
            "Convert DWG to DXF externally and re-upload.",
            document_id=str(document.id),
        )
        return [{
            "page_number": 1,
            "width": None,
            "height": None,
            "text": "DWG file requires external conversion to DXF. "
                    "Please convert using ODA File Converter and re-upload as DXF.",
            "has_images": False,
            "has_tables": False,
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

