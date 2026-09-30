"""BigOPipeline — orchestrator: monitor → memory → kafka"""
from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Iterable

from app.modules.bigo.domain.enums import MemoryPressure, Priority
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.domain.value_objects import Complexity, ProcessReport
from app.modules.bigo.infrastructure.big_o_monitor import BigOMonitor
from app.modules.bigo.infrastructure.kafka_queue_manager import (
    KafkaProducerLike, KafkaQueueManager,
)
from app.modules.bigo.infrastructure.memory_manager import MemoryManager
from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry


class BigOPipeline:
    """TH: pipeline รวม monitor + memory + kafka"""

    def __init__(
        self,
        config: PipelineConfig | None = None,
        producer: KafkaProducerLike | None = None,
        metrics: MetricsRegistry | None = None,
    ) -> None:
        self._config = config or PipelineConfig()
        self._metrics = metrics or MetricsRegistry()
        self._monitor = BigOMonitor(self._config, self._metrics)
        self._memory = MemoryManager(self._config, self._metrics)

        def _bp() -> bool:
            return self._memory.pressure() == MemoryPressure.CRITICAL

        self._kafka = KafkaQueueManager(
            self._config, producer=producer,
            metrics=self._metrics, backpressure_check=_bp,
        )

    def process(
        self,
        data: list[Any],
        algorithm_type: str = "O(n)",
        topic: str | None = None,
        cache_key: str | None = None,
    ) -> ProcessReport:
        trace_id = str(uuid.uuid4())
        t0 = time.perf_counter()

        n = len(data)
        status, policy_priority = self._monitor.check(n, algorithm_type)
        pressure = self._memory.pressure()
        priority = self._final_priority(status, policy_priority, pressure)

        key = cache_key or f"batch:{trace_id}"
        accepted, _ = self._memory.put(key, data)

        sent = False
        partition = self._config.kafka_partition_map["dlq"]
        if accepted:
            sent, partition = self._kafka.send(
                data, topic=topic, priority=priority,
                key=trace_id.encode(),
            )

        duration_ms = int((time.perf_counter() - t0) * 1000)
        rss_mb = 0.0
        try:
            import psutil
            rss_mb = psutil.Process().memory_info().rss / (1024 * 1024)
        except ImportError:
            rss_mb = self._memory.stats()["current_bytes"] / (1024 * 1024)

        self._metrics.observe("bigo.pipeline.duration_ms", duration_ms)
        self._metrics.incr("bigo.pipeline.processed", status=status)

        return ProcessReport(
            n=n, complexity=algorithm_type, status=status,
            priority=priority, rss_mb=rss_mb, pressure=pressure,
            duration_ms=duration_ms, kafka_partition=partition,
            kafka_sent=sent, trace_id=trace_id,
        )

    def analyze(
        self,
        fn: Callable[[int], Any],
        sizes: Iterable[int] | None = None,
    ) -> Complexity:
        return self._monitor.analyze(fn, sizes=sizes)

    @property
    def memory(self) -> MemoryManager:
        return self._memory

    @property
    def monitor(self) -> BigOMonitor:
        return self._monitor

    @property
    def kafka(self) -> KafkaQueueManager:
        return self._kafka

    @property
    def config(self) -> PipelineConfig:
        return self._config

    def metrics_snapshot(self) -> dict[str, Any]:
        return self._metrics.snapshot()

    @staticmethod
    def _final_priority(
        status: str, policy: Priority, pressure: MemoryPressure,
    ) -> Priority:
        if pressure in (MemoryPressure.CRITICAL, MemoryPressure.HIGH):
            return Priority.LOW
        if status == "CRITICAL":
            return Priority.LOW
        if status == "WARNING":
            return Priority.NORMAL if policy == Priority.HIGH else policy
        return policy
