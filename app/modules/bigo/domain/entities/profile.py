"""Profile entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class Profile:
    """TH: Profile | EN: Profile entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    function_name: str = ""
    module: str = ""
    complexity: str = ""
    sample_size: int = 0
    avg_ms: float = 0.0
    p95_ms: float = 0.0
    memory_peak_mb: float = 0.0
    notes: str = ""
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
