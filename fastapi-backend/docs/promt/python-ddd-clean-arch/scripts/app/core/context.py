"""TH: Request context + contextvar | EN: Request context + contextvar"""
from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi import Depends, Header, HTTPException, status

_ctx_var: ContextVar["RequestContext | None"] = ContextVar("request_ctx", default=None)


@dataclass(slots=True)
class RequestContext:
    """TH: context ต่อ request | EN: per-request context"""

    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None
    roles: list[str] = field(default_factory=list)
    trace_id: str = ""
    request_id: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))


async def get_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_roles: str | None = Header(default=None, alias="X-Roles"),
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> RequestContext:
    """TH: สร้าง ctx จาก header (prod ใช้ JWT) | EN: build ctx from headers (prod uses JWT)"""
    if not x_tenant_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="missing tenant context")

    try:
        tenant_id = uuid.UUID(x_tenant_id)
    except ValueError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid tenant id"
        ) from e

    ctx = RequestContext(
        tenant_id=tenant_id,
        user_id=uuid.UUID(x_user_id) if x_user_id else None,
        roles=[r.strip() for r in (x_roles or "").split(",") if r.strip()],
        trace_id=x_trace_id or uuid.uuid4().hex,
        request_id=x_request_id or uuid.uuid4().hex,
    )
    _ctx_var.set(ctx)
    return ctx


def current_context() -> RequestContext | None:
    """TH: ดึง ctx ปัจจุบัน | EN: get current ctx"""
    return _ctx_var.get()