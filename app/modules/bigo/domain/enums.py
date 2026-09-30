"""bigo enums"""
from __future__ import annotations
from enum import StrEnum


class ComplexityClass(StrEnum):
    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n^2)"
    CUBIC = "O(n^3)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"
    UNKNOWN = "UNKNOWN"


class MetricKind(StrEnum):
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_RSS = "memory_rss"
    MEMORY_HEAP = "memory_heap"
    CPU_PERCENT = "cpu_percent"
    GC_PAUSE = "gc_pause"
    QUEUE_DEPTH = "queue_depth"
    KAFKA_LAG = "kafka_lag"
    ERROR_RATE = "error_rate"


class MemoryPressure(StrEnum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    OOM = "OOM"


class LeakType(StrEnum):
    REFERENCE_CYCLE = "REFERENCE_CYCLE"
    UNBOUNDED_CACHE = "UNBOUNDED_CACHE"
    LISTENER_LEAK = "LISTENER_LEAK"
    THREAD_LOCAL = "THREAD_LOCAL"
    NATIVE_BUFFER = "NATIVE_BUFFER"
    UNKNOWN = "UNKNOWN"


class KafkaHealth(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class AlertSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Priority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DLQ = "dlq"
