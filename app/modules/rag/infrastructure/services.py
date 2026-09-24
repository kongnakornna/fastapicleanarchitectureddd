"""rag services — cross-module adapters · event bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EmbeddingModuleAdapter:
    """TH: adapter ไป embeddings module | EN: embeddings adapter"""

    def __init__(self, embedding_use_case: Any) -> None:
        self._uc = embedding_use_case

    async def embed(
        self, *, model: str, texts: list[str],
        normalize: bool = True,
    ) -> list[Any]:
        from app.modules.embeddings.domain.value_objects import (
            EmbeddingRequest,
        )
        from app.shared.context import RequestContext as SharedCtx

        if not texts:
            return []
        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
        req = EmbeddingRequest(
            model=model, input=texts, normalize=normalize,
        )
        return await self._uc.embed(ctx, req)


class VectorStoreModuleAdapter:
    """TH: adapter ไป vector_db | EN: vector_db adapter"""

    def __init__(self, vector_use_case: Any) -> None:
        self._uc = vector_use_case

    async def upsert(
        self, *, collection_id: uuid.UUID,
        items: list[dict[str, Any]],
    ) -> int:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
        return await self._uc.upsert(
            ctx, collection_id=collection_id, items=items,
        )

    async def query(
        self, *, collection_id: uuid.UUID,
        vector: list[float], top_k: int,
    ) -> list[Any]:
        from app.modules.vector_db.domain.value_objects import (
            VectorQuery,
        )
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
        return await self._uc.query(
            ctx, collection_id=collection_id,
            query=VectorQuery(vector=vector, top_k=top_k),
        )


class HybridSearchModuleAdapter:
    """TH: adapter ไป hybrid_search | EN: hybrid adapter"""

    def __init__(self, hybrid_use_case: Any) -> None:
        self._uc = hybrid_use_case

    async def search(
        self, *, query: str, top_k: int,
    ) -> list[Any]:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
        return await self._uc.search(
            ctx, query=query, top_k=top_k,
        )


class LLMGeneratorAdapter:
    """TH: adapter ไป llm module | EN: llm adapter"""

    def __init__(self, llm_port: Any) -> None:
        self._llm = llm_port

    async def chat(
        self, *, model: str, messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any:
        return await self._llm.chat(
            tenant_id=uuid.UUID(int=0),
            model=model, messages=messages,
            system_prompt=system_prompt,
        )


class NoopReranker:
    async def rerank(
        self, *, query: str,
        candidates: list[dict[str, Any]], top_k: int,
    ) -> list[dict[str, Any]]:
        return candidates[:top_k]


class LoggingEventBus:
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
