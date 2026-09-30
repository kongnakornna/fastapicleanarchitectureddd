"""KafkaConsumer entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class KafkaConsumer:
    """TH: KafkaConsumer | EN: KafkaConsumer entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    group_id: str = ""
    topic: str = ""
    member_count: int = 0
    total_lag: int = 0
    health: str = ""
    last_commit_at: datetime | None = None
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
