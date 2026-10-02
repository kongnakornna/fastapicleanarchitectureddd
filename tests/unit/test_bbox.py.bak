"""Unit tests for BBox"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.value_objects.bbox import BBox

pytestmark = pytest.mark.unit


def test_bbox_boundary_values():
    BBox(0.0, 0.0, 1.0, 1.0)


def test_bbox_negative_center():
    with pytest.raises(ValueError):
        BBox(-0.1, 0.5, 0.2, 0.2)


def test_bbox_roundtrip():
    b1 = BBox(0.5, 0.5, 0.4, 0.4)
    x1, y1, x2, y2 = b1.to_xyxy(200, 200)
    b2 = BBox.from_xyxy(x1, y1, x2, y2, 200, 200)
    assert abs(b1.x_center - b2.x_center) < 1e-9
