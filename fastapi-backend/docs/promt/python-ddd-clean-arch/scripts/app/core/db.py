"""TH: Async session + RLS | EN: Async session + RLS"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.context import RequestContext, get_context

log = structlog.get_logger()
_settings = get_settings()

engine: AsyncEngine = create_async_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    echo=_settings.db_echo,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session(
    ctx: RequestContext = None,  # type: ignore[assignment]
) -> AsyncIterator[AsyncSession]:
    """TH: 1 request = 1 session + set RLS | EN: 1 request = 1 session + set RLS"""
    if ctx is None:
        from fastapi import Depends  # noqa: PLC0415
        ctx = await get_context()

    async with SessionLocal() as session:
        # TH: ตั้งค่า RLS tenant ปัจจุบัน | EN: set current tenant for RLS
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(ctx.tenant_id)},
        )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """TH: ปิด engine ตอน shutdown | EN: dispose on shutdown"""
    await engine.dispose()