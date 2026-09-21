# app/shared/tenant_context.py - contextvars for tenant isolation
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    user_id: str | None = None
    correlation_id: str = ""


_ctx: ContextVar[TenantContext | None] = ContextVar("tenant_ctx", default=None)


def set_context(ctx: TenantContext) -> None:
    _ctx.set(ctx)


def get_context() -> TenantContext:
    ctx = _ctx.get()
    if ctx is None:
        raise RuntimeError("Tenant context not set")
    return ctx


def clear_context() -> None:
    _ctx.set(None)