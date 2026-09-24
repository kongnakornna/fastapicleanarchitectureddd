"""MqttHost entity — UUID PK"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class MqttHost(BaseModel):
    __tablename__ = "sd_mqtt_host"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(255), name="hostname", default="")
    host: Mapped[str] = mapped_column(String(255), name="host", default="")
    port: Mapped[str] = mapped_column(String(255), name="port", default="")
    username: Mapped[str] = mapped_column(String(255), name="username", default="")
    password: Mapped[str] = mapped_column(String(255), name="password", default="")
    idhost: Mapped[int] = mapped_column(Integer, name="idhost", default=0)
    status: Mapped[int] = mapped_column(Integer, name="status", default=0)
