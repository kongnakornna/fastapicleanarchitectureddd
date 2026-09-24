import logging

logger = logging.getLogger(__name__)


class StubProducer:
    async def send_and_wait(
        self, topic: str, *, key: bytes | None = None, value: bytes | None = None
    ) -> None:
        logger.info(
            "StubProducer.send_and_wait(topic=%r, key=%r, value=%r)",
            topic,
            key,
            value,
        )


_producer: StubProducer | None = None


def get_producer() -> StubProducer:
    global _producer
    if _producer is None:
        _producer = StubProducer()
    return _producer
