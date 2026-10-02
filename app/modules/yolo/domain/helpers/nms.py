"""NMS helper"""
from __future__ import annotations
from .coco_metrics import compute_iou


def non_max_suppression(
    boxes: list[tuple[float, float, float, float]],
    scores: list[float],
    iou_threshold: float = 0.45,
) -> list[int]:
    if not boxes:
        return []
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    keep: list[int] = []
    while order:
        i = order.pop(0)
        keep.append(i)
        remaining: list[int] = []
        for j in order:
            if compute_iou(boxes[i], boxes[j]) < iou_threshold:
                remaining.append(j)
        order = remaining
    return keep
