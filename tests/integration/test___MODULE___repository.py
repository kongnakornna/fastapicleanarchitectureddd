"""tests/integration/test_money_repository.py — Repository + RLS"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.modules.money.domain.entities import Money
from app.modules.money.infrastructure.repositories import (
    SQLAlchemyMoneyRepository,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db_session) -> SQLAlchemyMoneyRepository:
    return SQLAlchemyMoneyRepository(session=db_session)


class TestRepository:
    async def test_save_and_get(self, repo, tenant_ctx) -> None:
        e = Money.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"X-{uuid.uuid4().hex[:6]}",
            name="Repo Test",
            amount=Decimal("99.99"),
        )
        saved = await repo.save(e)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.code == saved.code

    async def test_rls_blocks_other_tenant(
        self, repo, db_session, tenant_ctx, other_tenant_ctx
    ) -> None:
        e = Money.create(
            tenant_id=tenant_ctx["tenant_id"],
            code="X-RLS-1", name="RLS", amount=Decimal("1.00"),
        )
        await repo.save(e)
        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx["tenant_id"])},
        )
        found = await repo.get_by_id(e.id)
        assert found is None

    async def test_unique_code_conflict(self, repo, tenant_ctx) -> None:
        code = f"X-{uuid.uuid4().hex[:6]}"
        e1 = Money.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="A", amount=Decimal("1.00"),
        )
        await repo.save(e1)
        e2 = Money.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="B", amount=Decimal("2.00"),
        )
        with pytest.raises(Exception):
            await repo.save(e2)

    async def test_soft_delete_filter(self, repo, tenant_ctx) -> None:
        e = Money.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"X-{uuid.uuid4().hex[:6]}",
            name="Soft", amount=Decimal("1.00"),
        )
        saved = await repo.save(e)
        await repo.soft_delete(saved.id)
        found = await repo.get_by_id(saved.id)
        assert found is None