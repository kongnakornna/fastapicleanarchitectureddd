"""Tenant context — Part 12"""
from __future__ import annotations

import uuid
from contextvars import ContextVar

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


_current_tenant: ContextVar[str | None] = ContextVar("current_tenant", default=None)


def set_current_tenant(tenant_id: str | uuid.UUID | None) -> None:
    _current_tenant.set(str(tenant_id) if tenant_id else None)


def get_current_tenant() -> str | None:
    return _current_tenant.get()


def clear_current_tenant() -> None:
    _current_tenant.set(None)


async def apply_tenant_rls(session: AsyncSession, tenant_id=None) -> None:
    tid = str(tenant_id) if tenant_id else _current_tenant.get()
    if not tid:
        logger.debug("no tenant to apply RLS")
        return
    try:
        await session.execute(text("SET LOCAL app.current_tenant = :tid"), {"tid": tid})
    except Exception as exc:
        logger.warning(f"apply RLS failed: {exc}")


__all__ = [
    "set_current_tenant",
    "get_current_tenant",
    "clear_current_tenant",
    "apply_tenant_rls",
]
