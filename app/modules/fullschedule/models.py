"""Fullschedule models"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey,
    Integer, SmallInteger, String, Text, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base
from app.modules.fullschedule.enums import (
    EventAction, EventType, HistoryStatus,
    ScheduleMode, ScheduleStatus, ScheduleStatusValue,
    TriggerSource, TriggeredBy,
)


# ═══ fs_schedule ═══════════════════════════════════════════════
class Schedule(Base):
    __tablename__ = "fs_schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ScheduleMode.WEEKLY.value,
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=ScheduleStatusValue.ACTIVE.value,
    )
    time_start: Mapped[str] = mapped_column(String(5), nullable=False, default="00:00")
    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EventType.DEVICE.value,
    )
    event_action: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EventAction.ON.value,
    )

    event: Mapped[int] = mapped_column(SmallInteger, name="event", default=1)
    sunday: Mapped[int] = mapped_column(SmallInteger, name="sunday", default=1)
    monday: Mapped[int] = mapped_column(SmallInteger, name="monday", default=0)
    tuesday: Mapped[int] = mapped_column(SmallInteger, name="tuesday", default=0)
    wednesday: Mapped[int] = mapped_column(SmallInteger, name="wednesday", default=0)
    thursday: Mapped[int] = mapped_column(SmallInteger, name="thursday", default=0)
    friday: Mapped[int] = mapped_column(SmallInteger, name="friday", default=0)
    saturday: Mapped[int] = mapped_column(SmallInteger, name="saturday", default=0)

    months: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), name="months", nullable=False,
        server_default="{}", default=list,
    )
    dates: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), name="dates", nullable=False,
        server_default="{}", default=list,
    )
    cron_expr: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    manual_trigger: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    run_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    area_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    devices: Mapped[List["ScheduleDevice"]] = relationship(
        "ScheduleDevice", back_populates="schedule",
        cascade="all, delete-orphan", lazy="selectin",
    )
    settings: Mapped[List["ScheduleSetting"]] = relationship(
        "ScheduleSetting", back_populates="schedule",
        cascade="all, delete-orphan", lazy="selectin",
    )

    @property
    def device_count(self) -> int:
        return len(self.devices) if self.devices else 0


# ═══ fs_schedule_device ════════════════════════════════════════
class ScheduleDevice(Base):
    __tablename__ = "fs_schedule_device"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_schedule.id"), nullable=False, index=True,
    )
    device_id: Mapped[int] = mapped_column(Integer, nullable=False)
    device_sn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="devices")


# ═══ fs_schedule_history ═══════════════════════════════════════
class ScheduleHistory(Base):
    __tablename__ = "fs_schedule_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_schedule.id"), nullable=False, index=True,
    )
    device_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    triggered_by: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TriggeredBy.SYSTEM.value,
    )
    trigger_source: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TriggerSource.AUTOMATIC.value,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=HistoryStatus.PROCESSING.value,
    )
    event_action: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )


# ═══ fs_schedule_settings ══════════════════════════════════════
class ScheduleSetting(Base):
    __tablename__ = "fs_schedule_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_schedule.id"), nullable=False, index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}", default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="settings")


# ═══ fs_groups ═════════════════════════════════════════════════
class Group(Base):
    __tablename__ = "fs_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ScheduleStatus.ACTIVE.value,
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    zones: Mapped[List["Zone"]] = relationship(
        "Zone", back_populates="group", cascade="all, delete-orphan", lazy="selectin",
    )


# ═══ fs_zones ══════════════════════════════════════════════════
class Zone(Base):
    __tablename__ = "fs_zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_groups.id"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    group: Mapped["Group"] = relationship("Group", back_populates="zones")
    areas: Mapped[List["Area"]] = relationship(
        "Area", back_populates="zone", cascade="all, delete-orphan", lazy="selectin",
    )


# ═══ fs_areas ══════════════════════════════════════════════════
class Area(Base):
    __tablename__ = "fs_areas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_zones.id"), nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    zone: Mapped["Zone"] = relationship("Zone", back_populates="areas")


# ═══ fs_device_area ════════════════════════════════════════════
class AreaDevice(Base):
    __tablename__ = "fs_device_area"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fs_areas.id"), nullable=False, index=True,
    )
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    device_sn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )


__all__ = [
    "Schedule", "ScheduleDevice", "ScheduleHistory", "ScheduleSetting",
    "Group", "Zone", "Area", "AreaDevice",
]
