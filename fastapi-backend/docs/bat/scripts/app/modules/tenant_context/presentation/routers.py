"""tenant_context presentation routers — API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from ..application.exceptions import (
    TenantContextException,
    TenantNotFoundInContext,
)
from ..application.use_cases import TenantContextUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext
from .dependencies import (
    get_tenant_context,
    get_tenant_context_use_cases,
)
from .schemas import (
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantContextSchema,
)

router = APIRouter(prefix="/api/v1/context", tags=["Tenant Context"])


@router.get("/current/", response_model=TenantContextSchema)
async def get_current(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """ดึง context ปัจจุบัน — Get current tenant context."""
    return TenantContextSchema(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        correlation_id=ctx.correlation_id,
        request_id=ctx.request_id,
        locale=ctx.locale,
        timezone=ctx.timezone,
        schema_name=ctx.schema_name,
        established_at=ctx.established_at,
    )


@router.post("/switch/", response_model=SwitchTenantResponse)
async def switch_tenant(
    req: SwitchTenantRequest,
    use_cases: TenantContextUseCases = Depends(get_tenant_context_use_cases),
):
    """เปลี่ยน tenant — Switch tenant."""
    try:
        ctx = await use_cases.establish(
            tenant_id=req.tenant_id,
            user_id=req.user_id,
            headers={},
        )
        return SwitchTenantResponse(
            tenant_id=ctx.tenant_id,
            correlation_id=ctx.correlation_id,
            schema_name=ctx.schema_name,
        )
    except TenantNotFoundInContext as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenantContextException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
