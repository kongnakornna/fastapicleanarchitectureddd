"""vector_db application utils"""
from __future__ import annotations
import json
from typing import Any


def vector_to_json(vec: list[float]) -> str:
    return json.dumps(vec, separators=(",", ":"))


def json_to_vector(raw: Any) -> list[float]:
    if isinstance(raw, list):
        return [float(x) for x in raw]
    if isinstance(raw, str):
        try:
            return [float(x) for x in json.loads(raw)]
        except Exception:
            return []
    return []


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
