"""llm application utils"""
from __future__ import annotations
import hashlib
from typing import Any

from app.modules.llm.domain.value_objects import ChatOptions


def build_cache_key(
    messages: list[dict[str, Any]],
    model: str,
    options: ChatOptions,
) -> str:
    """TH: สร้าง cache key จาก hash | EN: build deterministic cache key"""
    parts = [model]
    for m in messages:
        parts.append(f"{m.get('role','')}:{m.get('content','')}")
    parts.append(f"t={options.temperature}")
    parts.append(f"m={options.max_tokens}")
    parts.append(f"p={options.top_p}")
    raw = "|".join(parts)
    return "llm:cache:" + hashlib.sha256(raw.encode()).hexdigest()[:32]


def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
    """TH: ทำความสะอาด payload | EN: sanitize payload"""
    MASK = {
        "api_key", "api_key_encrypted", "password",
        "token", "secret",
    }
    return {k: ("***" if k in MASK else v) for k, v in data.items()}
