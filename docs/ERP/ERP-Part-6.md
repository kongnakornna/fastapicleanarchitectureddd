# 📕 PART 6 — Money Path Completion

> **Layer 2: Money Path (ต่อ)** — 2 modules ที่ปิดวงจรเงิน
> `payment` · `accounting_gateway`

---

## 6.0 ภาพรวม Money Path Completion

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│              LAYER 2: MONEY PATH — COMPLETION                                 │
│                                                                              │
│   ┌──────────────┐                                                           │
│   │   invoice    │  ← Part 5                                                 │
│   └──────┬───────┘                                                           │
│          │ InvoiceIssued                                                    │
│          ▼                                                                   │
│   ┌──────────────┐      ┌────────────────────┐                             │
│   │    ledger    │─────►│  accounting_       │                             │
│   │  (Part 5)    │      │  gateway           │                             │
│   └──────┬───────┘      │  (sync cloud)      │                             │
│          │              └─────────┬──────────┘                             │
│          │                        │                                        │
│          │                        │ Outbox → Worker                        │
│          │                        ▼                                        │
│          │              ┌────────────────────┐                             │
│          │              │ Thai Cloud         │                             │
│          │              │ Accounting API     │                             │
│          │              └────────────────────┘                             │
│          │                                                                  │
│          │ PaymentReceived                                                  │
│          ▼                                                                  │
│   ┌──────────────┐      ┌────────────────────┐                             │
│   │   payment    │─────►│   ledger           │  ← post AR/ Cash            │
│   │              │      │   (reversal/adj)   │                             │
│   └──────┬───────┘      └────────────────────┘                             │
│          │                                                                  │
│          │ InvoicePaid / PartiallyPaid                                     │
│          ▼                                                                  │
│   ┌──────────────┐                                                           │
│   │   invoice    │  ← mark paid                                             │
│   └──────────────┘                                                           │
│                                                                              │
│   Money Path ปิดวงจร:                                                       │
│   Order → Invoice → Ledger → Payment → Ledger(adj) → Cloud sync            │
│   + Reconciliation ตรวจทุกจุด                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Payment Path (ละเอียด):**

```text
Customer ─── โอน/จ่าย ───► Payment ─── allocation ───► Invoice
                                │
                                │ PaymentReceived
                                ▼
                         ┌──────────────┐
                         │   Ledger     │
                         │   Dr. เงินสด/ธนาคาร
                         │     Cr. ลูกหนี้การค้า
                         └──────────────┘
                                │
                                │ WHT (ถ้ามี)
                                ▼
                         ┌──────────────┐
                         │  WHT cert    │
                         │  Dr. ภาษีหัก
                         │  Cr. ลูกหนี้
                         └──────────────┘
                                │
                                │ LedgerPosted
                                ▼
                         ┌──────────────┐
                         │ Cloud sync   │
                         │ (AR payment) │
                         └──────────────┘
```

---

# 🧩 Module 6.1 — `payment`

## 6.1.1 Purpose & Scope

**Purpose:** รับชำระเงินจากลูกค้า รองรับ partial payment, multi-invoice allocation, refund, WHT และ post journal อัตโนมัติ

**Scope:**
- ✅ Payment (รับชำระ) + PaymentAllocation
- ✅ หลายวิธี: cash, transfer, cheque, credit card, e-wallet
- ✅ Partial payment + multi-invoice allocation
- ✅ WHT deduction
- ✅ Refund (คืนเงิน)
- ✅ Payment receipt (ใบเสร็จรับเงิน)
- ✅ Post ledger อัตโนมัติ
- ✅ Bank reconciliation
- ❌ ไม่ sync cloud (accounting_gateway ทำ)
- ❌ ไม่เก็บ customer (customer module)

## 6.1.2 Domain Model

```python
# app/modules/payment/domain/value_objects.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
import re


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    E_WALLET = "e_wallet"           # พร้อมเพย์, TrueMoney, ฯลฯ
    QR_PAYMENT = "qr_payment"       # PromptPay QR
    OFFSET = "offset"               # หักกลบ (credit note)
    OTHER = "other"


class PaymentStatus(str, Enum):
    DRAFT = "draft"
    RECEIVED = "received"           # รับแล้ว รอ allocate
    ALLOCATED = "allocated"         # allocate ครบ
    PARTIALLY_ALLOCATED = "partially_allocated"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentDirection(str, Enum):
    INBOUND = "inbound"             # รับชำระ (จากลูกค้า)
    OUTBOUND = "outbound"           # จ่ายชำระ (ให้ supplier)


@dataclass(frozen=True, slots=True)
class PaymentNumber:
    """
    เลขที่ใบรับชำระ
    Format: RCP-{YYYY}-{NNNNN}  (receipt)
    หรือ PMT-{YYYY}-{NNNNN}     (payment voucher)
    """
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^(RCP|PMT)-\d{4}-\d{5,7}$", self.value):
            raise ValueError(f"PaymentNumber ไม่ถูกต้อง: {self.value}")

    @classmethod
    def build(cls, prefix: str, year: int, seq: int) -> "PaymentNumber":
        return cls(f"{prefix}-{year}-{seq:05d}")


@dataclass(frozen=True, slots=True)
class BankAccountRef:
    """อ้างอิงบัญชีธนาคาร"""
    bank_code: str                  # "KBANK", "SCB", "BBL", ...
    account_number: str
    account_name: str
    branch: str | None = None


@dataclass(frozen=True, slots=True)
class ChequeInfo:
    """ข้อมูลเช็ค"""
    cheque_number: str
    cheque_date: date
    bank_code: str
    branch: str | None
    amount: Decimal


@dataclass(frozen=True, slots=True)
class WhtDeduction:
    """ภาษีหัก ณ ที่จ่ายที่ลูกค้าหักไว้"""
    income_type: str                # "service", "rental", ...
    rate: Decimal                   # 0.03 = 3%
    amount: Decimal
    certificate_number: str | None  # เลขหนังสือรับรอง


@dataclass(frozen=True, slots=True)
class CustomerSnapshot:
    """Snapshot ลูกค้า ณ เวลารับชำระ"""
    customer_id: str
    code: str
    name: str
    tax_id: str | None
    address: str
    branch_code: str | None
```

