"""iot WebSocket helpers"""
from __future__ import annotations

import structlog

from app.core.websocket_hub import ws_manager

log = structlog.get_logger()


async def broadcast_alarm(
    room: str, device_id: str, title: str, value: float,
) -> None:
    try:
        await ws_manager.broadcast_to_room(room, "alarm", {
            "device_id": device_id, "title": title, "value": value,
        })
    except Exception as e:
        log.warning("ws.broadcast_failed", err=str(e))


async def broadcast_data(
    room: str, device_id: str, data: dict,
) -> None:
    try:
        await ws_manager.broadcast_to_room(room, "data", {
            "device_id": device_id, "data": data,
        })
    except Exception as e:
        log.warning("ws.broadcast_failed", err=str(e))
