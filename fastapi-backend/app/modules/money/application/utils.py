"""Money application utils — เครื่องมือช่วย"""

from decimal import ROUND_HALF_UP, Decimal

from ..domain.value_objects import Money


def round_money(amount: Decimal, places: int = 2) -> Decimal:
    """ปัดเศษเงิน — Round money to N places"""
    quant = Decimal("0.01") if places == 2 else Decimal(10) ** -places
    return amount.quantize(quant, rounding=ROUND_HALF_UP)


def zero_money(currency: str = "THB") -> Money:
    """สร้าง Money ศูนย์ — Create zero money"""
    return Money(Decimal("0.00"), currency)
