"""Telegram Bot handler"""
from __future__ import annotations

import httpx
from loguru import logger

from app.modules.iot.infrastructure.alerting.base import (
    AlertMessage,
    BaseAlertHandler,
)


class TelegramHandler(BaseAlertHandler):
    @property
    def name(self) -> str:
        return "telegram"

    async def send(self, msg: AlertMessage) -> bool:
        if not self.config.enabled:
            return False

        bot_token = self.config.config.get("bot_token", "")
        if not bot_token or not self.config.recipients:
            logger.warning("telegram: missing bot_token/recipients")
            return False

        text = (
            f"🚨 *{msg.title}*\n"
            f"Device: `{msg.device_name}`\n"
            f"Value: `{msg.value_data} {msg.unit}`\n"
            f"Severity: `{msg.severity}`\n"
            f"Time: `{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}`"
        )

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                for chat_id in self.config.recipients:
                    r = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": text,
                            "parse_mode": "Markdown",
                        },
                    )
                    r.raise_for_status()
            logger.info(f"telegram sent to {len(self.config.recipients)}")
            return True
        except Exception as exc:
            logger.error(f"telegram send failed: {exc}")
            return False