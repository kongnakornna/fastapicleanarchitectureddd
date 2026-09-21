"""Module tenant_context — Layer 0 (Clean Architecture + DDD).

Tenant context propagation ผ่าน contextvars สำหรับ multi-tenant ERP/CRM/IoT
Tenant context propagation via contextvars for multi-tenant ERP/CRM/IoT
"""

__version__ = "1.0.0"

from .domain.enums import IsolationLevel, TenantScope
from .domain.value_objects import (
    RequestContext,
    TenantContext,
    clear_context,
    get_context,
    set_context,
)

__all__ = [
    "IsolationLevel",
    "RequestContext",
    "TenantContext",
    "TenantScope",
    "clear_context",
    "get_context",
    "set_context",
]
