"""Plant disease schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class DiagnosisResponse(BaseModel):
    image_id: str
    model_id: str | None = None
    plant_species: str | None = None
    overall_severity: str
    overall_health_score: float
    detections: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    treatment_plan: list[dict[str, Any]] = Field(default_factory=list)
    follow_up_days: int = 7
    confidence: float = 0.0
    generated_at: str = ""
    model_config = ConfigDict(extra="forbid")


class DiseaseCatalogItem(BaseModel):
    code: str
    name_th: str
    name_en: str
    pathogen_type: str
    treatment: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class TreatmentPlanResponse(BaseModel):
    code: str
    name_th: str
    name_en: str
    treatment: list[str]
    prevention: list[str]
    plan: list[dict[str, Any]]
    model_config = ConfigDict(extra="forbid")
