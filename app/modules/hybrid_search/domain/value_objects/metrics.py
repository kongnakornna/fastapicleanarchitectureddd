"""MetricScore VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class MetricScore(BaseModel):
    """TH: คะแนนของ metric | EN: Metric score"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    value: float
    k: int = Field(default=0, ge=0)
