"""COCO metrics"""
from __future__ import annotations
from typing import Any
import numpy as np


def compute_iou(box1: tuple[float, float, float, float],
                box2: tuple[float, float, float, float]) -> float:
    x1 = max(box1[0], box2[0]); y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2]); y2 = min(box1[3], box2[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    a1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    a2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    denom = a1 + a2 - inter
    return inter / denom if denom > 0 else 0.0


def compute_map(predictions: list[dict[str, Any]],
                ground_truth: list[dict[str, Any]],
                iou_thresholds: list[float] | None = None) -> dict[str, float]:
    if iou_thresholds is None:
        iou_thresholds = [0.5 + 0.05 * i for i in range(10)]
    if not predictions or not ground_truth:
        return {"mAP50": 0.0, "mAP50_95": 0.0, "precision": 0.0, "recall": 0.0}
    per_thresh: list[float] = []
    for thr in iou_thresholds:
        tp = 0; fp = 0
        gt_used = [False] * len(ground_truth)
        for pred in sorted(predictions, key=lambda p: -p.get("confidence", 0.0)):
            best_iou = 0.0; best_idx = -1
            for i, gt in enumerate(ground_truth):
                if gt_used[i]:
                    continue
                if gt.get("class_id") != pred.get("class_id"):
                    continue
                iou = compute_iou(
                    (pred["x1"], pred["y1"], pred["x2"], pred["y2"]),
                    (gt["x1"], gt["y1"], gt["x2"], gt["y2"]),
                )
                if iou > best_iou:
                    best_iou = iou; best_idx = i
            if best_iou >= thr and best_idx >= 0:
                tp += 1; gt_used[best_idx] = True
            else:
                fp += 1
        fn = sum(1 for u in gt_used if not u)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        per_thresh.append(precision * recall * 2.0 / (precision + recall)
                           if (precision + recall) > 0 else 0.0)
    mAP50 = per_thresh[0] if per_thresh else 0.0
    mAP50_95 = float(np.mean(per_thresh)) if per_thresh else 0.0
    return {"mAP50": mAP50, "mAP50_95": mAP50_95,
            "precision": per_thresh[0] if per_thresh else 0.0,
            "recall": per_thresh[0] if per_thresh else 0.0}
