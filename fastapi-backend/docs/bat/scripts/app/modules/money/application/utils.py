"""Money application utils — เครื่องมือช่วย"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ..domain.value_objects import Money


def round_money(amount: Decimal, places: int = 2) -> Decimal:
    """TH: ปัดเศษเงิน | EN: round money"""
    quant = Decimal("0.01") if places == 2 else Decimal(10) ** -places
    return amount.quantize(quant, rounding=ROUND_HALF_UP)


def zero_money(currency: str = "THB") -> Money:
    """TH: สร้าง Money ศูนย์ | EN: zero money"""
    return Money(Decimal("0.00"), currency)


def clamp_limit(limit: int, *, maximum: int = 100) -> int:
    """TH: จำกัด limit | EN: clamp limit"""
    return max(1, min(limit, maximum))