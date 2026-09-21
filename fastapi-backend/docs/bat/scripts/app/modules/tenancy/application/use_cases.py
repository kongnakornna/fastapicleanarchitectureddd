"""tenancy use cases — กรณีการใช้งาน.

Error handling: 3-branch (StandardException → DomainError → Exception)
"""

import logging

from app.shared.exceptions import DomainException, StandardException

from ..domain.entities import Tenant
from ..domain.exceptions import DomainError
from .exceptions import (
    TenancyException,
    TenantNotFoundException,
    TenantSlugConflictException,
)

logger = logging.getLogger(__name__)


class TenancyUseCases:
    """Tenancy use cases — กรณีการใช้งาน tenancy."""

    def __init__(
        self,
        repo,
        cache=None,
        schema_mgr=None,
        idempotency=None,
        audit=None,
        events=None,
    ):
        self.repo = repo
        self.cache = cache
        self.schema_mgr = schema_mgr
        self.idempotency = idempotency
        self.audit = audit
        self.events = events

    async def create_tenant(self, payload: dict, idem_key: str | None = None) -> Tenant:
        """Create tenant + schema — สร้าง tenant พร้อม schema (atomic)."""
        try:
            if idem_key and self.idempotency is not None:
                existing = await self.idempotency.get(idem_key)
                if existing is not None:
                    return existing

            tenant = Tenant(**payload)

            if await self.repo.get_by_slug(tenant.slug) is not None:
                raise TenantSlugConflictException(tenant.slug)

            # สร้าง schema ก่อน save
            if self.schema_mgr is not None:
                await self.schema_mgr.create_schema(tenant.schema_name)

            tenant = await self.repo.save(tenant)

            # read-back verify
            verified = await self.repo.get_by_id(tenant.id)
            if verified is None or verified.slug != tenant.slug:
                if self.schema_mgr is not None:
                    await self.schema_mgr.drop_schema(tenant.schema_name)
                raise TenancyException("Read-back failed")

            if self.audit is not None:
                await self.audit.log("tenant.created", tenant.id)
            if idem_key and self.idempotency is not None:
                await self.idempotency.set(idem_key, tenant)
            if self.events is not None:
                await self.events.publish("TenantCreated", tenant)

            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception:
            logger.exception("Error in create_tenant")
            raise TenancyException()

    async def suspend_tenant(self, id: str, reason: str) -> Tenant:
        """Suspend — ระงับ tenant."""
        try:
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            tenant.suspend(reason)
            tenant = await self.repo.save(tenant)
            if self.cache is not None:
                await self.cache.delete(id)
            if self.audit is not None:
                await self.audit.log("tenant.suspended", id)
            if self.events is not None:
                await self.events.publish(
                    "TenantSuspended", {"id": id, "reason": reason}
                )
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception:
            logger.exception("Error in suspend_tenant")
            raise TenancyException()

    async def upgrade_plan(self, id: str, new_plan: str) -> Tenant:
        """Upgrade plan — อัปเกรดแผน."""
        try:
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            tenant.upgrade_plan(new_plan)
            tenant = await self.repo.save(tenant)
            if self.cache is not None:
                await self.cache.delete(id)
            if self.audit is not None:
                await self.audit.log("tenant.upgraded", id)
            if self.events is not None:
                await self.events.publish(
                    "TenantPlanUpgraded", {"id": id, "plan": new_plan}
                )
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception:
            logger.exception("Error in upgrade_plan")
            raise TenancyException()

    async def get(self, id: str) -> Tenant:
        """Get by id — ดึงตาม id."""
        try:
            if self.cache is not None:
                cached = await self.cache.get(id)
                if cached is not None:
                    return cached
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            if self.cache is not None:
                await self.cache.insert(id, tenant)
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception:
            logger.exception("Error in get tenant")
            raise TenancyException()
