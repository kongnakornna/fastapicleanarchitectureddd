"""ReportData entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class ReportData(BaseModelNoPK):
    __tablename__ = "sd_report_data"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    template_id: Mapped[int | None] = mapped_column(Integer, name="template_id", nullable=True)
    report_type: Mapped[str] = mapped_column(String(50), name="report_type", index=True)
    data: Mapped[dict] = mapped_column(JSONB, name="data")
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="period_start", index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="period_end", index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="generated_at", server_default=func.current_timestamp(), index=True)
    file_path: Mapped[str | None] = mapped_column(String(500), name="file_path", nullable=True)
    file_format: Mapped[str | None] = mapped_column(String(20), name="file_format", nullable=True)
    is_exported: Mapped[bool] = mapped_column(Boolean, name="is_exported", default=False)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="exported_at", nullable=True)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
