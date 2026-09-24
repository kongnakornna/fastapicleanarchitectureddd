"""LINE Messaging API handler"""
from __future__ import annotations

import httpx
from loguru import logger

from app.modules.iot.infrastructure.alerting.base import (
    AlertMessage,
    BaseAlertHandler,
)


class LineHandler(BaseAlertHandler):
    @property
    def name(self) -> str:
        return "line"

    async def send(self, msg: AlertMessage) -> bool:
        if not self.config.enabled:
            return False

        token = self.config.config.get("channel_access_token", "")
        to_ids = self.config.recipients
        if not token or not to_ids:
            logger.warning("line: missing token/recipients")
            return False

        text = (
            f"🚨 [{msg.severity.upper()}] {msg.title}\n"
            f"Device: {msg.device_name}\n"
            f"Value: {msg.value_data} {msg.unit}\n"
            f"Time: {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                for to_id in to_ids:
                    r = await client.post(
                        "https://api.line.me/v2/bot/message/push",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "to": to_id,
                            "messages": [{"type": "text", "text": text}],
                        },
                    )
                    r.raise_for_status()
            logger.info(f"line sent to {len(to_ids)} recipients")
            return True
        except Exception as exc:
            logger.error(f"line send failed: {exc}")
            return False