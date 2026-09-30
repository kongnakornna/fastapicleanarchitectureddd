"""Unit tests for bigo domain"""
from __future__ import annotations
import pytest

from app.modules.bigo.domain.enums import (
    ComplexityClass, MemoryPressure, Priority,
)
from app.modules.bigo.domain.value_objects import (
    Complexity, ComplexityPolicy, KafkaLag, MemoryDelta,
)

pytestmark = pytest.mark.unit


class TestEnums:
    def test_complexity(self) -> None:
        assert ComplexityClass.CONSTANT == "O(1)"
        assert ComplexityClass.LINEAR == "O(n)"
        assert ComplexityClass.QUADRATIC == "O(n^2)"

    def test_priority(self) -> None:
        assert Priority.HIGH == "high"
        assert Priority.DLQ == "dlq"


class TestComplexityVO:
    def test_create(self) -> None:
        c = Complexity(cls=ComplexityClass.LINEAR, sample_size=7, r_squared=0.98)
        assert c.notation == "O(n)"

    def test_invalid_r2(self) -> None:
        with pytest.raises(ValueError):
            Complexity(cls=ComplexityClass.LINEAR, sample_size=5, r_squared=1.5)


class TestComplexityPolicy:
    def test_pass(self) -> None:
        p = ComplexityPolicy(ComplexityClass.LINEAR, 1000)
        assert p.classify(100) == "PASS"

    def test_warning(self) -> None:
        p = ComplexityPolicy(ComplexityClass.LINEAR, 1000, warn_ratio=0.8)
        assert p.classify(900) == "WARNING"

    def test_critical(self) -> None:
        p = ComplexityPolicy(ComplexityClass.LINEAR, 1000)
        assert p.classify(1500) == "CRITICAL"


class TestMemoryDelta:
    def test_delta(self) -> None:
        d = MemoryDelta(before_mb=100.0, after_mb=150.0)
        assert d.delta_mb == 50.0
        assert d.growth_rate == 1.5


class TestKafkaLag:
    def test_compute(self) -> None:
        lag = KafkaLag.compute("orders", 0, 100, 500)
        assert lag.lag == 400
