# app/core/kafka.py
"""TH: AIOKafka producer singleton | EN: AIOKafka producer singleton"""
from __future__ import annotations

import json
from typing import Any

from aiokafka import AIOKafkaProducer

from app.core.config import get_settings

_settings = get_settings()
_producer: AIOKafkaProducer | None = None


def _serializer(value: Any) -> bytes:
    return json.dumps(value, default=str).encode()


async def get_producer() -> AIOKafkaProducer:
    """TH: lazy init producer | EN: lazy init producer"""
    global _producer  # noqa: PLW0603
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=_settings.kafka_bootstrap,
            value_serializer=_serializer,
            acks="all",
            enable_idempotence=True,
        )
        await _producer.start()
    return _producer


async def stop_producer() -> None:
    global _producer  # noqa: PLW0603
    if _producer is not None:
        await _producer.stop()
        _producer = None