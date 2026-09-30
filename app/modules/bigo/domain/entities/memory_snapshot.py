"""MemorySnapshot entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class MemorySnapshot:
    """TH: MemorySnapshot | EN: MemorySnapshot entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    process_id: int = 0
    rss_mb: float = 0.0
    vms_mb: float = 0.0
    percent: float = 0.0
    pressure: str = ""
    top_allocations_json: str = ""
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
