"""iot services"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class AlertChannel:
    enabled: bool = False
    webhook_url: str = ""
    api_key: str = ""
    recipients: list[str] = field(default_factory=list)


@dataclass
class AlertNotification:
    device_id: int
    device_name: str
    alarm_status: int
    title: str
    subject: str
    content: str
    value_data: float
    severity: str = "info"
    channels: list[str] = field(default_factory=list)


class AlertService:
    def __init__(self, **channels: AlertChannel) -> None:
        self._channels: dict[str, AlertChannel] = dict(channels)

    async def send_alert(self, n: AlertNotification) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for name in (n.channels or list(self._channels.keys())):
            ch = self._channels.get(name)
            if ch is None or not ch.enabled:
                results[name] = False
                continue
            try:
                logger.info(f"alert.sent {name}: {n.title}")
                results[name] = True
            except Exception as exc:
                logger.error(f"alert.failed {name}: {exc}")
                results[name] = False
        return results


class WebSocketBroadcaster:
    async def broadcast(self, room: str, event: str, data: dict[str, Any]) -> None:
        try:
            from app.core.websocket_hub import ws_manager
            await ws_manager.broadcast_to_room(room, event, data)
        except Exception as exc:
            logger.debug(f"ws.broadcast skipped: {exc}")


class EventBus:
    def __init__(self, producer: Any | None = None, topic: str = "iot.events") -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: object) -> None:
        if self._producer is None:
            logger.debug(f"event.bus(stub): {type(event).__name__}")
            return
        try:
            await self._producer.send_and_wait(self._topic, {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            })
        except Exception as exc:
            logger.warning(f"event.publish_failed: {exc}")


alert_service = AlertService()
ws_broadcaster = WebSocketBroadcaster()
event_bus = EventBus()
