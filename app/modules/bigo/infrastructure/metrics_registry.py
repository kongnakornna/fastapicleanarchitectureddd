"""MetricsRegistry — Prometheus-style counter/gauge/histogram"""
from __future__ import annotations

import collections
import statistics
import threading
from typing import Any


class MetricsRegistry:
    """TH: metrics registry (thread-safe)"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = collections.Counter()
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = collections.defaultdict(list)

    def incr(self, name: str, value: int = 1, **labels: Any) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._counters[key] += value

    def gauge(self, name: str, value: float, **labels: Any) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._gauges[key] = float(value)

    def observe(self, name: str, value: float, **labels: Any) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._histograms[key].append(float(value))

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "min": min(v) if v else 0.0,
                        "max": max(v) if v else 0.0,
                        "mean": statistics.fmean(v) if v else 0.0,
                        "p95": self._quantile(v, 0.95),
                    }
                    for k, v in self._histograms.items()
                },
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    @staticmethod
    def _key(name: str, labels: dict[str, Any]) -> str:
        if not labels:
            return name
        suffix = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{suffix}}}"

    @staticmethod
    def _quantile(values: list[float], q: float) -> float:
        if not values:
            return 0.0
        sorted_v = sorted(values)
        idx = max(0, min(len(sorted_v) - 1, int(q * len(sorted_v)) - 1))
        return sorted_v[idx]
