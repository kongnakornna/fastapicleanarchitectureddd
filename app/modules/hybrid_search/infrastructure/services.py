"""hybrid_search services — adapters + reranker + bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any

from app.modules.hybrid_search.application.interfaces import (
    EventBus, RerankerPort,
)

logger = logging.getLogger(__name__)


class EmbeddingModuleAdapter:
    """TH: adapter ไปยัง embeddings module | EN: embeddings adapter"""

    def __init__(self, embedding_use_case: Any) -> None:
        self._uc = embedding_use_case

    async def embed(
        self, *, model: str, texts: list[str], normalize: bool = True,
    ) -> list[Any]:
        if not texts:
            return []
        try:
            from app.modules.embeddings.domain.value_objects import (
                EmbeddingRequest,
            )
            from app.shared.context import RequestContext as SharedCtx

            ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
            return await self._uc.embed(ctx, EmbeddingRequest(
                model=model, input=texts, normalize=normalize,
            ))
        except Exception as exc:
            logger.warning("embedding adapter failed: %s", exc)
            return []


class VectorStoreModuleAdapter:
    """TH: adapter ไปยัง vector_db module | EN: vector store adapter"""

    def __init__(self, vector_use_case: Any) -> None:
        self._uc = vector_use_case

    async def query(
        self, *, collection_id: uuid.UUID, vector: list[float],
        top_k: int,
    ) -> list[Any]:
        try:
            from app.modules.vector_db.domain.value_objects import (
                VectorQuery,
            )
            from app.shared.context import RequestContext as SharedCtx

            ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
            return await self._uc.query(
                ctx, collection_id=collection_id,
                query=VectorQuery(vector=vector, top_k=top_k),
            )
        except Exception as exc:
            logger.warning("vector adapter failed: %s", exc)
            return []


class ScoreBasedReranker(RerankerPort):
    """TH: reranker ด้วย score | EN: score-based reranker"""

    async def rerank(
        self, *, query: str, candidates: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        ordered = sorted(
            candidates,
            key=lambda c: float(c.get("score", 0.0)),
            reverse=True,
        )[:top_k]
        for i, h in enumerate(ordered, start=1):
            h["rank"] = i
        return ordered


class NoopReranker(RerankerPort):
    async def rerank(
        self, *, query: str, candidates: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        return candidates[:top_k]


class LoggingEventBus(EventBus):
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
