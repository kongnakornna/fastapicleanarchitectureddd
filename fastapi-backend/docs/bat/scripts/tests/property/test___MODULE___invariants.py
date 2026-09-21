"""tests/property/test_inventory_invariants.py — Property-based"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.inventory.domain.entities import Inventory
from app.modules.inventory.domain.exceptions import InvalidAmountError
from app.modules.inventory.domain.value_objects import Money

pytestmark = pytest.mark.property

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")

amounts = st.decimals(
    min_value=Decimal("0.00"),
    max_value=Decimal("999999999.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

codes = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-",
    min_size=1, max_size=50,
)


@settings(max_examples=100)
@given(amount=amounts, code=codes)
def test_non_negative_amount_always_valid(amount: Decimal, code: str) -> None:
    e = Inventory.create(
        tenant_id=TENANT, code=code or "X", name="P", amount=amount,
    )
    assert e.amount.amount >= Decimal("0.00")


@settings(max_examples=100)
@given(amount=st.decimals(
    min_value=Decimal("-9999"), max_value=Decimal("-0.01"), places=2,
))
def test_negative_amount_always_rejected(amount: Decimal) -> None:
    with pytest.raises(InvalidAmountError):
        Inventory.create(
            tenant_id=TENANT, code="X", name="P", amount=amount,
        )


@settings(max_examples=100)
@given(a=amounts, b=amounts)
def test_sum_is_commutative(a: Decimal, b: Decimal) -> None:
    m1 = Money(a); m2 = Money(b)
    assert (m1 + m2).amount == (m2 + m1).amount