"""structured_outputs HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.structured_outputs.application.exceptions import AppError
from app.modules.structured_outputs.application.use_case import (
    StructuredOutputsUseCase,
)
from app.modules.structured_outputs.domain.exceptions import SOError
from app.modules.structured_outputs.domain.value_objects import SchemaSpec
from app.modules.structured_outputs.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.structured_outputs.presentation.schemas import (
    GenerateRequest, GenerateResponse, OutputOut, SchemaCreateRequest,
    SchemaOut, ValidateRequest, ValidateResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/so", tags=["StructuredOutputs"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, SOError):
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


@router.get("/schemas", response_model=list[SchemaOut])
async def list_schemas(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
) -> list[SchemaOut]:
    """TH: list schemas | EN: list schemas"""
    try:
        items = await uc.list_schemas(ctx)
        return [SchemaOut.model_validate(s.model_dump()) for s in items]
    except (SOError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/schemas", response_model=SchemaOut, status_code=201)
async def create_schema(
    req: SchemaCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
) -> SchemaOut:
    """TH: ลงทะเบียน schema | EN: register schema"""
    try:
        spec = SchemaSpec(
            name=req.name, description=req.description,
            json_schema=req.json_schema,
            pydantic_model=req.pydantic_model,
            strict=req.strict, strategy=req.strategy,
        )
        row = await uc.register_schema(ctx, spec)
        return SchemaOut.model_validate(row.model_dump())
    except (SOError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    req: GenerateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
) -> GenerateResponse:
    """TH: generate structured output | EN: generate structured"""
    try:
        result = await uc.generate(
            ctx, model=req.model, prompt=req.prompt,
            schema_id=req.schema_id,
            temperature=req.temperature,
            max_repairs=req.max_repairs,
        )
        return GenerateResponse(
            status=str(result.status),
            parsed=result.parsed,
            is_valid=result.is_valid,
            attempts=result.attempts,
            errors=result.errors,
            tokens_used=result.tokens_used,
            latency_ms=result.latency_ms,
        )
    except (SOError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/outputs/{output_id}", response_model=OutputOut)
async def get_output(
    output_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
) -> OutputOut:
    """TH: ดึง output | EN: get output"""
    try:
        o = await uc.get_output(ctx, output_id)
        return OutputOut.model_validate(o.model_dump())
    except (SOError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/validate", response_model=ValidateResponse)
async def validate(
    req: ValidateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
) -> ValidateResponse:
    """TH: validate payload | EN: validate payload"""
    try:
        out = await uc.validate_raw(
            ctx, schema_id=req.schema_id, payload=req.payload,
        )
        return ValidateResponse(
            is_valid=out.get("is_valid", False),
            errors=out.get("errors", []),
        )
    except (SOError, AppError) as exc:
        _raise(exc)
        raise
