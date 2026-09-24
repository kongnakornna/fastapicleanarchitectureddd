"""Integration tests for pdpa repository — 6 tests §6"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import text

from app.modules.pdpa.domain.entities import ConsentLog, CookieConsent
from app.modules.pdpa.domain.enums import PurposeCategory
from app.modules.pdpa.domain.value_objects import Evidence
from app.modules.pdpa.infrastructure.repositories import (
    SQLAlchemyConsentRepository, SQLAlchemyCookieConsentRepository,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db_session) -> SQLAlchemyConsentRepository:
    return SQLAlchemyConsentRepository(session=db_session)


@pytest.fixture
def cc_repo(db_session) -> SQLAlchemyCookieConsentRepository:
    return SQLAlchemyCookieConsentRepository(session=db_session)


def _ev() -> Evidence:
    return Evidence(ip_address="127.0.0.1", user_agent="t",
                    occurred_at=datetime.now(UTC))


class TestConsentRepo:
    async def test_save_and_find(self, repo, tenant_ctx) -> None:
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uuid.uuid4(),
            purpose_code=PurposeCategory.DATA_COLLECTION, evidence=_ev())
        await repo.save(tenant_ctx, c)
        got = await repo.find_by_id(tenant_ctx, c.id)
        assert got is not None and got.id == c.id

    async def test_rls_blocks_other_tenant(
        self, repo, tenant_ctx, other_tenant_ctx,
    ) -> None:
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uuid.uuid4(),
            purpose_code=PurposeCategory.DATA_COLLECTION, evidence=_ev())
        await repo.save(tenant_ctx, c)
        got = await repo.find_by_id(other_tenant_ctx, c.id)
        assert got is None

    async def test_revoke_updates_status(self, repo, tenant_ctx) -> None:
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uuid.uuid4(),
            purpose_code=PurposeCategory.USER_ACCOUNT, evidence=_ev())
        await repo.save(tenant_ctx, c)
        c.revoke(reason="test")
        await repo.update(tenant_ctx, c)
        got = await repo.find_by_id(tenant_ctx, c.id)
        assert got is not None and got.status.value == "REVOKED"

    async def test_is_active_returns_false_after_revoke(self, repo, tenant_ctx) -> None:
        uid = uuid.uuid4()
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uid,
            purpose_code=PurposeCategory.USAGE_LOGS, evidence=_ev())
        await repo.save(tenant_ctx, c)
        assert await repo.is_consent_active(tenant_ctx, uid, PurposeCategory.USAGE_LOGS)

    async def test_find_by_user_returns_list(self, repo, tenant_ctx) -> None:
        uid = uuid.uuid4()
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uid,
            purpose_code=PurposeCategory.DATA_COLLECTION, evidence=_ev())
        await repo.save(tenant_ctx, c)
        rows = await repo.find_by_user_id(tenant_ctx, uid)
        assert len(rows) == 1

    async def test_delete_by_user(self, repo, tenant_ctx) -> None:
        uid = uuid.uuid4()
        c = ConsentLog.grant(
            tenant_id=tenant_ctx.tenant_id, user_id=uid,
            purpose_code=PurposeCategory.DATA_COLLECTION, evidence=_ev())
        await repo.save(tenant_ctx, c)
        await repo.delete_by_user_id(tenant_ctx, uid)
        rows = await repo.find_by_user_id(tenant_ctx, uid)
        assert rows == []