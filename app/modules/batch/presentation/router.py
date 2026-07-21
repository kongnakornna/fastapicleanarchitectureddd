from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.batch.application.use_case import BatchUseCase
from app.modules.batch.domain.entities.batch_job import BatchJob
from app.modules.batch.infrastructure.batch_repository import BatchRepository
from app.modules.batch.presentation.schemas import (
    BatchJobCreateRequest,
    BatchJobLogResponse,
    BatchJobResponse,
    BatchJobUpdateRequest,
    PaginatedBatchJobLogsResponse,
    PaginatedBatchJobsResponse,
)

router = APIRouter(prefix="/batch", tags=["Batch"])


async def get_batch_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> BatchUseCase:
    return BatchUseCase(batch_repository=BatchRepository(session))


def _job_to_response(job: BatchJob) -> BatchJobResponse:
    return BatchJobResponse(
        id=str(job.id),
        name=job.name,
        type=job.type,
        status=job.status,
        config=job.config,
        schedule=job.schedule,
        total_count=job.total_count,
        success_count=job.success_count,
        fail_count=job.fail_count,
        started_at=job.started_at.isoformat() if job.started_at else None,
        finished_at=job.finished_at.isoformat() if job.finished_at else None,
        created_at=job.created_at.isoformat() if job.created_at else "",
        updated_at=job.updated_at.isoformat() if job.updated_at else "",
    )


def _log_to_response(log) -> BatchJobLogResponse:
    return BatchJobLogResponse(
        id=str(log.id),
        job_id=str(log.job_id),
        message=log.message,
        level=log.level,
        created_at=log.created_at.isoformat() if log.created_at else "",
    )


@router.get("/jobs")
async def get_jobs(
    page: int = 1,
    per_page: int = 10,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> PaginatedBatchJobsResponse:
    per_page = min(per_page, 100)
    jobs, total = await use_case.get_jobs(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedBatchJobsResponse(
        jobs=[_job_to_response(j) for j in jobs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/jobs")
async def create_job(
    payload: BatchJobCreateRequest,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> BatchJobResponse:
    job = BatchJob(
        name=payload.name,
        type=payload.type,
        config=payload.config,
        schedule=payload.schedule,
    )
    result = await use_case.create_job(job)
    return _job_to_response(result)


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> BatchJobResponse:
    from uuid import UUID

    job = await use_case.get_job(UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return _job_to_response(job)


@router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    payload: BatchJobUpdateRequest,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> BatchJobResponse:
    from uuid import UUID

    values = payload.model_dump(exclude_none=True)
    job = await use_case.update_job(UUID(job_id), values)
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return _job_to_response(job)


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_job(UUID(job_id))
    if not success:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return {"success": True}


@router.post("/jobs/{job_id}/run")
async def run_job(
    job_id: str,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> BatchJobResponse:
    from uuid import UUID

    job = await use_case.run_job(UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return _job_to_response(job)


@router.get("/jobs/{job_id}/logs")
async def get_job_logs(
    job_id: str,
    page: int = 1,
    per_page: int = 10,
    use_case: BatchUseCase = Depends(get_batch_use_case),
) -> PaginatedBatchJobLogsResponse:
    from uuid import UUID

    per_page = min(per_page, 100)
    logs, total = await use_case.get_job_logs(UUID(job_id), page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedBatchJobLogsResponse(
        logs=[_log_to_response(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
