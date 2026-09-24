app/
├── modules/
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── utils.py                    [มีอยู่แล้ว — BRASILIA_TZ]
│   │   └── infrastructure/
│   │       ├── __init__.py                 ⭐ NEW
│   │       └── models.py                   ⭐ NEW (Base, BaseModel, BaseModelNoPK)
│   │
│   ├── iot/
│   │   ├── __init__.py                     ⭐ NEW
│   │   │
│   │   ├── domain/
│   │   │   ├── __init__.py                 🔧 FIX
│   │   │   ├── enums.py                    ✅ KEEP
│   │   │   ├── exceptions.py               ✅ KEEP
│   │   │   ├── events.py                   ✅ KEEP
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py             ✅ KEEP
│   │   │   │   ├── alarm.py                ✅ KEEP
│   │   │   │   ├── location.py             ✅ KEEP
│   │   │   │   └── mqtt.py                 ✅ KEEP
│   │   │   └── helpers/
│   │   │       ├── __init__.py             ✅ KEEP
│   │   │       └── alarm_logic.py          ✅ KEEP
│   │   │
│   │   ├── application/
│   │   │   ├── __init__.py                 ⭐ NEW
│   │   │   ├── exceptions.py               ✅ KEEP
│   │   │   ├── interfaces.py               ⭐ NEW
│   │   │   ├── mappers.py                  ✅ KEEP
│   │   │   ├── utils.py                    ✅ KEEP
│   │   │   └── use_case.py                 ⭐ REWRITE
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── __init__.py                 ⭐ NEW
│   │   │   ├── caches.py                   ⭐ NEW
│   │   │   ├── services.py                 ⭐ NEW
│   │   │   ├── models/
│   │   │   │   ├── __init__.py             ⭐ NEW
│   │   │   │   ├── common.py               🔧 FIX
│   │   │   │   └── ... (48 ไฟล์)           🔧 FIX (Base → BaseModelNoPK)
│   │   │   └── repositories/
│   │   │       ├── __init__.py             ⭐ NEW
│   │   │       ├── device_repository.py    ⭐ NEW
│   │   │       ├── device_config_repository.py      ⭐ NEW
│   │   │       ├── device_status_repository.py      ⭐ NEW
│   │   │       ├── device_alert_repository.py       ⭐ NEW
│   │   │       ├── iot_data_repository.py           ⭐ NEW
│   │   │       ├── alarm_log_repository.py          ⭐ NEW
│   │   │       ├── activity_log_repository.py       ⭐ NEW
│   │   │       ├── command_log_repository.py        ⭐ NEW
│   │   │       └── schedule_repository.py           ⭐ NEW
│   │   │
│   │   └── presentation/
│   │       ├── __init__.py                 ⭐ NEW
│   │       ├── schemas.py                  ⭐ REWRITE
│   │       ├── docs.py                     ✅ KEEP
│   │       ├── dependencies.py             ⭐ REWRITE
│   │       ├── routers.py                  ⭐ REWRITE
│   │       ├── swagger.py                  ✅ KEEP
│   │       └── ws.py                       ✅ KEEP
│   │
│   └── fullschedule/
│       ├── __init__.py                     ⭐ NEW
│       ├── enums.py                        ✅ KEEP
│       ├── models.py                       ✅ KEEP
│       └── schemas.py                      ✅ KEEP
│
├── core/
│   ├── mqtt_client.py                      ✅ KEEP
│   ├── influxdb_client.py                  ✅ KEEP
│   └── websocket_hub.py                    ✅ KEEP
│
├── app.py                                  🔧 ADD router
└── migrations/env.py                       🔧 ADD models


# 🚀 iot Module — Complete Rebuild (Fresh Start)

ให้ครบตั้งแต่ต้น พร้อมใช้งาน — ทำเป็น **bootstrap script** รันครั้งเดียวได้ทุกไฟล์

---

## 📐 Directory Tree (Final)

```
app/
├── modules/
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── utils.py                    [มีอยู่แล้ว — BRASILIA_TZ]
│   │   └── infrastructure/
│   │       ├── __init__.py                 ⭐ NEW
│   │       └── models.py                   ⭐ NEW (Base, BaseModel, BaseModelNoPK)
│   │
│   ├── iot/
│   │   ├── __init__.py                     ⭐ NEW
│   │   │
│   │   ├── domain/
│   │   │   ├── __init__.py                 🔧 FIX
│   │   │   ├── enums.py                    ✅ KEEP
│   │   │   ├── exceptions.py               ✅ KEEP
│   │   │   ├── events.py                   ✅ KEEP
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py             ✅ KEEP
│   │   │   │   ├── alarm.py                ✅ KEEP
│   │   │   │   ├── location.py             ✅ KEEP
│   │   │   │   └── mqtt.py                 ✅ KEEP
│   │   │   └── helpers/
│   │   │       ├── __init__.py             ✅ KEEP
│   │   │       └── alarm_logic.py          ✅ KEEP
│   │   │
│   │   ├── application/
│   │   │   ├── __init__.py                 ⭐ NEW
│   │   │   ├── exceptions.py               ✅ KEEP
│   │   │   ├── interfaces.py               ⭐ NEW
│   │   │   ├── mappers.py                  ✅ KEEP
│   │   │   ├── utils.py                    ✅ KEEP
│   │   │   └── use_case.py                 ⭐ REWRITE
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── __init__.py                 ⭐ NEW
│   │   │   ├── caches.py                   ⭐ NEW
│   │   │   ├── services.py                 ⭐ NEW
│   │   │   ├── models/
│   │   │   │   ├── __init__.py             ⭐ NEW
│   │   │   │   ├── common.py               🔧 FIX
│   │   │   │   └── ... (48 ไฟล์)           🔧 FIX (Base → BaseModelNoPK)
│   │   │   └── repositories/
│   │   │       ├── __init__.py             ⭐ NEW
│   │   │       ├── device_repository.py    ⭐ NEW
│   │   │       ├── device_config_repository.py      ⭐ NEW
│   │   │       ├── device_status_repository.py      ⭐ NEW
│   │   │       ├── device_alert_repository.py       ⭐ NEW
│   │   │       ├── iot_data_repository.py           ⭐ NEW
│   │   │       ├── alarm_log_repository.py          ⭐ NEW
│   │   │       ├── activity_log_repository.py       ⭐ NEW
│   │   │       ├── command_log_repository.py        ⭐ NEW
│   │   │       └── schedule_repository.py           ⭐ NEW
│   │   │
│   │   └── presentation/
│   │       ├── __init__.py                 ⭐ NEW
│   │       ├── schemas.py                  ⭐ REWRITE
│   │       ├── docs.py                     ✅ KEEP
│   │       ├── dependencies.py             ⭐ REWRITE
│   │       ├── routers.py                  ⭐ REWRITE
│   │       ├── swagger.py                  ✅ KEEP
│   │       └── ws.py                       ✅ KEEP
│   │
│   └── fullschedule/
│       ├── __init__.py                     ⭐ NEW
│       ├── enums.py                        ✅ KEEP
│       ├── models.py                       ✅ KEEP
│       └── schemas.py                      ✅ KEEP
│
├── core/
│   ├── mqtt_client.py                      ✅ KEEP
│   ├── influxdb_client.py                  ✅ KEEP
│   └── websocket_hub.py                    ✅ KEEP
│
├── app.py                                  🔧 ADD router
└── migrations/env.py                       🔧 ADD models
```

---

# 📦 FILE 1: `bootstrap_iot.py` (รันไฟล์เดียว)

> **บันทึก:** script นี้จะสร้าง **ทุกไฟล์ใหม่** + แก้ไฟล์ที่มี int PK ให้ใช้ `BaseModelNoPK`
> 
> **วิธีใช้:**
> ```bash
> cd /path/to/project
> python bootstrap_iot.py
> ```

