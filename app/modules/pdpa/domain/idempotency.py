"""pdpa domain entity: IdempotencyRecord"""
from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .enums import IdempotencyStatus

_DEFAULT_TTL_HOURS = 24


def compute_request_hash(payload: dict[str, Any]) -> str:
    """TH: hash payload แบบ deterministic | EN: deterministic payload hash"""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class IdempotencyRecord:
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None
    idempotency_key: str
    request_method: str
    request_path: str
    request_hash: str
    status: IdempotencyStatus
    response_status: int | None
    response_body: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    @classmethod
    def start(
        cls,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None,
        idempotency_key: str,
        request_method: str,
        request_path: str,
        request_hash: str,
        ttl_hours: int = _DEFAULT_TTL_HOURS,
    ) -> "IdempotencyRecord":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            idempotency_key=idempotency_key,
            request_method=request_method,
            request_path=request_path,
            request_hash=request_hash,
            status=IdempotencyStatus.IN_PROGRESS,
            response_status=None,
            response_body=None,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
        )

    def mark_completed(self, status: int, body: dict[str, Any]) -> None:
        self.status = IdempotencyStatus.COMPLETED
        self.response_status = status
        self.response_body = body
        self.updated_at = datetime.now(UTC)

    def mark_failed(self, status: int | None = None) -> None:
        self.status = IdempotencyStatus.FAILED
        self.response_status = status
        self.updated_at = datetime.now(UTC)

    def matches(self, request_hash: str) -> bool:
        return self.request_hash == request_hash

    def is_expired(self, *, now: datetime | None = None) -> bool:
        return (now or datetime.now(UTC)) >= self.expires_at