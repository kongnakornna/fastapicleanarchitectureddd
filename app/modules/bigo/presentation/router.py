"""bigo HTTP routers"""
from __future__ import annotations
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.bigo.application.use_case import BigOUseCase
from app.modules.bigo.domain.exceptions import (
    BigOError, KafkaConnectionError,
    LagThresholdExceededError, MemoryLimitExceededError,
)
from app.modules.bigo.infrastructure.pipeline import BigOPipeline
from app.modules.bigo.presentation.dependencies import (
    get_bigo_pipeline, get_bigo_use_case,
)
from app.modules.bigo.presentation.schemas import (
    AlertResponse, AlertTriggerRequest, BackpressureRequest,
    BackpressureResponse, KafkaLagMonitorRequest, KafkaLagResponse,
    KafkaTopicCreateRequest, KafkaTopicResponse,
    MemoryLeakResponse, MemorySnapshotResponse,
    MetricCreateRequest, MetricResponse,
    PipelineCheckRequest, PipelineCheckResponse,
    PipelineMemoryResponse, PipelineMetricsResponse,
    PipelineProcessRequest, PipelineProcessResponse,
    ProfileAnalyzeRequest, ProfileAnalyzeResponse,
    ProfileResponse, ResolveLeakResponse,
)

router = APIRouter(prefix="/bigo", tags=["Big-O Monitoring"])


class _CtxStub:
    def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self.user_id = user_id


async def _get_ctx() -> Any:
    try:
        from app.core.context import get_context
        return await get_context()
    except Exception:
        return _CtxStub(tenant_id=uuid.UUID(int=1), user_id=uuid.UUID(int=2))


def _error_status(exc: Exception) -> int:
    if isinstance(exc, LagThresholdExceededError):
        return status.HTTP_429_TOO_MANY_REQUESTS
    if isinstance(exc, MemoryLimitExceededError):
        return status.HTTP_507_INSUFFICIENT_STORAGE
    if isinstance(exc, KafkaConnectionError):
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_400_BAD_REQUEST


@router.post("/profiles/analyze", response_model=ProfileAnalyzeResponse,
             summary="Analyze function complexity", operation_id="bigo_analyze_function")
