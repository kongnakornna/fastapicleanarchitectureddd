"""Inventory application interfaces (ports) — Protocol"""
from __future__ import annotations

import uuid
from typing import Protocol

from ..domain.entities import Inventory
from ..domain.value_objects import Money


class IInventoryRepository(Protocol):
    """IInventoryRepository — port ของ repository"""

    async def save(self, entity: Inventory) -> Inventory: ...
    async def get_by_id(self, entity_id: uuid.UUID) -> Inventory | None: ...
    async def get_by_code(self, code: str) -> Inventory | None: ...
    async def list(
        self, *, status: str | None, q: str | None, limit: int, offset: int
    ) -> tuple[list[Inventory], int]: ...
    async def soft_delete(self, entity_id: uuid.UUID) -> None: ...


class IInventoryCache(Protocol):
    """IInventoryCache — port ของ cache.

    Contract:
      - never raise — Postgres is source of truth, Redis is best-effort
      - invalidate() writes a tombstone BEFORE deleting the entry
      - set() checks for a tombstone BEFORE writing
    """

    async def get(self, key: str) -> Inventory | None: ...
    async def set(
        self, key: str, entity: Inventory, ttl: int = 3600
    ) -> None: ...
    async def invalidate(self, key: str) -> bool: ...


class IEventBus(Protocol):
    """IEventBus — port ของ event bus"""

    async def publish(self, event: object) -> None: ...


class IIdempotencyStore(Protocol):
    """IIdempotencyStore — port ของ idempotency"""

    async def check_or_lock(
        self, *, key: str, scope: str, payload: dict, tenant_id: str
    ) -> object | None: ...
    async def complete(
        self, *, key: str, scope: str, tenant_id: str,
        status: int, body: dict
    ) -> None: ...


class IMoneyConverter(Protocol):
    """IMoneyConverter — แปลงสกุลเงิน (optional)"""

    def convert(self, amount: Money, rate: object) -> Money: ...