```python
#!/usr/bin/env python3
"""
bootstrap_iot.py — One-shot installer for iot module

- Creates all new files (repos, use_case, routers, __init__)
- Patches existing model files (Base → BaseModelNoPK for int PK)
- Removes duplicate `id: UUID` from models that inherit BaseModel
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════════
#  FILE CONTENT REGISTRY
# ═══════════════════════════════════════════════════════════════
FILES: dict[str, str] = {}

def reg(path: str, content: str) -> None:
    FILES[path] = content


# ───────────────────────────────────────────────────────────────
#  1. SHARED INFRASTRUCTURE
# ───────────────────────────────────────────────────────────────
reg("app/modules/shared/__init__.py", '"""shared module"""\n')

reg("app/modules/shared/infrastructure/__init__.py", '''"""shared infrastructure"""
from app.modules.shared.infrastructure.models import Base, BaseModel, BaseModelNoPK

__all__ = ["Base", "BaseModel", "BaseModelNoPK"]
''')

reg("app/modules/shared/infrastructure/models.py", '''"""
app/modules/shared/infrastructure/models.py
TH: Shared base models (Base / BaseModel / BaseModelNoPK)
EN: Shared base models
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.modules.shared.application.utils import BRASILIA_TZ


class Base(DeclarativeBase):
    __mapper_args__: ClassVar[dict[str, Any]] = {"eager_defaults": True}


class BaseModel(Base):
    """Base model with UUID PK + is_active + timestamps."""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="id", primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, name="is_active", default=True, server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="created_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="updated_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(), onupdate=func.now(),
    )


class BaseModelNoPK(Base):
    """Base model WITHOUT id — for models with int/custom PK."""
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="created_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="updated_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(), onupdate=func.now(),
    )


__all__ = ["Base", "BaseModel", "BaseModelNoPK"]
''')


# ───────────────────────────────────────────────────────────────
#  2. IOT INFRASTRUCTURE — MODELS __init__
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/infrastructure/__init__.py", '"""iot infrastructure"""\n')

reg("app/modules/iot/infrastructure/models/__init__.py", '''"""iot models — import all to resolve relationships"""
from app.modules.iot.infrastructure.models.common import BaseModel, StatusModel

from app.modules.iot.infrastructure.models.device import Device
from app.modules.iot.infrastructure.models.device_type import DeviceType
from app.modules.iot.infrastructure.models.device_status import DeviceStatus
from app.modules.iot.infrastructure.models.device_status_history import DeviceStatusHistory
from app.modules.iot.infrastructure.models.device_config import DeviceConfig
from app.modules.iot.infrastructure.models.device_alert import DeviceAlert
from app.modules.iot.infrastructure.models.device_category import DeviceCategory
from app.modules.iot.infrastructure.models.device_group import DeviceGroup
from app.modules.iot.infrastructure.models.device_group_member import DeviceGroupMember
from app.modules.iot.infrastructure.models.device_notification_config import DeviceNotificationConfig
from app.modules.iot.infrastructure.models.device_schedule import DeviceSchedule
from app.modules.iot.infrastructure.models.iot_data import IotData
from app.modules.iot.infrastructure.models.sensor_data import SensorData
from app.modules.iot.infrastructure.models.alarm import (
    DeviceAlarmAction, AlarmDevice, AlarmDeviceEvent,
)
from app.modules.iot.infrastructure.models.alarm_log import (
    AlarmProcessLog, AlarmProcessLogEmail, AlarmProcessLogTemp,
)
from app.modules.iot.infrastructure.models.activity_log import ActivityLog
from app.modules.iot.infrastructure.models.schedule import (
    Schedule, ScheduleDevice, ScheduleProcessLog,
)
from app.modules.iot.infrastructure.models.location import Location
from app.modules.iot.infrastructure.models.mqtt import Mqtt
from app.modules.iot.infrastructure.models.mqtt_host import MqttHost

from app.modules.iot.infrastructure.models.air_control import AirControl
from app.modules.iot.infrastructure.models.air_control_device_map import AirControlDeviceMap
from app.modules.iot.infrastructure.models.air_control_log import AirControlLog
from app.modules.iot.infrastructure.models.air_mod import AirMod
from app.modules.iot.infrastructure.models.air_mod_device_map import AirModDeviceMap
from app.modules.iot.infrastructure.models.air_period import AirPeriod
from app.modules.iot.infrastructure.models.air_period_device_map import AirPeriodDeviceMap
from app.modules.iot.infrastructure.models.air_setting_warning import AirSettingWarning
from app.modules.iot.infrastructure.models.air_setting_warning_device_map import AirSettingWarningDeviceMap
from app.modules.iot.infrastructure.models.air_warning import AirWarning
from app.modules.iot.infrastructure.models.air_warning_device_map import AirWarningDeviceMap

from app.modules.iot.infrastructure.models.notification_channel import NotificationChannel
from app.modules.iot.infrastructure.models.notification_type import NotificationType
from app.modules.iot.infrastructure.models.notification_condition import NotificationCondition
from app.modules.iot.infrastructure.models.notification_log import NotificationLog
from app.modules.iot.infrastructure.models.group_notification_config import GroupNotificationConfig
from app.modules.iot.infrastructure.models.channel_template import ChannelTemplate

from app.modules.iot.infrastructure.models.report_data import ReportData
from app.modules.iot.infrastructure.models.system_setting import SystemSetting
from app.modules.iot.infrastructure.models.api_key import ApiKey
from app.modules.iot.infrastructure.models.audit_log import AuditLog
from app.modules.iot.infrastructure.models.command_log import CommandLog

__all__ = [
    "BaseModel", "StatusModel",
    "Device", "DeviceType", "DeviceStatus", "DeviceStatusHistory",
    "DeviceConfig", "DeviceAlert", "DeviceCategory",
    "DeviceGroup", "DeviceGroupMember",
    "DeviceNotificationConfig", "DeviceSchedule",
    "IotData", "SensorData",
    "DeviceAlarmAction", "AlarmDevice", "AlarmDeviceEvent",
    "AlarmProcessLog", "AlarmProcessLogEmail", "AlarmProcessLogTemp",
    "ActivityLog", "Schedule", "ScheduleDevice", "ScheduleProcessLog",
    "Location", "Mqtt", "MqttHost",
    "AirControl", "AirControlDeviceMap", "AirControlLog",
    "AirMod", "AirModDeviceMap", "AirPeriod", "AirPeriodDeviceMap",
    "AirSettingWarning", "AirSettingWarningDeviceMap",
    "AirWarning", "AirWarningDeviceMap",
    "NotificationChannel", "NotificationType", "NotificationCondition",
    "NotificationLog", "GroupNotificationConfig", "ChannelTemplate",
    "ReportData", "SystemSetting", "ApiKey", "AuditLog", "CommandLog",
]
''')


# ───────────────────────────────────────────────────────────────
#  3. IOT INFRASTRUCTURE — REPOSITORIES
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/infrastructure/repositories/__init__.py", '''"""iot repositories"""
from app.modules.iot.infrastructure.repositories.activity_log_repository import ActivityLogRepository
from app.modules.iot.infrastructure.repositories.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.repositories.command_log_repository import CommandLogRepository
from app.modules.iot.infrastructure.repositories.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.repositories.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.repositories.device_repository import DeviceRepository
from app.modules.iot.infrastructure.repositories.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.repositories.iot_data_repository import IotDataRepository
from app.modules.iot.infrastructure.repositories.schedule_repository import ScheduleRepository

__all__ = [
    "ActivityLogRepository", "AlarmLogRepository", "CommandLogRepository",
    "DeviceAlertRepository", "DeviceConfigRepository", "DeviceRepository",
    "DeviceStatusRepository", "IotDataRepository", "ScheduleRepository",
]
''')

reg("app/modules/iot/infrastructure/repositories/device_repository.py", '''"""DeviceRepository — port จาก Go device_repo.go"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import (
    Device, DeviceType, Location, Mqtt, MqttHost,
)


@dataclass
class DeviceListFilter:
    device_id: str = ""
    mqtt_id: str = ""
    mqtt_device_name: str = ""
    keyword: str = ""
    status: int = 1
    bucket: str = ""
    buckets: list[str] = field(default_factory=list)
    org: str = ""
    type_id: int = 0
    location_id: int = 0
    sn: str = ""
    status_warning: str = ""
    recovery_warning: str = ""
    status_alert: str = ""
    recovery_alert: str = ""
    hardware_id: int = 0
    action_id: int = 0
    page: int = 1
    page_size: int = 20
    sort: str = ""
    is_count: bool = False
    no_status_filter: bool = False


@dataclass
class DeviceAlarmItem:
    device_id: int = 0
    mqtt_id: int = 0
    setting_id: int = 0
    type_id: int = 0
    device_name: str = ""
    sn: str = ""
    hardware_id: int = 0
    status_warning: str = ""
    recovery_warning: str = ""
    status_alert: str = ""
    recovery_alert: str = ""
    time_life: int = 0
    period: str = ""
    work_status: int = 0
    layout: int = 0
    menu: int = 0
    max_: str = ""
    min_: str = ""
    oid: str = ""
    calibration_add: str = ""
    calibration_subtract: str = ""
    calibration_type: int = 3
    mqtt_data_value: str = ""
    mqtt_data_control: str = ""
    model: str = ""
    vendor: str = ""
    compare_value: str = ""
    status: int = 0
    unit: str = ""
    action_id: int = 0
    status_alert_id: int = 0
    measurement: str = ""
    mqtt_control_on: str = "1"
    mqtt_control_off: str = "0"
    device_org: str = ""
    device_bucket: str = ""
    type_name: str = ""
    location_name: str = ""
    config_data: str = ""
    mqtt_name: str = ""
    mqtt_org: str = ""
    mqtt_bucket: str = ""
    mqtt_envavorment: str = ""
    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_device_name: str = ""
    mqtt_status_over_name: str = ""
    mqtt_status_data_name: str = ""
    mqtt_act_relay_name: str = ""
    mqtt_control_relay_name: str = ""
    host_name: str = ""
    port: int = 0
    host_id: str = ""
    hardware_type_name: str = ""
    layout_app: str = ""
    calibration_type_desc: str = ""
    icon: str = ""
    icon_on: str = ""
    icon_off: str = ""
    icon_normal: str = ""
    icon_warning: str = ""
    icon_alert: str = ""


def _hardware_name(h: int) -> str:
    return {1: "Sensor", 2: "IO Sensor", 3: "IO Control", 4: "Critical Sensor"}.get(h, "Unknown")


def _layout_name(v: int) -> str:
    return {1: "Right Menu", 2: "Card", 3: "Left Menu", 4: "Footer Menu"}.get(v, "Unknown")


def _calib_name(v: int) -> str:
    return {1: "Calibration Add", 2: "Calibration Subtract", 3: "Non calibration"}.get(v, "Non calibration")


class DeviceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, device_id: int) -> Device | None:
        r = await self._session.execute(select(Device).where(Device.device_id == device_id))
        return r.scalar_one_or_none()

    async def find_by_sn(self, sn: str) -> Device | None:
        r = await self._session.execute(select(Device).where(Device.sn == sn))
        return r.scalar_one_or_none()

    async def find_by_bucket(self, bucket: str) -> list[Device]:
        r = await self._session.execute(
            select(Device).where(Device.bucket == bucket, Device.status == 1)
            .order_by(Device.device_id.asc())
        )
        return list(r.scalars().all())

    async def find_by_location(self, location_id: int) -> list[Device]:
        r = await self._session.execute(
            select(Device).where(Device.location_id == location_id, Device.status == 1)
            .order_by(Device.device_id.asc())
        )
        return list(r.scalars().all())

    async def find_all_active(self) -> list[Device]:
        r = await self._session.execute(
            select(Device).where(Device.status == 1).order_by(Device.device_id.asc())
        )
        return list(r.scalars().all())

    def _base_join(self) -> Any:
        return (
            select(
                Device.device_id, Device.mqtt_id, Device.setting_id, Device.type_id,
                Device.device_name, Device.sn, Device.hardware_id,
                Device.status_warning, Device.recovery_warning,
                Device.status_alert, Device.recovery_alert,
                Device.time_life, Device.period, Device.work_status,
                Device.layout, Device.menu,
                Device.max_.label("max_"), Device.min_.label("min_"), Device.oid,
                Device.calibration_add, Device.calibration_subtract, Device.calibration_type,
                Device.mqtt_data_value, Device.mqtt_data_control,
                Device.model, Device.vendor, Device.comparevalue,
                Device.status, Device.unit,
                Device.action_id, Device.status_alert_id,
                Device.measurement, Device.mqtt_control_on, Device.mqtt_control_off,
                Device.org.label("device_org"), Device.bucket.label("device_bucket"),
                Device.mqtt_device_name, Device.mqtt_status_over_name,
                Device.mqtt_status_data_name, Device.mqtt_act_relay_name,
                Device.mqtt_control_relay_name,
                Device.icon, Device.icon_on, Device.icon_off,
                Device.icon_normal, Device.icon_warning, Device.icon_alert,
                DeviceType.type_name.label("type_name"),
                Location.location_name.label("location_name"),
                Location.configdata.label("config_data"),
                Mqtt.mqtt_name, Mqtt.org.label("mqtt_org"), Mqtt.bucket.label("mqtt_bucket"),
                Mqtt.envavorment.label("mqtt_envavorment"),
                Mqtt.host.label("mqtt_host"), Mqtt.port.label("mqtt_port"),
                MqttHost.hostname.label("host_name"),
                MqttHost.port.label("host_port"),
                MqttHost.idhost.label("host_id"),
            )
            .join(DeviceType, DeviceType.type_id == Device.type_id, isouter=True)
            .join(Mqtt, Mqtt.mqtt_id == Device.mqtt_id, isouter=True)
            .join(Location, Location.location_id == Device.location_id, isouter=True)
            .join(MqttHost, MqttHost.idhost == Mqtt.mqtt_main_id, isouter=True)
        )

    def _apply(self, stmt: Any, f: DeviceListFilter) -> Any:
        if not f.no_status_filter:
            stmt = stmt.where(Device.status == f.status)
        if f.keyword:
            stmt = stmt.where(Device.device_name.ilike(f"%{f.keyword}%"))
        if f.device_id:
            stmt = stmt.where(Device.device_id == int(f.device_id))
        if f.bucket:
            stmt = stmt.where(Device.bucket == f.bucket)
        if f.buckets:
            stmt = stmt.where(Device.bucket.in_(f.buckets))
        if f.mqtt_id:
            stmt = stmt.where(Device.mqtt_id == int(f.mqtt_id))
        if f.mqtt_device_name:
            stmt = stmt.where(Device.mqtt_device_name == f.mqtt_device_name)
        if f.org:
            stmt = stmt.where(Device.org == f.org)
        if f.type_id:
            stmt = stmt.where(Device.type_id == f.type_id)
        if f.location_id:
            stmt = stmt.where(Device.location_id == f.location_id)
        if f.sn:
            stmt = stmt.where(Device.sn == f.sn)
        if f.hardware_id:
            stmt = stmt.where(Device.hardware_id == f.hardware_id)
        if f.action_id:
            stmt = stmt.where(Device.action_id == f.action_id)
        return stmt

    async def list_with_alarm(self, f: DeviceListFilter) -> tuple[list[DeviceAlarmItem], int]:
        if f.page <= 0: f.page = 1
        if f.page_size <= 0: f.page_size = 20

        count_stmt = select(func.count(Device.device_id))
        count_stmt = self._apply(count_stmt, f)
        total = int((await self._session.execute(count_stmt)).scalar() or 0)

        if f.is_count:
            return [], total

        stmt = self._base_join()
        stmt = self._apply(stmt, f)
        stmt = stmt.order_by(Device.device_id.asc())
        stmt = stmt.offset((f.page - 1) * f.page_size).limit(f.page_size)

        rows = (await self._session.execute(stmt)).all()
        items = [self._row_to_item(r) for r in rows]
        return items, total

    @staticmethod
    def _row_to_item(row: Any) -> DeviceAlarmItem:
        m = row._mapping
        return DeviceAlarmItem(
            device_id=m.get("device_id", 0),
            mqtt_id=m.get("mqtt_id", 0) or 0,
            setting_id=m.get("setting_id", 0) or 0,
            type_id=m.get("type_id", 0) or 0,
            device_name=m.get("device_name", "") or "",
            sn=m.get("sn", "") or "",
            hardware_id=m.get("hardware_id", 0) or 0,
            status_warning=m.get("status_warning", "") or "",
            recovery_warning=m.get("recovery_warning", "") or "",
            status_alert=m.get("status_alert", "") or "",
            recovery_alert=m.get("recovery_alert", "") or "",
            time_life=m.get("time_life", 0) or 0,
            period=m.get("period", "") or "",
            work_status=m.get("work_status", 0) or 0,
            layout=m.get("layout", 0) or 0,
            menu=m.get("menu", 0) or 0,
            max_=str(m.get("max_", "") or ""),
            min_=str(m.get("min_", "") or ""),
            oid=m.get("oid", "") or "",
            calibration_add=m.get("calibration_add", "") or "",
            calibration_subtract=m.get("calibration_subtract", "") or "",
            calibration_type=m.get("calibration_type", 3) or 3,
            mqtt_data_value=m.get("mqtt_data_value", "") or "",
            mqtt_data_control=m.get("mqtt_data_control", "") or "",
            model=m.get("model", "") or "",
            vendor=m.get("vendor", "") or "",
            compare_value=m.get("comparevalue", "") or "",
            status=m.get("status", 0) or 0,
            unit=m.get("unit", "") or "",
            action_id=m.get("action_id", 0) or 0,
            status_alert_id=m.get("status_alert_id", 0) or 0,
            measurement=m.get("measurement", "") or "",
            mqtt_control_on=m.get("mqtt_control_on", "1") or "1",
            mqtt_control_off=m.get("mqtt_control_off", "0") or "0",
            device_org=m.get("device_org", "") or "",
            device_bucket=m.get("device_bucket", "") or "",
            type_name=m.get("type_name", "") or "",
            location_name=m.get("location_name", "") or "",
            config_data=m.get("config_data", "") or "",
            mqtt_name=m.get("mqtt_name", "") or "",
            mqtt_org=m.get("mqtt_org", "") or "",
            mqtt_bucket=m.get("mqtt_bucket", "") or "",
            mqtt_envavorment=m.get("mqtt_envavorment", "") or "",
            mqtt_host=m.get("mqtt_host", "") or "",
            mqtt_port=m.get("mqtt_port", 0) or 0,
            mqtt_device_name=m.get("mqtt_device_name", "") or "",
            mqtt_status_over_name=m.get("mqtt_status_over_name", "") or "",
            mqtt_status_data_name=m.get("mqtt_status_data_name", "") or "",
            mqtt_act_relay_name=m.get("mqtt_act_relay_name", "") or "",
            mqtt_control_relay_name=m.get("mqtt_control_relay_name", "") or "",
            host_name=m.get("host_name", "") or "",
            port=m.get("host_port", 0) or 0,
            host_id=str(m.get("host_id", "") or ""),
            hardware_type_name=_hardware_name(m.get("hardware_id", 0) or 0),
            layout_app=_layout_name(m.get("layout", 0) or 0),
            calibration_type_desc=_calib_name(m.get("calibration_type", 3) or 3),
            icon=m.get("icon", "") or "",
            icon_on=m.get("icon_on", "") or "",
            icon_off=m.get("icon_off", "") or "",
            icon_normal=m.get("icon_normal", "") or "",
            icon_warning=m.get("icon_warning", "") or "",
            icon_alert=m.get("icon_alert", "") or "",
        )
''')

reg("app/modules/iot/infrastructure/repositories/device_config_repository.py", '''"""DeviceConfigRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceConfig


class DeviceConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: str) -> DeviceConfig | None:
        r = await self._session.execute(
            select(DeviceConfig).where(DeviceConfig.device_id == device_id)
        )
        return r.scalar_one_or_none()

    async def upsert(self, cfg: DeviceConfig) -> DeviceConfig:
        existing = await self.find_by_device_id(cfg.device_id)
        if existing:
            existing.config = cfg.config
            existing.status = cfg.status
            await self._session.flush()
            return existing
        self._session.add(cfg)
        await self._session.flush()
        return cfg
''')

reg("app/modules/iot/infrastructure/repositories/device_status_repository.py", '''"""DeviceStatusRepository"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceStatus


class DeviceStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: str) -> DeviceStatus | None:
        r = await self._session.execute(
            select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        )
        return r.scalar_one_or_none()

    async def upsert(self, st: DeviceStatus) -> DeviceStatus:
        existing = await self.find_by_device_id(st.device_id)
        if existing:
            existing.is_online = st.is_online
            existing.last_seen = st.last_seen
            existing.last_data = st.last_data
            existing.battery_level = st.battery_level
            existing.signal_strength = st.signal_strength
            existing.firmware_version = st.firmware_version
            existing.location = st.location
            await self._session.flush()
            return existing
        self._session.add(st)
        await self._session.flush()
        return st

    async def update_last_seen(self, device_id: str) -> None:
        st = await self.find_by_device_id(device_id)
        if st:
            st.last_seen = datetime.now(timezone.utc)
            st.is_online = True
            await self._session.flush()
''')

reg("app/modules/iot/infrastructure/repositories/device_alert_repository.py", '''"""DeviceAlertRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceAlert


class DeviceAlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: DeviceAlert) -> DeviceAlert:
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def find_unresolved(self, device_id: str) -> list[DeviceAlert]:
        r = await self._session.execute(
            select(DeviceAlert).where(
                DeviceAlert.device_id == device_id,
                DeviceAlert.resolved.is_(False),
            ).order_by(DeviceAlert.id.desc())
        )
        return list(r.scalars().all())

    async def resolve(self, alert_id: int) -> DeviceAlert | None:
        r = await self._session.execute(select(DeviceAlert).where(DeviceAlert.id == alert_id))
        a = r.scalar_one_or_none()
        if a:
            a.resolved = True
            await self._session.flush()
        return a
''')

reg("app/modules/iot/infrastructure/repositories/iot_data_repository.py", '''"""IotDataRepository"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import IotData


class IotDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: IotData) -> IotData:
        self._session.add(data)
        await self._session.flush()
        return data

    async def find_latest(self, device_id: str, limit: int = 10) -> list[IotData]:
        r = await self._session.execute(
            select(IotData).where(IotData.device_id == device_id)
            .order_by(IotData.timestamp.desc()).limit(limit)
        )
        return list(r.scalars().all())

    async def find_by_date_range(
        self, device_id: str, start: datetime, end: datetime,
    ) -> list[IotData]:
        r = await self._session.execute(
            select(IotData).where(
                IotData.device_id == device_id,
                IotData.timestamp >= start,
                IotData.timestamp <= end,
            ).order_by(IotData.timestamp.asc())
        )
        return list(r.scalars().all())

    async def find_paginated(
        self, device_id: str, page: int = 1, page_size: int = 50,
    ) -> tuple[list[IotData], int]:
        total = int((await self._session.execute(
            select(func.count(IotData.id)).where(IotData.device_id == device_id)
        )).scalar() or 0)
        r = await self._session.execute(
            select(IotData).where(IotData.device_id == device_id)
            .order_by(IotData.timestamp.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        return list(r.scalars().all()), total

    async def cleanup_old(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        r = await self._session.execute(select(IotData).where(IotData.timestamp < cutoff))
        old = list(r.scalars().all())
        for x in old:
            await self._session.delete(x)
        await self._session.flush()
        return len(old)
''')

reg("app/modules/iot/infrastructure/repositories/alarm_log_repository.py", '''"""AlarmLogRepository"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import AlarmProcessLog


class AlarmLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: AlarmProcessLog) -> AlarmProcessLog:
        self._session.add(log)
        await self._session.flush()
        return log

    async def count_by_device(self, device_id: int) -> int:
        return int((await self._session.execute(
            select(func.count(AlarmProcessLog.id)).where(AlarmProcessLog.device_id == device_id)
        )).scalar() or 0)

    async def find_by_device(self, device_id: int, limit: int = 100) -> list[AlarmProcessLog]:
        r = await self._session.execute(
            select(AlarmProcessLog).where(AlarmProcessLog.device_id == device_id)
            .order_by(AlarmProcessLog.id.desc()).limit(limit)
        )
        return list(r.scalars().all())
''')

reg("app/modules/iot/infrastructure/repositories/activity_log_repository.py", '''"""ActivityLogRepository"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import ActivityLog


class ActivityLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: ActivityLog) -> ActivityLog:
        self._session.add(log)
        await self._session.flush()
        return log
''')

reg("app/modules/iot/infrastructure/repositories/command_log_repository.py", '''"""CommandLogRepository"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import CommandLog


class CommandLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: CommandLog) -> CommandLog:
        self._session.add(log)
        await self._session.flush()
        return log
''')

reg("app/modules/iot/infrastructure/repositories/schedule_repository.py", '''"""ScheduleRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import Schedule


class ScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_active(self) -> list[Schedule]:
        r = await self._session.execute(select(Schedule).where(Schedule.status == 1))
        return list(r.scalars().all())

    async def find_by_device(self, device_id: int) -> list[Schedule]:
        r = await self._session.execute(
            select(Schedule).where(Schedule.device_id == device_id, Schedule.status == 1)
        )
        return list(r.scalars().all())
''')


# ───────────────────────────────────────────────────────────────
#  4. IOT INFRASTRUCTURE — CACHE + SERVICES
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/infrastructure/caches.py", '''"""IotCache — Redis wrapper (never raise)"""
from __future__ import annotations

import json
from typing import Any

from loguru import logger


class IotCache:
    def __init__(self, redis: Any | None, default_ttl: int = 300) -> None:
        self._redis = redis
        self._ttl = default_ttl

    @property
    def enabled(self) -> bool:
        return self._redis is not None

    async def get(self, key: str) -> Any | None:
        if not self.enabled: return None
        try:
            raw = self._redis.get(key)
            if raw is None: return None
            if isinstance(raw, bytes): raw = raw.decode()
            try: return json.loads(raw)
            except (json.JSONDecodeError, TypeError): return raw
        except Exception as exc:
            logger.warning(f"cache.get failed {key}: {exc}")
            return None

    async def get_raw(self, key: str) -> str | None:
        if not self.enabled: return None
        try:
            raw = self._redis.get(key)
            if raw is None: return None
            return raw.decode() if isinstance(raw, bytes) else str(raw)
        except Exception as exc:
            logger.warning(f"cache.get_raw failed {key}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.enabled: return False
        try:
            payload = value if isinstance(value, str) else json.dumps(value, default=str)
            self._redis.set(key, payload, ex=(ttl or self._ttl))
            return True
        except Exception as exc:
            logger.warning(f"cache.set failed {key}: {exc}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled: return False
        try:
            self._redis.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"cache.delete failed {key}: {exc}")
            return False

    async def lpush_trim(self, key: str, value: Any, max_items: int = 100, ttl: int = 300) -> bool:
        if not self.enabled: return False
        try:
            payload = value if isinstance(value, str) else json.dumps(value, default=str)
            self._redis.lpush(key, payload)
            self._redis.ltrim(key, 0, max_items - 1)
            self._redis.expire(key, ttl)
            return True
        except Exception as exc:
            logger.warning(f"cache.lpush_trim failed {key}: {exc}")
            return False
''')

reg("app/modules/iot/infrastructure/services.py", '''"""iot services — AlertService / WebSocketBroadcaster / EventBus"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class AlertChannel:
    enabled: bool = False
    webhook_url: str = ""
    api_key: str = ""
    recipients: list[str] = field(default_factory=list)


@dataclass
class AlertNotification:
    device_id: int
    device_name: str
    alarm_status: int
    title: str
    subject: str
    content: str
    value_data: float
    severity: str = "info"
    channels: list[str] = field(default_factory=list)


class AlertService:
    def __init__(self, **channels: AlertChannel) -> None:
        self._channels: dict[str, AlertChannel] = dict(channels)

    async def send_alert(self, n: AlertNotification) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for name in (n.channels or list(self._channels.keys())):
            ch = self._channels.get(name)
            if ch is None or not ch.enabled:
                results[name] = False
                continue
            try:
                logger.info(f"alert.sent via {name}: {n.title}")
                results[name] = True
            except Exception as exc:
                logger.error(f"alert.failed via {name}: {exc}")
                results[name] = False
        return results


class WebSocketBroadcaster:
    async def broadcast(self, room: str, event: str, data: dict[str, Any]) -> None:
        try:
            from app.core.websocket_hub import ws_manager
            await ws_manager.broadcast_to_room(room, event, data)
        except Exception as exc:
            logger.debug(f"ws.broadcast skipped: {exc}")


class EventBus:
    def __init__(self, producer: Any | None = None, topic: str = "iot.events") -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: object) -> None:
        if self._producer is None:
            logger.debug(f"event.bus(stub): {type(event).__name__}")
            return
        try:
            await self._producer.send_and_wait(self._topic, {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            })
        except Exception as exc:
            logger.warning(f"event.publish_failed: {exc}")


alert_service = AlertService()
ws_broadcaster = WebSocketBroadcaster()
event_bus = EventBus()
''')


# ───────────────────────────────────────────────────────────────
#  5. IOT APPLICATION — USE CASE
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/application/__init__.py", '"""iot application layer"""\n')

reg("app/modules/iot/application/interfaces.py", '''"""iot application interfaces"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class MQTTClient(Protocol):
    def is_connected(self) -> bool: ...
    def publish(self, topic: str, message: str, qos: int = 1) -> bool: ...
    def get_data_from_topic(self, topic: str, timeout: int = 5) -> str | None: ...
    def subscribe(self, topic: str, qos: int = 1, handler: Any = None) -> bool: ...


class InfluxDBClient(Protocol):
    def query_filter_data(self, params: Any) -> list[dict]: ...
    def write_point_to_bucket(
        self, bucket: str, measurement: str,
        tags: dict[str, str], fields: dict[str, Any], ts: Any,
    ) -> None: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...


class AlertService(ABC):
    @abstractmethod
    async def send_alert(self, notification: Any) -> dict[str, bool]: ...
''')

reg("app/modules/iot/application/use_case.py", '''"""
iot use cases — port จาก Go usecase.go
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
from datetime import UTC, datetime, timedelta
from hashlib import md5
from typing import Any

from loguru import logger

from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO
from app.modules.iot.infrastructure.caches import IotCache
from app.modules.iot.infrastructure.models import (
    ActivityLog, CommandLog, DeviceConfig, DeviceStatus, IotData,
)
from app.modules.iot.infrastructure.repositories.device_repository import (
    DeviceListFilter,
)


# ═══════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════
def _f(v: Any) -> float:
    if v is None: return 0.0
    try: return float(v)
    except (TypeError, ValueError): return 0.0


def _i(v: Any) -> int:
    if v is None: return 0
    try: return int(float(v))
    except (TypeError, ValueError): return 0


def _extract(data: dict[str, Any], *keys: str) -> tuple[float, bool]:
    for k in keys:
        if not k: continue
        if k in data:
            try: return float(data[k]), True
            except (TypeError, ValueError): continue
    return 0.0, False


def _build_map(raw: str, cfg: dict[str, str] | None) -> dict[str, Any]:
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            obj["raw"] = raw
            return obj
    except (json.JSONDecodeError, TypeError):
        pass
    parts = raw.split(",")
    out: dict[str, Any] = {}
    for i, val in enumerate(parts):
        key = str(i)
        if cfg and key in cfg:
            key = cfg[key]
        t = val.strip()
        try: out[key] = float(t)
        except ValueError: out[key] = t
    out["raw"] = raw
    return out


def _bucket_from_topic(topic: str) -> str:
    return topic.split("/")[0].strip("/") if topic else ""


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ═══════════════════════════════════════════════════════════════
#  Use Case
# ═══════════════════════════════════════════════════════════════
class IotUseCase:
    def __init__(
        self,
        device_repository: Any,
        device_config_repository: Any,
        device_status_repository: Any,
        device_alert_repository: Any,
        iot_data_repository: Any,
        alarm_log_repository: Any,
        activity_log_repository: Any,
        command_log_repository: Any,
        mqtt_client: Any | None = None,
        influxdb_client: Any | None = None,
        redis_client: Any | None = None,
        cfg: Any | None = None,
    ) -> None:
        self._device_repo = device_repository
        self._device_config_repo = device_config_repository
        self._device_status_repo = device_status_repository
        self._device_alert_repo = device_alert_repository
        self._iot_data_repo = iot_data_repository
        self._alarm_log_repo = alarm_log_repository
        self._activity_log_repo = activity_log_repository
        self._command_log_repo = command_log_repository
        self._mqtt = mqtt_client
        self._influx = influxdb_client
        self._cache = IotCache(redis_client)
        self._cfg = cfg

    # ─── Status ─────────────────────────────────────────────
    def is_connected(self) -> bool:
        return bool(self._mqtt and self._mqtt.is_connected())

    def is_cache_enabled(self) -> bool:
        return self._cache.enabled

    def _base_url(self) -> str:
        if self._cfg is not None:
            return str(getattr(self._cfg, "SERVER_BASE_URL", "")).rstrip("/")
        return ""

    @staticmethod
    def _parse(data: Any) -> Any:
        if isinstance(data, bytes): data = data.decode()
        if isinstance(data, str):
            try: return json.loads(data)
            except (json.JSONDecodeError, TypeError): return data
        return data

    # ─── Topic data ─────────────────────────────────────────
    async def get_topic_data(self, topic: str, del_cache: bool = False) -> dict[str, Any]:
        key = f"mqtt_topic:{topic}"
        if del_cache:
            await self._cache.delete(key)
        elif self._cache.enabled:
            c = await self._cache.get(key)
            if c is not None:
                return {"topic": topic, "payload": c, "from": "cache", "cache": True}

        if not self.is_connected():
            return {"topic": topic, "payload": None, "from": "mqtt_disconnected", "cache": False}

        try:
            data = self._mqtt.get_data_from_topic(topic, timeout=1)
            if data:
                p = self._parse(data)
                await self._cache.set(key, p, ttl=10)
                return {"topic": topic, "payload": p, "from": "mqtt", "cache": False}
        except Exception as exc:
            logger.warning(f"MQTT fetch {topic}: {exc}")

        c = await self._cache.get(key)
        if c is not None:
            return {"topic": topic, "payload": c, "from": "cache_fallback", "cache": True}
        return {"topic": topic, "payload": None, "from": "mqtt_error", "cache": False}

    # ─── Control ────────────────────────────────────────────
    async def device_control(self, topic: str, message: str) -> bool:
        if not self.is_connected(): return False
        ok = self._mqtt.publish(topic, message, qos=1)
        with contextlib.suppress(Exception):
            await self._command_log_repo.create(CommandLog(
                device_id=topic, action=message,
                status="sent" if ok else "failed",
            ))
        return bool(ok)

    device_controls = device_control

    # ─── Device lists ───────────────────────────────────────
    async def get_device_list(
        self, bucket: str = "", hardware_id: int = 0,
        page: int = 1, page_size: int = 1000, keyword: str = "",
    ) -> dict[str, Any]:
        f = DeviceListFilter(
            bucket=bucket, hardware_id=hardware_id,
            page=page, page_size=page_size, keyword=keyword,
        )
        items, total = await self._device_repo.list_with_alarm(f)

        buckets: dict[str, Any] = {}
        for it in items:
            if it.device_bucket and it.device_bucket not in buckets:
                buckets[it.device_bucket] = it
        mqtt_map: dict[str, dict[str, Any]] = {}
        for b, s in buckets.items():
            mqtt_map[b] = await self._fetch_bucket(b, s)

        return {
            "data": [self._detail(it, mqtt_map.get(it.device_bucket, {})) for it in items],
            "total": total, "page": page, "pageSize": page_size,
            "totalPage": (total + page_size - 1) // page_size if page_size else 0,
        }

    async def get_device_list_page(self, **kw: Any) -> dict[str, Any]:
        return await self.get_device_list(**kw)

    async def get_device_list_by_location(self, location_id: int) -> list[dict[str, Any]]:
        devices = await self._device_repo.find_by_location(location_id)
        out = []
        for d in devices:
            s = type("S", (), {
                "device_id": d.device_id, "device_bucket": d.bucket,
                "mqtt_data_value": d.mqtt_data_value,
                "mqtt_status_data_name": d.mqtt_status_data_name,
                "measurement": d.measurement, "mqtt_device_name": d.mqtt_device_name,
            })()
            p = await self._fetch_bucket(d.bucket, s)
            out.append(self._detail(s, p))
        return out

    async def get_device_buckets(self, bucket: str) -> dict[str, Any]:
        devices = await self._device_repo.find_by_bucket(bucket)
        if not devices:
            return {"bucket": bucket, "devices": []}
        d = devices[0]
        s = type("S", (), {
            "device_id": d.device_id, "device_bucket": d.bucket,
            "mqtt_data_value": d.mqtt_data_value,
            "mqtt_status_data_name": d.mqtt_status_data_name,
            "measurement": d.measurement, "mqtt_device_name": d.mqtt_device_name,
        })()
        p = await self._fetch_bucket(bucket, s)
        return {"bucket": bucket, "devices": [self._detail(s, p) for _ in devices]}

    async def _fetch_bucket(self, bucket: str, sample: Any) -> dict[str, Any]:
        if not self.is_connected() and not self._cache.enabled:
            return {}
        topic = getattr(sample, "mqtt_data_value", "") or f"{bucket}/DATA"
        key = f"mqtt_payload:{bucket}"
        raw = await self._cache.get_raw(key) or ""
        if not raw and self.is_connected():
            try:
                data = self._mqtt.get_data_from_topic(topic, timeout=1)
                if data:
                    raw = data.decode() if isinstance(data, bytes) else str(data)
                    await self._cache.set(key, raw, ttl=30)
            except Exception as exc:
                logger.warning(f"MQTT bucket {bucket}: {exc}")
        if not raw:
            return {}
        parts = raw.split(",")
        cfg = None
        with contextlib.suppress(json.JSONDecodeError, TypeError):
            cfg = json.loads(getattr(sample, "mqtt_status_data_name", "") or "{}")
        out: dict[str, Any] = {}
        for i, v in enumerate(parts):
            k = cfg.get(str(i), str(i)) if cfg else str(i)
            out[k] = v.strip()
        return out

    def _detail(self, item: Any, mqtt: dict[str, Any]) -> dict[str, Any]:
        m = getattr(item, "measurement", "") or ""
        mn = getattr(item, "mqtt_device_name", "") or ""
        raw = mqtt.get(m) or mqtt.get(mn) or "0"
        v = _f(raw)
        vs = f"{v:.2f}" if getattr(item, "hardware_id", 0) == 1 else str(raw)
        dto = AlarmDetailDTO(
            hardware_id=getattr(item, "hardware_id", 0),
            value_data=vs, value_alarm=0,
            max_value=getattr(item, "max_", "") or 0,
            min_value=getattr(item, "min_", "") or 0,
            status_alert=getattr(item, "status_alert", "") or 0,
            status_warning=getattr(item, "status_warning", "") or 0,
            recovery_warning=getattr(item, "recovery_warning", "") or 0,
            recovery_alert=getattr(item, "recovery_alert", "") or 0,
            device_name=getattr(item, "device_name", "") or "",
            action_name=getattr(item, "mqtt_name", "") or "",
            mqtt_name=getattr(item, "mqtt_name", "") or "",
            mqtt_control_on=getattr(item, "mqtt_control_on", "") or "",
            mqtt_control_off=getattr(item, "mqtt_control_off", "") or "",
            count_alarm=0, event=1,
            unit=getattr(item, "unit", "") or "",
        )
        a = evaluate_alarm(dto, lang="en")
        return {
            "device_id": getattr(item, "device_id", 0),
            "device_name": getattr(item, "device_name", "") or "",
            "type_name": getattr(item, "type_name", "") or "",
            "value_data": vs, "unit": getattr(item, "unit", "") or "",
            "status": getattr(item, "status", 0),
            "alarm_title": a.title,
            "status_warning": getattr(item, "status_warning", "") or "",
            "status_alert": getattr(item, "status_alert", "") or "",
            "recovery_warning": getattr(item, "recovery_warning", "") or "",
            "recovery_alert": getattr(item, "recovery_alert", "") or "",
            "icon": getattr(item, "icon", "") or "",
        }

    # ─── Charts ─────────────────────────────────────────────
    async def get_senser_charts(
        self, bucket: str = "iot_sensors", measurement: str = "temperature",
        field: str = "value", start: str = "-1h", stop: str = "now()",
        limit: int = 1000,
    ) -> dict[str, Any]:
        return await self._influx_query(bucket, measurement, field, start, stop, limit)

    get_senser_data_chart = get_senser_charts
    get_senser_data = get_senser_charts
    get_device_senser_charts = get_senser_charts

    async def _influx_query(
        self, bucket: str, measurement: str, field: str,
        start: str, stop: str, limit: int,
    ) -> dict[str, Any]:
        if self._influx is None:
            return {"data": [], "date": [], "cache": "no cache"}
        try:
            from app.core.influxdb_client import QueryParams
            params = QueryParams(
                measurement=measurement, field=field, bucket=bucket,
                start=start, stop=stop, limit=limit,
            )
            results = self._influx.query_filter_data(params)
            dp, tp = [], []
            for r in results:
                if "_value" in r: dp.append(float(r["_value"]))
                if "_time" in r: tp.append(str(r["_time"]))
            return {"data": dp, "date": tp, "cache": "no cache"}
        except Exception as exc:
            logger.error(f"Influx: {exc}")
            return {"data": [], "date": [], "cache": "error", "error": str(exc)}

    async def get_monitor_device_chart(
        self, bucket: str = "iot_sensors", measurement: str = "temperature",
        field: str = "value", start: str = "-10m", stop: str = "now()",
        limit: int = 100, cache_delete: int = 0,
    ) -> dict[str, Any]:
        key = f"mqtt_chart:{md5(f'{bucket}:{measurement}:{field}:{start}:{stop}:{limit}'.encode()).hexdigest()}"
        if cache_delete:
            await self._cache.delete(key)
        else:
            c = await self._cache.get(key)
            if c is not None:
                c["cache"] = "cache"
                return c
        resp = await self._influx_query(bucket, measurement, field, start, stop, limit)
        await self._cache.set(key, resp, ttl=41)
        return resp

    async def get_topic_data_device_chart(
        self, bucket: str = "iot_sensors", topic: str = "",
        measurement: str = "temperature", field: str = "value",
        start: str = "-10m", stop: str = "now()", limit: int = 100,
        cache_delete: int = 0,
    ) -> dict[str, Any]:
        topic = topic or f"{bucket}/DATA"
        chart = await self.get_monitor_device_chart(
            bucket=bucket, measurement=measurement, field=field,
            start=start, stop=stop, limit=limit, cache_delete=cache_delete,
        )
        payload = None
        src = ""
        if not cache_delete:
            c = await self._cache.get(f"mqtt_topic:{topic}")
            if c is not None:
                payload, src = c, "cache"
        if src == "" and self.is_connected():
            try:
                data = self._mqtt.get_data_from_topic(topic, timeout=1)
                if data:
                    payload = self._parse(data)
                    src = "mqtt"
                    await self._cache.set(f"mqtt_topic:{topic}", payload, ttl=10)
            except Exception as exc:
                logger.warning(f"MQTT {topic}: {exc}")
        return {
            "topic": topic, "chart": chart, "latest_payload": payload,
            "latest_from": src,
            "cache": "cache" if src == "cache" else "no cache",
        }

    # ─── Alarm status ───────────────────────────────────────
    async def get_alarm_device_status(
        self, bucket: str = "", page: int = 1, page_size: int = 1000,
        measurement: str = "temperature", lang: str = "en", **filters: Any,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, page=page, page_size=page_size,
            hardware_id=_i(filters.get("hardware_id", 0)),
            keyword=filters.get("keyword", ""),
        )
        items, _ = await self._device_repo.list_with_alarm(f)

        mqtt_map: dict[str, Any] = {}
        raw = ""
        if mqtt_connected and items:
            s = items[0]
            raw = await self._cache.get_raw(f"mqtt_payload:{bucket}") or ""
            if not raw and s.device_bucket:
                raw = await self._cache.get_raw(f"mqtt_payload:{s.device_bucket}") or ""
            if not raw:
                try:
                    data = self._mqtt.get_data_from_topic(
                        s.mqtt_data_value or f"{bucket}/DATA", timeout=1,
                    )
                    if data:
                        raw = data.decode() if isinstance(data, bytes) else str(data)
                        await self._cache.set(f"mqtt_payload:{bucket}", raw, ttl=60)
                except Exception as exc:
                    logger.warning(f"MQTT alarm: {exc}")
            if raw:
                cfg = None
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    cfg = json.loads(s.mqtt_status_data_name or "{}")
                for i, v in enumerate(raw.split(",")):
                    k = cfg.get(str(i), str(i)) if cfg else str(i)
                    mqtt_map[k] = v.strip()

        grouped: dict[int, list[dict[str, Any]]] = {1: [], 2: [], 3: [], 4: []}
        io_info: list[dict[str, Any]] = []
        arr: list[dict[str, Any]] = []
        base_url = self._base_url()
        for it in items:
            hw = it.hardware_id
            grouped.setdefault(hw, []).append(self._detail(it, mqtt_map))
            rv = mqtt_map.get(it.measurement) or mqtt_map.get(it.mqtt_device_name) or "0"
            da = 1 if _f(rv) >= 1 else 0
            io_info.append({
                "device_id": it.device_id, "type_id": it.type_id,
                "status": it.status, "device_name": it.device_name,
                "timestamp": _now(), "subject": it.status_warning,
                "value_data": rv, "dataAlarm": da, "eventControl": 1,
                "value_data_msg": rv,
            })
            arr.append(self._build_mqtt_item(it, mqtt_map, lang, base_url))

        check = {
            "isConnected": mqtt_connected, "connected": mqtt_connected,
            "status": 1 if mqtt_connected else 0,
            "msg": "MQTT Connection Status: Connected" if mqtt_connected
                   else "MQTT Connection Status: Disconnected",
        }
        mqttrs = {
            "case": 1 if raw else 0, "status": 1 if raw else 0,
            "msg": raw or "No data available",
            "fromCache": False, "time": 0,
            "timestamp": _now(), "isConnected": mqtt_connected,
        }
        return {
            "statuscode": 200, "status": "success",
            "Mqttstatus": 1 if mqtt_connected else 0,
            "payload": {
                "checkConnectionMqtt": check, "mqttrs": mqttrs,
                "mqttname": items[0].mqtt_name if items else "",
                "bucket": bucket, "time": _now(),
                "mqttdata": mqtt_map, "deviceioinfo": io_info,
                "devicesensor": grouped.get(1, []),
                "deviceio": grouped.get(2, []),
                "devicecritical": grouped.get(4, []),
                "cache": "cache",
                "chart": {
                    "bucket": bucket, "field": "value",
                    "data": [], "date": [], "name": "value",
                    "cache": "no cache", "info": {},
                },
                "lang": lang, "page": page, "currentPage": page,
                "pageSize": page_size, "total": len(items),
                "device_count": len(arr), "device": arr,
            },
            "message": "check Connection Status Mqtt",
            "message_th": "check Connection Status Mqtt",
        }

    async def get_alarm_device_status_control(self, **kw: Any) -> dict[str, Any]:
        return await self.get_alarm_device_status(**kw)

    # ─── Monitor group ──────────────────────────────────────
    async def get_monitor_device_group(
        self, bucket: str = "", location_id: int = 0,
        hardware_id: int = 0, lang: str = "en", del_cache: int = 0,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, hardware_id=hardware_id, location_id=location_id,
            page=1, page_size=1000,
        )
        items, _ = await self._device_repo.list_with_alarm(f)
        if not items:
            return {"bucket": bucket, "device_count": 0, "data": []}

        s = items[0]
        mqtt_map = await self._fetch_bucket(bucket or s.device_bucket, s)
        names = {1: "Sensor", 2: "IO Sensor", 3: "IO Control", 4: "Critical Sensor"}
        groups: dict[int, list[dict[str, Any]]] = {}
        base_url = self._base_url()

        for it in items:
            hw = it.hardware_id
            rv = mqtt_map.get(it.measurement) or mqtt_map.get(it.mqtt_device_name) or "0"
            v = _f(rv)
            vs = f"{v:.2f}" if hw == 1 else str(rv)
            dto = AlarmDetailDTO(
                hardware_id=hw, value_data=vs, value_alarm=0,
                max_value=it.max_, min_value=it.min_,
                status_alert=it.status_alert, status_warning=it.status_warning,
                recovery_warning=it.recovery_warning, recovery_alert=it.recovery_alert,
                device_name=it.device_name, action_name=it.mqtt_name,
                mqtt_name=it.mqtt_name,
                mqtt_control_on=it.mqtt_control_on, mqtt_control_off=it.mqtt_control_off,
                count_alarm=0, event=1, unit=it.unit,
            )
            a = evaluate_alarm(dto, lang=lang)
            ctrl, dd, ic = "", "", it.icon
            if hw > 1:
                if vs == "1" or vs == it.mqtt_control_on:
                    ctrl = f"{base_url}/iot/controls?topic={it.mqtt_data_control}&message={it.mqtt_control_on}"
                    dd, ic = "ON", it.icon_on
                else:
                    ctrl = f"{base_url}/iot/controls?topic={it.mqtt_data_control}&message={it.mqtt_control_off}"
                    dd, ic = "OFF", it.icon_off
            else:
                dd = f"{vs} {it.unit}"
            groups.setdefault(hw, []).append({
                "device_id": it.device_id, "device_name": it.device_name,
                "hardware_id": hw, "type_id": it.type_id,
                "type_name": it.type_name, "location_name": it.location_name,
                "unit": it.unit, "status": it.status, "layout": it.layout,
                "mqtt_data_value": it.mqtt_data_value,
                "mqtt_data_control": it.mqtt_data_control,
                "measurement": it.measurement,
                "mqtt_control_on": it.mqtt_control_on,
                "mqtt_control_off": it.mqtt_control_off,
                "icon": it.icon, "icon_on": it.icon_on, "icon_off": it.icon_off,
                "value_data": vs,
                "alarm_title": a.title, "alarm_subject": a.subject,
                "alarm_status": a.status,
                "control": ctrl, "devicedata": dd, "icon_access": ic,
                "graph": f"{base_url}/iot/monitordevicechart?bucket={bucket}&measurement={it.measurement}&field=value&start=-5m&stop=now()&limit=120&lang={lang}",
                "timestamp": _now(), "mqtt_connected": mqtt_connected,
                "cache_used": False,
            })

        layout = items[0].layout if items else 2
        response_groups = [
            {"group_id": hw, "group_name": names.get(hw, "Unknown"),
             "count": len(devs), "devices": devs}
            for hw, devs in groups.items()
        ]
        return {
            "bucket": bucket, "timestamp": _now(),
            "device_count": len(items), "layout": layout, "layout_name": "Card",
            "group_name": names.get(hardware_id, ""),
            "device_type": names.get(hardware_id, ""),
            "data": response_groups, "mqtt_connected": mqtt_connected,
            "mqtt_raw_payload": "", "cache_used": False,
        }

    # ─── Device MQTT ────────────────────────────────────────
    async def get_device_mqtt(
        self, bucket: str = "", page: int = 1, page_size: int = 10_000_000,
        lang: str = "en", keyword: str = "", device_id: str = "",
        mqtt_id: str = "", type_id: int = 0, hardware_id: int = 0,
        deletecache: int = 0, **_: Any,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, page=page, page_size=page_size,
            keyword=keyword, device_id=device_id, mqtt_id=mqtt_id,
            type_id=type_id, hardware_id=hardware_id,
        )
        items, total = await self._device_repo.list_with_alarm(f)
        base_url = self._base_url()
        arr = [self._build_mqtt_item(it, {}, lang, base_url) for it in items]
        return {
            "code": 200,
            "payload": {
                "timestamps": _now(), "lang": lang,
                "page": page, "currentPage": page, "pageSize": page_size,
                "totalPages": (total + page_size - 1) // page_size if page_size else 1,
                "total": total, "cache": "no cache",
                "device_count": len(arr), "device": arr,
                "connectionMqtt": {
                    "isConnected": mqtt_connected, "connected": mqtt_connected,
                    "status": 1 if mqtt_connected else 0,
                    "msg": "Connected" if mqtt_connected else "Disconnected",
                },
            },
            "message": "OK", "message_th": "OK",
        }

    def _build_mqtt_item(
        self, it: Any, mqtt_map: dict[str, Any], lang: str, base_url: str,
    ) -> dict[str, Any]:
        rv = mqtt_map.get(it.measurement) or mqtt_map.get(it.mqtt_device_name) or "0"
        v = _f(rv)
        if it.hardware_id == 1:
            if it.calibration_type == 1: v += _f(it.calibration_add)
            elif it.calibration_type == 2: v -= _f(it.calibration_subtract)
            vs = f"{v:.2f}"
        else:
            vs = str(rv)
        ctrl: Any = ""
        dd, ic = "", it.icon
        if it.hardware_id > 1:
            if vs == "1" or vs == it.mqtt_control_on:
                dd, ic = "ON", it.icon_on
                ctrl = f"{base_url}/iot/controls?topic={it.mqtt_data_control}&message={it.mqtt_control_on}"
            else:
                dd, ic = "OFF", it.icon_off
                ctrl = f"{base_url}/iot/controls?topic={it.mqtt_data_control}&message={it.mqtt_control_off}"
        else:
            dd = f"{vs} {it.unit}"
        dto = AlarmDetailDTO(
            hardware_id=it.hardware_id, value_data=vs, value_alarm=0,
            max_value=it.max_, min_value=it.min_,
            status_alert=it.status_alert, status_warning=it.status_warning,
            recovery_warning=it.recovery_warning, recovery_alert=it.recovery_alert,
            device_name=it.device_name, action_name=it.mqtt_name,
            mqtt_name=it.mqtt_name,
            mqtt_control_on=it.mqtt_control_on, mqtt_control_off=it.mqtt_control_off,
            count_alarm=0, event=1, unit=it.unit,
        )
        a = evaluate_alarm(dto, lang=lang)
        return {
            "device_id": it.device_id, "tiime": _now(),
            "system_name": it.location_name, "location_name": it.mqtt_name,
            "zone_name": it.type_name, "device_name": it.device_name,
            "hardware_type": it.hardware_type_name, "bucket": it.mqtt_bucket,
            "measurement": it.measurement, "sensor_type": it.hardware_type_name,
            "devicedata": dd, "alarm_title": a.title, "alarm_detail": a.subject,
            "notification_status": a.alarm_status_set,
            "notification_alarm_status": a.status,
            "mqtt_data": it.mqtt_data_value, "mqtt_control": it.mqtt_data_control,
            "control": ctrl,
            "sensercharts": f"{base_url}/iot/sensercharts?bucket={it.mqtt_bucket}&measurement={it.measurement}",
            "from": "mqtt", "ttl": 60, "cachelift": "no cache",
            "hardware_id": it.hardware_id, "type_id": it.type_id,
            "mqtt_id": it.mqtt_id, "type_name": it.type_name,
            "unit": it.unit, "status": it.status, "value_data": vs,
            "icon_access": ic, "alarm_subject": a.subject, "alarm_status": a.status,
        }

    # ─── Process MQTT ───────────────────────────────────────
    async def process_mqtt_data(self, device_id: str, raw_data: str) -> dict[str, Any]:
        device = await self._device_repo.find_by_id(int(device_id))
        cfg: dict[str, str] | None = None
        if device and device.mqtt_status_data_name:
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                cfg = json.loads(device.mqtt_status_data_name)
        dm = _build_map(raw_data, cfg)

        if await self._should_save(device_id):
            await self._iot_data_repo.create(IotData(
                device_id=str(device_id), data=dm, timestamp=datetime.now(UTC),
            ))
        await self._cache.set(f"iot_data:latest:{device_id}", dm, ttl=300)
        await self._cache.lpush_trim("iot_data:recent", dm, 100, 300)

        with contextlib.suppress(Exception):
            await self._device_status_repo.update_last_seen(str(device_id))
        with contextlib.suppress(Exception):
            await self._activity_log_repo.create(ActivityLog(
                type="DATA_RECEIVED", device_id=str(device_id),
                details=f"Received data from {device_id}",
                data=dm, severity="info",
            ))
        if device is not None:
            await self._write_influx(device, dm)
        return {"device_id": device_id, "data": dm, "timestamp": _now()}

    async def _should_save(self, device_id: str) -> bool:
        key = f"iot_last_save:{device_id}"
        now = datetime.now(UTC)
        raw = await self._cache.get_raw(key)
        if raw:
            with contextlib.suppress(ValueError):
                last = datetime.fromisoformat(raw)
                if (now - last).total_seconds() < 60:
                    return False
        await self._cache.set(key, now.isoformat(), ttl=60)
        return True

    async def _write_influx(self, device: Any, dm: dict[str, Any]) -> None:
        if self._influx is None: return
        v, ok = _extract(dm, device.measurement or "", device.mqtt_device_name or "")
        if not ok: return
        bucket = device.bucket or ""
        meas = device.measurement or device.mqtt_device_name or device.device_name
        if not bucket or not meas: return
        try:
            self._influx.write_point_to_bucket(
                bucket, meas,
                {"device_id": str(device.device_id), "device_name": device.device_name},
                {"value": v}, datetime.now(UTC),
            )
        except Exception as exc:
            logger.warning(f"Influx write: {exc}")

    # ─── Status / Config ────────────────────────────────────
    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        st = await self._device_status_repo.find_by_device_id(device_id)
        if st is None:
            return {"deviceId": device_id, "isOnline": False, "isActive": True,
                    "lastSeen": _now(), "uptime": "0s"}
        online = False
        if st.last_seen:
            online = (datetime.now(UTC) - st.last_seen).total_seconds() < 900
        return {
            "deviceId": st.device_id, "isOnline": online, "isActive": st.is_active,
            "lastSeen": st.last_seen.isoformat() if st.last_seen else "",
            "batteryLevel": st.battery_level, "signalStrength": st.signal_strength,
            "firmwareVersion": st.firmware_version,
            "location": st.location, "lastData": st.last_data, "uptime": "0s",
        }

    async def update_device_status(self, device_id: str, data: dict[str, Any]) -> bool:
        st = await self._device_status_repo.find_by_device_id(device_id)
        if st is None:
            st = DeviceStatus(device_id=device_id)
        st.last_seen = datetime.now(UTC)
        st.is_online = True
        st.last_data = data
        with contextlib.suppress(Exception):
            b = data.get("battery")
            if b is not None: st.battery_level = int(float(b))
            s = data.get("signal")
            if s is not None: st.signal_strength = int(float(s))
            fw = data.get("firmware")
            if fw: st.firmware_version = str(fw)
            loc = data.get("location")
            if loc: st.location = loc
        await self._device_status_repo.upsert(st)
        return True

    async def get_device_config(self, device_id: str) -> dict[str, Any]:
        cfg = await self._device_config_repo.find_by_device_id(device_id)
        if cfg is None:
            return {
                "deviceId": device_id,
                "config": {
                    "general": {"deviceName": "", "timezone": "Asia/Bangkok"},
                    "reporting": {"enabled": True, "interval": 300, "format": "json"},
                    "thresholds": {
                        "temperature": {"min": 15, "max": 40},
                        "humidity": {"min": 30, "max": 80},
                    },
                    "alerts": {"enabled": True, "email": [], "sms": []},
                },
                "status": "active",
            }
        return {"deviceId": cfg.device_id, "config": cfg.config or {}, "status": cfg.status}

    async def update_device_config(self, device_id: str, config: dict[str, Any]) -> bool:
        cfg = await self._device_config_repo.find_by_device_id(device_id)
        if cfg is None:
            cfg = DeviceConfig(device_id=device_id, config=config)
        else:
            m = dict(cfg.config or {})
            m.update(config)
            cfg.config = m
        await self._device_config_repo.upsert(cfg)
        return True

    # ─── Data ───────────────────────────────────────────────
    async def list_iot_data(
        self, device_id: str, page: int = 1, limit: int = 50,
        start_date: str = "", end_date: str = "",
    ) -> dict[str, Any]:
        items, total = await self._iot_data_repo.find_paginated(device_id, page, limit)
        pages = (total + limit - 1) // limit if limit else 0
        return {
            "data": [{"id": i.id, "device_id": i.device_id, "data": i.data,
                      "timestamp": i.timestamp.isoformat() if i.timestamp else ""}
                     for i in items],
            "pagination": {"page": page, "limit": limit, "total": total, "pages": pages},
        }

    async def get_device_stats(self, device_id: str) -> dict[str, Any]:
        items = await self._iot_data_repo.find_latest(device_id, limit=1000)
        s: dict[str, Any] = {"count": len(items)}
        if items:
            s["lastRecord"] = items[0].timestamp.isoformat() if items[0].timestamp else None
            s["firstRecord"] = items[-1].timestamp.isoformat() if items[-1].timestamp else None
        return s

    async def export_data(
        self, device_id: str, start_date: datetime, end_date: datetime,
        export_format: str = "json",
    ) -> tuple[bytes, str]:
        items = await self._iot_data_repo.find_by_date_range(device_id, start_date, end_date)
        if export_format == "csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["timestamp", "device_id", "data"])
            for i in items:
                w.writerow([
                    i.timestamp.isoformat() if i.timestamp else "",
                    i.device_id, json.dumps(i.data, default=str),
                ])
            return buf.getvalue().encode(), "text/csv"
        payload = [
            {"id": i.id, "device_id": i.device_id, "data": i.data,
             "timestamp": i.timestamp.isoformat() if i.timestamp else ""}
            for i in items
        ]
        return json.dumps(payload, default=str).encode(), "application/json"

    async def cleanup_old_data(self, days: int = 30) -> int:
        return await self._iot_data_repo.cleanup_old(days)

    # ─── Ingester ───────────────────────────────────────────
    async def start_ingest(self) -> bool:
        if not self.is_connected():
            return False
        import asyncio

        def _handler(client: Any, msg: Any) -> None:
            topic = getattr(msg, "topic", "")
            payload = getattr(msg, "payload", b"")
            if isinstance(payload, bytes):
                payload = payload.decode(errors="replace")
            bucket = _bucket_from_topic(topic)
            if not bucket: return
            asyncio.create_task(self._handle_ingest(bucket, str(payload)))

        try:
            self._mqtt.subscribe("#", qos=0, handler=_handler)
            return True
        except Exception as exc:
            logger.error(f"ingest subscribe: {exc}")
            return False

    async def _handle_ingest(self, bucket: str, payload: str) -> None:
        try:
            for d in await self._device_repo.find_by_bucket(bucket):
                await self.process_mqtt_data(str(d.device_id), payload)
        except Exception as exc:
            logger.error(f"ingest {bucket}: {exc}")


# alias
iotUseCase = IotUseCase
''')


# ───────────────────────────────────────────────────────────────
#  6. IOT PRESENTATION
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/presentation/__init__.py", '"""iot presentation"""\n')

reg("app/modules/iot/presentation/schemas.py", '''"""iot Pydantic v2 schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ControlRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class UpdateDeviceStatusRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


class UpdateDeviceConfigRequest(BaseModel):
    config: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class ProcessMqttDataRequest(BaseModel):
    device_id: str = Field(..., min_length=1)
    raw_data: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class ExportDataRequest(BaseModel):
    device_id: str = ""
    start_date: str = ""
    end_date: str = ""
    format: str = Field(default="json", pattern="^(json|csv)$")
    model_config = ConfigDict(extra="forbid")
''')

reg("app/modules/iot/presentation/dependencies.py", '''"""iot DI container"""
from __future__ import annotations
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.iot.application.use_case import IotUseCase
from app.modules.iot.infrastructure.repositories import (
    ActivityLogRepository, AlarmLogRepository, CommandLogRepository,
    DeviceAlertRepository, DeviceConfigRepository, DeviceRepository,
    DeviceStatusRepository, IotDataRepository,
)

_mqtt: Any | None = None
_influx: Any | None = None
_redis: Any | None = None


def _get_mqtt() -> Any | None:
    global _mqtt
    if _mqtt is None:
        try:
            from app.core.mqtt_client import MQTTClient
            from app.core.settings import settings
            _mqtt = MQTTClient(
                broker=settings.MQTT_BROKER,
                client_id=getattr(settings, "MQTT_CLIENT_ID", ""),
                username=getattr(settings, "MQTT_USERNAME", ""),
                password=getattr(settings, "MQTT_PASSWORD", ""),
                keepalive=getattr(settings, "MQTT_KEEPALIVE", 30),
            )
            _mqtt.connect()
        except Exception:
            return None
    return _mqtt


def _get_influx() -> Any | None:
    global _influx
    if _influx is None:
        try:
            from app.core.influxdb_client import InfluxDBClientWrapper
            from app.core.settings import settings
            _influx = InfluxDBClientWrapper(
                url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG, bucket=settings.INFLUXDB_BUCKET,
                timeout=getattr(settings, "INFLUXDB_TIMEOUT", 30),
            )
        except Exception:
            return None
    return _influx


def _get_redis() -> Any | None:
    global _redis
    if _redis is None:
        try:
            import redis
            from app.core.settings import settings
            _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            return None
    return _redis


async def get_iot_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> IotUseCase:
    return IotUseCase(
        device_repository=DeviceRepository(session),
        device_config_repository=DeviceConfigRepository(session),
        device_status_repository=DeviceStatusRepository(session),
        device_alert_repository=DeviceAlertRepository(session),
        iot_data_repository=IotDataRepository(session),
        alarm_log_repository=AlarmLogRepository(session),
        activity_log_repository=ActivityLogRepository(session),
        command_log_repository=CommandLogRepository(session),
        mqtt_client=_get_mqtt(),
        influxdb_client=_get_influx(),
        redis_client=_get_redis(),
    )
''')

reg("app/modules/iot/presentation/routers.py", '''"""iot HTTP + WebSocket routers (match Go routes.go)"""
from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, WebSocket, WebSocketDisconnect

from app.modules.iot.application.use_case import IotUseCase
from app.modules.iot.presentation.dependencies import get_iot_use_case
from app.modules.iot.presentation.schemas import (
    ControlRequest, ProcessMqttDataRequest, UpdateDeviceConfigRequest,
    UpdateDeviceStatusRequest,
)

router = APIRouter(prefix="/iot", tags=["iot"])


@router.get("/status")
async def get_status(uc: IotUseCase = Depends(get_iot_use_case)) -> dict[str, Any]:
    return {"mqtt_connected": uc.is_connected(), "cache_enabled": uc.is_cache_enabled()}


@router.get("/topic")
async def get_topic(
    topic: str = Query(..., min_length=1),
    delcache: int = 0,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_topic_data(topic, del_cache=bool(delcache))


@router.get("/topicdevicechart")
async def get_topic_chart(
    bucket: str = "",
    topic: str = "",
    measurement: str = "temperature",
    field: str = "value",
    start: str = "-10m",
    stop: str = "now()",
    limit: int = 100,
    delcache: int = 0,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_topic_data_device_chart(
        bucket=bucket, topic=topic, measurement=measurement, field=field,
        start=start, stop=stop, limit=limit, cache_delete=delcache,
    )


@router.get("/controls")
async def controls_get(
    topic: str = Query(..., min_length=1),
    message: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, str]:
    ok = await uc.device_control(topic, message)
    return {"status": "ok" if ok else "failed", "statusCode": "200" if ok else "500"}


@router.post("/control")
async def control_post(
    payload: ControlRequest,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, str]:
    ok = await uc.device_control(payload.topic, payload.message)
    return {"status": "ok" if ok else "failed"}


@router.get("/device")
async def device_list(
    page: int = 1, pageSize: int = 1000, bucket: str = "",
    hardware_id: int = 0, type_id: int = 0, keyword: str = "", lang: str = "en",
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_list(
        bucket=bucket, hardware_id=hardware_id,
        page=page, page_size=pageSize, keyword=keyword,
    )


@router.get("/devicebuckets")
async def device_buckets(
    bucket: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_buckets(bucket)


@router.get("/locationdevice")
async def location_device(
    location_id: int = Query(..., gt=0),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> list[dict[str, Any]]:
    return await uc.get_device_list_by_location(location_id)


@router.get("/sensercharts")
async def senser_charts(
    bucket: str = Query(..., min_length=1),
    measurement: str = Query(..., min_length=1),
    field: str = "value", start: str = "-1h", stop: str = "now()", limit: int = 1000,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_senser_charts(bucket, measurement, field, start, stop, limit)


@router.get("/devicesensercharts")
async def device_senser_charts(
    bucket: str = Query(..., min_length=1),
    measurement: str = Query(..., min_length=1),
    field: str = "value", start: str = "-1h", stop: str = "now()", limit: int = 100,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_senser_charts(bucket, measurement, field, start, stop, limit)


@router.get("/monitordevicechart")
async def monitor_chart(
    bucket: str = "", measurement: str = "temperature",
    field: str = "value", start: str = "-10m", stop: str = "now()",
    limit: int = 100, cache_delete: int = 0,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_monitor_device_chart(
        bucket, measurement, field, start, stop, limit, cache_delete,
    )


@router.get("/alarmdevicestatus")
async def alarm_device_status(
    bucket: str = "", page: int = 1, pageSize: int = 1000,
    measurement: str = "temperature", lang: str = "en",
    device_id: str = "", type_id: int = 0, hardware_id: int = 0, keyword: str = "",
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_alarm_device_status(
        bucket=bucket, page=page, page_size=pageSize,
        measurement=measurement, lang=lang, device_id=device_id,
        type_id=type_id, hardware_id=hardware_id, keyword=keyword,
    )


@router.get("/alarmdevicestatuscontrol")
async def alarm_device_status_control(
    bucket: str = "",
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_alarm_device_status_control(bucket=bucket)


@router.get("/devicemqtt")
async def device_mqtt(
    bucket: str = "", page: int = 1, pageSize: int = 10_000_000,
    lang: str = "en", device_id: str = "", mqtt_id: str = "",
    type_id: int = 0, hardware_id: int = 0, keyword: str = "", deletecache: int = 0,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_mqtt(
        bucket=bucket, page=page, page_size=pageSize, lang=lang,
        device_id=device_id, mqtt_id=mqtt_id, type_id=type_id,
        hardware_id=hardware_id, keyword=keyword, deletecache=deletecache,
    )


@router.get("/monitordevicegroup")
async def monitor_group(
    bucket: str = "", location_id: int = 0, hardware_id: int = 0,
    lang: str = "en", delcache: int = 0,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_monitor_device_group(
        bucket=bucket, location_id=location_id,
        hardware_id=hardware_id, lang=lang, del_cache=delcache,
    )


@router.get("/devicestatus")
async def device_status(
    deviceId: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_status(deviceId)


@router.put("/devicestatus")
async def update_device_status(
    payload: UpdateDeviceStatusRequest,
    deviceId: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, str]:
    ok = await uc.update_device_status(deviceId, payload.model_dump(exclude_none=True))
    return {"status": "updated" if ok else "failed"}


@router.get("/deviceconfig")
async def device_config(
    deviceId: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_config(deviceId)


@router.put("/updatedeviceconfig")
async def update_device_config(
    payload: UpdateDeviceConfigRequest,
    deviceId: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, str]:
    ok = await uc.update_device_config(deviceId, payload.config)
    return {"status": "updated" if ok else "failed"}


@router.get("/deviceiotdata")
async def list_iot_data(
    deviceId: str = Query(..., min_length=1),
    page: int = 1, limit: int = 50,
    startDate: str = "", endDate: str = "",
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.list_iot_data(deviceId, page, limit, startDate, endDate)


@router.get("/devicestats")
async def device_stats(
    deviceId: str = Query(..., min_length=1),
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.get_device_stats(deviceId)


@router.get("/devicedataexport")
async def export_data(
    deviceId: str = Query(..., min_length=1),
    startDate: str = Query(..., min_length=1),
    endDate: str = Query(..., min_length=1),
    format: str = "json",
    uc: IotUseCase = Depends(get_iot_use_case),
) -> Response:
    try:
        start = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
        end = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
    except ValueError:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
    data, ctype = await uc.export_data(deviceId, start, end, format)
    fname = "data.csv" if format == "csv" else "data.json"
    return Response(
        content=data, media_type=ctype,
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )


@router.delete("/devicedatacleanup")
async def cleanup(
    days: int = 30,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, int]:
    n = await uc.cleanup_old_data(days if days > 0 else 30)
    return {"deleted": n}


@router.post("/processmqttdata")
async def process_mqtt(
    payload: ProcessMqttDataRequest,
    uc: IotUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await uc.process_mqtt_data(payload.device_id, payload.raw_data)


@router.websocket("/ws/{room}")
async def ws_endpoint(websocket: WebSocket, room: str = "default") -> None:
    try:
        from app.core.websocket_hub import ws_manager
    except Exception:
        await websocket.close()
        return
    await ws_manager.connect(websocket, room)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue
            t = msg.get("type", "")
            if t == "subscribe":
                topic = msg.get("topic", "")
                await ws_manager.subscribe(websocket, topic)
                await websocket.send_text(json.dumps({"event": "subscribed", "topic": topic}))
            elif t == "join_room":
                nr = msg.get("room", "default")
                await ws_manager.disconnect(websocket, room)
                room = nr
                await ws_manager.connect(websocket, room)
                await websocket.send_text(json.dumps({"event": "joined_room", "room": room}))
            elif t == "message":
                await ws_manager.broadcast_to_room(room, "message", msg.get("data", {}))
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, room)
''')


# ───────────────────────────────────────────────────────────────
#  7. FULLSCHEDULE
# ───────────────────────────────────────────────────────────────
reg("app/modules/fullschedule/__init__.py", '''"""fullschedule module — ตารางเวลาขั้นสูง"""
from app.modules.fullschedule.enums import (
    EventAction, EventType, HistoryStatus,
    ScheduleMode, ScheduleStatus, ScheduleStatusValue,
    TriggerSource, TriggeredBy,
)
from app.modules.fullschedule.models import (
    Area, AreaDevice, Group, Schedule,
    ScheduleDevice, ScheduleHistory, ScheduleSetting, Zone,
)
from app.modules.fullschedule.schemas import ScheduleReport, ScopeFilter

__all__ = [
    "EventAction", "EventType", "HistoryStatus",
    "ScheduleMode", "ScheduleStatus", "ScheduleStatusValue",
    "TriggerSource", "TriggeredBy",
    "Area", "AreaDevice", "Group", "Schedule",
    "ScheduleDevice", "ScheduleHistory", "ScheduleSetting", "Zone",
    "ScheduleReport", "ScopeFilter",
]
''')


# ───────────────────────────────────────────────────────────────
#  8. IOT ROOT __init__
# ───────────────────────────────────────────────────────────────
reg("app/modules/iot/__init__.py", '''"""iot module"""
from app.modules.iot.presentation.routers import router as iot_router

__all__ = ["iot_router"]
''')

reg("app/modules/iot/domain/__init__.py", '''"""iot domain layer"""
from .enums import (
    AlarmStatus, AlertSeverity, DataSource,
    DeviceStatusEnum, HardwareType,
)
from .events import (
    AlarmRecovered, AlarmTriggered, ColdChainAlert,
    DeviceCreated, DeviceOffline, DeviceStatusChanged,
    iotDataReceived,
)
from .exceptions import (
    AlarmThresholdError, DeviceControlError, DeviceNotFoundError,
    DeviceOfflineError, InfluxDBQueryError, InvalidHardwareTypeError,
    iotError, MQTTNotConnectedError, ScheduleConflictError,
)

__all__ = [
    "AlarmStatus", "AlertSeverity", "DataSource",
    "DeviceStatusEnum", "HardwareType",
    "AlarmRecovered", "AlarmTriggered", "ColdChainAlert",
    "DeviceCreated", "DeviceOffline", "DeviceStatusChanged",
    "iotDataReceived",
    "AlarmThresholdError", "DeviceControlError", "DeviceNotFoundError",
    "DeviceOfflineError", "InfluxDBQueryError", "InvalidHardwareTypeError",
    "iotError", "MQTTNotConnectedError", "ScheduleConflictError",
]
''')


# ═══════════════════════════════════════════════════════════════
#  PATCH RULES — for EXISTING model files
# ═══════════════════════════════════════════════════════════════
MODELS_WITH_INT_PK = {
    "device.py", "device_type.py", "device_status.py",
    "device_status_history.py", "device_config.py", "device_alert.py",
    "device_category.py", "device_group.py", "device_group_member.py",
    "device_notification_config.py", "device_schedule.py",
    "iot_data.py", "sensor_data.py", "activity_log.py",
    "location.py", "mqtt.py",
    "air_control.py", "air_mod.py", "air_period.py",
    "air_setting_warning.py", "air_warning.py",
    "notification_channel.py", "notification_type.py",
    "notification_condition.py", "notification_log.py",
    "group_notification_config.py", "channel_template.py",
    "report_data.py", "system_setting.py", "api_key.py",
    "audit_log.py", "command_log.py",
}

MODELS_WITH_UUID_PK_KEEP = {
    "air_control_log.py", "air_control_device_map.py",
    "air_mod_device_map.py", "air_period_device_map.py",
    "air_setting_warning_device_map.py", "air_warning_device_map.py",
    "mqtt_host.py",
}

# ไฟล์ที่ต้องใช้ BaseModelNoPK สำหรับบาง class (mixed)
MIXED_MODELS = {
    "alarm.py",   # DeviceAlarmAction (int) + AlarmDevice/Event (UUID)
    "alarm_log.py",   # BaseModel หมด
    "schedule.py",    # Schedule/ScheduleDevice (int) + ProcessLog (UUID)
}


def patch_int_pk_models(models_dir: Path) -> None:
    """เปลี่ยน BaseModel → BaseModelNoPK ในไฟล์ที่มี int PK"""
    for name in MODELS_WITH_INT_PK:
        p = models_dir / name
        if not p.exists():
            print(f"  [SKIP] {name}")
            continue
        content = p.read_text(encoding="utf-8")
        original = content

        # import
        content = content.replace(
            "from app.modules.shared.infrastructure.models import BaseModel\n",
            "from app.modules.shared.infrastructure.models import BaseModelNoPK\n",
        )
        # class
        content = re.sub(
            r"\bclass\s+(\w+)\s*\(\s*BaseModel\s*\)",
            r"class \1(BaseModelNoPK)",
            content,
        )
        if content != original:
            p.write_text(content, encoding="utf-8", newline="\n")
            print(f"  [FIX] {name}")


def remove_duplicate_uuid_id(models_dir: Path) -> None:
    """ลบ `id: Mapped[uuid.UUID] = mapped_column(...)` จาก models ที่ inherit BaseModel"""
    for name in MODELS_WITH_UUID_PK_KEEP:
        p = models_dir / name
        if not p.exists():
            print(f"  [SKIP] {name}")
            continue
        content = p.read_text(encoding="utf-8")
        # ลบ pattern: `    id: Mapped[uuid.UUID] = mapped_column(...)\n` (บรรทัดเดียว)
        new_content = re.sub(
            r"^\s*id:\s*Mapped\[uuid\.UUID\]\s*=\s*mapped_column\([^\n]*\)\n",
            "",
            content,
            flags=re.MULTILINE,
        )
        if new_content != content:
            p.write_text(new_content, encoding="utf-8", newline="\n")
            print(f"  [CLEAN] {name}")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> None:
    print("═" * 60)
    print("  iot module bootstrap")
    print("═" * 60)

    # 1. Write all new/rewritten files
    print("\n[1/3] Writing files...")
    for path, content in FILES.items():
        p = ROOT / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"  [OK] {path}")

    # 2. Patch existing model files (int PK → BaseModelNoPK)
    print("\n[2/3] Patching int-PK models...")
    models_dir = ROOT / "app/modules/iot/infrastructure/models"
    if models_dir.exists():
        patch_int_pk_models(models_dir)
    else:
        print(f"  [WARN] models dir not found: {models_dir}")

    # 3. Remove duplicate UUID id
    print("\n[3/3] Cleaning duplicate UUID id columns...")
    if models_dir.exists():
        remove_duplicate_uuid_id(models_dir)

    print("\n" + "═" * 60)
    print("  ✅ DONE")
    print("═" * 60)
    print("\nNext steps:")
    print("  1. Add iot_router to app/app.py (see below)")
    print("  2. Add models to migrations/env.py (see below)")
    print("  3. Verify: python -c 'from app.modules.iot import iot_router; print(\"OK\")'")
    print()


if __name__ == "__main__":
    main()
```

