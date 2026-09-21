# 📦 Module 4: `idempotency` — Exactly-Once Semantics for Money/Goods Path (Layer 0)

> **สถานะ:** เริ่มสร้างแล้ว — Cross-cutting module บังคับ idempotency สำหรับ money/goods path
> **Layer:** 0 (Core) · **Priority:** 🔴 · **Phase:** 1
> **Dependencies:** `tenant_context`, `audit` (optional)

---

## 🎯 หลักการออกแบบ

| ประเด็น | แนวทาง |
|---|---|
| **Two-phase commit** | Redis `SET NX` (fast lock) → Postgres (durable) → Redis (cache result) |
| **Fingerprint match** | `SHA256(method ‖ path ‖ canonical_body)` — กัน key reuse ผิด payload |
| **State machine** | `PENDING → COMPLETED / FAILED / EXPIRED` |
| **Concurrent safety** | PENDING ที่ยัง lock อยู่ → `409 Conflict` |
| **Cached response replay** | COMPLETED + fingerprint ตรง → คืน response เดิมเป๊ะ |
| **TTL bounded** | 1h – 7d (default 24h) |
| **Context manager** | `async with idem.guard(key, fp) as g:` — ใช้สวย |
| **Money-path strict** | ถ้าไม่มี key → `IdempotencyRequiredError` |

---

## 📐 โครงสร้างไฟล์ที่ส่งมอบ

```
app/modules/idempotency/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── enums.py
│   ├── value_objects.py
│   └── entities.py
├── application/
│   ├── __init__.py
│   ├── interfaces.py
│   ├── exceptions.py
│   ├── mappers.py
│   ├── utils.py
│   └── use_cases.py
├── infrastructure/
│   ├── __init__.py
│   ├── models.py
│   ├── repositories.py
│   ├── caches.py
│   └── services.py
└── presentation/
    ├── __init__.py
    ├── schemas.py
    ├── docs.py
    ├── dependencies.py
    └── routers.py

tests/unit/test_idempotency.py
```

**22 ไฟล์** (domain 4 + application 6 + infrastructure 4 + presentation 5 + init 2 + tests 1)

---

## 📄 1. `app/modules/idempotency/__init__.py`

```python
"""Idempotency module — โมดูล idempotency สำหรับ money/goods path."""
```

---

## 📄 2. `app/modules/idempotency/domain/__init__.py`

```python
"""Domain layer — เลเยอร์โดเมนของ idempotency."""
from app.modules.idempotency.domain.entities import IdempotencyRecord, IdempotencyScope
from app.modules.idempotency.domain.enums import (
    FingerprintStrategy,
    IdempotencyStatus,
)
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    IdempotencyTTL,
    RequestFingerprint,
)

__all__ = [
    "IdempotencyKey",
    "RequestFingerprint",
    "IdempotencyTTL",
    "IdempotencyRecord",
    "IdempotencyScope",
    "IdempotencyStatus",
    "FingerprintStrategy",
]
```

---

## 📄 3. `app/modules/idempotency/domain/enums.py`

```python
"""Enums for idempotency — Enum ของโมดูล idempotency."""
from enum import Enum


class IdempotencyStatus(str, Enum):
    """Idempotency record lifecycle — วงจรชีวิตของ record"""
    PENDING = "PENDING"        # กำลังประมวลผล — in-flight
    COMPLETED = "COMPLETED"    # สำเร็จ — cached response
    FAILED = "FAILED"          # ล้มเหลว — สามารถ retry ได้
    EXPIRED = "EXPIRED"        # หมดอายุ — TTL ผ่าน


class FingerprintStrategy(str, Enum):
    """How to compute request fingerprint — วิธีคำนวณ fingerprint"""
    BODY = "BODY"                          # hash body only
    BODY_AND_QUERY = "BODY_AND_QUERY"      # + query params
    METHOD_PATH_BODY = "METHOD_PATH_BODY"  # full — default


class GuardOutcome(str, Enum):
    """Outcome of guard context — ผลลัพธ์การ guard"""
    EXECUTE = "EXECUTE"        # ต้องประมวลผล — execute now
    CACHED = "CACHED"          # คืน response cache — replay
    IN_FLIGHT = "IN_FLIGHT"    # กำลังทำงาน — conflict
    FAILED_RETRY = "FAILED_RETRY"  # FAILED → retry
```

---

## 📄 4. `app/modules/idempotency/domain/value_objects.py`

```python
"""Value objects for idempotency — วัตถุค่าของโมดูล idempotency."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Any

from app.modules.idempotency.domain.enums import FingerprintStrategy
from app.modules.shared.domain.errors import DomainError


# ─────────────────────────────────────────────────────────────
# IdempotencyKey VO
# ─────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class IdempotencyKey:
    """Idempotency key VO — วัตถุ idempotency key.

    Format: [A-Za-z0-9_\\-:.]+ , 8..128 chars
    """

    value: str

    PATTERN = re.compile(r"^[A-Za-z0-9_\-:.]+$")
    MIN_LEN = 8
    MAX_LEN = 128

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.value, str):
            raise DomainError("IdempotencyKey must be a string")
        if not self.MIN_LEN <= len(self.value) <= self.MAX_LEN:
            raise DomainError(
                f"IdempotencyKey length must be {self.MIN_LEN}..{self.MAX_LEN}, "
                f"got {len(self.value)}"
            )
        if not self.PATTERN.match(self.value):
            raise DomainError(
                f"IdempotencyKey contains invalid characters: {self.value!r}"
            )

    def __str__(self) -> str:
        return self.value


# ─────────────────────────────────────────────────────────────
# RequestFingerprint VO
# ─────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class RequestFingerprint:
    """SHA-256 fingerprint of the request — ลายนิ้วมือคำขอ.

    Detects reuse of the same Idempotency-Key with a different payload.
    ตรวจจับการใช้ key ซ้ำกับ payload ที่ต่างกัน
    """

    value: str
    strategy: FingerprintStrategy = FingerprintStrategy.METHOD_PATH_BODY

    PATTERN = re.compile(r"^[0-9a-f]{64}$")

    def __post_init__(self) -> None:
        if not self.PATTERN.match(self.value):
            raise DomainError("Invalid fingerprint format (must be SHA-256 hex)")

    @classmethod
    def compute(
        cls,
        method: str,
        path: str,
        body: dict | None = None,
        query: dict | None = None,
        strategy: FingerprintStrategy = FingerprintStrategy.METHOD_PATH_BODY,
    ) -> "RequestFingerprint":
        """Compute fingerprint — คำนวณ fingerprint"""
        parts: dict[str, Any] = {}
        if strategy in (
            FingerprintStrategy.BODY,
            FingerprintStrategy.BODY_AND_QUERY,
            FingerprintStrategy.METHOD_PATH_BODY,
        ):
            parts["body"] = body or {}
        if strategy in (FingerprintStrategy.BODY_AND_QUERY,):
            parts["query"] = query or {}
        if strategy == FingerprintStrategy.METHOD_PATH_BODY:
            parts["method"] = method.upper()
            parts["path"] = path

        canonical = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=_json_default)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(value=digest, strategy=strategy)

    def __str__(self) -> str:
        return self.value


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    return str(obj)


# ─────────────────────────────────────────────────────────────
# IdempotencyTTL VO
# ─────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class IdempotencyTTL:
    """TTL bounded 1h..7d — เวลาอยู่ในระบบ 1 ชม..7 วัน"""

    seconds: int

    MIN_SECONDS = 3600            # 1 hour
    MAX_SECONDS = 7 * 24 * 3600   # 7 days
    DEFAULT_SECONDS = 24 * 3600   # 24 hours

    def __post_init__(self) -> None:
        if not isinstance(self.seconds, int):
            raise DomainError("TTL seconds must be int")
        if not self.MIN_SECONDS <= self.seconds <= self.MAX_SECONDS:
            raise DomainError(
                f"TTL must be {self.MIN_SECONDS}..{self.MAX_SECONDS}s, "
                f"got {self.seconds}"
            )

    @classmethod
    def default(cls) -> "IdempotencyTTL":
        return cls(cls.DEFAULT_SECONDS)

    @property
    def as_timedelta(self) -> timedelta:
        return timedelta(seconds=self.seconds)

    def __str__(self) -> str:
        return f"TTL({self.seconds}s)"
```

---

## 📄 5. `app/modules/idempotency/domain/entities.py`

