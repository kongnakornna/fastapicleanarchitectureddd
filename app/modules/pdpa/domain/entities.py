"""pdpa entities"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from .enums import (
    ConsentStatus, DSARStatus, DSARType,
    PrivacyPolicyStatus, PurposeCategory,
)
from .exceptions import InvalidConsentStateError
from .value_objects import Evidence

_DSAR_SLA_DAYS = 30


@dataclass(slots=True)
class ConsentLog:
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    purpose_code: PurposeCategory
    status: ConsentStatus
    granted_at: datetime
    revoked_at: datetime | None
    expires_at: datetime | None
    evidence: Evidence
    version: int
    created_at: datetime
    updated_at: datetime
    _events: list[object] = field(default_factory=list, repr=False)

    @classmethod
    def grant(
        cls, *, tenant_id: uuid.UUID, user_id: uuid.UUID,
        purpose_code: PurposeCategory, evidence: Evidence,
        expires_at: datetime | None = None,
    ) -> "ConsentLog":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id,
            purpose_code=purpose_code, status=ConsentStatus.GRANTED,
            granted_at=now, revoked_at=None, expires_at=expires_at,
            evidence=evidence, version=1, created_at=now, updated_at=now,
        )

    def revoke(self, *, reason: str) -> None:
        if self.status != ConsentStatus.GRANTED:
            raise InvalidConsentStateError(
                f"cannot revoke consent in status {self.status}"
            )
        self.status = ConsentStatus.REVOKED
        self.revoked_at = datetime.now(UTC)
        self.updated_at = self.revoked_at
        self.version += 1

    def is_active(self) -> bool:
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and self.expires_at < datetime.now(UTC):
            return False
        return True

    def pull_events(self) -> list[object]:
        events = list(self._events); self._events.clear(); return events


@dataclass(slots=True)
class DSARRequest:
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    type: DSARType
    status: DSARStatus
    reason: str | None
    rejection_reason: str | None
    response_payload: dict[str, Any]
    submitted_at: datetime
    verified_at: datetime | None
    completed_at: datetime | None
    deadline_at: datetime
    version: int
    created_at: datetime
    updated_at: datetime
    _events: list[object] = field(default_factory=list, repr=False)

    @classmethod
    def submit(
        cls, *, tenant_id: uuid.UUID, user_id: uuid.UUID,
        type: DSARType, reason: str | None = None,
    ) -> "DSARRequest":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id,
            type=type, status=DSARStatus.SUBMITTED, reason=reason,
            rejection_reason=None, response_payload={},
            submitted_at=now, verified_at=None, completed_at=None,
            deadline_at=now + timedelta(days=_DSAR_SLA_DAYS),
            version=1, created_at=now, updated_at=now,
        )

    def verify(self) -> None:
        if self.status != DSARStatus.SUBMITTED:
            raise InvalidConsentStateError(
                f"cannot verify DSAR in status {self.status}"
            )
        self.status = DSARStatus.VERIFIED
        self.verified_at = datetime.now(UTC)
        self.updated_at = self.verified_at
        self.version += 1

    def complete(self, *, response_payload: dict[str, Any]) -> None:
        if self.status not in (DSARStatus.VERIFIED, DSARStatus.PROCESSING):
            raise InvalidConsentStateError(
                f"cannot complete DSAR in status {self.status}"
            )
        self.status = DSARStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.response_payload = response_payload
        self.updated_at = self.completed_at
        self.version += 1

    def reject(self, *, reason: str) -> None:
        if self.status in (DSARStatus.COMPLETED, DSARStatus.REJECTED):
            raise InvalidConsentStateError(
                f"cannot reject DSAR in status {self.status}"
            )
        self.status = DSARStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = datetime.now(UTC)
        self.version += 1

    def is_overdue(self) -> bool:
        return (
            self.status not in (DSARStatus.COMPLETED, DSARStatus.REJECTED)
            and datetime.now(UTC) > self.deadline_at
        )

    def pull_events(self) -> list[object]:
        events = list(self._events); self._events.clear(); return events


@dataclass(slots=True)
class PrivacyPolicy:
    id: uuid.UUID
    tenant_id: uuid.UUID
    version: int
    content_th: str
    content_en: str
    status: PrivacyPolicyStatus
    effective_from: datetime
    published_at: datetime | None
    superseded_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls, *, tenant_id: uuid.UUID, version: int,
        content_th: str, content_en: str,
    ) -> "PrivacyPolicy":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(), tenant_id=tenant_id, version=version,
            content_th=content_th, content_en=content_en,
            status=PrivacyPolicyStatus.DRAFT, effective_from=now,
            published_at=None, superseded_at=None,
            created_at=now, updated_at=now,
        )

    def publish(self) -> None:
        if self.status != PrivacyPolicyStatus.DRAFT:
            raise InvalidConsentStateError(
                f"cannot publish policy in status {self.status}"
            )
        self.status = PrivacyPolicyStatus.PUBLISHED
        self.published_at = datetime.now(UTC)
        self.updated_at = self.published_at

    def supersede(self) -> None:
        if self.status != PrivacyPolicyStatus.PUBLISHED:
            raise InvalidConsentStateError(
                f"cannot supersede policy in status {self.status}"
            )
        self.status = PrivacyPolicyStatus.SUPERSEDED
        self.superseded_at = datetime.now(UTC)
        self.updated_at = self.superseded_at


@dataclass(slots=True)
class CookieConsent:
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None
    session_id: str
    necessary: bool
    analytics: bool
    marketing: bool
    functional: bool
    ip_address: str | None
    user_agent: str | None
    accepted_at: datetime
    withdrawn_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def record(
        cls, *, tenant_id: uuid.UUID, user_id: uuid.UUID | None,
        session_id: str, analytics: bool, marketing: bool,
        functional: bool, ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> "CookieConsent":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id,
            session_id=session_id, necessary=True,
            analytics=analytics, marketing=marketing, functional=functional,
            ip_address=ip_address, user_agent=user_agent,
            accepted_at=now, withdrawn_at=None, version=1,
            created_at=now, updated_at=now,
        )

    def update_preferences(
        self, *, analytics: bool | None = None,
        marketing: bool | None = None, functional: bool | None = None,
    ) -> None:
        if analytics is not None: self.analytics = analytics
        if marketing is not None: self.marketing = marketing
        if functional is not None: self.functional = functional
        self.updated_at = datetime.now(UTC)
        self.version += 1

    def withdraw(self) -> None:
        self.analytics = False
        self.marketing = False
        self.functional = False
        self.withdrawn_at = datetime.now(UTC)
        self.updated_at = self.withdrawn_at
        self.version += 1