```python
# app/modules/payment/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.money.domain.value_objects import Money, Currency
from app.modules.payment.domain.value_objects import (
    PaymentNumber, PaymentMethod, PaymentStatus, PaymentDirection,
    BankAccountRef, ChequeInfo, WhtDeduction, CustomerSnapshot,
)


@dataclass
class PaymentAllocation:
    """
    การจัดสรรเงินไปยัง invoice — Entity

    Invariants:
    - allocated_amount > 0
    - allocated_amount ≤ invoice remaining
    - 1 payment → N allocations
    - 1 invoice → N allocations (partial payments)
    """
    id: UUID
    payment_id: UUID
    invoice_id: UUID
    invoice_number: str
    invoice_grand_total: Money
    invoice_paid_before: Money       # ชำระไปแล้วก่อน allocation นี้
    allocated_amount: Money
    wht_amount: Money                # WHT ที่หักจาก invoice นี้
    net_amount: Money                # allocated + wht
    created_at: datetime

    @property
    def invoice_remaining_after(self) -> Money:
        return self.invoice_grand_total - self.invoice_paid_before - self.allocated_amount


@dataclass
class Payment:
    """
    Payment — Aggregate Root

    Invariants:
    1.  total_amount = Σ(allocations.allocated_amount) + unallocated
    2.  total_amount = net_received + wht_amount
    3.  RECEIVED → allocate → ALLOCATED/PARTIALLY_ALLOCATED
    4.  ห้าม allocate เกิน invoice remaining
    5.  REFUND → ต้องมี reversal ledger
    6.  RECEIVED แล้วห้ามแก้ allocations โดยไม่ผ่าน use case
    """
    id: UUID
    company_id: UUID
    branch_id: UUID | None
    payment_number: PaymentNumber
    direction: PaymentDirection
    status: PaymentStatus

    # Customer / Supplier
    customer: CustomerSnapshot | None
    supplier_id: UUID | None

    # Dates
    payment_date: date
    received_at: datetime

    # Method
    method: PaymentMethod
    bank_account: BankAccountRef | None
    cheque: ChequeInfo | None
    reference: str | None            # เลขอ้างอิงการโอน
    attachment_url: str | None       # หลักฐานการโอน

    # Amounts
    currency: str
    total_amount: Money              # ยอดรับรวม
    wht_amount: Money                # WHT ที่ถูกหัก
    net_received: Money              # ยอดที่เข้าบัญชีจริง = total − wht
    allocated_amount: Money          # Σ allocations
    unallocated_amount: Money        # ส่วนที่ยังไม่ allocate (advance)

    # WHT details
    wht: WhtDeduction | None

    # Meta
    note: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    cancel_reason: str | None

    _allocations: list[PaymentAllocation] = field(default_factory=list, repr=False)

    # ---------- Factory ----------

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        direction: PaymentDirection,
        customer: CustomerSnapshot | None,
        supplier_id: UUID | None,
        payment_date: date,
        method: PaymentMethod,
        total_amount: Money,
        currency: str = "THB",
        bank_account: BankAccountRef | None = None,
        cheque: ChequeInfo | None = None,
        wht: WhtDeduction | None = None,
        reference: str | None = None,
        attachment_url: str | None = None,
        note: str | None = None,
        created_by: UUID,
    ) -> "Payment":
        if direction == PaymentDirection.INBOUND and customer is None:
            raise ValueError("INBOUND ต้องมี customer")
        if direction == PaymentDirection.OUTBOUND and supplier_id is None:
            raise ValueError("OUTBOUND ต้องมี supplier")

        if method == PaymentMethod.CHEQUE and cheque is None:
            raise ValueError("CHEQUE ต้องมี cheque info")
        if method == PaymentMethod.BANK_TRANSFER and bank_account is None:
            raise ValueError("BANK_TRANSFER ต้องมี bank_account")

        wht_amount = Money(Decimal(str(wht.amount))) if wht else Money.zero()
        net_received = total_amount - wht_amount

        return cls(
            id=uuid4(),
            company_id=company_id,
            branch_id=branch_id,
            payment_number=None,  # type: ignore  # ออกตอน receive()
            direction=direction,
            status=PaymentStatus.DRAFT,
            customer=customer,
            supplier_id=supplier_id,
            payment_date=payment_date,
            received_at=datetime.utcnow(),
            method=method,
            bank_account=bank_account,
            cheque=cheque,
            reference=reference,
            attachment_url=attachment_url,
            currency=currency,
            total_amount=total_amount,
            wht_amount=wht_amount,
            net_received=net_received,
            allocated_amount=Money.zero(),
            unallocated_amount=total_amount,
            wht=wht,
            note=note,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            cancelled_at=None,
            cancel_reason=None,
            _allocations=[],
        )

    # ---------- Allocation ----------

    def allocate_to_invoice(
        self,
        *,
        invoice_id: UUID,
        invoice_number: str,
        invoice_grand_total: Money,
        invoice_paid_before: Money,
        allocate_amount: Money,
        wht_from_invoice: Money | None = None,
    ) -> PaymentAllocation:
        """
        Allocate เงินไปยัง invoice

        Invariants:
        - allocate_amount > 0
        - allocate_amount ≤ invoice remaining
        - allocate_amount + wht ≤ available unallocated
        """
        if self.status == PaymentStatus.CANCELLED:
            raise ValueError("payment ถูกยกเลิก — allocate ไม่ได้")
        if self.status == PaymentStatus.REFUNDED:
            raise ValueError("payment ถูก refund — allocate ไม่ได้")

        if allocate_amount.is_zero() or allocate_amount.is_negative():
            raise ValueError("allocate_amount ต้อง > 0")

        invoice_remaining = invoice_grand_total - invoice_paid_before
        if allocate_amount > invoice_remaining:
            raise ValueError(
                f"allocate เกินยอดค้าง: {allocate_amount} > {invoice_remaining}"
            )

        wht_amt = wht_from_invoice or Money.zero()
        net = allocate_amount + wht_amt

        # ตรวจ unallocated
        available = self.unallocated_amount + self.wht_amount
        if net > available:
            raise ValueError(
                f"allocate เกินยอด: {net} > {available}"
            )

        allocation = PaymentAllocation(
            id=uuid4(),
            payment_id=self.id,
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            invoice_grand_total=invoice_grand_total,
            invoice_paid_before=invoice_paid_before,
            allocated_amount=allocate_amount,
            wht_amount=wht_amt,
            net_amount=net,
            created_at=datetime.utcnow(),
        )
        self._allocations.append(allocation)

        self.allocated_amount = self.allocated_amount + allocate_amount
        self.unallocated_amount = self.total_amount - self.allocated_amount - self.wht_amount
        if self.unallocated_amount.is_negative():
            self.unallocated_amount = Money.zero()

        self._refresh_status()
        self.updated_at = datetime.utcnow()
        return allocation

    def unallocate(self, allocation_id: UUID) -> None:
        """ยกเลิก allocation (ก่อน receive finalize)"""
        if self.status in (PaymentStatus.RECEIVED, PaymentStatus.ALLOCATED):
            raise ValueError("ยกเลิก allocation ไม่ได้ — ต้อง refund")

        target = next((a for a in self._allocations if a.id == allocation_id), None)
        if not target:
            raise ValueError("ไม่พบ allocation")

        self._allocations.remove(target)
        self.allocated_amount = self.allocated_amount - target.allocated_amount
        self.unallocated_amount = self.unallocated_amount + target.allocated_amount
        self._refresh_status()
        self.updated_at = datetime.utcnow()

    def receive(self, payment_number: PaymentNumber) -> None:
        """
        ยืนยันรับชำระ — DRAFT → RECEIVED
        """
        if self.status != PaymentStatus.DRAFT:
            raise ValueError(f"receive ไม่ได้ — status = {self.status.value}")

        self.payment_number = payment_number
        self.status = PaymentStatus.RECEIVED
        self.received_at = datetime.utcnow()
        self.updated_at = self.received_at
        self._refresh_status()

    def refund(self, reason: str, amount: Money | None = None) -> None:
        """
        คืนเงิน — ต้องสร้าง reversal ledger

        ถ้า amount = None → refund ทั้งจำนวน
        """
        if self.status not in (
            PaymentStatus.RECEIVED,
            PaymentStatus.ALLOCATED,
            PaymentStatus.PARTIALLY_ALLOCATED,
        ):
            raise ValueError(f"refund ไม่ได้ — status = {self.status.value}")

        refund_amount = amount or self.total_amount
        if refund_amount > self.total_amount:
            raise ValueError("refund เกินยอดรับ")

        self.status = PaymentStatus.REFUNDED
        self.cancel_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.updated_at = self.cancelled_at

    def cancel(self, reason: str) -> None:
        """ยกเลิกก่อน receive"""
        if self.status != PaymentStatus.DRAFT:
            raise ValueError("cancel ได้เฉพาะ DRAFT — ถ้า receive แล้วใช้ refund")
        self.status = PaymentStatus.CANCELLED
        self.cancel_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.updated_at = self.cancelled_at

    # ---------- Private ----------

    def _refresh_status(self) -> None:
        if self.status in (PaymentStatus.CANCELLED, PaymentStatus.REFUNDED):
            return
        if self.unallocated_amount.is_zero() and self.allocated_amount.is_positive():
            self.status = PaymentStatus.ALLOCATED
        elif self.allocated_amount.is_positive():
            self.status = PaymentStatus.PARTIALLY_ALLOCATED
        elif self.status != PaymentStatus.DRAFT:
            self.status = PaymentStatus.RECEIVED

    # ---------- Read-only ----------

    @property
    def allocations(self) -> list[PaymentAllocation]:
        return list(self._allocations)

    def verify_totals(self) -> None:
        """
        🛡️ Read-back verify
        total = Σ allocated + wht + unallocated
        """
        sum_alloc = sum(
            (a.allocated_amount for a in self._allocations), Money.zero()
        )
        if sum_alloc != self.allocated_amount:
            raise ValueError(
                f"allocated mismatch: {self.allocated_amount} ≠ {sum_alloc}"
            )
        expected_unalloc = self.total_amount - self.allocated_amount - self.wht_amount
        if expected_unalloc.is_negative():
            expected_unalloc = Money.zero()
        if self.unallocated_amount != expected_unalloc:
            raise ValueError(
                f"unallocated mismatch: {self.unallocated_amount} ≠ {expected_unalloc}"
            )
```

## 6.1.3 Domain Events

```python
# app/modules/payment/domain/events.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Any

from app.core.events.domain.entities import DomainEvent


@dataclass(frozen=True, slots=True)
class PaymentReceived(DomainEvent):
    """
    รับชำระสำเร็จ — trigger ledger
    """
    @classmethod
    def create(
        cls, *, payment_id: UUID, company_id: UUID,
        payment_number: str, customer_id: str | None,
        supplier_id: str | None, amount: str, currency: str,
        method: str, payment_date: str,
        wht_amount: str = "0.00",
        bank_account_code: str | None = None,
        allocations: list[dict[str, Any]] | None = None,
        actor_id: UUID | None = None,
    ) -> "PaymentReceived":
        return cls(
            event_id=uuid4(),
            event_type="payment.received",
            aggregate_type="payment",
            aggregate_id=payment_id,
            company_id=company_id,
            payload={
                "payment_number": payment_number,
                "customer_id": customer_id,
                "supplier_id": supplier_id,
                "amount": amount,
                "currency": currency,
                "method": method,
                "payment_date": payment_date,
                "wht_amount": wht_amount,
                "bank_account_code": bank_account_code,
                "allocations": allocations or [],
            },
            occurred_at=datetime.utcnow(),
            actor_id=actor_id,
            correlation_id=None,
            causation_id=None,
        )


@dataclass(frozen=True, slots=True)
class PaymentRefunded(DomainEvent):
    """คืนเงิน — trigger reversal ledger"""
    ...


@dataclass(frozen=True, slots=True)
class PaymentAllocated(DomainEvent):
    """allocate ไป invoice — trigger invoice.mark_paid"""
    ...


@dataclass(frozen=True, slots=True)
class InvoiceFullyPaid(DomainEvent):
    """invoice ชำระครบ — trigger loyalty, notification"""
    ...
```

## 6.1.4 Application — Interfaces

```python
# app/modules/payment/application/interfaces.py

from typing import Protocol
from uuid import UUID
from datetime import date

from app.modules.payment.domain.entities import Payment
from app.modules.payment.domain.value_objects import PaymentNumber


class IPaymentRepository(Protocol):
    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...
    async def get_by_number(
        self, company_id: UUID, number: str,
    ) -> Payment | None: ...
    async def exists_by_number(
        self, company_id: UUID, number: str,
    ) -> bool: ...
    async def list_by_company(
        self, company_id: UUID, *,
        customer_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        status: str | None = None,
        limit: int = 100, offset: int = 0,
    ) -> list[Payment]: ...
    async def list_unallocated(self, company_id: UUID) -> list[Payment]: ...
    async def save(self, payment: Payment) -> None: ...
    async def update(self, payment: Payment) -> None: ...
    async def get_with_allocations(self, payment_id: UUID) -> Payment | None: ...


class IPaymentNumberSequence(Protocol):
    async def next_number(
        self, *, company_id: UUID, prefix: str, year: int,
    ) -> PaymentNumber: ...


class IInvoiceForPaymentPort(Protocol):
    """
    Port — เพื่อให้ payment module ไม่ผูกกับ invoice module โดยตรง
    """
    async def get_invoice_summary(
        self, invoice_id: UUID,
    ) -> dict | None: ...

    async def get_customer_outstanding(
        self, company_id: UUID, customer_id: UUID,
    ) -> list[dict]: ...

    async def mark_invoice_paid(
        self, invoice_id: UUID, paid_amount: str,
    ) -> None: ...
```

## 6.1.5 Application — Use Cases

