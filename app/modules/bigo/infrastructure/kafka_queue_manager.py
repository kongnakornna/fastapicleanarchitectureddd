"""KafkaQueueManager — priority + retry + DLQ + compression"""
from __future__ import annotations

import time
from typing import Any, Callable, Protocol

from app.modules.bigo.domain.enums import Priority
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry


class KafkaProducerLike(Protocol):
    def produce(
        self, topic: str, value: bytes, partition: int = 0,
        key: bytes | None = None, on_delivery: Any = None,
    ) -> None: ...
    def flush(self, timeout: float = 5.0) -> int: ...


class InMemoryProducer:
    """TH: mock producer สำหรับ demo/test"""

    def __init__(self) -> None:
        self.buffer: list[dict[str, Any]] = []

    def produce(
        self, topic: str, value: bytes, partition: int = 0,
        key: bytes | None = None, on_delivery: Any = None,
    ) -> None:
        self.buffer.append({
            "topic": topic, "value": value, "partition": partition,
            "key": key, "ts": time.time(),
        })
        if on_delivery is not None:
            on_delivery(None, None)

    def flush(self, timeout: float = 5.0) -> int:
        return 0


class KafkaQueueManager:
    """TH: จัดคิว + priority + retry + DLQ"""

    def __init__(
        self,
        config: PipelineConfig,
        producer: KafkaProducerLike | None = None,
        metrics: MetricsRegistry | None = None,
        backpressure_check: Callable[[], bool] | None = None,
    ) -> None:
        self._config = config
        self._producer = producer or InMemoryProducer()
        self._metrics = metrics or MetricsRegistry()
        self._bp_check = backpressure_check or (lambda: False)

    def send(
        self,
        data: Any,
        topic: str | None = None,
        priority: Priority = Priority.NORMAL,
        key: bytes | None = None,
    ) -> tuple[bool, int]:
        topic = topic or self._config.kafka_topic
        partition = self._config.kafka_partition_map.get(priority.value, 1)

        if self._bp_check():
            self._metrics.incr("bigo.kafka.backpressure", priority=priority.value)
            topic = self._config.kafka_dlq_topic
            partition = self._config.kafka_partition_map["dlq"]

        payload = self._encode(data, priority)

        for attempt in range(self._config.kafka_max_retries):
            try:
                self._producer.produce(
                    topic=topic, value=payload,
                    partition=partition, key=key,
                )
                self._producer.flush(timeout=self._config.kafka_flush_timeout_s)
                self._metrics.incr("bigo.kafka.sent", priority=priority.value, topic=topic)
                return True, partition
            except Exception:
                wait = (
                    self._config.kafka_backoff[attempt]
                    if attempt < len(self._config.kafka_backoff) else 4.0
                )
                time.sleep(wait)

        self._metrics.incr("bigo.kafka.failed", priority=priority.value)
        try:
            self._producer.produce(
                topic=self._config.kafka_dlq_topic,
                value=payload,
                partition=self._config.kafka_partition_map["dlq"],
                key=key,
            )
            self._producer.flush(timeout=self._config.kafka_flush_timeout_s)
        except Exception:
            self._metrics.incr("bigo.kafka.dlq_failed")
        return False, self._config.kafka_partition_map["dlq"]

    def _encode(self, data: Any, priority: Priority) -> bytes:
        raw = str(data).encode("utf-8")
        if priority == Priority.LOW and self._config.compress_low_priority:
            try:
                import zlib
                compressed = zlib.compress(raw, level=6)
                return b"\x01" + compressed
            except Exception:
                pass
        return b"\x00" + raw
