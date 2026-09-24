"""embeddings HTTP router"""
from __future__ import annotations
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.embeddings.application.exceptions import AppError
from app.modules.embeddings.application.use_case import (
    EmbeddingUseCase,
)
from app.modules.embeddings.domain.exceptions import EmbeddingError
from app.modules.embeddings.domain.value_objects import (
    BatchConfig, EmbeddingRequest,
)
from app.modules.embeddings.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.embeddings.presentation.schemas import (
    BatchRequest, BatchResponse, EmbeddingOut, EmbedOneRequest,
    EmbedRequest, EmbedResponse, EmbModelOut, EmbProviderOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, EmbeddingError):
        http = 400
        code = getattr(exc, "code", "DOMAIN_ERROR")
        if code == "NOT_FOUND":
            http = 404
        elif code == "VALIDATION_ERROR":
            http = 422
        elif code == "LIMIT_EXCEEDED":
            http = 402
        elif code == "RATE_LIMITED":
            http = 429
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


@router.post("", response_model=EmbedResponse)
async def embed(
    req: EmbedRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
) -> EmbedResponse:
    """TH: embed หลายข้อความ | EN: embed many"""
    try:
        results = await uc.embed(ctx, EmbeddingRequest(
            model=req.model, input=req.input,
            normalize=req.normalize, dimensions=req.dimensions,
        ))
        return EmbedResponse(
            model=req.model,
            embeddings=[
                EmbeddingOut(
                    vector=r.vector, dimension=r.dimension,
                    tokens=r.tokens, cached=r.cached,
                )
                for r in results
            ],
            count=len(results),
        )
    except (EmbeddingError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/one", response_model=EmbeddingOut)
async def embed_one(
    req: EmbedOneRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
) -> EmbeddingOut:
    """TH: embed ข้อความเดียว | EN: embed one"""
    try:
        results = await uc.embed(ctx, EmbeddingRequest(
            model=req.model, input=[req.text],
            normalize=req.normalize, dimensions=req.dimensions,
        ))
        if not results:
            raise HTTPException(
                status_code=500,
                detail={"code": "INTERNAL_ERROR",
                        "message": "no result"},
            )
        r = results[0]
        return EmbeddingOut(
            vector=r.vector, dimension=r.dimension,
            tokens=r.tokens, cached=r.cached,
        )
    except (EmbeddingError, AppError) as exc:
        _raise(exc)
        raise


@router.post(
    "/batch", response_model=BatchResponse, status_code=202,
)
async def embed_batch(
    req: BatchRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
) -> BatchResponse:
    """TH: batch embedding | EN: batch embedding"""
    try:
        batch_id = await uc.embed_batch(
            ctx, model_name=req.model, texts=req.texts,
            config=BatchConfig(
                batch_size=req.batch_size,
                max_concurrency=req.max_concurrency,
            ),
        )
        return BatchResponse(
            batch_id=batch_id, total=len(req.texts),
            status="PENDING",
        )
    except (EmbeddingError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/models", response_model=list[EmbModelOut])
async def list_models(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
) -> list[EmbModelOut]:
    try:
        items = await uc.list_models(ctx)
        return [
            EmbModelOut.model_validate({
                "id": m.id, "name": m.name,
                "display_name": m.display_name or "",
                "dimension": m.dimension,
                "max_tokens": m.max_tokens or 8192,
                "normalize": bool(m.normalize),
                "is_active": bool(m.is_active),
            })
            for m in items
        ]
    except (EmbeddingError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/providers", response_model=list[EmbProviderOut])
async def list_providers(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
) -> list[EmbProviderOut]:
    try:
        items = await uc.list_providers(ctx)
        return [
            EmbProviderOut.model_validate({
                "id": p.id, "name": p.name,
                "provider_type": p.provider_type,
                "base_url": p.base_url or "",
                "priority": p.priority or 100,
                "is_active": bool(p.is_active),
            })
            for p in items
        ]
    except (EmbeddingError, AppError) as exc:
        _raise(exc)
        raise
