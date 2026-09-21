"""
Infrastructure Services — บริการโครงสร้างพื้นฐาน
FernetCipher: เข้ารหัส/ถอดรหัส secret
ConfigPubSub: hot-reload ผ่าน Redis Pub/Sub
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from core.domain.exceptions import DomainError
from cryptography.fernet import Fernet, InvalidToken
from loguru import logger

from ..application.interfaces import ISecretCipher

# ชื่อ channel สำหรับ pub/sub
CONFIG_CHANNEL = "config:changed"


class FernetCipher(ISecretCipher):
    """
    Fernet cipher — เข้ารหัส/ถอดรหัส secret ด้วย Fernet (AES-128-CBC + HMAC)
    """

    def __init__(self, key: bytes) -> None:
        """
        Args:
            key: Fernet key (base64-encoded 32 bytes)
        """
        self.fernet = Fernet(key)

    def encrypt(self, plain: str) -> str:
        """เข้ารหัส plaintext → ciphertext (string)"""
        try:
            return self.fernet.encrypt(plain.encode()).decode()
        except Exception as e:
            raise DomainError(f"Encryption failed: {e}") from e

    def decrypt(self, cipher: str) -> str:
        """ถอดรหัส ciphertext → plaintext"""
        try:
            return self.fernet.decrypt(cipher.encode()).decode()
        except InvalidToken as e:
            raise DomainError("Decryption failed: invalid token") from e
        except Exception as e:
            raise DomainError(f"Decryption failed: {e}") from e

    @staticmethod
    def generate_key() -> bytes:
        """สร้าง Fernet key ใหม่"""
        return Fernet.generate_key()


class ConfigPubSub:
    """
    Config hot-reload ผ่าน Redis Pub/Sub
    เมื่อมี ConfigChanged event → callback ถูกเรียกเพื่อ reload
    """

    def __init__(self, redis: Any) -> None:
        self.redis = redis
        self._task: asyncio.Task | None = None

    async def publish(self, key: str, scope: str = "TENANT") -> None:
        """Publish ConfigChanged event"""
        try:
            payload = json.dumps({"key": key, "scope": scope})
            await self.redis.publish(CONFIG_CHANNEL, payload)
        except Exception as e:
            logger.opt(exception=e).warning(f"Config pub/sub publish failed for {key}")

    async def subscribe(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        """
        Subscribe และเรียก callback เมื่อมี ConfigChanged
        รันเป็น background task
        """
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(CONFIG_CHANNEL)

            async def _listener() -> None:
                try:
                    async for message in pubsub.listen():
                        if message.get("type") != "message":
                            continue
                        try:
                            data = json.loads(message["data"])
                            await callback(data)
                        except Exception as e:
                            logger.opt(exception=e).error(
                                "Config subscriber callback failed"
                            )
                except asyncio.CancelledError:
                    logger.info("Config subscriber cancelled")
                    raise
                except Exception as e:
                    logger.opt(exception=e).error("Config subscriber crashed")

            self._task = asyncio.create_task(_listener())
        except Exception as e:
            logger.opt(exception=e).error("Config subscribe failed")

    async def stop(self) -> None:
        """หยุด listener"""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
