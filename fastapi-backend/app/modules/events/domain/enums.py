# events/domain/enums.py
# Enums: EventStatus, EventPriority, EventCategory
# ตัวเลือก: สถานะ, ความสำคัญ, หมวดหมู่เหตุการณ์

from enum import Enum


class EventStatus(str, Enum):
    """Event lifecycle status — สถานะวงจรชีวิตเหตุการณ์"""

    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    PROCESSING = "PROCESSING"
    CONSUMED = "CONSUMED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


class EventPriority(str, Enum):
    """Event priority — ความสำคัญเหตุการณ์"""

    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class EventCategory(str, Enum):
    """Event category — หมวดหมู่เหตุการณ์"""

    MONEY = "MONEY"
    GOODS = "GOODS"
    USER = "USER"
    SYSTEM = "SYSTEM"
    IoT = "IoT"
