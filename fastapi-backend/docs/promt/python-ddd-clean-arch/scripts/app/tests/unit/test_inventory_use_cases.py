"""TH: Unit test use cases | EN: Use case unit tests"""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.inventory.application.exceptions import DuplicateCodeError
from app.modules.inventory.application.use_cases import CreateInventoryUseCase
from app.modules.inventory.domain.entities import Inventory
from app.modules.inventory.domain.enums import UoM

pytestmark = pytest.mark.unit
TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def repo() -> AsyncMock:
    """TH: in-memory repo ที่ read-back ได้จริง | EN: in-memory repo w/ read-back"""
    r = AsyncMock()
    r.get_by_code.return_value = None
    store: dict[uuid.UUID, Inventory] = {}

    async def _save(entity: Inventory) -> Inventory:
        store[entity.id] = entity
        return entity

    async def _get_by_id(entity_id: uuid.UUID) -> Inventory | None:
        return store.get(entity_id)

    r.save.side_effect = _save
    r.get_by_id.side_effect = _get_by_id
    return r


@pytest.fixture
def cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def bus() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def idem() -> AsyncMock:
    m = AsyncMock()
    m.check_or_lock.return_value = None
    return m


@pytest.fixture
def ctx() -> MagicMock:
    m = MagicMock()
    m.tenant_id = TENANT
    return m


@pytest.fixture
def uc(repo, cache, bus, idem, ctx) -> CreateInventoryUseCase:
    return CreateInventoryUseCase(
        repo=repo, cache=cache, bus=bus, idem=idem, ctx=ctx,
    )


class TestCreate:
    async def test_happy_path(self, uc, repo, bus) -> None:
        out = await uc.execute(
            code="INV-001", name="Widget", quantity=Decimal("10.00"),
            uom=UoM.PIECE, unit_cost=Decimal("99.99"), idempotency_key="k-1",
        )
        assert out.code == "INV-001"
        assert out.id is not None
        repo.save.assert_awaited_once()
        bus.publish.assert_awaited()

    async def test_duplicate(self, uc, repo) -> None:
        repo.get_by_code.return_value = MagicMock(spec=Inventory)
        with pytest.raises(DuplicateCodeError):
            await uc.execute(
                code="INV-001", name="Dup", quantity=Decimal("1.00"),
                uom=UoM.PIECE, unit_cost=Decimal("1.00"), idempotency_key="k-2",
            )
        repo.save.assert_not_awaited()

    async def test_cache_failure_does_not_break(self, uc, cache, bus) -> None:
        cache.invalidate.side_effect = RuntimeError("redis down")
        out = await uc.execute(
            code="INV-002", name="X", quantity=Decimal("1.00"),
            uom=UoM.PIECE, unit_cost=Decimal("1.00"), idempotency_key="k-3",
        )
        assert out.code == "INV-002"

    async def test_readback_returns_same_id(self, uc, repo) -> None:
        """TH: read-back ต้องได้ id เดียวกับ save | EN: read-back id equals saved id"""
        out = await uc.execute(
            code="INV-003", name="X", quantity=Decimal("1.00"),
            uom=UoM.PIECE, unit_cost=Decimal("1.00"), idempotency_key="k-4",
        )
        repo.get_by_id.assert_awaited()
        # ยืนยันว่า read-back คืน id เดียวกัน
        verified = await repo.get_by_id(out.id)
        assert verified is not None
        assert verified.id == out.id

    async def test_event_published(self, uc, bus) -> None:
        await uc.execute(
            code="INV-004", name="X", quantity=Decimal("1.00"),
            uom=UoM.PIECE, unit_cost=Decimal("1.00"), idempotency_key="k-5",
        )
        bus.publish.assert_awaited()