"""
Domain Events — ชื่อ event ของโดเมน config
ใช้เป็นค่าคงที่สำหรับ publish/subscribe
"""

from __future__ import annotations

from enum import Enum


class ConfigEvent(str, Enum):
    """Config domain event names — ชื่อ event ของ config"""

    CHANGED = "ConfigChanged"
    DELETED = "ConfigDeleted"
    RELOADED = "ConfigReloaded"


__all__ = ["ConfigEvent"]
