"""hybrid_search application utils"""
from __future__ import annotations
import json
import time
from typing import Any


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


def ms_now() -> int:
    return int(time.time() * 1000)


def hit_to_dict(hit: Any) -> dict[str, Any]:
    """TH: แปลง hit → dict | EN: normalize hit"""
    if isinstance(hit, dict):
        return hit
    return {
        "source_id": str(getattr(hit, "source_id", "")),
        "score": float(getattr(hit, "score", 0.0)),
        "metadata": getattr(hit, "metadata", None) or {},
        "snippet": getattr(hit, "snippet", "") or "",
    }
