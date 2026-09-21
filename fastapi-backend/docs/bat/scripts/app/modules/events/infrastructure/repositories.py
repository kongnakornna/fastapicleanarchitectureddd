# events/infrastructure/repositories.py
# Postgres repository for events (2-branch error handling)
# ที่เก็บเหตุการณ์ Postgres (จัดการข้อผิดพลาด 2 สาขา)

from datetime import UTC, datetime

from sqlalchemy import select

from app.core.logging import logger
from app.shared.exceptions import InfrastructureException

from ..application.mappers import EventMapper
from ..domain.enums import EventStatus
from ..domain.value_objects import EventEnvelope
from .models import EventStoreModel


class eventsRepositoryException(InfrastructureException):
    """Repository error for events — ข้อผิดพลาดที่เก็บเหตุการณ์"""

    code = "evt_REPO_ERROR"


class PostgreseventsRepository:
    """Postgres repository for events (2-branch error handling).

    ที่เก็บเหตุการณ์ Postgres — จัดการข้อผิดพลาด 2 สาขา:
      1. StandardException -> re-raise
      2. Exception -> log + wrap เป็น InfrastructureException
    """

    def __init__(self, session, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id

    async def append(self, envelope: EventEnvelope) -> None:
        """Append envelope (append-only, dedup by event_id) — เพิ่มเหตุการณ์"""
        try:
            model = EventMapper.envelope_to_orm(envelope)
            self.session.add(model)
            await self.session.flush()
        except InfrastructureException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("evt.repo.append.failed")
            raise eventsRepositoryException() from e

    async def get(self, event_id: str) -> EventEnvelope | None:
        """Get envelope by event_id — ดึงเหตุการณ์ตาม id"""
        try:
            stmt = select(EventStoreModel).where(
                EventStoreModel.event_id == event_id,
                EventStoreModel.tenant_id == self.tenant_id,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return EventMapper.orm_to_envelope(model)
        except InfrastructureException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("evt.repo.get.failed")
            raise eventsRepositoryException() from e

    async def mark_consumed(self, event_id: str) -> None:
        """Mark event as consumed — ทำเครื่องหมายว่าบริโภคแล้ว"""
        try:
            stmt = select(EventStoreModel).where(
                EventStoreModel.event_id == event_id,
                EventStoreModel.tenant_id == self.tenant_id,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is not None:
                model.status = EventStatus.CONSUMED.value
                model.consumed_at = datetime.now(UTC)
                await self.session.flush()
        except InfrastructureException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("evt.repo.mark_consumed.failed")
            raise eventsRepositoryException() from e
