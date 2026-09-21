"""tenancy presentation routers — API endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException

from ..application.exceptions import (
    TenancyException,
    TenantNotFoundException,
    TenantSlugConflictException,
)
from ..application.use_cases import TenancyUseCases
from ..domain.exceptions import DomainError
from .dependencies import get_tenancy_use_cases
from .schemas import (
    SuspendRequest,
    TenantCreate,
    TenantResponse,
    UpgradeRequest,
)

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenancy"])


@router.post("/", response_model=TenantResponse, status_code=201)
async def create_tenant(
    payload: TenantCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """สร้าง tenant — Create tenant."""
    try:
        tenant = await uc.create_tenant(payload.model_dump(), idem_key)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantSlugConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.get("/{id}/", response_model=TenantResponse)
async def get_tenant(
    id: str,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """ดึง tenant — Get tenant."""
    try:
        tenant = await uc.get(id)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.patch("/{id}/suspend/", response_model=TenantResponse)
async def suspend_tenant(
    id: str,
    payload: SuspendRequest,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """ระงับ tenant — Suspend tenant."""
    try:
        tenant = await uc.suspend_tenant(id, payload.reason)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.patch("/{id}/upgrade/", response_model=TenantResponse)
async def upgrade_plan(
    id: str,
    payload: UpgradeRequest,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """อัปเกรดแผน — Upgrade plan."""
    try:
        tenant = await uc.upgrade_plan(id, payload.plan)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")