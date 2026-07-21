from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.modules.dashboard.application.use_case import DashboardUseCase
from app.modules.dashboard.presentation.schemas import (
    DashboardStatsResponse,
    JobStatusResponse,
    JobStatusSummary,
    RevenueChartResponse,
    RevenueData,
    TopPartData,
    TopPartsResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


async def get_dashboard_use_case() -> DashboardUseCase:
    return DashboardUseCase()


@router.get("/stats")
async def get_dashboard_stats(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
) -> DashboardStatsResponse:
    result = await use_case.get_dashboard_stats()
    return DashboardStatsResponse(**result)


@router.get("/revenue")
async def get_revenue_chart(
    period: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
) -> RevenueChartResponse:
    data = await use_case.get_revenue_chart(period)
    return RevenueChartResponse(data=[RevenueData(**d) for d in data])


@router.get("/top-parts")
async def get_top_parts(
    limit: int = Query(default=5, ge=1, le=50),
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
) -> TopPartsResponse:
    data = await use_case.get_top_parts(limit)
    return TopPartsResponse(data=[TopPartData(**d) for d in data])


@router.get("/job-status")
async def get_job_status(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
) -> JobStatusResponse:
    data = await use_case.get_job_status_summary()
    return JobStatusResponse(data=[JobStatusSummary(**d) for d in data])
