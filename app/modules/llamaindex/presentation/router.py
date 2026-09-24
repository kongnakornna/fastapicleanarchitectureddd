"""llamaindex HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.llamaindex.application.exceptions import AppError
from app.modules.llamaindex.application.use_case import LlamaIndexUseCase
from app.modules.llamaindex.domain.exceptions import LIError
from app.modules.llamaindex.domain.value_objects import (
    IndexSpec, QueryEngineSpec,
)
from app.modules.llamaindex.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.llamaindex.presentation.schemas import (
    DocumentOut, IndexCreateRequest, IndexOut, IngestRequest,
    IngestResponse, QueryEngineCreateRequest, QueryEngineOut,
    QueryRequest, QueryResponse, RunOut, SourceNodeOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/li", tags=["LlamaIndex"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, LIError):
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


@router.get("/indexes", response_model=list[IndexOut])
async def list_indexes(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> list[IndexOut]:
    """TH: list indexes | EN: list indexes"""
    try:
        items = await uc.list_indexes(ctx)
        return [IndexOut.model_validate(i.model_dump()) for i in items]
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/indexes", response_model=IndexOut, status_code=201)
async def create_index(
    req: IndexCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> IndexOut:
    """TH: สร้าง index | EN: create index"""
    try:
        spec = IndexSpec(
            name=req.name, index_type=req.index_type,
            embed_model=req.embed_model,
            storage_kind=req.storage_kind, config=req.config,
        )
        row = await uc.create_index(ctx, spec)
        return IndexOut.model_validate(row.model_dump())
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/indexes/{index_id}/ingest", response_model=IngestResponse)
async def ingest(
    index_id: uuid.UUID,
    req: IngestRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> IngestResponse:
    """TH: ingest document | EN: ingest document"""
    try:
        doc = await uc.ingest(
            ctx, index_id=index_id, content=req.content,
            source_uri=req.source_uri, mime_type=req.mime_type,
            title=req.title, chunk_size=req.chunk_size,
            chunk_overlap=req.chunk_overlap,
        )
        return IngestResponse(
            document_id=doc.id, index_id=doc.index_id,
            status=doc.status,
            node_count=int(doc.node_count or 0),
        )
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/indexes/{index_id}/query", response_model=QueryResponse)
async def query_index(
    index_id: uuid.UUID,
    req: QueryRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> QueryResponse:
    """TH: query index | EN: query index"""
    try:
        out = await uc.query(
            ctx, index_id=index_id, query=req.query,
            query_engine_id=req.query_engine_id,
            top_k=req.top_k,
            response_mode=str(req.response_mode) if req.response_mode else None,
            model=req.model,
        )
        return QueryResponse(
            run_id=out["run_id"],
            answer=out.get("answer", ""),
            source_nodes=[
                SourceNodeOut(**{k: v for k, v in sn.items()
                                 if k in SourceNodeOut.model_fields})
                for sn in out.get("source_nodes", [])
            ],
            latency_ms=int(out.get("latency_ms", 0)),
            tokens_used=int(out.get("tokens_used", 0)),
            response_mode=str(out.get("response_mode", "compact")),
        )
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/indexes/{index_id}/query-engines",
             response_model=QueryEngineOut, status_code=201)
async def create_query_engine(
    index_id: uuid.UUID,
    req: QueryEngineCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> QueryEngineOut:
    """TH: สร้าง query engine | EN: create query engine"""
    try:
        spec = QueryEngineSpec(
            name=req.name, retriever_type=req.retriever_type,
            top_k=req.top_k, response_mode=req.response_mode,
            similarity_top_k=req.similarity_top_k,
        )
        row = await uc.create_query_engine(
            ctx, index_id=index_id, spec=spec,
        )
        return QueryEngineOut.model_validate(row.model_dump())
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/indexes/{index_id}/query-engines",
            response_model=list[QueryEngineOut])
async def list_query_engines(
    index_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> list[QueryEngineOut]:
    """TH: list query engines | EN: list query engines"""
    try:
        items = await uc.list_query_engines(ctx, index_id)
        return [QueryEngineOut.model_validate(q.model_dump()) for q in items]
    except (LIError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
) -> RunOut:
    """TH: ดึง run | EN: get run"""
    try:
        r = await uc.get_run(ctx, run_id)
        return RunOut.model_validate(r.model_dump())
    except (LIError, AppError) as exc:
        _raise(exc)
        raise
