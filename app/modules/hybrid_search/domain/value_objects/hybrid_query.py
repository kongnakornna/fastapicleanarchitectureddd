"""HybridQuery VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.hybrid_search.domain.enums import RerankerType


class HybridQuery(BaseModel):
    """TH: คำค้นแบบ hybrid | EN: Hybrid query"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=500)
    filters: Optional[dict[str, Any]] = None
    reranker_type: RerankerType = RerankerType.NONE
    score_threshold: Optional[float] = None
