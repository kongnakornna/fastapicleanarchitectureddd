"""vector_db DI container"""
from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.vector_db.application.use_case import (
    VectorDBUseCase,
)
from app.modules.vector_db.infrastructure.repositories import (
    VDBCollectionRepository, VDBIndexRepository,
    VDBNamespaceRepository, VDBStatsRepository,
    VDBVectorRepository,
)
from app.modules.vector_db.infrastructure.services import (
    DefaultBackendRegistry, LoggingEventBus,
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
                detail={"code": "DB_ERROR",
                        "message": "db session unavailable"},
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
            detail={"code": "AUTH_ERROR",
                    "message": "X-Tenant-Id required"},
        )
    try:
        tenant_id = uuid.UUID(x_tenant_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR",
                    "message": "invalid tenant id"},
        ) from exc
    user_id: Optional[uuid.UUID] = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError:
            user_id = None
    return Ctx(tenant_id=tenant_id, user_id=user_id)


async def get_use_case(
    db: AsyncSession = Depends(get_db),
) -> VectorDBUseCase:
    return VectorDBUseCase(
        collections=VDBCollectionRepository(db),
        vectors=VDBVectorRepository(db),
        indexes=VDBIndexRepository(db),
        namespaces=VDBNamespaceRepository(db),
        stats=VDBStatsRepository(db),
        backends=DefaultBackendRegistry(),
        event_bus=LoggingEventBus(),
    )
