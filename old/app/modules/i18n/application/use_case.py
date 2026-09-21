from __future__ import annotations

from app.modules.i18n.domain.entities.translation import Translation
from app.modules.i18n.infrastructure.translation_repository import (
    TranslationRepository,
)


class I18nUseCase:
    def __init__(self, translation_repository: TranslationRepository) -> None:
        self._translation_repo = translation_repository

    async def get_translations(
        self,
        locale: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Translation], int]:
        if locale:
            return await self._translation_repo.find_by_locale(
                locale, page, page_size
            )
        return await self._translation_repo.find_all_paginated(page, page_size)

    async def get_translation(self, translation_id) -> Translation | None:
        return await self._translation_repo.find_by_id(translation_id)

    async def get_by_locale_and_key(
        self, locale: str, key: str
    ) -> Translation | None:
        return await self._translation_repo.find_by_locale_and_key(locale, key)

    async def create_translation(self, translation: Translation) -> Translation:
        return await self._translation_repo.create(translation)

    async def update_translation(
        self, translation_id, values: dict
    ) -> Translation | None:
        translation = await self._translation_repo.find_by_id(translation_id)
        if not translation:
            return None
        for key, value in values.items():
            if value is not None and hasattr(translation, key):
                setattr(translation, key, value)
        return await self._translation_repo.update(translation)

    async def delete_translation(self, translation_id) -> bool:
        return await self._translation_repo.delete(translation_id)

    async def count(self) -> int:
        return await self._translation_repo.count()

    async def count_by_locale(self, locale: str) -> int:
        return await self._translation_repo.count_by_locale(locale)
