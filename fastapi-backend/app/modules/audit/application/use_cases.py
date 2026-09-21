"""
Audit Use Cases — กรณีการใช้งาน audit
Audit Use Cases — application use cases for audit module
"""

from __future__ import annotations

from typing import Any

from audit.application.exceptions import AuditException
from audit.domain.entities import AuditLog
from audit.domain.enums import AuditAction, AuditSeverity
from audit.domain.events import AuditEventNames
from audit.domain.exceptions import AuditDomainError
from loguru import logger
from app.shared.tenant_context import get_context
from app.shared.exceptions import DomainException, StandardException


class AuditUseCases:
    """
    Audit use cases — กรณีการใช้งาน audit

    Orchestrates audit log creation, verification, and publishing.
    """

    def __init__(self, repo, cache, publisher, events) -> None:
        self.repo = repo
        self.cache = cache
        self.publisher = publisher
        self.events = events

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        severity: str | None = None,
    ) -> AuditLog:
        """Append audit log — เพิ่มบันทึก audit"""
        try:
            ctx = get_context()
            before = before or {}
            after = after or {}

            if severity is None:
                try:
                    act_enum = AuditAction(action)
                    severity = (
                        AuditSeverity.CRITICAL.value
                        if act_enum.is_critical()
                        else AuditSeverity.INFO.value
                    )
                except ValueError:
                    severity = AuditSeverity.INFO.value

            log = AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_id=ctx.user_id or "system",
                before_state=before,
                after_state=after,
                ip_address=getattr(ctx, "ip_address", "") or "",
                user_agent=getattr(ctx, "user_agent", "") or "",
                correlation_id=ctx.correlation_id or "",
                severity=severity,
            )

            # Persist (append-only)
            log = await self.repo.append(log)

            # Read-back verification
            verified = await self.repo.get_by_id(log.id)
            if not verified:
                raise AuditException("Read-back verification failed")

            # Warm cache (never-raise)
            await self.cache.insert(log.id, log)

            # Publish to Kafka + event bus
            await self.publisher.publish(log)
            await self.events.publish(AuditEventNames.AUDIT_LOGGED, log)

            return log

        except StandardException:
            raise
        except AuditDomainError as e:
            raise DomainException(e) from e
        except Exception as e:
            logger.opt(exception=e).error("Error in audit log")
            raise AuditException() from e

    async def get(self, log_id: str) -> AuditLog | None:
        """Get audit log by id (cache-first) — ดึง audit log ตาม id"""
        try:
            cached = await self.cache.get(log_id)
            if cached is not None:
                return cached
            log = await self.repo.get_by_id(log_id)
            if log is not None:
                await self.cache.insert(log_id, log)
            return log
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in audit get")
            raise AuditException() from e

    async def query(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs — ค้นหาบันทึก audit"""
        try:
            result = await self.repo.query(filters, page, limit)
            _, total = result
            await self.events.publish(
                AuditEventNames.AUDIT_QUERY_EXECUTED,
                {
                    "filters": filters,
                    "page": page,
                    "limit": limit,
                    "total": total,
                },
            )
            return result
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in audit query")
            raise AuditException() from e

    async def resource_history(
        self, resource_type: str, resource_id: str
    ) -> list[AuditLog]:
        """Get full history of a resource — ดึงประวัติทั้งหมดของ resource"""
        try:
            filters = {
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
            items, _ = await self.repo.query(filters, page=1, limit=10_000)
            return sorted(items, key=lambda x: x.occurred_at)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in resource history")
            raise AuditException() from e
