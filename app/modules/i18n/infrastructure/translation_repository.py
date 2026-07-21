from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.i18n.domain.entities.translation import Translation


class TranslationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, translation_id) -> Translation | None:
        result = await self._session.execute(
            select(Translation).where(Translation.id == translation_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Translation], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(Translation)
            .where(Translation.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(Translation)
            .where(Translation.is_active.is_(True))
            .order_by(Translation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_locale(
        self, locale: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[Translation], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(Translation)
            .where(Translation.locale == locale, Translation.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(Translation)
            .where(Translation.locale == locale, Translation.is_active.is_(True))
            .order_by(Translation.key.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_locale_and_key(
        self, locale: str, key: str
    ) -> Translation | None:
        result = await self._session.execute(
            select(Translation).where(
                Translation.locale == locale,
                Translation.key == key,
                Translation.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, translation: Translation) -> Translation:
        self._session.add(translation)
        await self._session.flush()
        return translation

    async def update(self, translation: Translation) -> Translation:
        await self._session.flush()
        return translation

    async def delete(self, translation_id) -> bool:
        translation = await self.find_by_id(translation_id)
        if translation:
            translation.is_active = False
            await self._session.flush()
            return True
        return False

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Translation)
            .where(Translation.is_active.is_(True))
        )
        return result.scalar() or 0

    async def count_by_locale(self, locale: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Translation)
            .where(Translation.locale == locale, Translation.is_active.is_(True))
        )
        return result.scalar() or 0