```python
"""Entities for idempotency — เอนทิตีของโมดูล idempotency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.modules.idempotency.domain.enums import IdempotencyStatus
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    IdempotencyTTL,
    RequestFingerprint,
)
from app.modules.shared.domain.entities import BaseEntity
from app.modules.shared.domain.errors import DomainError


@dataclass
class IdempotencyRecord(BaseEntity):
    """Idempotency record — บันทึก idempotency.

    Invariants:
      - key + tenant_id เป็น unique
      - COMPLETED record's response ห้ามแก้
      - fingerprint ห้ามเปลี่ยนหลัง PENDING
    """

    tenant_id: str = ""
    key: IdempotencyKey | None = None
    fingerprint: RequestFingerprint | None = None
    status: IdempotencyStatus = IdempotencyStatus.PENDING
    ttl: IdempotencyTTL = field(default_factory=IdempotencyTTL.default)

    # Response cache
    response_status: int | None = None
    response_body: dict | None = None
    response_headers: dict = field(default_factory=dict)

    # Timing
    locked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    expires_at: datetime | None = None

    # Error
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.expires_at is None:
            object.__setattr__(
                self, "expires_at", self.locked_at + self.ttl.as_timedelta
            )
        self._validate()

    def _validate(self) -> None:
        if not self.tenant_id:
            raise DomainError("tenant_id is required")
        if self.key is None:
            raise DomainError("idempotency key is required")
        if self.fingerprint is None:
            raise DomainError("fingerprint is required")
        if self.status == IdempotencyStatus.COMPLETED and self.response_status is None:
            raise DomainError("COMPLETED record must have response_status")
        if self.status == IdempotencyStatus.FAILED and not self.error_code:
            raise DomainError("FAILED record must have error_code")

    # ── State transitions ─────────────────────────────────────
    def complete(
        self,
        response_status: int,
        response_body: dict | None,
        response_headers: dict | None = None,
    ) -> None:
        """Mark COMPLETED — ทำเครื่องหมายสำเร็จ"""
        if self.status != IdempotencyStatus.PENDING:
            raise DomainError(
                f"Cannot complete from status {self.status.value}"
            )
        self.status = IdempotencyStatus.COMPLETED
        self.response_status = response_status
        self.response_body = response_body or {}
        self.response_headers = response_headers or {}
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error_code: str, error_message: str) -> None:
        """Mark FAILED — ทำเครื่องหมายล้มเหลว"""
        if self.status != IdempotencyStatus.PENDING:
            raise DomainError(f"Cannot fail from status {self.status.value}")
        self.status = IdempotencyStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        """Mark EXPIRED — ทำเครื่องหมายหมดอายุ"""
        if self.status in (IdempotencyStatus.COMPLETED, IdempotencyStatus.FAILED):
            # keep terminal status but flag expiry
            return
        self.status = IdempotencyStatus.EXPIRED

    # ── Queries ───────────────────────────────────────────────
    @property
    def is_pending(self) -> bool:
        return self.status == IdempotencyStatus.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status == IdempotencyStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == IdempotencyStatus.FAILED

    @property
    def is_terminal(self) -> bool:
        return self.status in (
            IdempotencyStatus.COMPLETED,
            IdempotencyStatus.FAILED,
            IdempotencyStatus.EXPIRED,
        )

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.expires_at is not None and now >= self.expires_at

    def fingerprint_matches(self, other: RequestFingerprint) -> bool:
        return self.fingerprint is not None and self.fingerprint.value == other.value

    def cached_response(self) -> dict | None:
        """Return cached response dict — คืน response ที่ cache"""
        if not self.is_completed:
            return None
        return {
            "status": self.response_status,
            "body": self.response_body,
            "headers": self.response_headers,
        }

    def remaining_ttl_seconds(self, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        if self.expires_at is None:
            return 0
        delta = (self.expires_at - now).total_seconds()
        return max(0, int(delta))


@dataclass
class IdempotencyScope(BaseEntity):
    """Scope grouping idempotency records by workflow — กลุ่ม record ตาม workflow.

    e.g., one checkout flow → multiple idempotent sub-operations
    """

    tenant_id: str = ""
    scope_key: str = ""
    records: list[IdempotencyRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.tenant_id:
            raise DomainError("tenant_id is required")
        if not self.scope_key:
            raise DomainError("scope_key is required")

    def add(self, record: IdempotencyRecord) -> None:
        if record.tenant_id != self.tenant_id:
            raise DomainError("Cannot add record from different tenant")
        self.records.append(record)

    @property
    def all_completed(self) -> bool:
        return bool(self.records) and all(r.is_completed for r in self.records)

    @property
    def any_failed(self) -> bool:
        return any(r.is_failed for r in self.records)
```

---

## 📄 6. `app/modules/idempotency/application/__init__.py`

```python
"""Application layer — เลเยอร์แอปพลิเคชันของ idempotency."""
```

---

## 📄 7. `app/modules/idempotency/application/exceptions.py`

```python
"""Exceptions for idempotency — ข้อยกเว้นของโมดูล idempotency."""
from app.modules.shared.domain.errors import DomainError, StandardException


class IdempotencyException(StandardException):
    """Base exception — ข้อยกเว้นฐาน."""


class DomainException(IdempotencyException):
    """Wraps DomainError — ห่อ DomainError."""

    def __init__(self, cause: DomainError) -> None:
        self.cause = cause
        super().__init__(str(cause))


class IdempotencyRequiredError(IdempotencyException):
    """Money/goods path must include Idempotency-Key — ต้องมี key."""


class IdempotencyConflictError(IdempotencyException):
    """Same key already in-flight (PENDING) — key กำลังประมวลผล."""


class IdempotencyKeyReuseError(IdempotencyException):
    """Same key used with different payload — ใช้ key ซ้ำ payload ต่าง."""


class IdempotencyRecordNotFoundError(IdempotencyException):
    """Record not found — ไม่พบ record."""


class IdempotencyExpiredError(IdempotencyException):
    """Record expired — record หมดอายุ."""


class IdempotencyLockError(IdempotencyException):
    """Failed to acquire lock — ล็อกไม่สำเร็จ."""


class IdempotencyStoreError(IdempotencyException):
    """Storage failure — ที่เก็บล้มเหลว."""
```

---

## 📄 8. `app/modules/idempotency/application/interfaces.py`

```python
"""Protocol interfaces for idempotency — สัญญา Protocol."""
from __future__ import annotations

from typing import Protocol

from app.modules.idempotency.domain.entities import IdempotencyRecord
from app.modules.idempotency.domain.enums import FingerprintStrategy
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    RequestFingerprint,
)


class IIdempotencyRepository(Protocol):
    """Durable repository — รีโพซิทอรีแบบถาวร."""

    async def insert_pending(self, record: IdempotencyRecord) -> IdempotencyRecord: ...
    async def get(self, tenant_id: str, key: IdempotencyKey) -> IdempotencyRecord | None: ...
    async def complete(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        response_status: int,
        response_body: dict,
        response_headers: dict,
    ) -> IdempotencyRecord: ...
    async def fail(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        error_code: str,
        error_message: str,
    ) -> IdempotencyRecord: ...
    async def delete(self, tenant_id: str, key: IdempotencyKey) -> None: ...
    async def purge_expired(self, tenant_id: str, limit: int = 1000) -> int: ...


class IIdempotencyLock(Protocol):
    """Distributed lock (Redis) — ล็อกแบบกระจาย."""

    async def acquire(
        self, tenant_id: str, key: IdempotencyKey, ttl_seconds: int
    ) -> bool: ...
    async def release(self, tenant_id: str, key: IdempotencyKey) -> None: ...
    async def is_locked(self, tenant_id: str, key: IdempotencyKey) -> bool: ...


class IIdempotencyCache(Protocol):
    """Fast lookup cache for records — แคช record."""

    async def get(self, tenant_id: str, key: IdempotencyKey) -> dict | None: ...
    async def set(
        self, tenant_id: str, key: IdempotencyKey, record: dict, ttl_seconds: int
    ) -> None: ...
    async def invalidate(self, tenant_id: str, key: IdempotencyKey) -> None: ...


class IIdempotencyEventBus(Protocol):
    """Event bus — บัสเหตุการณ์."""

    async def publish(self, event_name: str, payload: dict) -> None: ...
```

---

## 📄 9. `app/modules/idempotency/application/utils.py`

```python
"""Utilities for idempotency — ยูทิลิตี้ของโมดูล idempotency."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.modules.idempotency.domain.enums import FingerprintStrategy
from app.modules.idempotency.domain.value_objects import RequestFingerprint


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_fingerprint(
    method: str,
    path: str,
    body: dict | None = None,
    query: dict | None = None,
    strategy: FingerprintStrategy = FingerprintStrategy.METHOD_PATH_BODY,
) -> RequestFingerprint:
    """Compute request fingerprint — คำนวณ fingerprint"""
    return RequestFingerprint.compute(method, path, body, query, strategy)


def canonical_json(payload: dict) -> str:
    """Canonical JSON — JSON แบบ canonical"""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def body_digest(body: dict) -> str:
    """SHA-256 of body — แฮชของ body"""
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()


def safe_body_for_log(body: dict | None, max_len: int = 512) -> str:
    """Truncate body for logging — ตัด body สำหรับ log"""
    if body is None:
        return "<none>"
    raw = canonical_json(body)
    if len(raw) <= max_len:
        return raw
    return raw[:max_len] + f"...({len(raw)} bytes)"
```

---

## 📄 10. `app/modules/idempotency/application/mappers.py`

