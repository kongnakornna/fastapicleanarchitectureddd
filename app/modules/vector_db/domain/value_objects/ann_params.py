"""ANN Params VOs"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class HNSWParams(BaseModel):
    """TH: HNSW params | EN: HNSW params"""
    model_config = ConfigDict(frozen=True, extra="forbid")
    m: int = Field(default=16, ge=2, le=128)
    ef_construction: int = Field(default=64, ge=4, le=1024)
    ef_search: int = Field(default=40, ge=1, le=1024)


class IVFFlatParams(BaseModel):
    """TH: IVFFlat params | EN: IVFFlat params"""
    model_config = ConfigDict(frozen=True, extra="forbid")
    lists: int = Field(default=100, ge=1, le=32768)
    probes: int = Field(default=1, ge=1, le=1024)
