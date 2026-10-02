"""TrainConfig value object"""
from __future__ import annotations
from dataclasses import dataclass
from ..enums import ModelType


@dataclass(frozen=True, slots=True)
class TrainConfig:
    model_type: str = "yolov8n"
    epochs: int = 100
    batch_size: int = 16
    imgsz: int = 640
    lr0: float = 0.01
    device: str = "auto"
    patience: int = 50
    optimizer: str = "auto"

    def __post_init__(self) -> None:
        if self.model_type not in {m.value for m in ModelType}:
            raise ValueError(f"unsupported model_type: {self.model_type}")
        if self.epochs < 1:
            raise ValueError("epochs must be >= 1")
        if self.batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if self.imgsz < 32 or self.imgsz > 4096:
            raise ValueError("imgsz must be in [32, 4096]")
        if not 0.0 < self.lr0 < 1.0:
            raise ValueError("lr0 must be in (0, 1)")
        if self.patience < 0:
            raise ValueError("patience must be >= 0")
