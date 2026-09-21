"""tenant_context infrastructure repositories."""

from __future__ import annotations

import logging

from app.shared.exceptions import InfrastructureException, StandardException

logger = logging.getLogger(__name__)


class TenantContextRepositoryException(InfrastructureException):
    """Repository exception."""

    code = "tenant_ctx_REPO_ERROR"


class PostgresTenantResolver:
    """Postgres tenant resolver — resolve tenant จาก DB."""

    def __init__(self, session):
        self.session = session

    async def resolve(self, identifier: str) -> str:
        """Resolve identifier to tenant_id."""
        try:
            # TODO: SELECT tenant_id FROM tenants WHERE slug = :identifier
            return identifier
        except StandardException:
            raise
        except Exception:
            logger.exception("Error resolving tenant")
            raise TenantContextRepositoryException()
