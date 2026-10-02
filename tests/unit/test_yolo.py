"""Unit tests for YOLO domain"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.enums import (
    DatasetStatus, ModelFormat, ModelType, TrainingStatus,
)
from app.modules.yolo.domain.value_objects import (
    AugConfig, Detection, TrainConfig,
)
from app.modules.yolo.domain.value_objects.bbox import BBox

pytestmark = pytest.mark.unit


class TestEnums:
    def test_dataset_status(self):
        assert DatasetStatus.DRAFT == "DRAFT"

    def test_model_types(self):
        assert ModelType.YOLOV8N == "yolov8n"

    def test_model_format(self):
        assert ModelFormat.ONNX == "onnx"

    def test_training_status(self):
        assert TrainingStatus.SUCCESS == "SUCCESS"


class TestBBox:
    def test_valid(self):
        b = BBox(x_center=0.5, y_center=0.5, width=0.2, height=0.3)
        assert b.x_center == 0.5

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            BBox(x_center=1.5, y_center=0.5, width=0.2, height=0.3)

    def test_to_xyxy(self):
        b = BBox(x_center=0.5, y_center=0.5, width=0.4, height=0.4)
        x1, y1, x2, y2 = b.to_xyxy(100, 100)
        assert x1 == 30.0
        assert x2 == 70.0

    def test_from_xyxy(self):
        b = BBox.from_xyxy(30, 30, 70, 70, 100, 100)
        assert abs(b.x_center - 0.5) < 1e-9


class TestDetection:
    def test_valid(self):
        d = Detection(bbox=BBox(0.5, 0.5, 0.2, 0.3), class_id=0,
                       class_name="person", confidence=0.9)
        assert d.confidence == 0.9

    def test_invalid_confidence(self):
        with pytest.raises(ValueError):
            Detection(bbox=BBox(0.5, 0.5, 0.2, 0.3), class_id=0,
                       class_name="x", confidence=1.5)


class TestTrainConfig:
    def test_defaults(self):
        c = TrainConfig()
        assert c.model_type == "yolov8n"
        assert c.epochs == 100

    def test_invalid_model_type(self):
        with pytest.raises(ValueError):
            TrainConfig(model_type="invalid")

    def test_invalid_epochs(self):
        with pytest.raises(ValueError):
            TrainConfig(epochs=0)


class TestAugConfig:
    def test_defaults(self):
        a = AugConfig()
        assert a.mosaic == 1.0

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            AugConfig(hsv_h=2.0)

    def test_to_dict(self):
        a = AugConfig()
        d = a.to_dict()
        assert "mosaic" in d
