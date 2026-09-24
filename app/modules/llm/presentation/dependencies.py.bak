"""llm DI container"""
from __future__ import annotations
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.modules.llm.application.use_case import LLMUseCase
from app.modules.llm.infrastructure.caches import RedisLLMCache
from app.modules.llm.infrastructure.conversation_repository import (
    ConversationRepository,
)
from app.modules.llm.infrastructure.message_repository import (
    MessageRepository,
)
from app.modules.llm.infrastructure.model_repository import (
    ModelRepository,
)
from app.modules.llm.infrastructure.provider_repository import (
    ProviderRepository,
)
from app.modules.llm.infrastructure.services import (
    DefaultProviderRegistry, NoopEventBus, RedisRateLimiter,
)
from app.modules.llm.infrastructure.usage_log_repository import (
    UsageLogRepository,
)

_registry: DefaultProviderRegistry | None = None


def _get_registry() -> DefaultProviderRegistry:
    global _registry
    if _registry is None:
        _registry = DefaultProviderRegistry()
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


async def _get_idempotency() -> Any:
    try:
        from app.core.idempotency import get_idempotency_store
        return await get_idempotency_store()
    except Exception:
        return _NoopIdempotency()


async def get_llm_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LLMUseCase:
    redis = await _get_redis()
    bus = await _get_event_bus()
    idem = await _get_idempotency()
    rate_limiter = (
        RedisRateLimiter(redis) if redis else _NoopRateLimiter()
    )
    cache = RedisLLMCache(redis) if redis else _NoopCache()
    return LLMUseCase(
        provider_repo=ProviderRepository(session),
        model_repo=ModelRepository(session),
        conversation_repo=ConversationRepository(session),
        message_repo=MessageRepository(session),
        usage_repo=UsageLogRepository(session),
        registry=_get_registry(),
        rate_limiter=rate_limiter,
        cache=cache,
        event_bus=bus,
        idempotency=idem,
    )


class _NoopCache:
    async def get(self, key: str) -> Any | None:
        return None

    async def set(
        self, key: str, value: Any, ttl: int = 3600,
    ) -> bool:
        return False

    async def invalidate(self, key: str) -> bool:
        return False


class _NoopRateLimiter:
    async def check(
        self, tenant_id: Any, user_id: Any, cost: int,
    ) -> bool:
        return True

    async def increment(
        self, tenant_id: Any, user_id: Any, cost: int,
    ) -> None:
        return None


class _NoopIdempotency:
    async def check_or_lock(
        self, key: str, scope: str, payload: dict,
    ) -> dict | None:
        return None

    async def complete(
        self, key: str, scope: str,
        status: int, body: dict,
    ) -> None:
        return None
