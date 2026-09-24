"""Money use cases — กรณีการใช้งานเงิน"""

from decimal import Decimal

from ..domain.enums import VATRate
from ..domain.exceptions import DomainError
from ..domain.value_objects import VAT, ExchangeRate, Money


class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""

    def add(self, a: Money, b: Money) -> Money:
        return a + b

    def subtract(self, a: Money, b: Money) -> Money:
        return a - b

    def multiply(self, a: Money, factor: Decimal) -> Money:
        return a * factor

    def calculate_vat(self, base: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).calculate(base)

    def extract_vat(self, total: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).extract(total)

    def convert(self, amount: Money, rate: ExchangeRate) -> Money:
        return rate.convert(amount)

    def sum_all(self, items: list[Money]) -> Money:
        if not items:
            raise DomainError("Cannot sum empty list")
        result = items[0]
        for item in items[1:]:
            result = result + item
        return result
