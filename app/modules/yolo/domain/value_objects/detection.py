"""Detection value object"""
from __future__ import annotations
from dataclasses import dataclass
from .bbox import BBox


@dataclass(frozen=True, slots=True)
class Detection:
    bbox: BBox
    class_id: int
    class_name: str
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0,1]: {self.confidence}")

    def to_dict(self) -> dict:
        return {
            "bbox": {
                "x_center": self.bbox.x_center,
                "y_center": self.bbox.y_center,
                "width": self.bbox.width,
                "height": self.bbox.height,
            },
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
        }
