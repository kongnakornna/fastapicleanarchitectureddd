"""
Audit Routers — router audit
Audit Routers — FastAPI endpoints for audit module
"""

from __future__ import annotations

from audit.application.use_cases import AuditUseCases
from audit.presentation.dependencies import get_audit_use_cases
from audit.presentation.schemas import (
    AuditLogPage,
    AuditLogSchema,
    AuditQuery,
)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


def _to_schema(log) -> AuditLogSchema:
    """Entity → schema — entity → schema"""
    return AuditLogSchema(
        id=log.id,
        action=log.action,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        actor_id=log.actor_id,
        before_state=log.before_state,
        after_state=log.after_state,
        changes=log.changes,
        ip_address=log.ip_address or None,
        user_agent=log.user_agent or None,
        correlation_id=log.correlation_id or None,
        severity=log.severity,
        occurred_at=log.occurred_at,
    )


@router.get("/logs/", response_model=AuditLogPage)
async def list_logs(
    filters: AuditQuery = Depends(),
    uc: AuditUseCases = Depends(get_audit_use_cases),
):
    """List audit logs with filters — แสดงรายการบันทึก audit พร้อม filter"""
    filter_dict = {
        k: v
        for k, v in filters.model_dump().items()
        if v is not None and k not in {"page", "limit"}
    }
    items, total = await uc.query(filter_dict, filters.page, filters.limit)
    return AuditLogPage(
        items=[_to_schema(i) for i in items],
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.get("/logs/{id}/", response_model=AuditLogSchema)
async def get_log(
    id: str,
    uc: AuditUseCases = Depends(get_audit_use_cases),
):
    """Get audit log by id — ดึงบันทึก audit ตาม id"""
    log = await uc.get(id)
    if log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return _to_schema(log)


@router.get(
    "/resources/{type}/{id}/history/",
    response_model=list[AuditLogSchema],
)
async def resource_history(
    type: str,
    id: str,
    uc: AuditUseCases = Depends(get_audit_use_cases),
):
    """Get resource history — ดึงประวัติ resource"""
    logs = await uc.resource_history(type, id)
    return [_to_schema(l) for l in logs]
