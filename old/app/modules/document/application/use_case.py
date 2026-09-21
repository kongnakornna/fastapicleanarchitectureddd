from __future__ import annotations

from uuid import UUID

from app.modules.document.domain.entities.document import Document
from app.modules.document.infrastructure.document_repository import DocumentRepository


class DocumentUseCase:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self._doc_repo = document_repository

    async def get_documents(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Document], int]:
        return await self._doc_repo.find_all_paginated(page, page_size)

    async def get_document(self, document_id: UUID) -> Document | None:
        return await self._doc_repo.find_by_id(document_id)

    async def get_by_filename(self, filename: str) -> Document | None:
        return await self._doc_repo.find_by_filename(filename)

    async def create_document(self, document: Document) -> Document:
        return await self._doc_repo.create(document)

    async def update_document(self, document_id: UUID, values: dict) -> Document | None:
        document = await self._doc_repo.find_by_id(document_id)
        if not document:
            return None
        for key, value in values.items():
            if value is not None and hasattr(document, key):
                setattr(document, key, value)
        return await self._doc_repo.update(document)

    async def delete_document(self, document_id: UUID) -> bool:
        return await self._doc_repo.delete(document_id)

    async def count(self) -> int:
        return await self._doc_repo.count()
