"""Settings schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class SettingsResponse(BaseModel):
    default_model: str
    device: str
    conf_threshold: float
    iou_threshold: float
    max_batch_size: int
    timeout_seconds: int
    cache_ttl: int
    artifact_bucket: str
    enable_tensorrt: bool
    enable_half: bool
    max_trainings: int
    retention_days: int
    extra: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class SettingsPatchRequest(BaseModel):
    default_model: str | None = None
    device: str | None = None
    conf_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    iou_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    max_batch_size: int | None = Field(default=None, ge=1, le=128)
    timeout_seconds: int | None = Field(default=None, ge=1, le=600)
    cache_ttl: int | None = Field(default=None, ge=0, le=86400)
    artifact_bucket: str | None = None
    enable_tensorrt: bool | None = None
    enable_half: bool | None = None
    max_trainings: int | None = Field(default=None, ge=1, le=16)
    retention_days: int | None = Field(default=None, ge=1, le=3650)
    extra_json: dict[str, Any] | None = None
    model_config = ConfigDict(extra="forbid")


class SettingsValidateResponse(BaseModel):
    valid: bool
    errors: list[str]
    preview: dict[str, Any]
    model_config = ConfigDict(extra="forbid")
