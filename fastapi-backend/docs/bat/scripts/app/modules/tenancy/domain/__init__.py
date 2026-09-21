"""tenancy domain layer — pure business logic."""

from .entities import Tenant
from .enums import TenantPlanCode, TenantStatus
from .events import TenantActivated, TenantCreated, TenantSuspended
from .exceptions import DomainError
from .value_objects import TenantPlan, TenantSlug

__all__ = [
    "DomainError",
    "Tenant",
    "TenantActivated",
    "TenantCreated",
    "TenantPlan",
    "TenantPlanCode",
    "TenantSlug",
    "TenantStatus",
    "TenantSuspended",
]
