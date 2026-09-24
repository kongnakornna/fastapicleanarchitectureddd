"""Token counter — นับ token แบบ best-effort"""
from __future__ import annotations

import structlog

log = structlog.get_logger()

_ENCODINGS: dict[str, object] = {}


def _get_encoding(model: str) -> object | None:
    try:
        import tiktoken
    except ImportError:
        return None
    if model in _ENCODINGS:
        return _ENCODINGS[model]
    try:
        enc = tiktoken.encoding_for_model(model)
        _ENCODINGS[model] = enc
        return enc
    except Exception:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            _ENCODINGS[model] = enc
            return enc
        except Exception:
            return None


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """TH: นับ token | EN: count tokens (never-raise)"""
    if not text:
        return 0
    enc = _get_encoding(model)
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception as exc:
            log.warning("token_counter.encode_failed", err=str(exc))
    return max(1, len(text) // 4)


def count_message_tokens(
    messages: list[dict], model: str = "gpt-4o-mini",
) -> int:
    """TH: นับ token ของ messages | EN: count message tokens"""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += count_tokens(content, model)
        total += 4
    return total + 2
