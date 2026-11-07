"""
SIP Intelligence — OCR Service (PaddleOCR)
"""
from __future__ import annotations

import io
from typing import Any, Optional

import numpy as np
import structlog
from PIL import Image

logger = structlog.get_logger()


class OcrService:
    """OCR processing using PaddleOCR."""

    _engine = None

    @classmethod
    def _get_engine(cls):
        if cls._engine is None:
            try:
                from paddleocr import PaddleOCR
                cls._engine = PaddleOCR(
                    use_angle_cls=True,
                    lang="en",
                    show_log=False,
                    use_gpu=False,
                )
            except ImportError:
                logger.warning("PaddleOCR not available")
                return None
        return cls._engine

    async def process_image_bytes(self, image_bytes: bytes) -> dict[str, Any]:
        """Run OCR on image bytes and return text with confidence."""
        engine = self._get_engine()
        if engine is None:
            return {"text": "", "confidence": 0.0, "boxes": []}

        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)

        results = engine.ocr(img_array, cls=True)

        texts = []
        confidences = []
        boxes = []

        if results and results[0]:
            for line in results[0]:
                bbox = line[0]
                text = line[1][0]
                conf = line[1][1]
                texts.append(text)
                confidences.append(conf)
                boxes.append({
                    "text": text,
                    "confidence": round(conf, 4),
                    "bbox": [
                        [int(p[0]), int(p[1])] for p in bbox
                    ],
                })

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "text": "\n".join(texts),
            "confidence": round(avg_conf, 4),
            "boxes": boxes,
        }

    async def process_image_file(self, path: str) -> dict[str, Any]:
        """Run OCR on an image file path."""
        from pathlib import Path
        image_bytes = Path(path).read_bytes()
        return await self.process_image_bytes(image_bytes)

