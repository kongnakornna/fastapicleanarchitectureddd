"""Money presentation schemas — Pydantic schemas"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..domain.enums import VATRate
from ..domain.value_objects import Money


class MoneySchema(BaseModel):
    """MoneySchema — schema สำหรับเงิน"""

    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    model_config = ConfigDict(from_attributes=True)

    def to_money(self) -> Money:
        """แปลงเป็น Money VO"""
        return Money(self.amount, self.currency)


class VATRequest(BaseModel):
    """VATRequest — คำขอคำนวณ VAT"""

    base: MoneySchema
    rate: VATRate = VATRate.SEVEN


class VATResponse(BaseModel):
    """VATResponse — ผลลัพธ์ VAT"""

    vat: MoneySchema
    total: MoneySchema


class ExchangeRateSchema(BaseModel):
    """ExchangeRateSchema — schema อัตราแลกเปลี่ยน"""

    from_currency: str = Field(..., pattern="^(THB|USD|EUR)$")
    to_currency: str = Field(..., pattern="^(THB|USD|EUR)$")
    rate: Decimal = Field(..., gt=0)
    as_of: datetime = Field(default_factory=datetime.utcnow)
