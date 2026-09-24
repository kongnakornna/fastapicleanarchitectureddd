# Full Code Update — PDPA Idempotency Support

Below is the complete, updated code integrating the `tenant_pdp.idempotency_keys` table (from your SQL dump) with the PDPA module. Files marked **NEW** are added; the rest are **UPDATED**.

---

## 1. `app/modules/pdpa/domain/enums.py` — **UPDATED**

```python
"""pdpa enums — Enum ของ PDPA"""
from __future__ import annotations
from enum import StrEnum


class ConsentStatus(StrEnum):
    """TH: สถานะความยินยอม | EN: Consent status"""
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class PurposeCategory(StrEnum):
    """TH: หมวดวัตถุประสงค์ | EN: Purpose category"""
    DATA_COLLECTION = "DATA_COLLECTION"
    DATA_DELETION = "DATA_DELETION"
    USER_ACCOUNT = "USER_ACCOUNT"
    USAGE_LOGS = "USAGE_LOGS"
    TRANSACTION_HISTORY = "TRANSACTION_HISTORY"


class DSARType(StrEnum):
    """TH: ประเภท DSAR | EN: DSAR type"""
    ACCESS = "ACCESS"
    ERASURE = "ERASURE"
    WITHDRAW_CONSENT = "WITHDRAW_CONSENT"


class DSARStatus(StrEnum):
    """TH: สถานะ DSAR | EN: DSAR status"""
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class PrivacyPolicyStatus(StrEnum):
    """TH: สถานะนโยบาย | EN: Privacy policy status"""
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class IdempotencyStatus(StrEnum):
    """TH: สถานะ idempotency key | EN: Idempotency status"""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

---

## 2. `app/modules/pdpa/domain/idempotency.py` — **NEW**

```python
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
```

---

## 3. `app/modules/pdpa/domain/__init__.py` — **UPDATED**

```python
"""pdpa domain layer"""
from .entities import ConsentLog, DSARRequest, PrivacyPolicy, CookieConsent
from .enums import (
    ConsentStatus, DSARStatus, DSARType,
    PrivacyPolicyStatus, PurposeCategory, IdempotencyStatus,
)
from .value_objects import (
    ConsentId, PurposeCode, DataSubjectId, Evidence, EncryptionKeyVersion,
)
from .events import (
    ConsentGranted, ConsentRevoked, DSARSubmitted, DSARCompleted,
    DataErasureRequested, PrivacyPolicyPublished,
)
from .exceptions import (
    PDPAError, ConsentRequiredError, InvalidConsentStateError,
    ConsentAlreadyGrantedError, DSARNotFoundError, DSARExpiredError,
    PrivacyPolicyNotFoundError, InvalidIdentityVerificationError,
)
from .idempotency import IdempotencyRecord, compute_request_hash

__all__ = [
    "ConsentLog", "DSARRequest", "PrivacyPolicy", "CookieConsent",
    "ConsentStatus", "DSARStatus", "DSARType", "PrivacyPolicyStatus",
    "PurposeCategory", "IdempotencyStatus",
    "ConsentId", "PurposeCode", "DataSubjectId", "Evidence",
    "EncryptionKeyVersion",
    "ConsentGranted", "ConsentRevoked", "DSARSubmitted", "DSARCompleted",
    "DataErasureRequested", "PrivacyPolicyPublished",
    "PDPAError", "ConsentRequiredError", "InvalidConsentStateError",
    "ConsentAlreadyGrantedError", "DSARNotFoundError", "DSARExpiredError",
    "PrivacyPolicyNotFoundError", "InvalidIdentityVerificationError",
    "IdempotencyRecord", "compute_request_hash",
]
```

---

## 4. `app/modules/pdpa/application/exceptions.py` — **UPDATED**

```python
"""pdpa application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    """TH: base | EN: base"""


class DuplicateConsentError(ApplicationError):
    """TH: consent ซ้ำ | EN: duplicate consent"""


class DSARNotFoundAppError(ApplicationError):
    """TH: ไม่พบ DSAR | EN: DSAR not found"""


class ConsentNotFoundAppError(ApplicationError):
    """TH: ไม่พบ consent | EN: consent not found"""


class PolicyNotFoundAppError(ApplicationError):
    """TH: ไม่พบ policy | EN: policy not found"""


class CookieConsentNotFoundAppError(ApplicationError):
    """TH: ไม่พบ cookie consent | EN: cookie consent not found"""


class VersionConflictError(ApplicationError):
    """TH: version ไม่ตรง | EN: version conflict"""


class IdentityVerificationRequiredError(ApplicationError):
    """TH: ต้องยืนยันตัวตน | EN: identity verification required"""


class IdempotencyConflictError(ApplicationError):
    """TH: คำขอเดียวกันกำลังประมวลผล | EN: same key in progress"""


class IdempotencyMismatchError(ApplicationError):
    """TH: payload ไม่ตรงกับ key เดิม | EN: payload mismatch for key"""
```

---

## 5. `app/modules/pdpa/application/interfaces.py` — **UPDATED**

```python
"""pdpa application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Protocol

from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import PurposeCategory


class RequestContext(Protocol):
    """TH: request context | EN: request context"""
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> uuid.UUID | None: ...


class ConsentRepository(ABC):
    """TH: consent repo port | EN: consent repo port"""

    @abstractmethod
    async def save(self, ctx: RequestContext, log: ConsentLog) -> ConsentLog: ...
    @abstractmethod
    async def update(self, ctx: RequestContext, log: ConsentLog) -> ConsentLog: ...
    @abstractmethod
    async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> ConsentLog | None: ...
    @abstractmethod
    async def find_by_user_id(self, ctx: RequestContext, user_id: uuid.UUID) -> list[ConsentLog]: ...
    @abstractmethod
    async def find_active_by_user_and_purpose(
        self, ctx: RequestContext, user_id: uuid.UUID, purpose: PurposeCategory
    ) -> ConsentLog | None: ...
    @abstractmethod
    async def find_latest_by_user_and_purpose(
        self, ctx: RequestContext, user_id: uuid.UUID, purpose: PurposeCategory
    ) -> ConsentLog | None: ...
    @abstractmethod
    async def find_ready_for_auto_deletion(
        self, ctx: RequestContext, before: datetime, limit: int = 100
    ) -> list[ConsentLog]: ...
    @abstractmethod
    async def delete_by_user_id(self, ctx: RequestContext, user_id: uuid.UUID) -> None: ...
    @abstractmethod
    async def delete_by_id(self, ctx: RequestContext, id: uuid.UUID) -> None: ...
    @abstractmethod
    async def is_consent_active(
        self, ctx: RequestContext, user_id: uuid.UUID, purpose: PurposeCategory
    ) -> bool: ...
    @abstractmethod
    async def count_active_by_purpose(
        self, ctx: RequestContext, start: datetime, end: datetime
    ) -> dict[PurposeCategory, int]: ...


class DSARRepository(ABC):
    """TH: DSAR repo port | EN: DSAR repo port"""

    @abstractmethod
    async def save(self, ctx: RequestContext, dsar: DSARRequest) -> DSARRequest: ...
    @abstractmethod
    async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> DSARRequest | None: ...
    @abstractmethod
    async def find_by_user_id(self, ctx: RequestContext, user_id: uuid.UUID) -> list[DSARRequest]: ...
    @abstractmethod
    async def list_paginated(self, ctx: RequestContext, offset: int = 0, limit: int = 100) -> list[DSARRequest]: ...
    @abstractmethod
    async def find_overdue(self, ctx: RequestContext, now: datetime, limit: int = 100) -> list[DSARRequest]: ...


class PrivacyPolicyRepository(ABC):
    """TH: privacy policy port | EN: privacy policy port"""

    @abstractmethod
    async def save(self, ctx: RequestContext, policy: PrivacyPolicy) -> PrivacyPolicy: ...
    @abstractmethod
    async def find_current(self, ctx: RequestContext) -> PrivacyPolicy | None: ...
    @abstractmethod
    async def find_by_version(self, ctx: RequestContext, version: int) -> PrivacyPolicy | None: ...
    @abstractmethod
    async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> PrivacyPolicy | None: ...


class CookieConsentRepository(ABC):
    """TH: cookie consent port | EN: cookie consent port"""

    @abstractmethod
    async def save(self, ctx: RequestContext, consent: CookieConsent) -> CookieConsent: ...
    @abstractmethod
    async def update(self, ctx: RequestContext, consent: CookieConsent) -> CookieConsent: ...
    @abstractmethod
    async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> CookieConsent | None: ...
    @abstractmethod
    async def find_by_session(self, ctx: RequestContext, session_id: str) -> CookieConsent | None: ...


class InventoryCache(ABC):
    """TH: cache port | EN: cache port"""

    @abstractmethod
    async def get(self, key: str) -> Any | None: ...
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool: ...
    @abstractmethod
    async def invalidate(self, key: str) -> bool: ...


class EventBus(ABC):
    """TH: event bus port | EN: event bus port"""

    @abstractmethod
    async def publish(self, event: object) -> None: ...


class EmailService(ABC):
    """TH: email service | EN: email service"""

    @abstractmethod
    async def send_consent_notification(self, to: str, subject: str, body: str) -> bool: ...
    @abstractmethod
    async def send_dsar_notification(self, to: str, dsar_id: uuid.UUID, status: str) -> bool: ...


class LLMService(ABC):
    """TH: LLM service | EN: LLM service"""

    @abstractmethod
    async def analyze_usage_history(self, anonymized_data: dict[str, Any]) -> dict[str, Any]: ...


class IdempotencyStore(ABC):
    """
    TH: idempotency port — ป้องกันคำขอซ้ำ
    EN: idempotency port — prevents duplicate side effects

    Semantics:
      * check_or_lock: คืน response_body เดิมถ้า key นี้ COMPLETED แล้ว,
        มิฉะนั้นจอง key ไว้และคืน None.
      * complete: บันทึก response ที่สำเร็จ
      * fail:     ปล่อย key ให้ retry ได้
    """

    @abstractmethod
    async def check_or_lock(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        method: str,
        path: str,
        payload: dict[str, Any],
        ttl_hours: int = 24,
    ) -> dict[str, Any] | None: ...

    @abstractmethod
    async def complete(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        response_status: int,
        response_body: dict[str, Any],
    ) -> None: ...

    @abstractmethod
    async def fail(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
    ) -> None: ...


class DataExporter(ABC):
    """TH: data exporter port (JSON/PDF) | EN: data exporter port"""

    @abstractmethod
    async def export_json(self, ctx: RequestContext, user_id: uuid.UUID) -> dict[str, Any]: ...
    @abstractmethod
    async def export_pdf(self, ctx: RequestContext, user_id: uuid.UUID) -> bytes: ...


class PIIAnonymizer(ABC):
    """TH: PII anonymizer port | EN: PII anonymizer port"""

    @abstractmethod
    async def anonymize_user(self, ctx: RequestContext, user_id: uuid.UUID) -> None: ...
```

---

## 6. `app/modules/pdpa/application/mappers.py` — **UPDATED**

```python
"""pdpa mappers — ORM ↔ domain"""
from __future__ import annotations
from typing import Any

from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import (
    ConsentStatus, DSARStatus, DSARType,
    IdempotencyStatus, PrivacyPolicyStatus, PurposeCategory,
)
from app.modules.pdpa.domain.idempotency import IdempotencyRecord
from app.modules.pdpa.domain.value_objects import Evidence


