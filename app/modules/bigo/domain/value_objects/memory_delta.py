"""MemoryDelta VO"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryDelta:
    before_mb: float
    after_mb: float
    peak_mb: float = 0.0

    def __post_init__(self) -> None:
        if self.before_mb < 0 or self.after_mb < 0:
            raise ValueError("memory must be non-negative")

    @property
    def delta_mb(self) -> float:
        return self.after_mb - self.before_mb

    @property
    def growth_rate(self) -> float:
        if self.before_mb == 0:
            return float("inf") if self.after_mb > 0 else 0.0
        return self.after_mb / self.before_mb
