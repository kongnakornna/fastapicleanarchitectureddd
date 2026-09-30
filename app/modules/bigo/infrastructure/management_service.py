"""ManagementService — admin ops: config, cache, ws, pipeline control"""
from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

import structlog

from app.modules.bigo.infrastructure.pipeline import BigOPipeline
from app.modules.bigo.infrastructure.redis_cache import RedisCache
from app.modules.bigo.infrastructure.websocket_manager import WebSocketManager

log = structlog.get_logger()


class ManagementService:
    """TH: บริการจัดการ (admin)"""

    def __init__(
        self,
        pipeline: BigOPipeline,
        cache: RedisCache,
        ws_manager: WebSocketManager,
    ) -> None:
        self._pipeline = pipeline
        self._cache = cache
        self._ws = ws_manager

    def get_config(self) -> dict[str, Any]:
        cfg = self._pipeline._config
        data = asdict(cfg)
        data["kafka_backoff"] = list(cfg.kafka_backoff)
        data["sample_sizes"] = list(cfg.sample_sizes)
        return data

    def update_config(self, **changes: Any) -> dict[str, Any]:
        cfg = self._pipeline._config
        allowed = set(cfg.__dataclass_fields__.keys())
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        new_cfg = replace(cfg, **changes)
        self._pipeline._config = new_cfg
        log.info("mgmt.config.updated", changes=list(changes.keys()))
        return self.get_config()

    async def cache_stats(self) -> dict[str, Any]:
        return self._cache.stats()

    async def cache_health(self) -> dict[str, Any]:
        return await self._cache.health()

    async def cache_clear(self, prefix: str | None = None) -> dict[str, Any]:
        if prefix:
            n = await self._cache.delete_prefix(prefix)
            return {"deleted": n, "prefix": prefix}
        n = await self._cache.delete_prefix(f"{self._cache._ns}:")
        return {"deleted": n, "prefix": f"{self._cache._ns}:"}

    def ws_stats(self) -> dict[str, Any]:
        return self._ws.stats()

    def ws_list(
        self, *, tenant_id: str | None = None, room: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._ws.list_connections(tenant_id=tenant_id, room=room)

    async def ws_broadcast(
        self,
        message: dict[str, Any],
        *,
        room: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        n = await self._ws.broadcast(message, room=room, tenant_id=tenant_id)
        return {"sent": n, "room": room, "tenant_id": tenant_id}

    async def ws_kick(self, conn_id: str) -> dict[str, Any]:
        await self._ws.send_personal(
            conn_id, {"type": "kicked", "reason": "admin_action"},
        )
        await self._ws.disconnect(conn_id)
        return {"conn_id": conn_id, "kicked": True}

    def pipeline_metrics(self) -> dict[str, Any]:
        return self._pipeline.metrics_snapshot()

    def pipeline_memory(self) -> dict[str, Any]:
        return self._pipeline.memory.stats()

    def pipeline_policies(self) -> dict[str, Any]:
        return {
            k: {
                "cls": v.cls.value,
                "max_n": v.max_n,
                "warn_ratio": v.warn_ratio,
                "critical_ratio": v.critical_ratio,
                "partition": v.partition.value,
            }
            for k, v in self._pipeline.monitor.policies().items()
        }

    def pipeline_reset_metrics(self) -> dict[str, Any]:
        self._pipeline._metrics.reset()
        return {"reset": True}

    async def health(self) -> dict[str, Any]:
        cache_h = await self._cache.health()
        mem = self._pipeline.memory.stats()
        return {
            "status": "ok" if cache_h.get("connected") else "degraded",
            "cache": cache_h,
            "memory": mem,
            "ws": {"connections": self._ws.stats()["connections"]},
        }
