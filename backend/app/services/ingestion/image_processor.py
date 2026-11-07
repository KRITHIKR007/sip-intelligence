"""
SIP Intelligence — Image Processor (PNG/JPG)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class ImageProcessor:
    """Process raster images (PNG, JPG) — OCR and normalization."""

    async def process(self, document) -> list[dict[str, Any]]:
        """Process an image file as a single-page document."""
        content = await self._get_bytes(document)

        from PIL import Image
        import io

        img = Image.open(io.BytesIO(content))
        width, height = img.size

        # Normalize image with OpenCV
        import numpy as np
        img_array = np.array(img)

        try:
            import cv2
            # Convert to grayscale if color
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Deskew
            coords = np.column_stack(np.where(gray < 200))
            if len(coords) > 100:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if abs(angle) > 0.5:
                    (h, w) = gray.shape
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=255)

            # Adaptive thresholding for OCR improvement
            processed = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        except Exception:
            processed = img_array

        # OCR
        ocr_text = ""
        ocr_confidence = 0.0
        try:
            from app.services.ingestion.ocr_service import OcrService
            ocr = OcrService()
            import cv2
            _, buf = cv2.imencode('.png', processed if len(processed.shape) == 2 else img_array)
            result = await ocr.process_image_bytes(buf.tobytes())
            ocr_text = result.get("text", "")
            ocr_confidence = result.get("confidence", 0.0)
        except Exception as e:
            logger.warning("OCR failed on image", error=str(e))

        # Save render
        render_path = None
        try:
            render_dir = Path("uploads/renders") / str(document.id)
            render_dir.mkdir(parents=True, exist_ok=True)
            render_file = render_dir / "page_1.png"
            img.save(str(render_file))
            render_path = str(render_file)
        except Exception:
            pass

        return [{
            "page_number": 1,
            "width": width,
            "height": height,
            "text": ocr_text,
            "has_images": True,
            "has_tables": False,
            "render_path": render_path,
            "ocr_text": ocr_text,
            "ocr_confidence": ocr_confidence,
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

