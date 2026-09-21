# events/application/utils.py
# Helper: @event_handler decorator — ตัวช่วย: decorator @event_handler

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def event_handler(event_type: str) -> Callable[[T], T]:
    """Mark a class as handler for given event type.

    ติดป้ายคลาสว่าเป็น handler สำหรับ event_type ที่กำหนด
    """

    def decorator(cls: T) -> T:
        cls.event_type = event_type
        return cls

    return decorator
