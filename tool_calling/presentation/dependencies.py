"""tool_calling DI container"""
from __future__ import annotations
from typing import Annotated, Any

from fastapi import Depends

from tool_calling.application.use_case import ToolCallingUseCase
from tool_calling.infrastructure.invocation_repository import InvocationRepository
from tool_calling.infrastructure.permission_repository import PermissionRepository
from tool_calling.infrastructure.services import (
    DefaultToolClientRegistry, NoopEventBus, RedisRateLimiter,
)
from tool_calling.infrastructure.tool_repository import ToolRepository

_registry: DefaultToolClientRegistry | None = None


def _get_registry() -> DefaultToolClientRegistry:
    global _registry
    if _registry is None:
        _registry = DefaultToolClientRegistry()
    return _registry


async def _get_redis() -> Any:
    try:
        from app.core.redis import get_redis
        return await get_redis()
    except Exception:
        return None


async def _get_event_bus() -> Any:
    try:
        from app.core.events import get_event_bus
        return await get_event_bus()
    except Exception:
        return NoopEventBus()


async def _get_session():
    try:
        from app.core.db import get_session
        async for s in get_session():
            yield s
    except Exception:
        yield None


async def get_tool_use_case(
    session: Annotated[Any, Depends(_get_session)] = None,
) -> ToolCallingUseCase:
    redis = await _get_redis()
    bus = await _get_event_bus()
    rate_limiter = RedisRateLimiter(redis) if redis else _NoopRateLimiter()
    return ToolCallingUseCase(
        tool_repo=ToolRepository(session),
        registration_repo=_NoopRegistrationRepo(),
        invocation_repo=InvocationRepository(session),
        permission_repo=PermissionRepository(session),
        clients=_get_registry(),
        rate_limiter=rate_limiter,
        event_bus=bus)


class _NoopRateLimiter:
    async def check_and_incr(self, tenant_id, user_id, tool_id, limit_per_min):
        return True


class _NoopRegistrationRepo:
    async def save(self, ctx, r):
        return r

    async def find_by_tool(self, ctx, tool_id):
        return None
