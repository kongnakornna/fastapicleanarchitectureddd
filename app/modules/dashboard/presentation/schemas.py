from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DashboardStatsResponse(BaseModel):
    total_devices: int
    online_devices: int
    active_alerts: int
    today_commands: int

    model_config = ConfigDict(extra="forbid")


class RevenueData(BaseModel):
    period: str
    amount: float

    model_config = ConfigDict(extra="forbid")


class RevenueChartResponse(BaseModel):
    data: list[RevenueData]

    model_config = ConfigDict(extra="forbid")


class TopPartData(BaseModel):
    part_name: str
    count: int

    model_config = ConfigDict(extra="forbid")


class TopPartsResponse(BaseModel):
    data: list[TopPartData]

    model_config = ConfigDict(extra="forbid")


class JobStatusSummary(BaseModel):
    status: str
    count: int

    model_config = ConfigDict(extra="forbid")


class JobStatusResponse(BaseModel):
    data: list[JobStatusSummary]

    model_config = ConfigDict(extra="forbid")