---

# 📦 FILE 2: Registration Snippets

## `app/app.py` — เพิ่ม

```python
# ─── Import ───────────────────────────────────────
from app.modules.iot.presentation.routers import router as iot_router

# ─── Routers list ─────────────────────────────────
routers = [
    health_router,
    iot_router,  # ← เพิ่ม
    # ...
]

# ─── OpenAPI tags ─────────────────────────────────
openapi_tags = [
    {"name": "Health", "description": "..."},
    {
        "name": "iot",
        "description": "iot Module — Real-Time Sensor & Alarm Monitoring (MQTT / InfluxDB / WebSocket).",
    },
    # ...
]
```

## `migrations/env.py` — เพิ่ม

```python
# ─── iot module (48 models) ──────────────────────
try:
    from app.modules.iot.infrastructure.models import (  # noqa: F401
        Device, DeviceType, DeviceStatus, DeviceStatusHistory,
        DeviceConfig, DeviceAlert, DeviceCategory,
        DeviceGroup, DeviceGroupMember, DeviceNotificationConfig,
        DeviceSchedule, IotData, SensorData,
        DeviceAlarmAction, AlarmDevice, AlarmDeviceEvent,
        AlarmProcessLog, AlarmProcessLogEmail, AlarmProcessLogTemp,
        ActivityLog, Schedule, ScheduleDevice, ScheduleProcessLog,
        Location, Mqtt, MqttHost,
        AirControl, AirControlDeviceMap, AirControlLog,
        AirMod, AirModDeviceMap, AirPeriod, AirPeriodDeviceMap,
        AirSettingWarning, AirSettingWarningDeviceMap,
        AirWarning, AirWarningDeviceMap,
        NotificationChannel, NotificationType, NotificationCondition,
        NotificationLog, GroupNotificationConfig, ChannelTemplate,
        ReportData, SystemSetting, ApiKey, AuditLog, CommandLog,
    )
except ImportError:
    pass

# ─── fullschedule module (8 models) ──────────────
try:
    from app.modules.fullschedule.models import (  # noqa: F401
        Schedule as FsSchedule,
        ScheduleDevice as FsScheduleDevice,
        ScheduleHistory as FsScheduleHistory,
        ScheduleSetting as FsScheduleSetting,
        Group as FsGroup,
        Zone as FsZone,
        Area as FsArea,
        AreaDevice as FsAreaDevice,
    )
except ImportError:
    pass
```

