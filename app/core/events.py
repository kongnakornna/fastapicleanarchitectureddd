"""Event bus — stub (log only)"""
from __future__ import annotations

from typing import Any

from app.core.logging import logger


class EventBus:
    """TH: event bus | EN: event bus"""

    async def publish(self, event: object) -> None:
        """TH: publish event | EN: publish event"""
        logger.info(
            f"event.publish type={type(event).__name__}",
            extra={"event_type": type(event).__name__},
        )


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """TH: DI event bus | EN: DI event bus"""
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
