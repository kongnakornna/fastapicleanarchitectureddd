"""Money domain events — เหตุการณ์โดเมนเงิน"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MoneyAdded:
    """MoneyAdded — เหตุการณ์บวกเงิน"""

    a: Decimal
    b: Decimal
    result: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class MoneySubtracted:
    """MoneySubtracted — เหตุการณ์ลบเงิน"""

    a: Decimal
    b: Decimal
    result: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class VATCalculated:
    """VATCalculated — เหตุการณ์คำนวณ VAT"""

    base: Decimal
    rate: Decimal
    vat: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class CurrencyConverted:
    """CurrencyConverted — เหตุการณ์แปลงสกุลเงิน"""

    from_currency: str
    to_currency: str
    rate: Decimal
    amount: Decimal
    converted: Decimal
    occurred_at: datetime
