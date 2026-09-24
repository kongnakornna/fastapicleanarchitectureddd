"""iot domain events — เหตุการณ์โดเมน iot"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class DeviceCreated:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    device_name: str
    hardware_id: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DeviceStatusChanged:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    old_status: str
    iot_status: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class iotDataReceived:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    raw_payload: str
    data_map: dict
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AlarmTriggered:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    alarm_type: int
    alarm_status: int
    title: str
    subject: str
    value_data: float
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AlarmRecovered:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    alarm_type: int
    recovery_status: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DeviceOffline:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    last_seen: datetime
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ColdChainAlert:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    temperature: float
    threshold: float
    location_name: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
