"""FusionConfig VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

from app.modules.hybrid_search.domain.enums import FusionType


class FusionConfig(BaseModel):
    """TH: การตั้งค่า fusion | EN: Fusion config"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    fusion_type: FusionType = FusionType.RRF
    rrf_k: int = Field(default=60, ge=1, le=1000)
    bm25_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.5, ge=0.0, le=1.0)
