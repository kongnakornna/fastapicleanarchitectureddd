"""AnnotationModel repository"""
from __future__ import annotations
import uuid
from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.yolo.application.exceptions import ApplicationError
from app.modules.yolo.infrastructure.models import AnnotationModel


class AnnotationModelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, ctx: Any, id: uuid.UUID):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.id == id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_paginated(self, ctx: Any, page: int = 1, size: int = 50):
        try:
            total_r = await self._session.execute(
                select(func.count()).select_from(AnnotationModel))
            total = int(total_r.scalar() or 0)
            result = await self._session.execute(
                select(AnnotationModel)
                .order_by(AnnotationModel.created_at.desc())
                .offset((page - 1) * size).limit(size))
            return list(result.scalars().all()), total
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_paginated failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def save(self, ctx: Any, row):
        try:
            self._session.add(row)
            await self._session.flush()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"annotation.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def update(self, ctx: Any, row):
        try:
            await self._session.flush()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"annotation.update failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.dataset_id == dataset_id))
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_by_dataset failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def bulk_create(self, ctx: Any, rows: list):
        try:
            self._session.add_all(rows)
            await self._session.flush()
            return rows
        except SQLAlchemyError as exc:
            logger.error(f"annotation.bulk_create failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def create(self, ctx: Any, row):
        return await self.save(ctx, row)

    async def find_by_training(self, ctx: Any, training_id: uuid.UUID):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.training_id == training_id))
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_by_training failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_active(self, ctx: Any):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.is_active.is_(True)))
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_active failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_deployed(self, ctx: Any):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.is_deployed.is_(True)))
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"annotation.find_deployed failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def update_status(self, ctx: Any, id: uuid.UUID, status: str) -> None:
        row = await self.find_by_id(ctx, id)
        if row:
            row.status = status
            await self._session.flush()

    async def set_best_model(self, ctx: Any, id: uuid.UUID, model_id: uuid.UUID) -> None:
        row = await self.find_by_id(ctx, id)
        if row:
            row.best_model_id = model_id
            await self._session.flush()

    async def find_by_hash(self, ctx: Any, content_hash: str):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.content_hash == content_hash)
                .limit(1))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            return None

    async def count_by_dataset(self, ctx: Any, dataset_id: uuid.UUID,
                                split: str | None = None) -> int:
        try:
            stmt = select(func.count()).select_from(AnnotationModel).where(
                AnnotationModel.dataset_id == dataset_id)
            if split:
                stmt = stmt.where(AnnotationModel.split == split)
            r = await self._session.execute(stmt)
            return int(r.scalar() or 0)
        except SQLAlchemyError:
            return 0

    async def find_by_image(self, ctx: Any, image_id: uuid.UUID):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.image_id == image_id))
            return list(result.scalars().all())
        except SQLAlchemyError:
            return []

    async def find_by_model(self, ctx: Any, model_id: uuid.UUID, limit: int = 100):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.model_id == model_id)
                .order_by(AnnotationModel.created_at.desc()).limit(limit))
            return list(result.scalars().all())
        except SQLAlchemyError:
            return []

    async def stats_by_model(self, ctx: Any, model_id: uuid.UUID, since):
        try:
            r = await self._session.execute(
                select(
                    func.count(AnnotationModel.id),
                    func.coalesce(func.avg(AnnotationModel.latency_ms), 0),
                    func.coalesce(func.max(AnnotationModel.latency_ms), 0),
                    func.coalesce(func.sum(AnnotationModel.detection_count), 0),
                ).where(
                    AnnotationModel.model_id == model_id,
                    AnnotationModel.created_at >= since))
            row = r.one()
            return {"count": int(row[0] or 0),
                    "avg_latency_ms": float(row[1] or 0),
                    "max_latency_ms": int(row[2] or 0),
                    "total_detections": int(row[3] or 0)}
        except SQLAlchemyError:
            return {"count": 0, "avg_latency_ms": 0.0,
                    "max_latency_ms": 0, "total_detections": 0}

    async def delete_by_image(self, ctx: Any, image_id: uuid.UUID) -> int:
        return 0

    async def soft_delete(self, ctx: Any, id: uuid.UUID) -> bool:
        row = await self.find_by_id(ctx, id)
        if row and hasattr(row, "status"):
            row.status = "ARCHIVED"
            await self._session.flush()
            return True
        return False

    async def class_distribution(self, ctx: Any, dataset_id: uuid.UUID) -> dict:
        return {}

    async def find_by_name(self, ctx: Any, name: str):
        try:
            result = await self._session.execute(
                select(AnnotationModel).where(AnnotationModel.name == name).limit(1))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            return None
