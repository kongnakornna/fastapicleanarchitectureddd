"""ProcessReport VO"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.modules.bigo.domain.enums import MemoryPressure, Priority


@dataclass(frozen=True, slots=True)
class ProcessReport:
    n: int
    complexity: str
    status: str
    priority: Priority
    rss_mb: float
    pressure: MemoryPressure
    duration_ms: int
    kafka_partition: int
    kafka_sent: bool
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "n": self.n,
            "complexity": self.complexity,
            "status": self.status,
            "priority": self.priority.value,
            "rss_mb": round(self.rss_mb, 2),
            "pressure": self.pressure.value,
            "duration_ms": self.duration_ms,
            "kafka_partition": self.kafka_partition,
            "kafka_sent": self.kafka_sent,
        }
