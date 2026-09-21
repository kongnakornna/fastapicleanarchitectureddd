from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class DeviceAlert(BaseModel):
    """Device alert - translated from Go: internal/modules/iot/models/device_alert.go"""

    __tablename__ = "iot_device_alert"

    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    alert_type: Mapped[str] = mapped_column(
        String(50), name="alert_type", default="", comment="Alert type"
    )
    severity: Mapped[str] = mapped_column(
        String(20), name="severity", default="low", comment="Severity: low/medium/high/critical"
    )
    title: Mapped[str] = mapped_column(
        String(255), name="title", default="", comment="Alert title"
    )
    message: Mapped[str] = mapped_column(
        String(1000), name="message", default="", comment="Alert message"
    )
    value_data: Mapped[float] = mapped_column(
        Float, name="value_data", default=0.0, comment="Sensor value at alert"
    )
    value_alarm: Mapped[float] = mapped_column(
        Float, name="value_alarm", default=0.0, comment="Alarm threshold value"
    )
    resolved: Mapped[bool] = mapped_column(
        Boolean, name="resolved", default=False, comment="Is resolved"
    )
    acknowledged: Mapped[bool] = mapped_column(
        Boolean, name="acknowledged", default=False, comment="Is acknowledged"
    )
