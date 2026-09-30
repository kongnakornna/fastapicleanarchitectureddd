"""MemoryManager — LRU + TTL + bytes tracking"""
from __future__ import annotations

import collections
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any

from app.modules.bigo.domain.enums import MemoryPressure
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry


@dataclass(slots=True)
class _MemEntry:
    key: str
    value: Any
    size_bytes: int
    inserted_at: float
    ttl_s: int


class MemoryManager:
    """TH: จัดการ memory ด้วย LRU + TTL"""

    def __init__(
        self,
        config: PipelineConfig,
        metrics: MetricsRegistry | None = None,
    ) -> None:
        self._config = config
        self._metrics = metrics or MetricsRegistry()
        self._lock = threading.Lock()
        self._store: collections.OrderedDict[str, _MemEntry] = collections.OrderedDict()
        self._current_bytes = 0

    def put(self, key: str, value: Any, ttl_s: int | None = None) -> tuple[bool, int]:
        size = self._estimate_size(value)
        ttl = ttl_s if ttl_s is not None else self._config.memory_default_ttl_s
        with self._lock:
            self._evict_expired_locked()
            evicted = 0
            while (self._current_bytes + size > self._config.memory_max_bytes and self._store):
                self._evict_lru_locked()
                evicted += 1
                if evicted >= self._config.memory_evict_batch:
                    if self._current_bytes + size > self._config.memory_max_bytes:
                        self._metrics.incr("bigo.memory.reject")
                        return False, self._current_bytes
                    break
            if size > self._config.memory_max_bytes:
                self._metrics.incr("bigo.memory.reject", reason="too_large")
                return False, self._current_bytes
            if key in self._store:
                old = self._store.pop(key)
                self._current_bytes -= old.size_bytes
            entry = _MemEntry(key=key, value=value, size_bytes=size,
                              inserted_at=time.time(), ttl_s=ttl)
            self._store[key] = entry
            self._current_bytes += size
            self._metrics.gauge("bigo.memory.bytes", self._current_bytes)
            self._metrics.incr("bigo.memory.put")
            return True, self._current_bytes

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._metrics.incr("bigo.memory.miss")
                return None
            if time.time() - entry.inserted_at > entry.ttl_s:
                self._store.pop(key, None)
                self._current_bytes -= entry.size_bytes
                self._metrics.incr("bigo.memory.expired")
                return None
            self._store.move_to_end(key)
            self._metrics.incr("bigo.memory.hit")
            return entry.value

    def pressure(self) -> MemoryPressure:
        ratio = (
            self._current_bytes / self._config.memory_max_bytes
            if self._config.memory_max_bytes > 0 else 0.0
        )
        if ratio >= self._config.memory_critical_ratio:
            return MemoryPressure.CRITICAL
        if ratio >= self._config.memory_high_ratio:
            return MemoryPressure.HIGH
        if ratio >= 0.5:
            return MemoryPressure.ELEVATED
        return MemoryPressure.NORMAL

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "entries": len(self._store),
                "current_bytes": self._current_bytes,
                "max_bytes": self._config.memory_max_bytes,
                "utilization": round(
                    self._current_bytes / self._config.memory_max_bytes, 4,
                ) if self._config.memory_max_bytes else 0.0,
                "pressure": self.pressure().value,
            }

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._current_bytes = 0
        self._metrics.gauge("bigo.memory.bytes", 0)

    @staticmethod
    def _estimate_size(value: Any) -> int:
        try:
            return sys.getsizeof(value)
        except Exception:
            return 64

    def _evict_lru_locked(self) -> None:
        if not self._store:
            return
        key, entry = self._store.popitem(last=False)
        self._current_bytes -= entry.size_bytes
        self._metrics.incr("bigo.memory.evict", reason="lru")

    def _evict_expired_locked(self) -> None:
        now = time.time()
        expired = [
            k for k, e in self._store.items()
            if now - e.inserted_at > e.ttl_s
        ]
        for k in expired:
            e = self._store.pop(k, None)
            if e:
                self._current_bytes -= e.size_bytes
                self._metrics.incr("bigo.memory.evict", reason="ttl")
