"""tool_calling services"""
from __future__ import annotations
import asyncio
import json
from typing import Any

import structlog

from tool_calling.application.interfaces import EventBus, ToolClient, ToolClientRegistry
from tool_calling.domain.exceptions import ToolExecutionError

log = structlog.get_logger()


class HttpToolClient:
    kind = "http"

    async def invoke(self, *, spec, args, secrets, timeout):
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
        headers.update(secrets)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                resp = await client.get(url, params=args, headers=headers)
            else:
                resp = await client.request(method, url, json=args, headers=headers)
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"text": resp.text}


class PythonToolClient:
    kind = "python"

    def __init__(self, handlers: dict[str, Any] | None = None) -> None:
        self._handlers = handlers or {}

    async def invoke(self, *, spec, args, secrets, timeout):
        handler = self._handlers.get(spec.name)
        if handler is None:
            raise ToolExecutionError(f"no python handler for {spec.name}")
        if asyncio.iscoroutinefunction(handler):
            return await handler(**args)
        return handler(**args)


class DefaultToolClientRegistry(ToolClientRegistry):
    def __init__(self) -> None:
        self._clients: dict[str, ToolClient] = {
            "http": HttpToolClient(), "openapi": HttpToolClient(),
            "python": PythonToolClient(), "sql": PythonToolClient(),
            "shell": PythonToolClient(), "mcp": PythonToolClient(),
        }

    def register(self, kind: str, client: ToolClient) -> None:
        self._clients[kind] = client

    def get(self, kind: str) -> ToolClient:
        c = self._clients.get(kind)
        if c is None:
            raise ToolExecutionError(f"unknown tool kind: {kind}")
        return c


class RedisRateLimiter:
    def __init__(self, redis: object) -> None:
        self._redis = redis

    async def check_and_incr(self, tenant_id, user_id, tool_id, limit_per_min):
        try:
            key = f"tool:rl:{tenant_id}:{user_id}:{tool_id}"
            pipe = self._redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            results = await pipe.execute()
            return int(results[0]) <= limit_per_min
        except Exception:
            return True


class NoopEventBus(EventBus):
    async def publish(self, event: object) -> None:
        log.debug("event.noop", type=type(event).__name__)
