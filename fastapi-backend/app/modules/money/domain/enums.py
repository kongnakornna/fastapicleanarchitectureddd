"""Money enums — Enum สำหรับเงิน"""

from enum import Enum


class Currency(str, Enum):
    """Currency — สกุลเงิน"""

    THB = "THB"
    USD = "USD"
    EUR = "EUR"


class VATRate(str, Enum):
    """VAT rate — อัตราภาษีมูลค่าเพิ่ม"""

    ZERO = "0.00"
    SEVEN = "0.07"


class RoundingMode(str, Enum):
    """Rounding mode — โหมดปัดเศษ"""

    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    BANKERS = "BANKERS"
