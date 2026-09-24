import logging

logger = logging.getLogger(__name__)


class StubEventBus:
    async def publish(self, event_name: str, payload: dict) -> None:
        logger.info(
            "StubEventBus.publish(event_name=%r, payload=%r)", event_name, payload
        )


_event_bus: StubEventBus | None = None


def get_event_bus() -> StubEventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = StubEventBus()
    return _event_bus