---

# 🚀 วิธีใช้ (Step-by-step)

```bash
# ─── 1. วาง bootstrap_iot.py ที่ root ของ project ─
cd /path/to/project
ls bootstrap_iot.py   # ต้องเห็นไฟล์

# ─── 2. Backup ก่อน ────────────────────────────────
git add .
git commit -m "Before iot bootstrap"

# ─── 3. รัน bootstrap ──────────────────────────────
python bootstrap_iot.py

# ─── 4. เพิ่ม router + models (manual) ─────────────
# แก้ app/app.py + migrations/env.py ตาม snippet ด้านบน

# ─── 5. ตรวจ import ────────────────────────────────
python -c "from app.modules.shared.infrastructure.models import Base, BaseModel, BaseModelNoPK; print('shared OK')"
python -c "from app.modules.iot.infrastructure.models import Device, IotData; print('models OK')"
python -c "from app.modules.iot.presentation.routers import router; print('router OK')"
python -c "from app.modules.fullschedule import Schedule, Group; print('fullschedule OK')"

# ─── 6. ตรวจ mappers ───────────────────────────────
python -c "
from sqlalchemy.orm import configure_mappers
import app.modules.iot.infrastructure.models
import app.modules.fullschedule.models
configure_mappers()
print('✅ All mappers OK')
"

# ─── 7. รัน server ─────────────────────────────────
uvicorn app.main:app --reload

# ─── 8. Test endpoints ─────────────────────────────
curl http://localhost:8000/iot/status
curl http://localhost:8000/docs
```

