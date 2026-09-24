"""iot domain layer — ชั้นโดเมน iot

TH: domain layer ไม่ export SQLAlchemy entities แล้ว
    ให้ import จาก `app.modules.iot.infrastructure.models` แทน
EN: domain layer no longer exports SQLAlchemy entities.
    Import from `app.modules.iot.infrastructure.models` instead.
"""
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
