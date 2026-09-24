"""EvalTarget VO"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.ai_evaluation.domain.enums import TargetKind


class EvalTarget(BaseModel):
    """TH: เป้าหมายการประเมิน | EN: Evaluation target"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: TargetKind = TargetKind.MODEL
    ref: str = Field(min_length=1, max_length=200)
    pipeline_id: Optional[str] = None
