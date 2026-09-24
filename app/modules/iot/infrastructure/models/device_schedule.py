"""DeviceSchedule entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceSchedule(BaseModelNoPK):
    __tablename__ = "sd_device_schedule"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    name: Mapped[str] = mapped_column(String(200), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    schedule_type: Mapped[str] = mapped_column(String(50), name="schedule_type", index=True)
    schedule_config: Mapped[dict] = mapped_column(JSONB, name="schedule_config")
    action: Mapped[dict] = mapped_column(JSONB, name="action")
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="last_run_at", nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="next_run_at", nullable=True, index=True)
    run_count: Mapped[int] = mapped_column(Integer, name="run_count", default=0)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
