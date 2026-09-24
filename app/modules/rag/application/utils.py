"""rag application utils"""
from __future__ import annotations
import hashlib
import json
import time
from typing import Any


def make_cache_key(
    tenant_id: str, model: str, query: str, top_k: int,
) -> str:
    raw = f"{tenant_id}|{model}|{query}|{top_k}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"rag:q:{digest}"


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


def build_context_block(chunks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, c in enumerate(chunks, start=1):
        snippet = (c.get("content") or "").strip().replace("\n", " ")
        lines.append(f"[{i}] {snippet}")
    return "\n\n".join(lines)
