"""rag HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.modules.rag.application.exceptions import AppError
from app.modules.rag.application.use_case import RAGUseCase
from app.modules.rag.domain.exceptions import RAGError
from app.modules.rag.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.rag.presentation.schemas import (
    ChunkOut, CitationOut, DocumentDetailOut, DocumentOut,
    IngestRequest, IngestResponse, PipelineCreateRequest,
    PipelineOut, QueryRequest, QueryResponse, RunOut, UsageOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, RAGError):
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


@router.post(
    "/ingest", response_model=IngestResponse, status_code=201,
)
async def ingest(
    req: IngestRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> IngestResponse:
    try:
        doc = await uc.ingest(
            ctx, content=req.content,
            source_uri=req.source_uri,
            mime_type=req.mime_type, title=req.title,
            pipeline_id=req.pipeline_id,
            metadata=req.metadata,
        )
        return IngestResponse(
            document_id=doc.id, status=str(doc.status),
            chunk_count=doc.chunk_count or 0,
            size_bytes=doc.size_bytes or 0,
        )
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> QueryResponse:
    try:
        result = await uc.query(
            ctx, query=req.query,
            pipeline_id=req.pipeline_id,
            conversation_id=req.conversation_id,
            use_cache=req.use_cache,
        )
        return QueryResponse(
            run_id=result["run_id"],
            answer=result["answer"],
            citations=[
                CitationOut(**c)
                for c in result.get("citations", [])
            ],
            usage=UsageOut(**result.get("usage", {})),
            cached=bool(result.get("cached", False)),
        )
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[DocumentOut]:
    try:
        items = await uc.list_documents(
            ctx, limit=limit, offset=offset,
        )
        return [
            DocumentOut.model_validate({
                "id": d.id,
                "source_uri": d.source_uri or "",
                "mime_type": d.mime_type or "",
                "title": d.title or "",
                "status": d.status,
                "size_bytes": d.size_bytes or 0,
                "chunk_count": d.chunk_count or 0,
                "created_at": d.created_at,
            })
            for d in items
        ]
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.get(
    "/documents/{document_id}", response_model=DocumentDetailOut,
)
async def get_document(
    document_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> DocumentDetailOut:
    try:
        doc, chunks = await uc.get_document(ctx, document_id)
        return DocumentDetailOut.model_validate({
            "id": doc.id,
            "source_uri": doc.source_uri or "",
            "mime_type": doc.mime_type or "",
            "title": doc.title or "",
            "status": doc.status,
            "size_bytes": doc.size_bytes or 0,
            "chunk_count": doc.chunk_count or 0,
            "created_at": doc.created_at,
            "chunks": [
                ChunkOut.model_validate({
                    "id": c.id,
                    "ordinal": c.ordinal or 0,
                    "content": c.content or "",
                    "token_count": c.token_count or 0,
                })
                for c in chunks
            ],
        })
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> dict:
    try:
        ok_del = await uc.delete_document(ctx, document_id)
        return {"deleted": ok_del,
                "document_id": str(document_id)}
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/pipelines", response_model=list[PipelineOut])
async def list_pipelines(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> list[PipelineOut]:
    try:
        items = await uc.list_pipelines(ctx)
        return [
            PipelineOut.model_validate({
                "id": p.id, "name": p.name,
                "chunker_type": p.chunker_type,
                "chunk_size": p.chunk_size or 512,
                "chunk_overlap": p.chunk_overlap or 50,
                "retriever_type": p.retriever_type,
                "top_k": p.top_k or 5,
                "reranker_type": p.reranker_type,
                "embedding_model": p.embedding_model or "",
                "generation_model": p.generation_model or "",
                "is_active": bool(p.is_active),
            })
            for p in items
        ]
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/pipelines", response_model=PipelineOut, status_code=201,
)
async def create_pipeline(
    req: PipelineCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> PipelineOut:
    try:
        p = await uc.create_pipeline(ctx, **req.model_dump())
        return PipelineOut.model_validate({
            "id": p.id, "name": p.name,
            "chunker_type": p.chunker_type,
            "chunk_size": p.chunk_size or 512,
            "chunk_overlap": p.chunk_overlap or 50,
            "retriever_type": p.retriever_type,
            "top_k": p.top_k or 5,
            "reranker_type": p.reranker_type,
            "embedding_model": p.embedding_model or "",
            "generation_model": p.generation_model or "",
            "is_active": bool(p.is_active),
        })
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[RAGUseCase, Depends(get_use_case)],
) -> RunOut:
    try:
        r = await uc.get_run(ctx, run_id)
        return RunOut.model_validate({
            "id": r.id, "query": r.query or "",
            "answer": r.answer or "",
            "model_name": r.model_name or "",
            "latency_ms": r.latency_ms or 0,
            "total_tokens": r.total_tokens or 0,
            "cost_usd": r.cost_usd,
            "status": r.status,
            "created_at": r.created_at,
        })
    except (RAGError, AppError) as exc:
        _raise(exc)
        raise
