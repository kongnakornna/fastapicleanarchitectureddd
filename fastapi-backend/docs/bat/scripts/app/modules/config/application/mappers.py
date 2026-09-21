"""
Application Mappers — แปลง entity ↔ schema
ConfigMapper: แปลง ConfigEntry เป็น dict/schema พร้อม mask secret
"""

from __future__ import annotations

from typing import Any

from ..domain.entities import ConfigEntry


class ConfigMapper:
    """
    Config mapper — แปลง entity เป็น dict สำหรับ API
    รองรับ mask secret และ typed value
    """

    @staticmethod
    def to_dict(entry: ConfigEntry, mask: bool = True) -> dict[str, Any]:
        """
        แปลง ConfigEntry → dict
        Args:
            entry: ConfigEntry
            mask: หาก True จะปิดบัง secret
        """
        target = entry.mask() if mask else entry
        return {
            "key": target.key,
            "value": target.value,
            "value_type": target.value_type,
            "scope": target.scope,
            "scope_id": target.scope_id,
            "is_secret": target.is_secret,
            "description": target.description,
            "created_at": getattr(target, "created_at", None),
            "updated_at": getattr(target, "updated_at", None),
        }

    @staticmethod
    def to_typed_dict(entry: ConfigEntry, mask: bool = True) -> dict[str, Any]:
        """
        แปลง ConfigEntry → dict พร้อม typed value
        secret จะถูก mask (ไม่ให้ typed_value เพราะจะ throw หากถูก mask)
        """
        target = entry.mask() if mask else entry
        result = ConfigMapper.to_dict(entry, mask=mask)
        if not target.is_secret:
            try:
                result["typed_value"] = target.typed_value()
            except Exception:
                result["typed_value"] = target.value
        else:
            result["typed_value"] = None
        return result
