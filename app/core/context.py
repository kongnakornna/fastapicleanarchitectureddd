"""Request context — tenant_id + user_id (จาก middleware หรือ JWT)"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, Request

# TH: default tenant (dev) — override ด้วย header X-Tenant-Id
DEFAULT_TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_USER = uuid.UUID("00000000-0000-0000-0000-000000000002")


@dataclass
class RequestContext:
    """TH: request context | EN: request context"""
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None


async def get_context(
    request: Request,
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-Id")] = None,
) -> RequestContext:
    """TH: dependency ที่ดึง context | EN: DI provider"""
    tenant_id = DEFAULT_TENANT
    if x_tenant_id:
        try:
            tenant_id = uuid.UUID(x_tenant_id)
        except ValueError:
            pass

    # ลองดึง user จาก request.state (middleware อาจ set ไว้)
    user_id = getattr(request.state, "user_id", None) or DEFAULT_USER
    return RequestContext(tenant_id=tenant_id, user_id=user_id)
