"""ai_evaluation DI container"""
from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_evaluation.application.use_case import (
    AIEvaluationUseCase,
)
from app.modules.ai_evaluation.infrastructure.repositories import (
    EvalDatasetRepository, EvalMetricRepository,
    EvalReportRepository, EvalResultRepository,
    EvalRunRepository, EvalTestCaseRepository,
)
from app.modules.ai_evaluation.infrastructure.services import (
    AnswerRelevanceEvaluator, ContextPrecisionEvaluator,
    ContextRecallEvaluator, ExactMatchEvaluator, F1Evaluator,
    FaithfulnessEvaluator, HallucinationEvaluator,
    LoggingEventBus, MRREvaluator, NDCGEvaluator, RAGASEvaluator,
    RougeEvaluator,
)


@dataclass
class Ctx:
    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID]


async def get_db(request: Request) -> AsyncSession:
    session = getattr(request.app.state, "db_session", None)
    if session is None:
        sm = getattr(request.app.state, "session_factory", None)
        if sm is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DB_ERROR", "message": "db session unavailable"},
            )
        session = sm()
    return session


async def get_ctx(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> Ctx:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_ERROR", "message": "X-Tenant-Id required"},
        )
    try:
        tenant_id = uuid.UUID(x_tenant_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "invalid tenant id"},
        ) from exc
    user_id: Optional[uuid.UUID] = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError:
            user_id = None
    return Ctx(tenant_id=tenant_id, user_id=user_id)


async def get_use_case(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AIEvaluationUseCase:
    judge = getattr(request.app.state, "eval_judge", None)
    target = getattr(request.app.state, "eval_target", None)
    bus = getattr(request.app.state, "eval_event_bus", None) or LoggingEventBus()

    evaluators = {
        "exact_match": ExactMatchEvaluator(),
        "f1": F1Evaluator(),
        "rouge": RougeEvaluator(),
        "mrr": MRREvaluator(),
        "ndcg": NDCGEvaluator(),
        "context_precision": ContextPrecisionEvaluator(),
        "context_recall": ContextRecallEvaluator(),
        "faithfulness": FaithfulnessEvaluator(judge),
        "answer_relevance": AnswerRelevanceEvaluator(judge),
        "hallucination": HallucinationEvaluator(judge),
        "ragas": RAGASEvaluator(judge),
    }

    return AIEvaluationUseCase(
        datasets=EvalDatasetRepository(db),
        cases=EvalTestCaseRepository(db),
        runs=EvalRunRepository(db),
        metrics=EvalMetricRepository(db),
        results=EvalResultRepository(db),
        reports=EvalReportRepository(db),
        evaluators=evaluators,
        target_invoker=target,
        llm_judge=judge,
        event_bus=bus,
    )
