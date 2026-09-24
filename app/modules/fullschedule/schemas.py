"""Fullschedule DTOs"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ScopeFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: Optional[uuid.UUID] = None
    zone_id: Optional[uuid.UUID] = None
    area_id: Optional[uuid.UUID] = None


class ScheduleReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: uuid.UUID
    name: str
    mode: str
    total_runs: int
    success_count: int
    failed_count: int
    skipped_count: int
    processing: int
    success_rate: float
    avg_duration: float
    last_run_at: Optional[datetime] = None


__all__ = ["ScopeFilter", "ScheduleReport"]
