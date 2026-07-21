from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.document.application.use_case import DocumentUseCase
from app.modules.document.domain.entities.document import Document
from app.modules.document.infrastructure.document_repository import DocumentRepository
from app.modules.document.presentation.schemas import (
    DocumentResponse,
    DocumentUploadRequest,
    PaginatedDocumentsResponse,
)

router = APIRouter(prefix="/document", tags=["Document"])


async def get_document_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> DocumentUseCase:
    return DocumentUseCase(document_repository=DocumentRepository(session))


def _doc_to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        original_name=doc.original_name,
        mime_type=doc.mime_type,
        size=doc.size,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
    )


@router.get("/")
async def get_documents(
    page: int = 1,
    per_page: int = 10,
    use_case: DocumentUseCase = Depends(get_document_use_case),
) -> PaginatedDocumentsResponse:
    per_page = min(per_page, 100)
    docs, total = await use_case.get_documents(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedDocumentsResponse(
        documents=[_doc_to_response(d) for d in docs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/")
async def create_document(
    payload: DocumentUploadRequest,
    use_case: DocumentUseCase = Depends(get_document_use_case),
) -> DocumentResponse:
    doc = Document(
        filename=payload.filename,
        original_name=payload.filename,
        mime_type=payload.mime_type,
        size=payload.size,
    )
    result = await use_case.create_document(doc)
    return _doc_to_response(result)


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    use_case: DocumentUseCase = Depends(get_document_use_case),
) -> DocumentResponse:
    from uuid import UUID

    doc = await use_case.get_document(UUID(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_to_response(doc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    use_case: DocumentUseCase = Depends(get_document_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_document(UUID(document_id))
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True}
