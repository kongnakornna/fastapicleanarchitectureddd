"""langchain DI container"""
from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.langchain.application.use_case import (
    LangChainUseCase,
)
from app.modules.langchain.infrastructure.repositories import (
    LCAgentRepository, LCChainRepository, LCMemoryRepository,
    LCRunRepository, LCTraceRepository,
)
from app.modules.langchain.infrastructure.services import (
    LoggingEventBus,
)


@dataclass
class Ctx:
    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID]


async def get_db(request: Request) -> AsyncSession:
    session = getattr(request.app.state, "db_session", None)
    if session is None:
        sm = getattr(request.app.state, "session_factory", None)
        if sm is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DB_ERROR", "message": "db session unavailable"},
            )
        session = sm()
    return session


async def get_ctx(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> Ctx:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_ERROR", "message": "X-Tenant-Id required"},
        )
    try:
        tenant_id = uuid.UUID(x_tenant_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "invalid tenant id"},
        ) from exc
    user_id: Optional[uuid.UUID] = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError:
            user_id = None
    return Ctx(tenant_id=tenant_id, user_id=user_id)


async def get_use_case(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LangChainUseCase:
    llm_port = getattr(request.app.state, "lc_llm_port", None)
    tool_invoker = getattr(request.app.state, "lc_tool_invoker", None)
    chain_runner = getattr(request.app.state, "lc_chain_runner", None)
    agent_runner = getattr(request.app.state, "lc_agent_runner", None)
    memory_store = getattr(request.app.state, "lc_memory_store", None)
    bus = getattr(request.app.state, "lc_event_bus", None) \
        or LoggingEventBus()

    return LangChainUseCase(
        chains=LCChainRepository(db),
        agents=LCAgentRepository(db),
        memories=LCMemoryRepository(db),
        runs=LCRunRepository(db),
        traces=LCTraceRepository(db),
        llm=llm_port,
        tool_invoker=tool_invoker,
        chain_runner=chain_runner,
        agent_runner=agent_runner,
        memory_store=memory_store,
        bus=bus,
    )
