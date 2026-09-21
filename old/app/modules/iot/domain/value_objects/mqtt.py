from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MQTTTopicData:
    """MQTT topic data value object."""

    topic: str
    payload: dict
    timestamp: float = 0.0


@dataclass(frozen=True)
class MQTTDeviceInfo:
    """MQTT device info value object."""

    device_id: int
    topic: str
    name: str = ""
    broker: str = ""
    username: str = ""
    password: str = ""