```python
"""Mappers for idempotency — ตัวแปลงข้อมูล.

Sections:
  # IDEM/SCHEMAS
  # IDEM/MODELS
  # IDEM/CACHE
  # IDEM/EVENTS
"""
from __future__ import annotations

from app.modules.idempotency.domain.entities import IdempotencyRecord
from app.modules.idempotency.domain.enums import IdempotencyStatus
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    IdempotencyTTL,
    RequestFingerprint,
)


class IdempotencyMapper:
    """Idempotency mapper — ตัวแปลงข้อมูล idempotency."""

    # ── IDEM/SCHEMAS ──────────────────────────────────────────
    @staticmethod
    def to_schema_dict(record: IdempotencyRecord) -> dict:
        return {
            "id": record.id,
            "tenant_id": record.tenant_id,
            "key": record.key.value if record.key else None,
            "fingerprint": record.fingerprint.value if record.fingerprint else None,
            "status": record.status.value,
            "response_status": record.response_status,
            "response_body": record.response_body,
            "response_headers": record.response_headers,
            "locked_at": record.locked_at.isoformat() if record.locked_at else None,
            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
            "expires_at": record.expires_at.isoformat() if record.expires_at else None,
            "error_code": record.error_code,
            "error_message": record.error_message,
        }

    @staticmethod
    def to_status_dict(record: IdempotencyRecord) -> dict:
        return {
            "key": record.key.value if record.key else None,
            "status": record.status.value,
            "is_terminal": record.is_terminal,
            "remaining_ttl_seconds": record.remaining_ttl_seconds(),
        }

    # ── IDEM/MODELS ───────────────────────────────────────────
    @staticmethod
    def to_model_dict(record: IdempotencyRecord) -> dict:
        return {
            "id": record.id,
            "tenant_id": record.tenant_id,
            "key": record.key.value if record.key else "",
            "fingerprint": record.fingerprint.value if record.fingerprint else "",
            "status": record.status.value,
            "response_status": record.response_status,
            "response_body": record.response_body,
            "response_headers": record.response_headers,
            "locked_at": record.locked_at,
            "completed_at": record.completed_at,
            "expires_at": record.expires_at,
            "ttl_seconds": record.ttl.seconds,
            "error_code": record.error_code,
            "error_message": record.error_message,
        }

    @staticmethod
    def from_model(model) -> IdempotencyRecord:
        return IdempotencyRecord(
            id=model.id,
            tenant_id=model.tenant_id,
            key=IdempotencyKey(model.key),
            fingerprint=RequestFingerprint(model.fingerprint),
            status=IdempotencyStatus(model.status),
            ttl=IdempotencyTTL(model.ttl_seconds),
            response_status=model.response_status,
            response_body=model.response_body,
            response_headers=model.response_headers or {},
            locked_at=model.locked_at,
            completed_at=model.completed_at,
            expires_at=model.expires_at,
            error_code=model.error_code,
            error_message=model.error_message,
        )

    # ── IDEM/CACHE ────────────────────────────────────────────
    @staticmethod
    def to_cache_dict(record: IdempotencyRecord) -> dict:
        return {
            "id": record.id,
            "tenant_id": record.tenant_id,
            "key": record.key.value if record.key else None,
            "fingerprint": record.fingerprint.value if record.fingerprint else None,
            "status": record.status.value,
            "response_status": record.response_status,
            "response_body": record.response_body,
            "response_headers": record.response_headers,
            "error_code": record.error_code,
            "error_message": record.error_message,
            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
        }

    @staticmethod
    def from_cache_dict(data: dict) -> dict:
        """Return raw dict (already shaped for guard) — คืน dict ดิบ"""
        return data

    # ── IDEM/EVENTS ───────────────────────────────────────────
    @staticmethod
    def to_event_payload(record: IdempotencyRecord) -> dict:
        return {
            "key": record.key.value if record.key else None,
            "tenant_id": record.tenant_id,
            "fingerprint": record.fingerprint.value if record.fingerprint else None,
            "status": record.status.value,
            "response_status": record.response_status,
        }
```

---

## 📄 11. `app/modules/idempotency/application/use_cases.py`

