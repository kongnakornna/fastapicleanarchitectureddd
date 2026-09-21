"""tenant_context enums — Enum สำหรับบริบทผู้เช่า."""

from enum import Enum


class TenantScope(str, Enum):
    """TenantScope — ขอบเขตการเข้าถึง tenant."""

    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class IsolationLevel(str, Enum):
    """IsolationLevel — ระดับการแยกข้อมูล."""

    SCHEMA_PER_TENANT = "SCHEMA_PER_TENANT"
    DATABASE_PER_TENANT = "DATABASE_PER_TENANT"
    ROW_LEVEL = "ROW_LEVEL"
