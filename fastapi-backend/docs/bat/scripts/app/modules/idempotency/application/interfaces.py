"""Idempotency application interfaces — Protocol"""

from typing import Protocol

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey


class IIdempotencyStore(Protocol):
    """IIdempotencyStore — อินเทอร์เฟซ store"""

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None: ...

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None: ...

    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool: ...

    async def unlock(self, key: IdempotencyKey, tenant_id: str) -> None: ...
