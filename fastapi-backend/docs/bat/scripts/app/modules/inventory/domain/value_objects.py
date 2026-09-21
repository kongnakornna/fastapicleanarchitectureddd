"""Inventory value objects — วัตถุค่า inventory"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from .exceptions import DomainError

SUPPORTED_CURRENCIES = frozenset({"THB", "USD", "EUR"})
CENT = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""

    amount: Decimal
    currency: str = "THB"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("amount must be Decimal")
        object.__setattr__(
            self, "amount",
            self.amount.quantize(CENT, rounding=ROUND_HALF_UP),
        )
        if self.currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(
                f"cannot operate {self.currency} vs {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            raise DomainError("factor must be Decimal")
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")


@dataclass(frozen=True)
class ExchangeRate:
    """ExchangeRate — วัตถุอัตราแลกเปลี่ยน"""

    from_currency: str
    to_currency: str
    rate: Decimal
    as_of: datetime

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise DomainError("exchange rate must be positive")
        if self.from_currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.from_currency}")
        if self.to_currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.to_currency}")

    def convert(self, amount: Money) -> Money:
        if amount.currency != self.from_currency:
            raise DomainError("currency mismatch")
        return Money(amount.amount * self.rate, self.to_currency)