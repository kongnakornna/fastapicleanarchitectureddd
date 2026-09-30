"""KafkaQueue entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class KafkaQueue:
    """TH: KafkaQueue | EN: KafkaQueue entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    topic: str = ""
    partition: int = 0
    current_offset: int = 0
    log_end_offset: int = 0
    lag: int = 0
    health: str = ""
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
