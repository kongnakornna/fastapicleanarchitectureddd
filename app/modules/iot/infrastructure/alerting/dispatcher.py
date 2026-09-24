"""Alert dispatcher"""
from __future__ import annotations

import os
from typing import Any

from loguru import logger

from app.modules.iot.infrastructure.alerting.base import (
    AlertChannel,
    AlertMessage,
    BaseAlertHandler,
)
from app.modules.iot.infrastructure.alerting.email_handler import EmailHandler
from app.modules.iot.infrastructure.alerting.line_handler import LineHandler
from app.modules.iot.infrastructure.alerting.telegram_handler import TelegramHandler
from app.modules.iot.infrastructure.alerting.webhook_handler import WebhookHandler


class AlertDispatcher:
    """TH: จัดการ channel ทั้งหมด | EN: manage all channels"""

    def __init__(self) -> None:
        self._handlers: dict[str, BaseAlertHandler] = {}

    def register(self, channel_name: str, handler: BaseAlertHandler) -> None:
        self._handlers[channel_name] = handler
        logger.info(f"alerting: registered {channel_name}")

    def configure_from_env(self) -> None:
        """สร้าง channels จาก .env"""
        # ─── Email ───
        email_cfg = AlertChannel(
            enabled=os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true",
            recipients=[
                r.strip()
                for r in os.getenv("ALERT_EMAIL_TO", "").split(",")
                if r.strip()
            ],
            config={
                "smtp_host": os.getenv("ALERT_SMTP_HOST", ""),
                "smtp_port": int(os.getenv("ALERT_SMTP_PORT", "587")),
                "smtp_user": os.getenv("ALERT_SMTP_USER", ""),
                "smtp_pass": os.getenv("ALERT_SMTP_PASS", ""),
                "from": os.getenv("ALERT_EMAIL_FROM", ""),
                "use_tls": os.getenv("ALERT_SMTP_TLS", "true").lower() == "true",
            },
        )
        self.register("email", EmailHandler(email_cfg))

        # ─── LINE ───
        line_cfg = AlertChannel(
            enabled=os.getenv("ALERT_LINE_ENABLED", "false").lower() == "true",
            recipients=[
                r.strip()
                for r in os.getenv("ALERT_LINE_TO", "").split(",")
                if r.strip()
            ],
            config={
                "channel_access_token": os.getenv("ALERT_LINE_TOKEN", ""),
            },
        )
        self.register("line", LineHandler(line_cfg))

        # ─── Telegram ───
        tg_cfg = AlertChannel(
            enabled=os.getenv("ALERT_TELEGRAM_ENABLED", "false").lower() == "true",
            recipients=[
                r.strip()
                for r in os.getenv("ALERT_TELEGRAM_CHAT_IDS", "").split(",")
                if r.strip()
            ],
            config={
                "bot_token": os.getenv("ALERT_TELEGRAM_BOT_TOKEN", ""),
            },
        )
        self.register("telegram", TelegramHandler(tg_cfg))

        # ─── Webhook ───
        wh_cfg = AlertChannel(
            enabled=os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() == "true",
            config={
                "url": os.getenv("ALERT_WEBHOOK_URL", ""),
                "headers": {},
            },
        )
        self.register("webhook", WebhookHandler(wh_cfg))

    async def send(
        self, msg: AlertMessage, channels: list[str] | None = None,
    ) -> dict[str, bool]:
        """TH: ส่งไป channel ที่เลือก | EN: send to selected channels"""
        targets = channels or list(self._handlers.keys())
        results: dict[str, bool] = {}
        for name in targets:
            handler = self._handlers.get(name)
            if handler is None:
                results[name] = False
                continue
            try:
                results[name] = await handler.send(msg)
            except Exception as exc:
                logger.error(f"dispatch {name} failed: {exc}")
                results[name] = False
        return results

    def get_channels_status(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "enabled": handler.config.enabled,
                "recipients": len(handler.config.recipients),
            }
            for name, handler in self._handlers.items()
        }


# Singleton
alert_dispatcher = AlertDispatcher()
alert_dispatcher.configure_from_env()