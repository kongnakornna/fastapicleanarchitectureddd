"""tests/unit/test_money_use_cases.py — Application layer"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.money.application.exceptions import DuplicateCodeError
from app.modules.money.application.use_cases import CreateMoneyUseCase
from app.modules.money.domain.entities import Money

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> AsyncMock:
    r = AsyncMock()
    r.get_by_code.return_value = None
    r.save.side_effect = lambda e: e
    r.get_by_id.side_effect = lambda _id: MagicMock(spec=Money)
    return r


@pytest.fixture
def cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def event_bus() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def idem() -> AsyncMock:
    m = AsyncMock()
    m.check_or_lock.return_value = None
    return m


@pytest.fixture
def uc(repo, cache, event_bus, idem, tenant_ctx) -> CreateMoneyUseCase:
    return CreateMoneyUseCase(
        repo=repo, cache=cache, event_bus=event_bus,
        idempotency=idem, ctx=tenant_ctx,
    )


class TestCreateUseCase:
    async def test_happy_path(self, uc, repo, event_bus) -> None:
        await uc.execute(
            code="X-001", name="Test",
            amount=Decimal("100.00"), idempotency_key="k-12345678",
        )
        repo.save.assert_awaited_once()
        event_bus.publish.assert_awaited_once()

    async def test_duplicate_code_raises(self, uc, repo) -> None:
        repo.get_by_code.return_value = MagicMock(spec=Money)
        with pytest.raises(DuplicateCodeError):
            await uc.execute(
                code="X-001", name="Dup",
                amount=Decimal("1.00"), idempotency_key="k-12345678",
            )
        repo.save.assert_not_awaited()

    async def test_cache_failure_does_not_break(self, uc, cache) -> None:
        cache.invalidate.side_effect = RuntimeError("redis down")
        await uc.execute(
            code="X-002", name="X",
            amount=Decimal("1.00"), idempotency_key="k-22345678",
        )

    async def test_readback_verification(self, uc, repo) -> None:
        await uc.execute(
            code="X-003", name="X",
            amount=Decimal("1.00"), idempotency_key="k-32345678",
        )
        repo.get_by_id.assert_awaited_once()