"""ai_evaluation repositories — SQLAlchemy 2.0 async"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_evaluation.application.exceptions import AppError
from app.modules.ai_evaluation.infrastructure.models import (
    EvalDatasetModel, EvalMetricModel, EvalReportModel,
    EvalResultModel, EvalRunModel, EvalTestCaseModel,
)


class EvalDatasetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, ds: EvalDatasetModel) -> EvalDatasetModel:
        try:
            self._session.add(ds)
            await self._session.flush()
            return ds
        except SQLAlchemyError as exc:
            logger.error(f"dataset.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> EvalDatasetModel | None:
        try:
            result = await self._session.execute(
                select(EvalDatasetModel).where(EvalDatasetModel.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"dataset.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> EvalDatasetModel | None:
        try:
            result = await self._session.execute(
                select(EvalDatasetModel).where(EvalDatasetModel.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"dataset.find_by_name failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all(self, ctx: object) -> list[EvalDatasetModel]:
        try:
            result = await self._session.execute(
                select(EvalDatasetModel).order_by(EvalDatasetModel.name)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"dataset.list failed: {exc}")
            raise AppError(str(exc)) from exc


class EvalTestCaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, cases: list) -> int:
        try:
            for c in cases:
                self._session.add(c)
            await self._session.flush()
            return len(cases)
        except SQLAlchemyError as exc:
            logger.error(f"case.create_many failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_dataset(self, ctx: object, dataset_id: uuid.UUID) -> list:
        try:
            result = await self._session.execute(
                select(EvalTestCaseModel).where(
                    EvalTestCaseModel.dataset_id == dataset_id
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"case.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def count_by_dataset(self, ctx: object, dataset_id: uuid.UUID) -> int:
        try:
            result = await self._session.execute(
                select(func.count()).select_from(EvalTestCaseModel).where(
                    EvalTestCaseModel.dataset_id == dataset_id
                )
            )
            return int(result.scalar() or 0)
        except SQLAlchemyError as exc:
            logger.error(f"case.count failed: {exc}")
            raise AppError(str(exc)) from exc


class EvalRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, r: EvalRunModel) -> EvalRunModel:
        try:
            self._session.add(r)
            await self._session.flush()
            return r
        except SQLAlchemyError as exc:
            logger.error(f"run.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> EvalRunModel | None:
        try:
            result = await self._session.execute(
                select(EvalRunModel).where(EvalRunModel.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"run.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def update(self, ctx: object, r: EvalRunModel) -> EvalRunModel:
        try:
            await self._session.flush()
            return r
        except SQLAlchemyError as exc:
            logger.error(f"run.update failed: {exc}")
            raise AppError(str(exc)) from exc

    async def list_by_tenant(self, ctx: object, limit: int = 50) -> list:
        try:
            result = await self._session.execute(
                select(EvalRunModel)
                .order_by(EvalRunModel.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"run.list failed: {exc}")
            raise AppError(str(exc)) from exc


class EvalMetricRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, m: EvalMetricModel) -> EvalMetricModel:
        try:
            self._session.add(m)
            await self._session.flush()
            return m
        except SQLAlchemyError as exc:
            logger.error(f"metric.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> EvalMetricModel | None:
        try:
            result = await self._session.execute(
                select(EvalMetricModel).where(EvalMetricModel.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"metric.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all(self, ctx: object) -> list[EvalMetricModel]:
        try:
            result = await self._session.execute(
                select(EvalMetricModel).order_by(EvalMetricModel.name)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"metric.list failed: {exc}")
            raise AppError(str(exc)) from exc


class EvalResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, results: list) -> int:
        try:
            for r in results:
                self._session.add(r)
            await self._session.flush()
            return len(results)
        except SQLAlchemyError as exc:
            logger.error(f"result.create_many failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
        try:
            result = await self._session.execute(
                select(EvalResultModel).where(EvalResultModel.run_id == run_id)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"result.find failed: {exc}")
            raise AppError(str(exc)) from exc


class EvalReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, r: EvalReportModel) -> EvalReportModel:
        try:
            self._session.add(r)
            await self._session.flush()
            return r
        except SQLAlchemyError as exc:
            logger.error(f"report.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> EvalReportModel | None:
        try:
            result = await self._session.execute(
                select(EvalReportModel).where(EvalReportModel.run_id == run_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"report.find failed: {exc}")
            raise AppError(str(exc)) from exc
