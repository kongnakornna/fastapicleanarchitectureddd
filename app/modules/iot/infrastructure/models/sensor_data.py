"""SensorData entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class SensorData(BaseModelNoPK):
    __tablename__ = "sd_sensor_data"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    value: Mapped[float] = mapped_column(Numeric(10, 2), name="value")
    raw_data: Mapped[dict | None] = mapped_column(JSONB, name="raw_data", nullable=True)
    notification_type_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), nullable=True, index=True)
    battery_level: Mapped[float | None] = mapped_column(Numeric(5, 2), name="battery_level", nullable=True)
    signal_strength: Mapped[int | None] = mapped_column(Integer, name="signal_strength", nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="timestamp", server_default=func.current_timestamp(), index=True)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
    notification_type: Mapped["NotificationType"] = relationship("NotificationType", lazy="selectin")
