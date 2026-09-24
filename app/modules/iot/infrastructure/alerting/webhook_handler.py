"""Generic webhook handler"""
from __future__ import annotations

import httpx
from loguru import logger

from app.modules.iot.infrastructure.alerting.base import (
    AlertMessage,
    BaseAlertHandler,
)


class WebhookHandler(BaseAlertHandler):
    @property
    def name(self) -> str:
        return "webhook"

    async def send(self, msg: AlertMessage) -> bool:
        if not self.config.enabled:
            return False

        cfg = self.config.config
        url = cfg.get("url", "")
        if not url:
            logger.warning("webhook: missing url")
            return False

        payload = {
            "device_id": msg.device_id,
            "device_name": msg.device_name,
            "alarm_status": msg.alarm_status,
            "severity": msg.severity,
            "title": msg.title,
            "subject": msg.subject,
            "content": msg.content,
            "value_data": msg.value_data,
            "unit": msg.unit,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    url, json=payload,
                    headers=cfg.get("headers", {}),
                )
                r.raise_for_status()
            logger.info(f"webhook sent to {url}")
            return True
        except Exception as exc:
            logger.error(f"webhook send failed: {exc}")
            return False