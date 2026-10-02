"""Unit tests for plant disease"""
from __future__ import annotations
import pytest
from app.modules.yolo.domain.applications.plant_disease import (
    DISEASE_CATALOG, PlantDiseaseDiagnoser,
)
from app.modules.yolo.domain.value_objects import BBox, Detection

pytestmark = pytest.mark.unit


def _mk(cx, cy, cls=0, name="rice-blast", conf=0.9, w=0.1):
    return Detection(bbox=BBox(cx, cy, w, w), class_id=cls,
                      class_name=name, confidence=conf)


def test_severity_mild():
    d = PlantDiseaseDiagnoser()
    sev = d.calc_severity(BBox(0.5, 0.5, 0.1, 0.1))
    assert sev.level == "mild"


def test_severity_critical():
    d = PlantDiseaseDiagnoser()
    sev = d.calc_severity(BBox(0.5, 0.5, 0.8, 0.8))
    assert sev.level == "critical"


def test_diagnose_healthy():
    d = PlantDiseaseDiagnoser()
    result = d.diagnose([], {}, None)
    assert result.overall_severity == "healthy"


def test_catalog():
    assert "rice-blast" in DISEASE_CATALOG
