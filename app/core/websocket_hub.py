"""WebSocket hub for real-time IoT data broadcasting.

Translated from Go: internal/modules/websocket/
"""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from starlette.websockets import WebSocket, WebSocketState


class ConnectionManager:
    """Manages WebSocket connections and room-based broadcasting."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._topic_subscriptions: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str = "default") -> None:
        await websocket.accept()
        if room not in self._connections:
            self._connections[room] = set()
        self._connections[room].add(websocket)
        logger.info(f"WebSocket connected to room: {room}")

    async def disconnect(self, websocket: WebSocket, room: str = "default") -> None:
        if room in self._connections:
            self._connections[room].discard(websocket)
            if not self._connections[room]:
                del self._connections[room]
        for topic_subs in self._topic_subscriptions.values():
            topic_subs.discard(websocket)
        logger.info(f"WebSocket disconnected from room: {room}")

    async def subscribe(self, websocket: WebSocket, topic: str) -> None:
        if topic not in self._topic_subscriptions:
            self._topic_subscriptions[topic] = set()
        self._topic_subscriptions[topic].add(websocket)
        logger.debug(f"WebSocket subscribed to topic: {topic}")

    async def unsubscribe(self, websocket: WebSocket, topic: str) -> None:
        if topic in self._topic_subscriptions:
            self._topic_subscriptions[topic].discard(websocket)

    async def broadcast_to_room(self, room: str, event: str, data: Any) -> None:
        if room not in self._connections:
            return
        message = json.dumps({"event": event, "data": data})
        disconnected: list[WebSocket] = []
        for ws in self._connections[room]:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self._connections[room].discard(ws)

    async def broadcast_to_topic(self, topic: str, data: Any) -> None:
        if topic not in self._topic_subscriptions:
            return
        message = json.dumps({"event": "topic_data", "topic": topic, "data": data})
        disconnected: list[WebSocket] = []
        for ws in self._topic_subscriptions[topic]:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self._topic_subscriptions[topic].discard(ws)

    async def broadcast_message(self, event: str, data: Any) -> None:
        message = json.dumps({"event": event, "data": data})
        for room_connections in self._connections.values():
            disconnected: list[WebSocket] = []
            for ws in room_connections:
                try:
                    if ws.client_state == WebSocketState.CONNECTED:
                        await ws.send_text(message)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                room_connections.discard(ws)

    def get_rooms(self) -> dict[str, int]:
        return {room: len(conns) for room, conns in self._connections.items()}

    def get_clients_in_room(self, room: str) -> int:
        return len(self._connections.get(room, set()))

    def get_total_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())


ws_manager = ConnectionManager()
