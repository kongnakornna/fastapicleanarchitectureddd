"""bigo DI container"""
from __future__ import annotations
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.modules.bigo.application.use_case import BigOUseCase
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.infrastructure.kafka_repository import (
    SqlKafkaConsumerRepository, SqlKafkaQueueRepository,
    SqlKafkaTopicRepository,
)
from app.modules.bigo.infrastructure.management_service import ManagementService
from app.modules.bigo.infrastructure.memory_repository import SqlMemoryRepository
from app.modules.bigo.infrastructure.metric_repository import SqlMetricRepository
from app.modules.bigo.infrastructure.pipeline import BigOPipeline
from app.modules.bigo.infrastructure.pipeline_report_repository import (
    SqlPipelineReportRepository,
)
from app.modules.bigo.infrastructure.profile_repository import SqlProfileRepository
from app.modules.bigo.infrastructure.redis_cache import RedisCache
from app.modules.bigo.infrastructure.services import (
    DefaultComplexityAnalyzer, DefaultKafkaAdmin,
    DefaultMemoryProfiler, LoggingEventBus,
    RedisBackpressureController, RedisCache as LegacyCache,
)
from app.modules.bigo.infrastructure.websocket_manager import WebSocketManager

_complexity = DefaultComplexityAnalyzer()
_memory = DefaultMemoryProfiler()
_kafka: DefaultKafkaAdmin | None = None
_pipeline: BigOPipeline | None = None
_ws_manager: WebSocketManager | None = None
_cache: RedisCache | None = None


def _get_kafka() -> DefaultKafkaAdmin:
    global _kafka
    if _kafka is None:
        try:
            from app.core.settings import settings
            bootstrap = getattr(settings, "KAFKA_BOOTSTRAP", "localhost:9092")
        except Exception:
            bootstrap = "localhost:9092"
        _kafka = DefaultKafkaAdmin(bootstrap)
    return _kafka


async def _get_redis() -> Any:
    try:
        from app.core.redis import get_redis
        return await get_redis()
    except Exception:
        return None


def get_bigo_pipeline() -> BigOPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = BigOPipeline(PipelineConfig())
    return _pipeline


def get_ws_manager() -> WebSocketManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager


async def get_cache() -> RedisCache:
    global _cache
    if _cache is None:
        redis = await _get_redis()
        _cache = RedisCache(redis=redis, namespace="bigo", default_ttl=300)
    return _cache


async def get_management_service() -> ManagementService:
    cache = await get_cache()
    return ManagementService(
        pipeline=get_bigo_pipeline(),
        cache=cache,
        ws_manager=get_ws_manager(),
    )


async def get_bigo_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BigOUseCase:
    redis = await _get_redis()
    return BigOUseCase(
        metric_repo=SqlMetricRepository(session),
        profile_repo=SqlProfileRepository(session),
        memory_repo=SqlMemoryRepository(session),
        topic_repo=SqlKafkaTopicRepository(session),
        queue_repo=SqlKafkaQueueRepository(session),
        consumer_repo=SqlKafkaConsumerRepository(session),
        complexity=_complexity,
        memory=_memory,
        kafka=_get_kafka(),
        backpressure=RedisBackpressureController(redis),
        cache=LegacyCache(redis),
        event_bus=LoggingEventBus(),
        pipeline_report_repo=SqlPipelineReportRepository(session),
    )
