"""iot mappers — ORM ↔ domain"""
from __future__ import annotations
from typing import Any


def device_to_dict(row: Any) -> dict[str, Any]:
    return {
        "device_id": str(row.id),
        "device_name": row.device_name,
        "hardware_id": row.hardware_id,
        "type_id": row.type_id,
        "unit": row.unit,
        "status": row.status,
        "location_name": row.location_name,
    }


def alarm_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "device_id": str(row.device_id),
        "alarm_type": row.alarm_type,
        "alarm_status": row.alarm_status,
        "title": row.title,
        "subject": row.subject,
        "value_data": row.value_data,
        "created_at": row.created_at.isoformat() if row.created_at else "",
    }
