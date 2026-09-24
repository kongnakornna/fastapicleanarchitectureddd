"""AirControlLog — UUID PK"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class AirControlLog(BaseModel):
    __tablename__ = "sd_air_control_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    alarm_action_id: Mapped[int | None] = mapped_column(Integer, name="alarm_action_id", nullable=True)
    air_control_id: Mapped[int | None] = mapped_column(Integer, name="air_control_id", nullable=True)
    device_id: Mapped[int | None] = mapped_column(Integer, name="device_id", nullable=True)
    type_id: Mapped[int | None] = mapped_column(Integer, name="type_id", nullable=True)
    temperature: Mapped[str | None] = mapped_column(String(255), name="temperature", nullable=True)
    warning: Mapped[str | None] = mapped_column(String(255), name="warning", nullable=True)
    recovery: Mapped[str | None] = mapped_column(String(150), name="recovery", nullable=True)
    period: Mapped[str | None] = mapped_column(String(150), name="period", nullable=True)
    percent: Mapped[str | None] = mapped_column(String(150), name="percent", nullable=True)
    firealarm: Mapped[str | None] = mapped_column(String(150), name="firealarm", nullable=True)
    humidityalarm: Mapped[str | None] = mapped_column(String(150), name="humidityalarm", nullable=True)
    air2_alarm: Mapped[str | None] = mapped_column(String(150), name="air2_alarm", nullable=True)
    air1_alarm: Mapped[str | None] = mapped_column(String(150), name="air1_alarm", nullable=True)
    temperaturealarm: Mapped[str | None] = mapped_column(String(150), name="temperaturealarm", nullable=True)
    mode: Mapped[str | None] = mapped_column(String(150), name="mode", nullable=True)
    state_air1: Mapped[str | None] = mapped_column(String(150), name="state_air1", nullable=True)
    state_air2: Mapped[str | None] = mapped_column(String(150), name="state_air2", nullable=True)
    temperaturealarmoff: Mapped[str | None] = mapped_column(String(150), name="temperaturealarmoff", nullable=True)
    ups_alarm: Mapped[str | None] = mapped_column(String(150), name="ups_alarm", nullable=True)
    ups2_alarm: Mapped[str | None] = mapped_column(String(150), name="ups2_alarm", nullable=True)
    hssdalarm: Mapped[str | None] = mapped_column(String(150), name="hssdalarm", nullable=True)
    waterleakalarm: Mapped[str | None] = mapped_column(String(150), name="waterleakalarm", nullable=True)
    date: Mapped[str] = mapped_column(String(100), name="date", default="")
    time: Mapped[str] = mapped_column(String(50), name="time", default="")
    data: Mapped[str | None] = mapped_column(String(255), name="data", nullable=True)
    status: Mapped[str | None] = mapped_column(String(150), name="status", nullable=True)
