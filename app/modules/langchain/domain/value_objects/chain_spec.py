"""ChainSpec VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.langchain.domain.enums import ChainType


class ChainSpec(BaseModel):
    """TH: ข้อกำหนด chain | EN: Chain specification"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    chain_type: ChainType = ChainType.LCEL
    config: dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    version: str = "1.0.0"