```python
# app/modules/payment/application/use_cases.py

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.core.money.domain.value_objects import Money
from app.modules.payment.domain.entities import Payment
from app.modules.payment.domain.value_objects import (
    PaymentMethod, PaymentDirection, PaymentStatus,
    BankAccountRef, ChequeInfo, WhtDeduction, CustomerSnapshot,
)
from app.modules.payment.domain.events import PaymentReceived, PaymentRefunded
from app.modules.payment.application.interfaces import (
    IPaymentRepository, IPaymentNumberSequence, IInvoiceForPaymentPort,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.core.tenant_context.domain.context import get_company_id


# ============================================================
# 1. Create Payment (draft)
# ============================================================

@dataclass
class CreatePaymentCommand:
    customer: CustomerSnapshot | None
    supplier_id: UUID | None
    payment_date: date
    method: PaymentMethod
    total_amount: Decimal
    direction: PaymentDirection = PaymentDirection.INBOUND
    currency: str = "THB"
    bank_account: BankAccountRef | None = None
    cheque: ChequeInfo | None = None
    wht: WhtDeduction | None = None
    reference: str | None = None
    attachment_url: str | None = None
    note: str | None = None
    branch_id: UUID | None = None
    actor_id: UUID = None  # type: ignore


class CreatePaymentUseCase:
    def __init__(self, payments: IPaymentRepository, uow):
        self.payments = payments
        self.uow = uow

    async def execute(self, cmd: CreatePaymentCommand) -> Payment:
        company_id = get_company_id()
        payment = Payment.create(
            company_id=company_id,
            branch_id=cmd.branch_id,
            direction=cmd.direction,
            customer=cmd.customer,
            supplier_id=cmd.supplier_id,
            payment_date=cmd.payment_date,
            method=cmd.method,
            total_amount=Money(cmd.total_amount),
            currency=cmd.currency,
            bank_account=cmd.bank_account,
            cheque=cmd.cheque,
            wht=cmd.wht,
            reference=cmd.reference,
            attachment_url=cmd.attachment_url,
            note=cmd.note,
            created_by=cmd.actor_id,
        )
        async with self.uow.transaction():
            await self.payments.save(payment)
        return payment


# ============================================================
# 2. Allocate Payment
# ============================================================

@dataclass
class AllocateToInvoiceCommand:
    payment_id: UUID
    invoice_id: UUID
    allocate_amount: Decimal
    wht_from_invoice: Decimal | None = None
    actor_id: UUID = None  # type: ignore


class AllocateToInvoiceUseCase:
    def __init__(
        self,
        payments: IPaymentRepository,
        invoices: IInvoiceForPaymentPort,
        uow,
    ):
        self.payments = payments
        self.invoices = invoices
        self.uow = uow

    async def execute(self, cmd: AllocateToInvoiceCommand) -> Payment:
        async with self.uow.transaction():
            payment = await self.payments.get_with_allocations(cmd.payment_id)
            if not payment:
                raise ValueError("ไม่พบ payment")

            invoice_summary = await self.invoices.get_invoice_summary(cmd.invoice_id)
            if not invoice_summary:
                raise ValueError("ไม่พบ invoice")

            if invoice_summary["status"] == "cancelled":
                raise ValueError("invoice ถูกยกเลิก — allocate ไม่ได้")

            payment.allocate_to_invoice(
                invoice_id=cmd.invoice_id,
                invoice_number=invoice_summary["invoice_number"],
                invoice_grand_total=Money(invoice_summary["grand_total"]),
                invoice_paid_before=Money(invoice_summary["paid_amount"]),
                allocate_amount=Money(cmd.allocate_amount),
                wht_from_invoice=(
                    Money(cmd.wht_from_invoice) if cmd.wht_from_invoice else None
                ),
            )

            await self.payments.update(payment)

            # Read-back
            persisted = await self.payments.get_with_allocations(payment.id)
            persisted.verify_totals()

        return payment


# ============================================================
# 3. Receive Payment (CORE — post ledger)
# ============================================================

@dataclass
class ReceivePaymentCommand:
    payment_id: UUID
    actor_id: UUID
    idempotency_key: str


class ReceivePaymentUseCase:
    """
    🎯 รับชำระ — ออกเลข, post ledger, mark invoice

    Flow:
    1.  Idempotency check
    2.  โหลด payment + allocations
    3.  ตรวจ status = DRAFT
    4.  ออกเลข (SELECT FOR UPDATE)
    5.  receive() → status RECEIVED
    6.  Persist
    7.  Read-back verify
    8.  Publish PaymentReceived → ledger handler
    9.  Audit
    """

    def __init__(
        self,
        payments: IPaymentRepository,
        sequence: IPaymentNumberSequence,
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        idempotency,
        uow,
    ):
        self.payments = payments
        self.sequence = sequence
        self.audit = audit
        self.publish = publish
        self.idempotency = idempotency
        self.uow = uow

    async def execute(self, cmd: ReceivePaymentCommand) -> Payment:
        company_id = get_company_id()

        async def _do() -> tuple[int, dict]:
            return await self._receive(cmd)

        await self.idempotency.execute(
            key=cmd.idempotency_key,
            company_id=company_id,
            endpoint=f"/api/v1/payments/{cmd.payment_id}/receive",
            method="POST",
            body={"payment_id": str(cmd.payment_id)},
            scope=IdempotencyScope.PERMANENT,
            action=_do,
        )
        return await self.payments.get_with_allocations(cmd.payment_id)

    async def _receive(self, cmd: ReceivePaymentCommand) -> tuple[int, dict]:
        async with self.uow.transaction():
            payment = await self.payments.get_with_allocations(cmd.payment_id)
            if not payment:
                raise ValueError("ไม่พบ payment")

            if payment.status != PaymentStatus.DRAFT:
                raise ValueError(f"receive ไม่ได้ — status = {payment.status.value}")

            # ตรวจ balance
            payment.verify_totals()

            # ออกเลข
            number = await self.sequence.next_number(
                company_id=payment.company_id,
                prefix="RCP",
                year=payment.payment_date.year,
            )
            payment.receive(number)

            await self.payments.update(payment)

            # Read-back
            persisted = await self.payments.get_with_allocations(payment.id)
            if not persisted:
                raise RuntimeError("read-back: ไม่พบ payment")
            persisted.verify_totals()
            if persisted.payment_number != payment.payment_number:
                raise RuntimeError("read-back: payment_number mismatch")

            # Audit
            await self.audit.execute(RecordAuditCommand(
                company_id=payment.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.PAYMENT_RECEIVED,
                entity_type="payment",
                entity_id=payment.id,
                after_state={
                    "payment_number": str(payment.payment_number),
                    "amount": str(payment.total_amount.amount),
                    "method": payment.method.value,
                },
            ))

            # Publish
            await self.publish.execute(PaymentReceived.create(
                payment_id=payment.id,
                company_id=payment.company_id,
                payment_number=str(payment.payment_number),
                customer_id=payment.customer.customer_id if payment.customer else None,
                supplier_id=str(payment.supplier_id) if payment.supplier_id else None,
                amount=str(payment.total_amount.amount),
                currency=payment.currency,
                method=payment.method.value,
                payment_date=payment.payment_date.isoformat(),
                wht_amount=str(payment.wht_amount.amount),
                bank_account_code=(
                    payment.bank_account.bank_code if payment.bank_account else None
                ),
                allocations=[
                    {
                        "invoice_id": str(a.invoice_id),
                        "invoice_number": a.invoice_number,
                        "allocated_amount": str(a.allocated_amount.amount),
                        "wht_amount": str(a.wht_amount.amount),
                    }
                    for a in payment.allocations
                ],
                actor_id=cmd.actor_id,
            ))

        return 201, {
            "id": str(payment.id),
            "payment_number": str(payment.payment_number),
        }


# ============================================================
# 4. Refund Payment
# ============================================================

@dataclass
class RefundPaymentCommand:
    payment_id: UUID
    reason: str
    amount: Decimal | None
    actor_id: UUID
    idempotency_key: str


class RefundPaymentUseCase:
    def __init__(self, payments, audit, publish, idempotency, uow):
        ...

    async def execute(self, cmd: RefundPaymentCommand) -> Payment:
        async with self.uow.transaction():
            payment = await self.payments.get_with_allocations(cmd.payment_id)
            if not payment:
                raise ValueError("ไม่พบ payment")

            before = payment.status.value
            amount = Money(cmd.amount) if cmd.amount else None
            payment.refund(cmd.reason, amount)
            await self.payments.update(payment)

            # Read-back
            persisted = await self.payments.get_by_id(payment.id)
            if persisted.status != PaymentStatus.REFUNDED:
                raise RuntimeError("read-back: status ไม่เปลี่ยน")

            await self.audit.execute(RecordAuditCommand(
                company_id=payment.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.PAYMENT_REFUNDED,
                entity_type="payment",
                entity_id=payment.id,
                before_state={"status": before},
                after_state={"status": "refunded", "reason": cmd.reason},
            ))

            await self.publish.execute(PaymentRefunded.create(
                payment_id=payment.id,
                company_id=payment.company_id,
                payload={
                    "reason": cmd.reason,
                    "amount": str((amount or payment.total_amount).amount),
                },
                actor_id=cmd.actor_id,
            ))
        return payment


# ============================================================
# 5. Customer Outstanding Query
# ============================================================

@dataclass
class GetCustomerOutstandingQuery:
    customer_id: UUID


class GetCustomerOutstandingUseCase:
    """ดูยอดค้างชำระของลูกค้า — ใช้ตอนรับชำระ"""

    def __init__(self, invoices: IInvoiceForPaymentPort):
        self.invoices = invoices

    async def execute(self, query: GetCustomerOutstandingQuery) -> list[dict]:
        company_id = get_company_id()
        return await self.invoices.get_customer_outstanding(
            company_id, query.customer_id,
        )
```

## 6.1.6 Ledger Handler

