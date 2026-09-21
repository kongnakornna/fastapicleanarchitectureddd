"""Money mappers — ตัวแปลงข้อมูล"""
from __future__ import annotations

from decimal import Decimal

from ..domain.entities import Money
from ..domain.enums import MoneyStatus
from ..domain.value_objects import Money


class MoneyMapper:
    """MoneyMapper — ตัวแปลง entity ↔ dict"""

    @staticmethod
    def to_dict(entity: Money) -> dict:
        return {
            "id": str(entity.id),
            "tenant_id": str(entity.tenant_id),
            "code": entity.code,
            "name": entity.name,
            "amount": str(entity.amount.amount),
            "currency": entity.amount.currency,
            "status": entity.status.value,
            "version": entity.version,
            "metadata": entity.metadata,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
            "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
        }

    @staticmethod
    def to_entity(data: dict) -> Money:
        return Money(
            code=data["code"],
            name=data["name"],
            amount=Money(
                Decimal(str(data.get("amount", "0.00"))),
                data.get("currency", "THB"),
            ),
            status=MoneyStatus(data.get("status", "ACTIVE")),
            metadata=data.get("metadata", {}),
        )