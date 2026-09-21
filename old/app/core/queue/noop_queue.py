from __future__ import annotations

import uuid
from typing import Any

from loguru import logger


class NoopQueue:
    """No-op fallback queue when Redis is unavailable."""

    def publish(self, topic: str, payload: dict[str, Any]) -> str:
        logger.debug(f"NoopQueue: publish to {topic}")
        return str(uuid.uuid4())

    def consume(self, timeout: int = 5) -> None:
        return None

    def get_stats(self) -> dict[str, int]:
        return {}
