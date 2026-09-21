"""Idempotency value objects — วัตถุค่า idempotency"""
from __future__ import annotations


from dataclasses import dataclass

from .exceptions import DomainError


@dataclass(frozen=True)
class IdempotencyKey:
    """Idempotency key VO — วัตถุกุญแจ idempotency"""

    value: str
    scope: str  # e.g., "invoice.create"

    def __post_init__(self):
        if len(self.value) < 8 or len(self.value) > 255:
            raise DomainError("Idempotency key length must be 8-255")

    def redis_key(self, tenant_id: str) -> str:
        return f"t:{tenant_id}:idem:{self.scope}:{self.value}"
