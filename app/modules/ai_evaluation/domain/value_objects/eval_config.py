"""EvalConfig VO"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EvalConfig(BaseModel):
    """TH: การตั้งค่าการประเมิน | EN: Evaluation config"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    metrics: list[str] = Field(
        default_factory=lambda: ["faithfulness", "answer_relevance"],
    )
    sample_size: int = Field(default=0, ge=0)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    seed: Optional[int] = None
    concurrency: int = Field(default=4, ge=1, le=32)
    timeout_seconds: int = Field(default=120, ge=10, le=3600)