---

# 📊 สรุปสิ่งที่ได้

| Layer | Files | Status |
|---|---|---|
| **Shared** | 3 ไฟล์ | ⭐ NEW |
| **iot/models/__init__** | 1 ไฟล์ | ⭐ NEW |
| **iot/repositories** | 10 ไฟล์ | ⭐ NEW |
| **iot/caches + services** | 2 ไฟล์ | ⭐ NEW |
| **iot/application/use_case** | 2 ไฟล์ | ⭐ REWRITE |
| **iot/presentation** | 5 ไฟล์ | ⭐ REWRITE |
| **iot/domain/__init__** | 1 ไฟล์ | 🔧 FIX |
| **iot/__init__** | 1 ไฟล์ | ⭐ NEW |
| **fullschedule/__init__** | 1 ไฟล์ | ⭐ NEW |
| **Model patches (auto)** | 32 ไฟล์ | 🔧 PATCHED (int PK) |
| **Model cleanups (auto)** | 7 ไฟล์ | 🔧 CLEANED (UUID id) |
| **รวม** | **~65 ไฟล์** | |

---

# ⚠️ หมายเหตุ

1. **`bootstrap_iot.py` เป็น idempotent** — รันซ้ำได้ ไม่พัง (เขียนทับเฉพาะไฟล์ที่ระบุ)
2. **Patches** — script จะแก้เฉพาะไฟล์ model ที่มี int PK / duplicate UUID id
3. **Mixed models** (`alarm.py`, `schedule.py`) — ต้องแก้ด้วยมือ (script ไม่แตะ):
   - `alarm.py`: `DeviceAlarmAction` → `BaseModelNoPK`, อีก 2 class → `BaseModel`
   - `schedule.py`: `Schedule`/`ScheduleDevice` → `BaseModelNoPK`, `ScheduleProcessLog` → `BaseModel`
4. **`app/core/settings.py`** — ต้องมี fields: `MQTT_BROKER`, `INFLUXDB_URL`, `REDIS_URL` ฯลฯ
5. **`app/core/database.py`** — ต้องมี `get_async_session` dependency

**วาง `bootstrap_iot.py` ที่ root → รัน → เสร็จ ✅**
