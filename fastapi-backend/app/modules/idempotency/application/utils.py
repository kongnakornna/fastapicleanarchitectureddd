"""Idempotency application utils — เครื่องมือช่วย"""

import functools
import hashlib
import json
from collections.abc import Callable


def hash_payload(payload: dict) -> str:
    """แฮช payload — Hash payload deterministically"""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def idempotent(fn: Callable) -> Callable:
    """Decorator สำหรับ idempotent — Decorator for idempotent methods"""

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        return await fn(*args, **kwargs)

    return wrapper
