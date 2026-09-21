"""tenancy infrastructure services — Postgres schema manager."""

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


class PostgresSchemaManager:
    """PostgresSchemaManager — จัดการ PostgreSQL schema."""

    def __init__(self, session):
        self.session = session

    async def create_schema(self, schema_name: str) -> None:
        """Create schema — สร้าง schema."""
        try:
            await self.session.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            )
            await self.session.flush()
        except Exception:
            logger.exception("Schema create failed: %s", schema_name)
            raise

    async def drop_schema(self, schema_name: str) -> None:
        """Drop schema — ลบ schema."""
        try:
            await self.session.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
            await self.session.flush()
        except Exception:
            logger.exception("Schema drop failed: %s", schema_name)
            raise

    async def schema_exists(self, schema_name: str) -> bool:
        """Check schema exists — ตรวจสอบ schema."""
        try:
            result = await self.session.execute(
                text(
                    "SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"
                ),
                {"s": schema_name},
            )
            return result.first() is not None
        except Exception:
            logger.exception("Schema check failed: %s", schema_name)
            return False
