from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.batch.domain.entities.batch_job import BatchJob
from app.modules.batch.domain.entities.batch_job_log import BatchJobLog


class BatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, job_id: UUID) -> BatchJob | None:
        result = await self._session.execute(
            select(BatchJob).where(BatchJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[BatchJob], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(BatchJob)
            .where(BatchJob.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(BatchJob)
            .where(BatchJob.is_active.is_(True))
            .order_by(BatchJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, job: BatchJob) -> BatchJob:
        self._session.add(job)
        await self._session.flush()
        return job

    async def update(self, job: BatchJob) -> BatchJob:
        await self._session.flush()
        return job

    async def delete(self, job_id: UUID) -> bool:
        job = await self.find_by_id(job_id)
        if job:
            job.is_active = False
            await self._session.flush()
            return True
        return False

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(BatchJob)
            .where(BatchJob.is_active.is_(True))
        )
        return result.scalar() or 0

    async def find_logs_by_job_id(
        self, job_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[BatchJobLog], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(BatchJobLog)
            .where(BatchJobLog.job_id == job_id)
        )
        total = count_result.scalar() or 0
        query = (
            select(BatchJobLog)
            .where(BatchJobLog.job_id == job_id)
            .order_by(BatchJobLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create_log(self, log: BatchJobLog) -> BatchJobLog:
        self._session.add(log)
        await self._session.flush()
        return log
