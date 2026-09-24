"""Device entity — sd_iot_device"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class Device(BaseModelNoPK):
    __tablename__ = "sd_iot_device"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(Integer, name="device_id", primary_key=True, autoincrement=True)
    mqtt_id: Mapped[int] = mapped_column(Integer, name="mqtt_id", default=0)
    setting_id: Mapped[int] = mapped_column(Integer, name="setting_id", default=0)
    type_id: Mapped[int] = mapped_column(Integer, name="type_id", default=0)
    location_id: Mapped[int] = mapped_column(Integer, name="location_id", default=0)
    device_name: Mapped[str] = mapped_column(String(255), name="device_name", default="")
    sn: Mapped[str] = mapped_column(String(255), name="sn", unique=True, index=True)
    hardware_id: Mapped[int] = mapped_column(Integer, name="hardware_id", default=0)
    status_warning: Mapped[str] = mapped_column(String(150), name="status_warning", default="")
    recovery_warning: Mapped[str] = mapped_column(String(150), name="recovery_warning", default="")
    status_alert: Mapped[str] = mapped_column(String(150), name="status_alert", default="")
    recovery_alert: Mapped[str] = mapped_column(String(150), name="recovery_alert", default="")
    time_life: Mapped[int] = mapped_column(Integer, name="time_life", default=1)
    period: Mapped[str] = mapped_column(String(150), name="period", default="")
    work_status: Mapped[int] = mapped_column(Integer, name="work_status", default=1)
    max_: Mapped[str] = mapped_column("max", String(255), default="")
    min_: Mapped[str] = mapped_column("min", String(255), default="")
    model: Mapped[str] = mapped_column(String(255), name="model", default="")
    vendor: Mapped[str] = mapped_column(String(255), name="vendor", default="")
    comparevalue: Mapped[str] = mapped_column(String(255), name="comparevalue", default="")
    unit: Mapped[str] = mapped_column(String(255), name="unit", default="")
    host_id: Mapped[str] = mapped_column(String, name="host_id", default="")
    oid: Mapped[str] = mapped_column(String(255), name="oid", default="")
    action_id: Mapped[int] = mapped_column(Integer, name="action_id", default=0)
    status_alert_id: Mapped[int] = mapped_column(Integer, name="status_alert_id", default=0)
    mqtt_data_value: Mapped[str] = mapped_column(String(255), name="mqtt_data_value", default="")
    mqtt_data_control: Mapped[str] = mapped_column(String(255), name="mqtt_data_control", default="")
    measurement: Mapped[str] = mapped_column(String(255), name="measurement", default="")
    mqtt_control_on: Mapped[str] = mapped_column(String(255), name="mqtt_control_on", default="1")
    mqtt_control_off: Mapped[str] = mapped_column(String(255), name="mqtt_control_off", default="0")
    org: Mapped[str] = mapped_column(String(255), name="org", default="")
    bucket: Mapped[str] = mapped_column(String(255), name="bucket", default="")
    status: Mapped[int] = mapped_column(Integer, name="status", default=0)
    mqtt_device_name: Mapped[str] = mapped_column(String(255), name="mqtt_device_name", default="")
    mqtt_status_over_name: Mapped[str] = mapped_column(Text, name="mqtt_status_over_name", default="")
    mqtt_status_data_name: Mapped[str] = mapped_column(Text, name="mqtt_status_data_name", default="")
    mqtt_act_relay_name: Mapped[str] = mapped_column(Text, name="mqtt_act_relay_name", default="")
    mqtt_control_relay_name: Mapped[str] = mapped_column(Text, name="mqtt_control_relay_name", default="")
    layout: Mapped[int] = mapped_column(Integer, name="layout", default=1)
    alert_set: Mapped[int] = mapped_column(Integer, name="alert_set", default=1)
    icon_normal: Mapped[str] = mapped_column(Text, name="icon_normal", default="")
    icon_warning: Mapped[str] = mapped_column(Text, name="icon_warning", default="")
    icon_alert: Mapped[str] = mapped_column(Text, name="icon_alert", default="")
    icon: Mapped[str] = mapped_column(Text, name="icon", default="")
    icon_on: Mapped[str] = mapped_column(Text, name="icon_on", default="")
    icon_off: Mapped[str] = mapped_column(Text, name="icon_off", default="")
    color_normal: Mapped[str] = mapped_column(String(50), name="color_normal", default="#22C55E")
    color_warning: Mapped[str] = mapped_column(String(50), name="color_warning", default="#F59E0B")
    color_alert: Mapped[str] = mapped_column(String(50), name="color_alert", default="#EF4444")
    code: Mapped[str] = mapped_column(String(50), name="code", default="normal")
    menu: Mapped[int] = mapped_column(Integer, name="menu", default=1)
    calibration_add: Mapped[str] = mapped_column(String(250), name="calibration_add", default="0")
    calibration_subtract: Mapped[str] = mapped_column(String(250), name="calibration_subtract", default="0")
    calibration_type: Mapped[int] = mapped_column(Integer, name="calibration_type", default=3)
