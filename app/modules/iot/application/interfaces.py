"""iot application interfaces"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class MQTTClient(Protocol):
    def is_connected(self) -> bool: ...
    def publish(self, topic: str, message: str, qos: int = 1) -> bool: ...
    def get_data_from_topic(self, topic: str, timeout: int = 5) -> str | None: ...
    def subscribe(self, topic: str, qos: int = 1) -> bool: ...


class InfluxDBClient(Protocol):
    def query_filter_data(self, params: Any) -> list[dict]: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...


class AlertService(ABC):
    @abstractmethod
    async def send_alert(self, notification: Any) -> dict[str, bool]: ...
