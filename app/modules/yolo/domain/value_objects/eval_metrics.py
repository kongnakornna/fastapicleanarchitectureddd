"""EvalMetrics value object"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvalMetrics:
    mAP50: float = 0.0
    mAP50_95: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    per_class: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        for name in ("mAP50", "mAP50_95", "precision", "recall", "f1"):
            val = getattr(self, name)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0,1]: {val}")

    def to_dict(self) -> dict:
        return {
            "mAP50": self.mAP50, "mAP50_95": self.mAP50_95,
            "precision": self.precision, "recall": self.recall,
            "f1": self.f1, "per_class": dict(self.per_class),
        }
