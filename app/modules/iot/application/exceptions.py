"""iot application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    """TH: base | EN: base"""


class DeviceNotFoundAppError(ApplicationError):
    """TH: ไม่พบ device | EN: device not found"""


class DuplicateDeviceError(ApplicationError):
    """TH: device ซ้ำ | EN: duplicate device"""


class MQTTNotConnectedAppError(ApplicationError):
    """TH: MQTT ไม่เชื่อมต่อ | EN: MQTT not connected"""


class InfluxDBQueryAppError(ApplicationError):
    """TH: InfluxDB query ล้มเหลว | EN: InfluxDB query failed"""
