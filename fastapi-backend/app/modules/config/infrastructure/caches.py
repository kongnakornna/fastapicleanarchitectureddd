"""
Infrastructure Caches — cache ของ config
RedisConfigCache: TTL 300s, tombstone, never-raise
"""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from ..application.interfaces import IConfigCache
from ..domain.entities import ConfigEntry

# TTL ของ cache (วินาที)
DEFAULT_TTL = 300
# ค่า tombstone — ใช้ mark ว่าถูกลบ
TOMBSTONE = "__TOMBSTONE__"


class RedisConfigCache(IConfigCache):
    """
    Redis Config Cache — cache config ที่ Redis
    - TTL 300 วินาที
    - Tombstone สำหรับ invalidate
    - Never raise (cache failure ไม่ทำให้ระบบพัง)
    """

    def __init__(self, redis: Any, ttl: int = DEFAULT_TTL) -> None:
        self.redis = redis
        self.ttl = ttl

    async def get(self, key: str) -> ConfigEntry | None:
        """
        ดึงจาก cache — คืน None หากไม่พบหรือ error
        Never raise
        """
        try:
            raw = await self.redis.get(key)
            if raw is None:
                return None
            data = json.loads(raw)
            if data.get("__tombstone__"):
                return None
            return ConfigEntry(
                key=data["key"],
                value=data["value"],
                value_type=data.get("value_type", "string"),
                scope=data.get("scope", "TENANT"),
                scope_id=data.get("scope_id", ""),
                is_secret=data.get("is_secret", False),
                description=data.get("description", ""),
            )
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Config cache get failed for {key} — fallback to repo"
            )
            return None

    async def insert(self, key: str, entry: ConfigEntry) -> None:
        """
        ใส่เข้า cache พร้อม TTL — Never raise
        """
        try:
            payload = {
                "key": entry.key,
                "value": entry.value,
                "value_type": entry.value_type,
                "scope": entry.scope,
                "scope_id": entry.scope_id,
                "is_secret": entry.is_secret,
                "description": entry.description,
            }
            await self.redis.setex(key, self.ttl, json.dumps(payload))
        except Exception as e:
            logger.opt(exception=e).warning(f"Config cache insert failed for {key}")

    async def invalidate(self, key: str) -> None:
        """
        Invalidate cache — ลบ key และใส่ tombstone ชั่วคราว — Never raise
        """
        try:
            await self.redis.delete(key)
            # tombstone สั้น ๆ กัน stale read ระหว่าง propagate
            await self.redis.setex(key, 5, json.dumps({"__tombstone__": True}))
        except Exception as e:
            logger.opt(exception=e).warning(f"Config cache invalidate failed for {key}")