```python
"""Idempotency use cases — กรณีการใช้งาน idempotency."""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator

from loguru import logger

from app.modules.idempotency.application.exceptions import (
    DomainException,
    IdempotencyConflictError,
    IdempotencyException,
    IdempotencyKeyReuseError,
    IdempotencyLockError,
    IdempotencyRecordNotFoundError,
    IdempotencyRequiredError,
    IdempotencyStoreError,
)
from app.modules.idempotency.application.interfaces import (
    IIdempotencyCache,
    IIdempotencyEventBus,
    IIdempotencyLock,
    IIdempotencyRepository,
)
from app.modules.idempotency.application.mappers import IdempotencyMapper
from app.modules.idempotency.domain.entities import IdempotencyRecord
from app.modules.idempotency.domain.enums import GuardOutcome, IdempotencyStatus
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    IdempotencyTTL,
    RequestFingerprint,
)
from app.modules.shared.domain.errors import DomainError, StandardException


@dataclass
class GuardContext:
    """Context yielded by guard — บริบทที่ guard คืนให้"""

    key: IdempotencyKey
    fingerprint: RequestFingerprint
    outcome: GuardOutcome
    cached_response: dict | None = None
    _use_cases: "IdempotencyUseCases | None" = None

    @property
    def should_execute(self) -> bool:
        return self.outcome in (GuardOutcome.EXECUTE, GuardOutcome.FAILED_RETRY)

    def record_response(
        self,
        status: int,
        body: dict | None = None,
        headers: dict | None = None,
    ) -> None:
        """Mark completion — กำหนดผลลัพธ์สำเร็จ"""
        self._status = status
        self._body = body or {}
        self._headers = headers or {}

    def record_failure(self, error_code: str, error_message: str) -> None:
        """Mark failure — กำหนดผลลัพธ์ล้มเหลว"""
        self._error_code = error_code
        self._error_message = error_message


class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency."""

    def __init__(
        self,
        repo: IIdempotencyRepository,
        lock: IIdempotencyLock,
        cache: IIdempotencyCache | None = None,
        event_bus: IIdempotencyEventBus | None = None,
        default_ttl: IdempotencyTTL | None = None,
    ) -> None:
        self.repo = repo
        self.lock = lock
        self.cache = cache
        self.event_bus = event_bus
        self.default_ttl = default_ttl or IdempotencyTTL.default()

    # ── Guard (context manager) ───────────────────────────────
    @asynccontextmanager
    async def guard(
        self,
        tenant_id: str,
        key: IdempotencyKey | None,
        fingerprint: RequestFingerprint,
        *,
        required: bool = False,
        ttl: IdempotencyTTL | None = None,
    ) -> AsyncIterator[GuardContext]:
        """Guard a money/goods-path operation — ป้องกันการทำงานซ้ำ.

        Usage:
            async with idem.guard(tenant, key, fp, required=True) as g:
                if g.cached_response:
                    return g.cached_response
                result = await do_work()
                g.record_response(201, result)
        """
        try:
            # 1) Required check
            if key is None:
                if required:
                    raise IdempotencyRequiredError(
                        "Idempotency-Key header is required for this operation"
                    )
                # Non-required path — execute directly
                yield GuardContext(
                    key=IdempotencyKey("auto_" + fingerprint.value[:32]),
                    fingerprint=fingerprint,
                    outcome=GuardOutcome.EXECUTE,
                    _use_cases=self,
                )
                return

            # 2) Fast cache lookup
            cached = await self._cache_get(tenant_id, key)
            ctx = await self._resolve_existing(tenant_id, key, fingerprint, cached)
            if ctx is not None and not ctx.should_execute:
                yield ctx
                return

            # 3) Acquire distributed lock
            ttl_used = ttl or self.default_ttl
            acquired = await self.lock.acquire(tenant_id, key, ttl_used.seconds)
            if not acquired:
                # Someone else is processing → 409-style
                yield GuardContext(
                    key=key,
                    fingerprint=fingerprint,
                    outcome=GuardOutcome.IN_FLIGHT,
                    _use_cases=self,
                )
                return

            # 4) Insert PENDING (durable)
            record = IdempotencyRecord(
                tenant_id=tenant_id,
                key=key,
                fingerprint=fingerprint,
                ttl=ttl_used,
            )
            try:
                record = await self.repo.insert_pending(record)
            except Exception as e:
                # Unique constraint conflict → another request got there first
                await self.lock.release(tenant_id, key)
                logger.warning(f"insert_pending conflict: {e}")
                refreshed = await self.repo.get(tenant_id, key)
                if refreshed and refreshed.fingerprint_matches(fingerprint):
                    if refreshed.is_completed:
                        yield GuardContext(
                            key=key,
                            fingerprint=fingerprint,
                            outcome=GuardOutcome.CACHED,
                            cached_response=refreshed.cached_response(),
                            _use_cases=self,
                        )
                        return
                    yield GuardContext(
                        key=key,
                        fingerprint=fingerprint,
                        outcome=GuardOutcome.IN_FLIGHT,
                        _use_cases=self,
                    )
                    return
                raise IdempotencyStoreError("Failed to insert PENDING record")

            # 5) Execute
            ctx = GuardContext(
                key=key,
                fingerprint=fingerprint,
                outcome=GuardOutcome.EXECUTE,
                _use_cases=self,
            )
            try:
                yield ctx
            except Exception as exc:
                # User code raised → mark FAILED, then re-raise
                await self._mark_failed(record, exc)
                raise
            else:
                await self._mark_completed(record, ctx)
            finally:
                await self.lock.release(tenant_id, key)
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.guard")
            raise IdempotencyException()

    # ── Explicit API (alternative to context manager) ─────────
    async def begin(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        fingerprint: RequestFingerprint,
        ttl: IdempotencyTTL | None = None,
    ) -> tuple[GuardOutcome, IdempotencyRecord | None]:
        """Begin — เริ่ม (สำหรับคนไม่ชอบ context manager)"""
        try:
            cached = await self._cache_get(tenant_id, key)
            existing = await self._load_existing(tenant_id, key, cached)

            if existing is not None:
                if not existing.fingerprint_matches(fingerprint):
                    raise IdempotencyKeyReuseError(
                        "Idempotency-Key reused with different payload"
                    )
                if existing.is_completed:
                    return GuardOutcome.CACHED, existing
                if existing.is_pending:
                    return GuardOutcome.IN_FLIGHT, existing
                if existing.is_failed:
                    # allow retry
                    await self.repo.delete(tenant_id, key)
                    await self._cache_invalidate(tenant_id, key)

            acquired = await self.lock.acquire(
                tenant_id, key, (ttl or self.default_ttl).seconds
            )
            if not acquired:
                return GuardOutcome.IN_FLIGHT, existing

            record = IdempotencyRecord(
                tenant_id=tenant_id,
                key=key,
                fingerprint=fingerprint,
                ttl=ttl or self.default_ttl,
            )
            record = await self.repo.insert_pending(record)
            return GuardOutcome.EXECUTE, record
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.begin")
            raise IdempotencyException()

    async def complete(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        response_status: int,
        response_body: dict | None = None,
        response_headers: dict | None = None,
    ) -> IdempotencyRecord:
        """Complete — สำเร็จ"""
        try:
            record = await self.repo.complete(
                tenant_id, key, response_status, response_body or {}, response_headers or {}
            )
            await self._cache_set(tenant_id, record)
            await self._publish("IdempotencyCompleted", record)
            await self.lock.release(tenant_id, key)
            return record
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.complete")
            raise IdempotencyStoreError()

    async def fail(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        error_code: str,
        error_message: str,
    ) -> IdempotencyRecord:
        """Fail — ล้มเหลว"""
        try:
            record = await self.repo.fail(tenant_id, key, error_code, error_message)
            await self._cache_set(tenant_id, record)
            await self._publish("IdempotencyFailed", record)
            await self.lock.release(tenant_id, key)
            return record
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.fail")
            raise IdempotencyStoreError()

    # ── Queries ───────────────────────────────────────────────
    async def get(
        self, tenant_id: str, key: IdempotencyKey
    ) -> IdempotencyRecord:
        try:
            cached = await self._cache_get(tenant_id, key)
            record = await self._load_existing(tenant_id, key, cached)
            if record is None:
                raise IdempotencyRecordNotFoundError(
                    f"Idempotency record not found for key {key.value}"
                )
            return record
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.get")
            raise IdempotencyException()

    async def purge_expired(self, tenant_id: str, limit: int = 1000) -> int:
        """Purge expired — ล้างที่หมดอายุ"""
        try:
            return await self.repo.purge_expired(tenant_id, limit)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idempotency.purge_expired")
            raise IdempotencyException()

    # ── Internals ─────────────────────────────────────────────
    async def _resolve_existing(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        fingerprint: RequestFingerprint,
        cached: dict | None,
    ) -> GuardContext | None:
        """Resolve existing record → GuardContext or None (execute)."""
        existing = await self._load_existing(tenant_id, key, cached)
        if existing is None:
            return None

        if not existing.fingerprint_matches(fingerprint):
            raise IdempotencyKeyReuseError(
                f"Idempotency-Key {key.value!r} reused with different payload"
            )

        if existing.is_completed:
            return GuardContext(
                key=key,
                fingerprint=fingerprint,
                outcome=GuardOutcome.CACHED,
                cached_response=existing.cached_response(),
                _use_cases=self,
            )
        if existing.is_pending:
            return GuardContext(
                key=key,
                fingerprint=fingerprint,
                outcome=GuardOutcome.IN_FLIGHT,
                _use_cases=self,
            )
        if existing.is_failed:
            # allow retry
            await self.repo.delete(tenant_id, key)
            await self._cache_invalidate(tenant_id, key)
            return GuardContext(
                key=key,
                fingerprint=fingerprint,
                outcome=GuardOutcome.FAILED_RETRY,
                _use_cases=self,
            )
        return None

    async def _load_existing(
        self, tenant_id: str, key: IdempotencyKey, cached: dict | None
    ) -> IdempotencyRecord | None:
        """Load existing from cache or DB — โหลดจาก cache/DB"""
        if cached is not None:
            try:
                return IdempotencyMapper.from_model(_DictModel(cached))
            except Exception:
                pass
        return await self.repo.get(tenant_id, key)

    async def _mark_completed(
        self, record: IdempotencyRecord, ctx: GuardContext
    ) -> None:
        """After user code succeeded — หลัง user code สำเร็จ"""
        status = getattr(ctx, "_status", 200)
        body = getattr(ctx, "_body", {})
        headers = getattr(ctx, "_headers", {})
        completed = await self.repo.complete(
            record.tenant_id, record.key, status, body, headers
        )
        await self._cache_set(record.tenant_id, completed)
        await self._publish("IdempotencyCompleted", completed)

    async def _mark_failed(
        self, record: IdempotencyRecord, exc: Exception
    ) -> None:
        """After user code raised — หลัง user code raise"""
        code = type(exc).__name__
        message = str(exc)[:500]
        try:
            failed = await self.repo.fail(
                record.tenant_id, record.key, code, message
            )
            await self._cache_set(record.tenant_id, failed)
            await self._publish("IdempotencyFailed", failed)
        except Exception as e:
            logger.opt(exception=e).error("Failed to mark FAILED (swallowed)")

    async def _cache_get(
        self, tenant_id: str, key: IdempotencyKey
    ) -> dict | None:
        if self.cache is None:
            return None
        try:
            return await self.cache.get(tenant_id, key)
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed (idem)")
            return None

    async def _cache_set(
        self, tenant_id: str, record: IdempotencyRecord
    ) -> None:
        if self.cache is None:
            return
        try:
            await self.cache.set(
                tenant_id,
                record.key,
                IdempotencyMapper.to_cache_dict(record),
                record.remaining_ttl_seconds() or record.ttl.seconds,
            )
        except Exception as e:
            logger.opt(exception=e).error("Cache set failed (idem)")

    async def _cache_invalidate(
        self, tenant_id: str, key: IdempotencyKey
    ) -> None:
        if self.cache is None:
            return
        try:
            await self.cache.invalidate(tenant_id, key)
        except Exception as e:
            logger.opt(exception=e).error("Cache invalidate failed (idem)")

    async def _publish(self, event_name: str, record: IdempotencyRecord) -> None:
        if self.event_bus is None:
            return
        try:
            await self.event_bus.publish(
                event_name, IdempotencyMapper.to_event_payload(record)
            )
        except Exception as e:
            logger.opt(exception=e).error("Publish failed (idem)")


# ─────────────────────────────────────────────────────────────
# Adapter so from_model works with dict from cache
# ─────────────────────────────────────────────────────────────
class _DictModel:
    """Lightweight attr wrapper for dict → mapper — wrapper สำหรับ mapper."""

    def __init__(self, data: dict) -> None:
        self.id = data.get("id") or ""
        self.tenant_id = data.get("tenant_id") or ""
        self.key = data.get("key") or ""
        self.fingerprint = data.get("fingerprint") or ""
        self.status = data.get("status") or "PENDING"
        self.response_status = data.get("response_status")
        self.response_body = data.get("response_body")
        self.response_headers = data.get("response_headers") or {}
        self.locked_at = None
        self.completed_at = None
        self.expires_at = None
        self.ttl_seconds = IdempotencyTTL.DEFAULT_SECONDS
        self.error_code = data.get("error_code")
        self.error_message = data.get("error_message")
```

---

## 📄 12. `app/modules/idempotency/infrastructure/__init__.py`

```python
"""Infrastructure layer — เลเยอร์โครงสร้างพื้นฐานของ idempotency."""
```

---

## 📄 13. `app/modules/idempotency/infrastructure/models.py`

```python
"""SQLAlchemy models for idempotency — โมเดล SQLAlchemy."""
from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.modules.shared.infrastructure.models import BaseModel


class IdempotencyRecordModel(BaseModel):
    """Idempotency record — บันทึก idempotency (unique per tenant+key)."""

    __tablename__ = "idempotency_records"

    tenant_id = Column(String(63), nullable=False, index=True)
    key = Column(String(128), nullable=False)
    fingerprint = Column(String(64), nullable=False)

    status = Column(String(16), nullable=False, default="PENDING", index=True)

    response_status = Column(Integer, nullable=True)
    response_body = Column(JSONB, nullable=True)
    response_headers = Column(JSONB, nullable=False, default=dict)

    locked_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ttl_seconds = Column(Integer, nullable=False, default=86400)

    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_idem_tenant_key"),
        Index("ix_idem_tenant_status", "tenant_id", "status"),
        Index("ix_idem_expires_at", "expires_at"),
    )
```

---

## 📄 14. `app/modules/idempotency/infrastructure/repositories.py`

```python
"""Repositories for idempotency — รีโพซิทอรีของโมดูล idempotency."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from loguru import logger

from app.modules.idempotency.application.exceptions import (
    IdempotencyRecordNotFoundError,
    IdempotencyStoreError,
)
from app.modules.idempotency.application.mappers import IdempotencyMapper
from app.modules.idempotency.domain.entities import IdempotencyRecord
from app.modules.idempotency.domain.enums import IdempotencyStatus
from app.modules.idempotency.domain.value_objects import IdempotencyKey
from app.modules.idempotency.infrastructure.models import IdempotencyRecordModel
from app.modules.shared.domain.errors import StandardException


class PostgresIdempotencyRepository:
    """Postgres idempotency repository — รีโพซิทอรี idempotency."""

    def __init__(self, session) -> None:
        self.session = session

    # ── Write ─────────────────────────────────────────────────
    async def insert_pending(
        self, record: IdempotencyRecord
    ) -> IdempotencyRecord:
        """Insert PENDING (fails on unique violation) — แทรก PENDING"""
        try:
            model = IdempotencyRecordModel(**IdempotencyMapper.to_model_dict(record))
            self.session.add(model)
            await self.session.flush()
            return IdempotencyMapper.from_model(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.insert_pending")
            raise IdempotencyStoreError()

    async def complete(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        response_status: int,
        response_body: dict,
        response_headers: dict,
    ) -> IdempotencyRecord:
        """Mark COMPLETED — เปลี่ยนเป็น COMPLETED"""
        try:
            stmt = (
                update(IdempotencyRecordModel)
                .where(
                    IdempotencyRecordModel.tenant_id == tenant_id,
                    IdempotencyRecordModel.key == key.value,
                    IdempotencyRecordModel.status == IdempotencyStatus.PENDING.value,
                )
                .values(
                    status=IdempotencyStatus.COMPLETED.value,
                    response_status=response_status,
                    response_body=response_body,
                    response_headers=response_headers,
                    completed_at=datetime.now(timezone.utc),
                )
                .returning(IdempotencyRecordModel)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise IdempotencyRecordNotFoundError(
                    f"Cannot complete — record not PENDING for key {key.value}"
                )
            await self.session.flush()
            return IdempotencyMapper.from_model(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.complete")
            raise IdempotencyStoreError()

    async def fail(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        error_code: str,
        error_message: str,
    ) -> IdempotencyRecord:
        """Mark FAILED — เปลี่ยนเป็น FAILED"""
        try:
            stmt = (
                update(IdempotencyRecordModel)
                .where(
                    IdempotencyRecordModel.tenant_id == tenant_id,
                    IdempotencyRecordModel.key == key.value,
                    IdempotencyRecordModel.status == IdempotencyStatus.PENDING.value,
                )
                .values(
                    status=IdempotencyStatus.FAILED.value,
                    error_code=error_code,
                    error_message=error_message,
                    completed_at=datetime.now(timezone.utc),
                )
                .returning(IdempotencyRecordModel)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise IdempotencyRecordNotFoundError(
                    f"Cannot fail — record not PENDING for key {key.value}"
                )
            await self.session.flush()
            return IdempotencyMapper.from_model(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.fail")
            raise IdempotencyStoreError()

    # ── Read ──────────────────────────────────────────────────
    async def get(
        self, tenant_id: str, key: IdempotencyKey
    ) -> IdempotencyRecord | None:
        try:
            stmt = select(IdempotencyRecordModel).where(
                IdempotencyRecordModel.tenant_id == tenant_id,
                IdempotencyRecordModel.key == key.value,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return IdempotencyMapper.from_model(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.get")
            raise IdempotencyStoreError()

    # ── Maintenance ───────────────────────────────────────────
    async def delete(self, tenant_id: str, key: IdempotencyKey) -> None:
        try:
            stmt = delete(IdempotencyRecordModel).where(
                IdempotencyRecordModel.tenant_id == tenant_id,
                IdempotencyRecordModel.key == key.value,
            )
            await self.session.execute(stmt)
            await self.session.flush()
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.delete")
            raise IdempotencyStoreError()

    async def purge_expired(self, tenant_id: str, limit: int = 1000) -> int:
        """Purge expired records — ล้าง record หมดอายุ"""
        try:
            now = datetime.now(timezone.utc)
            stmt = (
                delete(IdempotencyRecordModel)
                .where(
                    IdempotencyRecordModel.tenant_id == tenant_id,
                    IdempotencyRecordModel.expires_at < now,
                )
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount or 0
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in idem.purge_expired")
            raise IdempotencyStoreError()
```

---

## 📄 15. `app/modules/idempotency/infrastructure/caches.py`

```python
"""Caches for idempotency — แคชของโมดูล idempotency (never raises)."""
from __future__ import annotations

import json

from loguru import logger

from app.modules.idempotency.domain.value_objects import IdempotencyKey


class RedisIdempotencyCache:
    """Redis cache for idempotency records — แคช record (never raises)."""

    def __init__(self, redis, namespace: str = "idem") -> None:
        self.redis = redis
        self.namespace = namespace

    def _key(self, tenant_id: str, key: IdempotencyKey) -> str:
        return f"{self.namespace}:{tenant_id}:{key.value}"

    async def get(self, tenant_id: str, key: IdempotencyKey) -> dict | None:
        try:
            raw = await self.redis.get(self._key(tenant_id, key))
            if raw is None:
                return None
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)
        except Exception as e:
            logger.opt(exception=e).error("Idem cache get failed. Falling back.")
            return None

    async def set(
        self,
        tenant_id: str,
        key: IdempotencyKey,
        record: dict,
        ttl_seconds: int,
    ) -> None:
        try:
            await self.redis.setex(
                self._key(tenant_id, key),
                max(60, int(ttl_seconds)),
                json.dumps(record, default=str),
            )
        except Exception as e:
            logger.opt(exception=e).error("Idem cache set failed.")

    async def invalidate(self, tenant_id: str, key: IdempotencyKey) -> None:
        try:
            await self.redis.delete(self._key(tenant_id, key))
        except Exception as e:
            logger.opt(exception=e).error("Idem cache invalidate failed.")


class RedisIdempotencyLock:
    """Redis distributed lock — ล็อกแบบกระจาย (never raises on release)."""

    def __init__(self, redis, namespace: str = "idem_lock") -> None:
        self.redis = redis
        self.namespace = namespace

    def _key(self, tenant_id: str, key: IdempotencyKey) -> str:
        return f"{self.namespace}:{tenant_id}:{key.value}"

    async def acquire(
        self, tenant_id: str, key: IdempotencyKey, ttl_seconds: int
    ) -> bool:
        """SET NX with TTL — ล็อกแบบ atomic"""
        try:
            result = await self.redis.set(
                self._key(tenant_id, key),
                "1",
                nx=True,
                ex=max(60, int(ttl_seconds)),
            )
            return bool(result)
        except Exception as e:
            logger.opt(exception=e).error("Idem lock acquire failed.")
            # Fail-closed: ถ้าล็อกไม่ได้ ให้ถือว่ามี lock อยู่แล้ว
            return False

    async def release(self, tenant_id: str, key: IdempotencyKey) -> None:
        try:
            await self.redis.delete(self._key(tenant_id, key))
        except Exception as e:
            logger.opt(exception=e).error("Idem lock release failed.")

    async def is_locked(self, tenant_id: str, key: IdempotencyKey) -> bool:
        try:
            return bool(await self.redis.exists(self._key(tenant_id, key)))
        except Exception as e:
            logger.opt(exception=e).error("Idem lock is_locked failed.")
            return False
```

---

## 📄 16. `app/modules/idempotency/infrastructure/services.py`

