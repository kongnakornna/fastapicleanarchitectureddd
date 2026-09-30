"""MemoryLeak entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class MemoryLeak:
    """TH: MemoryLeak | EN: MemoryLeak entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    location: str = ""
    leak_type: str = ""
    growth_mb_per_hour: float = 0.0
    current_bytes: int = 0
    samples: int = 0
    status: str = ""
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
