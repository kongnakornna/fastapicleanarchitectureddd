"""DeviceRepository — port จาก Go device_repo.go"""
from __future__ import annotations

from dataclasses import dataclass, field
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


def _hw_name(h: int) -> str:
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
        return [self._row_to_item(r) for r in rows], total

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
            hardware_type_name=_hw_name(m.get("hardware_id", 0) or 0),
            layout_app=_layout_name(m.get("layout", 0) or 0),
            calibration_type_desc=_calib_name(m.get("calibration_type", 3) or 3),
            icon=m.get("icon", "") or "",
            icon_on=m.get("icon_on", "") or "",
            icon_off=m.get("icon_off", "") or "",
            icon_normal=m.get("icon_normal", "") or "",
            icon_warning=m.get("icon_warning", "") or "",
            icon_alert=m.get("icon_alert", "") or "",
        )
