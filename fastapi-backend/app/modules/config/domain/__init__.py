"""
Domain Layer — ชั้นโดเมน
ประกอบด้วย Entity, Value Object, Enum ของ config
"""

from __future__ import annotations

from .entities import ConfigEntry
from .enums import ConfigScope, ConfigType
from .value_objects import ConfigKey

__all__ = [
    "ConfigEntry",
    "ConfigKey",
    "ConfigScope",
    "ConfigType",
]
