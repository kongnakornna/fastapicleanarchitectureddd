"""Complexity VO"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.modules.bigo.domain.enums import ComplexityClass


@dataclass(frozen=True, slots=True)
class Complexity:
    cls: ComplexityClass
    sample_size: int
    r_squared: float = 0.0
    coefficients: tuple[tuple[str, float], ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if self.sample_size < 0:
            raise ValueError("sample_size must be >= 0")
        if not 0.0 <= self.r_squared <= 1.0:
            raise ValueError("r_squared must be 0-1")

    @property
    def notation(self) -> str:
        return self.cls.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "complexity": self.notation,
            "sample_size": self.sample_size,
            "r_squared": self.r_squared,
            "coefficients": dict(self.coefficients),
            "notes": self.notes,
        }


COMPLEXITY_ORDER: dict[str, int] = {
    "O(1)": 0, "O(log n)": 1, "O(n)": 2,
    "O(n log n)": 3, "O(n^2)": 4, "O(n^3)": 5,
    "O(2^n)": 6, "O(n!)": 7, "UNKNOWN": -1,
}


def compare(a: str, b: str) -> int:
    return COMPLEXITY_ORDER.get(a, -1) - COMPLEXITY_ORDER.get(b, -1)
