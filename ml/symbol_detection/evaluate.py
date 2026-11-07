"""
SIP Intelligence — Model Evaluation & Metrics (mAP, Precision, Recall)
"""
from __future__ import annotations

import numpy as np


def compute_iou(box1: list[float], box2: list[float]) -> float:
    """Calculate Intersection-over-Union for two bounding boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    b1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    b2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = b1_area + b2_area - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def evaluate_detections(
    predictions: list[dict],
    ground_truths: list[dict],
    iou_thresh: float = 0.5,
) -> dict:
    """Evaluate detected symbols against verified annotations."""
    tp = 0
    fp = 0
    fn = 0

    matched_gt = set()
    for p in predictions:
        match_found = False
        for idx, gt in enumerate(ground_truths):
            if idx in matched_gt:
                continue
            if p["class_id"] == gt["class_id"]:
                iou = compute_iou(p["bbox"], gt["bbox"])
                if iou >= iou_thresh:
                    tp += 1
                    matched_gt.add(idx)
                    match_found = True
                    break
        if not match_found:
            fp += 1

    fn = len(ground_truths) - len(matched_gt)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }

