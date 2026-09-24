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