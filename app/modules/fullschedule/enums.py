"""Fullschedule enums"""
from __future__ import annotations
from enum import Enum


class ScheduleMode(str, Enum):
    WEEKLY = "weekly"
    FULL = "full"
    BATCH = "batch"


class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ScheduleStatusValue(int, Enum):
    INACTIVE = 0
    ACTIVE = 1
    DRAFT = 3


class EventType(str, Enum):
    DEVICE = "device"
    EMAIL = "email"


class EventAction(str, Enum):
    ON = "ON"
    OFF = "OFF"
    START = "start"
    STOP = "stop"


class HistoryStatus(str, Enum):
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TriggerSource(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CRON = "cron"


class TriggeredBy(str, Enum):
    SYSTEM = "system"
    MANUAL = "manual"


__all__ = [
    "ScheduleMode", "ScheduleStatus", "ScheduleStatusValue",
    "EventType", "EventAction", "HistoryStatus",
    "TriggerSource", "TriggeredBy",
]
