"""Plant growth schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class GrowthMetricsResponse(BaseModel):
    stage: str
    stage_confidence: float
    plant_height_px: float
    plant_height_cm: float | None = None
    leaf_area_px: float
    leaf_area_pct: float
    leaf_count: int
    canopy_width_px: float
    greenness_index: float
    health_score: float
    growth_rate_pct: float | None = None
    model_config = ConfigDict(extra="forbid")


class GrowthAssessmentResponse(BaseModel):
    image_id: str
    model_id: str | None = None
    plant_id: str | None = None
    field_id: str | None = None
    metrics: GrowthMetricsResponse
    stage_history: list[dict[str, str]] = Field(default_factory=list)
    predictions: list[dict[str, Any]] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    generated_at: str = ""
    model_config = ConfigDict(extra="forbid")


class HarvestPredictionResponse(BaseModel):
    field_id: str
    predicted_harvest_date: str
    confidence: float
    stage_progression: list[dict[str, Any]]
    model_config = ConfigDict(extra="forbid")
