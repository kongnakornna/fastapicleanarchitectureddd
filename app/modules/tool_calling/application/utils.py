"""tool_calling application utils"""
from __future__ import annotations
import json
import time
from typing import Any


def json_dumps_safe(obj: Any, max_len: int = 10000) -> str:
    try:
        s = json.dumps(
            obj, separators=(",", ":"),
            default=str, ensure_ascii=False,
        )
    except Exception:
        s = "{}"
    if len(s) > max_len:
        s = s[:max_len] + "...[truncated]"
    return s


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
