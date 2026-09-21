# events/application/mappers.py
# Maps DomainEvent/EventEnvelope <-> ORM model <-> pydantic schema
# แปลงระหว่าง VO <-> ORM <-> pydantic

from ..domain.enums import EventStatus
from ..domain.value_objects import EventEnvelope


class EventMapper:
    """Maps domain entity <-> ORM model <-> pydantic schema."""

    @staticmethod
    def envelope_to_orm(envelope: EventEnvelope):
        """EventEnvelope -> EventStoreModel — VO ไป ORM"""
        from ..infrastructure.models import EventStoreModel

        return EventStoreModel(
            event_id=envelope.event_id,
            event_type=envelope.event_type,
            tenant_id=envelope.tenant_id,
            correlation_id=envelope.correlation_id,
            occurred_at=envelope.occurred_at,
            version=envelope.version,
            payload=envelope.payload,
            status=EventStatus.PENDING.value,
            retry_count=envelope.retry_count,
        )

    @staticmethod
    def orm_to_envelope(model) -> EventEnvelope:
        """EventStoreModel -> EventEnvelope — ORM ไป VO"""
        return EventEnvelope(
            event_id=model.event_id,
            event_type=model.event_type,
            tenant_id=model.tenant_id,
            correlation_id=model.correlation_id,
            occurred_at=model.occurred_at,
            version=model.version,
            payload=model.payload,
            retry_count=model.retry_count or 0,
        )


# Backward-compat alias (spec template ใช้ชื่อ eventsMapper)
eventsMapper = EventMapper
