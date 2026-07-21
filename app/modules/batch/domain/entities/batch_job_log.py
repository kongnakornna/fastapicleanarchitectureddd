from __future__ import annotations

from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class BatchJobLog(BaseModel):
    __tablename__ = "m_batch_job_log"

    job_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="job_id", comment="Reference to batch job"
    )
    message: Mapped[str] = mapped_column(
        Text, name="message", comment="Log message"
    )
    level: Mapped[str] = mapped_column(
        String(20), name="level", comment="Log level (info, warning, error)"
    )
