# events/infrastructure/services.py
# External services (Kafka, serializer, consumer loop)
# บริการภายนอก (Kafka, ตัวแปลง, consumer loop)

import json
from dataclasses import asdict

from app.core.logging import logger
from app.shared.exceptions import StandardException

from ..application.exceptions import EventException
from ..domain.value_objects import DomainEvent, EventEnvelope


class KafkaEventBus:
    """Kafka event bus — บัสเหตุการณ์ Kafka"""

    def __init__(self, bootstrap: str):
        self.bootstrap = bootstrap
        self.producer = None

    async def publish(self, event: DomainEvent) -> None:
        """Publish single event — เผยแพร่เหตุการณ์เดียว"""
        try:
            topic = f"t.{event.aggregate_id}.{event.event_type.lower()}"
            payload = json.dumps(asdict(event), default=str).encode()
            if self.producer is not None:
                await self.producer.send_and_wait(topic, payload)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Kafka publish failed")
            raise EventException() from e

    async def publish_batch(self, events: list[EventEnvelope]) -> None:
        """Publish batch — เผยแพร่เป็นชุด"""
        try:
            for env in events:
                topic = env.to_kafka_topic()
                payload = json.dumps(env.to_dict(), default=str).encode()
                if self.producer is not None:
                    await self.producer.send_and_wait(topic, payload)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Kafka batch publish failed")
            raise EventException() from e

    async def publish_to_dlq(self, envelope: EventEnvelope) -> None:
        """Publish to DLQ — ส่งไป DLQ"""
        try:
            payload = json.dumps(envelope.to_dict(), default=str).encode()
            if self.producer is not None:
                await self.producer.send_and_wait("dlq.events", payload)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Kafka DLQ publish failed")
            raise EventException() from e


class JsonEventSerializer:
    """JSON serializer — ตัวแปลง JSON"""

    def serialize(self, envelope: EventEnvelope) -> bytes:
        return json.dumps(envelope.to_dict(), default=str).encode()

    def deserialize(self, data: bytes) -> EventEnvelope:
        return EventEnvelope.from_dict(json.loads(data))


class EventConsumerLoop:
    """Kafka consumer loop — วนลูปผู้บริโภค"""

    def __init__(self, consumer=None):
        self.consumer = consumer

    async def run(self, topics: list[str], handler) -> None:
        """Run consumer loop — รัน consumer loop"""
        if self.consumer is None:
            logger.warning("evt.consumer.no_consumer")
            return
        async for msg in self.consumer:
            await handler(msg.value)
