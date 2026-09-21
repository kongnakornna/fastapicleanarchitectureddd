from __future__ import annotations

from uuid import UUID

from app.modules.quotation.domain.entities.quotation import Quotation
from app.modules.quotation.infrastructure.quotation_repository import QuotationRepository


class QuotationUseCase:
    def __init__(self, quotation_repository: QuotationRepository) -> None:
        self._quotation_repo = quotation_repository

    async def get_quotations(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Quotation], int]:
        return await self._quotation_repo.find_all_paginated(page, page_size)

    async def get_quotation(self, quotation_id: UUID) -> Quotation | None:
        return await self._quotation_repo.find_by_id(quotation_id)

    async def create_quotation(self, quotation: Quotation) -> Quotation:
        return await self._quotation_repo.create(quotation)

    async def update_quotation(
        self, quotation_id: UUID, values: dict
    ) -> Quotation | None:
        quotation = await self._quotation_repo.find_by_id(quotation_id)
        if not quotation:
            return None
        for key, value in values.items():
            if value is not None and hasattr(quotation, key):
                setattr(quotation, key, value)
        return await self._quotation_repo.update(quotation)

    async def delete_quotation(self, quotation_id: UUID) -> bool:
        return await self._quotation_repo.delete(quotation_id)

    async def count(self) -> int:
        return await self._quotation_repo.count()
