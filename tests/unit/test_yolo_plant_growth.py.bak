"""Unit tests for plant growth"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.applications.plant_growth import (
    GrowthStage, PlantGrowthAnalyzer,
)
from app.modules.yolo.domain.value_objects import BBox, Detection

pytestmark = pytest.mark.unit


def _mk(cx, cy, cls=1, name="leaf", conf=0.9, w=0.1):
    return Detection(bbox=BBox(cx, cy, w, w), class_id=cls,
                      class_name=name, confidence=conf)


def test_assess_empty():
    a = PlantGrowthAnalyzer()
    m = a.assess([], (1000, 1000))
    assert m.leaf_count == 0


def test_assess_single():
    a = PlantGrowthAnalyzer()
    dets = [_mk(0.5, 0.5, w=0.2)]
    m = a.assess(dets, (1000, 1000), greenness=0.7)
    assert m.leaf_count == 1
    assert m.health_score > 0


def test_growth_stages_enum():
    assert GrowthStage.SEEDLING.value == "seedling"
