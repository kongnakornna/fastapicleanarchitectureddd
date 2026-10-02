"""YOLO DI container"""
from __future__ import annotations
import uuid
from typing import Annotated, Any

from fastapi import Depends

from app.modules.yolo.application.use_case import YOLOUseCase
from app.modules.yolo.infrastructure.annotation_repository import AnnotationModelRepository
from app.modules.yolo.infrastructure.caches import NoopCache, RedisYOLOCache
from app.modules.yolo.infrastructure.class_repository import ClassModelRepository
from app.modules.yolo.infrastructure.dataset_repository import DatasetModelRepository
from app.modules.yolo.infrastructure.image_repository import ImageModelRepository
from app.modules.yolo.infrastructure.inference_repository import InferenceModelRepository
from app.modules.yolo.infrastructure.model_repository import ModelModelRepository
from app.modules.yolo.infrastructure.training_repository import TrainingModelRepository
from app.modules.yolo.infrastructure.services import (
    AlbumentationsAugmenter, ArtifactStore, LRUModelRegistry,
    NoopEventBus, UltralyticsDetector, UltralyticsExporter,
    UltralyticsTrainer,
)

_registry: LRUModelRegistry | None = None
_trainer: UltralyticsTrainer | None = None
_exporter: UltralyticsExporter | None = None
_augmenter: AlbumentationsAugmenter | None = None
_store: ArtifactStore | None = None


def _get_registry() -> LRUModelRegistry:
    global _registry
    if _registry is None:
        _registry = LRUModelRegistry(max_size=4)
    return _registry


def _get_trainer() -> UltralyticsTrainer:
    global _trainer
    if _trainer is None:
        _trainer = UltralyticsTrainer()
    return _trainer


def _get_exporter() -> UltralyticsExporter:
    global _exporter
    if _exporter is None:
        _exporter = UltralyticsExporter()
    return _exporter


def _get_augmenter() -> AlbumentationsAugmenter:
    global _augmenter
    if _augmenter is None:
        _augmenter = AlbumentationsAugmenter()
    return _augmenter


def _get_store() -> ArtifactStore:
    global _store
    if _store is None:
        _store = ArtifactStore()
    return _store


async def _get_redis() -> Any:
    try:
        from app.core.redis import get_redis
        return await get_redis()
    except Exception:
        return None


async def _get_event_bus() -> Any:
    try:
        from app.core.events import get_event_bus
        return await get_event_bus()
    except Exception:
        return NoopEventBus()


class _NoopRateLimiter:
    async def check(self, tenant_id: Any, user_id: Any, cost: int) -> bool:
        return True

    async def increment(self, tenant_id: Any, user_id: Any, cost: int) -> None:
        return None


class CtxStub:
    def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID | None = None):
        self.tenant_id = tenant_id
        self.user_id = user_id


async def get_ctx() -> Any:
    try:
        from app.core.context import get_context
        return await get_context()
    except Exception:
        return CtxStub(tenant_id=uuid.UUID(int=1), user_id=uuid.UUID(int=2))


async def _get_session() -> Any:
    try:
        from app.core.db import get_session
        async for s in get_session():
            yield s
    except Exception:
        yield None


async def get_yolo_use_case(
    session: Annotated[Any, Depends(_get_session)] = None,
) -> YOLOUseCase:
    redis = await _get_redis()
    bus = await _get_event_bus()
    cache = RedisYOLOCache(redis) if redis else NoopCache()
    registry = _get_registry()
    return YOLOUseCase(
        dataset_repo=DatasetModelRepository(session),
        class_repo=ClassModelRepository(session),
        image_repo=ImageModelRepository(session),
        annotation_repo=AnnotationModelRepository(session),
        training_repo=TrainingModelRepository(session),
        model_repo=ModelModelRepository(session),
        inference_repo=InferenceModelRepository(session),
        trainer=_get_trainer(),
        detector=UltralyticsDetector(registry),
        model_registry=registry,
        exporter=_get_exporter(),
        artifact_store=_get_store(),
        cache=cache,
        rate_limiter=_NoopRateLimiter(),
        event_bus=bus,
    )
