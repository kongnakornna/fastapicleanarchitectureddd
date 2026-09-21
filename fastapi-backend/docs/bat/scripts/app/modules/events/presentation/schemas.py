# events/presentation/schemas.py
# Pydantic schemas — สคีมา Pydantic

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventSchema(BaseModel):
    """Event read schema — สคีมาอ่านเหตุการณ์"""

    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    tenant_id: str
    correlation_id: str | None = None
    occurred_at: datetime
    version: int
    payload: dict
    status: str = "PENDING"
    retry_count: int = 0


class EventQuery(BaseModel):
    """Event query filters — ตัวกรองคำค้นหา"""

    event_type: str | None = None
    status: str | None = None
    correlation_id: str | None = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class EventPage(BaseModel):
    """Paginated events — หน้าของเหตุการณ์"""

    items: list[EventSchema]
    total: int
    limit: int
    offset: int


class EventCreate(BaseModel):
    """Event publish request — คำขอเผยแพร่เหตุการณ์"""

    event_type: str
    aggregate_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    version: int = 1
