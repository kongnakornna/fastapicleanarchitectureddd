"""Inventory dependencies — FastAPI DI container"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    CreateInventoryUseCase,
    DeleteInventoryUseCase,
    GetInventoryUseCase,
    ListInventoryUseCase,
    UpdateInventoryUseCase,
)
from ..infrastructure.caches import RedisInventoryCache
from ..infrastructure.repositories import SQLAlchemyInventoryRepository


try:
    from app.core.db import get_session  # type: ignore
except Exception:
    async def get_session():  # type: ignore
        raise RuntimeError("app.core.db.get_session not configured")

try:
    from app.core.context import get_context  # type: ignore
except Exception:
    def get_context():  # type: ignore
        return {"tenant_id": "00000000-0000-0000-0000-000000000001"}

try:
    from app.core.events import get_event_bus  # type: ignore
except Exception:
    class _NullBus:
        async def publish(self, event): return None
    def get_event_bus():  # type: ignore
        return _NullBus()

try:
    from app.core.idempotency import get_idempotency_store  # type: ignore
except Exception:
    class _NullIdem:
        async def check_or_lock(self, **_kw): return None
        async def complete(self, **_kw): return None
    def get_idempotency_store():  # type: ignore
        return _NullIdem()

try:
    from app.core.redis import get_redis  # type: ignore
except Exception:
    def get_redis():  # type: ignore
        return None


def get_inventory_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyInventoryRepository:
    return SQLAlchemyInventoryRepository(session=session)


def get_inventory_cache() -> RedisInventoryCache:
    return RedisInventoryCache(redis_client=get_redis())


async def get_create_uc(
    repo: Annotated[SQLAlchemyInventoryRepository, Depends(get_inventory_repo)],
    cache: Annotated[RedisInventoryCache, Depends(get_inventory_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    idem: Annotated[object, Depends(get_idempotency_store)],
    ctx: Annotated[dict, Depends(get_context)],
) -> CreateInventoryUseCase:
    return CreateInventoryUseCase(
        repo=repo, cache=cache, event_bus=bus, idempotency=idem, ctx=ctx,
    )


async def get_get_uc(
    repo: Annotated[SQLAlchemyInventoryRepository, Depends(get_inventory_repo)],
    cache: Annotated[RedisInventoryCache, Depends(get_inventory_cache)],
    ctx: Annotated[dict, Depends(get_context)],
) -> GetInventoryUseCase:
    return GetInventoryUseCase(repo=repo, cache=cache, ctx=ctx)


async def get_list_uc(
    repo: Annotated[SQLAlchemyInventoryRepository, Depends(get_inventory_repo)],
    ctx: Annotated[dict, Depends(get_context)],
) -> ListInventoryUseCase:
    return ListInventoryUseCase(repo=repo, ctx=ctx)


async def get_update_uc(
    repo: Annotated[SQLAlchemyInventoryRepository, Depends(get_inventory_repo)],
    cache: Annotated[RedisInventoryCache, Depends(get_inventory_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> UpdateInventoryUseCase:
    return UpdateInventoryUseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )


async def get_delete_uc(
    repo: Annotated[SQLAlchemyInventoryRepository, Depends(get_inventory_repo)],
    cache: Annotated[RedisInventoryCache, Depends(get_inventory_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> DeleteInventoryUseCase:
    return DeleteInventoryUseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )