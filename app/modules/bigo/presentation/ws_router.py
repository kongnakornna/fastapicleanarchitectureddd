"""bigo WebSocket router — realtime stream"""
from __future__ import annotations

import json
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

from app.modules.bigo.infrastructure.websocket_manager import WebSocketManager
from app.modules.bigo.presentation.dependencies import get_ws_manager

log = structlog.get_logger()

ws_router = APIRouter(prefix="/bigo/ws", tags=["Big-O WebSocket"])


@ws_router.websocket("/stream")
async def ws_stream(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    tenant_id: str = Query(default="00000000-0000-0000-0000-000000000001"),
    user_id: str | None = Query(default=None),
    room: str | None = Query(default=None),
) -> None:
    await websocket.accept()
    rooms = {f"tenant:{tenant_id}"}
    if room:
        rooms.add(room)

    conn = await manager.connect(
        websocket, tenant_id=tenant_id, user_id=user_id, rooms=rooms,
    )
    try:
        await manager.send_personal(conn.id, {
            "type": "welcome",
            "conn_id": conn.id,
            "rooms": sorted(rooms),
        })
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except (TypeError, ValueError):
                msg = {"type": "raw", "data": raw}

            t = msg.get("type")
            if t == "pong":
                continue
            if t == "subscribe" and isinstance(msg.get("room"), str):
                await manager.join(conn.id, msg["room"])
                await manager.send_personal(conn.id, {
                    "type": "subscribed", "room": msg["room"],
                })
                continue
            if t == "unsubscribe" and isinstance(msg.get("room"), str):
                await manager.leave(conn.id, msg["room"])
                await manager.send_personal(conn.id, {
                    "type": "unsubscribed", "room": msg["room"],
                })
                continue
            if t == "broadcast" and msg.get("room"):
                n = await manager.broadcast(
                    {"type": "message", "from": conn.id, "data": msg.get("data")},
                    room=msg["room"], exclude={conn.id},
                )
                await manager.send_personal(conn.id, {
                    "type": "broadcast_ack", "sent": n,
                })
                continue
            await manager.send_personal(conn.id, {"type": "echo", "data": msg})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        log.warning("ws.stream.error", err=str(exc))
    finally:
        await manager.disconnect(conn.id)