```python
# app/modules/payment/application/handlers.py

from decimal import Decimal
from datetime import date
from app.modules.ledger.application.use_cases import (
    PostJournalUseCase, PostJournalCommand, PostJournalLineInput,
)
from app.modules.ledger.domain.value_objects import JournalSource
from app.modules.payment.domain.events import PaymentReceived, PaymentRefunded
from app.core.audit.domain.entities import ActorType


class PaymentReceivedLedgerHandler:
    """
    ฟัง PaymentReceived → post journal

    Journal สำหรับรับชำระ:
      Dr. เงินสด/เงินฝากธนาคาร   net_received
      Dr. ภาษีหัก ณ ที่จ่าย       wht_amount
        Cr. ลูกหนี้การค้า          total_amount
    """

    def __init__(self, post_journal: PostJournalUseCase):
        self.post_journal = post_journal

    async def handle(self, event: PaymentReceived) -> None:
        p = event.payload
        total = Decimal(p["amount"])
        wht = Decimal(p.get("wht_amount", "0.00"))
        net = total - wht

        # เลือกบัญชีตาม method
        cash_account = self._cash_account_for(p["method"], p.get("bank_account_code"))

        lines = [
            PostJournalLineInput(
                account_code=cash_account,
                debit=net, credit=Decimal("0"),
                description=f"รับชำระ {p['payment_number']}",
                reference_id=event.aggregate_id,
            ),
        ]

        if wht > 0:
            lines.append(PostJournalLineInput(
                account_code="2110",  # ภาษีหัก ณ ที่จ่าย
                debit=wht, credit=Decimal("0"),
                description=f"WHT {p['payment_number']}",
                reference_id=event.aggregate_id,
                tax_code="WHT",
            ))

        # เครดิต AR (หรือ AP ถ้า outbound)
        ar_account = "1100" if p.get("customer_id") else "2000"
        lines.append(PostJournalLineInput(
            account_code=ar_account,
            debit=Decimal("0"), credit=total,
            description=f"รับชำระ {p['payment_number']}",
            reference_id=event.aggregate_id,
        ))

        await self.post_journal.execute(PostJournalCommand(
            source=JournalSource.PAYMENT,
            source_id=event.aggregate_id,
            posting_date=date.fromisoformat(p["payment_date"]),
            description=f"รับชำระ {p['payment_number']}",
            lines=lines,
            actor_id=event.actor_id,
            actor_type=ActorType.SYSTEM,
        ))

    @staticmethod
    def _cash_account_for(method: str, bank_code: str | None) -> str:
        if method == "cash":
            return "1000"
        return "1010"  # เงินฝากธนาคาร


class PaymentRefundedLedgerHandler:
    """
    ฟัง PaymentRefunded → reverse journal
    """

    def __init__(self, post_journal, reverse_journal, journals):
        self.post_journal = post_journal
        self.reverse_journal = reverse_journal
        self.journals = journals

    async def handle(self, event: PaymentRefunded) -> None:
        # หา journal เดิมของ payment นี้
        original = await self.journals.get_by_source(
            event.company_id, "payment", event.aggregate_id,
        )
        if not original:
            return
        await self.reverse_journal.execute(...)
```

## 6.1.7 Invoice Paid Handler

```python
# app/modules/payment/application/handlers.py (ต่อ)

class PaymentAllocationHandler:
    """
    ฟัง PaymentReceived → mark invoice paid

    เรียก invoice module ผ่าน port
    """

    def __init__(self, invoices: IInvoiceForPaymentPort, publish):
        self.invoices = invoices
        self.publish = publish

    async def handle(self, event: PaymentReceived) -> None:
        for alloc in event.payload.get("allocations", []):
            await self.invoices.mark_invoice_paid(
                invoice_id=UUID(alloc["invoice_id"]),
                paid_amount=alloc["allocated_amount"],
            )
```

## 6.1.8 Infrastructure — Models

```python
# app/modules/payment/infrastructure/models.py

from sqlalchemy import (
    Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base


class PaymentModel(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("company_id", "payment_number", name="uq_pay_company_number"),
        Index("ix_pay_company_date", "company_id", "payment_date"),
        Index("ix_pay_customer", "company_id", "customer_id"),
        Index("ix_pay_status", "company_id", "status"),
        Index("ix_pay_method", "company_id", "method", "payment_date"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    branch_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    payment_number: Mapped[str | None] = mapped_column(String(30))
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    # Customer snapshot
    customer_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    customer_code: Mapped[str | None] = mapped_column(String(50))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    customer_tax_id: Mapped[str | None] = mapped_column(String(13))
    customer_address: Mapped[str | None] = mapped_column(Text)
    customer_branch_code: Mapped[str | None] = mapped_column(String(10))

    # Supplier
    supplier_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    received_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    method: Mapped[str] = mapped_column(String(30), nullable=False)
    bank_account_data: Mapped[dict | None] = mapped_column(JSONB)
    cheque_data: Mapped[dict | None] = mapped_column(JSONB)
    reference: Mapped[str | None] = mapped_column(String(100))
    attachment_url: Mapped[str | None] = mapped_column(Text)

    currency: Mapped[str] = mapped_column(String(3), default="THB")
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    wht_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_received: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    unallocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    wht_data: Mapped[dict | None] = mapped_column(JSONB)

    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[str | None] = mapped_column(Text)

    allocations: Mapped[list["PaymentAllocationModel"]] = relationship(
        "PaymentAllocationModel", back_populates="payment",
        cascade="all, delete-orphan",
    )


class PaymentAllocationModel(Base):
    __tablename__ = "payment_allocations"
    __table_args__ = (
        Index("ix_pa_payment", "payment_id"),
        Index("ix_pa_invoice", "invoice_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    payment_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"),
    )
    invoice_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(30))
    invoice_grand_total: Mapped[float] = mapped_column(Numeric(15, 2))
    invoice_paid_before: Mapped[float] = mapped_column(Numeric(15, 2))
    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    wht_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    payment: Mapped[PaymentModel] = relationship(
        "PaymentModel", back_populates="allocations",
    )


class PaymentNumberSequenceModel(Base):
    __tablename__ = "payment_number_sequences"
    __table_args__ = (UniqueConstraint("company_id", "prefix", "year"),)

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    prefix: Mapped[str] = mapped_column(String(10))
    year: Mapped[int] = mapped_column(Integer)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
```

## 6.1.9 Database Schema

```sql
CREATE TABLE payments (
    id                  UUID PRIMARY KEY,
    company_id          UUID NOT NULL,
    branch_id           UUID,

    payment_number      VARCHAR(30),
    direction           VARCHAR(20) NOT NULL,
    status              VARCHAR(30) NOT NULL,

    customer_id         UUID,
    customer_code       VARCHAR(50),
    customer_name       VARCHAR(255),
    customer_tax_id     VARCHAR(13),
    customer_address    TEXT,
    customer_branch_code VARCHAR(10),

    supplier_id         UUID,

    payment_date        DATE NOT NULL,
    received_at         TIMESTAMPTZ NOT NULL,

    method              VARCHAR(30) NOT NULL,
    bank_account_data   JSONB,
    cheque_data         JSONB,
    reference           VARCHAR(100),
    attachment_url      TEXT,

    currency            VARCHAR(3) NOT NULL DEFAULT 'THB',
    total_amount        NUMERIC(15,2) NOT NULL,
    wht_amount          NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_received        NUMERIC(15,2) NOT NULL,
    allocated_amount    NUMERIC(15,2) NOT NULL DEFAULT 0,
    unallocated_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
    wht_data            JSONB,

    note                TEXT,
    created_by          UUID NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL,
    updated_at          TIMESTAMPTZ NOT NULL,
    cancelled_at        TIMESTAMPTZ,
    cancel_reason       TEXT,

    UNIQUE (company_id, payment_number)
);

CREATE INDEX ix_pay_company_date ON payments (company_id, payment_date DESC);
CREATE INDEX ix_pay_customer ON payments (company_id, customer_id);
CREATE INDEX ix_pay_status ON payments (company_id, status);
CREATE INDEX ix_pay_method ON payments (company_id, method, payment_date);

CREATE TABLE payment_allocations (
    id                    UUID PRIMARY KEY,
    payment_id            UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id            UUID NOT NULL,
    invoice_number        VARCHAR(30),
    invoice_grand_total   NUMERIC(15,2) NOT NULL,
    invoice_paid_before   NUMERIC(15,2) NOT NULL,
    allocated_amount      NUMERIC(15,2) NOT NULL,
    wht_amount            NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_amount            NUMERIC(15,2) NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL
);

CREATE INDEX ix_pa_payment ON payment_allocations (payment_id);
CREATE INDEX ix_pa_invoice ON payment_allocations (invoice_id);

CREATE TABLE payment_number_sequences (
    id             UUID PRIMARY KEY,
    company_id     UUID NOT NULL,
    prefix         VARCHAR(10) NOT NULL,
    year           INT NOT NULL,
    current_value  INT NOT NULL DEFAULT 0,
    UNIQUE (company_id, prefix, year)
);
```

## 6.1.10 Presentation — API

```python
# app/modules/payment/presentation/routers.py

router = APIRouter(prefix="/api/v1/payments", tags=["Payment"])


@router.post("/drafts", status_code=201)
async def create_payment_draft(
    body: CreatePaymentRequest,
    user = Depends(require_permission("payment:create")),
    use_case = Depends(get_create_payment_use_case),
):
    ...


@router.post("/{payment_id}/allocations", status_code=201)
async def allocate_to_invoice(
    payment_id: UUID,
    body: AllocateRequest,
    user = Depends(require_permission("payment:create")),
    use_case = Depends(get_allocate_use_case),
):
    ...


@router.post("/{payment_id}/receive", status_code=201)
async def receive_payment(
    payment_id: UUID,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("payment:create")),
    use_case = Depends(get_receive_payment_use_case),
):
    """ยืนยันรับชำระ — ต้องส่ง Idempotency-Key"""
    return await use_case.execute(ReceivePaymentCommand(
        payment_id=payment_id,
        actor_id=user.id,
        idempotency_key=idempotency_key,
    ))


@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: UUID,
    body: RefundRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("payment:refund")),
    use_case = Depends(get_refund_payment_use_case),
):
    ...


@router.get("/")
async def list_payments(
    customer_id: UUID | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    status: str | None = Query(None),
    user = Depends(require_permission("payment:read")),
):
    ...


@router.get("/{payment_id}")
async def get_payment(payment_id: UUID, ...): ...


@router.get("/customers/{customer_id}/outstanding")
async def get_customer_outstanding(
    customer_id: UUID,
    user = Depends(require_permission("payment:read")),
    use_case = Depends(get_customer_outstanding_use_case),
):
    """ดูยอดค้างของลูกค้า (ใช้ตอนรับชำระ)"""
    return await use_case.execute(GetCustomerOutstandingQuery(customer_id))


@router.get("/{payment_id}/receipt.pdf")
async def get_receipt_pdf(payment_id: UUID, ...):
    """ดาวน์โหลดใบเสร็จรับเงิน"""
    ...
```

## 6.1.11 Folder Structure

