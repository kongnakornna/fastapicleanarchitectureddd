"""structured_outputs application utils"""
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
