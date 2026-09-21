"""Money application interfaces — Protocol ว่าง (VO module)"""

from typing import Protocol

from ..domain.value_objects import ExchangeRate, Money


class IMoneyConverter(Protocol):
    """IMoneyConverter — อินเทอร์เฟซแปลงเงิน (optional)"""

    def convert(self, amount: Money, rate: ExchangeRate) -> Money: ...


__all__ = ["IMoneyConverter"]
