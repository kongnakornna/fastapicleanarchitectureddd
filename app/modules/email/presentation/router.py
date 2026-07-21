from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.email.application.use_case import EmailUseCase
from app.modules.email.domain.entities.email_config import EmailConfig
from app.modules.email.domain.entities.email_log import EmailLog
from app.modules.email.infrastructure.email_repository import EmailRepository
from app.modules.email.presentation.schemas import (
    EmailConfigResponse,
    EmailConfigUpdateRequest,
    EmailLogResponse,
    EmailSendRequest,
    PaginatedEmailLogsResponse,
)

router = APIRouter(prefix="/email", tags=["Email"])


async def get_email_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> EmailUseCase:
    return EmailUseCase(email_repository=EmailRepository(session))


def _log_to_response(log: EmailLog) -> EmailLogResponse:
    return EmailLogResponse(
        id=str(log.id),
        to_address=log.to_address,
        subject=log.subject,
        status=log.status,
        error_message=log.error_message,
        sent_at=log.sent_at.isoformat() if log.sent_at else None,
        created_at=log.created_at.isoformat() if log.created_at else "",
    )


def _config_to_response(config: EmailConfig) -> EmailConfigResponse:
    return EmailConfigResponse(
        smtp_host=config.smtp_host,
        smtp_port=config.smtp_port,
        smtp_user=config.smtp_user,
        from_email=config.from_email,
        from_name=config.from_name,
        is_active=config.is_active,
    )


@router.post("/send")
async def send_email(
    payload: EmailSendRequest,
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> EmailLogResponse:
    log = await use_case.send_email(
        to=payload.to,
        subject=payload.subject,
        body=payload.body,
        cc=payload.cc,
        bcc=payload.bcc,
    )
    return _log_to_response(log)


@router.get("/logs")
async def get_logs(
    page: int = 1,
    per_page: int = 10,
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> PaginatedEmailLogsResponse:
    per_page = min(per_page, 100)
    logs, total = await use_case.get_logs(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedEmailLogsResponse(
        logs=[_log_to_response(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/logs/{log_id}")
async def get_log(
    log_id: str,
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> EmailLogResponse:
    from uuid import UUID

    log = await use_case.get_log(UUID(log_id))
    if not log:
        raise HTTPException(status_code=404, detail="Email log not found")
    return _log_to_response(log)


@router.get("/config")
async def get_config(
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> EmailConfigResponse:
    config = await use_case.get_config()
    if not config:
        raise HTTPException(status_code=404, detail="Email config not found")
    return _config_to_response(config)


@router.put("/config")
async def update_config(
    payload: EmailConfigUpdateRequest,
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> EmailConfigResponse:
    values = payload.model_dump(exclude_none=True)
    config = await use_case.update_config(values)
    if not config:
        raise HTTPException(status_code=404, detail="Email config not found")
    return _config_to_response(config)
