"""RetrievalConfig VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

from app.modules.rag.domain.enums import RerankerType, RetrieverType


class RetrievalConfig(BaseModel):
    """TH: การตั้งค่า retrieval | EN: Retrieval config"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    retriever_type: RetrieverType = RetrieverType.VECTOR
    top_k: int = Field(default=5, ge=1, le=100)
    score_threshold: float = Field(default=0.0, ge=-1.0, le=1.0)
    reranker_type: RerankerType = RerankerType.NONE
    mmr_lambda: float = Field(default=0.5, ge=0.0, le=1.0)
