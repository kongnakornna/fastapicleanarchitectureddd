from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from app.modules.email.domain.entities.email_config import EmailConfig
from app.modules.email.domain.entities.email_log import EmailLog
from app.modules.email.infrastructure.email_repository import EmailRepository

logger = logging.getLogger(__name__)


class EmailUseCase:
    def __init__(self, email_repository: EmailRepository) -> None:
        self._email_repo = email_repository

    async def get_logs(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[EmailLog], int]:
        return await self._email_repo.find_all_paginated(page, page_size)

    async def get_log(self, log_id: UUID) -> EmailLog | None:
        return await self._email_repo.find_by_id(log_id)

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str | None = None,
        bcc: str | None = None,
    ) -> EmailLog:
        log = EmailLog(
            to_address=to,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            status="pending",
        )
        await self._email_repo.create(log)

        try:
            config = await self._email_repo.get_config()
            if not config:
                raise RuntimeError("Email config not found")

            logger.info(
                "Sending email to=%s subject=%s via %s:%s",
                to, subject, config.smtp_host, config.smtp_port,
            )

            log.status = "sent"
            log.sent_at = datetime.now(UTC)
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            log.status = "failed"
            log.error_message = str(e)

        return await self._email_repo.update(log)

    async def get_config(self) -> EmailConfig | None:
        return await self._email_repo.get_config()

    async def update_config(self, values: dict) -> EmailConfig | None:
        config = await self._email_repo.get_config()
        if not config:
            return None
        for key, value in values.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        return await self._email_repo.update_config(config)
