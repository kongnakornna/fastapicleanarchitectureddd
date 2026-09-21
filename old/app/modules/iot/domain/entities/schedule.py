from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Schedule(BaseModel):
    """Schedule - translated from Go: internal/modules/iot/models/schedule.go"""

    __tablename__ = "iot_schedule"

    schedule_id: Mapped[int] = mapped_column(
        Integer, name="schedule_id", default=0, comment="Schedule ID"
    )
    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    start_time: Mapped[str] = mapped_column(
        String(10), name="start_time", default="", comment="Start time HH:MM"
    )
    end_time: Mapped[str] = mapped_column(
        String(10), name="end_time", default="", comment="End time HH:MM"
    )
    event: Mapped[str] = mapped_column(
        String(50), name="event", default="", comment="Event action"
    )
    monday: Mapped[bool] = mapped_column(
        Boolean, name="monday", default=False, comment="Monday"
    )
    tuesday: Mapped[bool] = mapped_column(
        Boolean, name="tuesday", default=False, comment="Tuesday"
    )
    wednesday: Mapped[bool] = mapped_column(
        Boolean, name="wednesday", default=False, comment="Wednesday"
    )
    thursday: Mapped[bool] = mapped_column(
        Boolean, name="thursday", default=False, comment="Thursday"
    )
    friday: Mapped[bool] = mapped_column(
        Boolean, name="friday", default=False, comment="Friday"
    )
    saturday: Mapped[bool] = mapped_column(
        Boolean, name="saturday", default=False, comment="Saturday"
    )
    sunday: Mapped[bool] = mapped_column(
        Boolean, name="sunday", default=False, comment="Sunday"
    )
