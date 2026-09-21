from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.quotation.application.use_case import QuotationUseCase
from app.modules.quotation.domain.entities.quotation import Quotation
from app.modules.quotation.infrastructure.quotation_repository import QuotationRepository
from app.modules.quotation.presentation.schemas import (
    PaginatedQuotationsResponse,
    QuotationCreateRequest,
    QuotationResponse,
    QuotationUpdateRequest,
)

router = APIRouter(prefix="/quotation", tags=["Quotation"])


async def get_quotation_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> QuotationUseCase:
    return QuotationUseCase(quotation_repository=QuotationRepository(session))


def _quotation_to_response(q: Quotation) -> QuotationResponse:
    return QuotationResponse(
        id=str(q.id),
        quotation_no=q.quotation_no,
        job_id=str(q.job_id) if q.job_id else None,
        customer_id=str(q.customer_id) if q.customer_id else None,
        quotation_date=q.quotation_date.isoformat() if q.quotation_date else None,
        expiry_date=q.expiry_date.isoformat() if q.expiry_date else None,
        status=q.status,
        subtotal=q.subtotal,
        tax_rate=q.tax_rate,
        tax_amount=q.tax_amount,
        discount_type=q.discount_type,
        discount_value=q.discount_value,
        total=q.total,
        amount_in_words_th=q.amount_in_words_th,
        amount_in_words_en=q.amount_in_words_en,
        currency=q.currency,
        exchange_rate=q.exchange_rate,
        notes=q.notes,
        terms_and_conditions=q.terms_and_conditions,
        approved_by=str(q.approved_by) if q.approved_by else None,
        approved_at=q.approved_at.isoformat() if q.approved_at else None,
        rejected_reason=q.rejected_reason,
        converted_to_po=q.converted_to_po,
        created_at=q.created_at.isoformat() if q.created_at else "",
        updated_at=q.updated_at.isoformat() if q.updated_at else "",
    )


@router.get("/")
async def get_quotations(
    page: int = 1,
    per_page: int = 10,
    use_case: QuotationUseCase = Depends(get_quotation_use_case),
) -> PaginatedQuotationsResponse:
    per_page = min(per_page, 100)
    quotations, total = await use_case.get_quotations(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedQuotationsResponse(
        items=[_quotation_to_response(q) for q in quotations],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/")
async def create_quotation(
    payload: QuotationCreateRequest,
    use_case: QuotationUseCase = Depends(get_quotation_use_case),
) -> QuotationResponse:
    from datetime import date
    from uuid import UUID

    quotation = Quotation(
        quotation_no=payload.quotation_no,
        job_id=UUID(payload.job_id) if payload.job_id else None,
        customer_id=UUID(payload.customer_id) if payload.customer_id else None,
        quotation_date=date.fromisoformat(payload.quotation_date)
        if payload.quotation_date else None,
        expiry_date=date.fromisoformat(payload.expiry_date) if payload.expiry_date else None,
        subtotal=payload.subtotal,
        tax_rate=payload.tax_rate,
        tax_amount=payload.tax_amount,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        total=payload.total,
        currency=payload.currency,
        notes=payload.notes,
        terms_and_conditions=payload.terms_and_conditions,
    )
    result = await use_case.create_quotation(quotation)
    return _quotation_to_response(result)


@router.get("/{quotation_id}")
async def get_quotation(
    quotation_id: str,
    use_case: QuotationUseCase = Depends(get_quotation_use_case),
) -> QuotationResponse:
    from uuid import UUID

    quotation = await use_case.get_quotation(UUID(quotation_id))
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return _quotation_to_response(quotation)


@router.put("/{quotation_id}")
async def update_quotation(
    quotation_id: str,
    payload: QuotationUpdateRequest,
    use_case: QuotationUseCase = Depends(get_quotation_use_case),
) -> QuotationResponse:
    from datetime import date, datetime
    from uuid import UUID

    values = payload.model_dump(exclude_none=True)
    if "job_id" in values and values["job_id"] is not None:
        values["job_id"] = UUID(values["job_id"])
    if "customer_id" in values and values["customer_id"] is not None:
        values["customer_id"] = UUID(values["customer_id"])
    if "approved_by" in values and values["approved_by"] is not None:
        values["approved_by"] = UUID(values["approved_by"])
    if "quotation_date" in values and values["quotation_date"] is not None:
        values["quotation_date"] = date.fromisoformat(values["quotation_date"])
    if "expiry_date" in values and values["expiry_date"] is not None:
        values["expiry_date"] = date.fromisoformat(values["expiry_date"])
    if "approved_at" in values and values["approved_at"] is not None:
        values["approved_at"] = datetime.fromisoformat(values["approved_at"])
    quotation = await use_case.update_quotation(UUID(quotation_id), values)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return _quotation_to_response(quotation)


@router.delete("/{quotation_id}")
async def delete_quotation(
    quotation_id: str,
    use_case: QuotationUseCase = Depends(get_quotation_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_quotation(UUID(quotation_id))
    if not success:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"success": True}