def consent_to_entity(row: Any) -> ConsentLog:
    """TH: ORM → ConsentLog | EN: ORM → ConsentLog"""
    ev = row.evidence or {}
    return ConsentLog(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        purpose_code=PurposeCategory(row.purpose_code),
        status=ConsentStatus(row.status),
        granted_at=row.granted_at, revoked_at=row.revoked_at,
        expires_at=row.expires_at,
        evidence=Evidence(
            ip_address=ev.get("ip_address", "0.0.0.0"),
            user_agent=ev.get("user_agent", ""),
            occurred_at=row.granted_at,
        ),
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def dsar_to_entity(row: Any) -> DSARRequest:
    """TH: ORM → DSARRequest | EN: ORM → DSARRequest"""
    return DSARRequest(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        type=DSARType(row.type), status=DSARStatus(row.status),
        reason=row.reason, rejection_reason=row.rejection_reason,
        response_payload=dict(row.response_payload or {}),
        submitted_at=row.submitted_at, verified_at=row.verified_at,
        completed_at=row.completed_at, deadline_at=row.deadline_at,
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def policy_to_entity(row: Any) -> PrivacyPolicy:
    """TH: ORM → PrivacyPolicy | EN: ORM → PrivacyPolicy"""
    return PrivacyPolicy(
        id=row.id, tenant_id=row.tenant_id, version=row.version,
        content_th=row.content_th, content_en=row.content_en,
        status=PrivacyPolicyStatus(row.status),
        effective_from=row.effective_from,
        published_at=row.published_at, superseded_at=row.superseded_at,
        created_at=row.created_at, updated_at=row.updated_at,
    )


def cookie_to_entity(row: Any) -> CookieConsent:
    """TH: ORM → CookieConsent | EN: ORM → CookieConsent"""
    return CookieConsent(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        session_id=row.session_id, necessary=row.necessary,
        analytics=row.analytics, marketing=row.marketing,
        functional=row.functional,
        ip_address=str(row.ip_address) if row.ip_address else None,
        user_agent=row.user_agent,
        accepted_at=row.accepted_at, withdrawn_at=row.withdrawn_at,
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def idempotency_to_entity(row: Any) -> IdempotencyRecord:
    """TH: ORM → IdempotencyRecord | EN: ORM → IdempotencyRecord"""
    return IdempotencyRecord(
        id=row.id,
        tenant_id=row.tenant_id,
        user_id=row.user_id,
        idempotency_key=row.idempotency_key,
        request_method=row.request_method,
        request_path=row.request_path,
        request_hash=(row.request_hash or "").strip(),
        status=IdempotencyStatus(row.status),
        response_status=row.response_status,
        response_body=dict(row.response_body) if row.response_body else None,
        created_at=row.created_at,
        updated_at=row.updated_at,
        expires_at=row.expires_at,
    )
```

---

## 7. `app/modules/pdpa/application/utils.py` — **UPDATED**

```python
"""pdpa application utils"""
from __future__ import annotations
from datetime import UTC, datetime, timedelta
from typing import Any


def anonymize_pii(data: dict[str, Any]) -> dict[str, Any]:
    """TH: ปิดบัง PII ก่อนส่ง LLM | EN: Anonymize PII before LLM"""
    MASK_FIELDS = {
        "email", "phone", "national_id", "full_name",
        "address", "ip_address", "user_agent",
    }
    return {
        k: ("***" if k in MASK_FIELDS else v)
        for k, v in data.items()
    }


def dsar_sla_deadline(days: int = 30) -> datetime:
    """TH: deadline มาตรฐาน | EN: standard deadline"""
    return datetime.now(UTC) + timedelta(days=days)


def scoped_idempotency_scope(scope: str, method: str, path: str) -> str:
    """TH: สร้าง scope key ให้เหมาะกับ log | EN: compose a scope string"""
    return f"{scope}:{method.upper()}:{path}"
```

---

## 8. `app/modules/pdpa/application/use_cases.py` — **UPDATED**

```python
"""pdpa use cases — 8 use cases ตามสเปค + idempotency"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.logging import logger

from app.modules.pdpa.application.exceptions import (
    CookieConsentNotFoundAppError, ConsentNotFoundAppError,
    DuplicateConsentError, DSARNotFoundAppError,
    IdempotencyConflictError, IdentityVerificationRequiredError,
    PolicyNotFoundAppError,
)
from app.modules.pdpa.application.interfaces import (
    ConsentRepository, CookieConsentRepository, DataExporter,
    DSARRepository, EmailService, EventBus, IdempotencyStore,
    LLMService, PIIAnonymizer, PrivacyPolicyRepository, RequestContext,
)
from app.modules.pdpa.application.utils import anonymize_pii
from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import DSARType, PurposeCategory
from app.modules.pdpa.domain.events import (
    ConsentGranted, ConsentRevoked, DSARCompleted, DSARSubmitted,
    DataErasureRequested, PrivacyPolicyPublished,
)
from app.modules.pdpa.domain.exceptions import PDPAError
from app.modules.pdpa.domain.value_objects import Evidence


# ═══════════════════════════════════════════════════════════════
# 1. RecordConsentUseCase
# ═══════════════════════════════════════════════════════════════
class RecordConsentUseCase:
    """TH: บันทึกความยินยอม (idempotent) | EN: Record consent (idempotent)"""

    SCOPE = "record_consent"

    def __init__(
        self, *, repo: ConsentRepository, bus: EventBus,
        idem: IdempotencyStore, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._bus = bus
        self._idem = idem; self._ctx = ctx

    async def execute(
        self, *, user_id: uuid.UUID, purpose_code: PurposeCategory,
        ip_address: str, user_agent: str,
        expires_at: datetime | None = None,
        idempotency_key: str,
        request_method: str = "POST",
        request_path: str = "/pdpa/consent/",
    ) -> ConsentLog:
        logger.info("usecase.record_consent.start", purpose=purpose_code.value)

        request_payload = {
            "user_id": str(user_id),
            "purpose": purpose_code.value,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": expires_at.isoformat() if expires_at else None,
        }

        # ── 1. Idempotency check / lock ────────────────────────────
        cached = await self._idem.check_or_lock(
            self._ctx, idempotency_key, self.SCOPE,
            request_method, request_path, request_payload,
        )
        if cached is not None:
            entity_id = uuid.UUID(str(cached["id"]))
            existing = await self._repo.find_by_id(self._ctx, entity_id)
            if existing is None:
                raise IdempotencyConflictError(
                    f"idempotent record references missing consent {entity_id}"
                )
            logger.info("usecase.record_consent.replayed", id=str(entity_id))
            return existing

        # ── 2. Domain logic ────────────────────────────────────────
        try:
            active = await self._repo.find_active_by_user_and_purpose(
                self._ctx, user_id, purpose_code,
            )
            if active is not None:
                raise DuplicateConsentError(
                    f"consent already granted for {purpose_code.value}"
                )

            evidence = Evidence(
                ip_address=ip_address, user_agent=user_agent,
                occurred_at=datetime.now(UTC),
            )
            consent = ConsentLog.grant(
                tenant_id=self._ctx.tenant_id, user_id=user_id,
                purpose_code=purpose_code, evidence=evidence,
                expires_at=expires_at,
            )
            saved = await self._repo.save(self._ctx, consent)
            verified = await self._repo.find_by_id(self._ctx, saved.id)
            if verified is None:
                raise RuntimeError("read-back verify failed")

            verified._events.append(  # noqa: SLF001
                ConsentGranted(
                    consent_id=verified.id, tenant_id=verified.tenant_id,
                    user_id=verified.user_id,
                    purpose_code=verified.purpose_code.value,
                )
            )
            for evt in verified.pull_events():
                await self._bus.publish(evt)

            # ── 3. Persist idempotent result ──────────────────────
            await self._idem.complete(
                self._ctx, idempotency_key, self.SCOPE,
                response_status=201,
                response_body={"id": str(verified.id)},
            )
            return verified

        except (DuplicateConsentError, PDPAError):
            # Domain error — release the key so the client can retry
            await self._idem.fail(self._ctx, idempotency_key, self.SCOPE)
            logger.warning("usecase.record_consent.domain_error")
            raise
        except Exception:
            await self._idem.fail(self._ctx, idempotency_key, self.SCOPE)
            logger.exception("usecase.record_consent.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 2. RevokeConsentUseCase
# ═══════════════════════════════════════════════════════════════
class RevokeConsentUseCase:
    """TH: ถอนความยินยอม | EN: Revoke consent"""

    def __init__(
        self, *, repo: ConsentRepository, bus: EventBus, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._bus = bus; self._ctx = ctx

    async def execute(
        self, *, consent_id: uuid.UUID, reason: str = "user_withdrawal",
    ) -> ConsentLog:
        logger.info("usecase.revoke_consent.start", id=str(consent_id))
        try:
            consent = await self._repo.find_by_id(self._ctx, consent_id)
            if consent is None:
                raise ConsentNotFoundAppError(f"consent {consent_id} not found")
            consent.revoke(reason=reason)
            saved = await self._repo.update(self._ctx, consent)
            await self._bus.publish(
                ConsentRevoked(
                    consent_id=saved.id, tenant_id=saved.tenant_id,
                    user_id=saved.user_id,
                    purpose_code=saved.purpose_code.value, reason=reason,
                )
            )
            return saved
        except PDPAError:
            raise
        except Exception:
            logger.exception("usecase.revoke_consent.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 3. SubmitDSARUseCase
# ═══════════════════════════════════════════════════════════════
class SubmitDSARUseCase:
    """TH: ยื่นคำร้อง DSAR (idempotent) | EN: Submit DSAR (idempotent)"""

    SCOPE = "submit_dsar"

    def __init__(
        self, *, repo: DSARRepository, bus: EventBus,
        email: EmailService, idem: IdempotencyStore, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._bus = bus
        self._email = email; self._idem = idem; self._ctx = ctx

    async def execute(
        self, *, user_id: uuid.UUID, type: DSARType,
        reason: str | None = None,
        idempotency_key: str,
        request_method: str = "POST",
        request_path: str = "/pdpa/dsar/",
    ) -> DSARRequest:
        logger.info("usecase.submit_dsar.start", type=type.value)

        request_payload = {
            "user_id": str(user_id),
            "type": type.value,
            "reason": reason or "",
        }

        cached = await self._idem.check_or_lock(
            self._ctx, idempotency_key, self.SCOPE,
            request_method, request_path, request_payload,
        )
        if cached is not None:
            entity_id = uuid.UUID(str(cached["id"]))
            existing = await self._repo.find_by_id(self._ctx, entity_id)
            if existing is None:
                raise IdempotencyConflictError(
                    f"idempotent record references missing DSAR {entity_id}"
                )
            logger.info("usecase.submit_dsar.replayed", id=str(entity_id))
            return existing

        try:
            dsar = DSARRequest.submit(
                tenant_id=self._ctx.tenant_id, user_id=user_id,
                type=type, reason=reason,
            )
            saved = await self._repo.save(self._ctx, dsar)
            await self._bus.publish(
                DSARSubmitted(
                    dsar_id=saved.id, tenant_id=saved.tenant_id,
                    user_id=saved.user_id, type=saved.type.value,
                )
            )
            if type == DSARType.ERASURE:
                await self._bus.publish(
                    DataErasureRequested(
                        dsar_id=saved.id, tenant_id=saved.tenant_id,
                        user_id=saved.user_id,
                    )
                )

            await self._idem.complete(
                self._ctx, idempotency_key, self.SCOPE,
                response_status=201,
                response_body={"id": str(saved.id)},
            )
            return saved

        except Exception:
            await self._idem.fail(self._ctx, idempotency_key, self.SCOPE)
            logger.exception("usecase.submit_dsar.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 4. ProcessDSARUseCase
# ═══════════════════════════════════════════════════════════════
class ProcessDSARUseCase:
    """TH: ประมวลผล DSAR | EN: Process DSAR"""

    def __init__(
        self, *, repo: DSARRepository, bus: EventBus,
        email: EmailService, llm: LLMService, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._bus = bus
        self._email = email; self._llm = llm; self._ctx = ctx

    async def execute(
        self, *, dsar_id: uuid.UUID,
        response_payload: dict[str, Any],
    ) -> DSARRequest:
        logger.info("usecase.process_dsar.start", id=str(dsar_id))
        try:
            dsar = await self._repo.find_by_id(self._ctx, dsar_id)
            if dsar is None:
                raise DSARNotFoundAppError(f"dsar {dsar_id} not found")
            if dsar.status.value == "SUBMITTED":
                raise IdentityVerificationRequiredError(
                    "DSAR must be verified before processing"
                )
            dsar.complete(response_payload=response_payload)
            saved = await self._repo.save(self._ctx, dsar)
            await self._bus.publish(
                DSARCompleted(
                    dsar_id=saved.id, tenant_id=saved.tenant_id,
                    user_id=saved.user_id,
                    response_payload=response_payload,
                )
            )
            return saved
        except Exception:
            logger.exception("usecase.process_dsar.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 5. ExportDataUseCase
# ═══════════════════════════════════════════════════════════════
class ExportDataUseCase:
    """TH: export ข้อมูลผู้ใช้ (JSON/PDF) | EN: Export user data"""

    def __init__(
        self, *, dsar_repo: DSARRepository, exporter: DataExporter,
        bus: EventBus, ctx: RequestContext,
    ) -> None:
        self._dsar_repo = dsar_repo; self._exporter = exporter
        self._bus = bus; self._ctx = ctx

    async def execute_json(
        self, *, dsar_id: uuid.UUID, user_id: uuid.UUID,
    ) -> dict[str, Any]:
        logger.info("usecase.export_data.json", dsar_id=str(dsar_id))
        try:
            dsar = await self._dsar_repo.find_by_id(self._ctx, dsar_id)
            if dsar is None:
                raise DSARNotFoundAppError(f"dsar {dsar_id} not found")
            return await self._exporter.export_json(self._ctx, user_id)
        except Exception:
            logger.exception("usecase.export_data.json.unexpected")
            raise

    async def execute_pdf(
        self, *, dsar_id: uuid.UUID, user_id: uuid.UUID,
    ) -> bytes:
        logger.info("usecase.export_data.pdf", dsar_id=str(dsar_id))
        try:
            dsar = await self._dsar_repo.find_by_id(self._ctx, dsar_id)
            if dsar is None:
                raise DSARNotFoundAppError(f"dsar {dsar_id} not found")
            return await self._exporter.export_pdf(self._ctx, user_id)
        except Exception:
            logger.exception("usecase.export_data.pdf.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 6. EraseDataUseCase
# ═══════════════════════════════════════════════════════════════
class EraseDataUseCase:
    """TH: ลบ/anonymize ข้อมูล | EN: Erase / anonymize data"""

    def __init__(
        self, *, consent_repo: ConsentRepository, dsar_repo: DSARRepository,
        anonymizer: PIIAnonymizer, bus: EventBus, ctx: RequestContext,
    ) -> None:
        self._consent_repo = consent_repo; self._dsar_repo = dsar_repo
        self._anonymizer = anonymizer; self._bus = bus; self._ctx = ctx

    async def execute(
        self, *, dsar_id: uuid.UUID, user_id: uuid.UUID,
    ) -> DSARRequest:
        logger.info("usecase.erase_data.start", dsar_id=str(dsar_id))
        try:
            dsar = await self._dsar_repo.find_by_id(self._ctx, dsar_id)
            if dsar is None:
                raise DSARNotFoundAppError(f"dsar {dsar_id} not found")
            if dsar.type != DSARType.ERASURE:
                raise PDPAError("dsar is not ERASURE type")

            await self._anonymizer.anonymize_user(self._ctx, user_id)

            dsar.complete(response_payload={"erased": True, "method": "anonymize"})
            saved = await self._dsar_repo.save(self._ctx, dsar)
            await self._bus.publish(
                DSARCompleted(
                    dsar_id=saved.id, tenant_id=saved.tenant_id,
                    user_id=saved.user_id,
                    response_payload={"erased": True},
                )
            )
            return saved
        except Exception:
            logger.exception("usecase.erase_data.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 7. PublishPrivacyPolicyUseCase / GetCurrentPolicyUseCase
# ═══════════════════════════════════════════════════════════════
class PublishPrivacyPolicyUseCase:
    """TH: publish นโยบาย | EN: Publish privacy policy"""

    def __init__(
        self, *, repo: PrivacyPolicyRepository, bus: EventBus,
        ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._bus = bus; self._ctx = ctx

    async def execute(
        self, *, version: int, content_th: str, content_en: str,
    ) -> PrivacyPolicy:
        logger.info("usecase.publish_policy.start", version=version)
        try:
            current = await self._repo.find_current(self._ctx)
            if current is not None and current.version >= version:
                raise PDPAError(
                    f"version {version} <= current {current.version}"
                )
            policy = PrivacyPolicy.create(
                tenant_id=self._ctx.tenant_id, version=version,
                content_th=content_th, content_en=content_en,
            )
            policy.publish()
            if current is not None:
                current.supersede()
                await self._repo.save(self._ctx, current)
            saved = await self._repo.save(self._ctx, policy)
            await self._bus.publish(
                PrivacyPolicyPublished(
                    policy_id=saved.id, tenant_id=saved.tenant_id,
                    version=saved.version,
                )
            )
            return saved
        except Exception:
            logger.exception("usecase.publish_policy.unexpected")
            raise


class GetCurrentPolicyUseCase:
    """TH: ดึงนโยบายปัจจุบัน | EN: Get current policy"""

    def __init__(
        self, *, repo: PrivacyPolicyRepository, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._ctx = ctx

    async def execute(self, *, version: int | None = None) -> PrivacyPolicy:
        logger.info("usecase.get_current_policy.start", version=version)
        try:
            if version is not None:
                policy = await self._repo.find_by_version(self._ctx, version)
            else:
                policy = await self._repo.find_current(self._ctx)
            if policy is None:
                raise PolicyNotFoundAppError("privacy policy not found")
            return policy
        except Exception:
            logger.exception("usecase.get_current_policy.unexpected")
            raise


# ═══════════════════════════════════════════════════════════════
# 8. RecordCookieConsentUseCase / UpdateCookieConsentUseCase
# ═══════════════════════════════════════════════════════════════
class RecordCookieConsentUseCase:
    """TH: บันทึก cookie consent | EN: Record cookie consent"""

    def __init__(
        self, *, repo: CookieConsentRepository, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._ctx = ctx

    async def execute(
        self, *, session_id: str, analytics: bool, marketing: bool,
        functional: bool, ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> CookieConsent:
        logger.info("usecase.record_cookie.start", session=session_id[:8])
        try:
            consent = CookieConsent.record(
                tenant_id=self._ctx.tenant_id, user_id=self._ctx.user_id,
                session_id=session_id, analytics=analytics,
                marketing=marketing, functional=functional,
                ip_address=ip_address, user_agent=user_agent,
            )
            return await self._repo.save(self._ctx, consent)
        except Exception:
            logger.exception("usecase.record_cookie.unexpected")
            raise


class UpdateCookieConsentUseCase:
    """TH: แก้ไข cookie consent | EN: Update cookie consent"""

    def __init__(
        self, *, repo: CookieConsentRepository, ctx: RequestContext,
    ) -> None:
        self._repo = repo; self._ctx = ctx

    async def execute(
        self, *, consent_id: uuid.UUID,
        analytics: bool | None = None,
        marketing: bool | None = None,
        functional: bool | None = None,
    ) -> CookieConsent:
        logger.info("usecase.update_cookie.start", id=str(consent_id))
        try:
            consent = await self._repo.find_by_id(self._ctx, consent_id)
            if consent is None:
                raise CookieConsentNotFoundAppError(
                    f"cookie consent {consent_id} not found"
                )
            consent.update_preferences(
                analytics=analytics, marketing=marketing, functional=functional,
            )
            return await self._repo.update(self._ctx, consent)
        except Exception:
            logger.exception("usecase.update_cookie.unexpected")
            raise
```

---

## 9. `app/modules/pdpa/infrastructure/models.py` — **UPDATED**

Add this model at the end (existing models unchanged):

```python
class IdempotencyKeyModel(Base):
    """TH: ตาราง idempotency_keys | EN: idempotency_keys table"""
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_idempotency_key"),
        CheckConstraint(
            "status IN ('IN_PROGRESS','COMPLETED','FAILED')",
            name="ck_idempotency_status",
        ),
        Index("ix_idempotency_keys_expires", "expires_at"),
        Index("ix_idempotency_keys_user", "user_id"),
        {"schema": "tenant_pdp"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_method: Mapped[str] = mapped_column(String(10), nullable=False)
    request_path: Mapped[str] = mapped_column(String(500), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="IN_PROGRESS",
    )
    response_status: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
```

---

## 10. `app/modules/pdpa/infrastructure/idempotency_store.py` — **NEW**

```python
"""pdpa idempotency store — SQLAlchemy-backed implementation"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.logging import logger
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pdpa.application.exceptions import (
    ApplicationError, IdempotencyConflictError, IdempotencyMismatchError,
)
from app.modules.pdpa.application.interfaces import (
    IdempotencyStore, RequestContext,
)
from app.modules.pdpa.application.mappers import idempotency_to_entity
from app.modules.pdpa.domain.enums import IdempotencyStatus
from app.modules.pdpa.domain.idempotency import (
    IdempotencyRecord, compute_request_hash,
)
from app.modules.pdpa.infrastructure.models import IdempotencyKeyModel


class IdempotencyStoreError(ApplicationError):
    """TH: idempotency ผิดพลาด | EN: idempotency failure"""


class SQLAlchemyIdempotencyStore(IdempotencyStore):
    """
    TH: เก็บ idempotency key ใน PostgreSQL (tenant_pdp.idempotency_keys)
    EN: Persists idempotency keys in PostgreSQL

    Semantics:
      * check_or_lock → INSERT ... ON CONFLICT DO NOTHING then re-SELECT
      * complete      → UPDATE ... WHERE status='IN_PROGRESS'
      * fail          → DELETE row so client can retry
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ───────────────────────────────────────────────────────────
    async def check_or_lock(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        method: str,
        path: str,
        payload: dict[str, Any],
        ttl_hours: int = 24,
    ) -> dict[str, Any] | None:
        request_hash = compute_request_hash(payload)
        try:
            # 1. Try to claim the key
            record = IdempotencyRecord.start(
                tenant_id=ctx.tenant_id,
                user_id=ctx.user_id,
                idempotency_key=key,
                request_method=method,
                request_path=path,
                request_hash=request_hash,
                ttl_hours=ttl_hours,
            )
            model = IdempotencyKeyModel(
                id=record.id,
                tenant_id=record.tenant_id,
                user_id=record.user_id,
                idempotency_key=record.idempotency_key,
                request_method=record.request_method,
                request_path=record.request_path,
                request_hash=record.request_hash,
                status=record.status.value,
                response_status=None,
                response_body=None,
                created_at=record.created_at,
                updated_at=record.updated_at,
                expires_at=record.expires_at,
            )
            self._session.add(model)
            try:
                await self._session.flush()
                # New row inserted → this is the first execution
                logger.info("idempotency.locked", key=key, scope=scope)
                return None
            except IntegrityError:
                await self._session.rollback()
                # fall through to read existing row

            # 2. Row already existed — read it
            existing = await self._load(ctx, key)
            if existing is None:
                # Lost the race and the other txn rolled back — retry once
                logger.warning("idempotency.race_retry", key=key)
                return await self.check_or_lock(
                    ctx, key, scope, method, path, payload, ttl_hours,
                )

            # 3. Expired → delete and retry
            if existing.is_expired():
                await self._delete(ctx, key)
                return await self.check_or_lock(
                    ctx, key, scope, method, path, payload, ttl_hours,
                )

            # 4. Payload mismatch
            if not existing.matches(request_hash):
                raise IdempotencyMismatchError(
                    f"idempotency_key {key} reused with different payload"
                )

            # 5. Status routing
            if existing.status == IdempotencyStatus.COMPLETED:
                logger.info("idempotency.replay", key=key, scope=scope)
                return existing.response_body or {}

            if existing.status == IdempotencyStatus.IN_PROGRESS:
                raise IdempotencyConflictError(
                    f"request with key {key} is already being processed"
                )

            # FAILED → treat as fresh
            await self._delete(ctx, key)
            return await self.check_or_lock(
                ctx, key, scope, method, path, payload, ttl_hours,
            )

        except ApplicationError:
            raise
        except Exception as e:
            logger.exception("idempotency.check_or_lock.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def complete(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        response_status: int,
        response_body: dict[str, Any],
    ) -> None:
        try:
            stmt = (
                update(IdempotencyKeyModel)
                .where(
                    IdempotencyKeyModel.tenant_id == ctx.tenant_id,
                    IdempotencyKeyModel.idempotency_key == key,
                )
                .values(
                    status=IdempotencyStatus.COMPLETED.value,
                    response_status=response_status,
                    response_body=response_body,
                    updated_at=datetime.now(UTC),
                )
            )
            await self._session.execute(stmt)
            await self._session.flush()
            logger.info("idempotency.completed", key=key, scope=scope)
        except Exception as e:
            logger.exception("idempotency.complete.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def fail(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
    ) -> None:
        try:
            await self._delete(ctx, key)
            logger.info("idempotency.failed", key=key, scope=scope)
        except Exception as e:
            logger.exception("idempotency.fail.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def _load(
        self, ctx: RequestContext, key: str,
    ) -> IdempotencyRecord | None:
        stmt = select(IdempotencyKeyModel).where(
            IdempotencyKeyModel.tenant_id == ctx.tenant_id,
            IdempotencyKeyModel.idempotency_key == key,
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return idempotency_to_entity(row) if row else None

    async def _delete(self, ctx: RequestContext, key: str) -> None:
        stmt = delete(IdempotencyKeyModel).where(
            IdempotencyKeyModel.tenant_id == ctx.tenant_id,
            IdempotencyKeyModel.idempotency_key == key,
        )
        await self._session.execute(stmt)
        await self._session.flush()
```

---

## 11. `app/modules/pdpa/infrastructure/__init__.py` — **UPDATED**

```python
"""pdpa infrastructure layer"""
from .idempotency_store import (
    IdempotencyStoreError, SQLAlchemyIdempotencyStore,
)

__all__ = ["IdempotencyStoreError", "SQLAlchemyIdempotencyStore"]
```

---

## 12. `app/modules/pdpa/presentation/dependencies.py` — **UPDATED**

```python
"""pdpa DI container"""
from __future__ import annotations
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import RequestContext, get_context
from app.core.db import get_session
from app.core.events import EventBus, get_event_bus
from app.modules.pdpa.application.interfaces import (
    DataExporter, EmailService, IdempotencyStore, LLMService, PIIAnonymizer,
)
from app.modules.pdpa.application.use_cases import (
    EraseDataUseCase, ExportDataUseCase, GetCurrentPolicyUseCase,
    ProcessDSARUseCase, PublishPrivacyPolicyUseCase,
    RecordConsentUseCase, RecordCookieConsentUseCase,
    RevokeConsentUseCase, SubmitDSARUseCase,
    UpdateCookieConsentUseCase,
)
from app.modules.pdpa.infrastructure.idempotency_store import (
    SQLAlchemyIdempotencyStore,
)
from app.modules.pdpa.infrastructure.repositories import (
    SQLAlchemyConsentRepository, SQLAlchemyCookieConsentRepository,
    SQLAlchemyDSARRepository, SQLAlchemyPrivacyPolicyRepository,
)
from app.modules.pdpa.infrastructure.services import (
    DefaultPIIAnonymizer, JsonPdfDataExporter,
    OpenAILLMService, SMTPEmailService,
)


def get_consent_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyConsentRepository:
    return SQLAlchemyConsentRepository(session=session)


def get_dsar_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyDSARRepository:
    return SQLAlchemyDSARRepository(session=session)


def get_pp_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyPrivacyPolicyRepository:
    return SQLAlchemyPrivacyPolicyRepository(session=session)


def get_cc_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyCookieConsentRepository:
    return SQLAlchemyCookieConsentRepository(session=session)


def get_email_service() -> EmailService:
    return SMTPEmailService(smtp_client=None, from_addr="noreply@example.com")


def get_llm_service() -> LLMService:
    return OpenAILLMService(client=None)


def get_exporter(
    consent_repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
) -> DataExporter:
    return JsonPdfDataExporter(repo=consent_repo)


def get_anonymizer() -> PIIAnonymizer:
    return DefaultPIIAnonymizer()


def get_idempotency_store(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IdempotencyStore:
    return SQLAlchemyIdempotencyStore(session=session)


# ─── Use case factories ──────────────────────────────────────────
async def get_record_consent_uc(
    repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RecordConsentUseCase:
    return RecordConsentUseCase(repo=repo, bus=bus, idem=idem, ctx=ctx)


async def get_revoke_consent_uc(
    repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RevokeConsentUseCase:
    return RevokeConsentUseCase(repo=repo, bus=bus, ctx=ctx)


async def get_submit_dsar_uc(
    repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    email: Annotated[EmailService, Depends(get_email_service)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> SubmitDSARUseCase:
    return SubmitDSARUseCase(
        repo=repo, bus=bus, email=email, idem=idem, ctx=ctx,
    )


async def get_process_dsar_uc(
    repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    email: Annotated[EmailService, Depends(get_email_service)],
    llm: Annotated[LLMService, Depends(get_llm_service)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> ProcessDSARUseCase:
    return ProcessDSARUseCase(
        repo=repo, bus=bus, email=email, llm=llm, ctx=ctx,
    )


async def get_export_data_uc(
    dsar_repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    exporter: Annotated[DataExporter, Depends(get_exporter)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> ExportDataUseCase:
    return ExportDataUseCase(
        dsar_repo=dsar_repo, exporter=exporter, bus=bus, ctx=ctx,
    )


async def get_erase_data_uc(
    consent_repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    dsar_repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    anonymizer: Annotated[PIIAnonymizer, Depends(get_anonymizer)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> EraseDataUseCase:
    return EraseDataUseCase(
        consent_repo=consent_repo, dsar_repo=dsar_repo,
        anonymizer=anonymizer, bus=bus, ctx=ctx,
    )


async def get_publish_pp_uc(
    repo: Annotated[SQLAlchemyPrivacyPolicyRepository, Depends(get_pp_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> PublishPrivacyPolicyUseCase:
    return PublishPrivacyPolicyUseCase(repo=repo, bus=bus, ctx=ctx)


async def get_current_pp_uc(
    repo: Annotated[SQLAlchemyPrivacyPolicyRepository, Depends(get_pp_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> GetCurrentPolicyUseCase:
    return GetCurrentPolicyUseCase(repo=repo, ctx=ctx)


async def get_record_cookie_uc(
    repo: Annotated[SQLAlchemyCookieConsentRepository, Depends(get_cc_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RecordCookieConsentUseCase:
    return RecordCookieConsentUseCase(repo=repo, ctx=ctx)


async def get_update_cookie_uc(
    repo: Annotated[SQLAlchemyCookieConsentRepository, Depends(get_cc_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> UpdateCookieConsentUseCase:
    return UpdateCookieConsentUseCase(repo=repo, ctx=ctx)
```

---

## 13. `app/modules/pdpa/presentation/routers.py` — **UPDATED**

```python
"""pdpa HTTP routers — 4 groups ตามสเปค §4"""
from __future__ import annotations
import uuid
from typing import Annotated

from app.core.logging import logger
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.modules.pdpa.application.exceptions import (
    ConsentNotFoundAppError, CookieConsentNotFoundAppError,
    DSARNotFoundAppError, DuplicateConsentError,
    IdempotencyConflictError, IdempotencyMismatchError,
    IdentityVerificationRequiredError, PolicyNotFoundAppError,
)
from app.modules.pdpa.application.use_cases import (
    EraseDataUseCase, ExportDataUseCase, GetCurrentPolicyUseCase,
    ProcessDSARUseCase, PublishPrivacyPolicyUseCase,
    RecordConsentUseCase, RecordCookieConsentUseCase,
    RevokeConsentUseCase, SubmitDSARUseCase,
    UpdateCookieConsentUseCase,
)
from app.modules.pdpa.domain.exceptions import PDPAError
from app.modules.pdpa.presentation.dependencies import (
    get_current_pp_uc, get_erase_data_uc, get_export_data_uc,
    get_process_dsar_uc, get_publish_pp_uc,
    get_record_consent_uc, get_record_cookie_uc,
    get_revoke_consent_uc, get_submit_dsar_uc,
    get_update_cookie_uc,
)
from app.modules.pdpa.presentation.docs import (
    RESPONSE_CREATE_201, RESPONSE_ERROR_400,
    RESPONSE_ERROR_404, RESPONSE_ERROR_409, RESPONSE_ERROR_422,
)
from app.modules.pdpa.presentation.schemas import (
    ConsentCreateRequest, ConsentResponse, ConsentRevokeRequest,
    CookieConsentRequest, CookieConsentResponse, CookieConsentUpdateRequest,
    DSARCreateRequest, DSARProcessRequest, DSARResponse,
    PrivacyPolicyCreateRequest, PrivacyPolicyResponse,
)

router = APIRouter(prefix="/pdpa", tags=["PDPA"])

IdemKey = Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=255)]


# ═══════════════════════════════════════════════════════════════
# Consent
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/consent/",
    status_code=status.HTTP_201_CREATED,
    summary="บันทึกความยินยอม",
    operation_id="record_consent",
    response_model=ConsentResponse,
    responses={201: RESPONSE_CREATE_201, 400: RESPONSE_ERROR_400,
               409: RESPONSE_ERROR_409, 422: RESPONSE_ERROR_422},
)
async def record_consent(
    request: Request,
    payload: ConsentCreateRequest,
    idem_key: IdemKey,
    uc: Annotated[RecordConsentUseCase, Depends(get_record_consent_uc)],
) -> ConsentResponse:
    """TH: บันทึกความยินยอมรายข้อ (idempotent) | EN: Record granular consent"""
    try:
        entity = await uc.execute(
            user_id=payload.user_id, purpose_code=payload.purpose_code,
            ip_address=payload.ip_address, user_agent=payload.user_agent,
            expires_at=payload.expires_at, idempotency_key=idem_key,
            request_method=request.method,
            request_path=request.url.path,
        )
    except DuplicateConsentError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyMismatchError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e),
        ) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return ConsentResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/consent/{consent_id}/revoke",
    summary="ถอนความยินยอม",
    operation_id="revoke_consent",
    response_model=ConsentResponse,
    responses={404: RESPONSE_ERROR_404, 400: RESPONSE_ERROR_400},
)
async def revoke_consent(
    consent_id: uuid.UUID,
    payload: ConsentRevokeRequest,
    uc: Annotated[RevokeConsentUseCase, Depends(get_revoke_consent_uc)],
) -> ConsentResponse:
    try:
        entity = await uc.execute(consent_id=consent_id, reason=payload.reason)
    except ConsentNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return ConsentResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# DSAR
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/dsar/",
    status_code=status.HTTP_201_CREATED,
    summary="ยื่นคำร้อง DSAR",
    operation_id="submit_dsar",
    response_model=DSARResponse,
    responses={201: RESPONSE_CREATE_201, 409: RESPONSE_ERROR_409,
               422: RESPONSE_ERROR_422},
)
async def submit_dsar(
    request: Request,
    payload: DSARCreateRequest,
    idem_key: IdemKey,
    uc: Annotated[SubmitDSARUseCase, Depends(get_submit_dsar_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(
            user_id=payload.user_id, type=payload.type, reason=payload.reason,
            idempotency_key=idem_key,
            request_method=request.method,
            request_path=request.url.path,
        )
    except IdempotencyConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyMismatchError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e),
        ) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


@router.post(
    "/dsar/{dsar_id}/process",
    summary="ประมวลผล DSAR",
    operation_id="process_dsar",
    response_model=DSARResponse,
    responses={404: RESPONSE_ERROR_404, 400: RESPONSE_ERROR_400},
)
async def process_dsar(
    dsar_id: uuid.UUID,
    payload: DSARProcessRequest,
    uc: Annotated[ProcessDSARUseCase, Depends(get_process_dsar_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(
            dsar_id=dsar_id, response_payload=payload.response_payload)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (PDPAError, IdentityVerificationRequiredError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/dsar/{dsar_id}/export",
    summary="Export ข้อมูลผู้ใช้ (JSON)",
    operation_id="export_dsar_data",
    responses={404: RESPONSE_ERROR_404},
)
async def export_dsar_data(
    dsar_id: uuid.UUID,
    user_id: uuid.UUID,
    uc: Annotated[ExportDataUseCase, Depends(get_export_data_uc)],
) -> dict:
    try:
        return await uc.execute_json(dsar_id=dsar_id, user_id=user_id)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/dsar/{dsar_id}/erase",
    summary="ลบ/anonymize ข้อมูล",
    operation_id="erase_dsar_data",
    response_model=DSARResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def erase_dsar_data(
    dsar_id: uuid.UUID,
    user_id: uuid.UUID,
    uc: Annotated[EraseDataUseCase, Depends(get_erase_data_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(dsar_id=dsar_id, user_id=user_id)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Privacy Policy
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/privacy-policy/current",
    summary="นโยบายปัจจุบัน",
    operation_id="get_current_policy",
    response_model=PrivacyPolicyResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_current_policy(
    uc: Annotated[GetCurrentPolicyUseCase, Depends(get_current_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute()
    except PolicyNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/privacy-policy/{version}",
    summary="นโยบายตาม version",
    operation_id="get_policy_version",
    response_model=PrivacyPolicyResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_policy_version(
    version: int,
    uc: Annotated[GetCurrentPolicyUseCase, Depends(get_current_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute(version=version)
    except PolicyNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


@router.post(
    "/privacy-policy/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง/publish privacy policy (admin)",
    operation_id="publish_privacy_policy",
    response_model=PrivacyPolicyResponse,
    responses={201: RESPONSE_CREATE_201, 400: RESPONSE_ERROR_400},
)
async def publish_privacy_policy(
    payload: PrivacyPolicyCreateRequest,
    uc: Annotated[PublishPrivacyPolicyUseCase, Depends(get_publish_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute(
            version=payload.version,
            content_th=payload.content_th,
            content_en=payload.content_en)
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Cookie Consent
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/cookie-consent/",
    status_code=status.HTTP_201_CREATED,
    summary="บันทึก cookie consent (no pre-tick)",
    operation_id="record_cookie_consent",
    response_model=CookieConsentResponse,
    responses={201: RESPONSE_CREATE_201, 422: RESPONSE_ERROR_422},
)
async def record_cookie_consent(
    payload: CookieConsentRequest,
    uc: Annotated[RecordCookieConsentUseCase, Depends(get_record_cookie_uc)],
) -> CookieConsentResponse:
    entity = await uc.execute(
        session_id=payload.session_id,
        analytics=payload.analytics, marketing=payload.marketing,
        functional=payload.functional)
    return CookieConsentResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/cookie-consent/{consent_id}",
    summary="แก้ไข cookie consent",
    operation_id="update_cookie_consent",
    response_model=CookieConsentResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def update_cookie_consent(
    consent_id: uuid.UUID,
    payload: CookieConsentUpdateRequest,
    uc: Annotated[UpdateCookieConsentUseCase, Depends(get_update_cookie_uc)],
) -> CookieConsentResponse:
    try:
        entity = await uc.execute(
            consent_id=consent_id,
            analytics=payload.analytics, marketing=payload.marketing,
            functional=payload.functional)
    except CookieConsentNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return CookieConsentResponse.model_validate(entity, from_attributes=True)
```

---

## 14. `app/modules/pdpa/presentation/docs.py` — **UPDATED**

```python
"""pdpa OpenAPI metadata"""
from __future__ import annotations

RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ",
    "content": {"application/json": {"example": {
        "id": "01HXYZ...", "purpose_code": "DATA_COLLECTION",
        "status": "GRANTED", "version": 1,
    }}},
}
RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {"application/json": {"example": {
        "detail": "invalid state", "code": "DOMAIN_ERROR",
    }}},
}
RESPONSE_ERROR_404 = {
    "description": "ไม่พบ entity",
    "content": {"application/json": {"example": {
        "detail": "not found", "code": "NOT_FOUND",
    }}},
}
RESPONSE_ERROR_409 = {
    "description": "Conflict (duplicate / idempotency in progress)",
    "content": {"application/json": {"example": {
        "detail": "consent already granted", "code": "CONFLICT",
    }}},
}
RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {"application/json": {"example": {
        "detail": [{"loc": ["body"], "msg": "invalid", "type": "value_error"}],
    }}},
}
```

---

## 15. Summary of Changes

| File | Status | Purpose |
|------|--------|---------|
| `domain/enums.py` | updated | Added `IdempotencyStatus` |
| `domain/idempotency.py` | **NEW** | `IdempotencyRecord` entity + hash helper |
| `domain/__init__.py` | updated | Re-export new symbols |
| `application/exceptions.py` | updated | `IdempotencyConflictError`, `IdempotencyMismatchError` |
| `application/interfaces.py` | updated | Rewritten `IdempotencyStore` port (ctx + method/path + fail) |
| `application/mappers.py` | updated | `idempotency_to_entity` |
| `application/utils.py` | updated | `scoped_idempotency_scope` helper |
| `application/use_cases.py` | updated | `RecordConsentUseCase` & `SubmitDSARUseCase` now idempotent |
| `infrastructure/models.py` | updated | `IdempotencyKeyModel` matching SQL schema |
| `infrastructure/idempotency_store.py` | **NEW** | `SQLAlchemyIdempotencyStore` |
| `infrastructure/__init__.py` | updated | Export new store |
| `presentation/dependencies.py` | updated | `get_idempotency_store` + wire into UCs |
| `presentation/routers.py` | updated | Pass `request.method` / `request.url.path` to UCs |
| `presentation/docs.py` | updated | Document 409 semantics |

### Behavior recap
1. Client sends `Idempotency-Key: <uuid>` on `POST /pdpa/consent/` or `POST /pdpa/dsar/`.
2. `SQLAlchemyIdempotencyStore.check_or_lock` computes a SHA-256 of the payload and tries `INSERT`. If the row already existed:
   - **COMPLETED** with same payload → replays stored response by fetching entity by id.
   - **COMPLETED** with different payload → `IdempotencyMismatchError` (422).
   - **IN_PROGRESS** → `IdempotencyConflictError` (409).
   - **FAILED/EXPIRED** → deleted and retried.
3. On success → `complete()` marks row `COMPLETED` and stores `{"id": "..."}`.
4. On domain exception → `fail()` deletes the row so the client can retry with the same key.

This aligns exactly with the `tenant_pdp.idempotency_keys` table from your SQL dump (columns, unique constraint, check constraint, indexes, and the `updated_at` trigger).
