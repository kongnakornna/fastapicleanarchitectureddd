"""hybrid_search HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.hybrid_search.application.exceptions import AppError
from app.modules.hybrid_search.application.use_case import (
    HybridSearchUseCase,
)
from app.modules.hybrid_search.domain.exceptions import HSError
from app.modules.hybrid_search.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.hybrid_search.presentation.schemas import (
    ConfigCreateRequest, ConfigOut, MetricsRequest, MetricsResponse,
    QueryOut, RankingOut, SearchHitOut, SearchRequest, SearchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hs", tags=["HybridSearch"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, HSError):
        http = 400
        code = getattr(exc, "code", "DOMAIN_ERROR")
        if code == "NOT_FOUND":
            http = 404
        elif code == "VALIDATION_ERROR":
            http = 422
        elif code == "CONFLICT":
            http = 409
        elif code == "LIMIT_EXCEEDED":
            http = 402
        elif code == "PROVIDER_ERROR":
            http = 502
        raise HTTPException(
            status_code=http,
            detail={"code": code, "message": str(exc)},
        )
    if isinstance(exc, AppError):
        raise HTTPException(
            status_code=getattr(exc, "http_status", 400),
            detail={
                "code": getattr(exc, "code", "APP_ERROR"),
                "message": str(exc),
            },
        )
    logger.exception("unhandled error")
    raise HTTPException(
        status_code=500,
        detail={"code": "INTERNAL_ERROR", "message": "internal error"},
    )


@router.get("/configs", response_model=list[ConfigOut])
async def list_configs(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> list[ConfigOut]:
    """TH: list configs | EN: list configs"""
    try:
        items = await uc.list_configs(ctx)
        return [ConfigOut.model_validate(c.model_dump()) for c in items]
    except (HSError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/configs", response_model=ConfigOut, status_code=201)
async def create_config(
    req: ConfigCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> ConfigOut:
    """TH: สร้าง config | EN: create config"""
    try:
        c = await uc.create_config(
            ctx, name=req.name,
            fusion_type=str(req.fusion_type),
            rrf_k=req.rrf_k,
            bm25_weight=req.bm25_weight,
            vector_weight=req.vector_weight,
            top_k=req.top_k,
            reranker_type=str(req.reranker_type),
        )
        return ConfigOut.model_validate(c.model_dump())
    except (HSError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> SearchResponse:
    """TH: hybrid search | EN: hybrid search"""
    try:
        out = await uc.search(
            ctx, query=req.query,
            config_id=req.config_id,
            top_k=req.top_k,
            collection_id=req.collection_id,
            embedding_model=req.embedding_model,
            corpus=req.corpus,
        )
        return SearchResponse(
            query_id=out["query_id"],
            config_id=out["config_id"],
            fusion_type=out["fusion_type"],
            reranker_type=out["reranker_type"],
            top_k=out["top_k"],
            results=[
                SearchHitOut(**{k: v for k, v in h.items()
                                if k in SearchHitOut.model_fields})
                for h in out.get("results", [])
            ],
            sparse_count=out.get("sparse_count", 0),
            dense_count=out.get("dense_count", 0),
            latency_ms=out.get("latency_ms", 0),
            metrics=out.get("metrics", {}) or {},
        )
    except (HSError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/queries/{query_id}", response_model=QueryOut)
async def get_query(
    query_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> QueryOut:
    """TH: ดึง query | EN: get query"""
    try:
        q = await uc.get_query(ctx, query_id)
        return QueryOut.model_validate(q.model_dump())
    except (HSError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/queries/{query_id}/ranking", response_model=list[RankingOut])
async def get_ranking(
    query_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> list[RankingOut]:
    """TH: ดึง ranking intermediates | EN: get ranking"""
    try:
        rows = await uc.get_query_rankings(ctx, query_id)
        return [RankingOut.model_validate(r.model_dump()) for r in rows]
    except (HSError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/metrics", response_model=MetricsResponse)
async def compute_metrics(
    req: MetricsRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
) -> MetricsResponse:
    """TH: คำนวณ metrics | EN: compute metrics"""
    try:
        out = await uc.compute_metrics(
            ctx, retrieved_ids=req.retrieved_ids,
            relevant_ids=req.relevant_ids,
            relevances=req.relevances or None,
            k=req.k,
        )
        return MetricsResponse(**out)
    except (HSError, AppError) as exc:
        _raise(exc)
        raise
