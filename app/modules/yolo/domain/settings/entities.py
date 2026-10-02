"""Settings entities"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class PlatformSettings:
    tenant_id: uuid.UUID
    default_model: str = "yolov8n.pt"
    device: str = "auto"
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_batch_size: int = 32
    timeout_seconds: int = 30
    cache_ttl: int = 300
    artifact_bucket: str = "yolo-artifacts"
    enable_tensorrt: bool = False
    enable_half: bool = True
    max_trainings: int = 1
    retention_days: int = 90
    extra_json: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0.0 <= self.conf_threshold <= 1.0:
            errors.append("conf_threshold must be in [0,1]")
        if not 0.0 <= self.iou_threshold <= 1.0:
            errors.append("iou_threshold must be in [0,1]")
        if not 1 <= self.max_batch_size <= 128:
            errors.append("max_batch_size must be in [1,128]")
        if not 1 <= self.timeout_seconds <= 600:
            errors.append("timeout_seconds must be in [1,600]")
        if self.device not in ("auto", "cpu") and not self.device.startswith("cuda"):
            errors.append("device must be auto|cpu|cuda:N")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_model": self.default_model, "device": self.device,
            "conf_threshold": self.conf_threshold,
            "iou_threshold": self.iou_threshold,
            "max_batch_size": self.max_batch_size,
            "timeout_seconds": self.timeout_seconds,
            "cache_ttl": self.cache_ttl,
            "artifact_bucket": self.artifact_bucket,
            "enable_tensorrt": self.enable_tensorrt,
            "enable_half": self.enable_half,
            "max_trainings": self.max_trainings,
            "retention_days": self.retention_days,
            "extra": self.extra_json}


@dataclass(frozen=True, slots=True)
class SettingsPatch:
    default_model: str | None = None
    device: str | None = None
    conf_threshold: float | None = None
    iou_threshold: float | None = None
    max_batch_size: int | None = None
    timeout_seconds: int | None = None
    cache_ttl: int | None = None
    artifact_bucket: str | None = None
    enable_tensorrt: bool | None = None
    enable_half: bool | None = None
    max_trainings: int | None = None
    retention_days: int | None = None
    extra_json: dict[str, Any] | None = None

    def apply_to(self, settings: PlatformSettings) -> PlatformSettings:
        for field_name in (
            "default_model", "device", "conf_threshold",
            "iou_threshold", "max_batch_size", "timeout_seconds",
            "cache_ttl", "artifact_bucket", "enable_tensorrt",
            "enable_half", "max_trainings", "retention_days"):
            val = getattr(self, field_name)
            if val is not None:
                setattr(settings, field_name, val)
        if self.extra_json is not None:
            settings.extra_json.update(self.extra_json)
        settings.updated_at = datetime.now(UTC)
        return settings
