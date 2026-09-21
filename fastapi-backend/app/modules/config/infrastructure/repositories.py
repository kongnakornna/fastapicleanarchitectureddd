"""
Infrastructure Repositories — ที่เก็บ config
PostgresConfigRepository: จัดการ override 3 ระดับ (USER > TENANT > GLOBAL)
"""

from __future__ import annotations

from core.infrastructure.repositories import BaseRepository
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.interfaces import IConfigRepository
from ..domain.entities import ConfigEntry
from ..domain.enums import ConfigScope
from .models import ConfigEntryModel


class PostgresConfigRepository(BaseRepository, IConfigRepository):
    """
    Postgres Config Repository — ที่เก็บ config ใน PostgreSQL
    รองรับ 3-level override: USER > TENANT > GLOBAL
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.session = session

    # ---------- Mapping ----------
    @staticmethod
    def _to_entity(model: ConfigEntryModel) -> ConfigEntry:
        """แปลง ORM → Entity"""
        return ConfigEntry(
            id=str(model.id),
            key=model.key,
            value=model.value,
            value_type=model.value_type,
            scope=model.scope,
            scope_id=model.scope_id,
            is_secret=bool(model.is_secret),
            description=model.description or "",
        )

    @staticmethod
    def _to_model(entry: ConfigEntry) -> ConfigEntryModel:
        """แปลง Entity → ORM"""
        return ConfigEntryModel(
            key=entry.key,
            value=entry.value,
            value_type=entry.value_type,
            scope=entry.scope,
            scope_id=entry.scope_id,
            is_secret=entry.is_secret,
            description=entry.description,
        )

    # ---------- Queries ----------
    async def get(self, key: str, scope: str, scope_id: str) -> ConfigEntry | None:
        """
        ดึง config ตาม key + scope + scope_id (2-branch error handling)
        """
        try:
            stmt = select(ConfigEntryModel).where(
                ConfigEntryModel.key == key,
                ConfigEntryModel.scope == scope,
                ConfigEntryModel.scope_id == scope_id,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None
        except Exception as e:
            logger.opt(exception=e).error(
                f"Error getting config {key}/{scope}/{scope_id}"
            )
            raise

    async def get_effective(
        self, key: str, tenant_id: str, user_id: str | None
    ) -> ConfigEntry | None:
        """
        ดึง config ที่มีผลจริง — override 3 ระดับ
        ลำดับความสำคัญ: USER > TENANT > GLOBAL
        """
        try:
            # สร้างรายการ (scope, scope_id) ตามลำดับความสำคัญ
            candidates: list[tuple[str, str]] = []
            if user_id:
                candidates.append((ConfigScope.USER.value, user_id))
            candidates.append((ConfigScope.TENANT.value, tenant_id))
            candidates.append((ConfigScope.GLOBAL.value, "GLOBAL"))

            for scope, scope_id in candidates:
                entry = await self.get(key, scope, scope_id)
                if entry is not None:
                    return entry
            return None
        except Exception as e:
            logger.opt(exception=e).error(f"Error getting effective config {key}")
            raise

    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """
        บันทึก config (upsert by key+scope+scope_id)
        """
        try:
            existing = await self.get(entry.key, entry.scope, entry.scope_id)
            if existing:
                stmt = select(ConfigEntryModel).where(
                    ConfigEntryModel.key == entry.key,
                    ConfigEntryModel.scope == entry.scope,
                    ConfigEntryModel.scope_id == entry.scope_id,
                )
                result = await self.session.execute(stmt)
                model = result.scalar_one()
                model.value = entry.value
                model.value_type = entry.value_type
                model.is_secret = entry.is_secret
                model.description = entry.description
            else:
                model = self._to_model(entry)
                self.session.add(model)

            await self.session.flush()
            await self.session.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            logger.opt(exception=e).error(f"Error saving config {entry.key}")
            raise

    async def list(self, scope: str, scope_id: str) -> list[ConfigEntry]:
        """แสดงรายการ config ตาม scope"""
        try:
            stmt = (
                select(ConfigEntryModel)
                .where(
                    ConfigEntryModel.scope == scope,
                    ConfigEntryModel.scope_id == scope_id,
                )
                .order_by(ConfigEntryModel.key)
            )
            result = await self.session.execute(stmt)
            return [self._to_entity(m) for m in result.scalars().all()]
        except Exception as e:
            logger.opt(exception=e).error(f"Error listing config {scope}/{scope_id}")
            raise

    async def delete(self, key: str, scope: str, scope_id: str) -> bool:
        """ลบ config entry"""
        try:
            stmt = select(ConfigEntryModel).where(
                ConfigEntryModel.key == key,
                ConfigEntryModel.scope == scope,
                ConfigEntryModel.scope_id == scope_id,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            await self.session.delete(model)
            await self.session.flush()
            return True
        except Exception as e:
            logger.opt(exception=e).error(
                f"Error deleting config {key}/{scope}/{scope_id}"
            )
            raise
