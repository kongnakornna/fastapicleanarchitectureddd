"""tenant_context application utils — เครื่องมือช่วย."""

import functools
from collections.abc import Callable

from ..domain.value_objects import get_context, has_context
from .exceptions import TenantNotFoundInContext


def requires_tenant(fn: Callable) -> Callable:
    """Decorator: บังคับว่าต้องมี tenant context.

    Decorator: enforce that tenant context exists.
    """

    @functools.wraps(fn)
    async def async_wrapper(*args, **kwargs):
        if not has_context():
            raise TenantNotFoundInContext()
        return await fn(*args, **kwargs)

    @functools.wraps(fn)
    def sync_wrapper(*args, **kwargs):
        if not has_context():
            raise TenantNotFoundInContext()
        return fn(*args, **kwargs)

    import inspect

    if inspect.iscoroutinefunction(fn):
        return async_wrapper
    return sync_wrapper


def tenant_scoped(key: str) -> str:
    """สร้าง key ที่ scope ตาม tenant ปัจจุบัน — Tenant-scoped key."""
    ctx = get_context()
    return ctx.redis_namespace(key)
