"""Unit tests for bigo pipeline"""
from __future__ import annotations
import time
import pytest

from app.modules.bigo.domain.enums import MemoryPressure, Priority
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.infrastructure.big_o_monitor import BigOMonitor
from app.modules.bigo.infrastructure.kafka_queue_manager import (
    InMemoryProducer, KafkaQueueManager,
)
from app.modules.bigo.infrastructure.memory_manager import MemoryManager
from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry
from app.modules.bigo.infrastructure.pipeline import BigOPipeline

pytestmark = pytest.mark.unit


class TestMetricsRegistry:
    def test_counter(self) -> None:
        m = MetricsRegistry()
        m.incr("hits")
        m.incr("hits", 3)
        assert m.snapshot()["counters"]["hits"] == 4

    def test_histogram(self) -> None:
        m = MetricsRegistry()
        for i in range(100):
            m.observe("latency", float(i))
        h = m.snapshot()["histograms"]["latency"]
        assert h["count"] == 100
        assert 90 <= h["p95"] <= 99


class TestBigOMonitor:
    def test_pass(self) -> None:
        m = BigOMonitor(PipelineConfig(max_n_linear=10_000))
        status, priority = m.check(100, "O(n)")
        assert status == "PASS"
        assert priority == Priority.NORMAL

    def test_critical(self) -> None:
        m = BigOMonitor(PipelineConfig(max_n_linear=10_000))
        status, _ = m.check(20_000, "O(n)")
        assert status == "CRITICAL"


class TestMemoryManager:
    def test_put_get(self) -> None:
        m = MemoryManager(PipelineConfig(memory_max_bytes=1024 * 1024))
        ok, _ = m.put("k1", [1, 2, 3])
        assert ok
        assert m.get("k1") == [1, 2, 3]

    def test_ttl(self) -> None:
        m = MemoryManager(PipelineConfig(memory_max_bytes=1024))
        m.put("k1", "hello", ttl_s=1)
        time.sleep(1.1)
        assert m.get("k1") is None


class TestKafkaQueueManager:
    def test_send_high(self) -> None:
        cfg = PipelineConfig()
        q = KafkaQueueManager(cfg, producer=InMemoryProducer())
        sent, partition = q.send([1, 2, 3], priority=Priority.HIGH)
        assert sent is True
        assert partition == 0

    def test_backpressure_dlq(self) -> None:
        cfg = PipelineConfig()
        q = KafkaQueueManager(
            cfg, producer=InMemoryProducer(),
            backpressure_check=lambda: True,
        )
        _, partition = q.send([1], priority=Priority.HIGH)
        assert partition == cfg.kafka_partition_map["dlq"]


class TestBigOPipeline:
    def test_process(self) -> None:
        p = BigOPipeline(PipelineConfig(memory_max_bytes=1024 * 1024))
        r = p.process(list(range(100)), algorithm_type="O(n)")
        assert r.status == "PASS"
        assert r.kafka_sent is True

    def test_process_critical(self) -> None:
        p = BigOPipeline(PipelineConfig(max_n_linear=10_000))
        r = p.process(list(range(50_000)), algorithm_type="O(n)")
        assert r.status == "CRITICAL"
        assert r.priority == Priority.LOW
