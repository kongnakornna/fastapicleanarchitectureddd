"""Alarm entities"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel, BaseModelNoPK


class DeviceAlarmAction(BaseModelNoPK):
    __tablename__ = "sd_iot_device_alarm_action"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    alarm_action_id: Mapped[int] = mapped_column(Integer, name="alarm_action_id", primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(String(255), name="action_name", default="")
    status_warning: Mapped[str] = mapped_column(String(150), name="status_warning", default="")
    recovery_warning: Mapped[str] = mapped_column(String(150), name="recovery_warning", default="")
    status_alert: Mapped[str] = mapped_column(String(150), name="status_alert", default="")
    recovery_alert: Mapped[str] = mapped_column(String(150), name="recovery_alert", default="")
    email_alarm: Mapped[int] = mapped_column(Integer, name="email_alarm", default=0)
    line_alarm: Mapped[int] = mapped_column(Integer, name="line_alarm", default=0)
    telegram_alarm: Mapped[int] = mapped_column(Integer, name="telegram_alarm", default=0)
    sms_alarm: Mapped[int] = mapped_column(Integer, name="sms_alarm", default=0)
    nonc_alarm: Mapped[int] = mapped_column(Integer, name="nonc_alarm", default=0)
    time_life: Mapped[int] = mapped_column(Integer, name="time_life", default=0)
    event: Mapped[int] = mapped_column(Integer, name="event", default=0)
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)


class AlarmDevice(BaseModel):
    __tablename__ = "sd_iot_alarm_device"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    alarm_action_id: Mapped[int] = mapped_column(Integer, name="alarm_action_id")
    device_id: Mapped[int] = mapped_column(Integer, name="device_id")


class AlarmDeviceEvent(BaseModel):
    __tablename__ = "sd_iot_alarm_device_event"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    alarm_action_id: Mapped[int] = mapped_column(Integer, name="alarm_action_id")
    device_id: Mapped[int] = mapped_column(Integer, name="device_id")
