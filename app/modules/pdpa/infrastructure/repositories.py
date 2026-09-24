"""pdpa SQLAlchemy 2.0 async repositories (tenant-isolated)"""
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.modules.pdpa.application.exceptions import ApplicationError
from app.modules.pdpa.application.interfaces import (
    ConsentRepository, CookieConsentRepository, DSARRepository,
    PrivacyPolicyRepository, RequestContext,
)
from app.modules.pdpa.application.mappers import (
    consent_to_entity, cookie_to_entity, dsar_to_entity, policy_to_entity,
)
from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import PurposeCategory
from app.modules.pdpa.infrastructure.models import (
    ConsentLogModel, CookieConsentModel, DSARRequestModel, PrivacyPolicyModel,
)


class RepositoryError(ApplicationError):
    """TH: infra error | EN: infra error"""


def _tid(ctx: RequestContext) -> uuid.UUID:
    """
    TH: ดึง tenant_id พร้อม guard กัน None
    EN: Extract tenant_id with a defensive None guard.

    Fails loudly instead of silently leaking cross-tenant rows.
    """
    tid = getattr(ctx, "tenant_id", None)
    if tid is None:
        raise RepositoryError(
            "RequestContext.tenant_id is None — "
            "check app.core.context.get_context middleware."
        )
    return tid


