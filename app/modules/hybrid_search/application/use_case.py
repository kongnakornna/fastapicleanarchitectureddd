"""hybrid_search use cases"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.hybrid_search.application.exceptions import (
    ConflictAppError, NotFoundAppError, RetrieverAppError,
    ValidationAppError,
)
from app.modules.hybrid_search.application.utils import (
    hit_to_dict, json_dumps_safe, ms_now,
)
from app.modules.hybrid_search.domain.enums import (
    FusionType, SourceKind,
)
from app.modules.hybrid_search.domain.events import (
    ConfigCreated, MetricsComputed, RerankCompleted, SearchExecuted,
)
from app.modules.hybrid_search.domain.helpers.bm25 import bm25_score
from app.modules.hybrid_search.domain.helpers.fusion import (
    comb_mnz_fuse, comb_sum_fuse, rrf_fuse, weighted_sum_fuse,
)
from app.modules.hybrid_search.domain.helpers.metrics import (
    mrr, ndcg, precision_at_k, recall_at_k,
)
from app.modules.hybrid_search.domain.value_objects import (
    FusionConfig, HybridQuery,
)

logger = logging.getLogger(__name__)

_DEFAULT_CORPUS = "default"


class HybridSearchUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)

    # ─── Configs ─────────────────────────────────
    async def create_config(
        self, ctx: Any, *,
        name: str,
        fusion_type: str = "rrf",
        rrf_k: int = 60,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        top_k: int = 10,
        reranker_type: str = "none",
    ) -> Any:
        """TH: สร้าง config | EN: create config"""
        from app.modules.hybrid_search.infrastructure.models import (
            HSConfigModel,
        )

        existing = await self._configs.find_by_name(ctx, name)
        if existing is not None:
            raise ConflictAppError(f"config exists: {name}")

        row = HSConfigModel(
            tenant_id=ctx.tenant_id, name=name,
            fusion_type=fusion_type, rrf_k=rrf_k,
            bm25_weight=bm25_weight, vector_weight=vector_weight,
            top_k=top_k, reranker_type=reranker_type,
            is_active=True,
        )
        saved = await self._configs.save(ctx, row)

        if self._bus:
            try:
                await self._bus.publish(ConfigCreated(
                    config_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, fusion_type=fusion_type,
                ))
            except Exception:
                pass
        return saved

    async def list_configs(self, ctx: Any) -> list[Any]:
        return await self._configs.find_all_active(ctx)

    async def get_config(self, ctx: Any, config_id: uuid.UUID) -> Any:
        c = await self._configs.find_by_id(ctx, config_id)
        if c is None:
            raise NotFoundAppError("config not found")
        return c

    # ─── Search ──────────────────────────────────
    async def search(
        self, ctx: Any, *,
        query: str,
        config_id: Optional[uuid.UUID] = None,
        top_k: Optional[int] = None,
        collection_id: Optional[uuid.UUID] = None,
        embedding_model: str = "text-embedding-3-small",
        corpus: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """TH: hybrid search | EN: hybrid search"""
        if not query or not query.strip():
            raise ValidationAppError("empty query")

        config = await self._resolve_config(ctx, config_id)
        effective_top_k = int(top_k or config.top_k or 10)
        fusion_type = str(config.fusion_type)
        reranker_type = str(config.reranker_type)

        started = ms_now()

        # 1) Dense retrieval
        dense_hits: list[dict[str, Any]] = []
        if self._embedder is not None and self._vector_store is not None \
                and collection_id is not None:
            try:
                embeddings = await self._embedder.embed(
                    model=embedding_model, texts=[query],
                )
                qv = self._extract_vector(embeddings[0] if embeddings else None)
                if qv:
                    raw = await self._vector_store.query(
                        collection_id=collection_id, vector=qv,
                        top_k=effective_top_k * 2,
                    )
                    dense_hits = [hit_to_dict(h) for h in raw]
            except Exception as exc:
                logger.warning("dense retrieval failed: %s", exc)

        # 2) Sparse retrieval
        sparse_hits: list[dict[str, Any]] = []
        if corpus:
            try:
                if self._sparse is not None:
                    sparse_hits = await self._sparse.search(
                        corpus=_DEFAULT_CORPUS, query=query,
                        top_k=effective_top_k * 2,
                    )
                else:
                    sparse_hits = bm25_score(query, corpus)
            except Exception as exc:
                logger.warning("sparse retrieval failed: %s", exc)

        # 3) Fusion
        ranked_lists = [sparse_hits, dense_hits]
        fused = self._fuse(ranked_lists, config)
        fused = fused[: effective_top_k]

        # 4) Rerank
        rerank_input_count = len(fused)
        if reranker_type != "none" and self._reranker is not None:
            try:
                rerank_started = ms_now()
                fused = await self._reranker.rerank(
                    query=query, candidates=fused,
                    top_k=effective_top_k,
                )
                rerank_latency = ms_now() - rerank_started
                if self._rerank_logs:
                    from app.modules.hybrid_search.infrastructure.models import (
                        HSRerankLogModel,
                    )
                    # log after we have query_id (below)
                if self._bus:
                    try:
                        await self._bus.publish(RerankCompleted(
                            query_id=uuid.uuid4(),
                            tenant_id=ctx.tenant_id,
                            reranker_type=reranker_type,
                            input_count=rerank_input_count,
                            output_count=len(fused),
                            latency_ms=rerank_latency,
                        ))
                    except Exception:
                        pass
            except Exception as exc:
                logger.warning("reranker failed: %s", exc)

        latency = ms_now() - started

        # 5) Persist query + results + rankings
        from app.modules.hybrid_search.infrastructure.models import (
            HSQueryModel, HSRankingModel, HSResultModel,
        )
        query_row = HSQueryModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            config_id=config.id,
            query_text=query,
            latency_ms=latency,
            result_count=len(fused),
        )
        saved_query = await self._queries.create(ctx, query_row)

        # persist results
        if fused:
            try:
                result_rows = [
                    HSResultModel(
                        tenant_id=ctx.tenant_id,
                        query_id=saved_query.id,
                        rank=int(h.get("rank", i + 1)),
                        score=float(h.get("score", 0.0)),
                        source_kind=str(h.get("source_kind", "hybrid")),
                        source_id=str(h.get("source_id", "")),
                        snippet=str(h.get("snippet", ""))[:1000],
                        metadata_json=json_dumps_safe(
                            h.get("metadata") or {}
                        ),
                    )
                    for i, h in enumerate(fused)
                ]
                await self._results.create_many(ctx, result_rows)
            except Exception as exc:
                logger.debug("persist results failed: %s", exc)

        # persist rankings (intermediates)
        if self._rankings:
            try:
                rank_rows: list[Any] = []
                for src_kind, lst in (("bm25", sparse_hits),
                                       ("vector", dense_hits)):
                    for h in lst:
                        rank_rows.append(HSRankingModel(
                            tenant_id=ctx.tenant_id,
                            query_id=saved_query.id,
                            stage="retrieve",
                            source_kind=src_kind,
                            source_id=str(h.get("source_id", "")),
                            raw_score=float(h.get("score", 0.0)),
                            normalized_score=float(h.get("score", 0.0)),
                            rank=int(h.get("rank", 0)),
                        ))
                if rank_rows:
                    await self._rankings.create_many(ctx, rank_rows)
            except Exception as exc:
                logger.debug("persist rankings failed: %s", exc)

        # publish SearchExecuted
        if self._bus:
            try:
                await self._bus.publish(SearchExecuted(
                    query_id=saved_query.id,
                    tenant_id=ctx.tenant_id,
                    query_text=query,
                    result_count=len(fused),
                    latency_ms=latency,
                ))
            except Exception:
                pass

        # metrics (if relevant set provided)
        metrics = self._compute_metrics(
            fused, relevant_set=None, k=effective_top_k,
        )

        return {
            "query_id": str(saved_query.id),
            "config_id": str(config.id),
            "fusion_type": fusion_type,
            "reranker_type": reranker_type,
            "top_k": effective_top_k,
            "results": fused,
            "sparse_count": len(sparse_hits),
            "dense_count": len(dense_hits),
            "latency_ms": latency,
            "metrics": metrics,
        }

    async def get_query(self, ctx: Any, query_id: uuid.UUID) -> Any:
        q = await self._queries.find_by_id(ctx, query_id)
        if q is None:
            raise NotFoundAppError("query not found")
        return q

    async def get_query_results(
        self, ctx: Any, query_id: uuid.UUID,
    ) -> list[Any]:
        return await self._results.find_by_query(ctx, query_id)

    async def get_query_rankings(
        self, ctx: Any, query_id: uuid.UUID,
    ) -> list[Any]:
        return await self._rankings.find_by_query(ctx, query_id)

    async def compute_metrics(
        self, ctx: Any, *,
        retrieved_ids: list[str], relevant_ids: list[str],
        relevances: Optional[list[float]] = None,
        k: int = 10,
    ) -> dict[str, float]:
        """TH: คำนวณ MRR/NDCG/Recall/Precision | EN: compute metrics"""
        relevant = set(relevant_ids)
        ranks = [
            i + 1 for i, rid in enumerate(retrieved_ids)
            if rid in relevant
        ]
        rel_list = relevances or [
            1.0 if rid in relevant else 0.0 for rid in retrieved_ids
        ]
        return {
            "mrr": round(mrr(ranks), 4),
            "ndcg": round(ndcg(rel_list, k=k), 4),
            "recall_at_k": round(recall_at_k(retrieved_ids, relevant, k), 4),
            "precision_at_k": round(
                precision_at_k(retrieved_ids, relevant, k), 4
            ),
        }

    # ─── Internal ────────────────────────────────
    async def _resolve_config(
        self, ctx: Any, config_id: Optional[uuid.UUID],
    ) -> Any:
        if config_id is not None:
            return await self.get_config(ctx, config_id)

        existing = await self._configs.find_all_active(ctx)
        if existing:
            return existing[0]

        return await self.create_config(
            ctx, name="default", fusion_type="rrf", rrf_k=60,
            bm25_weight=0.5, vector_weight=0.5, top_k=10,
            reranker_type="none",
        )

    def _fuse(
        self, ranked_lists: list[list[dict[str, Any]]], config: Any,
    ) -> list[dict[str, Any]]:
        fusion_type = str(config.fusion_type)
        weights = [
            float(config.bm25_weight or 0.5),
            float(config.vector_weight or 0.5),
        ]
        k = int(config.rrf_k or 60)

        if fusion_type == "rrf":
            return rrf_fuse(ranked_lists, k=k)
        if fusion_type == "weighted_sum":
            return weighted_sum_fuse(ranked_lists, weights=weights)
        if fusion_type == "comb_sum":
            return comb_sum_fuse(ranked_lists)
        if fusion_type == "comb_mnz":
            return comb_mnz_fuse(ranked_lists)
        # fallback
        return rrf_fuse(ranked_lists, k=k)

    @staticmethod
    def _extract_vector(item: Any) -> list[float]:
        if item is None:
            return []
        if isinstance(item, list):
            return [float(x) for x in item]
        vec = getattr(item, "vector", None)
        if vec is not None:
            return [float(x) for x in vec]
        return []

    def _compute_metrics(
        self, hits: list[dict[str, Any]],
        relevant_set: Optional[set[str]], k: int,
    ) -> dict[str, float]:
        if not relevant_set:
            return {}
        retrieved = [str(h.get("source_id", "")) for h in hits]
        return {
            "mrr": round(mrr([
                i + 1 for i, rid in enumerate(retrieved)
                if rid in relevant_set
            ]), 4),
            "recall_at_k": round(
                recall_at_k(retrieved, relevant_set, k), 4
            ),
            "precision_at_k": round(
                precision_at_k(retrieved, relevant_set, k), 4
            ),
        }
