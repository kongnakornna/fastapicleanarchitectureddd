"""AirSettingWarning entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class AirSettingWarning(BaseModelNoPK):
    __tablename__ = "sd_air_setting_warning"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    air_setting_warning_id: Mapped[int] = mapped_column(Integer, name="air_setting_warning_id", primary_key=True, autoincrement=True)
    type_id: Mapped[int | None] = mapped_column(Integer, name="type_id", nullable=True)
    device_id: Mapped[int | None] = mapped_column(Integer, name="device_id", nullable=True)
    period_id: Mapped[int | None] = mapped_column(Integer, name="period_id", nullable=True)
    event_name: Mapped[str | None] = mapped_column(String(255), name="event_name", nullable=True)
    date: Mapped[str] = mapped_column(String(100), name="date", default="")
    time: Mapped[str] = mapped_column(String(50), name="time", default="")
    data: Mapped[str | None] = mapped_column(String(255), name="data", nullable=True)
    status: Mapped[str | None] = mapped_column(String(150), name="status", nullable=True)
    active: Mapped[int | None] = mapped_column(Integer, name="active", nullable=True)
