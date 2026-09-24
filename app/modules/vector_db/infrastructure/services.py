"""vector_db services — backends · registry · event bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any

from app.modules.vector_db.application.utils import (
    json_loads_safe, json_to_vector,
)
from app.modules.vector_db.domain.enums import VectorMetric
from app.modules.vector_db.domain.helpers.metrics import (
    cosine_similarity, inner_product, l2_distance,
)
from app.modules.vector_db.domain.value_objects import SearchHit

logger = logging.getLogger(__name__)


class PgVectorAdapter:
    """TH: pgvector adapter (via JSON) | EN: pgvector adapter"""

    async def upsert(self, collection: Any, vectors: list[Any]) -> int:
        return len(vectors)

    async def query(self, collection: Any, query: Any) -> list:
        raise NotImplementedError("delegated to in-memory fallback")

    async def delete(self, collection: Any, vector_ids: list) -> int:
        return len(vector_ids)

    async def build_index(self, collection: Any, index: Any) -> int:
        return collection.dimension * 4 * 1000


class QdrantAdapter:
    """TH: qdrant adapter (stub) | EN: qdrant adapter"""

    async def upsert(self, collection: Any, vectors: list) -> int:
        logger.info("qdrant upsert %d vectors", len(vectors))
        return len(vectors)

    async def query(self, collection: Any, query: Any) -> list:
        return []

    async def delete(self, collection: Any, vector_ids: list) -> int:
        return len(vector_ids)

    async def build_index(self, collection: Any, index: Any) -> int:
        return 0


class InMemoryAdapter:
    """TH: in-memory adapter (fallback) | EN: in-memory adapter"""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, list] = {}

    async def upsert(self, collection: Any, vectors: list) -> int:
        bucket = self._store.setdefault(collection.id, [])
        for v in vectors:
            vec = json_to_vector(v.vector_json)
            meta = json_loads_safe(v.metadata_json, {})
            bucket.append((v.id, vec, meta))
        return len(vectors)

    async def query(self, collection: Any, query: Any) -> list:
        bucket = self._store.get(collection.id, [])
        scored: list = []
        for vid, vec, meta in bucket:
            if query.metric == VectorMetric.COSINE:
                s = cosine_similarity(query.vector, vec)
            elif query.metric == VectorMetric.L2:
                s = -l2_distance(query.vector, vec)
            else:
                s = inner_product(query.vector, vec)
            scored.append((s, vid, meta))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            SearchHit(
                vector_id=vid, source_id=str(vid),
                score=float(s),
                metadata=meta if query.include_metadata else None,
                rank=i + 1,
            )
            for i, (s, vid, meta) in enumerate(
                scored[: query.top_k],
            )
        ]

    async def delete(self, collection: Any, vector_ids: list) -> int:
        bucket = self._store.get(collection.id, [])
        ids_set = set(vector_ids)
        before = len(bucket)
        self._store[collection.id] = [
            r for r in bucket if r[0] not in ids_set
        ]
        return before - len(self._store[collection.id])

    async def build_index(self, collection: Any, index: Any) -> int:
        bucket = self._store.get(collection.id, [])
        return sum(len(v) * 4 for _, v, _ in bucket)


class DefaultBackendRegistry:
    def __init__(self) -> None:
        self._in_memory = InMemoryAdapter()

    def get_adapter(self, backend: str) -> Any:
        b = (backend or "").lower()
        if b == "qdrant":
            return QdrantAdapter()
        return self._in_memory


class LoggingEventBus:
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
