"""ai_evaluation application utils"""
from __future__ import annotations
import json
import random
import time
from typing import Any, Optional


def json_dumps_safe(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), default=str)


def json_loads_safe(raw: Any, default: Any = None) -> Any:
    if raw is None:
        return default
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return default
    return default


def sample_cases(
    cases: list, sample_size: int, seed: Optional[int] = None,
) -> list:
    if sample_size <= 0 or sample_size >= len(cases):
        return cases
    rng = random.Random(seed)
    return rng.sample(cases, sample_size)


def ms_now() -> int:
    return int(time.time() * 1000)


def aggregate_scores(
    results: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[float]] = {}
    for r in results:
        name = r.get("metric_name", "")
        if not name:
            continue
        buckets.setdefault(name, []).append(float(r.get("score", 0.0)))

    summary: dict[str, dict[str, float]] = {}
    for name, scores in buckets.items():
        if not scores:
            continue
        summary[name] = {
            "mean": round(sum(scores) / len(scores), 4),
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
            "count": float(len(scores)),
        }
    return summary
