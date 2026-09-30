"""bigo Management router — admin ops"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.bigo.infrastructure.management_service import ManagementService
from app.modules.bigo.presentation.dependencies import get_management_service
from app.modules.bigo.presentation.schemas import (
    AdminCacheClearRequest, AdminCacheClearResponse, AdminConfigResponse,
    AdminConfigUpdateRequest, AdminHealthResponse, AdminWSBroadcastRequest,
    AdminWSBroadcastResponse, AdminWSKickResponse, AdminWSListResponse,
    AdminWSStatsResponse,
)

admin_router = APIRouter(prefix="/bigo/admin", tags=["Big-O Admin"])


@admin_router.get("/config", response_model=AdminConfigResponse)
async def get_config(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminConfigResponse:
    return AdminConfigResponse(**svc.get_config())


@admin_router.patch("/config", response_model=AdminConfigResponse)
async def update_config(
    payload: AdminConfigUpdateRequest,
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminConfigResponse:
    try:
        data = svc.update_config(**payload.model_dump(exclude_unset=True))
        return AdminConfigResponse(**data)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@admin_router.get("/health", response_model=AdminHealthResponse)
async def health(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminHealthResponse:
    return AdminHealthResponse(**await svc.health())


@admin_router.get("/cache/stats")
async def cache_stats(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> dict[str, Any]:
    return await svc.cache_stats()


@admin_router.post("/cache/clear", response_model=AdminCacheClearResponse)
async def cache_clear(
    payload: AdminCacheClearRequest,
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminCacheClearResponse:
    data = await svc.cache_clear(prefix=payload.prefix)
    return AdminCacheClearResponse(**data)


@admin_router.get("/ws/stats", response_model=AdminWSStatsResponse)
async def ws_stats(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminWSStatsResponse:
    return AdminWSStatsResponse(**svc.ws_stats())


@admin_router.get("/ws/connections", response_model=AdminWSListResponse)
async def ws_list(
    svc: Annotated[ManagementService, Depends(get_management_service)],
    tenant_id: str | None = None,
    room: str | None = None,
) -> AdminWSListResponse:
    return AdminWSListResponse(
        connections=svc.ws_list(tenant_id=tenant_id, room=room),
    )


@admin_router.post("/ws/broadcast", response_model=AdminWSBroadcastResponse)
async def ws_broadcast(
    payload: AdminWSBroadcastRequest,
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminWSBroadcastResponse:
    data = await svc.ws_broadcast(
        payload.message, room=payload.room, tenant_id=payload.tenant_id,
    )
    return AdminWSBroadcastResponse(**data)


@admin_router.post("/ws/kick/{conn_id}", response_model=AdminWSKickResponse)
async def ws_kick(
    conn_id: str,
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> AdminWSKickResponse:
    return AdminWSKickResponse(**await svc.ws_kick(conn_id))


@admin_router.get("/pipeline/policies")
async def pipeline_policies(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> dict[str, Any]:
    return svc.pipeline_policies()


@admin_router.post("/pipeline/reset-metrics")
async def pipeline_reset_metrics(
    svc: Annotated[ManagementService, Depends(get_management_service)],
) -> dict[str, Any]:
    return svc.pipeline_reset_metrics()
