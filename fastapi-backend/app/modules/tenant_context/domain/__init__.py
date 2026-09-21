"""tenant_context domain layer — pure business logic.

ชั้นโดเมน — ตรรกะธุรกิจล้วน
"""

from .entities import RequestContext
from .enums import IsolationLevel, TenantScope
from .events import (
    TenantContextCleared,
    TenantContextEstablished,
    TenantSwitched,
)
from .exceptions import DomainError
from .value_objects import (
    RequestContext as RequestContextVO,
)
from .value_objects import (
    TenantContext,
    clear_context,
    get_context,
    set_context,
)

__all__ = [
    "DomainError",
    "IsolationLevel",
    "RequestContext",
    "RequestContextVO",
    "TenantContext",
    "TenantContextCleared",
    "TenantContextEstablished",
    "TenantScope",
    "TenantSwitched",
    "clear_context",
    "get_context",
    "set_context",
]
