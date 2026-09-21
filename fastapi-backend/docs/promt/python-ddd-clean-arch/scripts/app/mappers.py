"""TH: Mapper ระหว่าง domain ↔ infra | EN: Domain ↔ infra mappers"""
from __future__ import annotations

from typing import Any

from app.modules.inventory.domain.entities import Inventory
from app.modules.inventory.domain.enums import InventoryStatus, UoM


def to_entity(row: Any) -> Inventory:
    """TH: ORM row → domain entity | EN: ORM row → domain entity"""
    return Inventory(
        id=row.id,
        tenant_id=row.tenant_id,
        code=row.code,
        name=row.name,
        description=row.description,
        quantity=row.quantity,
        uom=UoM(row.uom),
        unit_cost=row.unit_cost,
        status=InventoryStatus(row.status),
        metadata=dict(row.metadata_ or {}),
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
        deleted_at=row.deleted_at,
        # TH: event buffer เริ่มว่างเสมอ (domain เป็นผู้ emit)
        # EN: event buffer starts empty (domain emits)
    )