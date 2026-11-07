"""
SIP Intelligence — YOLO11 Detector Integration
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image
import numpy as np


class YOLOSymbolDetector:
    """YOLO detector wrapper with inference and coordinate preservation."""

    def __init__(self, weights_path: str = "yolo11n.pt", conf_thresh: float = 0.25):
        self.weights_path = weights_path
        self.conf_thresh = conf_thresh
        self.model = None

    def _load(self):
        if self.model is None:
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.weights_path)
            except Exception as e:
                print(f"Warning: YOLO could not be loaded: {e}")
                self.model = None

    def detect(self, image: Image.Image | np.ndarray) -> list[dict]:
        self._load()
        if self.model is None:
            return []

        results = self.model(image, conf=self.conf_thresh, verbose=False)
        detections = []
        for r in results:
            if r.boxes is None:
                continue
            for b in r.boxes:
                xyxy = b.xyxy[0].cpu().numpy().tolist()
                conf = float(b.conf[0])
                cls_id = int(b.cls[0])
                name = r.names.get(cls_id, str(cls_id))
                detections.append({
                    "bbox": xyxy,
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": name,
                })
        return detections

