"""Unit tests for counting"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.applications.counting import (
    CountingConfig, ProductCounter,
)
from app.modules.yolo.domain.value_objects import BBox, Detection

pytestmark = pytest.mark.unit


def _mk(cx, cy, cls=0, name="cola", conf=0.9):
    return Detection(bbox=BBox(cx, cy, 0.1, 0.1), class_id=cls,
                      class_name=name, confidence=conf)


def test_config_invalid_mode():
    with pytest.raises(ValueError):
        CountingConfig(mode="invalid")


def test_count_shelf_two_rows():
    dets = [_mk(0.2, 0.2), _mk(0.4, 0.2),
            _mk(0.2, 0.7), _mk(0.4, 0.7), _mk(0.6, 0.7)]
    counter = ProductCounter(CountingConfig(mode="shelf"))
    result = counter.count(dets, (1000, 1000))
    assert result.total_count == 5
    assert len(result.regions) == 2


def test_count_conveyor():
    dets = [_mk(0.3, 0.5), _mk(0.7, 0.5), _mk(0.8, 0.5)]
    counter = ProductCounter(CountingConfig(mode="conveyor",
                                              line_position=0.5))
    result = counter.count(dets, (1000, 1000))
    assert result.total_count == 2


def test_min_confidence_filter():
    dets = [_mk(0.5, 0.5, conf=0.3), _mk(0.6, 0.6, conf=0.9)]
    counter = ProductCounter(CountingConfig(mode="shelf",
                                              min_confidence=0.5))
    result = counter.count(dets, (1000, 1000))
    assert result.total_count == 1
