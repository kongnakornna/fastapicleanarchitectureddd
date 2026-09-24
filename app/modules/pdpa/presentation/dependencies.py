"""pdpa DI container"""
from __future__ import annotations
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import RequestContext, get_context
from app.core.db import get_session
from app.core.events import EventBus, get_event_bus
from app.modules.pdpa.application.interfaces import (
    DataExporter, EmailService, IdempotencyStore, LLMService, PIIAnonymizer,
)
from app.modules.pdpa.application.use_cases import (
    EraseDataUseCase, ExportDataUseCase, GetCurrentPolicyUseCase,
    ProcessDSARUseCase, PublishPrivacyPolicyUseCase,
    RecordConsentUseCase, RecordCookieConsentUseCase,
    RevokeConsentUseCase, SubmitDSARUseCase,
    UpdateCookieConsentUseCase,
)
from app.modules.pdpa.infrastructure.idempotency_store import (
    SQLAlchemyIdempotencyStore,
)
from app.modules.pdpa.infrastructure.repositories import (
    SQLAlchemyConsentRepository, SQLAlchemyCookieConsentRepository,
    SQLAlchemyDSARRepository, SQLAlchemyPrivacyPolicyRepository,
)
from app.modules.pdpa.infrastructure.services import (
    DefaultPIIAnonymizer, JsonPdfDataExporter,
    OpenAILLMService, SMTPEmailService,
)


def get_consent_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyConsentRepository:
    return SQLAlchemyConsentRepository(session=session)


def get_dsar_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyDSARRepository:
    return SQLAlchemyDSARRepository(session=session)


def get_pp_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyPrivacyPolicyRepository:
    return SQLAlchemyPrivacyPolicyRepository(session=session)


def get_cc_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyCookieConsentRepository:
    return SQLAlchemyCookieConsentRepository(session=session)


def get_email_service() -> EmailService:
    return SMTPEmailService(smtp_client=None, from_addr="noreply@example.com")


def get_llm_service() -> LLMService:
    return OpenAILLMService(client=None)


def get_exporter(
    consent_repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
) -> DataExporter:
    return JsonPdfDataExporter(repo=consent_repo)


def get_anonymizer() -> PIIAnonymizer:
    return DefaultPIIAnonymizer()


def get_idempotency_store(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IdempotencyStore:
    return SQLAlchemyIdempotencyStore(session=session)


# ─── Use case factories ──────────────────────────────────────────
async def get_record_consent_uc(
    repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RecordConsentUseCase:
    return RecordConsentUseCase(repo=repo, bus=bus, idem=idem, ctx=ctx)


async def get_revoke_consent_uc(
    repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RevokeConsentUseCase:
    return RevokeConsentUseCase(repo=repo, bus=bus, ctx=ctx)


async def get_submit_dsar_uc(
    repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    email: Annotated[EmailService, Depends(get_email_service)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> SubmitDSARUseCase:
    return SubmitDSARUseCase(
        repo=repo, bus=bus, email=email, idem=idem, ctx=ctx,
    )


async def get_process_dsar_uc(
    repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    email: Annotated[EmailService, Depends(get_email_service)],
    llm: Annotated[LLMService, Depends(get_llm_service)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> ProcessDSARUseCase:
    return ProcessDSARUseCase(
        repo=repo, bus=bus, email=email, llm=llm, ctx=ctx,
    )


async def get_export_data_uc(
    dsar_repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    exporter: Annotated[DataExporter, Depends(get_exporter)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> ExportDataUseCase:
    return ExportDataUseCase(
        dsar_repo=dsar_repo, exporter=exporter, bus=bus, ctx=ctx,
    )


async def get_erase_data_uc(
    consent_repo: Annotated[SQLAlchemyConsentRepository, Depends(get_consent_repo)],
    dsar_repo: Annotated[SQLAlchemyDSARRepository, Depends(get_dsar_repo)],
    anonymizer: Annotated[PIIAnonymizer, Depends(get_anonymizer)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> EraseDataUseCase:
    return EraseDataUseCase(
        consent_repo=consent_repo, dsar_repo=dsar_repo,
        anonymizer=anonymizer, bus=bus, ctx=ctx,
    )


async def get_publish_pp_uc(
    repo: Annotated[SQLAlchemyPrivacyPolicyRepository, Depends(get_pp_repo)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> PublishPrivacyPolicyUseCase:
    return PublishPrivacyPolicyUseCase(repo=repo, bus=bus, ctx=ctx)


async def get_current_pp_uc(
    repo: Annotated[SQLAlchemyPrivacyPolicyRepository, Depends(get_pp_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> GetCurrentPolicyUseCase:
    return GetCurrentPolicyUseCase(repo=repo, ctx=ctx)


async def get_record_cookie_uc(
    repo: Annotated[SQLAlchemyCookieConsentRepository, Depends(get_cc_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> RecordCookieConsentUseCase:
    return RecordCookieConsentUseCase(repo=repo, ctx=ctx)


async def get_update_cookie_uc(
    repo: Annotated[SQLAlchemyCookieConsentRepository, Depends(get_cc_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> UpdateCookieConsentUseCase:
    return UpdateCookieConsentUseCase(repo=repo, ctx=ctx)