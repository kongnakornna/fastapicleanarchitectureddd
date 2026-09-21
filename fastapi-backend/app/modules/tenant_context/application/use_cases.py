"""tenant_context use cases — กรณีการใช้งาน tenant context."""

from __future__ import annotations

import logging

from app.shared.exceptions import DomainException, StandardException

from ..domain.value_objects import TenantContext
from .exceptions import TenantContextException

logger = logging.getLogger(__name__)


class TenantContextUseCases:
    """Tenant context use cases — จัดการ context ของ tenant."""

    def __init__(self, provider=None, resolver=None, cache=None, events=None):
        self.provider = provider
        self.resolver = resolver
        self.cache = cache
        self.events = events

    async def establish(self, tenant_id: str, request_id: str = "") -> TenantContext:
        """Establish tenant context — สร้าง context."""
        try:
            ctx = TenantContext(tenant_id=tenant_id, request_id=request_id)
            if self.provider is not None:
                await self.provider.set(ctx)
            if self.events is not None:
                await self.events.publish("TenantContextEstablished", ctx)
            return ctx
        except StandardException:
            raise
        except DomainException:
            raise
        except Exception:
            logger.exception("Error in establish tenant context")
            raise TenantContextException()

    async def resolve_and_establish(
        self, identifier: str, request_id: str = ""
    ) -> TenantContext:
        """Resolve tenant by identifier and establish context."""
        try:
            if self.resolver is None:
                raise TenantContextException("Resolver not configured")
            tenant_id = await self.resolver.resolve(identifier)
            return await self.establish(tenant_id, request_id)
        except StandardException:
            raise
        except DomainException:
            raise
        except Exception:
            logger.exception("Error in resolve_and_establish")
            raise TenantContextException()

    async def current(self) -> TenantContext | None:
        """Get current context — ดึง context ปัจจุบัน."""
        try:
            if self.provider is None:
                return None
            return await self.provider.get()
        except StandardException:
            raise
        except DomainException:
            raise
        except Exception:
            logger.exception("Error in current()")
            raise TenantContextException()
