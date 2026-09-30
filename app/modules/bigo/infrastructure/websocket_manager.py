"""WebSocketManager — connection lifecycle + rooms + broadcast + heartbeat"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import structlog

from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry

log = structlog.get_logger()


@dataclass
class WSConnection:
    id: str
    tenant_id: str
    user_id: str | None
    websocket: Any
    rooms: set[str] = field(default_factory=set)
    connected_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "rooms": sorted(self.rooms),
            "connected_at": self.connected_at,
            "last_seen": self.last_seen,
            "uptime_s": round(time.time() - self.connected_at, 1),
        }


class WebSocketManager:
    """TH: จัดการ WS connections + rooms + broadcast + heartbeat"""

    def __init__(
        self,
        metrics: MetricsRegistry | None = None,
        *,
        heartbeat_interval_s: int = 30,
        max_connections_per_tenant: int = 1000,
        send_timeout_s: float = 5.0,
    ) -> None:
        self._metrics = metrics or MetricsRegistry()
        self._lock = asyncio.Lock()
        self._conns: dict[str, WSConnection] = {}
        self._rooms: dict[str, set[str]] = {}
        self._by_tenant: dict[str, set[str]] = {}
        self._heartbeat_interval = heartbeat_interval_s
        self._max_per_tenant = max_connections_per_tenant
        self._send_timeout = send_timeout_s
        self._heartbeat_task: asyncio.Task | None = None

    async def connect(
        self,
        websocket: Any,
        *,
        tenant_id: str,
        user_id: str | None = None,
        rooms: set[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WSConnection:
        conn_id = str(uuid.uuid4())
        async with self._lock:
            tenant_conns = self._by_tenant.setdefault(tenant_id, set())
            if len(tenant_conns) >= self._max_per_tenant:
                self._metrics.incr("bigo.ws.reject", reason="tenant_limit")
                raise RuntimeError(
                    f"tenant {tenant_id} reached max connections ({self._max_per_tenant})"
                )
            conn = WSConnection(
                id=conn_id, tenant_id=tenant_id, user_id=user_id,
                websocket=websocket,
                rooms=set(rooms or {f"tenant:{tenant_id}"}),
                metadata=metadata or {},
            )
            self._conns[conn_id] = conn
            tenant_conns.add(conn_id)
            for room in conn.rooms:
                self._rooms.setdefault(room, set()).add(conn_id)
        self._metrics.incr("bigo.ws.connect", tenant=tenant_id)
        self._metrics.gauge("bigo.ws.connections", len(self._conns))
        log.info("ws.connect", conn_id=conn_id, tenant=tenant_id)
        return conn

    async def disconnect(self, conn_id: str) -> None:
        async with self._lock:
            conn = self._conns.pop(conn_id, None)
            if conn is None:
                return
            for room in conn.rooms:
                members = self._rooms.get(room)
                if members:
                    members.discard(conn_id)
                    if not members:
                        self._rooms.pop(room, None)
            tenant_conns = self._by_tenant.get(conn.tenant_id)
            if tenant_conns:
                tenant_conns.discard(conn_id)
                if not tenant_conns:
                    self._by_tenant.pop(conn.tenant_id, None)
        self._metrics.incr("bigo.ws.disconnect", tenant=conn.tenant_id)
        self._metrics.gauge("bigo.ws.connections", len(self._conns))
        log.info("ws.disconnect", conn_id=conn_id)

    async def join(self, conn_id: str, room: str) -> bool:
        async with self._lock:
            conn = self._conns.get(conn_id)
            if conn is None:
                return False
            conn.rooms.add(room)
            self._rooms.setdefault(room, set()).add(conn_id)
        return True

    async def leave(self, conn_id: str, room: str) -> bool:
        async with self._lock:
            conn = self._conns.get(conn_id)
            if conn is None:
                return False
            conn.rooms.discard(room)
            members = self._rooms.get(room)
            if members:
                members.discard(conn_id)
                if not members:
                    self._rooms.pop(room, None)
        return True

    async def send_personal(self, conn_id: str, message: dict[str, Any]) -> bool:
        conn = self._conns.get(conn_id)
        if conn is None:
            return False
        return await self._safe_send(conn, message)

    async def broadcast(
        self,
        message: dict[str, Any],
        *,
        room: str | None = None,
        tenant_id: str | None = None,
        exclude: set[str] | None = None,
    ) -> int:
        exclude = exclude or set()
        async with self._lock:
            if room is not None:
                targets = [self._conns[cid] for cid in self._rooms.get(room, set())
                           if cid in self._conns and cid not in exclude]
            elif tenant_id is not None:
                targets = [self._conns[cid] for cid in self._by_tenant.get(tenant_id, set())
                           if cid in self._conns and cid not in exclude]
            else:
                targets = [c for cid, c in self._conns.items() if cid not in exclude]
        if not targets:
            return 0
        results = await asyncio.gather(
            *(self._safe_send(c, message) for c in targets),
            return_exceptions=True,
        )
        sent = sum(1 for r in results if r is True)
        self._metrics.incr("bigo.ws.broadcast", sent=sent, total=len(targets))
        return sent

    async def _safe_send(self, conn: WSConnection, message: dict[str, Any]) -> bool:
        try:
            payload = json.dumps(message, default=str)
            await asyncio.wait_for(
                conn.websocket.send_text(payload),
                timeout=self._send_timeout,
            )
            conn.last_seen = time.time()
            self._metrics.incr("bigo.ws.sent")
            return True
        except Exception as exc:
            self._metrics.incr("bigo.ws.send_failed")
            log.warning("ws.send_failed", conn_id=conn.id, err=str(exc))
            return False

    async def start_heartbeat(self) -> None:
        if self._heartbeat_task is not None:
            return
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop_heartbeat(self) -> None:
        if self._heartbeat_task is None:
            return
        self._heartbeat_task.cancel()
        try:
            await self._heartbeat_task
        except asyncio.CancelledError:
            pass
        self._heartbeat_task = None

    async def _heartbeat_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                await self.broadcast({"type": "ping", "ts": time.time()})
                await self._sweep_stale()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("ws.heartbeat.error", err=str(exc))

    async def _sweep_stale(self) -> None:
        cutoff = time.time() - self._heartbeat_interval * 3
        async with self._lock:
            stale = [cid for cid, c in self._conns.items() if c.last_seen < cutoff]
        for cid in stale:
            self._metrics.incr("bigo.ws.sweep")
            await self.disconnect(cid)

    def list_connections(
        self, *, tenant_id: str | None = None, room: str | None = None,
    ) -> list[dict[str, Any]]:
        if tenant_id is not None:
            ids = self._by_tenant.get(tenant_id, set())
        elif room is not None:
            ids = self._rooms.get(room, set())
        else:
            ids = set(self._conns)
        return [self._conns[i].to_dict() for i in ids if i in self._conns]

    def stats(self) -> dict[str, Any]:
        return {
            "connections": len(self._conns),
            "rooms": {r: len(m) for r, m in self._rooms.items()},
            "tenants": {t: len(m) for t, m in self._by_tenant.items()},
            "heartbeat_interval_s": self._heartbeat_interval,
            "max_per_tenant": self._max_per_tenant,
        }