# ═══════════════════════════════════════════════════════════════
# Consent
# ═══════════════════════════════════════════════════════════════
class SQLAlchemyConsentRepository(ConsentRepository):
    """TH: consent repository | EN: consent repository"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: RequestContext, log_: ConsentLog) -> ConsentLog:
        try:
            model = ConsentLogModel(
                id=log_.id, tenant_id=log_.tenant_id, user_id=log_.user_id,
                purpose_code=log_.purpose_code.value, status=log_.status.value,
                granted_at=log_.granted_at, revoked_at=log_.revoked_at,
                expires_at=log_.expires_at,
                evidence={
                    "ip_address": log_.evidence.ip_address,
                    "user_agent": log_.evidence.user_agent,
                    "occurred_at": log_.evidence.occurred_at.isoformat(),
                },
                version=log_.version,
                created_at=log_.created_at, updated_at=log_.updated_at,
            )
            self._session.add(model)
            await self._session.flush()
            return log_
        except ApplicationError:
            raise
        except Exception as e:
            raise RepositoryError(f"consent save failed: {e}") from e

    async def update(self, ctx: RequestContext, log_: ConsentLog) -> ConsentLog:
        try:
            stmt = select(ConsentLogModel).where(
                ConsentLogModel.id == log_.id,
                ConsentLogModel.tenant_id == _tid(ctx),
            )
            model = (await self._session.execute(stmt)).scalar_one_or_none()
            if model is None:
                raise RepositoryError(f"consent {log_.id} not found")
            model.status = log_.status.value
            model.revoked_at = log_.revoked_at
            model.version = log_.version
            model.updated_at = log_.updated_at
            await self._session.flush()
            return log_
        except ApplicationError:
            raise
        except Exception as e:
            raise RepositoryError(f"consent update failed: {e}") from e

    async def find_by_id(
        self, ctx: RequestContext, id: uuid.UUID,
    ) -> ConsentLog | None:
        try:
            stmt = select(ConsentLogModel).where(
                ConsentLogModel.id == id,
                ConsentLogModel.tenant_id == _tid(ctx),
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return consent_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"consent find_by_id failed: {e}") from e

    async def find_by_user_id(
        self, ctx: RequestContext, user_id: uuid.UUID,
    ) -> list[ConsentLog]:
        try:
            stmt = (
                select(ConsentLogModel)
                .where(
                    ConsentLogModel.tenant_id == _tid(ctx),
                    ConsentLogModel.user_id == user_id,
                )
                .order_by(ConsentLogModel.granted_at.desc())
            )
            rows = (await self._session.execute(stmt)).scalars().all()
            return [consent_to_entity(r) for r in rows]
        except Exception as e:
            raise RepositoryError(f"consent find_by_user_id failed: {e}") from e

    async def find_active_by_user_and_purpose(
        self, ctx: RequestContext, user_id: uuid.UUID,
        purpose: PurposeCategory,
    ) -> ConsentLog | None:
        try:
            stmt = (
                select(ConsentLogModel)
                .where(
                    ConsentLogModel.tenant_id == _tid(ctx),
                    ConsentLogModel.user_id == user_id,
                    ConsentLogModel.purpose_code == purpose.value,
                    ConsentLogModel.status == "GRANTED",
                )
                .order_by(ConsentLogModel.granted_at.desc())
                .limit(1)
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return consent_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"consent find_active failed: {e}") from e

    async def find_latest_by_user_and_purpose(
        self, ctx: RequestContext, user_id: uuid.UUID,
        purpose: PurposeCategory,
    ) -> ConsentLog | None:
        try:
            stmt = (
                select(ConsentLogModel)
                .where(
                    ConsentLogModel.tenant_id == _tid(ctx),
                    ConsentLogModel.user_id == user_id,
                    ConsentLogModel.purpose_code == purpose.value,
                )
                .order_by(ConsentLogModel.granted_at.desc())
                .limit(1)
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return consent_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"consent find_latest failed: {e}") from e

    async def find_ready_for_auto_deletion(
        self, ctx: RequestContext, before: datetime, limit: int = 100,
    ) -> list[ConsentLog]:
        try:
            stmt = (
                select(ConsentLogModel)
                .where(
                    ConsentLogModel.tenant_id == _tid(ctx),
                    ConsentLogModel.expires_at < before,
                    ConsentLogModel.status == "GRANTED",
                )
                .limit(limit)
            )
            rows = (await self._session.execute(stmt)).scalars().all()
            return [consent_to_entity(r) for r in rows]
        except Exception as e:
            raise RepositoryError(f"consent auto_deletion query failed: {e}") from e

    async def delete_by_user_id(
        self, ctx: RequestContext, user_id: uuid.UUID,
    ) -> None:
        try:
            stmt = delete(ConsentLogModel).where(
                ConsentLogModel.tenant_id == _tid(ctx),
                ConsentLogModel.user_id == user_id,
            )
            await self._session.execute(stmt)
            await self._session.flush()
        except Exception as e:
            raise RepositoryError(f"consent delete_by_user_id failed: {e}") from e

    async def delete_by_id(
        self, ctx: RequestContext, id: uuid.UUID,
    ) -> None:
        try:
            stmt = delete(ConsentLogModel).where(
                ConsentLogModel.id == id,
                ConsentLogModel.tenant_id == _tid(ctx),
            )
            await self._session.execute(stmt)
            await self._session.flush()
        except Exception as e:
            raise RepositoryError(f"consent delete_by_id failed: {e}") from e

    async def is_consent_active(
        self, ctx: RequestContext, user_id: uuid.UUID,
        purpose: PurposeCategory,
    ) -> bool:
        try:
            existing = await self.find_active_by_user_and_purpose(
                ctx, user_id, purpose,
            )
            return existing is not None and existing.is_active()
        except Exception as e:
            raise RepositoryError(f"consent is_active failed: {e}") from e

    async def count_active_by_purpose(
        self, ctx: RequestContext, start: datetime, end: datetime,
    ) -> dict[PurposeCategory, int]:
        try:
            stmt = (
                select(
                    ConsentLogModel.purpose_code,
                    func.count(ConsentLogModel.id),
                )
                .where(
                    ConsentLogModel.tenant_id == _tid(ctx),
                    ConsentLogModel.status == "GRANTED",
                    ConsentLogModel.granted_at.between(start, end),
                )
                .group_by(ConsentLogModel.purpose_code)
            )
            rows = (await self._session.execute(stmt)).all()
            return {PurposeCategory(r[0]): int(r[1]) for r in rows}
        except Exception as e:
            raise RepositoryError(f"consent count failed: {e}") from e


# ═══════════════════════════════════════════════════════════════
# DSAR
# ═══════════════════════════════════════════════════════════════
class SQLAlchemyDSARRepository(DSARRepository):
    """TH: DSAR repository | EN: DSAR repository"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: RequestContext, dsar: DSARRequest) -> DSARRequest:
        try:
            stmt = select(DSARRequestModel).where(
                DSARRequestModel.id == dsar.id,
                DSARRequestModel.tenant_id == _tid(ctx),
            )
            existing = (await self._session.execute(stmt)).scalar_one_or_none()
            if existing is None:
                model = DSARRequestModel(
                    id=dsar.id, tenant_id=dsar.tenant_id, user_id=dsar.user_id,
                    type=dsar.type.value, status=dsar.status.value,
                    reason=dsar.reason, rejection_reason=dsar.rejection_reason,
                    response_payload=dsar.response_payload,
                    submitted_at=dsar.submitted_at, verified_at=dsar.verified_at,
                    completed_at=dsar.completed_at, deadline_at=dsar.deadline_at,
                    version=dsar.version,
                    created_at=dsar.created_at, updated_at=dsar.updated_at,
                )
                self._session.add(model)
            else:
                existing.status = dsar.status.value
                existing.reason = dsar.reason
                existing.rejection_reason = dsar.rejection_reason
                existing.response_payload = dsar.response_payload
                existing.verified_at = dsar.verified_at
                existing.completed_at = dsar.completed_at
                existing.version = dsar.version
                existing.updated_at = dsar.updated_at
            await self._session.flush()
            return dsar
        except ApplicationError:
            raise
        except Exception as e:
            raise RepositoryError(f"dsar save failed: {e}") from e

    async def find_by_id(
        self, ctx: RequestContext, id: uuid.UUID,
    ) -> DSARRequest | None:
        try:
            stmt = select(DSARRequestModel).where(
                DSARRequestModel.id == id,
                DSARRequestModel.tenant_id == _tid(ctx),
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return dsar_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"dsar find_by_id failed: {e}") from e

    async def find_by_user_id(
        self, ctx: RequestContext, user_id: uuid.UUID,
    ) -> list[DSARRequest]:
        try:
            stmt = (
                select(DSARRequestModel)
                .where(
                    DSARRequestModel.tenant_id == _tid(ctx),
                    DSARRequestModel.user_id == user_id,
                )
                .order_by(DSARRequestModel.submitted_at.desc())
            )
            rows = (await self._session.execute(stmt)).scalars().all()
            return [dsar_to_entity(r) for r in rows]
        except Exception as e:
            raise RepositoryError(f"dsar find_by_user_id failed: {e}") from e

    async def list_paginated(
        self, ctx: RequestContext, offset: int = 0, limit: int = 100,
    ) -> list[DSARRequest]:
        try:
            stmt = (
                select(DSARRequestModel)
                .where(DSARRequestModel.tenant_id == _tid(ctx))
                .order_by(DSARRequestModel.submitted_at.desc())
                .offset(offset).limit(limit)
            )
            rows = (await self._session.execute(stmt)).scalars().all()
            return [dsar_to_entity(r) for r in rows]
        except Exception as e:
            raise RepositoryError(f"dsar list failed: {e}") from e

    async def find_overdue(
        self, ctx: RequestContext, now: datetime, limit: int = 100,
    ) -> list[DSARRequest]:
        try:
            stmt = (
                select(DSARRequestModel)
                .where(
                    DSARRequestModel.tenant_id == _tid(ctx),
                    DSARRequestModel.deadline_at < now,
                    DSARRequestModel.status.notin_(["COMPLETED", "REJECTED"]),
                )
                .limit(limit)
            )
            rows = (await self._session.execute(stmt)).scalars().all()
            return [dsar_to_entity(r) for r in rows]
        except Exception as e:
            raise RepositoryError(f"dsar find_overdue failed: {e}") from e


