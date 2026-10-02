"""AugConfig value object"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AugConfig:
    hsv_h: float = 0.015
    hsv_s: float = 0.7
    hsv_v: float = 0.4
    degrees: float = 0.0
    translate: float = 0.1
    scale: float = 0.5
    shear: float = 0.0
    perspective: float = 0.0
    flipud: float = 0.0
    fliplr: float = 0.5
    mosaic: float = 1.0
    mixup: float = 0.0
    copy_paste: float = 0.0

    def __post_init__(self) -> None:
        for name in ("hsv_h", "hsv_s", "hsv_v", "translate", "scale",
                     "shear", "perspective", "flipud", "fliplr",
                     "mosaic", "mixup", "copy_paste"):
            val = getattr(self, name)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0,1]: {val}")
        if not 0.0 <= self.degrees <= 180.0:
            raise ValueError("degrees must be in [0,180]")

    def to_dict(self) -> dict:
        return {
            "hsv_h": self.hsv_h, "hsv_s": self.hsv_s, "hsv_v": self.hsv_v,
            "degrees": self.degrees, "translate": self.translate,
            "scale": self.scale, "shear": self.shear,
            "perspective": self.perspective, "flipud": self.flipud,
            "fliplr": self.fliplr, "mosaic": self.mosaic,
            "mixup": self.mixup, "copy_paste": self.copy_paste,
        }
