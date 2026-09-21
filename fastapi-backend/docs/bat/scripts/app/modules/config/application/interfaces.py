"""
Application Interfaces — สัญญาของ repository, cache, cipher
ใช้ Protocol เพื่อให้ infra นำไป implement
"""

from __future__ import annotations

from typing import Protocol

from ..domain.entities import ConfigEntry


class IConfigRepository(Protocol):
    """Config repository interface — สัญญาของที่เก็บ config"""

    async def get(self, key: str, scope: str, scope_id: str) -> ConfigEntry | None:
        """ดึง config ตาม key + scope + scope_id"""
        ...

    async def get_effective(
        self, key: str, tenant_id: str, user_id: str | None
    ) -> ConfigEntry | None:
        """
        ดึง config ที่มีผลจริง (override 3 ระดับ)
        ลำดับ: USER > TENANT > GLOBAL
        """
        ...

    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """บันทึก config entry"""
        ...

    async def list(self, scope: str, scope_id: str) -> list[ConfigEntry]:
        """แสดงรายการ config ตาม scope"""
        ...

    async def delete(self, key: str, scope: str, scope_id: str) -> bool:
        """ลบ config entry"""
        ...


class IConfigCache(Protocol):
    """Config cache interface — สัญญาของ cache"""

    async def get(self, key: str) -> ConfigEntry | None:
        """ดึงจาก cache"""
        ...

    async def insert(self, key: str, entry: ConfigEntry) -> None:
        """ใส่เข้า cache"""
        ...

    async def invalidate(self, key: str) -> None:
        """ลบออกจาก cache (tombstone)"""
        ...


class ISecretCipher(Protocol):
    """Secret cipher interface — สัญญาของการเข้ารหัส secret"""

    def encrypt(self, plain: str) -> str:
        """เข้ารหัส plaintext → ciphertext"""
        ...

    def decrypt(self, cipher: str) -> str:
        """ถอดรหัส ciphertext → plaintext"""
        ...


class IEventPublisher(Protocol):
    """Event publisher interface — สัญญาของการ publish event"""

    async def publish(self, event_name: str, payload: dict) -> None:
        """Publish domain event"""
        ...
