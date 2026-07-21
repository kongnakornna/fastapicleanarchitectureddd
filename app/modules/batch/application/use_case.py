from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.modules.batch.domain.entities.batch_job import BatchJob
from app.modules.batch.domain.entities.batch_job_log import BatchJobLog
from app.modules.batch.infrastructure.batch_repository import BatchRepository


class BatchUseCase:
    def __init__(self, batch_repository: BatchRepository) -> None:
        self._batch_repo = batch_repository

    async def get_jobs(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[BatchJob], int]:
        return await self._batch_repo.find_all_paginated(page, page_size)

    async def get_job(self, job_id: UUID) -> BatchJob | None:
        return await self._batch_repo.find_by_id(job_id)

    async def create_job(self, job: BatchJob) -> BatchJob:
        return await self._batch_repo.create(job)

    async def update_job(self, job_id: UUID, values: dict) -> BatchJob | None:
        job = await self._batch_repo.find_by_id(job_id)
        if not job:
            return None
        for key, value in values.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        return await self._batch_repo.update(job)

    async def delete_job(self, job_id: UUID) -> bool:
        return await self._batch_repo.delete(job_id)

    async def run_job(self, job_id: UUID) -> BatchJob | None:
        job = await self._batch_repo.find_by_id(job_id)
        if not job:
            return None
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.total_count = 10
        job.success_count = 8
        job.fail_count = 2
        job.status = "completed"
        job.finished_at = datetime.now(UTC)
        await self._batch_repo.update(job)
        log = BatchJobLog(
            job_id=job.id,
            message="Job completed successfully (simulated)",
            level="info",
        )
        await self._batch_repo.create_log(log)
        return job

    async def get_job_logs(
        self, job_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[BatchJobLog], int]:
        return await self._batch_repo.find_logs_by_job_id(job_id, page, page_size)
