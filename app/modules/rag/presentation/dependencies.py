"""rag DI container"""
from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rag.application.use_case import RAGUseCase
from app.modules.rag.infrastructure.caches import (
    NoopRAGCache, RedisRAGCache,
)
from app.modules.rag.infrastructure.repositories import (
    ChunkRepository, CitationRepository, DocumentRepository,
    PipelineRepository, RetrievalLogRepository, RunRepository,
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
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RAGUseCase:
    embedder = getattr(request.app.state, "rag_embedder", None)
    vector_store = getattr(
        request.app.state, "rag_vector_store", None,
    )
    hybrid = getattr(request.app.state, "rag_hybrid", None)
    reranker = getattr(request.app.state, "rag_reranker", None)
    generator = getattr(request.app.state, "rag_generator", None)
    redis = getattr(request.app.state, "redis", None)
    event_bus = getattr(
        request.app.state, "rag_event_bus", None,
    )
    collection_id = getattr(
        request.app.state, "rag_collection_id", None,
    )
    cache = RedisRAGCache(redis) if redis else NoopRAGCache()

    return RAGUseCase(
        documents=DocumentRepository(db),
        chunks=ChunkRepository(db),
        pipelines=PipelineRepository(db),
        runs=RunRepository(db),
        citations=CitationRepository(db),
        retrieval_logs=RetrievalLogRepository(db),
        embedder=embedder,
        vector_store=vector_store,
        hybrid=hybrid,
        reranker=reranker,
        generator=generator,
        cache=cache,
        event_bus=event_bus,
        collection_id=collection_id,
    )
