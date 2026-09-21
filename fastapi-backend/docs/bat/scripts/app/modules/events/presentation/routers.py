# events/presentation/routers.py
# HTTP routers — เราเตอร์ HTTP

import uuid

from fastapi import APIRouter, Depends, HTTPException

from ..domain.value_objects import DomainEvent
from .dependencies import get_events_use_cases
from .schemas import EventCreate, EventPage, EventQuery, EventSchema

router = APIRouter(prefix="/api/v1/events", tags=["Events"])


@router.get("/", response_model=EventPage)
async def list_events(
    filters: EventQuery = Depends(),
    use_cases=Depends(get_events_use_cases),
):
    """List events — แสดงรายการเหตุการณ์"""
    # TODO: implement list via repository
    return EventPage(items=[], total=0, limit=filters.limit, offset=filters.offset)


@router.get("/{event_id}/", response_model=EventSchema)
async def get_event(
    event_id: str,
    use_cases=Depends(get_events_use_cases),
):
    """Get event by id — ดึงเหตุการณ์ตาม id"""
    envelope = await use_cases.store.get(event_id)
    if envelope is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventSchema(**envelope.to_dict())


@router.post("/", response_model=EventSchema, status_code=201)
async def publish_event(
    body: EventCreate,
    use_cases=Depends(get_events_use_cases),
):
    """Publish event — เผยแพร่เหตุการณ์"""
    event = DomainEvent(
        event_type=body.event_type,
        aggregate_id=body.aggregate_id,
        payload=body.payload,
        version=body.version,
    )
    tenant_id = "00000000-0000-0000-0000-000000000001"
    correlation_id = str(uuid.uuid4())
    envelope = await use_cases.publish(event, tenant_id, correlation_id)
    return EventSchema(**envelope.to_dict())


@router.post("/{event_id}/replay/", response_model=EventSchema)
async def replay_event(
    event_id: str,
    use_cases=Depends(get_events_use_cases),
):
    """Replay event (admin only) — เล่นเหตุการณ์ซ้ำ (ผู้ดูแลเท่านั้น)"""
    envelope = await use_cases.store.get(event_id)
    if envelope is None:
        raise HTTPException(status_code=404, detail="Event not found")
    await use_cases.bus.publish_batch([envelope])
    return EventSchema(**envelope.to_dict())


@router.get("/dlq/", response_model=EventPage)
async def list_dlq(
    filters: EventQuery = Depends(),
    use_cases=Depends(get_events_use_cases),
):
    """List dead-letter queue — แสดงรายการ DLQ"""
    # TODO: implement DLQ listing
    return EventPage(items=[], total=0, limit=filters.limit, offset=filters.offset)


@router.post("/dlq/{event_id}/retry/", response_model=EventSchema)
async def retry_dlq(
    event_id: str,
    use_cases=Depends(get_events_use_cases),
):
    """Retry a DLQ message — ลองใหม่ข้อความ DLQ"""
    envelope = await use_cases.store.get(event_id)
    if envelope is None:
        raise HTTPException(status_code=404, detail="Event not found")
    await use_cases._retry(envelope)
    return EventSchema(**envelope.to_dict())
