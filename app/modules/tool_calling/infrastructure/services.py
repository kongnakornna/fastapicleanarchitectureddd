"""tool_calling services — clients · registry · event bus"""
from __future__ import annotations
import asyncio
import json
import uuid
from typing import Any

import structlog

from app.modules.tool_calling.application.interfaces import (
    EventBus, ToolClient, ToolClientRegistry,
)
from app.modules.tool_calling.domain.exceptions import (
    ToolExecutionError,
)

log = structlog.get_logger()


class HttpToolClient:
    """TH: HTTP tool client | EN: HTTP tool client"""
    kind = "http"

    async def invoke(
        self, *, spec: Any, args: dict[str, Any],
        secrets: dict[str, str], timeout: int,
    ) -> Any:
        try:
            import httpx
        except ImportError as exc:
            raise ToolExecutionError("httpx not installed") from exc

        config = {}
        try:
            config = json.loads(spec.parameters_json or "{}")
        except Exception:
            config = {}

        url = config.get("url", "")
        method = config.get("method", "POST").upper()
        headers = config.get("headers", {}) or {}
        headers.update({k: v for k, v in secrets.items()})

        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                resp = await client.get(url, params=args, headers=headers)
            else:
                resp = await client.request(
                    method, url, json=args, headers=headers,
                )
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"text": resp.text}


class PythonToolClient:
    """TH: stub — ต้อง register handler เอง | EN: python tool stub"""
    kind = "python"

    def __init__(self, handlers: dict[str, Any] | None = None) -> None:
        self._handlers = handlers or {}

    async def invoke(
        self, *, spec: Any, args: dict[str, Any],
        secrets: dict[str, str], timeout: int,
    ) -> Any:
        handler = self._handlers.get(spec.name)
        if handler is None:
            raise ToolExecutionError(
                f"no python handler for {spec.name}",
            )
        if asyncio.iscoroutinefunction(handler):
            return await handler(**args)
        return handler(**args)


class DefaultToolClientRegistry(ToolClientRegistry):
    def __init__(self) -> None:
        self._clients: dict[str, ToolClient] = {
            "http": HttpToolClient(),
            "openapi": HttpToolClient(),
            "python": PythonToolClient(),
            "sql": PythonToolClient(),
            "shell": PythonToolClient(),
            "mcp": PythonToolClient(),
        }

    def register(self, kind: str, client: ToolClient) -> None:
        self._clients[kind] = client

    def get(self, kind: str) -> ToolClient:
        client = self._clients.get(kind)
        if client is None:
            raise ToolExecutionError(f"unknown tool kind: {kind}")
        return client


class RedisRateLimiter:
    def __init__(self, redis: object) -> None:
        self._redis = redis

    async def check_and_incr(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
        tool_id: uuid.UUID, limit_per_min: int,
    ) -> bool:
        try:
            key = f"tool:rl:{tenant_id}:{user_id}:{tool_id}"
            pipe = self._redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            results = await pipe.execute()
            current = int(results[0])
            return current <= limit_per_min
        except Exception as e:
            log.warning("ratelimit.check_failed", err=str(e))
            return True


class KafkaEventBus(EventBus):
    def __init__(self, producer: object, topic: str = "tool.events") -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: object) -> None:
        try:
            payload = {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            }
            await self._producer.send_and_wait(self._topic, payload)
        except Exception as e:
            log.warning("event.publish_failed", err=str(e))


class NoopEventBus(EventBus):
    async def publish(self, event: object) -> None:
        log.debug("event.noop", type=type(event).__name__)