```python
"""Services for idempotency — บริการของโมดูล idempotency.

Includes:
  - KafkaIdempotencyPublisher → publish lifecycle events
  - IdempotencyMiddleware      → FastAPI middleware สกัด key + fingerprint
"""
from __future__ import annotations

import json

from fastapi import Request
from loguru import logger

from app.modules.idempotency.domain.enums import FingerprintStrategy
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    RequestFingerprint,
)


class KafkaIdempotencyPublisher:
    """Kafka publisher — ผู้เผยแพร่ event (never blocks)."""

    def __init__(self, producer, topic: str = "idempotency.events") -> None:
        self.producer = producer
        self.topic = topic

    async def publish(self, event_name: str, payload: dict) -> None:
        try:
            message = json.dumps(
                {"event": event_name, "payload": payload}, default=str
            ).encode("utf-8")
            await self.producer.send_and_wait(self.topic, message)
        except Exception as e:
            logger.opt(exception=e).error("Kafka publish failed (idem)")


class IdempotencyExtractor:
    """Extract key + fingerprint from request — สกัด key/fingerprint."""

    HEADER = "Idempotency-Key"

    def __init__(
        self,
        strategy: FingerprintStrategy = FingerprintStrategy.METHOD_PATH_BODY,
        required_paths: tuple[str, ...] = (),
    ) -> None:
        self.strategy = strategy
        self.required_paths = required_paths

    def extract_key(self, request: Request) -> IdempotencyKey | None:
        raw = request.headers.get(self.HEADER)
        if not raw:
            return None
        try:
            return IdempotencyKey(raw)
        except Exception:
            return None

    def is_required(self, request: Request) -> bool:
        """Path-based required — path ที่บังคับ"""
        return any(request.url.path.startswith(p) for p in self.required_paths)

    async def compute_fingerprint(
        self, request: Request, body: dict | None = None
    ) -> RequestFingerprint:
        """Compute fingerprint from request — คำนวณ fingerprint"""
        if body is None:
            try:
                body = await request.json()
            except Exception:
                body = {}
        return RequestFingerprint.compute(
            method=request.method,
            path=request.url.path,
            body=body,
            query=dict(request.query_params),
            strategy=self.strategy,
        )
```

---

## 📄 17. `app/modules/idempotency/presentation/__init__.py`

```python
"""Presentation layer — เลเยอร์นำเสนอของ idempotency."""
```

---

## 📄 18. `app/modules/idempotency/presentation/schemas.py`

```python
"""Pydantic schemas for idempotency — สคีมาของโมดูล idempotency."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IdempotencyStatusSchema(BaseModel):
    """Status response — ผลลัพธ์สถานะ"""

    key: str
    status: str = Field(..., examples=["PENDING", "COMPLETED", "FAILED"])
    is_terminal: bool
    remaining_ttl_seconds: int


class IdempotencyRecordSchema(BaseModel):
    """Record response — ผลลัพธ์ record"""

    id: str
    tenant_id: str
    key: str
    fingerprint: str
    status: str
    response_status: int | None = None
    response_body: dict | None = None
    response_headers: dict = Field(default_factory=dict)
    locked_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class IdempotencyPurgeResponse(BaseModel):
    """Purge result — ผลลัพธ์การล้าง"""

    deleted: int
```

---

## 📄 19. `app/modules/idempotency/presentation/docs.py`

```python
"""OpenAPI docs for idempotency — เอกสาร OpenAPI."""

router_docs = {
    "tags": ["Idempotency"],
    "description": (
        "Idempotency module — exactly-once semantics for money/goods-path operations. "
        "โมดูล idempotency — รับประกันการทำงานครั้งเดียวสำหรับ money/goods path"
    ),
}

get_docs = {
    "summary": "Get record by key — ดู record ตาม key",
    "description": "Retrieve an idempotency record — ค้นหา record",
}

status_docs = {
    "summary": "Status of key — สถานะของ key",
    "description": "Lightweight status check — ตรวจสอบสถานะแบบเบา",
}

purge_docs = {
    "summary": "Purge expired records — ล้าง record หมดอายุ",
    "description": "Remove expired idempotency records — ลบ record ที่หมดอายุ",
}
```

---

## 📄 20. `app/modules/idempotency/presentation/dependencies.py`

```python
"""FastAPI dependencies for idempotency — dependencies ของโมดูล idempotency."""
from __future__ import annotations

from fastapi import Depends, Header, Request

from app.modules.idempotency.application.use_cases import IdempotencyUseCases
from app.modules.idempotency.domain.enums import FingerprintStrategy
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    RequestFingerprint,
)
from app.modules.idempotency.infrastructure.caches import (
    RedisIdempotencyCache,
    RedisIdempotencyLock,
)
from app.modules.idempotency.infrastructure.repositories import (
    PostgresIdempotencyRepository,
)
from app.modules.idempotency.infrastructure.services import (
    KafkaIdempotencyPublisher,
)


# ── Factories (override in app.py) ────────────────────────────
def get_idem_session():
    raise NotImplementedError("Override in app.py")


def get_idem_redis():
    raise NotImplementedError("Override in app.py")


def get_idem_producer():
    raise NotImplementedError("Override in app.py")


# ── Composed ──────────────────────────────────────────────────
def get_idem_repository(session=Depends(get_idem_session)) -> PostgresIdempotencyRepository:
    return PostgresIdempotencyRepository(session)


def get_idem_cache(redis=Depends(get_idem_redis)) -> RedisIdempotencyCache:
    return RedisIdempotencyCache(redis)


def get_idem_lock(redis=Depends(get_idem_redis)) -> RedisIdempotencyLock:
    return RedisIdempotencyLock(redis)


def get_idem_event_bus(producer=Depends(get_idem_producer)) -> KafkaIdempotencyPublisher:
    return KafkaIdempotencyPublisher(producer)


def get_idem_use_cases(
    repo: PostgresIdempotencyRepository = Depends(get_idem_repository),
    lock: RedisIdempotencyLock = Depends(get_idem_lock),
    cache: RedisIdempotencyCache = Depends(get_idem_cache),
    event_bus: KafkaIdempotencyPublisher = Depends(get_idem_event_bus),
) -> IdempotencyUseCases:
    return IdempotencyUseCases(
        repo=repo, lock=lock, cache=cache, event_bus=event_bus
    )


# ── Header dependency ─────────────────────────────────────────
async def extract_idempotency_key(
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> IdempotencyKey | None:
    """Extract Idempotency-Key header — สกัด header"""
    if not idempotency_key:
        return None
    return IdempotencyKey(idempotency_key)


async def extract_fingerprint(
    request: Request,
    strategy: FingerprintStrategy = FingerprintStrategy.METHOD_PATH_BODY,
) -> RequestFingerprint:
    """Compute fingerprint from request — คำนวณ fingerprint"""
    try:
        body = await request.json()
    except Exception:
        body = {}
    return RequestFingerprint.compute(
        method=request.method,
        path=request.url.path,
        body=body,
        query=dict(request.query_params),
        strategy=strategy,
    )
```

---

## 📄 21. `app/modules/idempotency/presentation/routers.py`

```python
"""FastAPI routers for idempotency — เราเตอร์ของโมดูล idempotency."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.modules.idempotency.application.exceptions import (
    DomainException,
    IdempotencyException,
    IdempotencyRecordNotFoundError,
)
from app.modules.idempotency.application.mappers import IdempotencyMapper
from app.modules.idempotency.application.use_cases import IdempotencyUseCases
from app.modules.idempotency.domain.value_objects import IdempotencyKey
from app.modules.idempotency.presentation import docs as d
from app.modules.idempotency.presentation.dependencies import get_idem_use_cases
from app.modules.idempotency.presentation.schemas import (
    IdempotencyPurgeResponse,
    IdempotencyRecordSchema,
    IdempotencyStatusSchema,
)
from app.modules.shared.domain.errors import DomainError, StandardException
from app.modules.tenant_context.presentation.dependencies import (
    require_current_context,
)

router = APIRouter(prefix="/api/v1/idempotency", tags=d.router_docs["tags"])


def _handle_error(e: Exception, ctx: str) -> None:
    if isinstance(e, StandardException):
        raise
    if isinstance(e, DomainError):
        raise DomainException(e)
    logger.opt(exception=e).error(f"Error in idempotency.{ctx}")
    raise IdempotencyException()


@router.get("/{key}/", response_model=IdempotencyRecordSchema, **d.get_docs)
async def get_record(
    key: str,
    tenant_ctx=Depends(require_current_context),
    use_cases: IdempotencyUseCases = Depends(get_idem_use_cases),
) -> IdempotencyRecordSchema:
    """Get record by key — ดู record"""
    try:
        record = await use_cases.get(tenant_ctx.tenant_id.value, IdempotencyKey(key))
        return IdempotencyRecordSchema(**IdempotencyMapper.to_schema_dict(record))
    except IdempotencyRecordNotFoundError:
        raise HTTPException(status_code=404, detail="Idempotency record not found")
    except Exception as e:
        _handle_error(e, "get_record")


@router.get("/{key}/status/", response_model=IdempotencyStatusSchema, **d.status_docs)
async def get_status(
    key: str,
    tenant_ctx=Depends(require_current_context),
    use_cases: IdempotencyUseCases = Depends(get_idem_use_cases),
) -> IdempotencyStatusSchema:
    """Status of key — สถานะ"""
    try:
        record = await use_cases.get(tenant_ctx.tenant_id.value, IdempotencyKey(key))
        return IdempotencyStatusSchema(**IdempotencyMapper.to_status_dict(record))
    except IdempotencyRecordNotFoundError:
        raise HTTPException(status_code=404, detail="Idempotency record not found")
    except Exception as e:
        _handle_error(e, "get_status")


@router.post("/purge/", response_model=IdempotencyPurgeResponse, **d.purge_docs)
async def purge_expired(
    limit: int = 1000,
    tenant_ctx=Depends(require_current_context),
    use_cases: IdempotencyUseCases = Depends(get_idem_use_cases),
) -> IdempotencyPurgeResponse:
    """Purge expired — ล้างหมดอายุ"""
    try:
        deleted = await use_cases.purge_expired(tenant_ctx.tenant_id.value, limit)
        return IdempotencyPurgeResponse(deleted=deleted)
    except Exception as e:
        _handle_error(e, "purge")
```

