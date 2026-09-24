"""BatchConfig VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class BatchConfig(BaseModel):
    """TH: การตั้งค่า batch | EN: Batch config"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    batch_size: int = Field(default=64, ge=1, le=2048)
    max_concurrency: int = Field(default=4, ge=1, le=32)
    retry: int = Field(default=3, ge=0, le=10)
