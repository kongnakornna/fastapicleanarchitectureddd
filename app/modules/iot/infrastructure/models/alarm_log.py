"""Alarm log entities — 3 independent tables (ไม่ใช้ inheritance)

TH: ใช้ mixin เพื่อแชร์ columns ระหว่าง 3 ตาราง โดยไม่ให้ SQLAlchemy
    เข้าใจผิดว่าเป็น joined-table inheritance
EN: Use mixin to share columns across 3 tables without SQLAlchemy
    treating them as joined-table inheritance
"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class _AlarmProcessLogMixin:
    """Pure mixin — ไม่ inherit จาก BaseModel โดยตรง (ไม่มี __tablename__)"""
    # Note: id มาจาก BaseModel ของแต่ละ subclass
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), name="tenant_id", nullable=False, index=True,
    )
    alarm_action_id: Mapped[int] = mapped_column(Integer, name="alarm_action_id", default=0)
    device_id: Mapped[int] = mapped_column(Integer, name="device_id", default=0)
    type_id: Mapped[int] = mapped_column(Integer, name="type_id", default=0)
    event: Mapped[str] = mapped_column(String(255), name="event", default="")
    alarm_type: Mapped[str] = mapped_column(String(255), name="alarm_type", default="")
    status_warning: Mapped[str] = mapped_column(String(150), name="status_warning", default="")
    recovery_warning: Mapped[str] = mapped_column(String(150), name="recovery_warning", default="")
    status_alert: Mapped[str] = mapped_column(String(150), name="status_alert", default="")
    recovery_alert: Mapped[str] = mapped_column(String(150), name="recovery_alert", default="")
    email_alarm: Mapped[int] = mapped_column(Integer, name="email_alarm", default=0)
    line_alarm: Mapped[int] = mapped_column(Integer, name="line_alarm", default=0)
    telegram_alarm: Mapped[int] = mapped_column(Integer, name="telegram_alarm", default=0)
    sms_alarm: Mapped[int] = mapped_column(Integer, name="sms_alarm", default=0)
    nonc_alarm: Mapped[int] = mapped_column(Integer, name="nonc_alarm", default=0)
    status: Mapped[str] = mapped_column(String(150), name="status", default="")
    date: Mapped[str] = mapped_column(String(100), name="date", default="")
    time: Mapped[str] = mapped_column(String(50), name="time", default="")
    data: Mapped[str] = mapped_column(String(255), name="data", default="")
    data_alarm: Mapped[str] = mapped_column(String(255), name="data_alarm", default="")
    alarm_status: Mapped[str] = mapped_column(String(255), name="alarm_status", default="")
    subject: Mapped[str] = mapped_column(String(255), name="subject", default="")
    content: Mapped[str] = mapped_column(String(255), name="content", default="")


class AlarmProcessLog(BaseModel, _AlarmProcessLogMixin):
    """TH: log การประมวลผล alarm หลัก"""
    __tablename__ = "sd_alarm_process_log"


class AlarmProcessLogEmail(BaseModel, _AlarmProcessLogMixin):
    """TH: log การประมวลผล alarm (email)"""
    __tablename__ = "sd_alarm_process_log_email"


class AlarmProcessLogTemp(BaseModel, _AlarmProcessLogMixin):
    """TH: log การประมวลผล alarm (temp)"""
    __tablename__ = "sd_alarm_process_log_temp"
