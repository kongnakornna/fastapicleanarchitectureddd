"""
Application Use Cases — กรณีการใช้งาน config
ConfigUseCases: จัดการ get/set/list/delete พร้อม cache + secret + event
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from core.application.context import get_context
from core.application.exceptions import StandardException
from core.domain.exceptions import DomainError
from loguru import logger

from ..domain.entities import ConfigEntry
from ..domain.enums import ConfigType
from .exceptions import ConfigException, ConfigKeyNotFoundException
from .interfaces import (
    IConfigCache,
    IConfigRepository,
    IEventPublisher,
    ISecretCipher,
)


class ConfigUseCases:
    """
    Config use cases — กรณีการใช้งาน config

    รองรับ:
    - get_effective: ดึงค่าที่มีผล (override 3 ระดับ)
    - set: ตั้งค่า (encrypt secret, read-back, invalidate cache, publish event)
    - list: แสดงรายการ
    - delete: ลบ
    """

    def __init__(
        self,
        repo: IConfigRepository,
        cache: IConfigCache,
        cipher: ISecretCipher,
        events: IEventPublisher,
        config: Any = None,
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.cipher = cipher
        self.events = events
        self.config = config

    async def get_effective(self, key: str, user_id: str | None = None) -> ConfigEntry:
        """
        Get effective config — ดึงค่าที่มีผลจริง
        ลำดับ override: USER > TENANT > GLOBAL
        """
        try:
            ctx = get_context()
            cache_key = f"{ctx.tenant_id}:{user_id or '-'}:{key}"

            # 1) ลอง cache ก่อน
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            # 2) ดึงจาก repo (มี override ในตัว)
            entry = await self.repo.get_effective(key, ctx.tenant_id, user_id)
            if entry is None:
                raise ConfigKeyNotFoundException(key)

            # 3) ถอดรหัส secret
            if entry.is_secret:
                plain = self.cipher.decrypt(entry.value)
                entry = replace(entry, value=plain)

            # 4) ใส่ cache
            await self.cache.insert(cache_key, entry)
            return entry

        except StandardException:
            raise
        except DomainError as e:
            raise ConfigException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in get_effective config")
            raise ConfigException() from e

    async def set(
        self,
        key: str,
        value: str,
        value_type: str = ConfigType.STRING.value,
        scope: str = "TENANT",
        scope_id: str = "",
        is_secret: bool = False,
        description: str = "",
    ) -> ConfigEntry:
        """
        Set config — ตั้งค่า config
        - หาก is_secret → encrypt ก่อนเก็บ
        - Read-back verify
        - Invalidate cache + publish event
        """
        try:
            # 1) เข้ารหัส secret
            if is_secret:
                value = self.cipher.encrypt(value)

            # 2) สร้าง entity
            entry = ConfigEntry(
                key=key,
                value=value,
                value_type=value_type,
                scope=scope,
                scope_id=scope_id,
                is_secret=is_secret,
                description=description,
            )

            # 3) บันทึก
            entry = await self.repo.save(entry)

            # 4) Read-back verify
            verified = await self.repo.get(key, scope, scope_id)
            if not verified or verified.value != entry.value:
                raise ConfigException("Read-back failed")

            # 5) Invalidate cache
            await self.cache.invalidate(f"{scope_id}:{key}")
            await self.cache.invalidate(f"{scope_id}:-:{key}")

            # 6) Publish event
            await self.events.publish(
                "ConfigChanged",
                {"key": key, "scope": scope, "scope_id": scope_id},
            )

            # 7) Return masked
            return entry.mask()

        except StandardException:
            raise
        except DomainError as e:
            raise ConfigException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in set config")
            raise ConfigException() from e

    async def list(self, scope: str, scope_id: str) -> list[ConfigEntry]:
        """List config — แสดงรายการ config ตาม scope (mask secret)"""
        try:
            entries = await self.repo.list(scope, scope_id)
            return [e.mask() for e in entries]
        except StandardException:
            raise
        except DomainError as e:
            raise ConfigException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in list config")
            raise ConfigException() from e

    async def delete(self, key: str, scope: str, scope_id: str) -> bool:
        """
        Delete config — ลบ config entry
        Invalidate cache + publish event
        """
        try:
            deleted = await self.repo.delete(key, scope, scope_id)
            if deleted:
                await self.cache.invalidate(f"{scope_id}:{key}")
                await self.events.publish(
                    "ConfigDeleted",
                    {"key": key, "scope": scope, "scope_id": scope_id},
                )
            return deleted
        except StandardException:
            raise
        except DomainError as e:
            raise ConfigException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in delete config")
            raise ConfigException() from e
