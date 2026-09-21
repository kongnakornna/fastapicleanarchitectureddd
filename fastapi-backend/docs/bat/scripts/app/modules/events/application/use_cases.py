# events/application/use_cases.py
# Use cases for events (3-branch error handling)
# กรณีการใช้งานเหตุการณ์ (จัดการข้อผิดพลาด 3 สาขา)

import asyncio
import uuid
from datetime import UTC, datetime

from app.core.logging import logger
from app.shared.exceptions import (
    DomainException,
    StandardException,
)

from ..domain.exceptions import DomainError
from ..domain.value_objects import DomainEvent, EventEnvelope
from .exceptions import EventException


def _utcnow() -> datetime:
    return datetime.now(UTC)


class eventsUseCases:
    """Use cases for events (3-branch error handling).

    กรณีการใช้งานเหตุการณ์ — จัดการข้อผิดพลาด 3 สาขา:
      1. StandardException -> re-raise
      2. DomainError -> wrap เป็น DomainException
      3. Exception -> log + wrap เป็น ApplicationException
    """

    def __init__(
        self, bus, store, handlers=None, serializer=None, cache=None, audit=None
    ):
        self.bus = bus
        self.store = store
        self.handlers = {h.event_type: h for h in (handlers or [])}
        self.serializer = serializer
        self.cache = cache
        self.audit = audit

    # ---------- publish ----------
    async def publish(
        self, event: DomainEvent, tenant_id: str, correlation_id: str
    ) -> EventEnvelope:
        """Publish event — เผยแพร่เหตุการณ์"""
        try:
            envelope = EventEnvelope(
                event_id=str(uuid.uuid4()),
                event_type=event.event_type,
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                occurred_at=event.occurred_at,
                version=event.version,
                payload=event.payload,
            )
            await self.store.append(envelope)
            await self.bus.publish(event)
            return envelope
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in publish event")
            raise EventException() from e

    # ---------- consume ----------
    async def consume(self, raw: bytes) -> None:
        """Consume event — รับเหตุการณ์"""
        envelope: EventEnvelope | None = None
        try:
            envelope = self.serializer.deserialize(raw)

            # Idempotency check — ตรวจสอบ idempotency
            existing = await self.store.get(envelope.event_id)
            if existing is not None:
                logger.info(f"Duplicate event {envelope.event_id}, skipping")
                return

            handler = self.handlers.get(envelope.event_type)
            if not handler:
                logger.warning(f"No handler for {envelope.event_type}")
                return

            await handler.handle(envelope)
            await self.store.mark_consumed(envelope.event_id)
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e)) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in consume event")
            if envelope is not None:
                if envelope.retry_count < 5:
                    await self._retry(envelope)
                else:
                    await self._to_dlq(envelope)
            else:
                raise EventException() from e

    # ---------- retry ----------
    async def _retry(self, envelope: EventEnvelope) -> None:
        """Retry with exponential backoff — ลองใหม่แบบ exponential"""
        delay = 2**envelope.retry_count
        await asyncio.sleep(delay)
        new_env = EventEnvelope(
            event_id=envelope.event_id,
            event_type=envelope.event_type,
            tenant_id=envelope.tenant_id,
            correlation_id=envelope.correlation_id,
            occurred_at=envelope.occurred_at,
            version=envelope.version,
            payload=envelope.payload,
            retry_count=envelope.retry_count + 1,
        )
        await self.bus.publish_batch([new_env])

    # ---------- dlq ----------
    async def _to_dlq(self, envelope: EventEnvelope) -> None:
        """Send to DLQ — ส่งไป DLQ"""
        await self.bus.publish_to_dlq(envelope)


# Backward-compat alias
EventUseCases = eventsUseCases
