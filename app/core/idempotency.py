"""Idempotency store — stub (in-memory)"""
from __future__ import annotations

from typing import Any


class IdempotencyStore:
    """TH: idempotency store | EN: idempotency store"""

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    async def check_or_lock(
        self, key: str, scope: str, payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        """TH: ตรวจ key ซ้ำ | EN: check or lock"""
        full_key = f"{scope}:{key}"
        return self._cache.get(full_key)

    async def complete(
        self, key: str, scope: str, status: int, body: dict[str, Any],
    ) -> None:
        """TH: บันทึกผลลัพธ์ | EN: mark complete"""
        full_key = f"{scope}:{key}"
        self._cache[full_key] = body


_store: IdempotencyStore | None = None


def get_idempotency_store() -> IdempotencyStore:
    """TH: DI idempotency store | EN: DI idempotency store"""
    global _store
    if _store is None:
        _store = IdempotencyStore()
    return _store
