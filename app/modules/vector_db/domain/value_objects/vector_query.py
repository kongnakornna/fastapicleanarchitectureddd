"""VectorQuery VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.vector_db.domain.enums import VectorMetric


class VectorQuery(BaseModel):
    """TH: คำค้นเวกเตอร์ | EN: Vector query"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    vector: list[float] = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=1000)
    metric: VectorMetric = VectorMetric.COSINE
    filter: Optional[dict[str, Any]] = None
    include_metadata: bool = True
    score_threshold: Optional[float] = None
