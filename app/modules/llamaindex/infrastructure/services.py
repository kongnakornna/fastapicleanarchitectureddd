"""llamaindex services — adapters + bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.llamaindex.application.interfaces import EventBus

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

    async def upsert(
        self, *, collection_id: uuid.UUID,
        items: list[dict[str, Any]],
    ) -> int:
        try:
            from app.shared.context import RequestContext as SharedCtx
            ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
            return await self._uc.upsert(
                ctx, collection_id=collection_id, items=items,
            )
        except Exception as exc:
            logger.warning("vector upsert failed: %s", exc)
            return 0

    async def query(
        self, *, collection_id: uuid.UUID,
        vector: list[float], top_k: int,
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
            logger.warning("vector query failed: %s", exc)
            return []


class LLMPortAdapter:
    """TH: adapter ไปยัง llm module | EN: LLM port adapter"""

    def __init__(self, llm_use_case: Any) -> None:
        self._uc = llm_use_case

    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=tenant_id)
        return await self._uc.chat(
            ctx, model_name=model, messages=messages,
            system_prompt=system_prompt,
        )


class LoggingEventBus(EventBus):
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
