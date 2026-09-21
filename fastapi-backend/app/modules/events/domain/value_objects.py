# events/domain/value_objects.py
# Value Objects: DomainEvent, EventEnvelope (VO)
# วัตถุค่า: DomainEvent, EventEnvelope

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from .exceptions import DomainError


def _utcnow() -> datetime:
    """Return timezone-aware UTC now — คืนเวลาปัจจุบัน UTC"""
    return datetime.now(UTC)


@dataclass(frozen=True)
class DomainEvent:
    """Domain event VO — วัตถุเหตุการณ์

    Represents something that happened in the domain.
    แทนเหตุการณ์ที่เกิดขึ้นในโดเมน
    """

    event_type: str
    aggregate_id: str
    payload: dict
    occurred_at: datetime = field(default_factory=_utcnow)
    version: int = 1

    def __post_init__(self):
        if not self.event_type:
            raise DomainError("Event type required")
        if not self.aggregate_id:
            raise DomainError("Aggregate ID required")
        if self.version < 1:
            raise DomainError("Version must be >= 1")


@dataclass(frozen=True)
class EventEnvelope:
    """Event envelope — วัตถุซองเหตุการณ์

    Wraps a DomainEvent with metadata for transport (Kafka, etc.).
    ห่อ DomainEvent ด้วย metadata สำหรับการขนส่ง
    """

    event_id: str
    event_type: str
    tenant_id: str
    correlation_id: str
    occurred_at: datetime
    version: int
    payload: dict
    retry_count: int = 0

    def to_kafka_topic(self) -> str:
        """Kafka topic name — ชื่อ topic"""
        return f"t.{self.tenant_id}.{self.event_type.lower()}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> EventEnvelope:
        return cls(**data)
