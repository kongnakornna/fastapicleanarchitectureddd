"""app/middleware/tenant.py"""
from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.modules.iot.infrastructure.tenant_context import set_current_tenant


class TenantMiddleware(BaseHTTPMiddleware):
    """TH: ดึง tenant จาก header/query -> set context"""

    SKIP_PREFIXES = (
        "/health", "/docs", "/redoc", "/openapi.json",
        "/static", "/devtools", "/favicon.ico",
    )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return await call_next(request)

        tenant_id = (
            request.headers.get("X-Tenant-Id")
            or request.headers.get("X-Tenant-ID")
            or request.query_params.get("tenant_id")
        )
        set_current_tenant(tenant_id)
        return await call_next(request)
