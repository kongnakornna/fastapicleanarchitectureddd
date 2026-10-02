"""Counting schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CountingConfigRequest(BaseModel):
    mode: str = Field(default="shelf",
                        pattern=r"^(shelf|conveyor|checkout|warehouse)$")
    line_position: float = Field(default=0.5, ge=0.0, le=1.0)
    line_orientation: str = Field(default="vertical",
                                    pattern=r"^(vertical|horizontal)$")
    class_filter: list[int] = Field(default_factory=list)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    merge_distance: float = Field(default=0.05, ge=0.0, le=1.0)
    deduplication: bool = True
    model_config = ConfigDict(extra="forbid")


class ClassCount(BaseModel):
    class_name: str
    count: int
    model_config = ConfigDict(extra="forbid")


class CountingResultResponse(BaseModel):
    model_id: str
    mode: str
    total_count: int
    per_class_count: list[ClassCount]
    regions: list[dict[str, Any]] = Field(default_factory=list)
    confidence_avg: float = 0.0
    processing_ms: int = 0
    warnings: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class BatchCountingResponse(BaseModel):
    model_id: str
    total: int
    results: list[dict[str, Any]]
    model_config = ConfigDict(extra="forbid")
