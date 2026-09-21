"""Money mappers — ตัวแปลงข้อมูล"""

from decimal import Decimal

from ..domain.value_objects import Money


class MoneyMapper:
    """MoneyMapper — ตัวแปลง Money ไป-กลับ schema"""

    @staticmethod
    def to_schema(money: Money) -> dict:
        """แปลง Money เป็น dict"""
        return {"amount": str(money.amount), "currency": money.currency}

    @staticmethod
    def to_entity(data: dict) -> Money:
        """แปลง dict เป็น Money"""
        return Money(Decimal(str(data["amount"])), data.get("currency", "THB"))
