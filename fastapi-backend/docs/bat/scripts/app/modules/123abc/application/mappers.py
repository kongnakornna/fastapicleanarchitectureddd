"""123Abc mappers — ตัวแปลงข้อมูล"""
from __future__ import annotations

from decimal import Decimal

from ..domain.entities import 123Abc
from ..domain.enums import 123AbcStatus
from ..domain.value_objects import Money


class 123AbcMapper:
    """123AbcMapper — ตัวแปลง entity ↔ dict"""

    @staticmethod
    def to_dict(entity: 123Abc) -> dict:
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
    def to_entity(data: dict) -> 123Abc:
        return 123Abc(
            code=data["code"],
            name=data["name"],
            amount=Money(
                Decimal(str(data.get("amount", "0.00"))),
                data.get("currency", "THB"),
            ),
            status=123AbcStatus(data.get("status", "ACTIVE")),
            metadata=data.get("metadata", {}),
        )