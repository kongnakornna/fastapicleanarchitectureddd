"""embeddings application utils"""
from __future__ import annotations
import json
import time
from typing import Any

from app.modules.embeddings.domain.helpers.hasher import content_hash


def make_cache_key(tenant_id: str, model: str, text: str) -> str:
    h = content_hash(text)
    return f"emb:cache:{tenant_id}:{model}:{h}"


def make_vector_hash(text: str, model: str) -> str:
    return content_hash(text, prefix=f"{model}:")


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


def ms_now() -> int:
    return int(time.time() * 1000)
