"""Mqtt entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class Mqtt(BaseModelNoPK):
    __tablename__ = "sd_iot_mqtt"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    mqtt_id: Mapped[int] = mapped_column(Integer, name="mqtt_id", primary_key=True, autoincrement=True)
    mqtt_type_id: Mapped[int] = mapped_column(Integer, name="mqtt_type_id", default=0)
    sort: Mapped[int] = mapped_column(Integer, name="sort", default=1)
    mqtt_name: Mapped[str] = mapped_column(String(255), name="mqtt_name", default="")
    host: Mapped[str] = mapped_column(String(255), name="host", default="")
    port: Mapped[int] = mapped_column(Integer, name="port", default=0)
    username: Mapped[str] = mapped_column(String(255), name="username", default="")
    password: Mapped[str] = mapped_column(String(255), name="password", default="")
    secret: Mapped[str] = mapped_column(String(255), name="secret", default="")
    expire_in: Mapped[str] = mapped_column(String(255), name="expire_in", default="")
    token_value: Mapped[str] = mapped_column(Text, name="token_value", default="")
    org: Mapped[str] = mapped_column(String(255), name="org", default="")
    bucket: Mapped[str] = mapped_column(String(255), name="bucket", default="")
    envavorment: Mapped[str] = mapped_column(String(255), name="envavorment", default="")
    location_id: Mapped[int] = mapped_column(Integer, name="location_id", default=0)
    latitude: Mapped[str] = mapped_column(String(255), name="latitude", default="")
    longitude: Mapped[str] = mapped_column(String(255), name="longitude", default="")
    zoom: Mapped[int] = mapped_column(Integer, name="zoom", default=6)
    mqtt_main_id: Mapped[int] = mapped_column(Integer, name="mqtt_main_id", default=1)
    configuration: Mapped[str] = mapped_column(Text, name="configuration", default="")
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)
