"""AirMod entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class AirMod(BaseModelNoPK):
    __tablename__ = "sd_air_mod"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    air_mod_id: Mapped[int] = mapped_column(Integer, name="air_mod_id", primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255), name="name", nullable=True)
    data: Mapped[str | None] = mapped_column(String(255), name="data", nullable=True)
    status: Mapped[str | None] = mapped_column(String(150), name="status", nullable=True)
    active: Mapped[int | None] = mapped_column(Integer, name="active", nullable=True)
