# events/application/exceptions.py
# Application-layer exceptions — ข้อยกเว้นชั้นแอปพลิเคชัน

from app.shared.exceptions import ApplicationException


class EventException(ApplicationException):
    """Base application exception for events — ข้อยกเว้นฐาน"""

    code = "evt_APP_ERROR"


class EventHandlerNotFoundException(EventException):
    """No handler registered for event type — ไม่พบ handler"""

    code = "evt_HANDLER_NOT_FOUND"


class EventSerializationException(EventException):
    """Serialization / deserialization failed — แปลงข้อมูลล้มเหลว"""

    code = "evt_SERIALIZATION_ERROR"


class EventMaxRetriesExceededException(EventException):
    """Max retries exceeded, routed to DLQ — เกินจำนวน retry สูงสุด"""

    code = "evt_MAX_RETRIES_EXCEEDED"
