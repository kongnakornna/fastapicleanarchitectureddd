from __future__ import annotations

from sqlalchemy import Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class DeviceConfig(BaseModel):
    """Device configuration - translated from Go: internal/modules/iot/models/device_config.go"""

    __tablename__ = "iot_device_config"
    __table_args__ = (
        UniqueConstraint("device_id", name="uq_device_config_device_id"),
    )

    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    max_value: Mapped[float] = mapped_column(
        Float, name="max_value", default=0.0, comment="Maximum threshold"
    )
    min_value: Mapped[float] = mapped_column(
        Float, name="min_value", default=0.0, comment="Minimum threshold"
    )
    warning_threshold: Mapped[float] = mapped_column(
        Float, name="warning_threshold", default=0.0, comment="Warning threshold"
    )
    alert_threshold: Mapped[float] = mapped_column(
        Float, name="alert_threshold", default=0.0, comment="Alert threshold"
    )
    recovery_warning: Mapped[float] = mapped_column(
        Float, name="recovery_warning", default=0.0, comment="Recovery warning level"
    )
    recovery_alert: Mapped[float] = mapped_column(
        Float, name="recovery_alert", default=0.0, comment="Recovery alert level"
    )
    calibration_offset: Mapped[float] = mapped_column(
        Float, name="calibration_offset", default=0.0, comment="Calibration offset"
    )
    calibration_multiplier: Mapped[float] = mapped_column(
        Float, name="calibration_multiplier", default=1.0, comment="Calibration multiplier"
    )
    mqtt_control_on: Mapped[str] = mapped_column(
        String(255), name="mqtt_control_on", default="", comment="MQTT control ON payload"
    )
    mqtt_control_off: Mapped[str] = mapped_column(
        String(255), name="mqtt_control_off", default="", comment="MQTT control OFF payload"
    )
    action_name: Mapped[str] = mapped_column(
        String(255), name="action_name", default="", comment="Alarm action name"
    )
    config_json: Mapped[str] = mapped_column(
        String(2000), name="config_json", default="{}", comment="Additional config JSON"
    )
