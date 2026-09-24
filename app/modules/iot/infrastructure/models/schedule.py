"""Schedule entities"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel, BaseModelNoPK


class Schedule(BaseModelNoPK):
    __tablename__ = "sd_iot_schedule"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, name="schedule_id", primary_key=True, autoincrement=True)
    schedule_name: Mapped[str] = mapped_column(String(255), name="schedule_name", default="")
    device_id: Mapped[int] = mapped_column(Integer, name="device_id", index=True)
    start: Mapped[str] = mapped_column(String(50), name="start", default="")
    event: Mapped[int] = mapped_column(Integer, name="event", default=0)
    sunday: Mapped[int] = mapped_column(Integer, name="sunday", default=0)
    monday: Mapped[int] = mapped_column(Integer, name="monday", default=0)
    tuesday: Mapped[int] = mapped_column(Integer, name="tuesday", default=0)
    wednesday: Mapped[int] = mapped_column(Integer, name="wednesday", default=0)
    thursday: Mapped[int] = mapped_column(Integer, name="thursday", default=0)
    friday: Mapped[int] = mapped_column(Integer, name="friday", default=0)
    saturday: Mapped[int] = mapped_column(Integer, name="saturday", default=0)
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)


class IotScheduleDevice(BaseModelNoPK):
    __tablename__ = "sd_iot_schedule_device"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, name="schedule_id", primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, name="device_id", primary_key=True)


class ScheduleProcessLog(BaseModel):
    __tablename__ = "sd_schedule_process_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, name="schedule_id", default=0)
    device_id: Mapped[int] = mapped_column(Integer, name="device_id", default=0)
    schedule_event_start: Mapped[str] = mapped_column(String(50), name="schedule_event_start", default="")
    day: Mapped[str] = mapped_column(String(20), name="day", default="")
    doday: Mapped[str] = mapped_column(String(20), name="doday", default="")
    dotime: Mapped[str] = mapped_column(String(50), name="dotime", default="")
    schedule_event: Mapped[str] = mapped_column(String(50), name="schedule_event", default="")
    device_status: Mapped[str] = mapped_column(String(50), name="device_status", default="")
    status: Mapped[int] = mapped_column(Integer, name="status", default=0)
    date: Mapped[str] = mapped_column(String(20), name="date", default="")
    time: Mapped[str] = mapped_column(String(20), name="time", default="")
