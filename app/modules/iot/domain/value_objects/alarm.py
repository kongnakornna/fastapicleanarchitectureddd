from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AlarmDetailDTO:
    """Alarm detail input - translated from Go: pkg/helpers/iot.go AlarmDetailDto"""

    hardware_id: Any
    value_data: Any
    value_alarm: Any
    value_relay: Any = None
    value_control_relay: Any = None
    max_value: Any = None
    min_value: Any = None
    status_alert: Any = None
    status_warning: Any = None
    recovery_warning: Any = None
    recovery_alert: Any = None
    device_name: str = ""
    action_name: str = ""
    mqtt_name: str = ""
    mqtt_control_on: str = ""
    mqtt_control_off: str = ""
    count_alarm: Any = 0
    event: Any = 0
    unit: str = ""
    sensor_value_data: Any = None


@dataclass(frozen=True)
class AlarmDetailResult:
    """Alarm detail output - translated from Go: pkg/helpers/iot.go AlarmDetailResult"""

    status: int
    status_control: int
    alarm_type_id: int
    type_id: int
    hardware_id: int
    alarm_status_set: int
    title: str
    subject: str
    content: str
    value_data: Any
    value_alarm: Any
    value_relay: Any
    value_control_relay: Any
    data_alarm: int
    data_alarm_raw: int
    max_value: Any
    min_value: Any
    event_control: int
    message_mqtt_control: str
    sensor_data: Any
    count_alarm: int
    mqtt_name: str
    mqtt_name_str: str
    device_name_str: str
    mqtt_control_on_str: str
    unit: str
    sensor_value: Any
    status_alert_val: int = 0
    status_warning_val: int = 0
    recovery_warning_val: int = 0
    recovery_alert_val: int = 0
    device_name_val: str = ""
    alarm_action_name: str = ""
    mqtt_control_on_val: str = ""
    mqtt_control_off_val: str = ""
    event_val: int = 0
    timestamp: str = ""
    lang: str = ""


@dataclass(frozen=True)
class MQTTConfig:
    """MQTT configuration value object."""

    broker: str
    client_id: str = ""
    username: str = ""
    password: str = ""
    keepalive: int = 30
    clean_session: bool = True


@dataclass(frozen=True)
class InfluxDBConfig:
    """InfluxDB configuration value object."""

    url: str
    token: str
    org: str
    bucket: str
    timeout: int = 30


@dataclass(frozen=True)
class Location:
    """Location value object."""

    location_id: int = 0
    location_name: str = ""
    config_data: str = ""
