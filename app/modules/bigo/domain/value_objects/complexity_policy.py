"""ComplexityPolicy VO"""
from __future__ import annotations
from dataclasses import dataclass

from app.modules.bigo.domain.enums import ComplexityClass, Priority


@dataclass(frozen=True, slots=True)
class ComplexityPolicy:
    cls: ComplexityClass
    max_n: int
    warn_ratio: float = 0.8
    critical_ratio: float = 1.0
    partition: Priority = Priority.NORMAL

    def __post_init__(self) -> None:
        if self.max_n <= 0:
            raise ValueError("max_n must be > 0")
        if not 0.0 < self.warn_ratio <= 1.0:
            raise ValueError("warn_ratio must be in (0, 1]")
        if self.critical_ratio < self.warn_ratio:
            raise ValueError("critical_ratio must be >= warn_ratio")

    @property
    def warn_at(self) -> int:
        return int(self.max_n * self.warn_ratio)

    @property
    def critical_at(self) -> int:
        return int(self.max_n * self.critical_ratio)

    def classify(self, n: int) -> str:
        if n > self.critical_at:
            return "CRITICAL"
        if n > self.warn_at:
            return "WARNING"
        return "PASS"
