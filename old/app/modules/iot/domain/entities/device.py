from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Device(BaseModel):
    """Device entity - translated from Go: internal/modules/iot/models/device.go"""

    __tablename__ = "iot_device"

    hardware_id: Mapped[int] = mapped_column(
        Integer, name="hardware_id", comment="Hardware identifier"
    )
    type_id: Mapped[int] = mapped_column(
        Integer, name="type_id", default=0, comment="Device type ID"
    )
    location_id: Mapped[int] = mapped_column(
        Integer, name="location_id", default=0, comment="Location ID"
    )
    device_sn: Mapped[str] = mapped_column(
        String(100), name="device_sn", default="", comment="Serial number"
    )
    device_name: Mapped[str] = mapped_column(
        String(255), name="device_name", comment="Device name"
    )
    device_type: Mapped[str] = mapped_column(
        String(100), name="device_type", default="", comment="Device type"
    )
    location_name: Mapped[str] = mapped_column(
        String(255), name="location_name", default="", comment="Location name"
    )

    # MQTT config
    mqtt_id: Mapped[int] = mapped_column(
        Integer, name="mqtt_id", default=0, comment="MQTT config ID"
    )
    mqtt_main_id: Mapped[int] = mapped_column(
        Integer, name="mqtt_main_id", default=0, comment="MQTT main broker ID"
    )
    mqtt_topic: Mapped[str] = mapped_column(
        String(500), name="mqtt_topic", default="", comment="MQTT topic"
    )
    mqtt_name: Mapped[str] = mapped_column(
        String(255), name="mqtt_name", default="", comment="MQTT display name"
    )
    mqtt_username: Mapped[str] = mapped_column(
        String(255), name="mqtt_username", default="", comment="MQTT username"
    )
    mqtt_password: Mapped[str] = mapped_column(
        String(255), name="mqtt_password", default="", comment="MQTT password"
    )

    # Device info
    unit: Mapped[str] = mapped_column(
        String(50), name="unit", default="", comment="Measurement unit"
    )
    status: Mapped[str] = mapped_column(
        String(50), name="status", default="offline", comment="Device status"
    )
    icon: Mapped[str] = mapped_column(
        String(255), name="icon", default="", comment="Icon name"
    )
    icon_color: Mapped[str] = mapped_column(
        String(50), name="icon_color", default="", comment="Icon color"
    )
    description: Mapped[str] = mapped_column(
        String(500), name="description", default="", comment="Description"
    )
    firmware_version: Mapped[str] = mapped_column(
        String(50), name="firmware_version", default="", comment="Firmware version"
    )
