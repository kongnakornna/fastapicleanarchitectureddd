"""tenancy infrastructure repositories — Postgres repo (2-branch)."""

import logging
from datetime import UTC, datetime

from app.shared.exceptions import InfrastructureException, StandardException

from ..domain.entities import Tenant

logger = logging.getLogger(__name__)


class TenancyRepositoryException(InfrastructureException):
    """Repository exception."""

    code = "ten_REPO_ERROR"


class PostgresTenantRepository:
    """PostgresTenantRepository — 2-branch error handling."""

    def __init__(self, session):
        self.session = session

    async def save(self, tenant: Tenant) -> Tenant:
        try:
            tenant.updated_at = datetime.now(UTC)
            # TODO: SQLAlchemy upsert
            return tenant
        except StandardException:
            raise
        except Exception:
            logger.exception("Repo save failed")
            raise TenancyRepositoryException()

    async def get_by_id(self, id: str) -> Tenant | None:
        try:
            # TODO: select
            return None
        except StandardException:
            raise
        except Exception:
            logger.exception("Repo get_by_id failed")
            raise TenancyRepositoryException()

    async def get_by_slug(self, slug: str) -> Tenant | None:
        try:
            # TODO: select
            return None
        except StandardException:
            raise
        except Exception:
            logger.exception("Repo get_by_slug failed")
            raise TenancyRepositoryException()

    async def list(self, page: int, limit: int) -> tuple[list[Tenant], int]:
        try:
            # TODO: pagination query
            return [], 0
        except StandardException:
            raise
        except Exception:
            logger.exception("Repo list failed")
            raise TenancyRepositoryException()

    async def soft_delete(self, id: str) -> None:
        try:
            # TODO: UPDATE deleted_at
            return
        except StandardException:
            raise
        except Exception:
            logger.exception("Repo soft_delete failed")
            raise TenancyRepositoryException()
