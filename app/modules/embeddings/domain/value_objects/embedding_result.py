"""EmbeddingResult VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class EmbeddingResult(BaseModel):
    """TH: ผลลัพธ์ embedding | EN: Embedding result"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    vector: list[float]
    dimension: int = Field(ge=1)
    tokens: int = Field(ge=0, default=0)
    cached: bool = False

    @classmethod
    def from_vector(
        cls, vector: list[float], *, tokens: int = 0,
        cached: bool = False,
    ) -> "EmbeddingResult":
        return cls(
            vector=vector, dimension=len(vector),
            tokens=tokens, cached=cached,
        )
