from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import redis
from loguru import logger


@dataclass
class QueueMessage:
    id: str
    topic: str
    payload: dict[str, Any]
    created_at: float
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    error: str = ""


class RedisQueue:
    """Redis-backed queue with delayed messages and dead letter queue.

    Translated from Go: internal/modules/queue/manager.go
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        topic: str,
        max_retries: int = 3,
    ):
        self._redis = redis_client
        self._topic = topic
        self._max_retries = max_retries
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._running = False

        self._queue_key = f"queue:{topic}:pending"
        self._processing_key = f"queue:{topic}:processing"
        self._dlq_key = f"queue:{topic}:dead_letter"
        self._stats_key = f"queue:{topic}:stats"

    def register_handler(self, topic: str, handler: Callable[..., Any]) -> None:
        self._handlers[topic] = handler

    def publish(self, topic: str, payload: dict[str, Any]) -> str:
        msg_id = str(uuid.uuid4())
        msg_data = json.dumps({
            "id": msg_id,
            "topic": topic,
            "payload": payload,
            "created_at": time.time(),
            "retry_count": 0,
            "max_retries": self._max_retries,
            "status": "pending",
        })
        self._redis.lpush(self._queue_key, msg_data)
        self._redis.hincrby(self._stats_key, "published", 1)
        logger.debug(f"Message published: topic={topic}, id={msg_id}")
        return msg_id

    def consume(self, timeout: int = 5) -> QueueMessage | None:
        result = self._redis.brpop(self._queue_key, timeout=timeout)
        if result is None:
            return None

        _queue_name, data = result
        msg_dict = json.loads(data)
        msg = QueueMessage(
            id=msg_dict["id"],
            topic=msg_dict["topic"],
            payload=msg_dict["payload"],
            created_at=msg_dict["created_at"],
            retry_count=msg_dict.get("retry_count", 0),
            max_retries=msg_dict.get("max_retries", self._max_retries),
            status="processing",
        )

        self._redis.lpush(self._processing_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": msg.status,
        }))

        return msg

    def complete(self, msg_id: str) -> None:
        items = self._redis.lrange(self._processing_key, 0, -1)
        for item in items:
            data = json.loads(item)
            if data["id"] == msg_id:
                self._redis.lrem(self._processing_key, 1, item)
                break
        self._redis.hincrby(self._stats_key, "completed", 1)

    def retry(self, msg: QueueMessage) -> None:
        msg.retry_count += 1
        if msg.retry_count >= msg.max_retries:
            self._move_to_dlq(msg)
            return

        self._redis.lpush(self._queue_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": "pending",
        }))
        self._redis.hincrby(self._stats_key, "retried", 1)

    def _move_to_dlq(self, msg: QueueMessage) -> None:
        msg.status = "failed"
        self._redis.lpush(self._dlq_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": msg.status,
            "error": msg.error,
        }))
        self._redis.hincrby(self._stats_key, "dead_letter", 1)
        logger.warning(f"Message moved to DLQ: topic={msg.topic}, id={msg.id}")

    def get_stats(self) -> dict[str, int]:
        stats = self._redis.hgetall(self._stats_key)
        return {k.decode(): int(v.decode()) for k, v in stats.items()}

    def get_dlq_messages(self, limit: int = 10) -> list[dict[str, Any]]:
        items = self._redis.lrange(self._dlq_key, 0, limit - 1)
        return [json.loads(item) for item in items]

    def clear_dlq(self) -> int:
        return self._redis.delete(self._dlq_key)

    def process_messages(self) -> None:
        self._running = True
        while self._running:
            msg = self.consume(timeout=1)
            if msg is None:
                continue

            handler = self._handlers.get(msg.topic) or self._handlers.get("*")
            if handler:
                try:
                    handler(msg)
                    self.complete(msg.id)
                except Exception as e:
                    msg.error = str(e)
                    self.retry(msg)
                    logger.error(f"Message processing failed: {e}")
            else:
                logger.warning(f"No handler for topic: {msg.topic}")
                self.complete(msg.id)

    def stop(self) -> None:
        self._running = False
