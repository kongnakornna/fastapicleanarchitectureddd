"""tool_calling HTTP routers"""
from __future__ import annotations
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Header, status

from tool_calling.application.exceptions import ApplicationError
from tool_calling.application.use_case import ToolCallingUseCase
from tool_calling.domain.exceptions import ToolError
from tool_calling.domain.value_objects import ToolSpec
from tool_calling.presentation.dependencies import get_tool_use_case
from tool_calling.presentation.schemas import (
    InvocationResponse, InvokeRequest, InvokeResponse,
    ToolCreateRequest, ToolDetailResponse, ToolResponse,
)

router = APIRouter(prefix="/tools", tags=["Tools"])


class _CtxStub:
    def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self.user_id = user_id


async def _get_ctx() -> Any:
    try:
        from app.core.context import get_context
        return await get_context()
    except Exception:
        return _CtxStub(tenant_id=uuid.UUID(int=1), user_id=uuid.UUID(int=2))


def _raise_http(exc: Exception) -> None:
    if isinstance(exc, ToolError):
        code = getattr(exc, "code", "DOMAIN_ERROR")
        http = {"NOT_FOUND": 404, "CONFLICT": 409,
                "PERMISSION_DENIED": 403, "VALIDATION_ERROR": 422,
                "RATE_LIMITED": 429, "TIMEOUT": 504,
                "PROVIDER_ERROR": 502}.get(code, 400)
        raise HTTPException(status_code=http,
                            detail={"code": code, "message": str(exc)})
    if isinstance(exc, ApplicationError):
        raise HTTPException(
            status_code=getattr(exc, "http_status", 400),
            detail={"code": getattr(exc, "code", "APP_ERROR"),
                    "message": str(exc)})
    raise HTTPException(status_code=500,
                        detail={"code": "INTERNAL_ERROR", "message": "internal error"})


@router.get("", response_model=list[ToolResponse])
async def list_tools(
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
    limit: int = 100, offset: int = 0,
) -> list[ToolResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_tools(ctx, limit, offset)
    return [ToolResponse(**r) for r in rows]


@router.post("", response_model=ToolResponse,
              status_code=status.HTTP_201_CREATED)
async def create_tool(
    payload: ToolCreateRequest,
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
) -> ToolResponse:
    ctx = await _get_ctx()
    try:
        spec = ToolSpec(**payload.model_dump())
        result = await uc.register_tool(ctx, spec)
        return ToolResponse(**result)
    except (ToolError, ApplicationError) as e:
        _raise_http(e)
        raise


@router.get("/{tool_id}", response_model=ToolDetailResponse)
async def get_tool(
    tool_id: uuid.UUID,
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
) -> ToolDetailResponse:
    ctx = await _get_ctx()
    try:
        return ToolDetailResponse(**await uc.get_tool(ctx, tool_id))
    except (ToolError, ApplicationError) as e:
        _raise_http(e)
        raise


@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: uuid.UUID,
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
) -> dict[str, Any]:
    ctx = await _get_ctx()
    try:
        ok_del = await uc.delete_tool(ctx, tool_id)
        return {"deleted": ok_del, "tool_id": str(tool_id)}
    except (ToolError, ApplicationError) as e:
        _raise_http(e)
        raise


@router.post("/{tool_id}/invoke", response_model=InvokeResponse)
async def invoke_tool(
    tool_id: uuid.UUID,
    payload: InvokeRequest,
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
    idem_key: Annotated[str, Header(alias="Idempotency-Key")] = "",
) -> InvokeResponse:
    ctx = await _get_ctx()
    try:
        tool = await uc.get_tool(ctx, tool_id)
        result = await uc.invoke(ctx, tool_name=tool["name"],
                                   arguments=payload.arguments,
                                   idempotency_key=idem_key, role=payload.role)
        return InvokeResponse(
            invocation_id=result.invocation_id, tool_name=result.tool_name,
            status=result.status, output=result.output,
            error=result.error, latency_ms=result.latency_ms)
    except (ToolError, ApplicationError) as e:
        _raise_http(e)
        raise


@router.get("/invocations/list", response_model=list[InvocationResponse])
async def list_invocations(
    uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
    limit: int = 50, offset: int = 0,
) -> list[InvocationResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_invocations(ctx, limit, offset)
    return [InvocationResponse(**r) for r in rows]
