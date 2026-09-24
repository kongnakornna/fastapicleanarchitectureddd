"""RunContext VO"""
from __future__ import annotations
import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RunContext(BaseModel):
    """TH: context ของ run | EN: Run context"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: uuid.UUID
    kind: str = "chain"
    target_id: uuid.UUID
    inputs: dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[uuid.UUID] = None
