"""vector_db HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.vector_db.application.exceptions import AppError
from app.modules.vector_db.application.use_case import (
    VectorDBUseCase,
)
from app.modules.vector_db.domain.exceptions import VectorDBError
from app.modules.vector_db.domain.value_objects import VectorQuery
from app.modules.vector_db.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.vector_db.presentation.schemas import (
    CollectionCreateRequest, CollectionOut, IndexCreateRequest,
    IndexOut, QueryRequest, QueryResponse, SearchHitOut,
    StatsOut, UpsertRequest, UpsertResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vdb", tags=["VectorDB"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, VectorDBError):
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
        detail={"code": "INTERNAL_ERROR",
                "message": "internal error"},
    )


@router.get("/collections", response_model=list[CollectionOut])
async def list_collections(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> list[CollectionOut]:
    try:
        items = await uc.list_collections(ctx)
        return [
            CollectionOut.model_validate({
                "id": c.id, "name": c.name,
                "dimension": c.dimension,
                "metric": c.metric, "backend": c.backend,
                "is_active": bool(c.is_active),
            })
            for c in items
        ]
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/collections", response_model=CollectionOut, status_code=201,
)
async def create_collection(
    req: CollectionCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> CollectionOut:
    try:
        coll = await uc.create_collection(
            ctx, name=req.name, dimension=req.dimension,
            metric=req.metric, backend=req.backend,
            config=req.config,
        )
        return CollectionOut.model_validate({
            "id": coll.id, "name": coll.name,
            "dimension": coll.dimension,
            "metric": coll.metric, "backend": coll.backend,
            "is_active": bool(coll.is_active),
        })
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/collections/{collection_id}/upsert",
    response_model=UpsertResponse,
)
async def upsert(
    collection_id: uuid.UUID,
    req: UpsertRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> UpsertResponse:
    try:
        n = await uc.upsert(
            ctx, collection_id=collection_id,
            items=[item.model_dump() for item in req.items],
        )
        return UpsertResponse(
            collection_id=collection_id, upserted=n,
        )
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/collections/{collection_id}/query",
    response_model=QueryResponse,
)
async def query(
    collection_id: uuid.UUID,
    req: QueryRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> QueryResponse:
    try:
        from app.modules.vector_db.domain.enums import VectorMetric
        q = VectorQuery(
            vector=req.vector, top_k=req.top_k,
            metric=req.metric or VectorMetric.COSINE,
            filter=req.filter,
            include_metadata=req.include_metadata,
            score_threshold=req.score_threshold,
        )
        hits = await uc.query(
            ctx, collection_id=collection_id, query=q,
        )
        return QueryResponse(
            collection_id=collection_id,
            hits=[
                SearchHitOut.model_validate(h.model_dump())
                for h in hits
            ],
        )
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.delete(
    "/collections/{collection_id}/vectors/{vector_id}",
)
async def delete_vector(
    collection_id: uuid.UUID,
    vector_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> dict:
    try:
        ok_del = await uc.delete_vector(
            ctx, collection_id=collection_id,
            vector_id=vector_id,
        )
        return {"deleted": ok_del, "vector_id": str(vector_id)}
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.get(
    "/collections/{collection_id}/stats",
    response_model=StatsOut,
)
async def stats(
    collection_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> StatsOut:
    try:
        data = await uc.stats(ctx, collection_id)
        return StatsOut(**data)
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/collections/{collection_id}/indexes",
    response_model=IndexOut, status_code=201,
)
async def build_index(
    collection_id: uuid.UUID,
    req: IndexCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> IndexOut:
    try:
        idx = await uc.build_index(
            ctx, collection_id=collection_id,
            index_type=str(req.index_type), params=req.params,
        )
        return IndexOut.model_validate({
            "id": idx.id, "collection_id": idx.collection_id,
            "name": idx.name, "index_type": idx.index_type,
            "build_status": idx.build_status,
            "size_bytes": idx.size_bytes or 0,
        })
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise


@router.get(
    "/collections/{collection_id}/indexes",
    response_model=list[IndexOut],
)
async def list_indexes(
    collection_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
) -> list[IndexOut]:
    try:
        items = await uc.list_indexes(ctx, collection_id)
        return [
            IndexOut.model_validate({
                "id": i.id, "collection_id": i.collection_id,
                "name": i.name, "index_type": i.index_type,
                "build_status": i.build_status,
                "size_bytes": i.size_bytes or 0,
            })
            for i in items
        ]
    except (VectorDBError, AppError) as exc:
        _raise(exc)
        raise
