"""
SIP Intelligence — Symbol Detection Service (YOLO + ConvNeXt)
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import structlog
from PIL import Image

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class DetectedSymbol:
    """A detected symbol with bounding box and classification."""
    x: float
    y: float
    width: float
    height: float
    class_name: str
    confidence: float
    crop_path: Optional[str] = None
    catalog_match: Optional[str] = None


class SymbolDetector:
    """Symbol detection using YOLO11 + ConvNeXt-Tiny classification."""

    _detector = None
    _classifier = None

    @classmethod
    def _load_detector(cls):
        if cls._detector is None:
            try:
                from ultralytics import YOLO
                model_path = Path("d:/newsas/ml/weights/yolo_sip_best.pt")
                if not model_path.exists():
                    model_path = Path(settings.symbol_detector_model)
                cls._detector = YOLO(str(model_path))
                logger.info("YOLO detector loaded", model=str(model_path))
            except Exception as e:
                logger.error("Failed to load YOLO", error=str(e))
                raise
        return cls._detector

    @classmethod
    def _load_classifier(cls):
        if cls._classifier is None:
            try:
                import timm
                import torch

                cls._classifier = timm.create_model(
                    settings.symbol_classifier_model,
                    pretrained=True,
                    num_classes=0,  # Feature extractor mode
                )
                cls._classifier.eval()
                logger.info("ConvNeXt classifier loaded")
            except Exception as e:
                logger.warning("ConvNeXt not available", error=str(e))
        return cls._classifier

    @classmethod
    def detect(
        cls,
        image: Image.Image,
        confidence_threshold: float = settings.symbol_detector_confidence,
    ) -> list[DetectedSymbol]:
        """Run symbol detection on an image."""
        detector = cls._load_detector()
        img_array = np.array(image)

        results = detector(img_array, conf=confidence_threshold, imgsz=800, verbose=False)

        detected = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = result.names.get(cls_id, f"class_{cls_id}")

                detected.append(DetectedSymbol(
                    x=float(x1),
                    y=float(y1),
                    width=float(x2 - x1),
                    height=float(y2 - y1),
                    class_name=class_name,
                    confidence=round(conf, 4),
                ))

        logger.info("Symbols detected", count=len(detected))
        return detected

    @classmethod
    def crop_symbol(cls, image: Image.Image, symbol: DetectedSymbol) -> Image.Image:
        """Crop a detected symbol from the source image."""
        return image.crop((
            int(symbol.x),
            int(symbol.y),
            int(symbol.x + symbol.width),
            int(symbol.y + symbol.height),
        ))

    @classmethod
    def classify_crop(cls, crop: Image.Image) -> dict:
        """Classify a symbol crop using ConvNeXt (pretrained features)."""
        classifier = cls._load_classifier()
        if classifier is None:
            return {"class": "UNKNOWN", "confidence": 0.0, "note": "Classifier not loaded"}

        import torch
        from torchvision import transforms

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        tensor = transform(crop.convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            features = classifier(tensor)

        return {
            "features": features.cpu().numpy().tolist()[0][:10],
            "note": "Pretrained features — SIP-specific classification requires fine-tuning",
        }

