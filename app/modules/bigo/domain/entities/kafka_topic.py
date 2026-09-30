"""KafkaTopic entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class KafkaTopic:
    """TH: KafkaTopic | EN: KafkaTopic entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    partitions: int = 0
    replication_factor: int = 0
    retention_ms: int = 0
    max_message_bytes: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