---

## 📄 22. `tests/unit/test_idempotency.py`

```python
"""Unit tests for idempotency — การทดสอบหน่วยของโมดูล idempotency."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.modules.idempotency.application.exceptions import (
    IdempotencyKeyReuseError,
    IdempotencyRecordNotFoundError,
    IdempotencyRequiredError,
)
from app.modules.idempotency.application.use_cases import IdempotencyUseCases
from app.modules.idempotency.domain.entities import IdempotencyRecord, IdempotencyScope
from app.modules.idempotency.domain.enums import (
    FingerprintStrategy,
    GuardOutcome,
    IdempotencyStatus,
)
from app.modules.idempotency.domain.value_objects import (
    IdempotencyKey,
    IdempotencyTTL,
    RequestFingerprint,
)
from app.modules.shared.domain.errors import DomainError


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def key():
    return IdempotencyKey("checkout-abc-123")


@pytest.fixture
def fp():
    return RequestFingerprint.compute("POST", "/orders", {"sku": "A", "qty": 1})


@pytest.fixture
def fp_other():
    return RequestFingerprint.compute("POST", "/orders", {"sku": "B", "qty": 1})


# ─────────────────────────────────────────────────────────────
# Fakes
# ─────────────────────────────────────────────────────────────
class FakeRepo:
    def __init__(self):
        self.items: dict[tuple[str, str], IdempotencyRecord] = {}

    async def insert_pending(self, record):
        k = (record.tenant_id, record.key.value)
        if k in self.items:
            raise RuntimeError("conflict")
        record.id = f"r-{len(self.items) + 1}"
        self.items[k] = record
        return record

    async def get(self, tenant_id, key):
        return self.items.get((tenant_id, key.value))

    async def complete(self, tenant_id, key, response_status, response_body, response_headers):
        rec = self.items[(tenant_id, key.value)]
        rec.complete(response_status, response_body, response_headers)
        return rec

    async def fail(self, tenant_id, key, error_code, error_message):
        rec = self.items[(tenant_id, key.value)]
        rec.fail(error_code, error_message)
        return rec

    async def delete(self, tenant_id, key):
        self.items.pop((tenant_id, key.value), None)

    async def purge_expired(self, tenant_id, limit=1000):
        now = datetime.now(timezone.utc)
        to_remove = [k for k, v in self.items.items() if v.is_expired(now)]
        for k in to_remove[:limit]:
            self.items.pop(k, None)
        return len(to_remove)


class FakeLock:
    def __init__(self):
        self.locks: set[tuple[str, str]] = set()

    async def acquire(self, tenant_id, key, ttl_seconds):
        k = (tenant_id, key.value)
        if k in self.locks:
            return False
        self.locks.add(k)
        return True

    async def release(self, tenant_id, key):
        self.locks.discard((tenant_id, key.value))

    async def is_locked(self, tenant_id, key):
        return (tenant_id, key.value) in self.locks


class FakeCache:
    def __init__(self):
        self.store: dict = {}

    async def get(self, tenant_id, key):
        return self.store.get((tenant_id, key.value))

    async def set(self, tenant_id, key, record, ttl_seconds):
        self.store[(tenant_id, key.value)] = record

    async def invalidate(self, tenant_id, key):
        self.store.pop((tenant_id, key.value), None)


def make_uc() -> IdempotencyUseCases:
    return IdempotencyUseCases(repo=FakeRepo(), lock=FakeLock(), cache=FakeCache())


# ─────────────────────────────────────────────────────────────
# IdempotencyKey
# ─────────────────────────────────────────────────────────────
def test_key_valid():
    k = IdempotencyKey("abc-123_456:xyz")
    assert str(k) == "abc-123_456:xyz"


def test_key_too_short():
    with pytest.raises(DomainError):
        IdempotencyKey("abc")


def test_key_invalid_chars():
    with pytest.raises(DomainError):
        IdempotencyKey("has space!!!")


def test_key_too_long():
    with pytest.raises(DomainError):
        IdempotencyKey("a" * 129)


# ─────────────────────────────────────────────────────────────
# RequestFingerprint
# ─────────────────────────────────────────────────────────────
def test_fingerprint_deterministic():
    f1 = RequestFingerprint.compute("POST", "/x", {"a": 1})
    f2 = RequestFingerprint.compute("POST", "/x", {"a": 1})
    assert f1.value == f2.value


def test_fingerprint_differs_on_body():
    f1 = RequestFingerprint.compute("POST", "/x", {"a": 1})
    f2 = RequestFingerprint.compute("POST", "/x", {"a": 2})
    assert f1.value != f2.value


def test_fingerprint_differs_on_path():
    f1 = RequestFingerprint.compute("POST", "/x", {"a": 1})
    f2 = RequestFingerprint.compute("POST", "/y", {"a": 1})
    assert f1.value != f2.value


def test_fingerprint_differs_on_method():
    f1 = RequestFingerprint.compute("POST", "/x", {"a": 1})
    f2 = RequestFingerprint.compute("PUT", "/x", {"a": 1})
    assert f1.value != f2.value


def test_fingerprint_body_only_strategy():
    f1 = RequestFingerprint.compute(
        "POST", "/x", {"a": 1}, strategy=FingerprintStrategy.BODY
    )
    f2 = RequestFingerprint.compute(
        "PUT", "/y", {"a": 1}, strategy=FingerprintStrategy.BODY
    )
    assert f1.value == f2.value  # body same


def test_fingerprint_invalid_format():
    with pytest.raises(DomainError):
        RequestFingerprint("not-hex")


# ─────────────────────────────────────────────────────────────
# IdempotencyTTL
# ─────────────────────────────────────────────────────────────
def test_ttl_default():
    assert IdempotencyTTL.default().seconds == 24 * 3600


def test_ttl_bounds():
    with pytest.raises(DomainError):
        IdempotencyTTL(60)  # < 1h
    with pytest.raises(DomainError):
        IdempotencyTTL(8 * 24 * 3600)  # > 7d


def test_ttl_ok():
    IdempotencyTTL(3600)
    IdempotencyTTL(7 * 24 * 3600)


# ─────────────────────────────────────────────────────────────
# IdempotencyRecord entity
# ─────────────────────────────────────────────────────────────
def test_record_valid(key, fp):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    assert r.is_pending
    assert not r.is_terminal


def test_record_requires_tenant(key, fp):
    with pytest.raises(DomainError):
        IdempotencyRecord(tenant_id="", key=key, fingerprint=fp)


def test_record_requires_key(fp):
    with pytest.raises(DomainError):
        IdempotencyRecord(tenant_id="acme", key=None, fingerprint=fp)


def test_record_complete(key, fp):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    r.complete(201, {"id": "o-1"})
    assert r.is_completed
    assert r.response_status == 201
    assert r.cached_response()["body"] == {"id": "o-1"}


def test_record_cannot_complete_twice(key, fp):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    r.complete(200, {})
    with pytest.raises(DomainError):
        r.complete(200, {})


def test_record_fail_requires_code(key, fp):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    with pytest.raises(DomainError):
        r.fail("", "msg")


def test_record_fail_ok(key, fp):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    r.fail("UPSTREAM_TIMEOUT", "gateway timed out")
    assert r.is_failed
    assert r.error_code == "UPSTREAM_TIMEOUT"


def test_record_fingerprint_matches(key, fp, fp_other):
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    assert r.fingerprint_matches(fp)
    assert not r.fingerprint_matches(fp_other)


# ─────────────────────────────────────────────────────────────
# IdempotencyScope
# ─────────────────────────────────────────────────────────────
def test_scope_add(key, fp):
    s = IdempotencyScope(tenant_id="acme", scope_key="checkout-1")
    s.add(IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp))
    assert len(s.records) == 1
    assert not s.all_completed


def test_scope_all_completed(key, fp):
    s = IdempotencyScope(tenant_id="acme", scope_key="checkout-1")
    r = IdempotencyRecord(tenant_id="acme", key=key, fingerprint=fp)
    r.complete(200, {})
    s.add(r)
    assert s.all_completed


def test_scope_rejects_other_tenant(key, fp):
    s = IdempotencyScope(tenant_id="acme", scope_key="x")
    with pytest.raises(DomainError):
        s.add(IdempotencyRecord(tenant_id="beta", key=key, fingerprint=fp))


# ─────────────────────────────────────────────────────────────
# UseCases — guard
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_guard_first_call_executes(key, fp):
    uc = make_uc()
    async with uc.guard("acme", key, fp, required=True) as g:
        assert g.should_execute
        g.record_response(201, {"id": "o-1"})
    # second call with same key + fp → CACHED
    async with uc.guard("acme", key, fp, required=True) as g2:
        assert g2.outcome == GuardOutcome.CACHED
        assert g2.cached_response["status"] == 201
        assert g2.cached_response["body"] == {"id": "o-1"}


@pytest.mark.asyncio
async def test_guard_rejects_key_reuse_different_fp(key, fp, fp_other):
    uc = make_uc()
    async with uc.guard("acme", key, fp, required=True) as g:
        g.record_response(200, {})
    with pytest.raises(IdempotencyKeyReuseError):
        async with uc.guard("acme", key, fp_other, required=True):
            pass


@pytest.mark.asyncio
async def test_guard_required_without_key(fp):
    uc = make_uc()
    with pytest.raises(IdempotencyRequiredError):
        async with uc.guard("acme", None, fp, required=True):
            pass


@pytest.mark.asyncio
async def test_guard_optional_without_key(fp):
    uc = make_uc()
    async with uc.guard("acme", None, fp, required=False) as g:
        assert g.should_execute


@pytest.mark.asyncio
async def test_guard_marks_failed_on_exception(key, fp):
    uc = make_uc()

    with pytest.raises(ValueError):
        async with uc.guard("acme", key, fp, required=True):
            raise ValueError("boom")

    # now record should be FAILED → next attempt with same fp should retry
    async with uc.guard("acme", key, fp, required=True) as g2:
        assert g2.should_execute  # FAILED → retry


@pytest.mark.asyncio
async def test_guard_in_flight_conflict(key, fp):
    uc = make_uc()
    # manually acquire lock to simulate concurrent
    await uc.lock.acquire("acme", key, 3600)
    async with uc.guard("acme", key, fp, required=True) as g:
        assert g.outcome == GuardOutcome.IN_FLIGHT


# ─────────────────────────────────────────────────────────────
# UseCases — explicit
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_begin_execute_then_complete(key, fp):
    uc = make_uc()
    outcome, _ = await uc.begin("acme", key, fp)
    assert outcome == GuardOutcome.EXECUTE

    await uc.complete("acme", key, 201, {"id": "o-1"})

    outcome2, record = await uc.begin("acme", key, fp)
    assert outcome2 == GuardOutcome.CACHED
    assert record.response_status == 201


@pytest.mark.asyncio
async def test_begin_reuse_different_fp(key, fp, fp_other):
    uc = make_uc()
    await uc.begin("acme", key, fp)
    await uc.complete("acme", key, 200, {})

    with pytest.raises(IdempotencyKeyReuseError):
        await uc.begin("acme", key, fp_other)


@pytest.mark.asyncio
async def test_get_not_found(key):
    uc = make_uc()
    with pytest.raises(IdempotencyRecordNotFoundError):
        await uc.get("acme", key)


@pytest.mark.asyncio
async def test_purge_expired(key, fp):
    uc = make_uc()
    await uc.begin("acme", key, fp)
    # fake expiry
    uc.repo.items[("acme", key.value)].expires_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    n = await uc.purge_expired("acme")
    assert n == 1


# ─────────────────────────────────────────────────────────────
# Property-style invariants
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_guard_is_exactly_once(fp):
    """Same key + fp → exactly one execution — ทำงานครั้งเดียว"""
    uc = make_uc()
    executions = 0
    for _ in range(5):
        async with uc.guard("acme", IdempotencyKey("checkout-loop"), fp, required=True) as g:
            if g.should_execute:
                executions += 1
                g.record_response(200, {"ok": True})
    assert executions == 1


@pytest.mark.asyncio
async def test_tenant_isolation(key, fp):
    """Same key across tenants → independent — แยกตาม tenant"""
    uc = make_uc()
    async with uc.guard("acme", key, fp, required=True) as g:
        g.record_response(200, {"tenant": "acme"})
    async with uc.guard("beta", key, fp, required=True) as g2:
        assert g2.should_execute  # different tenant → execute
        g2.record_response(200, {"tenant": "beta"})
```

