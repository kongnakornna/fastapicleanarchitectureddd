"""Email alert handler (SMTP)"""
from __future__ import annotations

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from app.modules.iot.infrastructure.alerting.base import (
    AlertChannel,
    AlertMessage,
    BaseAlertHandler,
)


class EmailHandler(BaseAlertHandler):
    @property
    def name(self) -> str:
        return "email"

    async def send(self, msg: AlertMessage) -> bool:
        if not self.config.enabled or not self.config.recipients:
            return False

        cfg = self.config.config
        smtp_host = cfg.get("smtp_host", "")
        smtp_port = int(cfg.get("smtp_port", 587))
        smtp_user = cfg.get("smtp_user", "")
        smtp_pass = cfg.get("smtp_pass", "")
        sender = cfg.get("from", smtp_user)
        use_tls = cfg.get("use_tls", True)

        if not smtp_host or not smtp_user:
            logger.warning("email: missing smtp config")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = f"[{msg.severity.upper()}] {msg.title}"
            message["From"] = sender
            message["To"] = ", ".join(self.config.recipients)

            color = "#EF4444" if msg.alarm_status == 2 else "#F59E0B"
            html = f"""
            <html><body style="font-family: Arial, sans-serif;">
              <h2 style="color: {color};">{msg.title}</h2>
              <table style="border-collapse: collapse;">
                <tr><td style="padding:4px 8px;"><b>Device:</b></td>
                    <td style="padding:4px 8px;">{msg.device_name} (ID: {msg.device_id})</td></tr>
                <tr><td style="padding:4px 8px;"><b>Value:</b></td>
                    <td style="padding:4px 8px;">{msg.value_data} {msg.unit}</td></tr>
                <tr><td style="padding:4px 8px;"><b>Severity:</b></td>
                    <td style="padding:4px 8px;">{msg.severity}</td></tr>
                <tr><td style="padding:4px 8px;"><b>Time:</b></td>
                    <td style="padding:4px 8px;">{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
              </table>
              <p>{msg.content}</p>
            </body></html>
            """
            message.attach(MIMEText(html, "html"))

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._send_sync, message,
                smtp_host, smtp_port, smtp_user, smtp_pass, use_tls,
            )
            logger.info(f"email sent to {self.config.recipients}")
            return True
        except Exception as exc:
            logger.error(f"email send failed: {exc}")
            return False

    @staticmethod
    def _send_sync(
        message: MIMEMultipart, host: str, port: int,
        user: str, password: str, use_tls: bool,
    ) -> None:
        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                server.starttls()
            if user:
                server.login(user, password)
            server.send_message(message)