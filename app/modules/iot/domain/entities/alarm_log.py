from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class AlarmLog(BaseModel):
    """Alarm log - translated from Go: internal/modules/iot/models/alarm_log.go"""

    __tablename__ = "iot_alarm_log"

    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    alarm_action_id: Mapped[int] = mapped_column(
        Integer, name="alarm_action_id", default=0, comment="Alarm action ID"
    )
    alarm_type: Mapped[int] = mapped_column(
        Integer, name="alarm_type", default=0, comment="Alarm type"
    )
    alarm_status: Mapped[int] = mapped_column(
        Integer, name="alarm_status", default=0, comment="Alarm status"
    )
    value_data: Mapped[float] = mapped_column(
        Float, name="value_data", default=0.0, comment="Sensor value"
    )
    value_alarm: Mapped[float] = mapped_column(
        Float, name="value_alarm", default=0.0, comment="Alarm threshold"
    )
    title: Mapped[str] = mapped_column(
        String(255), name="title", default="", comment="Alarm title"
    )
    subject: Mapped[str] = mapped_column(
        String(500), name="subject", default="", comment="Alarm subject"
    )
    content: Mapped[str] = mapped_column(
        Text, name="content", default="", comment="Alarm content"
    )
    data_alarm: Mapped[int] = mapped_column(
        Integer, name="data_alarm", default=0, comment="Alarm data value"
    )
    data_alarm_raw: Mapped[int] = mapped_column(
        Integer, name="data_alarm_raw", default=0, comment="Raw alarm data"
    )
    event_control: Mapped[int] = mapped_column(
        Integer, name="event_control", default=0, comment="Event control state"
    )
    message_mqtt_control: Mapped[str] = mapped_column(
        String(500), name="message_mqtt_control", default="", comment="MQTT control message"
    )
