from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class BatchJob(BaseModel):
    __tablename__ = "m_batch_job"

    name: Mapped[str] = mapped_column(
        String(200), name="name", comment="Batch job name"
    )
    type: Mapped[str] = mapped_column(
        String(50), name="type", comment="Batch job type"
    )
    config: Mapped[dict | None] = mapped_column(
        JSON, name="config", comment="Job configuration JSON", nullable=True
    )
    schedule: Mapped[str | None] = mapped_column(
        String(100), name="schedule", comment="Job schedule expression", nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="pending", server_default="pending", comment="Job status"
    )
    total_count: Mapped[int] = mapped_column(
        Integer, name="total_count", default=0, server_default="0", comment="Total items to process"
    )
    success_count: Mapped[int] = mapped_column(
        Integer, name="success_count", default=0,
        server_default="0", comment="Successfully processed items"
    )
    fail_count: Mapped[int] = mapped_column(
        Integer, name="fail_count", default=0, server_default="0", comment="Failed items"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="started_at", comment="Job start timestamp", nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="finished_at", comment="Job finish timestamp", nullable=True
    )