```text
app/modules/payment/
├── domain/
│   ├── entities.py            # Payment, PaymentAllocation
│   ├── value_objects.py       # PaymentNumber, PaymentMethod, enums, ChequeInfo, WhtDeduction
│   ├── events.py              # PaymentReceived, PaymentRefunded, ...
│   └── errors.py
├── application/
│   ├── interfaces.py          # IPaymentRepository, IInvoiceForPaymentPort
│   ├── use_cases.py           # Create, Allocate, Receive, Refund
│   └── handlers.py            # PaymentReceivedLedgerHandler, PaymentAllocationHandler
├── infrastructure/
│   ├── models.py              # PaymentModel, PaymentAllocationModel, Sequence
│   ├── repositories.py        # PostgresPaymentRepository + Sequence
│   └── pdf/
│       └── receipt_renderer.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── domain/
    │   ├── test_entities.py
    │   ├── test_allocation.py
    │   └── test_state_machine.py
    ├── application/
    │   ├── test_receive.py
    │   └── test_allocation_overflow.py
    └── integration/
        └── test_payment_to_ledger.py
```

## 6.1.12 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (stabilize) / 2 (harden) |
| **DoD** | ✅ allocate ไม่เกิน invoice remaining<br>✅ partial payment ทำงาน<br>✅ multi-invoice allocation ทำงาน<br>✅ receive → post ledger อัตโนมัติ<br>✅ WHT deduction ทำงาน<br>✅ Refund → reversal journal<br>✅ Idempotency: ยิงซ้ำ → 1<br>✅ verify_totals ผ่านทุกครั้ง |

---

# 🧩 Module 6.2 — `accounting_gateway`

## 6.2.1 Purpose & Scope

**Purpose:** Sync ข้อมูลบัญชีไปยัง Thai Cloud Accounting (FlowAccount, PEAK, ฯลฯ) ผ่าน Outbox pattern เพื่อความ reliable + retry-safe + ไม่ double-post

**Scope:**
- ✅ Provider abstraction (FlowAccount, PEAK, Xero, ...)
- ✅ Outbox pattern (transactional outbox)
- ✅ Retry + exponential backoff
- ✅ Idempotency (ตาม provider)
- ✅ Sync mapping (invoice ↔ cloud invoice)
- ✅ Reconcile (DB ↔ Cloud)
- ✅ Dead letter queue
- ✅ Manual retry / resolve
- ❌ ไม่เป็น source of truth (DB คือ)
- ❌ ไม่ทำ ERP เอง (Cloud = secondary)

## 6.2.2 Domain Model

```python
# app/modules/accounting_gateway/domain/value_objects.py

from dataclasses import dataclass
from enum import Enum


class SyncProvider(str, Enum):
    FLOWACCOUNT = "flowaccount"
    PEAK = "peak"
    XERO = "xero"
    QUICKBOOKS = "quickbooks"
    CUSTOM = "custom"


class SyncEntityType(str, Enum):
    INVOICE = "invoice"
    TAX_INVOICE = "tax_invoice"
    PAYMENT = "payment"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    CONTACT = "contact"
    PRODUCT = "product"
    JOURNAL = "journal"


class SyncDirection(str, Enum):
    PUSH = "push"                 # DB → Cloud
    PULL = "pull"                 # Cloud → DB (rare)


class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"             # retry ได้
    DEAD_LETTER = "dead_letter"   # retry ครบแล้ว ต้อง manual
    SKIPPED = "skipped"           # ไม่ sync (config)


@dataclass(frozen=True, slots=True)
class ExternalRef:
    """
    อ้างอิง entity ใน cloud
    """
    provider: SyncProvider
    external_id: str
    external_number: str | None
    synced_at: str
    raw_response: dict | None     # เก็บ response ไว้ debug


@dataclass(frozen=True, slots=True)
class SyncMapping:
    """
    Mapping ระหว่าง internal entity ↔ external entity
    """
    id: str
    company_id: str
    entity_type: SyncEntityType
    internal_id: str
    provider: SyncProvider
    external_id: str
    external_number: str | None
    last_synced_at: str
    last_sync_hash: str           # hash ของ payload → ตรวจ diff
    sync_metadata: dict | None
```

```python
# app/modules/accounting_gateway/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, SyncEntityType, SyncDirection, SyncStatus, ExternalRef,
)


@dataclass
class SyncJob:
    """
    Sync Job — Aggregate Root

    Invariants:
    1.  status transitions: PENDING → IN_PROGRESS → SUCCESS/FAILED
    2.  FAILED → retry_count++
    3.  retry_count ≥ max_retries → DEAD_LETTER
    4.  SUCCESS → external_ref ต้องมี
    5.  event_id unique (ห้ามสร้าง job ซ้ำจาก event เดียว)
    """
    id: UUID
    company_id: UUID
    event_id: UUID                # อ้างถึง outbox event
    entity_type: SyncEntityType
    entity_id: UUID
    provider: SyncProvider
    direction: SyncDirection
    status: SyncStatus

    payload: dict                 # snapshot payload ที่จะส่ง
    payload_hash: str             # sha256 ของ payload

    external_ref: ExternalRef | None
    last_error: str | None
    retry_count: int
    max_retries: int

    next_retry_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        event_id: UUID,
        entity_type: SyncEntityType,
        entity_id: UUID,
        provider: SyncProvider,
        direction: SyncDirection,
        payload: dict,
        payload_hash: str,
        max_retries: int = 5,
    ) -> "SyncJob":
        return cls(
            id=uuid4(),
            company_id=company_id,
            event_id=event_id,
            entity_type=entity_type,
            entity_id=entity_id,
            provider=provider,
            direction=direction,
            status=SyncStatus.PENDING,
            payload=payload,
            payload_hash=payload_hash,
            external_ref=None,
            last_error=None,
            retry_count=0,
            max_retries=max_retries,
            next_retry_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            created_at=datetime.utcnow(),
        )

    def start(self) -> None:
        if self.status != SyncStatus.PENDING:
            raise ValueError(f"start ไม่ได้ — status = {self.status.value}")
        self.status = SyncStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def succeed(self, external_ref: ExternalRef) -> None:
        if self.status != SyncStatus.IN_PROGRESS:
            raise ValueError("succeed ได้เฉพาะ IN_PROGRESS")
        self.status = SyncStatus.SUCCESS
        self.external_ref = external_ref
        self.completed_at = datetime.utcnow()
        self.last_error = None

    def fail(self, error: str, next_retry_at: datetime | None) -> None:
        if self.status != SyncStatus.IN_PROGRESS:
            raise ValueError("fail ได้เฉพาะ IN_PROGRESS")
        self.last_error = error[:2000]  # truncate
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = SyncStatus.DEAD_LETTER
            self.completed_at = datetime.utcnow()
        else:
            self.status = SyncStatus.FAILED
            self.next_retry_at = next_retry_at or datetime.utcnow()

    def retry(self, actor_id: UUID) -> None:
        """Manual retry จาก dead letter"""
        if self.status not in (SyncStatus.FAILED, SyncStatus.DEAD_LETTER):
            raise ValueError("retry ได้เฉพาะ FAILED / DEAD_LETTER")
        self.status = SyncStatus.PENDING
        self.next_retry_at = datetime.utcnow()
        self.retry_count = 0
        self.last_error = None


@dataclass
class SyncMappingEntry:
    """Sync mapping — entity ↔ external"""
    id: UUID
    company_id: UUID
    entity_type: SyncEntityType
    internal_id: UUID
    provider: SyncProvider
    external_id: str
    external_number: str | None
    last_synced_at: datetime
    last_sync_hash: str
    sync_metadata: dict | None
```

## 6.2.3 Domain Events

```python
# app/modules/accounting_gateway/domain/events.py

from app.core.events.domain.entities import DomainEvent


class SyncJobCreated(DomainEvent): ...
class SyncJobSucceeded(DomainEvent): ...
class SyncJobFailed(DomainEvent): ...
class SyncJobDeadLetter(DomainEvent):
    """🚨 ต้อง manual — alert"""
    ...
class ReconciliationMismatch(DomainEvent):
    """🚨 DB ↔ Cloud ไม่ตรง"""
    ...
```

## 6.2.4 Application — Interfaces (Ports)

```python
# app/modules/accounting_gateway/application/interfaces.py

from typing import Protocol, Any
from uuid import UUID

from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, ExternalRef,
)
from app.modules.accounting_gateway.domain.entities import (
    SyncJob, SyncMappingEntry,
)


class IAccountingProvider(Protocol):
    """
    Port — abstraction ของ cloud accounting provider
    แต่ละ provider implement (FlowAccount, PEAK, ...)
    """

    @property
    def provider(self) -> SyncProvider: ...

    async def authenticate(self, company_id: UUID) -> None: ...

    async def push_invoice(
        self, company_id: UUID, payload: dict,
    ) -> ExternalRef: ...

    async def push_tax_invoice(
        self, company_id: UUID, payload: dict,
    ) -> ExternalRef: ...

    async def push_payment(
        self, company_id: UUID, payload: dict,
    ) -> ExternalRef: ...

    async def push_contact(
        self, company_id: UUID, payload: dict,
    ) -> ExternalRef: ...

    async def push_product(
        self, company_id: UUID, payload: dict,
    ) -> ExternalRef: ...

    async def find_by_external_id(
        self, company_id: UUID, external_id: str,
    ) -> dict | None: ...

    async def list_invoices(
        self, company_id: UUID, *,
        from_date: str, to_date: str,
    ) -> list[dict]: ...

    async def health_check(self, company_id: UUID) -> bool: ...


class ISyncJobRepository(Protocol):
    async def get_by_id(self, job_id: UUID) -> SyncJob | None: ...
    async def exists_by_event(
        self, company_id: UUID, event_id: UUID,
    ) -> bool: ...
    async def fetch_pending(
        self, *, limit: int, now,
    ) -> list[SyncJob]: ...
    async def fetch_dead_letters(
        self, company_id: UUID, limit: int,
    ) -> list[SyncJob]: ...
    async def save(self, job: SyncJob) -> None: ...
    async def update(self, job: SyncJob) -> None: ...


class ISyncMappingRepository(Protocol):
    async def get_by_internal(
        self, company_id: UUID, entity_type: str, internal_id: UUID,
        provider: SyncProvider,
    ) -> SyncMappingEntry | None: ...
    async def get_by_external(
        self, company_id: UUID, provider: SyncProvider, external_id: str,
    ) -> SyncMappingEntry | None: ...
    async def save(self, mapping: SyncMappingEntry) -> None: ...
    async def update(self, mapping: SyncMappingEntry) -> None: ...
```

## 6.2.5 Application — Use Cases

