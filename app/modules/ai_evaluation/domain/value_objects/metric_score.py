"""MetricScore VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class MetricScore(BaseModel):
    """TH: คะแนน 1 metric | EN: Single metric score"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    value: float
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    higher_is_better: bool = True
    details: Optional[dict[str, Any]] = None
