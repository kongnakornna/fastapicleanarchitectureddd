"""Memory analyzer"""
from __future__ import annotations
import gc
import tracemalloc
from typing import Any


def take_snapshot() -> list[tuple[str, int, int]]:
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    gc.collect()
    snap = tracemalloc.take_snapshot()
    stats = snap.statistics("lineno")
    return [(str(s.traceback), s.size, s.count) for s in stats[:50]]


def diff_snapshots(
    before: list[tuple[str, int, int]],
    after: list[tuple[str, int, int]],
) -> list[dict[str, Any]]:
    b_map = {{k: (size, count) for k, size, count in before}}
    a_map = {{k: (size, count) for k, size, count in after}}
    keys = set(b_map) | set(a_map)
    diffs: list[dict[str, Any]] = []
    for k in keys:
        b_size, b_count = b_map.get(k, (0, 0))
        a_size, a_count = a_map.get(k, (0, 0))
        delta = a_size - b_size
        if delta == 0:
            continue
        diffs.append({
            "location": k,
            "before_bytes": b_size,
            "after_bytes": a_size,
            "delta_bytes": delta,
            "delta_count": a_count - b_count,
        })
    diffs.sort(key=lambda d: d["delta_bytes"], reverse=True)
    return diffs[:50]


def detect_leaks(
    snapshots: list[list[tuple[str, int, int]]],
    threshold_mb_per_hour: float = 10.0,
) -> list[dict[str, Any]]:
    if len(snapshots) < 3:
        return []

    counters: dict[str, list[int]] = {}
    for snap in snapshots:
        for loc, size, _ in snap:
            counters.setdefault(loc, []).append(size)

    leaks: list[dict[str, Any]] = []
    for loc, sizes in counters.items():
        if len(sizes) < 3:
            continue
        n = len(sizes)
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(sizes) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, sizes))
        den = sum((x - mean_x) ** 2 for x in xs)
        slope = num / den if den else 0.0
        growth_mb = slope / (1024 * 1024)
        if growth_mb > threshold_mb_per_hour:
            leaks.append({
                "location": loc,
                "growth_mb_per_hour": growth_mb,
                "current_bytes": sizes[-1],
                "samples": n,
            })
    leaks.sort(key=lambda d: d["growth_mb_per_hour"], reverse=True)
    return leaks[:20]


def get_memory_info() -> dict[str, Any]:
    try:
        import psutil
        proc = psutil.Process()
        mem = proc.memory_info()
        return {
            "rss_mb": mem.rss / (1024 * 1024),
            "vms_mb": mem.vms / (1024 * 1024),
            "percent": proc.memory_percent(),
            "cpu_percent": proc.cpu_percent(interval=0.1),
        }
    except ImportError:
        return {"rss_mb": 0.0, "vms_mb": 0.0, "percent": 0.0, "cpu_percent": 0.0}
