"""MQTT value objects"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class MQTTTopicData:
    """TH: MQTT topic data | EN: MQTT topic data VO"""
    topic: str
    payload: dict
    timestamp: float = 0.0


@dataclass(frozen=True)
class MQTTDeviceInfo:
    """TH: MQTT device info | EN: MQTT device info VO"""
    device_id: int
    topic: str
    name: str = ""
    broker: str = ""
    username: str = ""
    password: str = ""
