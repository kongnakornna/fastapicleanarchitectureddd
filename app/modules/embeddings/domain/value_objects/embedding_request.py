"""EmbeddingRequest VO"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmbeddingRequest(BaseModel):
    """TH: คำขอ embedding | EN: Embedding request"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(min_length=1, max_length=100)
    input: list[str] = Field(min_length=1)
    normalize: bool = True
    dimensions: Optional[int] = Field(default=None, ge=1, le=8192)
    encoding_format: str = Field(
        default="float", pattern="^(float|base64)$",
    )
