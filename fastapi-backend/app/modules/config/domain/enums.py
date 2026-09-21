"""
Domain Enums — enum ของโดเมน config
ConfigScope: ระดับของ config
ConfigType: ชนิดของค่า config
"""

from __future__ import annotations

from enum import Enum


class ConfigScope(str, Enum):
    """
    Config scope — ขอบเขตของ config
    ลำดับ override: USER > TENANT > GLOBAL
    """

    GLOBAL = "GLOBAL"  # ค่าทั้งระบบ (ใช้ร่วมทุก tenant)
    TENANT = "TENANT"  # ค่าเฉพาะ tenant
    USER = "USER"  # ค่าเฉพาะ user (override สูงสุด)


class ConfigType(str, Enum):
    """
    Config type — ชนิดของค่าที่เก็บ
    """

    STRING = "string"
    INT = "int"
    DECIMAL = "decimal"
    BOOL = "bool"
    JSON = "json"
    SECRET = "secret"
