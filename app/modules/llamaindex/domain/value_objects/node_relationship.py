"""NodeRelationship VO"""
from __future__ import annotations
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NodeRelationship(BaseModel):
    """TH: ความสัมพันธ์ของ node | EN: Node relationship"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    parent_id: Optional[uuid.UUID] = None
    prev_id: Optional[uuid.UUID] = None
    next_id: Optional[uuid.UUID] = None
    child_ids: list[uuid.UUID] = []
