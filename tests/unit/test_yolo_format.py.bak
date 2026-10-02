"""Unit tests for YOLO format"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.helpers import (
    bbox_to_yolo, write_dataset_yaml, yolo_to_bbox,
)

pytestmark = pytest.mark.unit


def test_bbox_to_yolo():
    s = bbox_to_yolo(0, 0.5, 0.5, 0.2, 0.3)
    assert s.startswith("0 ")


def test_yolo_to_bbox_roundtrip():
    line = bbox_to_yolo(1, 0.25, 0.75, 0.1, 0.15)
    cid, x, y, w, h = yolo_to_bbox(line)
    assert cid == 1
    assert abs(x - 0.25) < 1e-6


def test_yolo_to_bbox_invalid():
    with pytest.raises(ValueError):
        yolo_to_bbox("0 0.5")


def test_write_dataset_yaml():
    yaml = write_dataset_yaml(["cat", "dog"], "/tmp/root",
                                {"train": "images/train", "val": "images/val"})
    assert "cat" in yaml
    assert "path:" in yaml
