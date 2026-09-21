"""
Presentation Dependencies — DI provider ของ config
จัดเตรียม use_cases พร้อม dependency ครบ
"""

from __future__ import annotations

from core.infrastructure.database import get_session
from core.infrastructure.events import get_event_publisher
from core.infrastructure.redis import get_redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import ConfigUseCases
from ..infrastructure.caches import RedisConfigCache
from ..infrastructure.repositories import PostgresConfigRepository
from ..infrastructure.services import FernetCipher


async def get_secret_cipher() -> FernetCipher:
    """
    สร้าง FernetCipher จาก settings
    (สมมติว่า settings.CONFIG_FERNET_KEY เป็น bytes)
    """
    from core.config.settings import settings

    return FernetCipher(key=settings.CONFIG_FERNET_KEY)


async def get_config_use_cases(
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis),
    cipher: FernetCipher = Depends(get_secret_cipher),
    events=Depends(get_event_publisher),
) -> ConfigUseCases:
    """
    DI provider — สร้าง ConfigUseCases พร้อม dependency ครบ
    tenant_id มาจาก context (ไม่ hardcode)
    """
    repo = PostgresConfigRepository(session=session)
    cache = RedisConfigCache(redis=redis)
    return ConfigUseCases(
        repo=repo,
        cache=cache,
        cipher=cipher,
        events=events,
    )


__all__ = ["get_config_use_cases", "get_secret_cipher"]
