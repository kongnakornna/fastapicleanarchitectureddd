"""iot enums — Enum ของ iot"""
from __future__ import annotations
from enum import IntEnum, StrEnum


class HardwareType(IntEnum):
    """TH: ประเภท hardware | EN: Hardware type"""
    SENSOR = 1
    IO_SENSOR = 2
    IO_CONTROL = 3
    CRITICAL_SENSOR = 4


class AlarmStatus(IntEnum):
    """TH: สถานะ alarm | EN: Alarm status"""
    NORMAL = 5
    WARNING = 1
    CRITICAL = 2
    RECOVERY_WARNING = 3
    RECOVERY_CRITICAL = 4


class DeviceStatusEnum(StrEnum):
    """TH: สถานะ device | EN: Device status"""
    ACTIVE = "ACTIVE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"


class AlertSeverity(StrEnum):
    """TH: ระดับความรุนแรง | EN: Alert severity"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataSource(StrEnum):
    """TH: แหล่งข้อมูล | EN: Data source"""
    MQTT = "mqtt"
    CACHE = "cache"
    CACHE_FALLBACK = "cache_fallback"
    INFLUXDB = "influxdb"
    POSTGRES = "postgres"