async def analyze_function(
    payload: ProfileAnalyzeRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> ProfileAnalyzeResponse:
    ctx = await _get_ctx()

    def _stub(n: int) -> int:
        return sum(range(n))

    try:
        result = await uc.analyze_function(
            ctx, fn=_stub, name=payload.function_name,
            module=payload.module, sizes=payload.sizes or None,
        )
        return ProfileAnalyzeResponse(**result)
    except BigOError as e:
        raise HTTPException(_error_status(e), detail=str(e)) from e


@router.get("/profiles", response_model=list[ProfileResponse],
            summary="List profiles", operation_id="bigo_list_profiles")
async def list_profiles(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
    function_name: str = "", days: int = 7, limit: int = 100,
) -> list[ProfileResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_profiles(ctx, function_name=function_name, since_days=days, limit=limit)
    return [ProfileResponse(**r) for r in rows]


@router.post("/memory/snapshots", response_model=MemorySnapshotResponse,
             summary="Take memory snapshot", operation_id="bigo_take_snapshot")
async def take_snapshot(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> MemorySnapshotResponse:
    ctx = await _get_ctx()
    try:
        result = await uc.take_memory_snapshot(ctx)
        return MemorySnapshotResponse(**result)
    except BigOError as e:
        raise HTTPException(_error_status(e), detail=str(e)) from e


@router.post("/memory/leaks/detect", response_model=list[MemoryLeakResponse],
             summary="Detect memory leaks", operation_id="bigo_detect_leaks")
async def detect_leaks(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
    threshold_mb_per_hour: float = 10.0,
) -> list[MemoryLeakResponse]:
    ctx = await _get_ctx()
    rows = await uc.detect_memory_leaks(ctx, threshold_mb_per_hour=threshold_mb_per_hour)
    return [MemoryLeakResponse(**r) for r in rows]


@router.get("/memory/leaks", response_model=list[MemoryLeakResponse],
            summary="List memory leaks", operation_id="bigo_list_leaks")
async def list_leaks(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
    status_filter: str = "OPEN", limit: int = 50,
) -> list[MemoryLeakResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_leaks(ctx, status=status_filter, limit=limit)
    return [MemoryLeakResponse(**r) for r in rows]


@router.post("/memory/leaks/{leak_id}/resolve", response_model=ResolveLeakResponse,
             summary="Resolve memory leak", operation_id="bigo_resolve_leak")
async def resolve_leak(
    leak_id: uuid.UUID,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> ResolveLeakResponse:
    ctx = await _get_ctx()
    result = await uc.resolve_leak(ctx, leak_id)
    return ResolveLeakResponse(**result)


@router.post("/kafka/topics", response_model=KafkaTopicResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Register Kafka topic", operation_id="bigo_register_topic")
async def register_topic(
    payload: KafkaTopicCreateRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> KafkaTopicResponse:
    ctx = await _get_ctx()
    result = await uc.register_topic(
        ctx, name=payload.name, partitions=payload.partitions,
        replication=payload.replication,
        retention_ms=payload.retention_ms,
        max_message_bytes=payload.max_message_bytes,
    )
    return KafkaTopicResponse(**result)


@router.get("/kafka/topics", response_model=list[KafkaTopicResponse],
            summary="List Kafka topics", operation_id="bigo_list_topics")
async def list_topics(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> list[KafkaTopicResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_topics(ctx)
    return [KafkaTopicResponse(**r) for r in rows]


@router.post("/kafka/lag/monitor", response_model=KafkaLagResponse,
             summary="Monitor consumer lag", operation_id="bigo_monitor_lag")
async def monitor_lag(
    payload: KafkaLagMonitorRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> KafkaLagResponse:
    ctx = await _get_ctx()
    try:
        result = await uc.monitor_lag(
            ctx, group_id=payload.group_id,
            topic=payload.topic, threshold=payload.threshold,
        )
        return KafkaLagResponse(**result)
    except BigOError as e:
        raise HTTPException(_error_status(e), detail=str(e)) from e


@router.post("/kafka/backpressure/activate", response_model=BackpressureResponse,
             summary="Activate backpressure", operation_id="bigo_bp_activate")
async def activate_bp(
    payload: BackpressureRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> BackpressureResponse:
    ctx = await _get_ctx()
    result = await uc.activate_backpressure(ctx, topic=payload.topic, reason=payload.reason)
    return BackpressureResponse(**result)


@router.post("/kafka/backpressure/deactivate", response_model=BackpressureResponse,
             summary="Deactivate backpressure", operation_id="bigo_bp_deactivate")
async def deactivate_bp(
    payload: BackpressureRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> BackpressureResponse:
    ctx = await _get_ctx()
    result = await uc.deactivate_backpressure(ctx, payload.topic)
    return BackpressureResponse(**result)


@router.post("/metrics", response_model=MetricResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Record metric", operation_id="bigo_record_metric")
async def record_metric(
    payload: MetricCreateRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> MetricResponse:
    ctx = await _get_ctx()
    result = await uc.record_metric(
        ctx, kind=payload.kind, name=payload.name,
        value=payload.value, unit=payload.unit, labels=payload.labels,
    )
    return MetricResponse(**result)


@router.get("/metrics", response_model=list[MetricResponse],
            summary="List metrics", operation_id="bigo_list_metrics")
async def list_metrics(
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
    kind: str = "", days: int = 1, limit: int = 500,
) -> list[MetricResponse]:
    ctx = await _get_ctx()
    rows = await uc.get_metrics(ctx, kind=kind, days=days, limit=limit)
    return [MetricResponse(**r) for r in rows]


@router.post("/alerts", response_model=AlertResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Trigger alert", operation_id="bigo_trigger_alert")
async def trigger_alert(
    payload: AlertTriggerRequest,
    uc: Annotated[BigOUseCase, Depends(get_bigo_use_case)],
) -> AlertResponse:
    ctx = await _get_ctx()
    result = await uc.trigger_alert(
        ctx, severity=payload.severity, kind=payload.kind,
        message=payload.message, payload=payload.payload,
    )
    return AlertResponse(**result)


@router.post("/pipeline/check", response_model=PipelineCheckResponse,
             summary="Static Big-O policy check", operation_id="bigo_pipeline_check")
async def pipeline_check(
    payload: PipelineCheckRequest,
    pipe: Annotated[BigOPipeline, Depends(get_bigo_pipeline)],
) -> PipelineCheckResponse:
    status_, priority = pipe.monitor.check(payload.n, payload.algorithm_type)
    return PipelineCheckResponse(
        n=payload.n, algorithm_type=payload.algorithm_type,
        status=status_, priority=priority.value,
    )


@router.post("/pipeline/process", response_model=PipelineProcessResponse,
             summary="Process synthetic batch", operation_id="bigo_pipeline_process")
async def pipeline_process(
    payload: PipelineProcessRequest,
    pipe: Annotated[BigOPipeline, Depends(get_bigo_pipeline)],
) -> PipelineProcessResponse:
    data = list(range(payload.n))
    report = pipe.process(
        data, algorithm_type=payload.algorithm_type,
        topic=payload.topic, cache_key=payload.cache_key,
    )
    return PipelineProcessResponse(**report.to_dict())


@router.get("/pipeline/metrics", response_model=PipelineMetricsResponse,
            summary="Get pipeline metrics", operation_id="bigo_pipeline_metrics")
async def pipeline_metrics(
    pipe: Annotated[BigOPipeline, Depends(get_bigo_pipeline)],
) -> PipelineMetricsResponse:
    snap = pipe.metrics_snapshot()
    return PipelineMetricsResponse(**snap)


@router.get("/pipeline/memory", response_model=PipelineMemoryResponse,
            summary="Get pipeline memory stats", operation_id="bigo_pipeline_memory")
async def pipeline_memory(
    pipe: Annotated[BigOPipeline, Depends(get_bigo_pipeline)],
) -> PipelineMemoryResponse:
    stats = pipe.memory.stats()
    return PipelineMemoryResponse(**stats)
