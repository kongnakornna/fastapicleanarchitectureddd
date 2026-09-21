"""123Abc dependencies — FastAPI DI container"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    Create123AbcUseCase,
    Delete123AbcUseCase,
    Get123AbcUseCase,
    List123AbcUseCase,
    Update123AbcUseCase,
)
from ..infrastructure.caches import Redis123AbcCache
from ..infrastructure.repositories import SQLAlchemy123AbcRepository


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


def get_123abc_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemy123AbcRepository:
    return SQLAlchemy123AbcRepository(session=session)


def get_123abc_cache() -> Redis123AbcCache:
    return Redis123AbcCache(redis_client=get_redis())


async def get_create_uc(
    repo: Annotated[SQLAlchemy123AbcRepository, Depends(get_123abc_repo)],
    cache: Annotated[Redis123AbcCache, Depends(get_123abc_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    idem: Annotated[object, Depends(get_idempotency_store)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Create123AbcUseCase:
    return Create123AbcUseCase(
        repo=repo, cache=cache, event_bus=bus, idempotency=idem, ctx=ctx,
    )


async def get_get_uc(
    repo: Annotated[SQLAlchemy123AbcRepository, Depends(get_123abc_repo)],
    cache: Annotated[Redis123AbcCache, Depends(get_123abc_cache)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Get123AbcUseCase:
    return Get123AbcUseCase(repo=repo, cache=cache, ctx=ctx)


async def get_list_uc(
    repo: Annotated[SQLAlchemy123AbcRepository, Depends(get_123abc_repo)],
    ctx: Annotated[dict, Depends(get_context)],
) -> List123AbcUseCase:
    return List123AbcUseCase(repo=repo, ctx=ctx)


async def get_update_uc(
    repo: Annotated[SQLAlchemy123AbcRepository, Depends(get_123abc_repo)],
    cache: Annotated[Redis123AbcCache, Depends(get_123abc_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Update123AbcUseCase:
    return Update123AbcUseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )


async def get_delete_uc(
    repo: Annotated[SQLAlchemy123AbcRepository, Depends(get_123abc_repo)],
    cache: Annotated[Redis123AbcCache, Depends(get_123abc_cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Delete123AbcUseCase:
    return Delete123AbcUseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )