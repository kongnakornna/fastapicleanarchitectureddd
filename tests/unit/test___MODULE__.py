"""tests/unit/test_money.py — Domain layer unit tests"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.modules.money.domain.entities import Money
from app.modules.money.domain.enums import MoneyStatus
from app.modules.money.domain.exceptions import (
    DomainError, InvalidAmountError, InvalidStatusTransitionError,
)
from app.modules.money.domain.value_objects import Money

pytestmark = pytest.mark.unit

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def make_entity():
    def _make(
        code: str = "X-001",
        name: str = "Sample",
        amount: Decimal = Decimal("100.00"),
        status: MoneyStatus = MoneyStatus.ACTIVE,
    ) -> Money:
        return Money.create(
            tenant_id=TENANT, code=code, name=name, amount=amount, status=status,
        )
    return _make


class TestCreate:
    def test_create_sets_defaults(self, make_entity) -> None:
        e = make_entity()
        assert e.id is not None
        assert e.version == 1
        assert e.status is MoneyStatus.ACTIVE
        assert e.deleted_at is None

    def test_create_with_zero_amount(self, make_entity) -> None:
        e = make_entity(amount=Decimal("0.00"))
        assert e.amount.amount == Decimal("0.00")

    def test_amount_precision_quantized(self, make_entity) -> None:
        e = make_entity(amount=Decimal("100.005"))
        assert e.amount.amount == Decimal("100.01")


class TestBehavior:
    def test_activate_from_inactive(self, make_entity) -> None:
        e = make_entity(status=MoneyStatus.INACTIVE)
        e.activate()
        assert e.status is MoneyStatus.ACTIVE
        assert e.version == 2

    def test_archive_then_activate_raises(self, make_entity) -> None:
        e = make_entity()
        e.archive()
        with pytest.raises(InvalidStatusTransitionError):
            e.activate()

    def test_soft_delete_sets_timestamp(self, make_entity) -> None:
        e = make_entity()
        e.soft_delete()
        assert e.deleted_at is not None
        assert e.is_deleted() is True


class TestErrors:
    def test_negative_amount_raises(self, make_entity) -> None:
        with pytest.raises(InvalidAmountError):
            make_entity(amount=Decimal("-1.00"))

    def test_empty_code_raises(self, make_entity) -> None:
        with pytest.raises(DomainError):
            make_entity(code="")


class TestMoneyVO:
    def test_money_add(self) -> None:
        a = Money(Decimal("10.00"))
        b = Money(Decimal("5.50"))
        assert (a + b).amount == Decimal("15.50")

    def test_money_currency_mismatch(self) -> None:
        a = Money(Decimal("10.00"), "THB")
        b = Money(Decimal("5.00"), "USD")
        with pytest.raises(DomainError):
            _ = a + b