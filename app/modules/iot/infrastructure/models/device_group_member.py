"""DeviceGroupMember entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceGroupMember(BaseModelNoPK):
    __tablename__ = "sd_device_member"
    __table_args__ = (UniqueConstraint("Device_id", "group_id", name="unique_Device_group"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column("Device_id", Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_device_group.id"), index=True)
    role: Mapped[str] = mapped_column(String(50), name="role", default="member")
    priority: Mapped[int] = mapped_column(Integer, name="priority", default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)

    device: Mapped["Device"] = relationship("Device", foreign_keys=[device_id], lazy="selectin")
    group: Mapped["DeviceGroup"] = relationship("DeviceGroup", foreign_keys=[group_id], lazy="selectin")