```python
# app/modules/accounting_gateway/application/use_cases.py

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from app.modules.accounting_gateway.domain.entities import (
    SyncJob, SyncMappingEntry,
)
from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, SyncEntityType, SyncDirection, SyncStatus, ExternalRef,
)
from app.modules.accounting_gateway.domain.events import (
    SyncJobCreated, SyncJobSucceeded, SyncJobFailed, SyncJobDeadLetter,
)
from app.modules.accounting_gateway.application.interfaces import (
    IAccountingProvider, ISyncJobRepository, ISyncMappingRepository,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase


# ============================================================
# 1. Enqueue Sync (จาก Outbox)
# ============================================================

@dataclass
class EnqueueSyncCommand:
    company_id: UUID
    event_id: UUID
    entity_type: SyncEntityType
    entity_id: UUID
    provider: SyncProvider
    direction: SyncDirection
    payload: dict


class EnqueueSyncUseCase:
    """
    สร้าง SyncJob จาก event — idempotent (event_id unique)

    เรียกจาก handler ที่ฟัง domain event (InvoiceIssued, PaymentReceived, ...)
    """

    def __init__(
        self,
        jobs: ISyncJobRepository,
        publish: PublishEventUseCase,
        uow,
    ):
        self.jobs = jobs
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: EnqueueSyncCommand) -> SyncJob | None:
        # ตรวจว่ามี job ของ event นี้แล้วหรือยัง
        if await self.jobs.exists_by_event(cmd.company_id, cmd.event_id):
            return None

        payload_hash = hashlib.sha256(
            json.dumps(cmd.payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        job = SyncJob.create(
            company_id=cmd.company_id,
            event_id=cmd.event_id,
            entity_type=cmd.entity_type,
            entity_id=cmd.entity_id,
            provider=cmd.provider,
            direction=cmd.direction,
            payload=cmd.payload,
            payload_hash=payload_hash,
        )

        async with self.uow.transaction():
            await self.jobs.save(job)
            await self.publish.execute(SyncJobCreated.create(
                company_id=cmd.company_id,
                payload={
                    "job_id": str(job.id),
                    "entity_type": cmd.entity_type.value,
                    "entity_id": str(cmd.entity_id),
                    "provider": cmd.provider.value,
                },
            ))
        return job


# ============================================================
# 2. Process Sync Job (Worker)
# ============================================================

class ProcessSyncJobWorker:
    """
    Worker — poll pending jobs → push to cloud → mark result

    ใช้ exponential backoff:
    - retry 1: 30s
    - retry 2: 2 min
    - retry 3: 8 min
    - retry 4: 30 min
    - retry 5: 2 hours
    - เกิน 5 → DEAD_LETTER
    """

    def __init__(
        self,
        jobs: ISyncJobRepository,
        mappings: ISyncMappingRepository,
        providers: dict[SyncProvider, IAccountingProvider],
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        uow,
        batch_size: int = 50,
    ):
        self.jobs = jobs
        self.mappings = mappings
        self.providers = providers
        self.audit = audit
        self.publish = publish
        self.uow = uow
        self.batch_size = batch_size

    async def run_once(self) -> int:
        now = datetime.utcnow()
        pending = await self.jobs.fetch_pending(limit=self.batch_size, now=now)
        processed = 0
        for job in pending:
            try:
                await self._process_one(job)
                processed += 1
            except Exception as e:
                # log, ไม่ให้ worker ตาย
                ...
        return processed

    async def _process_one(self, job: SyncJob) -> None:
        provider = self.providers.get(job.provider)
        if not provider:
            async with self.uow.transaction():
                job.start()
                job.fail(
                    f"provider {job.provider.value} ไม่พร้อม",
                    next_retry_at=self._backoff(job.retry_count),
                )
                await self.jobs.update(job)
            return

        # ----- Idempotency: ตรวจ mapping ก่อน -----
        existing = await self.mappings.get_by_internal(
            job.company_id, job.entity_type.value,
            job.entity_id, job.provider,
        )
        if existing:
            # sync แล้ว — verify hash
            if existing.last_sync_hash == job.payload_hash:
                # ไม่มีอะไรเปลี่ยน — mark success by replay
                async with self.uow.transaction():
                    job.start()
                    job.succeed(ExternalRef(
                        provider=job.provider,
                        external_id=existing.external_id,
                        external_number=existing.external_number,
                        synced_at=existing.last_synced_at.isoformat(),
                        raw_response={"replayed": True},
                    ))
                    await self.jobs.update(job)
                return

        # ----- Push to cloud -----
        async with self.uow.transaction():
            job.start()
            await self.jobs.update(job)

        try:
            ref = await self._push(provider, job)

            async with self.uow.transaction():
                job.succeed(ref)
                await self.jobs.update(job)

                # upsert mapping
                await self._upsert_mapping(job, ref)

                await self.publish.execute(SyncJobSucceeded.create(
                    company_id=job.company_id,
                    payload={
                        "job_id": str(job.id),
                        "external_id": ref.external_id,
                    },
                ))

        except Exception as e:
            async with self.uow.transaction():
                job.fail(str(e), next_retry_at=self._backoff(job.retry_count))
                await self.jobs.update(job)

                if job.status == SyncStatus.DEAD_LETTER:
                    await self.publish.execute(SyncJobDeadLetter.create(
                        company_id=job.company_id,
                        payload={
                            "job_id": str(job.id),
                            "entity_type": job.entity_type.value,
                            "entity_id": str(job.entity_id),
                            "error": str(e)[:500],
                            "retry_count": job.retry_count,
                        },
                    ))

    async def _push(
        self, provider: IAccountingProvider, job: SyncJob,
    ) -> ExternalRef:
        if job.entity_type == SyncEntityType.INVOICE:
            return await provider.push_invoice(job.company_id, job.payload)
        if job.entity_type == SyncEntityType.TAX_INVOICE:
            return await provider.push_tax_invoice(job.company_id, job.payload)
        if job.entity_type == SyncEntityType.PAYMENT:
            return await provider.push_payment(job.company_id, job.payload)
        if job.entity_type == SyncEntityType.CONTACT:
            return await provider.push_contact(job.company_id, job.payload)
        if job.entity_type == SyncEntityType.PRODUCT:
            return await provider.push_product(job.company_id, job.payload)
        raise ValueError(f"ไม่รองรับ entity_type: {job.entity_type}")

    async def _upsert_mapping(self, job: SyncJob, ref: ExternalRef) -> None:
        existing = await self.mappings.get_by_internal(
            job.company_id, job.entity_type.value, job.entity_id, job.provider,
        )
        if existing:
            existing.external_id = ref.external_id
            existing.external_number = ref.external_number
            existing.last_synced_at = datetime.utcnow()
            existing.last_sync_hash = job.payload_hash
            existing.sync_metadata = ref.raw_response
            await self.mappings.update(existing)
        else:
            from uuid import uuid4
            await self.mappings.save(SyncMappingEntry(
                id=uuid4(),
                company_id=job.company_id,
                entity_type=job.entity_type,
                internal_id=job.entity_id,
                provider=job.provider,
                external_id=ref.external_id,
                external_number=ref.external_number,
                last_synced_at=datetime.utcnow(),
                last_sync_hash=job.payload_hash,
                sync_metadata=ref.raw_response,
            ))

    @staticmethod
    def _backoff(retry_count: int) -> datetime:
        """30s, 2m, 8m, 30m, 2h"""
        seconds = [30, 120, 480, 1800, 7200]
        idx = min(retry_count, len(seconds) - 1)
        return datetime.utcnow() + timedelta(seconds=seconds[idx])


# ============================================================
# 3. Manual Retry
# ============================================================

@dataclass
class RetrySyncJobCommand:
    job_id: UUID
    actor_id: UUID


class RetrySyncJobUseCase:
    def __init__(self, jobs, audit, uow):
        self.jobs = jobs
        self.audit = audit
        self.uow = uow

    async def execute(self, cmd: RetrySyncJobCommand) -> SyncJob:
        async with self.uow.transaction():
            job = await self.jobs.get_by_id(cmd.job_id)
            if not job:
                raise ValueError("ไม่พบ job")

            job.retry(cmd.actor_id)
            await self.jobs.update(job)

            await self.audit.execute(RecordAuditCommand(
                company_id=job.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.CONFIG_CHANGED,
                entity_type="sync_job",
                entity_id=job.id,
                after_state={"status": "pending (manual retry)"},
            ))
        return job


# ============================================================
# 4. Reconciliation
# ============================================================

@dataclass
class ReconcileCommand:
    company_id: UUID
    from_date: str
    to_date: str


class ReconcileUseCase:
    """
    เทียบ DB ↔ Cloud

    Checks:
    1. invoice ใน DB → มีใน cloud
    2. invoice ใน cloud → มีใน DB
    3. ยอด invoice ตรงกัน
    4. payment ตรงกัน
    """

    def __init__(
        self,
        jobs: ISyncJobRepository,
        mappings: ISyncMappingRepository,
        invoices_port,  # query internal invoices
        providers: dict[SyncProvider, IAccountingProvider],
    ):
        self.jobs = jobs
        self.mappings = mappings
        self.invoices_port = invoices_port
        self.providers = providers

    async def execute(self, cmd: ReconcileCommand) -> dict:
        discrepancies = []

        for provider_enum, provider in self.providers.items():
            # 1. ดึง internal invoices
            internal = await self.invoices_port.list_by_date_range(
                cmd.company_id, cmd.from_date, cmd.to_date,
            )

            # 2. ดึง external invoices
            external = await provider.list_invoices(
                cmd.company_id, from_date=cmd.from_date, to_date=cmd.to_date,
            )

            external_by_ref = {
                e["reference"]: e for e in external if e.get("reference")
            }

            # 3. เทียบ
            for inv in internal:
                ext = external_by_ref.get(inv["invoice_number"])
                if not ext:
                    discrepancies.append({
                        "type": "missing_in_cloud",
                        "invoice_number": inv["invoice_number"],
                        "internal_total": inv["grand_total"],
                    })
                elif abs(float(ext["total"]) - float(inv["grand_total"])) > 0.01:
                    discrepancies.append({
                        "type": "amount_mismatch",
                        "invoice_number": inv["invoice_number"],
                        "internal_total": inv["grand_total"],
                        "external_total": ext["total"],
                    })

            # 4. หา external ที่ไม่มี internal
            internal_numbers = {i["invoice_number"] for i in internal}
            for ext in external:
                if ext.get("reference") not in internal_numbers:
                    discrepancies.append({
                        "type": "missing_in_db",
                        "external_id": ext.get("id"),
                        "external_reference": ext.get("reference"),
                    })

        return {
            "company_id": str(cmd.company_id),
            "from_date": cmd.from_date,
            "to_date": cmd.to_date,
            "total_discrepancies": len(discrepancies),
            "discrepancies": discrepancies[:100],  # limit
        }
```

