"""Base alert handler"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AlertChannel:
    """Config ของ channel"""
    enabled: bool = False
    recipients: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertMessage:
    """ข้อความ alert"""
    device_id: int
    device_name: str
    alarm_status: int
    title: str
    subject: str
    content: str
    value_data: float
    unit: str = ""
    severity: str = "info"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAlertHandler(ABC):
    """Base ของ channel handler"""

    def __init__(self, config: AlertChannel) -> None:
        self.config = config

    @abstractmethod
    async def send(self, msg: AlertMessage) -> bool:
        """ส่งข้อความ → True ถ้าสำเร็จ"""

    @property
    @abstractmethod
    def name(self) -> str: ...