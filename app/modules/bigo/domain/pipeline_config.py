"""PipelineConfig"""
from __future__ import annotations
from dataclasses import dataclass, field

from app.modules.bigo.domain.enums import Priority


@dataclass(slots=True)
class PipelineConfig:
    max_n_linear: int = 10_000
    max_n_quadratic: int = 1_000
    max_n_cubic: int = 200
    max_n_linearithmic: int = 50_000
    warn_ratio: float = 0.8

    memory_max_bytes: int = 50 * 1024 * 1024
    memory_high_ratio: float = 0.8
    memory_critical_ratio: float = 0.95
    memory_default_ttl_s: int = 3600
    memory_evict_batch: int = 32

    kafka_bootstrap: str = "localhost:9092"
    kafka_topic: str = "monitoring.logs"
    kafka_dlq_topic: str = "monitoring.logs.dlq"
    kafka_partition_map: dict[str, int] = field(
        default_factory=lambda: {
            Priority.HIGH.value: 0,
            Priority.NORMAL.value: 1,
            Priority.LOW.value: 2,
            Priority.DLQ.value: 9,
        },
    )
    kafka_max_retries: int = 3
    kafka_backoff: tuple[float, ...] = (1.0, 2.0, 4.0)
    kafka_flush_timeout_s: float = 5.0

    cache_namespace: str = "bigo"
    cache_default_ttl_s: int = 300
    cache_lock_timeout_s: float = 5.0

    ws_heartbeat_interval_s: int = 30
    ws_max_per_tenant: int = 1000
    ws_send_timeout_s: float = 5.0

    compress_low_priority: bool = True
    sample_sizes: tuple[int, ...] = (10, 50, 100, 500, 1000, 5000, 10_000)
