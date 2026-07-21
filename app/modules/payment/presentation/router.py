from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.payment.application.use_case import PaymentUseCase
from app.modules.payment.domain.entities.payment import Payment
from app.modules.payment.domain.entities.payment_history import PaymentHistory
from app.modules.payment.domain.entities.receipt import Receipt
from app.modules.payment.infrastructure.payment_history_repository import (
    PaymentHistoryRepository,
)
from app.modules.payment.infrastructure.payment_repository import PaymentRepository
from app.modules.payment.infrastructure.receipt_repository import ReceiptRepository
from app.modules.payment.presentation.schemas import (
    OutstandingBalanceResponse,
    PaginatedPaymentsResponse,
    PaymentHistoryResponse,
    PaymentRecordRequest,
    PaymentResponse,
    PaymentSearchRequest,
    ReceiptResponse,
    RefundRequest,
)

router = APIRouter(prefix="/payment", tags=["Payment"])


async def get_payment_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> PaymentUseCase:
    return PaymentUseCase(
        payment_repository=PaymentRepository(session),
        receipt_repository=ReceiptRepository(session),
        payment_history_repository=PaymentHistoryRepository(session),
    )


def _payment_to_response(p: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=str(p.id),
        payment_no=p.payment_no,
        invoice_id=str(p.invoice_id) if p.invoice_id else None,
        job_id=str(p.job_id) if p.job_id else None,
        customer_id=str(p.customer_id) if p.customer_id else None,
        payment_date=p.payment_date.isoformat() if p.payment_date else None,
        payment_method_id=str(p.payment_method_id) if p.payment_method_id else None,
        amount=p.amount,
        amount_received=p.amount_received,
        change_amount=p.change_amount,
        currency=p.currency,
        exchange_rate=p.exchange_rate,
        status=p.status,
        reference_number=p.reference_number,
        bank_name=p.bank_name,
        cheque_number=p.cheque_number,
        cheque_bank=p.cheque_bank,
        cheque_date=p.cheque_date.isoformat() if p.cheque_date else None,
        notes=p.notes,
        received_by=str(p.received_by) if p.received_by else None,
        approved_by=str(p.approved_by) if p.approved_by else None,
        approved_at=p.approved_at.isoformat() if p.approved_at else None,
        refunded_amount=p.refunded_amount,
        refunded_at=p.refunded_at.isoformat() if p.refunded_at else None,
        created_at=p.created_at.isoformat() if p.created_at else "",
        updated_at=p.updated_at.isoformat() if p.updated_at else "",
    )


def _receipt_to_response(r: Receipt) -> ReceiptResponse:
    return ReceiptResponse(
        id=str(r.id),
        receipt_no=r.receipt_no,
        payment_id=str(r.payment_id),
        invoice_id=str(r.invoice_id) if r.invoice_id else None,
        customer_id=str(r.customer_id) if r.customer_id else None,
        receipt_date=r.receipt_date.isoformat() if r.receipt_date else None,
        receipt_type=r.receipt_type,
        amount=r.amount,
        amount_in_words_th=r.amount_in_words_th,
        amount_in_words_en=r.amount_in_words_en,
        currency=r.currency,
        status=r.status,
        notes=r.notes,
        issued_by=str(r.issued_by) if r.issued_by else None,
        created_at=r.created_at.isoformat() if r.created_at else "",
        updated_at=r.updated_at.isoformat() if r.updated_at else "",
    )


def _history_to_response(h: PaymentHistory) -> PaymentHistoryResponse:
    return PaymentHistoryResponse(
        id=str(h.id),
        payment_id=str(h.payment_id),
        from_status=h.from_status,
        to_status=h.to_status,
        changed_by=str(h.changed_by) if h.changed_by else None,
        changed_at=h.changed_at.isoformat() if h.changed_at else None,
        reason=h.reason,
    )


@router.post("/payments/")
async def record_payment(
    payload: PaymentRecordRequest,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> PaymentResponse:
    now = datetime.now(UTC)
    values = payload.model_dump()
    values["payment_no"] = f"PAY-{now.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
    values["receipt_no"] = f"RCT-{now.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
    values["payment_date"] = now
    if values.get("amount_received") is None:
        values["amount_received"] = values.get("amount", 0)
    values["change_amount"] = max(
        0, values.get("amount_received", 0) - values.get("amount", 0)
    )
    values["received_by"] = None
    payment, receipt = await use_case.record_payment(values)
    return _payment_to_response(payment)


@router.post("/payments/search")
async def search_payments(
    payload: PaymentSearchRequest,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> PaginatedPaymentsResponse:
    per_page = min(payload.per_page, 100)
    filters = payload.model_dump(exclude={"page", "per_page"})
    payments, total = await use_case.search_payments(
        filters=filters,
        page=payload.page,
        page_size=per_page,
    )
    total_pages = (total + per_page - 1) // per_page
    return PaginatedPaymentsResponse(
        items=[_payment_to_response(p) for p in payments],
        total=total,
        page=payload.page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/payments/outstanding/{customer_id}")
async def get_outstanding(
    customer_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> list[OutstandingBalanceResponse]:
    from uuid import UUID

    results = await use_case.get_outstanding(UUID(customer_id))
    return [OutstandingBalanceResponse(**r) for r in results]


@router.get("/payments/history/{customer_id}")
async def get_payment_history(
    customer_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> list[dict]:
    from uuid import UUID

    results = await use_case.get_payment_history(UUID(customer_id))
    output = []
    for entry in results:
        output.append({
            "payment": _payment_to_response(entry["payment"]),
            "histories": [_history_to_response(h) for h in entry["histories"]],
        })
    return output


@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> PaymentResponse:
    from uuid import UUID

    payment = await use_case.get_payment(UUID(payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return _payment_to_response(payment)


@router.post("/payments/{payment_id}/refund")
async def process_refund(
    payment_id: str,
    payload: RefundRequest,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> PaymentResponse:
    from uuid import UUID

    payment = await use_case.process_refund(
        UUID(payment_id), payload.amount, payload.reason
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return _payment_to_response(payment)


@router.put("/payments/{payment_id}/cancel")
async def cancel_payment(
    payment_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> PaymentResponse:
    from uuid import UUID

    payment = await use_case.cancel_payment(UUID(payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return _payment_to_response(payment)


@router.get("/payments/invoice/{invoice_id}")
async def get_payments_by_invoice(
    invoice_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> list[PaymentResponse]:
    from uuid import UUID

    payments = await use_case.get_payments_by_invoice_id(UUID(invoice_id))
    return [_payment_to_response(p) for p in payments]


@router.get("/receipts/{receipt_id}")
async def get_receipt(
    receipt_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> ReceiptResponse:
    from uuid import UUID

    receipt = await use_case.get_receipt(UUID(receipt_id))
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return _receipt_to_response(receipt)


@router.get("/receipts/payment/{payment_id}")
async def get_receipt_by_payment(
    payment_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> ReceiptResponse:
    from uuid import UUID

    receipt = await use_case.get_receipt_by_payment_id(UUID(payment_id))
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return _receipt_to_response(receipt)


@router.put("/receipts/{receipt_id}/cancel")
async def cancel_receipt(
    receipt_id: str,
    use_case: PaymentUseCase = Depends(get_payment_use_case),
) -> ReceiptResponse:
    from uuid import UUID

    receipt = await use_case.cancel_receipt(UUID(receipt_id))
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return _receipt_to_response(receipt)
