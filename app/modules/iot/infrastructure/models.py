"""iot SQLAlchemy 2.0 models — รวมทุก model"""
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Float, Index,
    Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """TH: declarative base | EN: declarative base"""


class DeviceModel(Base):
    __tablename__ = "iot_devices"
    __table_args__ = (
        CheckConstraint("hardware_id IN (1,2,3,4)", name="ck_iot_hardware"),
        Index("ix_iot_device_tenant", "tenant_id"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    hardware_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type_id: Mapped[int] = mapped_column(Integer, default=0)
    location_id: Mapped[int] = mapped_column(Integer, default=0)
    device_sn: Mapped[str] = mapped_column(String(100), default="")
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(100), default="")
    location_name: Mapped[str] = mapped_column(String(255), default="")
    mqtt_id: Mapped[int] = mapped_column(Integer, default=0)
    mqtt_main_id: Mapped[int] = mapped_column(Integer, default=0)
    mqtt_topic: Mapped[str] = mapped_column(String(500), default="")
    mqtt_name: Mapped[str] = mapped_column(String(255), default="")
    mqtt_username: Mapped[str] = mapped_column(String(255), default="")
    mqtt_password: Mapped[str] = mapped_column(String(255), default="")
    unit: Mapped[str] = mapped_column(String(50), default="")
    status: Mapped[str] = mapped_column(String(50), default="offline")
    icon: Mapped[str] = mapped_column(String(255), default="")
    icon_color: Mapped[str] = mapped_column(String(50), default="")
    description: Mapped[str] = mapped_column(String(500), default="")
    firmware_version: Mapped[str] = mapped_column(String(50), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class DeviceConfigModel(Base):
    __tablename__ = "iot_device_configs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "device_id", name="uq_iot_config_device"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    max_value: Mapped[float] = mapped_column(Float, default=0.0)
    min_value: Mapped[float] = mapped_column(Float, default=0.0)
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    alert_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_warning: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_alert: Mapped[float] = mapped_column(Float, default=0.0)
    calibration_offset: Mapped[float] = mapped_column(Float, default=0.0)
    calibration_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    mqtt_control_on: Mapped[str] = mapped_column(String(255), default="")
    mqtt_control_off: Mapped[str] = mapped_column(String(255), default="")
    action_name: Mapped[str] = mapped_column(String(255), default="")
    config_json: Mapped[str] = mapped_column(String(2000), default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class DeviceStatusModel(Base):
    __tablename__ = "iot_device_statuses"
    __table_args__ = (
        UniqueConstraint("tenant_id", "device_id", name="uq_iot_status_device"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_value: Mapped[float] = mapped_column(Float, default=0.0)
    last_alarm: Mapped[int] = mapped_column(Integer, default=0)
    count_alarm: Mapped[int] = mapped_column(Integer, default=0)
    event: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="offline")
    sensor_data: Mapped[str] = mapped_column(String(500), default="")
    sensor_min: Mapped[float] = mapped_column(Float, default=0.0)
    sensor_max: Mapped[float] = mapped_column(Float, default=0.0)
    sensor_avg: Mapped[float] = mapped_column(Float, default=0.0)
    battery: Mapped[float] = mapped_column(Float, default=0.0)
    rssi: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class DeviceAlertModel(Base):
    __tablename__ = "iot_device_alerts"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('info','low','medium','high','critical')",
            name="ck_iot_severity"),
        Index("ix_iot_alert_device", "device_id", "resolved"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), default="")
    severity: Mapped[str] = mapped_column(String(20), default="low")
    title: Mapped[str] = mapped_column(String(255), default="")
    message: Mapped[str] = mapped_column(String(1000), default="")
    value_data: Mapped[float] = mapped_column(Float, default=0.0)
    value_alarm: Mapped[float] = mapped_column(Float, default=0.0)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class iotDataModel(Base):
    __tablename__ = "iot_data"
    __table_args__ = (
        Index("ix_iot_data_device_time", "device_id", "created_at"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    data_json: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location_id: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class AlarmLogModel(Base):
    __tablename__ = "iot_alarm_logs"
    __table_args__ = (
        Index("ix_iot_alarm_device", "device_id", "created_at"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    alarm_action_id: Mapped[int] = mapped_column(Integer, default=0)
    alarm_type: Mapped[int] = mapped_column(Integer, default=0)
    alarm_status: Mapped[int] = mapped_column(Integer, default=0)
    value_data: Mapped[float] = mapped_column(Float, default=0.0)
    value_alarm: Mapped[float] = mapped_column(Float, default=0.0)
    title: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(500), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    data_alarm: Mapped[int] = mapped_column(Integer, default=0)
    data_alarm_raw: Mapped[int] = mapped_column(Integer, default=0)
    event_control: Mapped[int] = mapped_column(Integer, default=0)
    message_mqtt_control: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class ActivityLogModel(Base):
    __tablename__ = "iot_activity_logs"
    __table_args__ = (
        Index("ix_iot_activity_device", "device_id", "created_at"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    log_type: Mapped[str] = mapped_column(String(50), default="")
    device_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    severity: Mapped[str] = mapped_column(String(20), default="info")
    data_json: Mapped[str] = mapped_column(Text, default="{}")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())


class ScheduleModel(Base):
    __tablename__ = "iot_schedules"
    __table_args__ = (
        Index("ix_iot_schedule_device", "device_id", "is_active"),
        {"schema": "tenant_iot"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    schedule_id: Mapped[int] = mapped_column(Integer, default=0)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), default="")
    end_time: Mapped[str] = mapped_column(String(10), default="")
    event: Mapped[str] = mapped_column(String(50), default="")
    monday: Mapped[bool] = mapped_column(Boolean, default=False)
    tuesday: Mapped[bool] = mapped_column(Boolean, default=False)
    wednesday: Mapped[bool] = mapped_column(Boolean, default=False)
    thursday: Mapped[bool] = mapped_column(Boolean, default=False)
    friday: Mapped[bool] = mapped_column(Boolean, default=False)
    saturday: Mapped[bool] = mapped_column(Boolean, default=False)
    sunday: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now())
