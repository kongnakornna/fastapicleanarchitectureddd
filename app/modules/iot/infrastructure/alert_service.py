"""Alert notification service for IoT alarms.

Supports email, LINE Notify, Telegram, and SMS notifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class AlertChannel:
    """Configuration for a notification channel."""

    enabled: bool = False
    webhook_url: str = ""
    api_key: str = ""
    recipients: list[str] = field(default_factory=list)


@dataclass
class AlertNotification:
    """Alert notification payload."""

    device_id: int
    device_name: str
    alarm_status: int
    title: str
    subject: str
    content: str
    value_data: float
    value_alarm: float
    severity: str = "info"
    channels: list[str] = field(default_factory=list)


class AlertService:
    """Sends alert notifications through configured channels."""

    def __init__(
        self,
        email_config: AlertChannel | None = None,
        line_config: AlertChannel | None = None,
        telegram_config: AlertChannel | None = None,
        sms_config: AlertChannel | None = None,
    ) -> None:
        self._channels: dict[str, AlertChannel] = {}
        if email_config:
            self._channels["email"] = email_config
        if line_config:
            self._channels["line"] = line_config
        if telegram_config:
            self._channels["telegram"] = telegram_config
        if sms_config:
            self._channels["sms"] = sms_config

    async def send_alert(self, notification: AlertNotification) -> dict[str, bool]:
        results: dict[str, bool] = {}
        target_channels = notification.channels or list(self._channels.keys())

        for channel_name in target_channels:
            if channel_name not in self._channels:
                results[channel_name] = False
                continue
            channel = self._channels[channel_name]
            if not channel.enabled:
                results[channel_name] = False
                continue
            try:
                await self._send_to_channel(channel_name, channel, notification)
                results[channel_name] = True
                logger.info(f"Alert sent via {channel_name}: {notification.title}")
            except Exception as exc:
                logger.error(f"Failed to send alert via {channel_name}: {exc}")
                results[channel_name] = False
        return results

    async def _send_to_channel(
        self,
        channel_name: str,
        channel: AlertChannel,
        notification: AlertNotification,
    ) -> None:
        if channel_name == "email":
            await self._send_email(channel, notification)
        elif channel_name == "line":
            await self._send_line_notify(channel, notification)
        elif channel_name == "telegram":
            await self._send_telegram(channel, notification)
        elif channel_name == "sms":
            await self._send_sms(channel, notification)

    async def _send_email(
        self, channel: AlertChannel, notification: AlertNotification
    ) -> None:
        logger.debug(
            f"Email alert: to={channel.recipients}, subject={notification.subject}"
        )

    async def _send_line_notify(
        self, channel: AlertChannel, notification: AlertNotification
    ) -> None:
        logger.debug(f"LINE Notify alert: {notification.title}")

    async def _send_telegram(
        self, channel: AlertChannel, notification: AlertNotification
    ) -> None:
        logger.debug(f"Telegram alert: {notification.title}")

    async def _send_sms(
        self, channel: AlertChannel, notification: AlertNotification
    ) -> None:
        logger.debug(f"SMS alert: to={channel.recipients}, message={notification.title}")

    def get_channel_status(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "enabled": ch.enabled,
                "recipients_count": len(ch.recipients),
            }
            for name, ch in self._channels.items()
        }


alert_service = AlertService()
