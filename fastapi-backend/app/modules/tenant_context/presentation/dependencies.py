"""tenant_context presentation dependencies — FastAPI DI."""

from fastapi import Header, HTTPException

from ..application.use_cases import TenantContextUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext, get_context, has_context


async def get_tenant_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> TenantContext:
    """FastAPI dependency — ดึง tenant context จาก request.

    ถ้ามี context ใน contextvars แล้ว → ใช้ค่านั้น
    ถ้าไม่มี → สร้างจาก headers
    """
    if has_context():
        return get_context()

    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID header required",
        )

    try:
        ctx = TenantContext(
            tenant_id=x_tenant_id,
            user_id=x_user_id,
            correlation_id=x_correlation_id or "auto-generated",
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ctx


async def get_tenant_context_use_cases() -> TenantContextUseCases:
    """DI provider for tenant_context use cases."""
    # resolver/cache จะถูก inject ในภายหลังผ่าน app wiring
    return TenantContextUseCases(resolver=None, cache=None)
