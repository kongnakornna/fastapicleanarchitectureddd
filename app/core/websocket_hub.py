"""
app/core/websocket_hub.py — Global WebSocket connection manager

TH: จัดการ WebSocket connections + rooms + topics
EN: Manage WebSocket connections + rooms + topics

ใช้ร่วมกันทุก module ที่ต้องการ broadcast แบบ real-time (iot, notification, ...)
"""
from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any

import structlog
from fastapi import WebSocket

log = structlog.get_logger()


class WebSocketManager:
    """TH: WebSocket hub | EN: WebSocket hub"""

    def __init__(self) -> None:
        # room → set[WebSocket]
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        # topic → set[WebSocket]
        self._topics: dict[str, set[WebSocket]] = defaultdict(set)
        # WebSocket → set[room]
        self._ws_rooms: dict[WebSocket, set[str]] = defaultdict(set)
        # WebSocket → set[topic]
        self._ws_topics: dict[WebSocket, set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    # ═══════════════════════════════════════════════════════════
    #  CONNECT / DISCONNECT
    # ═══════════════════════════════════════════════════════════
    async def connect(self, websocket: WebSocket, room: str = "default") -> None:
        """TH: accept + join room | EN: accept + join room"""
        await websocket.accept()
        async with self._lock:
            self._rooms[room].add(websocket)
            self._ws_rooms[websocket].add(room)
        log.info("ws.connected", room=room,
                 total=self.get_total_connections())

    async def disconnect(self, websocket: WebSocket, room: str = "") -> None:
        """TH: ออกจาก room + ปิด | EN: leave room + close"""
        async with self._lock:
            rooms = [room] if room else list(self._ws_rooms.get(websocket, []))
            for r in rooms:
                if r in self._rooms:
                    self._rooms[r].discard(websocket)
                    if not self._rooms[r]:
                        del self._rooms[r]

            for t in list(self._ws_topics.get(websocket, [])):
                self._topics[t].discard(websocket)
                if not self._topics[t]:
                    del self._topics[t]

            self._ws_rooms.pop(websocket, None)
            self._ws_topics.pop(websocket, None)

        log.info("ws.disconnected",
                 total=self.get_total_connections())

    # ═══════════════════════════════════════════════════════════
    #  SUBSCRIBE / UNSUBSCRIBE
    # ═══════════════════════════════════════════════════════════
    async def subscribe(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            self._topics[topic].add(websocket)
            self._ws_topics[websocket].add(topic)

    async def unsubscribe(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            if topic in self._topics:
                self._topics[topic].discard(websocket)
                if not self._topics[topic]:
                    del self._topics[topic]
            if websocket in self._ws_topics:
                self._ws_topics[websocket].discard(topic)

    # ═══════════════════════════════════════════════════════════
    #  BROADCAST
    # ═══════════════════════════════════════════════════════════
    async def broadcast_to_room(
        self, room: str, event: str, payload: dict[str, Any],
    ) -> int:
        """TH: broadcast ไปยังทุก client ใน room | EN: broadcast to room"""
        if room not in self._rooms:
            return 0
        msg = json.dumps({"event": event, "data": payload}, default=str)
        return await self._broadcast(list(self._rooms[room]), msg)

    async def broadcast_to_topic(
        self, topic: str, payload: dict[str, Any],
    ) -> int:
        """TH: broadcast ตาม topic | EN: broadcast by topic"""
        if topic not in self._topics:
            return 0
        msg = json.dumps({"topic": topic, "data": payload}, default=str)
        return await self._broadcast(list(self._topics[topic]), msg)

    async def _broadcast(self, sockets: list[WebSocket], msg: str) -> int:
        if not sockets:
            return 0
        results = await asyncio.gather(
            *(self._safe_send(ws, msg) for ws in sockets),
            return_exceptions=True,
        )
        return sum(1 for r in results if r is True)

    @staticmethod
    async def _safe_send(ws: WebSocket, msg: str) -> bool:
        try:
            await ws.send_text(msg)
            return True
        except Exception as exc:
            log.warning("ws.send_failed", err=str(exc))
            return False

    # ═══════════════════════════════════════════════════════════
    #  STATS
    # ═══════════════════════════════════════════════════════════
    def get_rooms(self) -> dict[str, int]:
        """TH: จำนวน clients ต่อ room | EN: clients count per room"""
        return {r: len(s) for r, s in self._rooms.items()}

    def get_topics(self) -> dict[str, int]:
        return {t: len(s) for t, s in self._topics.items()}

    def get_total_connections(self) -> int:
        """TH: จำนวน connection ทั้งหมด | EN: total connections"""
        return len(self._ws_rooms)

    def get_clients_in_room(self, room: str) -> int:
        return len(self._rooms.get(room, set()))


# ═══════════════════════════════════════════════════════════════
#  SINGLETON
# ═══════════════════════════════════════════════════════════════
ws_manager = WebSocketManager()