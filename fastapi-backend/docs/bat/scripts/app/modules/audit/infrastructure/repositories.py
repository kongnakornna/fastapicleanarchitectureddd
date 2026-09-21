"""
Audit Repository — repository audit
Audit Repository — Postgres append-only repository
"""

from __future__ import annotations

from typing import Any

from audit.application.exceptions import AuditImmutableViolation
from audit.application.mappers import AuditMapper
from audit.domain.entities import AuditLog
from audit.infrastructure.models import AuditLogModel
from loguru import logger
from app.shared.exceptions import RepositoryException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgresAuditRepository:
    """
    Postgres audit repository — repository audit บน Postgres

    Append-only: provides `append()` + `get_by_id()` + `query()`.
    NO update/delete methods by design.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Append-only API — API แบบ append-only
    # ------------------------------------------------------------------
    async def append(self, log: AuditLog) -> AuditLog:
        """
        Append audit log — เพิ่มบันทึก audit

        2-branch error handling: known vs unexpected.
        """
        try:
            model = AuditLogModel(**AuditMapper.to_model_dict(log))
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return AuditMapper.to_entity(model)
        except RepositoryException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error appending audit log")
            raise RepositoryException() from e

    async def get_by_id(self, id: str) -> AuditLog | None:
        """Get by id — ดึงตาม id"""
        try:
            result = await self.session.execute(
                select(AuditLogModel).where(AuditLogModel.id == id)
            )
            model = result.scalar_one_or_none()
            return AuditMapper.to_entity(model) if model else None
        except RepositoryException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error fetching audit log")
            raise RepositoryException() from e

    async def query(
        self, filters: dict[str, Any], page: int, limit: int
    ) -> tuple[list[AuditLog], int]:
        """
        Query with filters + pagination — ค้นหาพร้อม filter + pagination

        Supported filters: action, resource_type, resource_id,
        actor_id, correlation_id, severity, from_date, to_date.
        """
        try:
            stmt = select(AuditLogModel)
            count_stmt = select(func.count()).select_from(AuditLogModel)

            conditions = []
            if filters.get("action"):
                conditions.append(AuditLogModel.action == filters["action"])
            if filters.get("resource_type"):
                conditions.append(
                    AuditLogModel.resource_type == filters["resource_type"]
                )
            if filters.get("resource_id"):
                conditions.append(AuditLogModel.resource_id == filters["resource_id"])
            if filters.get("actor_id"):
                conditions.append(AuditLogModel.actor_id == filters["actor_id"])
            if filters.get("correlation_id"):
                conditions.append(
                    AuditLogModel.correlation_id == filters["correlation_id"]
                )
            if filters.get("severity"):
                conditions.append(AuditLogModel.severity == filters["severity"])
            if filters.get("from_date"):
                conditions.append(AuditLogModel.occurred_at >= filters["from_date"])
            if filters.get("to_date"):
                conditions.append(AuditLogModel.occurred_at <= filters["to_date"])

            for c in conditions:
                stmt = stmt.where(c)
                count_stmt = count_stmt.where(c)

            stmt = (
                stmt.order_by(AuditLogModel.occurred_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )

            rows = (await self.session.execute(stmt)).scalars().all()
            total = (await self.session.execute(count_stmt)).scalar_one()

            return [AuditMapper.to_entity(r) for r in rows], int(total)
        except RepositoryException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error querying audit logs")
            raise RepositoryException() from e

    # ------------------------------------------------------------------
    # Explicitly blocked operations — operation ที่บล็อคชัดเจน
    # ------------------------------------------------------------------
    async def update(self, *args, **kwargs) -> None:
        """Blocked: audit log is immutable — บล็อค: audit log เป็น immutable"""
        raise AuditImmutableViolation("update() is forbidden on audit_logs")

    async def delete(self, *args, **kwargs) -> None:
        """Blocked: audit log is append-only — บล็อค: audit log เป็น append-only"""
        raise AuditImmutableViolation("delete() is forbidden on audit_logs")