## 6.2.6 Outbox Event Handlers

```python
# app/modules/accounting_gateway/application/handlers.py

from app.modules.invoice.domain.events import (
    InvoiceIssued, InvoiceCancelled,
)
from app.modules.payment.domain.events import PaymentReceived
from app.modules.accounting_gateway.application.use_cases import (
    EnqueueSyncUseCase, EnqueueSyncCommand,
)
from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, SyncEntityType, SyncDirection,
)


class InvoiceIssuedSyncHandler:
    """ฟัง InvoiceIssued → enqueue sync job"""

    def __init__(
        self,
        enqueue: EnqueueSyncUseCase,
        provider: SyncProvider,
        config,
    ):
        self.enqueue = enqueue
        self.provider = provider
        self.config = config

    async def handle(self, event: InvoiceIssued) -> None:
        # ตรวจ config ว่าบริษัทนี้เปิด sync ไหม
        enabled = await self.config.execute(
            event.company_id, "sync.accounting.enabled", True,
        )
        if not enabled:
            return

        payload = self._build_payload(event)
        await self.enqueue.execute(EnqueueSyncCommand(
            company_id=event.company_id,
            event_id=event.event_id,
            entity_type=SyncEntityType.TAX_INVOICE,
            entity_id=event.aggregate_id,
            provider=self.provider,
            direction=SyncDirection.PUSH,
            payload=payload,
        ))

    def _build_payload(self, event: InvoiceIssued) -> dict:
        """แปลง InvoiceIssued payload → format ที่ provider ต้องการ"""
        p = event.payload
        return {
            "invoice_number": p["invoice_number"],
            "issue_date": p["issue_date"],
            "due_date": p["due_date"],
            "customer_id": p["customer_id"],
            "currency": p["currency"],
            "grand_total": p["grand_total"],
            "lines": p["lines"],
            # ... map ตาม spec ของ provider
        }


class PaymentReceivedSyncHandler:
    """ฟัง PaymentReceived → enqueue sync job"""

    def __init__(self, enqueue, provider, config):
        self.enqueue = enqueue
        self.provider = provider
        self.config = config

    async def handle(self, event: PaymentReceived) -> None:
        enabled = await self.config.execute(
            event.company_id, "sync.accounting.enabled", True,
        )
        if not enabled:
            return

        await self.enqueue.execute(EnqueueSyncCommand(
            company_id=event.company_id,
            event_id=event.event_id,
            entity_type=SyncEntityType.PAYMENT,
            entity_id=event.aggregate_id,
            provider=self.provider,
            direction=SyncDirection.PUSH,
            payload=event.payload,
        ))
```

## 6.2.7 Infrastructure — Provider Implementations

```python
# app/modules/accounting_gateway/infrastructure/providers/base.py

import httpx
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type,
)

from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, ExternalRef,
)


class BaseHttpProvider:
    """Base class สำหรับ HTTP-based provider"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def _request(
        self, method: str, path: str, *, headers: dict, json: dict | None = None,
    ) -> dict:
        response = await self.client.request(method, path, headers=headers, json=json)
        if response.status_code >= 500:
            response.raise_for_status()
        return response.json()
```

```python
# app/modules/accounting_gateway/infrastructure/providers/flowaccount.py

from uuid import UUID
from datetime import datetime

from app.modules.accounting_gateway.domain.value_objects import (
    SyncProvider, ExternalRef,
)
from app.modules.accounting_gateway.infrastructure.providers.base import (
    BaseHttpProvider,
)


class FlowAccountProvider(BaseHttpProvider):
    """
    FlowAccount API implementation
    https://flowaccount.com/
    """

    provider = SyncProvider.FLOWACCOUNT

    def __init__(self, base_url: str, token_store):
        super().__init__(base_url)
        self.token_store = token_store

    async def authenticate(self, company_id: UUID) -> None:
        token = await self.token_store.get_token(company_id, "flowaccount")
        if not token:
            raise RuntimeError(f"ไม่พบ token สำหรับ company {company_id}")
        self._headers = {"Authorization": f"Bearer {token}"}

    async def push_invoice(self, company_id: UUID, payload: dict) -> ExternalRef:
        await self.authenticate(company_id)
        body = self._transform_invoice(payload)
        response = await self._request(
            "POST", "/invoices", headers=self._headers, json=body,
        )
        return ExternalRef(
            provider=self.provider,
            external_id=str(response["id"]),
            external_number=response.get("documentNumber"),
            synced_at=datetime.utcnow().isoformat(),
            raw_response=response,
        )

    async def push_tax_invoice(self, company_id: UUID, payload: dict) -> ExternalRef:
        # คล้าย push_invoice แต่ endpoint tax invoice
        ...

    async def push_payment(self, company_id: UUID, payload: dict) -> ExternalRef:
        ...

    async def list_invoices(
        self, company_id: UUID, *, from_date: str, to_date: str,
    ) -> list[dict]:
        await self.authenticate(company_id)
        response = await self._request(
            "GET", "/invoices",
            headers=self._headers,
            json={"fromDate": from_date, "toDate": to_date},
        )
        return response.get("data", [])

    async def health_check(self, company_id: UUID) -> bool:
        try:
            await self.authenticate(company_id)
            await self._request("GET", "/me", headers=self._headers)
            return True
        except Exception:
            return False

    def _transform_invoice(self, payload: dict) -> dict:
        """แปลง internal payload → FlowAccount format"""
        return {
            "documentNumber": payload["invoice_number"],
            "issuedDate": payload["issue_date"],
            "dueDate": payload["due_date"],
            "contactId": payload["customer_id"],
            "currency": payload.get("currency", "THB"),
            "total": float(payload["grand_total"]),
            "items": [
                {
                    "description": ln.get("description", ""),
                    "quantity": float(ln.get("quantity", 1)),
                    "price": float(ln.get("net_amount", 0)),
                }
                for ln in payload.get("lines", [])
            ],
        }
```

```python
# app/modules/accounting_gateway/infrastructure/providers/peak.py

class PeakProvider(BaseHttpProvider):
    """PEAK Accounting"""
    provider = SyncProvider.PEAK
    ...
```

```python
# app/modules/accounting_gateway/infrastructure/providers/noop.py

class NoopProvider:
    """
    Noop provider — ใช้เมื่อยังไม่ตั้งค่า provider
    (dev / test)
    """
    provider = SyncProvider.CUSTOM

    async def authenticate(self, company_id: UUID) -> None:
        pass

    async def push_invoice(self, company_id: UUID, payload: dict) -> ExternalRef:
        from uuid import uuid4
        return ExternalRef(
            provider=self.provider,
            external_id=str(uuid4()),
            external_number=payload.get("invoice_number"),
            synced_at=datetime.utcnow().isoformat(),
            raw_response={"noop": True},
        )

    # ... methods อื่น
```

## 6.2.8 Infrastructure — Models

```python
# app/modules/accounting_gateway/infrastructure/models.py

from sqlalchemy import (
    DateTime, Index, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class SyncJobModel(Base):
    __tablename__ = "sync_jobs"
    __table_args__ = (
        UniqueConstraint("company_id", "event_id", name="uq_sync_event"),
        Index("ix_sync_status_retry", "status", "next_retry_at"),
        Index("ix_sync_company_entity", "company_id", "entity_type", "entity_id"),
        Index("ix_sync_provider_status", "provider", "status"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    event_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    external_id: Mapped[str | None] = mapped_column(String(255))
    external_number: Mapped[str | None] = mapped_column(String(100))
    external_response: Mapped[dict | None] = mapped_column(JSONB)

    last_error: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=5)

    next_retry_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class SyncMappingModel(Base):
    __tablename__ = "sync_mappings"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "entity_type", "internal_id", "provider",
            name="uq_sync_mapping_internal",
        ),
        Index("ix_sync_map_external", "company_id", "provider", "external_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    internal_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_number: Mapped[str | None] = mapped_column(String(100))
    last_synced_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_sync_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    sync_metadata: Mapped[dict | None] = mapped_column(JSONB)


class ProviderCredentialModel(Base):
    """
    Credentials ของ cloud accounting ต่อ company
    🔐 token ต้อง encrypt at rest
    """
    __tablename__ = "provider_credentials"
    __table_args__ = (
        UniqueConstraint("company_id", "provider", name="uq_cred_company_provider"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
```

## 6.2.9 Database Schema

```sql
CREATE TABLE sync_jobs (
    id                 UUID PRIMARY KEY,
    company_id         UUID NOT NULL,
    event_id           UUID NOT NULL,
    entity_type        VARCHAR(30) NOT NULL,
    entity_id          UUID NOT NULL,
    provider           VARCHAR(30) NOT NULL,
    direction          VARCHAR(10) NOT NULL,
    status             VARCHAR(20) NOT NULL,
    payload            JSONB NOT NULL,
    payload_hash       VARCHAR(64) NOT NULL,
    external_id        VARCHAR(255),
    external_number    VARCHAR(100),
    external_response  JSONB,
    last_error         TEXT,
    retry_count        INT NOT NULL DEFAULT 0,
    max_retries        INT NOT NULL DEFAULT 5,
    next_retry_at      TIMESTAMPTZ,
    started_at         TIMESTAMPTZ,
    completed_at       TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL,
    UNIQUE (company_id, event_id)
);

CREATE INDEX ix_sync_status_retry ON sync_jobs (status, next_retry_at)
    WHERE status IN ('pending', 'failed');
CREATE INDEX ix_sync_company_entity ON sync_jobs (company_id, entity_type, entity_id);
CREATE INDEX ix_sync_provider_status ON sync_jobs (provider, status);

CREATE TABLE sync_mappings (
    id                UUID PRIMARY KEY,
    company_id        UUID NOT NULL,
    entity_type       VARCHAR(30) NOT NULL,
    internal_id       UUID NOT NULL,
    provider          VARCHAR(30) NOT NULL,
    external_id       VARCHAR(255) NOT NULL,
    external_number   VARCHAR(100),
    last_synced_at    TIMESTAMPTZ NOT NULL,
    last_sync_hash    VARCHAR(64) NOT NULL,
    sync_metadata     JSONB,
    UNIQUE (company_id, entity_type, internal_id, provider)
);

CREATE INDEX ix_sync_map_external ON sync_mappings (company_id, provider, external_id);

CREATE TABLE provider_credentials (
    id                     UUID PRIMARY KEY,
    company_id             UUID NOT NULL,
    provider               VARCHAR(30) NOT NULL,
    encrypted_token        TEXT NOT NULL,
    encrypted_refresh_token TEXT,
    token_expires_at       TIMESTAMPTZ,
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ NOT NULL,
    updated_at             TIMESTAMPTZ NOT NULL,
    UNIQUE (company_id, provider)
);
```

