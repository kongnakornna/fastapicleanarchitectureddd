from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class DeviceStatus(BaseModel):
    """Device status - translated from Go: internal/modules/iot/models/device_status.go"""

    __tablename__ = "iot_device_status"
    __table_args__ = (
        UniqueConstraint("device_id", name="uq_device_status_device_id"),
    )

    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    is_online: Mapped[bool] = mapped_column(
        Boolean, name="is_online", default=False, comment="Online status"
    )
    last_seen: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), name="last_seen", nullable=True, comment="Last seen timestamp"
    )
    last_value: Mapped[float] = mapped_column(
        Float, name="last_value", default=0.0, comment="Last sensor value"
    )
    last_alarm: Mapped[int] = mapped_column(
        Integer, name="last_alarm", default=0, comment="Last alarm status"
    )
    count_alarm: Mapped[int] = mapped_column(
        Integer, name="count_alarm", default=0, comment="Alarm count"
    )
    event: Mapped[int] = mapped_column(
        Integer, name="event", default=0, comment="Event state"
    )
    status: Mapped[str] = mapped_column(
        String(50), name="status", default="offline", comment="Status string"
    )
    sensor_data: Mapped[str] = mapped_column(
        String(500), name="sensor_data", default="", comment="Sensor data JSON"
    )
    sensor_min: Mapped[float] = mapped_column(
        Float, name="sensor_min", default=0.0, comment="Sensor min value"
    )
    sensor_max: Mapped[float] = mapped_column(
        Float, name="sensor_max", default=0.0, comment="Sensor max value"
    )
    sensor_avg: Mapped[float] = mapped_column(
        Float, name="sensor_avg", default=0.0, comment="Sensor avg value"
    )
    battery: Mapped[float] = mapped_column(
        Float, name="battery", default=0.0, comment="Battery level"
    )
    rssi: Mapped[int] = mapped_column(
        Integer, name="rssi", default=0, comment="Signal strength"
    )
