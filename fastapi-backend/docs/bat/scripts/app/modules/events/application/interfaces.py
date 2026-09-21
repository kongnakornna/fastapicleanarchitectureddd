# events/application/interfaces.py
# Ports (Protocol) — พอร์ต (Protocol)

from typing import Protocol

from ..domain.value_objects import DomainEvent, EventEnvelope


class IEventBus(Protocol):
    """Event bus port — พอร์ตบัสเหตุการณ์"""

    async def publish(self, event: DomainEvent) -> None: ...
    async def publish_batch(self, events: list[DomainEvent]) -> None: ...
    async def publish_to_dlq(self, envelope: EventEnvelope) -> None: ...


class IEventStore(Protocol):
    """Event store port — พอร์ตที่เก็บเหตุการณ์"""

    async def append(self, envelope: EventEnvelope) -> None: ...
    async def get(self, event_id: str) -> EventEnvelope | None: ...
    async def mark_consumed(self, event_id: str) -> None: ...


class IEventHandler(Protocol):
    """Event handler port — พอร์ตตัวจัดการเหตุการณ์"""

    event_type: str

    async def handle(self, envelope: EventEnvelope) -> None: ...


class IEventSerializer(Protocol):
    """Event serializer port — พอร์ตตัวแปลงเหตุการณ์"""

    def serialize(self, envelope: EventEnvelope) -> bytes: ...
    def deserialize(self, data: bytes) -> EventEnvelope: ...
