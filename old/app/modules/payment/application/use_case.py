from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.modules.payment.domain.entities.payment import Payment
from app.modules.payment.domain.entities.payment_history import PaymentHistory
from app.modules.payment.domain.entities.receipt import Receipt
from app.modules.payment.infrastructure.payment_history_repository import (
    PaymentHistoryRepository,
)
from app.modules.payment.infrastructure.payment_repository import PaymentRepository
from app.modules.payment.infrastructure.receipt_repository import ReceiptRepository


class PaymentUseCase:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        receipt_repository: ReceiptRepository,
        payment_history_repository: PaymentHistoryRepository,
    ) -> None:
        self._payment_repo = payment_repository
        self._receipt_repo = receipt_repository
        self._history_repo = payment_history_repository

    async def record_payment(self, values: dict) -> tuple[Payment, Receipt]:
        now = datetime.now(UTC)
        payment = Payment(
            payment_no=values.get("payment_no", ""),
            invoice_id=values.get("invoice_id"),
            job_id=values.get("job_id"),
            customer_id=values.get("customer_id"),
            payment_date=values.get("payment_date", now),
            payment_method_id=values.get("payment_method_id"),
            amount=values.get("amount", 0),
            amount_received=values.get("amount_received", 0),
            change_amount=values.get("change_amount", 0),
            currency=values.get("currency", "THB"),
            exchange_rate=values.get("exchange_rate", 1),
            status=values.get("status", "completed"),
            reference_number=values.get("reference_number"),
            bank_name=values.get("bank_name"),
            cheque_number=values.get("cheque_number"),
            cheque_bank=values.get("cheque_bank"),
            cheque_date=values.get("cheque_date"),
            notes=values.get("notes"),
            received_by=values.get("received_by"),
        )
        payment = await self._payment_repo.create(payment)

        receipt = Receipt(
            receipt_no=values.get("receipt_no", ""),
            payment_id=payment.id,
            invoice_id=payment.invoice_id,
            customer_id=payment.customer_id,
            receipt_date=now,
            receipt_type=values.get("receipt_type", "payment"),
            amount=payment.amount,
            amount_in_words_th=values.get("amount_in_words_th"),
            amount_in_words_en=values.get("amount_in_words_en"),
            currency=payment.currency,
            status="active",
            notes=payment.notes,
            issued_by=payment.received_by,
        )
        receipt = await self._receipt_repo.create(receipt)

        history = PaymentHistory(
            payment_id=payment.id,
            from_status="pending",
            to_status=payment.status,
            changed_by=payment.received_by,
            changed_at=now,
            reason="Payment recorded",
        )
        await self._history_repo.create(history)

        return payment, receipt

    async def search_payments(
        self,
        filters: dict,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Payment], int]:
        return await self._payment_repo.search_payments(
            customer_id=filters.get("customer_id"),
            invoice_id=filters.get("invoice_id"),
            status=filters.get("status"),
            payment_method_id=filters.get("payment_method_id"),
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
            page=page,
            page_size=page_size,
        )

    async def get_payment(self, payment_id: UUID) -> Payment | None:
        return await self._payment_repo.find_by_id(payment_id)

    async def get_payments_by_invoice_id(self, invoice_id: UUID) -> list[Payment]:
        return await self._payment_repo.find_by_invoice_id(invoice_id)

    async def get_outstanding(
        self, customer_id: UUID
    ) -> list[dict]:
        payments, _ = await self._payment_repo.find_by_customer_id(
            customer_id, page=1, page_size=1000
        )
        invoice_map: dict[UUID, dict] = {}
        for p in payments:
            if p.invoice_id is None:
                continue
            key = p.invoice_id
            if key not in invoice_map:
                invoice_map[key] = {
                    "invoice_id": str(key),
                    "amount_paid": 0.0,
                    "refunded_amount": 0.0,
                    "last_payment_date": p.payment_date,
                }
            entry = invoice_map[key]
            if p.status in ("completed", "approved"):
                entry["amount_paid"] += p.amount
            entry["refunded_amount"] += p.refunded_amount
            if p.payment_date and (
                entry["last_payment_date"] is None
                or p.payment_date > entry["last_payment_date"]
            ):
                entry["last_payment_date"] = p.payment_date

        result = []
        for _inv_id, info in invoice_map.items():
            outstanding = info["amount_paid"] - info["refunded_amount"]
            result.append({
                "invoice_id": info["invoice_id"],
                "invoice_total": info["amount_paid"],
                "amount_paid": info["amount_paid"],
                "outstanding_amount": outstanding,
                "last_payment_date": (
                    info["last_payment_date"].isoformat()
                    if info["last_payment_date"]
                    else None
                ),
                "status": "outstanding" if outstanding > 0 else "settled",
            })
        return result

    async def get_payment_history(
        self, customer_id: UUID
    ) -> list[dict]:
        payments, _ = await self._payment_repo.find_by_customer_id(
            customer_id, page=1, page_size=1000
        )
        result = []
        for p in payments:
            histories = await self._history_repo.find_by_payment_id(p.id)
            result.append({
                "payment": p,
                "histories": histories,
            })
        return result

    async def process_refund(
        self, payment_id: UUID, amount: float, reason: str
    ) -> Payment | None:
        payment = await self._payment_repo.find_by_id(payment_id)
        if not payment:
            return None
        old_status = payment.status
        payment.refunded_amount += amount
        payment.refunded_at = datetime.now(UTC)
        if payment.refunded_amount >= payment.amount:
            payment.status = "refunded"
        else:
            payment.status = "partial_refund"
        await self._payment_repo.update(payment)

        history = PaymentHistory(
            payment_id=payment.id,
            from_status=old_status,
            to_status=payment.status,
            changed_at=datetime.now(UTC),
            reason=reason or f"Refund of {amount}",
        )
        await self._history_repo.create(history)
        return payment

    async def cancel_payment(self, payment_id: UUID) -> Payment | None:
        payment = await self._payment_repo.find_by_id(payment_id)
        if not payment:
            return None
        old_status = payment.status
        payment.status = "cancelled"
        await self._payment_repo.update(payment)

        history = PaymentHistory(
            payment_id=payment.id,
            from_status=old_status,
            to_status="cancelled",
            changed_at=datetime.now(UTC),
            reason="Payment cancelled",
        )
        await self._history_repo.create(history)
        return payment

    async def get_receipt(self, receipt_id: UUID) -> Receipt | None:
        return await self._receipt_repo.find_by_id(receipt_id)

    async def get_receipt_by_payment_id(
        self, payment_id: UUID
    ) -> Receipt | None:
        return await self._receipt_repo.find_by_payment_id(payment_id)

    async def cancel_receipt(self, receipt_id: UUID) -> Receipt | None:
        receipt = await self._receipt_repo.find_by_id(receipt_id)
        if not receipt:
            return None
        receipt.status = "cancelled"
        return await self._receipt_repo.update(receipt)
