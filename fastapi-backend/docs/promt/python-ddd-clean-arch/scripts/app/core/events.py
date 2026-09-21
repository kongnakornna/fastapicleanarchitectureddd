# app/core/events.py
"""TH: EventBus port + no-op impl | EN: EventBus port + no-op impl"""
from __future__ import annotations

from abc import ABC, abstractmethod

import structlog

log = structlog.get_logger()


class EventBus(ABC):
    """TH: port | EN: port"""

    @abstractmethod
    async def publish(self, event: object) -> None: ...


class NoopEventBus(EventBus):
    """TH: ใช้ใน dev/test | EN: for dev/test"""

    async def publish(self, event: object) -> None:
        log.debug("event.noop", type=type(event).__name__)


_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """TH: factory — prod สลับเป็น KafkaEventBus | EN: factory"""
    global _event_bus  # noqa: PLW0603
    from app.core.config import get_settings  # noqa: PLC0415

    if _event_bus is None:
        if get_settings().kafka_enabled:
            from app.modules.inventory.infrastructure.services import (  # noqa: PLC0415
                KafkaEventBus,
            )
            _event_bus = KafkaEventBus(get_producer())
        else:
            _event_bus = NoopEventBus()
    return _event_bus