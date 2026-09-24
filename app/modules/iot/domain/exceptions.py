"""iot domain exceptions — ข้อยกเว้นโดเมน iot"""
from __future__ import annotations


class iotError(Exception):
    """TH: base error | EN: base error"""


class DeviceNotFoundError(iotError):
    """TH: ไม่พบ device | EN: device not found"""


class DeviceOfflineError(iotError):
    """TH: device offline | EN: device offline"""


class MQTTNotConnectedError(iotError):
    """TH: MQTT ไม่เชื่อมต่อ | EN: MQTT not connected"""


class InvalidHardwareTypeError(iotError):
    """TH: hardware type ไม่ถูกต้อง | EN: invalid hardware type"""


class AlarmThresholdError(iotError):
    """TH: threshold ผิดพลาด | EN: alarm threshold error"""


class ScheduleConflictError(iotError):
    """TH: schedule ทับซ้อน | EN: schedule conflict"""


class InfluxDBQueryError(iotError):
    """TH: InfluxDB query ล้มเหลว | EN: InfluxDB query failed"""


class DeviceControlError(iotError):
    """TH: ส่งคำสั่ง control ล้มเหลว | EN: device control failed"""
