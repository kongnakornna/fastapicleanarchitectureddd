"""Device repository"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from loguru import logger
from sqlalchemy import String, bindparam, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceModel


# ---------------------------------------------------------------------------
# Simple listing / lookup
# ---------------------------------------------------------------------------
class DeviceRepository:
    """TH: device repo | EN: device repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_device_by_id(self, device_id: int) -> DeviceModel | None:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.device_id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_devices_by_bucket(self, bucket: str) -> list[DeviceModel]:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.bucket == bucket)
        )
        return list(result.scalars().all())

    async def get_devices_by_location(self, location_id: int) -> list[DeviceModel]:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.location_id == location_id)
        )
        return list(result.scalars().all())

    async def list_devices(
        self,
        filters: dict[str, object] | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[DeviceModel], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        allowed_columns = {
            "device_id", "type_id", "hardware_id", "location_id",
            "mqtt_id", "status", "bucket", "org",
        }

        stmt = select(DeviceModel)
        filters = filters or {}
        for key, val in filters.items():
            if key not in allowed_columns:
                continue
            # Skip empty values (matches Go's skip logic)
            if val is None or val == "" or (val == 0 and key != "status"):
                continue
            stmt = stmt.where(getattr(DeviceModel, key) == val)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self._session.execute(count_stmt)).scalar() or 0)
        if total == 0:
            return [], 0

        stmt = (
            stmt.order_by(DeviceModel.device_id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total


# ---------------------------------------------------------------------------
# Advanced listing (ListDevicesWithAlarm)
# ---------------------------------------------------------------------------
@dataclass
class DeviceListAlarmRequest:
    device_id: str | None = None
    mqtt_id: str | None = None
    mqtt_device_name: str | None = None
    keyword: str | None = None
    status: int = 0
    bucket: str | None = None
    buckets: list[str] = field(default_factory=list)
    org: str | None = None
    type_id: int = 0
    location_id: int = 0
    sn: str | None = None
    status_warning: str | None = None
    recovery_warning: str | None = None
    status_alert: str | None = None
    recovery_alert: str | None = None
    time_life: int = 0
    period: str | None = None
    max_value: str | None = None
    min_value: str | None = None
    hardware_id: int = 0
    model: str | None = None
    vendor: str | None = None
    compare_value: str | None = None
    oid: str | None = None
    action_id: int = 0
    mqtt_data_value: str | None = None
    mqtt_data_control: str | None = None
    created_date: datetime | None = None
    updated_date: datetime | None = None
    page: int = 1
    page_size: int = 10
    sort: str | None = None
    is_count: bool = False
    no_status_filter: bool = False


@dataclass
class DeviceAlarmListItem:
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
    max_value: str = ""
    min_value: str = ""
    oid: str = ""
    calibration_add: str = ""
    calibration_subtract: str = ""
    calibration_type: int = 0
    mqtt_data_value: str = ""
    mqtt_data_control: str = ""
    model: str = ""
    vendor: str = ""
    comparevalue: str = ""
    createddate: datetime | None = None
    updateddate: datetime | None = None
    status: int = 0
    unit: str = ""
    action_id: int = 0
    status_alert_id: int = 0
    measurement: str = ""
    mqtt_control_on: str = ""
    mqtt_control_off: str = ""
    device_org: str = ""
    device_bucket: str = ""
    type_name: str = ""
    location_name: str = ""
    configdata: str = ""
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
    layoutapp: str = ""
    calibrationtype: str = ""
    icon: str = ""
    icon_on: str = ""
    icon_off: str = ""
    icon_normal: str = ""
    icon_warning: str = ""
    icon_alert: str = ""


@dataclass
class PaginatedDeviceResult:
    items: list[DeviceAlarmListItem] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 10


# Whitelist of sortable columns (matches Go)
_ALLOWED_SORT_FIELDS = {
    "device_id", "device_name", "type_id", "hardware_id",
    "location_id", "status", "createddate", "updateddate", "sn",
}


def _build_filters_sql(
    req: DeviceListAlarmRequest, params: dict[str, object],
) -> list[str]:
    """TH: สร้างเงื่อนไข WHERE | EN: build WHERE clauses."""
    clauses: list[str] = []

    if req.keyword:
        clauses.append("d.device_name LIKE :keyword")
        params["keyword"] = f"%{req.keyword}%"
    if req.device_id:
        clauses.append("d.device_id = :device_id")
        params["device_id"] = req.device_id
    if req.bucket:
        clauses.append("d.bucket = :bucket")
        params["bucket"] = req.bucket
    if req.buckets:
        clauses.append("d.bucket IN :buckets")
        params["buckets"] = tuple(req.buckets)
    if req.mqtt_id:
        clauses.append("d.mqtt_id = :mqtt_id")
        params["mqtt_id"] = req.mqtt_id
    if req.mqtt_device_name:
        clauses.append("d.mqtt_device_name = :mqtt_device_name")
        params["mqtt_device_name"] = req.mqtt_device_name
    if req.org:
        clauses.append("d.org = :org")
        params["org"] = req.org
    if req.type_id:
        clauses.append("d.type_id = :type_id")
        params["type_id"] = req.type_id
    if req.location_id:
        clauses.append("d.location_id = :location_id")
        params["location_id"] = req.location_id
    if req.sn:
        clauses.append("d.sn = :sn")
        params["sn"] = req.sn
    if req.status_warning:
        clauses.append("d.status_warning = :status_warning")
        params["status_warning"] = req.status_warning
    if req.recovery_warning:
        clauses.append("d.recovery_warning = :recovery_warning")
        params["recovery_warning"] = req.recovery_warning
    if req.status_alert:
        clauses.append("d.status_alert = :status_alert")
        params["status_alert"] = req.status_alert
    if req.recovery_alert:
        clauses.append("d.recovery_alert = :recovery_alert")
        params["recovery_alert"] = req.recovery_alert
    if req.time_life:
        clauses.append("d.time_life = :time_life")
        params["time_life"] = req.time_life
    if req.period:
        clauses.append("d.period = :period")
        params["period"] = req.period
    if req.max_value:
        clauses.append("d.max = :max_value")
        params["max_value"] = req.max_value
    if req.min_value:
        clauses.append("d.min = :min_value")
        params["min_value"] = req.min_value
    if req.hardware_id:
        clauses.append("d.hardware_id = :hardware_id")
        params["hardware_id"] = req.hardware_id
    if req.model:
        clauses.append("d.model = :model")
        params["model"] = req.model
    if req.vendor:
        clauses.append("d.vendor = :vendor")
        params["vendor"] = req.vendor
    if req.compare_value:
        clauses.append("d.comparevalue = :compare_value")
        params["compare_value"] = req.compare_value
    if req.oid:
        clauses.append("d.oid = :oid")
        params["oid"] = req.oid
    if req.action_id:
        clauses.append("d.action_id = :action_id")
        params["action_id"] = req.action_id
    if req.mqtt_data_value:
        clauses.append("d.mqtt_data_value = :mqtt_data_value")
        params["mqtt_data_value"] = req.mqtt_data_value
    if req.mqtt_data_control:
        clauses.append("d.mqtt_data_control = :mqtt_data_control")
        params["mqtt_data_control"] = req.mqtt_data_control
    if req.created_date is not None:
        clauses.append("DATE(d.createddate) = :created_date")
        params["created_date"] = req.created_date.strftime("%Y-%m-%d")
    if req.updated_date is not None:
        clauses.append("DATE(d.updateddate) = :updated_date")
        params["updated_date"] = req.updated_date.strftime("%Y-%m-%d")

    return clauses


_SELECT_COLUMNS = """
    d.device_id, d.mqtt_id, d.setting_id, d.type_id, d.device_name, d.sn, d.hardware_id,
    d.status_warning, d.recovery_warning, d.status_alert, d.recovery_alert,
    d.time_life, d.period, d.work_status, d.layout, d.menu, d.max, d.min, d.oid,
    d.calibration_add, d.calibration_subtract, d.calibration_type,
    d.mqtt_data_value, d.mqtt_data_control, d.model, d.vendor, d.comparevalue,
    d.createddate, d.updateddate, d.status, d.unit, d.action_id, d.status_alert_id,
    d.measurement, d.mqtt_control_on, d.mqtt_control_off, d.org AS device_org,
    d.bucket AS device_bucket, d.mqtt_device_name, d.mqtt_status_over_name,
    d.mqtt_status_data_name, d.mqtt_act_relay_name, d.mqtt_control_relay_name,
    d.icon, d.icon_on, d.icon_off, d.icon_normal, d.icon_warning, d.icon_alert,
    t.type_name, l.location_name, l.configdata,
    mq.mqtt_name, mq.org AS mqtt_org, mq.bucket AS mqtt_bucket,
    mq.envavorment AS mqtt_envavorment, mq.host AS mqtt_host, mq.port AS mqtt_port,
    h.host_name, h.port, h.host_id,
    CASE
        WHEN d.hardware_id = 1 THEN 'Sensor'
        WHEN d.hardware_id = 2 THEN 'IO Sensor'
        WHEN d.hardware_id = 3 THEN 'IO Control'
        WHEN d.hardware_id = 4 THEN 'Critical Sensor'
        ELSE 'Unknown'
    END AS hardware_type_name,
    CASE
        WHEN d.layout = 1 THEN 'Right Menu'
        WHEN d.layout = 2 THEN 'Card'
        WHEN d.layout = 3 THEN 'Left Menu'
        WHEN d.layout = 4 THEN 'Footer Menu'
        ELSE 'Unknown'
    END AS layoutapp,
    CASE
        WHEN d.calibration_type = 1 THEN 'Calibration Add'
        WHEN d.calibration_type = 2 THEN 'Calibration Subtract'
        WHEN d.calibration_type = 3 THEN 'Non calibration'
        ELSE 'Non calibration'
    END AS calibrationtype
"""

_BASE_JOINS = """
    FROM sd_iot_device AS d
    LEFT JOIN sd_iot_device_type t ON t.type_id = d.type_id
    LEFT JOIN sd_iot_mqtt mq ON mq.mqtt_id = d.mqtt_id
    LEFT JOIN sd_iot_location l ON l.location_id = d.location_id
    LEFT JOIN sd_iot_host h ON h.idhost = mq.mqtt_main_id
"""


async def list_devices_with_alarm(
    session: AsyncSession, req: DeviceListAlarmRequest,
) -> PaginatedDeviceResult:
    """TH: ดึง device + alarm แบบ join | EN: list devices with alarm joins."""
    if req.page <= 0:
        req.page = 1
    if req.page_size <= 0:
        req.page_size = 10

    status_filter = req.status if req.status != 0 else 1

    params: dict[str, object] = {}
    where_parts: list[str] = []

    if not req.no_status_filter:
        where_parts.append("d.status = :d_status")
        where_parts.append("mq.status = :mq_status")
        params["d_status"] = status_filter
        params["mq_status"] = status_filter

    where_parts.extend(_build_filters_sql(req, params))
    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

    # --- Count-only request -------------------------------------------------
    if req.is_count:
        # SLOW SQL FIX: only device + mqtt joins are needed for the count.
        count_sql = text(
            "SELECT COUNT(*) FROM sd_iot_device AS d "
            "LEFT JOIN sd_iot_mqtt mq ON mq.mqtt_id = d.mqtt_id"
            + where_sql
        ).bindparams(
            *[bindparam(k) for k in params]
        )
        total = int(
            (await session.execute(count_sql, params)).scalar() or 0
        )
        return PaginatedDeviceResult(
            total_count=total, page=req.page, page_size=req.page_size,
        )

    # --- Count (paginated request) -----------------------------------------
    count_sql = text(
        "SELECT COUNT(*) FROM sd_iot_device AS d "
        "LEFT JOIN sd_iot_mqtt mq ON mq.mqtt_id = d.mqtt_id"
        + where_sql
    ).bindparams(*[bindparam(k) for k in params])
    total = int((await session.execute(count_sql, params)).scalar() or 0)

    # --- Sorting ------------------------------------------------------------
    order_sql = ""
    if req.sort:
        parts = req.sort.split(":", 1)
        if len(parts) == 2:
            field, order = parts[0], parts[1].upper()
            if field in _ALLOWED_SORT_FIELDS and order in ("ASC", "DESC"):
                order_sql = f" ORDER BY d.{field} {order}"
    if not order_sql:
        order_sql = " ORDER BY mq.sort ASC, d.device_id ASC"

    # --- Paginated select ---------------------------------------------------
    offset = (req.page - 1) * req.page_size
    select_sql = text(
        f"SELECT {_SELECT_COLUMNS} {_BASE_JOINS} {where_sql} {order_sql} "
        f"LIMIT :_limit OFFSET :_offset"
    ).bindparams(*[bindparam(k) for k in params])
    params["_limit"] = req.page_size
    params["_offset"] = offset

    rows = (await session.execute(select_sql, params)).mappings().all()
    items = [DeviceAlarmListItem(**dict(row)) for row in rows]

    logger.info(
        f"Listed devices with alarm: total={total}, returned={len(items)}"
    )
    return PaginatedDeviceResult(
        items=items,
        total_count=total,
        page=req.page,
        page_size=req.page_size,
    )