# ═══════════════════════════════════════════════════════════════
# Privacy Policy
# ═══════════════════════════════════════════════════════════════
class SQLAlchemyPrivacyPolicyRepository(PrivacyPolicyRepository):
    """TH: privacy policy repository | EN: privacy policy repository"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self, ctx: RequestContext, policy: PrivacyPolicy,
    ) -> PrivacyPolicy:
        try:
            stmt = select(PrivacyPolicyModel).where(
                PrivacyPolicyModel.id == policy.id,
                PrivacyPolicyModel.tenant_id == _tid(ctx),
            )
            existing = (await self._session.execute(stmt)).scalar_one_or_none()
            if existing is None:
                model = PrivacyPolicyModel(
                    id=policy.id, tenant_id=policy.tenant_id,
                    version=policy.version,
                    content_th=policy.content_th, content_en=policy.content_en,
                    status=policy.status.value, effective_from=policy.effective_from,
                    published_at=policy.published_at,
                    superseded_at=policy.superseded_at,
                    created_at=policy.created_at, updated_at=policy.updated_at,
                )
                self._session.add(model)
            else:
                existing.status = policy.status.value
                existing.published_at = policy.published_at
                existing.superseded_at = policy.superseded_at
                existing.updated_at = policy.updated_at
            await self._session.flush()
            return policy
        except Exception as e:
            raise RepositoryError(f"policy save failed: {e}") from e

    async def find_current(self, ctx: RequestContext) -> PrivacyPolicy | None:
        try:
            stmt = (
                select(PrivacyPolicyModel)
                .where(
                    PrivacyPolicyModel.tenant_id == _tid(ctx),
                    PrivacyPolicyModel.status == "PUBLISHED",
                )
                .order_by(PrivacyPolicyModel.version.desc())
                .limit(1)
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return policy_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"policy find_current failed: {e}") from e

    async def find_by_version(
        self, ctx: RequestContext, version: int,
    ) -> PrivacyPolicy | None:
        try:
            stmt = (
                select(PrivacyPolicyModel)
                .where(
                    PrivacyPolicyModel.tenant_id == _tid(ctx),
                    PrivacyPolicyModel.version == version,
                )
                .order_by(PrivacyPolicyModel.created_at.desc())
                .limit(1)
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return policy_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"policy find_by_version failed: {e}") from e

    async def find_by_id(
        self, ctx: RequestContext, id: uuid.UUID,
    ) -> PrivacyPolicy | None:
        try:
            stmt = select(PrivacyPolicyModel).where(
                PrivacyPolicyModel.id == id,
                PrivacyPolicyModel.tenant_id == _tid(ctx),
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return policy_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"policy find_by_id failed: {e}") from e


# ═══════════════════════════════════════════════════════════════
# Cookie Consent
# ═══════════════════════════════════════════════════════════════
class SQLAlchemyCookieConsentRepository(CookieConsentRepository):
    """TH: cookie consent repository | EN: cookie consent repository"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self, ctx: RequestContext, consent: CookieConsent,
    ) -> CookieConsent:
        try:
            model = CookieConsentModel(
                id=consent.id, tenant_id=consent.tenant_id,
                user_id=consent.user_id, session_id=consent.session_id,
                necessary=consent.necessary, analytics=consent.analytics,
                marketing=consent.marketing, functional=consent.functional,
                ip_address=consent.ip_address, user_agent=consent.user_agent,
                accepted_at=consent.accepted_at, withdrawn_at=consent.withdrawn_at,
                version=consent.version,
                created_at=consent.created_at, updated_at=consent.updated_at,
            )
            self._session.add(model)
            await self._session.flush()
            return consent
        except Exception as e:
            raise RepositoryError(f"cookie save failed: {e}") from e

    async def update(
        self, ctx: RequestContext, consent: CookieConsent,
    ) -> CookieConsent:
        try:
            stmt = select(CookieConsentModel).where(
                CookieConsentModel.id == consent.id,
                CookieConsentModel.tenant_id == _tid(ctx),
            )
            model = (await self._session.execute(stmt)).scalar_one_or_none()
            if model is None:
                raise RepositoryError(f"cookie {consent.id} not found")
            model.analytics = consent.analytics
            model.marketing = consent.marketing
            model.functional = consent.functional
            model.withdrawn_at = consent.withdrawn_at
            model.version = consent.version
            model.updated_at = consent.updated_at
            await self._session.flush()
            return consent
        except ApplicationError:
            raise
        except Exception as e:
            raise RepositoryError(f"cookie update failed: {e}") from e

    async def find_by_id(
        self, ctx: RequestContext, id: uuid.UUID,
    ) -> CookieConsent | None:
        try:
            stmt = select(CookieConsentModel).where(
                CookieConsentModel.id == id,
                CookieConsentModel.tenant_id == _tid(ctx),
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return cookie_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"cookie find_by_id failed: {e}") from e

    async def find_by_session(
        self, ctx: RequestContext, session_id: str,
    ) -> CookieConsent | None:
        try:
            stmt = (
                select(CookieConsentModel)
                .where(
                    CookieConsentModel.tenant_id == _tid(ctx),
                    CookieConsentModel.session_id == session_id,
                )
                .order_by(CookieConsentModel.accepted_at.desc())
                .limit(1)
            )
            row = (await self._session.execute(stmt)).scalar_one_or_none()
            return cookie_to_entity(row) if row else None
        except Exception as e:
            raise RepositoryError(f"cookie find_by_session failed: {e}") from e
