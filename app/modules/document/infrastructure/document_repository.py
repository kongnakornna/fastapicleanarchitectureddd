from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.document.domain.entities.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Document], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(Document)
            .where(Document.is_active.is_(True))
            .order_by(Document.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_filename(self, filename: str) -> Document | None:
        result = await self._session.execute(
            select(Document).where(
                Document.filename == filename,
                Document.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.is_active.is_(True))
        )
        return result.scalar() or 0

    async def create(self, document: Document) -> Document:
        self._session.add(document)
        await self._session.flush()
        return document

    async def update(self, document: Document) -> Document:
        await self._session.flush()
        return document

    async def delete(self, document_id: UUID) -> bool:
        document = await self.find_by_id(document_id)
        if document:
            document.is_active = False
            await self._session.flush()
            return True
        return False
