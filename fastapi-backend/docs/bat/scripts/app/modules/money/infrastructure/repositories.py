"""Money repositories — SQLAlchemy async"""
from __future__ import annotations

import uuid
from decimal import Decimal

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import Money
from ..domain.enums import MoneyStatus
from ..domain.value_objects import Money
from .models import MoneyModel

log = structlog.get_logger()


class RepositoryError(Exception):
    """RepositoryError — ข้อผิดพลาด infrastructure"""


class SQLAlchemyMoneyRepository:
    """SQLAlchemyMoneyRepository — repository implementation"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _to_entity(row: MoneyModel) -> Money:
        return Money(
            id=row.id,
            tenant_id=row.tenant_id,
            code=row.code,
            name=row.name,
            amount=Money(Decimal(str(row.amount))),
            status=MoneyStatus(row.status),
            version=row.version,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )

    async def save(self, entity: Money) -> Money:
        """TH: บันทึก (flush เท่านั้น ห้าม commit) | EN: save (flush only)"""
        try:
            row = await self.session.get(MoneyModel, entity.id)
            if row is None:
                row = MoneyModel(
                    id=entity.id,
                    tenant_id=entity.tenant_id,
                    code=entity.code,
                    name=entity.name,
                    amount=entity.amount.amount,
                    status=entity.status.value,
                    version=entity.version,
                    metadata_=entity.metadata,
                    deleted_at=entity.deleted_at,
                )
                self.session.add(row)
            else:
                row.name = entity.name
                row.amount = entity.amount.amount
                row.status = entity.status.value
                row.version = entity.version
                row.metadata_ = entity.metadata
                row.deleted_at = entity.deleted_at
            await self.session.flush()
            return entity
        except Exception as e:
            raise RepositoryError(f"save failed: {e}") from e

    async def soft_delete(self, entity_id: uuid.UUID) -> None:
        try:
            row = await self.session.get(MoneyModel, entity_id)
            if row is not None:
                row.deleted_at = func.now()
                await self.session.flush()
        except Exception as e:
            raise RepositoryError(f"soft_delete failed: {e}") from e

    async def get_by_id(self, entity_id: uuid.UUID) -> Money | None:
        stmt = select(MoneyModel).where(
            MoneyModel.id == entity_id,
            MoneyModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_code(self, code: str) -> Money | None:
        stmt = select(MoneyModel).where(
            MoneyModel.code == code,
            MoneyModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list(
        self,
        *,
        status: str | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Money], int]:
        base = select(MoneyModel).where(
            MoneyModel.deleted_at.is_(None)
        )
        if status:
            base = base.where(MoneyModel.status == status)
        if q:
            like = f"%{q}%"
            base = base.where(
                or_(
                    MoneyModel.code.ilike(like),
                    MoneyModel.name.ilike(like),
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = base.order_by(MoneyModel.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(r) for r in rows], int(total)