"""BBox value object"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BBox:
    x_center: float
    y_center: float
    width: float
    height: float

    def __post_init__(self) -> None:
        for name, val in (
            ("x_center", self.x_center), ("y_center", self.y_center),
            ("width", self.width), ("height", self.height),
        ):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0,1]: {val}")
        if self.width <= 0.0:
            raise ValueError("width must be > 0")
        if self.height <= 0.0:
            raise ValueError("height must be > 0")

    def to_xyxy(self, img_w: int, img_h: int) -> tuple[float, float, float, float]:
        x1 = (self.x_center - self.width / 2.0) * img_w
        y1 = (self.y_center - self.height / 2.0) * img_h
        x2 = (self.x_center + self.width / 2.0) * img_w
        y2 = (self.y_center + self.height / 2.0) * img_h
        return max(0.0, x1), max(0.0, y1), min(float(img_w), x2), min(float(img_h), y2)

    @classmethod
    def from_xyxy(cls, x1: float, y1: float, x2: float, y2: float,
                  img_w: int, img_h: int) -> "BBox":
        w = max(0.0, x2 - x1) / img_w
        h = max(0.0, y2 - y1) / img_h
        cx = (x1 + x2) / 2.0 / img_w
        cy = (y1 + y2) / 2.0 / img_h
        return cls(x_center=cx, y_center=cy, width=w, height=h)
