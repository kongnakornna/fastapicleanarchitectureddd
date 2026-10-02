"""Unit tests for COCO metrics"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.helpers import compute_iou, compute_map

pytestmark = pytest.mark.unit


def test_iou_perfect():
    box = (0.0, 0.0, 1.0, 1.0)
    assert compute_iou(box, box) == 1.0


def test_iou_no_overlap():
    b1 = (0.0, 0.0, 1.0, 1.0)
    b2 = (2.0, 2.0, 3.0, 3.0)
    assert compute_iou(b1, b2) == 0.0


def test_map_perfect():
    preds = [{"class_id": 0, "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
    gts = [{"class_id": 0, "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
    result = compute_map(preds, gts)
    assert result["mAP50"] > 0.9


def test_map_empty():
    result = compute_map([], [])
    assert result["mAP50"] == 0.0
