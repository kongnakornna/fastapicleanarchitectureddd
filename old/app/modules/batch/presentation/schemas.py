from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BatchJobCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., min_length=1, max_length=50)
    config: dict[str, Any] | None = None
    schedule: str | None = Field(None, max_length=100)

    model_config = ConfigDict(extra="forbid")


class BatchJobUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=200)
    type: str | None = Field(None, max_length=50)
    config: dict[str, Any] | None = None
    schedule: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=20)

    model_config = ConfigDict(extra="forbid")


class BatchJobResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    config: dict[str, Any] | None = None
    schedule: str | None = None
    total_count: int
    success_count: int
    fail_count: int
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class BatchJobLogResponse(BaseModel):
    id: str
    job_id: str
    message: str
    level: str
    created_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedBatchJobsResponse(BaseModel):
    jobs: list[BatchJobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")


class PaginatedBatchJobLogsResponse(BaseModel):
    logs: list[BatchJobLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
