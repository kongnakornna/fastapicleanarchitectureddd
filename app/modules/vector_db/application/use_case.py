"""vector_db use cases"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.vector_db.application.exceptions import (
    ConflictAppError, NotFoundAppError, ValidationAppError,
)
from app.modules.vector_db.application.utils import (
    json_dumps_safe, json_loads_safe, json_to_vector,
    vector_to_json,
)
from app.modules.vector_db.domain.enums import VectorMetric
from app.modules.vector_db.domain.events import (
    CollectionCreated, IndexBuilt, VectorDeleted, VectorsUpserted,
)
from app.modules.vector_db.domain.helpers.metrics import (
    cosine_similarity, inner_product, l2_distance,
)
from app.modules.vector_db.domain.value_objects import (
    SearchHit, VectorQuery,
)

logger = logging.getLogger(__name__)


class VectorDBUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)

    async def create_collection(
        self, ctx: Any, *,
        name: str, dimension: int,
        metric: VectorMetric = VectorMetric.COSINE,
        backend: str = "pgvector",
        config: Optional[dict[str, Any]] = None,
    ) -> Any:
        """TH: สร้าง collection | EN: create collection"""
        from app.modules.vector_db.infrastructure.models import (
            VDBCollectionModel,
        )

        existing = await self._collections.find_by_name(ctx, name)
        if existing is not None:
            raise ConflictAppError(f"collection exists: {name}")

        coll = VDBCollectionModel(
            tenant_id=ctx.tenant_id, name=name,
            dimension=dimension, metric=str(metric),
            backend=backend,
            config_json=json_dumps_safe(config or {}),
        )
        saved = await self._collections.save(ctx, coll)

        if self._bus:
            try:
                await self._bus.publish(CollectionCreated(
                    collection_id=saved.id,
                    tenant_id=saved.tenant_id,
                    name=saved.name,
                    dimension=saved.dimension,
                    metric=str(saved.metric),
                ))
            except Exception as exc:
                logger.debug("publish failed: %s", exc)
        return saved

    async def list_collections(self, ctx: Any) -> list[Any]:
        return await self._collections.find_all(ctx)

    async def get_collection(
        self, ctx: Any, id: uuid.UUID,
    ) -> Any:
        coll = await self._collections.find_by_id(ctx, id)
        if coll is None:
            raise NotFoundAppError("collection not found")
        return coll

    async def upsert(
        self, ctx: Any, *,
        collection_id: uuid.UUID,
        items: list[dict[str, Any]],
    ) -> int:
        """TH: upsert vectors | EN: upsert vectors"""
        from app.modules.vector_db.infrastructure.models import (
            VDBVectorModel,
        )

        coll = await self.get_collection(ctx, collection_id)
        if not items:
            return 0

        prepared: list[Any] = []
        for item in items:
            vec = item.get("vector") or []
            if len(vec) != coll.dimension:
                raise ValidationAppError(
                    f"dimension mismatch: expected "
                    f"{coll.dimension}, got {len(vec)}"
                )
            prepared.append(VDBVectorModel(
                tenant_id=ctx.tenant_id,
                collection_id=coll.id,
                source_id=str(item.get("source_id", "")),
                vector_json=vector_to_json(
                    [float(x) for x in vec],
                ),
                metadata_json=json_dumps_safe(
                    item.get("metadata") or {},
                ),
                norm=float(sum(x * x for x in vec) ** 0.5),
            ))

        adapter = self._backends.get_adapter(str(coll.backend))
        try:
            count = await adapter.upsert(coll, prepared)
        except Exception as exc:
            logger.warning("backend upsert failed: %s", exc)
            count = await self._vectors.upsert_many(ctx, prepared)

        if self._bus:
            try:
                await self._bus.publish(VectorsUpserted(
                    collection_id=coll.id,
                    tenant_id=ctx.tenant_id,
                    count=count,
                ))
            except Exception:
                pass
        return count

    async def query(
        self, ctx: Any, *,
        collection_id: uuid.UUID, query: VectorQuery,
    ) -> list[SearchHit]:
        """TH: query vectors | EN: query vectors"""
        coll = await self.get_collection(ctx, collection_id)
        if len(query.vector) != coll.dimension:
            raise ValidationAppError(
                f"dimension mismatch: expected {coll.dimension}"
            )
        adapter = self._backends.get_adapter(str(coll.backend))
        try:
            return await adapter.query(coll, query)
        except Exception as exc:
            logger.debug(
                "backend query failed, in-memory fallback: %s", exc,
            )
            return await self._query_in_memory(ctx, coll, query)

    async def delete_vector(
        self, ctx: Any, *,
        collection_id: uuid.UUID, vector_id: uuid.UUID,
    ) -> bool:
        await self.get_collection(ctx, collection_id)
        ok_del = await self._vectors.delete(ctx, vector_id)
        if ok_del and self._bus:
            try:
                await self._bus.publish(VectorDeleted(
                    collection_id=collection_id,
                    tenant_id=ctx.tenant_id,
                    vector_id=vector_id,
                ))
            except Exception:
                pass
        return ok_del

    async def stats(
        self, ctx: Any, collection_id: uuid.UUID,
    ) -> dict[str, Any]:
        await self.get_collection(ctx, collection_id)
        s = await self._stats.find_by_collection(
            ctx, collection_id,
        )
        count = await self._vectors.count(ctx, collection_id)
        if s is None:
            return {
                "collection_id": str(collection_id),
                "vector_count": count,
                "size_bytes": 0,
                "avg_latency_ms": 0.0,
            }
        return {
            "collection_id": str(s.collection_id),
            "vector_count": s.vector_count or count,
            "size_bytes": s.size_bytes or 0,
            "avg_latency_ms": float(s.avg_latency_ms or 0.0),
        }

    async def build_index(
        self, ctx: Any, *,
        collection_id: uuid.UUID,
        index_type: str, params: dict[str, Any],
    ) -> Any:
        """TH: สร้าง ANN index | EN: build ANN index"""
        from app.modules.vector_db.infrastructure.models import (
            VDBIndexModel,
        )

        coll = await self.get_collection(ctx, collection_id)
        idx = VDBIndexModel(
            collection_id=coll.id,
            name=f"idx_{index_type}_{uuid.uuid4().hex[:8]}",
            index_type=index_type,
            params_json=json_dumps_safe(params),
        )
        saved = await self._indexes.save(ctx, idx)
        adapter = self._backends.get_adapter(str(coll.backend))
        try:
            size = await adapter.build_index(coll, saved)
            saved.size_bytes = size
            saved.build_status = "READY"
            await self._indexes.save(ctx, saved)
            if self._bus:
                try:
                    await self._bus.publish(IndexBuilt(
                        index_id=saved.id,
                        collection_id=coll.id,
                        index_type=index_type,
                        size_bytes=size,
                    ))
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("index build failed: %s", exc)
            saved.build_status = "FAILED"
            await self._indexes.save(ctx, saved)
        return saved

    async def list_indexes(
        self, ctx: Any, collection_id: uuid.UUID,
    ) -> list[Any]:
        await self.get_collection(ctx, collection_id)
        return await self._indexes.find_by_collection(
            ctx, collection_id,
        )

    async def _query_in_memory(
        self, ctx: Any, coll: Any, query: VectorQuery,
    ) -> list[SearchHit]:
        candidates = await self._vectors.query_candidates(
            ctx, coll.id, limit=max(query.top_k * 10, 100),
        )
        scored: list[tuple[float, Any]] = []
        for cand in candidates:
            vec = json_to_vector(cand.vector_json)
            if query.metric == VectorMetric.COSINE:
                score = cosine_similarity(query.vector, vec)
            elif query.metric == VectorMetric.L2:
                score = -l2_distance(query.vector, vec)
            else:
                score = inner_product(query.vector, vec)
            if (query.score_threshold is not None
                    and score < query.score_threshold):
                continue
            scored.append((score, cand))

        scored.sort(key=lambda x: x[0], reverse=True)
        hits: list[SearchHit] = []
        for rank, (score, cand) in enumerate(
            scored[: query.top_k], start=1,
        ):
            hits.append(SearchHit(
                vector_id=cand.id,
                source_id=cand.source_id,
                score=float(score),
                metadata=(
                    json_loads_safe(cand.metadata_json, {})
                    if query.include_metadata else None
                ),
                rank=rank,
            ))
        return hits
