# events/domain/events.py
# Domain event names (meta) — ชื่อเหตุการณ์โดเมน (meta)


class EventNames:
    """Meta domain event names — ชื่อเหตุการณ์โดเมนระดับ meta"""

    EVENT_PUBLISHED = "EventPublished"
    EVENT_CONSUMED = "EventConsumed"
    EVENT_FAILED = "EventFailed"
    EVENT_DEAD_LETTERED = "EventDeadLettered"
