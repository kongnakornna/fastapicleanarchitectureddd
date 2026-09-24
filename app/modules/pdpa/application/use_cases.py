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