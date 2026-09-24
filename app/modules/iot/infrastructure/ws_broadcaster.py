"""WebSocket broadcaster — real-time push"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from loguru import logger


class WSBroadcaster:
    """TH: broadcast events ไป WS rooms | EN: broadcast events to WS rooms"""

    async def alarm_triggered(
        self,
        device_id: int,
        device_name: str,
        alarm_status: int,
        title: str,
        subject: str,
        value: float,
        unit: str = "",
    ) -> None:
        """Broadcast alarm ใหม่"""
        room = "alerts" if alarm_status in (1, 2) else "alerts_recovery"
        try:
            from app.core.websocket_hub import ws_manager

            payload = {
                "device_id": device_id,
                "device_name": device_name,
                "alarm_status": alarm_status,
                "severity": self._severity(alarm_status),
                "title": title,
                "subject": subject,
                "value": value,
                "unit": unit,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Broadcast ไป alerts room
            await ws_manager.broadcast_to_room(room, "alarm", payload)

            # Broadcast ไป device-specific room
            await ws_manager.broadcast_to_room(
                f"device:{device_id}", "alarm", payload,
            )

            logger.debug(f"ws.alarm_triggered: device={device_id} status={alarm_status}")
        except Exception as exc:
            logger.warning(f"ws.alarm_triggered failed: {exc}")

    async def data_received(
        self, device_id: int, data: dict[str, Any],
    ) -> None:
        """Broadcast ข้อมูลใหม่"""
        try:
            from app.core.websocket_hub import ws_manager
            await ws_manager.broadcast_to_room(
                f"device:{device_id}", "data",
                {"device_id": device_id, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()},
            )
        except Exception as exc:
            logger.warning(f"ws.data_received failed: {exc}")

    async def device_status_changed(
        self, device_id: int, is_online: bool,
    ) -> None:
        """Broadcast device online/offline"""
        try:
            from app.core.websocket_hub import ws_manager
            event = "device_online" if is_online else "device_offline"
            await ws_manager.broadcast_to_room("devices", event, {
                "device_id": device_id,
                "is_online": is_online,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            logger.warning(f"ws.device_status_changed failed: {exc}")

    async def broadcast_custom(
        self, room: str, event: str, data: dict[str, Any],
    ) -> None:
        """Broadcast custom event"""
        try:
            from app.core.websocket_hub import ws_manager
            await ws_manager.broadcast_to_room(room, event, data)
        except Exception as exc:
            logger.warning(f"ws.broadcast_custom failed: {exc}")

    @staticmethod
    def _severity(status: int) -> str:
        return {1: "medium", 2: "critical", 3: "low", 4: "low", 5: "info"}.get(
            status, "info"
        )


# Singleton
ws_broadcaster = WSBroadcaster()