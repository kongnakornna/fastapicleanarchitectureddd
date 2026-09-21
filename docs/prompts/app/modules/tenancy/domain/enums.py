"""tenancy enums — Enum สำหรับ tenancy."""
from enum import Enum


class TenantStatus(str, Enum):
    """TenantStatus — สถานะผู้เช่า."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    CANCELLED = "CANCELLED"


class TenantPlanCode(str, Enum):
    """TenantPlanCode — รหัสแผน."""
    FREE = "FREE"
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"