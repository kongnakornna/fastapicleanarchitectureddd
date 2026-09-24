"""ai_evaluation HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.ai_evaluation.application.exceptions import AppError
from app.modules.ai_evaluation.application.use_case import (
    AIEvaluationUseCase,
)
from app.modules.ai_evaluation.application.utils import json_loads_safe
from app.modules.ai_evaluation.domain.exceptions import EvalError
from app.modules.ai_evaluation.domain.value_objects import (
    EvalConfig, EvalTarget,
)
from app.modules.ai_evaluation.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.ai_evaluation.presentation.schemas import (
    DatasetCreateRequest, DatasetOut, MetricOut, ReportOut,
    RunOut, RunRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eval", tags=["AIEvaluation"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, EvalError):
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


@router.get("/datasets", response_model=list[DatasetOut])
async def list_datasets(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> list[DatasetOut]:
    try:
        items = await uc.list_datasets(ctx)
        return [DatasetOut.model_validate(d.model_dump()) for d in items]
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/datasets", response_model=DatasetOut, status_code=201)
async def create_dataset(
    req: DatasetCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> DatasetOut:
    try:
        ds = await uc.create_dataset(
            ctx, name=req.name, description=req.description,
            task_type=str(req.task_type),
            cases=[c.model_dump() for c in req.cases],
            metadata=req.metadata,
        )
        return DatasetOut.model_validate(ds.model_dump())
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/run", response_model=RunOut)
async def run_evaluation(
    req: RunRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> RunOut:
    try:
        target = EvalTarget(
            kind=req.target_kind, ref=req.target_ref,
            pipeline_id=req.pipeline_id,
        )
        config = EvalConfig(
            metrics=req.metrics, sample_size=req.sample_size,
            temperature=req.temperature, seed=req.seed,
            concurrency=req.concurrency,
        )
        run = await uc.run_evaluation(
            ctx, dataset_id=req.dataset_id,
            target=target, config=config,
        )
        return RunOut.model_validate(run.model_dump())
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> RunOut:
    try:
        r = await uc.get_run(ctx, run_id)
        return RunOut.model_validate(r.model_dump())
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}/report", response_model=ReportOut)
async def get_report(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> ReportOut:
    try:
        r = await uc.get_report(ctx, run_id)
        return ReportOut(
            id=r.id, run_id=r.run_id,
            summary=json_loads_safe(r.summary_json, {}),
            passed=r.passed, generated_at=r.generated_at,
        )
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/metrics", response_model=list[MetricOut])
async def list_metrics(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
) -> list[MetricOut]:
    try:
        items = await uc.list_metrics(ctx)
        return [MetricOut.model_validate(m.model_dump()) for m in items]
    except (EvalError, AppError) as exc:
        _raise(exc)
        raise
