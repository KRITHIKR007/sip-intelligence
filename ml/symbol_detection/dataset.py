"""
SIP Intelligence — YOLO Dataset Formatting and Conversion Tools
"""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image


def convert_annotations_to_yolo(
    image_width: int,
    image_height: int,
    boxes: list[dict],
) -> list[str]:
    """
    Convert bounding boxes to standard YOLO normalized coordinates:
    <class_id> <x_center> <y_center> <width> <height>
    """
    lines = []
    for b in boxes:
        cls_id = b["class_id"]
        x1, y1, x2, y2 = b["bbox"]

        box_w = x2 - x1
        box_h = y2 - y1
        x_c = x1 + box_w / 2.0
        y_c = y1 + box_h / 2.0

        # Normalize
        norm_xc = max(0.0, min(1.0, x_c / image_width))
        norm_yc = max(0.0, min(1.0, y_c / image_height))
        norm_w = max(0.0, min(1.0, box_w / image_width))
        norm_h = max(0.0, min(1.0, box_h / image_height))

        lines.append(f"{cls_id} {norm_xc:.6f} {norm_yc:.6f} {norm_w:.6f} {norm_h:.6f}")
    return lines