---

## ✅ Checklist ตรวจสอบ

| ข้อ | สถานะ |
|---|---|
| Domain layer ไม่ import framework | ✅ |
| ใช้ `flush()` ไม่ใช่ `commit()` | ✅ |
| Cache never raises | ✅ |
| Error handling ถูก shape (3/2/never) | ✅ |
| Idempotency ครบ | ✅ (module นี้คือ idempotency เอง) |
| Audit log ครบ | ✅ (publish event ให้ audit subscribe ได้) |
| Read-back verification | ✅ (`get` หลัง `complete`) |
| Tests ครบ 3 ประเภท | ✅ (unit + property + async + exactly-once) |
| Comment 2 ภาษา | ✅ |
| พร้อมรัน | ✅ |

---

## 🚀 วิธีใช้ + ตัวอย่าง

### 1) Override dependencies ใน `app/app.py`

```python
from app.modules.idempotency.presentation import dependencies as idem_deps

app.dependency_overrides[idem_deps.get_idem_session] = lambda: session
app.dependency_overrides[idem_deps.get_idem_redis] = lambda: redis
app.dependency_overrides[idem_deps.get_idem_producer] = lambda: producer
```

### 2) ใช้ใน invoice use case (money path — required)

```python
@router.post("/invoices/")
async def create_invoice(
    payload: InvoiceCreate,
    request: Request,
    tenant_ctx=Depends(require_current_context),
    idem: IdempotencyUseCases = Depends(get_idem_use_cases),
    key: IdempotencyKey | None = Depends(extract_idempotency_key),
    fp: RequestFingerprint = Depends(extract_fingerprint),
):
    """Create invoice — exactly once — สร้างใบกำกับครั้งเดียว"""
    async with idem.guard(
        tenant_ctx.tenant_id.value, key, fp, required=True
    ) as g:
        if g.cached_response:
            return JSONResponse(**g.cached_response)

        invoice = await invoice_use_cases.create_invoice(payload)
        g.record_response(201, {"id": invoice.id, "total": str(invoice.total)})
        return {"id": invoice.id, "total": str(invoice.total)}
```

### 3) ใช้แบบ explicit (สำหรับ background job)

```python
outcome, record = await idem.begin("acme", key, fp)
if outcome == GuardOutcome.CACHED:
    return record.cached_response()
if outcome == GuardOutcome.IN_FLIGHT:
    raise HTTPException(409, "Already in progress")

try:
    result = await do_work()
    await idem.complete("acme", key, 200, result)
except Exception as e:
    await idem.fail("acme", key, type(e).__name__, str(e))
    raise
```

### 4) ตัวอย่าง request

```bash
# First call — executes
curl -X POST http://localhost:8000/api/v1/invoices/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: acme" \
  -H "Idempotency-Key: checkout-abc-123" \
  -d '{"customer_id":"c1","lines":[{"sku":"A","qty":1}]}'
# → 201 {"id":"inv-1","total":"107.00"}

# Retry (same key + same payload) → cached response
curl -X POST http://localhost:8000/api/v1/invoices/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: acme" \
  -H "Idempotency-Key: checkout-abc-123" \
  -d '{"customer_id":"c1","lines":[{"sku":"A","qty":1}]}'
# → 201 {"id":"inv-1","total":"107.00"}  (same, no new invoice)

# Same key + different payload → 422
curl -X POST http://localhost:8000/api/v1/invoices/ \
  -H "X-Tenant-Id: acme" \
  -H "Idempotency-Key: checkout-abc-123" \
  -d '{"customer_id":"c2","lines":[{"sku":"B","qty":5}]}'
# → 422 IdempotencyKeyReuseError
```

---

## 📌 สรุป Module 4: `idempotency`

- **22 ไฟล์** (domain 4 + application 6 + infrastructure 4 + presentation 5 + init 2 + tests 1)
- **Two-phase**: Redis lock (`SET NX`) → Postgres PENDING → Postgres COMPLETED/FAILED
- **Context manager**: `async with idem.guard(...) as g:` — ใช้งานสวย อ่านง่าย
- **State machine**: `PENDING → COMPLETED / FAILED / EXPIRED`
- **Fingerprint**: SHA-256 `(method ‖ path ‖ body ‖ query)` ตรวจจับ key reuse
- **Exactly-once**: test ยืนยัน 5 calls → 1 execution
- **Tenant isolation**: key scope ต่อ tenant
- **Cache-first**: Redis lookup ก่อน, Postgres fallback
- **TTL bounded**: 1h – 7d
- **Fail-closed**: lock error → ถือว่ามี lock อยู่ (safety over availability)
- **Dependencies:** `tenant_context` (context), `audit` (subscribe events ได้)

**ต่อไป Module 5: `config` ต่อหรือยังครับ?** 🚀