## 6.2.10 Worker Setup

```python
# app/modules/accounting_gateway/infrastructure/worker.py

import asyncio
import logging

logger = logging.getLogger(__name__)


class SyncWorker:
    """
    Worker loop — poll → process → sleep

    รันเป็น process แยก หรือ asyncio task
    """

    def __init__(
        self,
        worker: ProcessSyncJobWorker,
        interval_seconds: int = 10,
    ):
        self.worker = worker
        self.interval = interval_seconds
        self._running = False

    async def start(self) -> None:
        self._running = True
        logger.info("SyncWorker started")
        while self._running:
            try:
                count = await self.worker.run_once()
                if count > 0:
                    logger.info(f"processed {count} jobs")
            except Exception as e:
                logger.exception(f"worker error: {e}")
            await asyncio.sleep(self.interval)

    async def stop(self) -> None:
        self._running = False
        logger.info("SyncWorker stopped")
```

## 6.2.11 Presentation — API

```python
# app/modules/accounting_gateway/presentation/routers.py

router = APIRouter(
    prefix="/api/v1/accounting-gateway", tags=["Accounting Gateway"],
)


# ---------- Sync Jobs ----------
@router.get("/jobs")
async def list_sync_jobs(
    status: str | None = Query(None),
    entity_type: str | None = Query(None),
    user = Depends(require_permission("config:read")),
):
    ...


@router.get("/jobs/{job_id}")
async def get_sync_job(job_id: UUID, ...): ...


@router.post("/jobs/{job_id}/retry")
async def retry_sync_job(
    job_id: UUID,
    user = Depends(require_permission("config:update")),
    use_case = Depends(get_retry_sync_job_use_case),
):
    """Manual retry — สำหรับ dead letter"""
    ...


@router.get("/jobs/dead-letters")
async def list_dead_letters(
    user = Depends(require_permission("config:read")),
):
    """ดู dead letter ทั้งหมด — ต้อง manual"""
    ...


# ---------- Mappings ----------
@router.get("/mappings")
async def list_mappings(
    entity_type: str | None = Query(None),
    user = Depends(require_permission("config:read")),
):
    """ดู mapping ระหว่าง internal ↔ external"""
    ...


# ---------- Reconciliation ----------
@router.post("/reconcile")
async def reconcile(
    body: ReconcileRequest,
    user = Depends(require_permission("config:read")),
    use_case = Depends(get_reconcile_use_case),
):
    """เทียบ DB ↔ Cloud"""
    return await use_case.execute(ReconcileCommand(
        company_id=body.company_id,
        from_date=body.from_date,
        to_date=body.to_date,
    ))


# ---------- Providers ----------
@router.get("/providers")
async def list_providers(user = Depends(require_permission("config:read"))):
    ...


@router.post("/providers/{provider}/connect")
async def connect_provider(
    provider: str,
    body: ConnectProviderRequest,
    user = Depends(require_permission("config:update")),
):
    """ตั้งค่า credential ของ provider"""
    ...


@router.post("/providers/{provider}/health-check")
async def health_check(
    provider: str,
    user = Depends(require_permission("config:read")),
):
    """ทดสอบ connection"""
    ...
```

## 6.2.12 Folder Structure

```text
app/modules/accounting_gateway/
├── domain/
│   ├── entities.py            # SyncJob, SyncMappingEntry
│   ├── value_objects.py       # SyncProvider, SyncEntityType, SyncStatus, ExternalRef
│   ├── events.py              # SyncJobCreated, SyncJobSucceeded, ...
│   └── errors.py
├── application/
│   ├── interfaces.py          # IAccountingProvider, ISyncJobRepository
│   ├── use_cases.py           # EnqueueSync, ProcessSyncJobWorker, Retry, Reconcile
│   └── handlers.py            # InvoiceIssuedSyncHandler, PaymentReceivedSyncHandler
├── infrastructure/
│   ├── models.py              # SyncJobModel, SyncMappingModel, ProviderCredentialModel
│   ├── repositories.py        # PostgresSyncJobRepository, PostgresSyncMappingRepository
│   ├── providers/
│   │   ├── base.py            # BaseHttpProvider
│   │   ├── flowaccount.py     # FlowAccountProvider
│   │   ├── peak.py            # PeakProvider
│   │   ├── xero.py            # XeroProvider
│   │   └── noop.py            # NoopProvider (dev)
│   ├── token_store.py         # encrypted credential storage
│   └── worker.py              # SyncWorker loop
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── test_enqueue.py          # event_id unique
    ├── test_worker_retry.py     # backoff + dead letter
    ├── test_idempotency.py      # push ซ้ำ → mapping replay
    ├── test_provider_mock.py
    └── integration/
        └── test_reconcile.py    # DB ↔ mock cloud
```

## 6.2.13 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 2 (implement Worker) |
| **DoD** | ✅ event_id unique — ห้ามสร้าง job ซ้ำ<br>✅ retry + exponential backoff<br>✅ dead letter + manual retry<br>✅ idempotency: push ซ้ำ → replay<br>✅ mapping ระหว่าง internal ↔ external<br>✅ reconcile DB ↔ Cloud<br>✅ provider abstraction (FlowAccount, PEAK, ...)<br>✅ credential encrypted at rest |

---

# 📊 PART 6 — สรุป

## Dependency Graph

```text
                    ┌────────────────────┐
                    │   core/events (L0) │  ← outbox + worker
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌──────────────────┐
│   invoice     │    │   payment     │    │  ledger (Part 5) │
│   (Part 5)    │    │               │    │                  │
└───────┬───────┘    └───────┬───────┘    └────────┬─────────┘
        │                    │                     │
        │ InvoiceIssued      │ PaymentReceived     │ LedgerPosted
        ▼                    ▼                     ▼
   ┌──────────────────────────────────────────────────────┐
   │              accounting_gateway                       │
   │  enqueue → worker → provider → cloud                  │
   │  + mapping + reconciliation                           │
   └──────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Thai Cloud         │
                    │ Accounting API     │
                    └────────────────────┘
```

## Integration Flow (ครบทั้ง Money Path)

```text
1. Invoice.issue() → InvoiceIssued
   ├─ Ledger handler → post journal (Dr. AR / Cr. Revenue / Cr. VAT)
   └─ Gateway handler → enqueue SyncJob(TAX_INVOICE, provider)
       └─ Worker → push → FlowAccount → ExternalRef → mapping

2. Payment.receive() → PaymentReceived
   ├─ Ledger handler → post journal (Dr. Cash / Dr. WHT / Cr. AR)
   ├─ Invoice handler → mark_invoice_paid
   └─ Gateway handler → enqueue SyncJob(PAYMENT, provider)
       └─ Worker → push → FlowAccount

3. Payment.refund() → PaymentRefunded
   ├─ Ledger handler → reverse original journal
   └─ Gateway handler → enqueue SyncJob(PAYMENT, provider, retract)

4. Invoice.cancel() → InvoiceCancelled
   ├─ Ledger handler → reverse original journal
   └─ Gateway handler → enqueue SyncJob(TAX_INVOICE, provider, cancel)

5. Reconcile (scheduled daily)
   └─ ReconcileUseCase → เทียบ DB ↔ Cloud → Discrepancy report
```

## Checklist รวม Part 6

```text
┌─────────────────────────────────────────────────────────────────┐
│  MONEY PATH COMPLETION — FINAL CHECKLIST                        │
├─────────────────────────────────────────────────────────────────┤
│  payment                                                        │
│   □ allocate ไม่เกิน invoice remaining                         │
│   □ partial payment + multi-invoice allocation                 │
│   □ receive → post ledger อัตโนมัติ                            │
│   □ WHT deduction ทำงาน                                        │
│   □ Refund → reversal journal                                  │
│   □ Idempotency: ยิงซ้ำ 100 → 1                                │
│   □ verify_totals ผ่านทุกครั้ง                                 │
│   □ Bank account / cheque info เก็บถูก                          │
├─────────────────────────────────────────────────────────────────┤
│  accounting_gateway                                             │
│   □ event_id unique — ห้ามสร้าง job ซ้ำ                        │
│   □ Outbox pattern ทำงาน                                        │
│   □ retry + exponential backoff                                │
│   □ dead letter + manual retry                                 │
│   □ idempotency: push ซ้ำ → mapping replay                     │
│   □ mapping ระหว่าง internal ↔ external                        │
│   □ reconcile DB ↔ Cloud                                       │
│   □ provider abstraction (FlowAccount, PEAK, ...)              │
│   □ credential encrypted at rest                                │
│   □ worker health check                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics ที่ต้องติดตาม

| Metric | Target | ตรวจโดย |
|--------|--------|---------|
| Payment allocation overflow | 0 | domain invariant |
| Sync job success rate | ≥ 99.9% | monitoring |
| Sync job dead letter count | 0 | reconciliation |
| Cloud sync latency | < 30s (p95) | monitoring |
| DB ↔ Cloud discrepancy | 0 | reconcile |
| Double-push (same event) | 0 | event_id unique |
| WHT calculation error | 0 | property test |
| Refund → reversal missing | 0 | reconciliation |

## ลำดับการ Implement

```text
Week 1:
  Day 1-3: payment domain (entities, allocation, events)
  Day 4-5: payment use cases + ledger handler
  Day 6-7: payment infrastructure + API

Week 2:
  Day 8-9:  accounting_gateway domain + enqueue
  Day 10-11: provider abstraction + FlowAccount impl
  Day 12-13: worker + retry + dead letter
  Day 14: reconcile + integration test
  Day 15: E2E test (invoice → payment → cloud)
```

---

 