# 📕 PART 5 — Money Path Core Modules

> **Layer 2: Money Path** — 3 modules ที่เป็นหัวใจของระบบ
> `invoice` · `ledger` · `tax`

---

## 5.0 ภาพรวม Money Path

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 2: MONEY PATH CORE                                  │
│                                                                              │
│   ┌──────────────┐                                                           │
│   │  order       │  ← Part 12 (จะกล่าวภายหลัง)                              │
│   └──────┬───────┘                                                           │
│          │ OrderConfirmed                                                    │
│          ▼                                                                   │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│   │   invoice    │─────►│    tax       │─────►│   ledger     │             │
│   │              │      │  (VAT, WHT)  │      │ (double-entry)│             │
│   └──────┬───────┘      └──────────────┘      └──────┬───────┘             │
│          │                                            │                     │
│          │ InvoiceIssued                     LedgerPosted                   │
│          ▼                                            ▼                     │
│   ┌──────────────────────────────────────────────────────────┐             │
│   │              payment  │  accounting_gateway              │             │
│   │              (Part 6) │  (Part 6)                        │             │
│   └──────────────────────────────────────────────────────────┘             │
│                                                                              │
│   Money Path Invariants:                                                    │
│   • Invoice.total = Σ(lines) + VAT − discount                              │
│   • Σ(debit) = Σ(credit)                                                    │
│   • CANCELLED invoice → reversal ledger entry                              │
│   • Invoice number unique per company per year                             │
│   • ทุก action → audit + idempotency                                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Money Path Flow (ละเอียด):**

```text
   Order
     │ OrderConfirmed
     ▼
┌─────────────────┐
│  IssueInvoice   │  ①  Idempotency key
│                 │  ②  SELECT FOR UPDATE (invoice number)
│                 │  ③  Compute VAT via Tax module
│   ┌─────────┐   │  ④  Persist invoice + lines
   │ Invoice │───┼─►⑤  Read-back verify
   └────┬────┘   │  ⑥  Publish InvoiceIssued (outbox)
        │        │  ⑦  Audit log
        │        └───────────────────────────────────
        │
        │ InvoiceIssued event
        ▼
┌─────────────────┐
│  PostLedger     │  ①  Build JournalEntry (double-entry)
│                 │  ②  Validate Σdebit = Σcredit
│   ┌─────────┐   │  ③  Persist journal + lines
   │ Ledger  │◄──┼──④  Read-back verify
   └─────────┘   │  ⑤  Publish LedgerPosted
                 │  ⑥  Audit log
                 └───────────────────────────────────
        │
        │ LedgerPosted event
        ▼
┌─────────────────┐
│  SyncToCloud    │  (Part 6 — accounting_gateway)
└─────────────────┘
```

---

# 🧩 Module 5.1 — `invoice`

## 5.1.1 Purpose & Scope

**Purpose:** ออกใบแจ้งหนี้/ใบกำกับภาษีที่ถูกต้องตามกฎหมายไทย มีเลขรันต่อปี ไม่ซ้ำ คำนวณ VAT แม่นระดับสตางค์ และรองรับการยกเลิก/แก้ไขที่ต้อง reverse ledger

**Scope:**
- ✅ Invoice (ใบแจ้งหนี้) + InvoiceLine
- ✅ Tax Invoice (ใบกำกับภาษี) — แยกหรือรวมกับ invoice
- ✅ Invoice numbering (per company per year)
- ✅ VAT calculation via `tax` module
- ✅ Discount (line-level + invoice-level)
- ✅ Cancel + Amendment (reversal)
- ✅ Credit Note / Debit Note
- ✅ PDF generation
- ✅ Multi-currency (optional)
- ❌ ไม่ post ledger (ledger module ทำ)
- ❌ ไม่รับชำระ (payment module ทำ)
- ❌ ไม่ sync cloud (accounting_gateway ทำ)

## 5.1.2 Domain Model

```python
# app/modules/invoice/domain/value_objects.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re

from app.core.money.domain.value_objects import Money, Currency
from app.core.money.domain.vat import VatRate, VatBreakdown


@dataclass(frozen=True, slots=True)
class InvoiceNumber:
    """
    เลขใบแจ้งหนี้
    Format: {PREFIX}-{YYYY}-{NNNNN}
    เช่น INV-2026-00001

    Invariants:
    - unique ต่อ company ต่อปี
    - immutable หลังสร้าง
    """
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z]{2,10}-\d{4}-\d{5,7}$", self.value):
            raise ValueError(f"InvoiceNumber ไม่ถูกต้อง: {self.value}")

    @property
    def year(self) -> int:
        return int(self.value.split("-")[1])

    @property
    def sequence(self) -> int:
        return int(self.value.split("-")[2])

    @classmethod
    def build(cls, prefix: str, year: int, seq: int) -> "InvoiceNumber":
        return cls(f"{prefix}-{year}-{seq:05d}")


@dataclass(frozen=True, slots=True)
class TaxInvoiceNumber:
    """เลขใบกำกับภาษี — อาจเหมือนหรือต่างจาก invoice number"""
    value: str


@dataclass(frozen=True, slots=True)
class InvoiceLineData:
    """
    ข้อมูล line ก่อนสร้าง entity
    """
    product_id: str
    product_code: str
    description: str
    quantity: Decimal
    unit: str                       # "kg", "pcs", "box"
    unit_price: Money
    discount_pct: Decimal = Decimal("0")
    discount_amount: Money | None = None
    vat_rate: VatRate | None = None
    lot_id: str | None = None       # traceability
    note: str | None = None


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"              # ออกแล้ว รอชำระ
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    AMENDED = "amended"            # ถูกแทนที่ด้วยใบใหม่


class InvoiceType(str, Enum):
    INVOICE = "invoice"            # ใบแจ้งหนี้
    TAX_INVOICE = "tax_invoice"    # ใบกำกับภาษี
    RECEIPT = "receipt"            # ใบเสร็จรับเงิน
    CREDIT_NOTE = "credit_note"    # ใบลดหนี้
    DEBIT_NOTE = "debit_note"      # ใบเพิ่มหนี้


class PaymentTerm(str, Enum):
    CASH = "cash"
    NET_7 = "net_7"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    CUSTOM = "custom"

    def due_days(self, custom_days: int | None = None) -> int:
        if self == PaymentTerm.CASH:
            return 0
        if self == PaymentTerm.CUSTOM:
            return custom_days or 0
        return int(self.value.split("_")[1])


@dataclass(frozen=True, slots=True)
class CustomerSnapshot:
    """
    Snapshot ของลูกค้า ณ เวลาออก invoice
    — เก็บไว้เพื่อไม่ให้ใบเก่าเปลี่ยนตามข้อมูลลูกค้า
    """
    customer_id: str
    code: str
    name: str
    tax_id: str | None
    address: str
    branch_code: str | None       # "00000" = สำนักงานใหญ่
    phone: str | None
    email: str | None
```

```python
# app/modules/invoice/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.money.domain.value_objects import Money
from app.core.money.domain.vat import VatRate, VatCalculator, VatBreakdown, VatMode
from app.modules.invoice.domain.value_objects import (
    InvoiceNumber, TaxInvoiceNumber, InvoiceStatus, InvoiceType,
    PaymentTerm, CustomerSnapshot, InvoiceLineData,
)


@dataclass
class InvoiceLine:
    """
    Line ของ invoice — Entity

    Invariants:
    - quantity > 0
    - unit_price ≥ 0
    - discount_pct ∈ [0, 1]
    - line_total = (qty × unit_price) − discount
    - vat = line_total × vat_rate (ตาม mode)
    """
    id: UUID
    invoice_id: UUID
    line_number: int
    product_id: UUID
    product_code: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Money
    discount_pct: Decimal
    discount_amount: Money
    subtotal: Money                # qty × unit_price (ก่อน discount)
    net_amount: Money              # subtotal − discount
    vat_rate: VatRate
    vat_amount: Money
    total_with_vat: Money
    lot_id: UUID | None
    note: str | None

    @classmethod
    def create(
        cls,
        *,
        invoice_id: UUID,
        line_number: int,
        data: InvoiceLineData,
        default_vat: VatRate,
    ) -> "InvoiceLine":
        if data.quantity <= 0:
            raise ValueError("quantity ต้อง > 0")

        subtotal = data.unit_price * data.quantity

        if data.discount_amount is not None:
            discount = data.discount_amount
        elif data.discount_pct > 0:
            discount = Money(
                (subtotal.amount * data.discount_pct).quantize(Decimal("0.01")),
                subtotal.currency,
            )
        else:
            discount = Money.zero(subtotal.currency)

        if discount > subtotal:
            raise ValueError("discount มากกว่า subtotal")
        if data.discount_pct < 0 or data.discount_pct > 1:
            raise ValueError("discount_pct ต้องอยู่ 0-1")

        net_amount = subtotal - discount
        vat_rate = data.vat_rate or default_vat
        breakdown = VatCalculator.calculate(net_amount, vat_rate)

        return cls(
            id=uuid4(),
            invoice_id=invoice_id,
            line_number=line_number,
            product_id=UUID(data.product_id),
            product_code=data.product_code,
            description=data.description,
            quantity=data.quantity,
            unit=data.unit,
            unit_price=data.unit_price,
            discount_pct=data.discount_pct,
            discount_amount=discount,
            subtotal=subtotal,
            net_amount=net_amount,
            vat_rate=vat_rate,
            vat_amount=breakdown.vat,
            total_with_vat=breakdown.total,
            lot_id=UUID(data.lot_id) if data.lot_id else None,
            note=data.note,
        )


@dataclass
class Invoice:
    """
    Invoice — Aggregate Root

    Invariants (สำคัญมาก):
    1.  total = Σ(line.total_with_vat) − invoice_discount + shipping
    2.  subtotal = Σ(line.net_amount)
    3.  vat_total = Σ(line.vat_amount)
    4.  ISSUED แล้ว แก้ line ไม่ได้ (ต้อง cancel + ออกใหม่)
    5.  CANCELLED → ต้องมี reversal ledger entry
    6.  เลข invoice unique ต่อ company ต่อปี
    7.  due_date = issue_date + payment_term.due_days
    8.  status transitions ตาม state machine
    """
    id: UUID
    company_id: UUID
    branch_id: UUID | None
    invoice_number: InvoiceNumber
    tax_invoice_number: TaxInvoiceNumber | None
    invoice_type: InvoiceType
    status: InvoiceStatus

    # Customer
    customer: CustomerSnapshot
    # Reference
    order_id: UUID | None
    parent_invoice_id: UUID | None      # สำหรับ credit/debit note

    # Dates
    issue_date: date
    due_date: date
    payment_term: PaymentTerm
    custom_due_days: int | None

    # Currency
    currency: str                        # "THB"

    # Amounts
    subtotal: Money                      # Σ net_amount
    discount_total: Money                # line discount
    invoice_discount: Money              # invoice-level discount
    shipping_fee: Money
    vat_total: Money
    withholding_tax: Money               # WHT (optional)
    grand_total: Money                   # subtotal − invoice_discount + shipping + vat − wht

    # Meta
    note: str | None
    reference: str | None                # เลขอ้างอิงลูกค้า
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    issued_at: datetime | None
    cancelled_at: datetime | None
    cancel_reason: str | None

    _lines: list[InvoiceLine] = field(default_factory=list, repr=False)

    # ---------- Factory ----------

    @classmethod
    def create_draft(
        cls,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        invoice_type: InvoiceType,
        customer: CustomerSnapshot,
        issue_date: date,
        payment_term: PaymentTerm,
        currency: str = "THB",
        order_id: UUID | None = None,
        reference: str | None = None,
        note: str | None = None,
        created_by: UUID,
        custom_due_days: int | None = None,
    ) -> "Invoice":
        """
        สร้าง draft — ยังไม่มีเลข invoice
        เลขจะออกตอน issue()
        """
        due_days = payment_term.due_days(custom_due_days)
        due_date = date.fromordinal(issue_date.toordinal() + due_days)

        zero = Money.zero()
        return cls(
            id=uuid4(),
            company_id=company_id,
            branch_id=branch_id,
            invoice_number=None,  # type: ignore  # จะตั้งตอน issue
            tax_invoice_number=None,
            invoice_type=invoice_type,
            status=InvoiceStatus.DRAFT,
            customer=customer,
            order_id=order_id,
            parent_invoice_id=None,
            issue_date=issue_date,
            due_date=due_date,
            payment_term=payment_term,
            custom_due_days=custom_due_days,
            currency=currency,
            subtotal=zero,
            discount_total=zero,
            invoice_discount=zero,
            shipping_fee=zero,
            vat_total=zero,
            withholding_tax=zero,
            grand_total=zero,
            note=note,
            reference=reference,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            issued_at=None,
            cancelled_at=None,
            cancel_reason=None,
            _lines=[],
        )

    # ---------- Mutations ----------

    def add_line(self, data: InvoiceLineData, default_vat: VatRate) -> InvoiceLine:
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError(
                f"แก้ line ไม่ได้ — invoice อยู่สถานะ {self.status.value} "
                "(ต้อง cancel + ออกใหม่)"
            )
        line = InvoiceLine.create(
            invoice_id=self.id,
            line_number=len(self._lines) + 1,
            data=data,
            default_vat=default_vat,
        )
        self._lines.append(line)
        self._recalculate()
        return line

    def remove_line(self, line_id: UUID) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("แก้ line ไม่ได้ — ต้อง cancel + ออกใหม่")
        self._lines = [ln for ln in self._lines if ln.id != line_id]
        for i, ln in enumerate(self._lines, start=1):
            ln.line_number = i
        self._recalculate()

    def set_invoice_discount(self, amount: Money) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("แก้ discount ไม่ได้")
        self.invoice_discount = amount
        self._recalculate()

    def set_shipping_fee(self, amount: Money) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("แก้ shipping ไม่ได้")
        self.shipping_fee = amount
        self._recalculate()

    def set_withholding_tax(self, amount: Money) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("แก้ WHT ไม่ได้")
        self.withholding_tax = amount
        self._recalculate()

    # ---------- Lifecycle ----------

    def issue(self, invoice_number: InvoiceNumber) -> None:
        """
        ออก invoice — เปลี่ยน status DRAFT → ISSUED
        ต้องมีอย่างน้อย 1 line
        """
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError(f"ออก invoice ไม่ได้ — status = {self.status.value}")
        if not self._lines:
            raise ValueError("ต้องมีอย่างน้อย 1 line")

        self.invoice_number = invoice_number
        self.status = InvoiceStatus.ISSUED
        self.issued_at = datetime.utcnow()
        self.updated_at = self.issued_at

    def mark_paid(self, paid_amount: Money) -> None:
        """เรียกจาก payment module"""
        if self.status not in (InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID):
            raise ValueError(f"mark_paid ไม่ได้ — status = {self.status.value}")
        if paid_amount >= self.grand_total:
            self.status = InvoiceStatus.PAID
        elif paid_amount > Money.zero():
            self.status = InvoiceStatus.PARTIALLY_PAID
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: str) -> None:
        """ยกเลิก invoice → ต้อง reverse ledger"""
        if self.status == InvoiceStatus.CANCELLED:
            raise ValueError("invoice ถูกยกเลิกแล้ว")
        if self.status == InvoiceStatus.PAID:
            raise ValueError("ยกเลิก invoice ที่ชำระแล้วไม่ได้ — ต้องออก credit note")
        self.status = InvoiceStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.cancel_reason = reason
        self.updated_at = self.cancelled_at

    # ---------- Private ----------

    def _recalculate(self) -> None:
        """
        คำนวณยอดใหม่จาก lines
        ⚠️ ต้องเรียกทุกครั้งที่ lines/discount/shipping เปลี่ยน
        """
        if not self._lines:
            zero = Money.zero()
            self.subtotal = zero
            self.discount_total = zero
            self.vat_total = zero
            self.grand_total = zero
            return

        self.subtotal = sum((ln.net_amount for ln in self._lines), Money.zero())
        self.discount_total = sum((ln.discount_amount for ln in self._lines), Money.zero())
        self.vat_total = sum((ln.vat_amount for ln in self._lines), Money.zero())

        # grand = subtotal − invoice_discount + shipping + vat − wht
        grand = (
            self.subtotal
            - self.invoice_discount
            + self.shipping_fee
            + self.vat_total
            - self.withholding_tax
        )
        self.grand_total = grand
        self.updated_at = datetime.utcnow()

    # ---------- Read-only ----------

    @property
    def lines(self) -> list[InvoiceLine]:
        return list(self._lines)

    def verify_totals(self) -> None:
        """
        🛡️ Read-back verification
        ตรวจว่า total ที่คำนวณตรงกับ sum ของ lines
        """
        expected_subtotal = sum((ln.net_amount for ln in self._lines), Money.zero())
        expected_vat = sum((ln.vat_amount for ln in self._lines), Money.zero())
        expected_grand = (
            expected_subtotal
            - self.invoice_discount
            + self.shipping_fee
            + expected_vat
            - self.withholding_tax
        )
        if self.subtotal != expected_subtotal:
            raise ValueError(f"subtotal mismatch: {self.subtotal} ≠ {expected_subtotal}")
        if self.vat_total != expected_vat:
            raise ValueError(f"vat mismatch: {self.vat_total} ≠ {expected_vat}")
        if self.grand_total != expected_grand:
            raise ValueError(f"grand mismatch: {self.grand_total} ≠ {expected_grand}")
```

## 5.1.3 Domain Events

```python
# app/modules/invoice/domain/events.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Any

from app.core.events.domain.entities import DomainEvent


@dataclass(frozen=True, slots=True)
class InvoiceIssued(DomainEvent):
    """ออก invoice สำเร็จ — trigger ledger"""
    @classmethod
    def create(
        cls, *, invoice_id: UUID, company_id: UUID,
        invoice_number: str, customer_id: str, grand_total: str,
        currency: str, issue_date: str, due_date: str,
        lines: list[dict[str, Any]],
        actor_id: UUID | None = None, correlation_id: UUID | None = None,
    ) -> "InvoiceIssued":
        return cls(
            event_id=uuid4(),
            event_type="invoice.issued",
            aggregate_type="invoice",
            aggregate_id=invoice_id,
            company_id=company_id,
            payload={
                "invoice_number": invoice_number,
                "customer_id": customer_id,
                "grand_total": grand_total,
                "currency": currency,
                "issue_date": issue_date,
                "due_date": due_date,
                "lines": lines,
            },
            occurred_at=datetime.utcnow(),
            actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=None,
        )


@dataclass(frozen=True, slots=True)
class InvoiceCancelled(DomainEvent):
    """ยกเลิก invoice — trigger reversal"""
    ...


@dataclass(frozen=True, slots=True)
class InvoiceAmended(DomainEvent):
    """แก้ไข invoice — trigger amendment ledger"""
    ...


@dataclass(frozen=True, slots=True)
class InvoicePaid(DomainEvent):
    """ชำระครบ — trigger payment allocation"""
    ...
```

## 5.1.4 Application — Interfaces

```python
# app/modules/invoice/application/interfaces.py

from typing import Protocol
from uuid import UUID
from datetime import date

from app.modules.invoice.domain.entities import Invoice, InvoiceLine
from app.modules.invoice.domain.value_objects import InvoiceNumber


class IInvoiceRepository(Protocol):
    async def get_by_id(self, invoice_id: UUID) -> Invoice | None: ...
    async def get_by_number(
        self, company_id: UUID, invoice_number: str,
    ) -> Invoice | None: ...
    async def exists_by_number(
        self, company_id: UUID, invoice_number: str,
    ) -> bool: ...
    async def list_by_company(
        self, company_id: UUID, *,
        status: str | None = None,
        customer_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 100, offset: int = 0,
    ) -> list[Invoice]: ...
    async def save(self, invoice: Invoice) -> None: ...
    async def update(self, invoice: Invoice) -> None: ...
    async def get_with_lines(self, invoice_id: UUID) -> Invoice | None: ...


class IInvoiceNumberSequence(Protocol):
    """
    Sequence generator — ต้อง atomic
    ใช้ SELECT FOR UPDATE เพื่อกัน concurrent
    """
    async def next_number(
        self, *, company_id: UUID, prefix: str, year: int,
    ) -> InvoiceNumber: ...


class IPdfRenderer(Protocol):
    """Render invoice เป็น PDF"""
    async def render(self, invoice: Invoice) -> bytes: ...
```

## 5.1.5 Application — Use Cases

```python
# app/modules/invoice/application/use_cases.py

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.core.money.domain.value_objects import Money
from app.core.money.domain.vat import VatRate, VatMode
from app.modules.invoice.domain.entities import Invoice
from app.modules.invoice.domain.value_objects import (
    InvoiceType, PaymentTerm, CustomerSnapshot, InvoiceLineData,
)
from app.modules.invoice.domain.events import InvoiceIssued, InvoiceCancelled
from app.modules.invoice.application.interfaces import (
    IInvoiceRepository, IInvoiceNumberSequence,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.core.config.application.use_cases import GetConfigUseCase
from app.core.tenant_context.domain.context import get_company_id


# ============================================================
# 1. Create Draft
# ============================================================

@dataclass
class CreateDraftCommand:
    customer: CustomerSnapshot
    issue_date: date
    payment_term: PaymentTerm
    invoice_type: InvoiceType = InvoiceType.TAX_INVOICE
    branch_id: UUID | None = None
    order_id: UUID | None = None
    reference: str | None = None
    note: str | None = None
    actor_id: UUID = None  # type: ignore
    custom_due_days: int | None = None


class CreateInvoiceDraftUseCase:
    def __init__(self, invoices: IInvoiceRepository, uow) -> None:
        self.invoices = invoices
        self.uow = uow

    async def execute(self, cmd: CreateDraftCommand) -> Invoice:
        company_id = get_company_id()
        invoice = Invoice.create_draft(
            company_id=company_id,
            branch_id=cmd.branch_id,
            invoice_type=cmd.invoice_type,
            customer=cmd.customer,
            issue_date=cmd.issue_date,
            payment_term=cmd.payment_term,
            order_id=cmd.order_id,
            reference=cmd.reference,
            note=cmd.note,
            created_by=cmd.actor_id,
            custom_due_days=cmd.custom_due_days,
        )
        async with self.uow.transaction():
            await self.invoices.save(invoice)
        return invoice


# ============================================================
# 2. Add Line
# ============================================================

@dataclass
class AddLineCommand:
    invoice_id: UUID
    line_data: InvoiceLineData
    actor_id: UUID


class AddInvoiceLineUseCase:
    def __init__(
        self, invoices: IInvoiceRepository,
        config: GetConfigUseCase, uow,
    ):
        self.invoices = invoices
        self.config = config
        self.uow = uow

    async def execute(self, cmd: AddLineCommand) -> Invoice:
        invoice = await self.invoices.get_with_lines(cmd.invoice_id)
        if not invoice:
            raise ValueError("ไม่พบ invoice")

        # default VAT จาก config
        vat_rate_value = await self.config.get_decimal(
            invoice.company_id, "tax.vat_standard_rate",
        )
        default_vat = VatRate(rate=vat_rate_value, mode=VatMode.EXCLUSIVE)

        invoice.add_line(cmd.line_data, default_vat)

        async with self.uow.transaction():
            await self.invoices.update(invoice)
        return invoice


# ============================================================
# 3. Issue Invoice (CORE)
# ============================================================

@dataclass
class IssueInvoiceCommand:
    invoice_id: UUID
    actor_id: UUID
    idempotency_key: str


class IssueInvoiceUseCase:
    """
    🎯 หัวใจของ Money Path

    Flow:
    1. Idempotency check (middleware/guard)
    2. โหลด invoice + lines
    3. ตรวจ status = DRAFT
    4. คำนวณ totals ใหม่ (verify)
    5. ออกเลข invoice (SELECT FOR UPDATE)
    6. issue() → status ISSUED
    7. Persist (transaction เดียว)
    8. Read-back verify
    9. Audit + Publish event (outbox)
    """

    def __init__(
        self,
        invoices: IInvoiceRepository,
        sequence: IInvoiceNumberSequence,
        config: GetConfigUseCase,
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        idempotency,  # IdempotencyGuard
        uow,
    ) -> None:
        self.invoices = invoices
        self.sequence = sequence
        self.config = config
        self.audit = audit
        self.publish = publish
        self.idempotency = idempotency
        self.uow = uow

    async def execute(self, cmd: IssueInvoiceCommand) -> Invoice:
        company_id = get_company_id()

        # --- Idempotency wrapper ---
        async def _do() -> tuple[int, dict]:
            return await self._issue(cmd)

        result = await self.idempotency.execute(
            key=cmd.idempotency_key,
            company_id=company_id,
            endpoint=f"/api/v1/invoices/{cmd.invoice_id}/issue",
            method="POST",
            body={"invoice_id": str(cmd.invoice_id)},
            scope=IdempotencyScope.PERMANENT,
            action=_do,
        )
        # result.body = serialized invoice
        return await self.invoices.get_by_id(cmd.invoice_id)

    async def _issue(self, cmd: IssueInvoiceCommand) -> tuple[int, dict]:
        async with self.uow.transaction():
            # 1. โหลด
            invoice = await self.invoices.get_with_lines(cmd.invoice_id)
            if not invoice:
                raise ValueError("ไม่พบ invoice")

            # 2. ตรวจ status
            if invoice.status.value != "draft":
                raise ValueError(f"ออกไม่ได้ — status = {invoice.status.value}")

            # 3. Verify totals (safety)
            invoice.verify_totals()

            # 4. ออกเลข invoice
            prefix = await self.config.execute(
                invoice.company_id, "invoice.number_format", "INV-{YYYY}-{NNNNN}",
            )
            year = invoice.issue_date.year
            number = await self.sequence.next_number(
                company_id=invoice.company_id,
                prefix="INV",
                year=year,
            )

            # 5. Issue
            invoice.issue(number)

            # 6. Persist
            await self.invoices.update(invoice)

            # 7. Read-back verify
            persisted = await self.invoices.get_with_lines(invoice.id)
            if not persisted:
                raise RuntimeError("read-back failed: ไม่พบ invoice หลัง save")
            persisted.verify_totals()
            if persisted.invoice_number != invoice.invoice_number:
                raise RuntimeError("read-back: invoice_number mismatch")
            if persisted.grand_total != invoice.grand_total:
                raise RuntimeError(
                    f"read-back: grand_total mismatch "
                    f"{persisted.grand_total} ≠ {invoice.grand_total}"
                )

            # 8. Audit
            await self.audit.execute(RecordAuditCommand(
                company_id=invoice.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.INVOICE_ISSUED,
                entity_type="invoice",
                entity_id=invoice.id,
                before_state={"status": "draft"},
                after_state={
                    "status": "issued",
                    "invoice_number": str(invoice.invoice_number),
                    "grand_total": str(invoice.grand_total),
                },
            ))

            # 9. Publish event (outbox)
            await self.publish.execute(InvoiceIssued.create(
                invoice_id=invoice.id,
                company_id=invoice.company_id,
                invoice_number=str(invoice.invoice_number),
                customer_id=invoice.customer.customer_id,
                grand_total=str(invoice.grand_total.amount),
                currency=invoice.currency,
                issue_date=invoice.issue_date.isoformat(),
                due_date=invoice.due_date.isoformat(),
                lines=[
                    {
                        "product_id": str(ln.product_id),
                        "net_amount": str(ln.net_amount.amount),
                        "vat_amount": str(ln.vat_amount.amount),
                        "total": str(ln.total_with_vat.amount),
                    }
                    for ln in invoice.lines
                ],
                actor_id=cmd.actor_id,
            ))

        return 201, {"id": str(invoice.id), "invoice_number": str(invoice.invoice_number)}


# ============================================================
# 4. Cancel Invoice
# ============================================================

@dataclass
class CancelInvoiceCommand:
    invoice_id: UUID
    reason: str
    actor_id: UUID
    idempotency_key: str


class CancelInvoiceUseCase:
    """
    ยกเลิก invoice → trigger reversal ledger

    ห้าม cancel ถ้า:
    - ชำระแล้ว (ต้อง credit note)
    - cancel แล้ว
    """

    def __init__(
        self, invoices, audit, publish, idempotency, uow,
    ):
        ...

    async def execute(self, cmd: CancelInvoiceCommand) -> Invoice:
        async with self.uow.transaction():
            invoice = await self.invoices.get_with_lines(cmd.invoice_id)
            if not invoice:
                raise ValueError("ไม่พบ invoice")

            before_status = invoice.status.value
            invoice.cancel(cmd.reason)
            await self.invoices.update(invoice)

            # Read-back
            persisted = await self.invoices.get_by_id(invoice.id)
            if persisted.status.value != "cancelled":
                raise RuntimeError("read-back: status ไม่เปลี่ยน")

            await self.audit.execute(RecordAuditCommand(
                company_id=invoice.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.INVOICE_CANCELLED,
                entity_type="invoice",
                entity_id=invoice.id,
                before_state={"status": before_status},
                after_state={"status": "cancelled", "reason": cmd.reason},
            ))

            await self.publish.execute(InvoiceCancelled.create(
                invoice_id=invoice.id,
                company_id=invoice.company_id,
                payload={"reason": cmd.reason},
                actor_id=cmd.actor_id,
            ))
        return invoice
```

## 5.1.6 Infrastructure — Models

```python
# app/modules/invoice/infrastructure/models.py

from sqlalchemy import (
    Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base


class InvoiceModel(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("company_id", "invoice_number", name="uq_inv_company_number"),
        Index("ix_inv_company_status_date", "company_id", "status", "issue_date"),
        Index("ix_inv_customer", "company_id", "customer_id"),
        Index("ix_inv_due_date", "company_id", "due_date"),
        Index("ix_inv_order", "order_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    branch_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    invoice_number: Mapped[str | None] = mapped_column(String(30))
    tax_invoice_number: Mapped[str | None] = mapped_column(String(30))
    invoice_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    # Customer snapshot
    customer_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    customer_code: Mapped[str] = mapped_column(String(50))
    customer_name: Mapped[str] = mapped_column(String(255))
    customer_tax_id: Mapped[str | None] = mapped_column(String(13))
    customer_address: Mapped[str] = mapped_column(Text)
    customer_branch_code: Mapped[str | None] = mapped_column(String(10))
    customer_phone: Mapped[str | None] = mapped_column(String(20))
    customer_email: Mapped[str | None] = mapped_column(String(255))

    order_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    parent_invoice_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("invoices.id"),
    )

    issue_date: Mapped[Date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Date] = mapped_column(Date, nullable=False)
    payment_term: Mapped[str] = mapped_column(String(20), nullable=False)
    custom_due_days: Mapped[int | None] = mapped_column(Integer)

    currency: Mapped[str] = mapped_column(String(3), default="THB")

    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    discount_total: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    invoice_discount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    shipping_fee: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    vat_total: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    withholding_tax: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    grand_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    note: Mapped[str | None] = mapped_column(Text)
    reference: Mapped[str | None] = mapped_column(String(100))

    created_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[str | None] = mapped_column(Text)

    lines: Mapped[list["InvoiceLineModel"]] = relationship(
        "InvoiceLineModel", back_populates="invoice",
        cascade="all, delete-orphan", order_by="InvoiceLineModel.line_number",
    )


class InvoiceLineModel(Base):
    __tablename__ = "invoice_lines"
    __table_args__ = (
        Index("ix_invl_invoice", "invoice_id", "line_number", unique=True),
        Index("ix_invl_product", "product_id"),
        Index("ix_invl_lot", "lot_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    invoice_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"),
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_code: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20))

    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    vat_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    vat_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    vat_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_with_vat: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    lot_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    note: Mapped[str | None] = mapped_column(String(500))

    invoice: Mapped[InvoiceModel] = relationship("InvoiceModel", back_populates="lines")


class InvoiceNumberSequenceModel(Base):
    """Sequence สำหรับออกเลข invoice"""
    __tablename__ = "invoice_number_sequences"
    __table_args__ = (
        UniqueConstraint("company_id", "prefix", "year", name="uq_seq"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    current_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

## 5.1.7 Infrastructure — Repositories

```python
# app/modules/invoice/infrastructure/repositories.py

from uuid import UUID
from datetime import date

from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.money.domain.value_objects import Money, Currency
from app.core.money.domain.vat import VatRate, VatMode
from app.modules.invoice.domain.entities import Invoice, InvoiceLine
from app.modules.invoice.domain.value_objects import (
    InvoiceNumber, TaxInvoiceNumber, InvoiceStatus, InvoiceType,
    PaymentTerm, CustomerSnapshot,
)
from app.modules.invoice.infrastructure.models import (
    InvoiceModel, InvoiceLineModel, InvoiceNumberSequenceModel,
)


class PostgresInvoiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        stmt = select(InvoiceModel).where(InvoiceModel.id == invoice_id)
        m = (await self.session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_with_lines(self, invoice_id: UUID) -> Invoice | None:
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.id == invoice_id)
            .options(selectinload(InvoiceModel.lines))
        )
        m = (await self.session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(m, with_lines=True) if m else None

    async def exists_by_number(
        self, company_id: UUID, invoice_number: str,
    ) -> bool:
        stmt = select(exists().where(
            InvoiceModel.company_id == company_id,
            InvoiceModel.invoice_number == invoice_number,
        ))
        return (await self.session.execute(stmt)).scalar()

    async def save(self, invoice: Invoice) -> None:
        m = self._to_model(invoice)
        self.session.add(m)

    async def update(self, invoice: Invoice) -> None:
        m = await self.session.get(
            InvoiceModel, invoice.id, options=[selectinload(InvoiceModel.lines)],
        )
        if not m:
            raise LookupError(f"ไม่พบ invoice {invoice.id}")

        # update scalar fields
        m.status = invoice.status.value
        m.invoice_number = str(invoice.invoice_number) if invoice.invoice_number else None
        m.tax_invoice_number = (
            invoice.tax_invoice_number.value if invoice.tax_invoice_number else None
        )
        m.subtotal = invoice.subtotal.amount
        m.discount_total = invoice.discount_total.amount
        m.invoice_discount = invoice.invoice_discount.amount
        m.shipping_fee = invoice.shipping_fee.amount
        m.vat_total = invoice.vat_total.amount
        m.withholding_tax = invoice.withholding_tax.amount
        m.grand_total = invoice.grand_total.amount
        m.updated_at = invoice.updated_at
        m.issued_at = invoice.issued_at
        m.cancelled_at = invoice.cancelled_at
        m.cancel_reason = invoice.cancel_reason

        # lines: replace all (draft-only mutation)
        m.lines.clear()
        for ln in invoice.lines:
            m.lines.append(self._line_to_model(ln))

    @staticmethod
    def _to_entity(m: InvoiceModel, *, with_lines: bool = False) -> Invoice:
        lines: list[InvoiceLine] = []
        if with_lines:
            lines = [PostgresInvoiceRepository._line_to_entity(ln) for ln in m.lines]

        return Invoice(
            id=m.id,
            company_id=m.company_id,
            branch_id=m.branch_id,
            invoice_number=InvoiceNumber(m.invoice_number) if m.invoice_number else None,
            tax_invoice_number=(
                TaxInvoiceNumber(m.tax_invoice_number) if m.tax_invoice_number else None
            ),
            invoice_type=InvoiceType(m.invoice_type),
            status=InvoiceStatus(m.status),
            customer=CustomerSnapshot(
                customer_id=str(m.customer_id),
                code=m.customer_code,
                name=m.customer_name,
                tax_id=m.customer_tax_id,
                address=m.customer_address,
                branch_code=m.customer_branch_code,
                phone=m.customer_phone,
                email=m.customer_email,
            ),
            order_id=m.order_id,
            parent_invoice_id=m.parent_invoice_id,
            issue_date=m.issue_date,
            due_date=m.due_date,
            payment_term=PaymentTerm(m.payment_term),
            custom_due_days=m.custom_due_days,
            currency=m.currency,
            subtotal=Money(m.subtotal, Currency(m.currency)),
            discount_total=Money(m.discount_total, Currency(m.currency)),
            invoice_discount=Money(m.invoice_discount, Currency(m.currency)),
            shipping_fee=Money(m.shipping_fee, Currency(m.currency)),
            vat_total=Money(m.vat_total, Currency(m.currency)),
            withholding_tax=Money(m.withholding_tax, Currency(m.currency)),
            grand_total=Money(m.grand_total, Currency(m.currency)),
            note=m.note,
            reference=m.reference,
            created_by=m.created_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
            issued_at=m.issued_at,
            cancelled_at=m.cancelled_at,
            cancel_reason=m.cancel_reason,
            _lines=lines,
        )

    @staticmethod
    def _line_to_entity(m: InvoiceLineModel) -> InvoiceLine:
        return InvoiceLine(
            id=m.id,
            invoice_id=m.invoice_id,
            line_number=m.line_number,
            product_id=m.product_id,
            product_code=m.product_code,
            description=m.description,
            quantity=m.quantity,
            unit=m.unit,
            unit_price=Money(m.unit_price),
            discount_pct=m.discount_pct,
            discount_amount=Money(m.discount_amount),
            subtotal=Money(m.subtotal),
            net_amount=Money(m.net_amount),
            vat_rate=VatRate(rate=m.vat_rate, mode=VatMode(m.vat_mode)),
            vat_amount=Money(m.vat_amount),
            total_with_vat=Money(m.total_with_vat),
            lot_id=m.lot_id,
            note=m.note,
        )

    @staticmethod
    def _to_model(inv: Invoice) -> InvoiceModel:
        m = InvoiceModel(
            id=inv.id,
            company_id=inv.company_id,
            branch_id=inv.branch_id,
            invoice_number=str(inv.invoice_number) if inv.invoice_number else None,
            tax_invoice_number=(
                inv.tax_invoice_number.value if inv.tax_invoice_number else None
            ),
            invoice_type=inv.invoice_type.value,
            status=inv.status.value,
            customer_id=UUID(inv.customer.customer_id),
            customer_code=inv.customer.code,
            customer_name=inv.customer.name,
            customer_tax_id=inv.customer.tax_id,
            customer_address=inv.customer.address,
            customer_branch_code=inv.customer.branch_code,
            customer_phone=inv.customer.phone,
            customer_email=inv.customer.email,
            order_id=inv.order_id,
            parent_invoice_id=inv.parent_invoice_id,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            payment_term=inv.payment_term.value,
            custom_due_days=inv.custom_due_days,
            currency=inv.currency,
            subtotal=inv.subtotal.amount,
            discount_total=inv.discount_total.amount,
            invoice_discount=inv.invoice_discount.amount,
            shipping_fee=inv.shipping_fee.amount,
            vat_total=inv.vat_total.amount,
            withholding_tax=inv.withholding_tax.amount,
            grand_total=inv.grand_total.amount,
            note=inv.note,
            reference=inv.reference,
            created_by=inv.created_by,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
            issued_at=inv.issued_at,
            cancelled_at=inv.cancelled_at,
            cancel_reason=inv.cancel_reason,
        )
        m.lines = [PostgresInvoiceRepository._line_to_model(ln) for ln in inv.lines]
        return m

    @staticmethod
    def _line_to_model(ln: InvoiceLine) -> InvoiceLineModel:
        return InvoiceLineModel(
            id=ln.id,
            invoice_id=ln.invoice_id,
            line_number=ln.line_number,
            product_id=ln.product_id,
            product_code=ln.product_code,
            description=ln.description,
            quantity=ln.quantity,
            unit=ln.unit,
            unit_price=ln.unit_price.amount,
            discount_pct=ln.discount_pct,
            discount_amount=ln.discount_amount.amount,
            subtotal=ln.subtotal.amount,
            net_amount=ln.net_amount.amount,
            vat_rate=ln.vat_rate.rate,
            vat_mode=ln.vat_rate.mode.value,
            vat_amount=ln.vat_amount.amount,
            total_with_vat=ln.total_with_vat.amount,
            lot_id=ln.lot_id,
            note=ln.note,
        )


class PostgresInvoiceNumberSequence:
    """
    Sequence generator — atomic ด้วย SELECT FOR UPDATE
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def next_number(
        self, *, company_id: UUID, prefix: str, year: int,
    ) -> InvoiceNumber:
        stmt = (
            select(InvoiceNumberSequenceModel)
            .where(
                InvoiceNumberSequenceModel.company_id == company_id,
                InvoiceNumberSequenceModel.prefix == prefix,
                InvoiceNumberSequenceModel.year == year,
            )
            .with_for_update()
        )
        seq = (await self.session.execute(stmt)).scalar_one_or_none()

        if not seq:
            from uuid import uuid4
            seq = InvoiceNumberSequenceModel(
                id=uuid4(),
                company_id=company_id,
                prefix=prefix,
                year=year,
                current_value=0,
            )
            self.session.add(seq)
            await self.session.flush()

        seq.current_value += 1
        return InvoiceNumber.build(prefix=prefix, year=year, seq=seq.current_value)
```

## 5.1.8 Database Schema

```sql
CREATE TABLE invoices (
    id                    UUID PRIMARY KEY,
    company_id            UUID NOT NULL,
    branch_id             UUID,

    invoice_number        VARCHAR(30),
    tax_invoice_number    VARCHAR(30),
    invoice_type          VARCHAR(20) NOT NULL,
    status                VARCHAR(20) NOT NULL,

    customer_id           UUID NOT NULL,
    customer_code         VARCHAR(50) NOT NULL,
    customer_name         VARCHAR(255) NOT NULL,
    customer_tax_id       VARCHAR(13),
    customer_address      TEXT NOT NULL,
    customer_branch_code  VARCHAR(10),
    customer_phone        VARCHAR(20),
    customer_email        VARCHAR(255),

    order_id              UUID,
    parent_invoice_id     UUID REFERENCES invoices(id),

    issue_date            DATE NOT NULL,
    due_date              DATE NOT NULL,
    payment_term          VARCHAR(20) NOT NULL,
    custom_due_days       INT,

    currency              VARCHAR(3) NOT NULL DEFAULT 'THB',

    subtotal              NUMERIC(15,2) NOT NULL,
    discount_total        NUMERIC(15,2) NOT NULL DEFAULT 0,
    invoice_discount      NUMERIC(15,2) NOT NULL DEFAULT 0,
    shipping_fee          NUMERIC(15,2) NOT NULL DEFAULT 0,
    vat_total             NUMERIC(15,2) NOT NULL DEFAULT 0,
    withholding_tax       NUMERIC(15,2) NOT NULL DEFAULT 0,
    grand_total           NUMERIC(15,2) NOT NULL,

    note                  TEXT,
    reference             VARCHAR(100),

    created_by            UUID NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL,
    updated_at            TIMESTAMPTZ NOT NULL,
    issued_at             TIMESTAMPTZ,
    cancelled_at          TIMESTAMPTZ,
    cancel_reason         TEXT,

    CONSTRAINT uq_inv_company_number UNIQUE (company_id, invoice_number)
);

CREATE INDEX ix_inv_company_status_date ON invoices (company_id, status, issue_date DESC);
CREATE INDEX ix_inv_customer ON invoices (company_id, customer_id);
CREATE INDEX ix_inv_due_date ON invoices (company_id, due_date)
    WHERE status IN ('issued', 'partially_paid');
CREATE INDEX ix_inv_order ON invoices (order_id);

CREATE TABLE invoice_lines (
    id              UUID PRIMARY KEY,
    invoice_id      UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_number     INT NOT NULL,

    product_id      UUID NOT NULL,
    product_code    VARCHAR(50) NOT NULL,
    description     VARCHAR(500) NOT NULL,
    quantity        NUMERIC(15,3) NOT NULL,
    unit            VARCHAR(20) NOT NULL,

    unit_price      NUMERIC(15,2) NOT NULL,
    discount_pct    NUMERIC(5,4) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
    subtotal        NUMERIC(15,2) NOT NULL,
    net_amount      NUMERIC(15,2) NOT NULL,

    vat_rate        NUMERIC(5,4) NOT NULL,
    vat_mode        VARCHAR(20) NOT NULL,
    vat_amount      NUMERIC(15,2) NOT NULL,
    total_with_vat  NUMERIC(15,2) NOT NULL,

    lot_id          UUID,
    note            VARCHAR(500),

    UNIQUE (invoice_id, line_number)
);

CREATE INDEX ix_invl_product ON invoice_lines (product_id);
CREATE INDEX ix_invl_lot ON invoice_lines (lot_id) WHERE lot_id IS NOT NULL;

CREATE TABLE invoice_number_sequences (
    id             UUID PRIMARY KEY,
    company_id     UUID NOT NULL,
    prefix         VARCHAR(10) NOT NULL,
    year           INT NOT NULL,
    current_value  INT NOT NULL DEFAULT 0,
    UNIQUE (company_id, prefix, year)
);
```

## 5.1.9 Presentation — API

```python
# app/modules/invoice/presentation/routers.py

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoice"])


@router.post("/drafts", status_code=201)
async def create_draft(
    body: CreateDraftRequest,
    user = Depends(require_permission("invoice:create")),
    use_case = Depends(get_create_draft_use_case),
):
    return await use_case.execute(CreateDraftCommand(...))


@router.post("/{invoice_id}/lines", status_code=201)
async def add_line(
    invoice_id: UUID,
    body: AddLineRequest,
    user = Depends(require_permission("invoice:create")),
    use_case = Depends(get_add_line_use_case),
):
    return await use_case.execute(AddLineCommand(...))


@router.post("/{invoice_id}/issue", status_code=201)
async def issue_invoice(
    invoice_id: UUID,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("invoice:create")),
    use_case = Depends(get_issue_invoice_use_case),
):
    """ออก invoice — ต้องส่ง Idempotency-Key header"""
    return await use_case.execute(IssueInvoiceCommand(
        invoice_id=invoice_id,
        actor_id=user.id,
        idempotency_key=idempotency_key,
    ))


@router.post("/{invoice_id}/cancel")
async def cancel_invoice(
    invoice_id: UUID,
    body: CancelRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("invoice:cancel")),
    use_case = Depends(get_cancel_invoice_use_case),
):
    return await use_case.execute(CancelInvoiceCommand(
        invoice_id=invoice_id,
        reason=body.reason,
        actor_id=user.id,
        idempotency_key=idempotency_key,
    ))


@router.get("/")
async def list_invoices(
    status: str | None = Query(None),
    customer_id: UUID | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    user = Depends(require_permission("invoice:read")),
    use_case = Depends(get_list_invoices_use_case),
):
    return await use_case.execute(...)


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: UUID,
    user = Depends(require_permission("invoice:read")),
):
    ...


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: UUID,
    user = Depends(require_permission("invoice:read")),
):
    """ดาวน์โหลด PDF"""
    ...
```

## 5.1.10 Folder Structure

```text
app/modules/invoice/
├── domain/
│   ├── entities.py            # Invoice, InvoiceLine
│   ├── value_objects.py       # InvoiceNumber, TaxInvoiceNumber, enums, CustomerSnapshot
│   ├── events.py              # InvoiceIssued, InvoiceCancelled, ...
│   ├── services.py            # InvoiceCalculator (optional)
│   └── errors.py
├── application/
│   ├── interfaces.py          # IInvoiceRepository, IInvoiceNumberSequence, IPdfRenderer
│   └── use_cases.py           # CreateDraft, AddLine, IssueInvoice, CancelInvoice, ...
├── infrastructure/
│   ├── models.py              # InvoiceModel, InvoiceLineModel, Sequence
│   ├── repositories.py        # PostgresInvoiceRepository + Sequence
│   └── pdf/
│       └── weasyprint_renderer.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   ├── dependencies.py
│   └── exceptions.py
└── tests/
    ├── domain/
    │   ├── test_entities.py
    │   ├── test_totals.py         # verify_totals
    │   └── test_state_machine.py  # DRAFT → ISSUED → CANCELLED
    ├── application/
    │   ├── test_issue.py          # happy path + read-back
    │   ├── test_idempotency.py    # ยิงซ้ำ 100 ครั้ง
    │   └── test_concurrency.py    # ออกพร้อมกัน → เลขไม่ซ้ำ
    └── integration/
        └── test_money_path.py     # invoice → ledger → outbox
```

## 5.1.11 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (stabilize) / 2 (harden) |
| **DoD** | ✅ verify_totals ผ่านทุกใบ<br>✅ Read-back verify หลัง issue<br>✅ Idempotency: ยิงซ้ำ 100 → 1<br>✅ Concurrency: ออกพร้อม 10 thread → เลขไม่ซ้ำ<br>✅ Cancel → emit InvoiceCancelled<br>✅ Property test: total = Σlines + VAT |

---

# 🧩 Module 5.2 — `ledger`

## 5.2.1 Purpose & Scope

**Purpose:** บันทึกบัญชีแบบ **double-entry** ที่ debit = credit เสมอ รองรับ reversal (ห้ามลบ) และ post ตามผังบัญชีมาตรฐานไทย

**Scope:**
- ✅ Chart of Accounts (ผังบัญชี)
- ✅ JournalEntry + LedgerLine (double-entry)
- ✅ Post journal จาก domain event (invoice, payment, stock)
- ✅ Reversal (ห้าม DELETE)
- ✅ Period close (ปิดงวด)
- ✅ Trial balance, GL report
- ❌ ไม่คำนวณ VAT (tax module ทำ)
- ❌ ไม่ sync cloud (accounting_gateway ทำ)

## 5.2.2 Domain Model

```python
# app/modules/ledger/domain/value_objects.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"              # สินทรัพย์
    LIABILITY = "liability"      # หนี้สิน
    EQUITY = "equity"            # ส่วนของเจ้าของ
    REVENUE = "revenue"          # รายได้
    EXPENSE = "expense"          # ค่าใช้จ่าย
    COGS = "cogs"                # ต้นทุนขาย


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass(frozen=True, slots=True)
class AccountCode:
    """
    รหัสบัญชี — ตามมาตรฐานไทย
    1xxx = สินทรัพย์
    2xxx = หนี้สิน
    3xxx = ส่วนของเจ้าของ
    4xxx = รายได้
    5xxx = ค่าใช้จ่าย
    6xxx = ต้นทุนขาย
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value[0].isdigit():
            raise ValueError(f"AccountCode ต้องเริ่มด้วยตัวเลข: {self.value}")

    @property
    def major_type(self) -> AccountType:
        first = self.value[0]
        return {
            "1": AccountType.ASSET,
            "2": AccountType.LIABILITY,
            "3": AccountType.EQUITY,
            "4": AccountType.REVENUE,
            "5": AccountType.EXPENSE,
            "6": AccountType.COGS,
        }.get(first, AccountType.ASSET)


@dataclass(frozen=True, slots=True)
class DebitCredit:
    """ค่า debit หรือ credit — ต้อง ≥ 0"""
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("debit/credit ต้อง ≥ 0")
        if not isinstance(self.amount, Decimal):
            raise TypeError("ต้องเป็น Decimal")


class JournalSource(str, Enum):
    """แหล่งที่มาของ journal"""
    INVOICE = "invoice"
    PAYMENT = "payment"
    STOCK = "stock"
    PRODUCTION = "production"
    MANUAL = "manual"
    OPENING = "opening"
    ADJUSTMENT = "adjustment"
    REVERSAL = "reversal"


class JournalStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"       # ถูก reversal แล้ว
```

```python
# app/modules/ledger/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.modules.ledger.domain.value_objects import (
    AccountCode, AccountType, NormalBalance,
    JournalSource, JournalStatus,
)


@dataclass
class Account:
    """
    บัญชีในผังบัญชี

    Invariants:
    - code unique ต่อ company
    - account_type ต้องตรงกับ code
    - is_active เปลี่ยนได้ แต่ห้ามลบถ้ามี entry
    """
    id: UUID
    company_id: UUID
    code: AccountCode
    name: str
    name_en: str | None
    account_type: AccountType
    normal_balance: NormalBalance
    parent_account_id: UUID | None
    is_active: bool
    is_system: bool                 # บัญชีระบบ (ห้ามลบ)
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        code: str,
        name: str,
        account_type: AccountType,
        normal_balance: NormalBalance,
        name_en: str | None = None,
        parent_account_id: UUID | None = None,
        is_system: bool = False,
    ) -> "Account":
        code_vo = AccountCode(code)
        if code_vo.major_type != account_type:
            raise ValueError(
                f"account_type {account_type.value} ไม่ตรงกับ code {code}"
            )
        return cls(
            id=uuid4(),
            company_id=company_id,
            code=code_vo,
            name=name,
            name_en=name_en,
            account_type=account_type,
            normal_balance=normal_balance,
            parent_account_id=parent_account_id,
            is_active=True,
            is_system=is_system,
            created_at=datetime.utcnow(),
        )


@dataclass
class LedgerLine:
    """
    บรรทัดใน journal — Entity

    Invariants:
    - debit = 0 หรือ credit = 0 (ไม่ใช่ทั้งคู่)
    - amount > 0 (ฝั่งที่เป็น)
    """
    id: UUID
    journal_id: UUID
    line_number: int
    account_id: UUID
    account_code: AccountCode
    account_name: str
    debit: Decimal
    credit: Decimal
    description: str
    cost_center_id: UUID | None      # branch/cost center
    tax_code: str | None             # "VAT7", "WHT3"
    reference_id: UUID | None        # invoice_id, payment_id

    def __post_init__(self) -> None:
        if self.debit < 0 or self.credit < 0:
            raise ValueError("debit/credit ต้อง ≥ 0")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("line ต้องเป็น debit หรือ credit อย่างใดอย่างหนึ่ง")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("line ต้องมี debit หรือ credit")

    @property
    def amount(self) -> Decimal:
        return self.debit if self.debit > 0 else self.credit


@dataclass
class JournalEntry:
    """
    Journal Entry — Aggregate Root

    Invariants:
    1.  Σ(debit) = Σ(credit)  ← CRITICAL
    2.  อย่างน้อย 2 lines
    3.  POSTED แล้วห้ามแก้ — ต้อง reversal
    4.  posting_date ต้องไม่ย้อนหลังใน period ที่ปิดแล้ว
    5.  reversal_of ชี้ entry ที่ถูก reverse
    """
    id: UUID
    company_id: UUID
    journal_number: str               # "JN-2026-00001"
    source: JournalSource
    source_id: UUID | None            # invoice_id, payment_id, ...
    posting_date: date
    description: str
    status: JournalStatus
    reversal_of_id: UUID | None
    reversed_by_id: UUID | None
    created_by: UUID
    created_at: datetime
    posted_at: datetime | None

    _lines: list[LedgerLine] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        journal_number: str,
        source: JournalSource,
        source_id: UUID | None,
        posting_date: date,
        description: str,
        created_by: UUID,
    ) -> "JournalEntry":
        return cls(
            id=uuid4(),
            company_id=company_id,
            journal_number=journal_number,
            source=source,
            source_id=source_id,
            posting_date=posting_date,
            description=description,
            status=JournalStatus.DRAFT,
            reversal_of_id=None,
            reversed_by_id=None,
            created_by=created_by,
            created_at=datetime.utcnow(),
            posted_at=None,
            _lines=[],
        )

    def add_line(
        self,
        *,
        account: Account,
        debit: Decimal,
        credit: Decimal,
        description: str,
        cost_center_id: UUID | None = None,
        tax_code: str | None = None,
        reference_id: UUID | None = None,
    ) -> LedgerLine:
        if self.status != JournalStatus.DRAFT:
            raise ValueError("แก้ line ไม่ได้ — journal posted แล้ว")
        line = LedgerLine(
            id=uuid4(),
            journal_id=self.id,
            line_number=len(self._lines) + 1,
            account_id=account.id,
            account_code=account.code,
            account_name=account.name,
            debit=debit,
            credit=credit,
            description=description,
            cost_center_id=cost_center_id,
            tax_code=tax_code,
            reference_id=reference_id,
        )
        self._lines.append(line)
        return line

    def post(self) -> None:
        """
        Post journal — ตรวจ balance ก่อน

        🛡️ CRITICAL: ต้อง debit = credit เสมอ
        """
        if self.status != JournalStatus.DRAFT:
            raise ValueError(f"post ไม่ได้ — status = {self.status.value}")
        if len(self._lines) < 2:
            raise ValueError("ต้องมีอย่างน้อย 2 lines")
        self._verify_balance()
        self.status = JournalStatus.POSTED
        self.posted_at = datetime.utcnow()

    def _verify_balance(self) -> None:
        total_debit = sum((ln.debit for ln in self._lines), Decimal("0"))
        total_credit = sum((ln.credit for ln in self._lines), Decimal("0"))
        if total_debit != total_credit:
            raise ValueError(
                f"🚨 DEBIT ≠ CREDIT: debit={total_debit}, credit={total_credit}, "
                f"ต่าง={abs(total_debit - total_credit)}"
            )

    @property
    def total_debit(self) -> Decimal:
        return sum((ln.debit for ln in self._lines), Decimal("0"))

    @property
    def total_credit(self) -> Decimal:
        return sum((ln.credit for ln in self._lines), Decimal("0"))

    @property
    def lines(self) -> list[LedgerLine]:
        return list(self._lines)

    def reverse(
        self, *, reversal_number: str, created_by: UUID,
    ) -> "JournalEntry":
        """
        สร้าง reversal entry — สลับ debit/credit
        """
        if self.status != JournalStatus.POSTED:
            raise ValueError("reverse ได้เฉพาะ POSTED")
        if self.reversed_by_id is not None:
            raise ValueError("journal นี้ถูก reverse แล้ว")

        reversal = JournalEntry.create(
            company_id=self.company_id,
            journal_number=reversal_number,
            source=JournalSource.REVERSAL,
            source_id=self.id,
            posting_date=self.posting_date,
            description=f"REVERSAL of {self.journal_number}: {self.description}",
            created_by=created_by,
        )
        reversal.reversal_of_id = self.id
        for ln in self._lines:
            reversal.add_line(
                account=Account(  # mock — ในทางจริงต้อง lookup
                    id=ln.account_id, company_id=self.company_id,
                    code=ln.account_code, name=ln.account_name,
                    name_en=None, account_type=ln.account_code.major_type,
                    normal_balance=NormalBalance.DEBIT,
                    parent_account_id=None, is_active=True,
                    is_system=False, created_at=datetime.utcnow(),
                ),
                debit=ln.credit,
                credit=ln.debit,
                description=f"REVERSAL: {ln.description}",
                cost_center_id=ln.cost_center_id,
                tax_code=ln.tax_code,
                reference_id=ln.reference_id,
            )
        reversal.post()
        self.reversed_by_id = reversal.id
        self.status = JournalStatus.REVERSED
        return reversal
```

## 5.2.3 Domain Events

```python
# app/modules/ledger/domain/events.py

from app.core.events.domain.entities import DomainEvent


class LedgerPosted(DomainEvent):
    """Post journal สำเร็จ"""
    ...


class LedgerReversed(DomainEvent):
    """Reversal journal"""
    ...


class PeriodClosed(DomainEvent):
    """ปิดงวดบัญชี"""
    ...


class TrialBalanceMismatch(DomainEvent):
    """🚨 debit ≠ credit (ไม่ควรเกิด — alert!)"""
    ...
```

## 5.2.4 Chart of Accounts (Thai Standard)

```python
# app/modules/ledger/domain/chart_of_accounts.py

"""
ผังบัญชีมาตรฐานสำหรับธุรกิจอาหาร
"""

DEFAULT_CHART_OF_ACCOUNTS = [
    # ===== 1xxx สินทรัพย์ =====
    ("1000", "เงินสด", AccountType.ASSET, NormalBalance.DEBIT),
    ("1010", "เงินฝากธนาคาร", AccountType.ASSET, NormalBalance.DEBIT),
    ("1100", "ลูกหนี้การค้า", AccountType.ASSET, NormalBalance.DEBIT),
    ("1110", "ลูกหนี้อื่น", AccountType.ASSET, NormalBalance.DEBIT),
    ("1200", "สินค้าคงเหลือ", AccountType.ASSET, NormalBalance.DEBIT),
    ("1210", "วัตถุดิบ", AccountType.ASSET, NormalBalance.DEBIT),
    ("1220", "สินค้าระหว่างผลิต", AccountType.ASSET, NormalBalance.DEBIT),
    ("1230", "สินค้าสำเร็จรูป", AccountType.ASSET, NormalBalance.DEBIT),
    ("1300", "ภาษีซื้อ", AccountType.ASSET, NormalBalance.DEBIT),
    ("1310", "ภาษีซื้อไม่ถึงกำหนด", AccountType.ASSET, NormalBalance.DEBIT),
    ("1400", "ค่าใช้จ่ายล่วงหน้า", AccountType.ASSET, NormalBalance.DEBIT),
    ("1500", "ที่ดิน อาคาร อุปกรณ์", AccountType.ASSET, NormalBalance.DEBIT),
    ("1510", "ค่าเสื่อมราคาสะสม", AccountType.ASSET, NormalBalance.CREDIT),

    # ===== 2xxx หนี้สิน =====
    ("2000", "เจ้าหนี้การค้า", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2010", "เจ้าหนี้อื่น", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2100", "ภาษีขาย", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2110", "ภาษีหัก ณ ที่จ่าย", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2120", "ภาษีเงินได้ค้างจ่าย", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2200", "เงินเดือนค้างจ่าย", AccountType.LIABILITY, NormalBalance.CREDIT),
    ("2300", "เงินกู้ยืม", AccountType.LIABILITY, NormalBalance.CREDIT),

    # ===== 3xxx ส่วนของเจ้าของ =====
    ("3000", "ทุน", AccountType.EQUITY, NormalBalance.CREDIT),
    ("3100", "กำไรสะสม", AccountType.EQUITY, NormalBalance.CREDIT),
    ("3200", "เงินปันผล", AccountType.EQUITY, NormalBalance.DEBIT),

    # ===== 4xxx รายได้ =====
    ("4000", "รายได้จากการขาย", AccountType.REVENUE, NormalBalance.CREDIT),
    ("4010", "รายได้จากการขายส่ง", AccountType.REVENUE, NormalBalance.CREDIT),
    ("4020", "รายได้จากการขายปลีก", AccountType.REVENUE, NormalBalance.CREDIT),
    ("4100", "ส่วนลดจ่าย", AccountType.REVENUE, NormalBalance.DEBIT),
    ("4200", "รายได้อื่น", AccountType.REVENUE, NormalBalance.CREDIT),

    # ===== 5xxx ค่าใช้จ่าย =====
    ("5000", "เงินเดือน", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5010", "ค่าแรง", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5100", "ค่าเช่า", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5110", "ค่าน้ำ ค่าไฟ", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5200", "ค่าน้ำมัน", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5210", "ค่าขนส่ง", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5300", "ค่าของเสีย", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5400", "ค่าเสื่อมราคา", AccountType.EXPENSE, NormalBalance.DEBIT),
    ("5500", "ดอกเบี้ยจ่าย", AccountType.EXPENSE, NormalBalance.DEBIT),

    # ===== 6xxx ต้นทุนขาย =====
    ("6000", "ต้นทุนขาย", AccountType.COGS, NormalBalance.DEBIT),
    ("6010", "ต้นทุนวัตถุดิบ", AccountType.COGS, NormalBalance.DEBIT),
    ("6020", "ต้นทุนการผลิต", AccountType.COGS, NormalBalance.DEBIT),
]
```

## 5.2.5 Application — Use Cases

```python
# app/modules/ledger/application/use_cases.py

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.modules.ledger.domain.entities import Account, JournalEntry
from app.modules.ledger.domain.value_objects import JournalSource
from app.modules.ledger.domain.events import LedgerPosted, LedgerReversed
from app.modules.ledger.application.interfaces import (
    IAccountRepository, IJournalRepository, IJournalNumberSequence,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.core.tenant_context.domain.context import get_company_id


# ============================================================
# 1. Seed Chart of Accounts
# ============================================================

class SeedChartOfAccountsUseCase:
    """
    Seed ผังบัญชีมาตรฐาน — เรียกตอน provision บริษัทใหม่
    """

    def __init__(self, accounts: IAccountRepository, uow):
        self.accounts = accounts
        self.uow = uow

    async def execute(self, company_id: UUID) -> None:
        from app.modules.ledger.domain.chart_of_accounts import DEFAULT_CHART_OF_ACCOUNTS
        async with self.uow.transaction():
            for code, name, atype, nbalance in DEFAULT_CHART_OF_ACCOUNTS:
                if await self.accounts.exists_by_code(company_id, code):
                    continue
                acc = Account.create(
                    company_id=company_id,
                    code=code,
                    name=name,
                    account_type=atype,
                    normal_balance=nbalance,
                    is_system=True,
                )
                await self.accounts.save(acc)


# ============================================================
# 2. Post Journal (CORE)
# ============================================================

@dataclass
class PostJournalLineInput:
    account_code: str
    debit: Decimal
    credit: Decimal
    description: str
    cost_center_id: UUID | None = None
    tax_code: str | None = None
    reference_id: UUID | None = None


@dataclass
class PostJournalCommand:
    source: JournalSource
    source_id: UUID | None
    posting_date: date
    description: str
    lines: list[PostJournalLineInput]
    actor_id: UUID | None = None
    actor_type: ActorType = ActorType.SYSTEM


class PostJournalUseCase:
    """
    🎯 Post journal — double-entry

    Flow:
    1.  ดึง account แต่ละ code
    2.  สร้าง JournalEntry + lines
    3.  post() → verify debit = credit
    4.  Persist
    5.  Read-back verify
    6.  Audit + Publish
    """

    def __init__(
        self,
        accounts: IAccountRepository,
        journals: IJournalRepository,
        sequence: IJournalNumberSequence,
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        uow,
    ):
        self.accounts = accounts
        self.journals = journals
        self.sequence = sequence
        self.audit = audit
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: PostJournalCommand) -> JournalEntry:
        company_id = get_company_id()

        async with self.uow.transaction():
            # 1. ออกเลข journal
            number = await self.sequence.next_number(
                company_id=company_id,
                prefix="JN",
                year=cmd.posting_date.year,
            )

            # 2. สร้าง entry
            journal = JournalEntry.create(
                company_id=company_id,
                journal_number=number,
                source=cmd.source,
                source_id=cmd.source_id,
                posting_date=cmd.posting_date,
                description=cmd.description,
                created_by=cmd.actor_id,
            )

            # 3. เพิ่ม lines
            for line_in in cmd.lines:
                account = await self.accounts.get_by_code(
                    company_id, line_in.account_code,
                )
                if not account:
                    raise ValueError(f"ไม่พบบัญชี: {line_in.account_code}")
                journal.add_line(
                    account=account,
                    debit=line_in.debit,
                    credit=line_in.credit,
                    description=line_in.description,
                    cost_center_id=line_in.cost_center_id,
                    tax_code=line_in.tax_code,
                    reference_id=line_in.reference_id,
                )

            # 4. post → verify debit = credit
            journal.post()

            # 5. Persist
            await self.journals.save(journal)

            # 6. Read-back verify
            persisted = await self.journals.get_with_lines(journal.id)
            if not persisted:
                raise RuntimeError("read-back: ไม่พบ journal")
            if persisted.total_debit != persisted.total_credit:
                raise RuntimeError("🚨 read-back: debit ≠ credit")

            # 7. Audit
            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=cmd.actor_type,
                action=AuditAction.LEDGER_POSTED,
                entity_type="journal",
                entity_id=journal.id,
                after_state={
                    "journal_number": journal.journal_number,
                    "total_debit": str(journal.total_debit),
                    "total_credit": str(journal.total_credit),
                    "source": cmd.source.value,
                },
            ))

            # 8. Publish
            await self.publish.execute(LedgerPosted.create(
                company_id=company_id,
                payload={
                    "journal_id": str(journal.id),
                    "journal_number": journal.journal_number,
                    "source": cmd.source.value,
                    "source_id": str(cmd.source_id) if cmd.source_id else None,
                },
                actor_id=cmd.actor_id,
            ))

        return journal


# ============================================================
# 3. Reverse Journal
# ============================================================

@dataclass
class ReverseJournalCommand:
    journal_id: UUID
    actor_id: UUID


class ReverseJournalUseCase:
    """
    สร้าง reversal — ห้ามลบ entry
    """

    def __init__(self, journals, sequence, audit, publish, uow):
        ...

    async def execute(self, cmd: ReverseJournalCommand) -> JournalEntry:
        company_id = get_company_id()
        async with self.uow.transaction():
            original = await self.journals.get_with_lines(cmd.journal_id)
            if not original:
                raise ValueError("ไม่พบ journal")

            number = await self.sequence.next_number(
                company_id=company_id, prefix="JN", year=original.posting_date.year,
            )

            reversal = original.reverse(
                reversal_number=number,
                created_by=cmd.actor_id,
            )

            await self.journals.save(reversal)
            await self.journals.update(original)  # status → REVERSED

            # Read-back
            persisted = await self.journals.get_with_lines(reversal.id)
            if persisted.total_debit != persisted.total_credit:
                raise RuntimeError("reversal: debit ≠ credit")

            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.LEDGER_REVERSED,
                entity_type="journal",
                entity_id=reversal.id,
                before_state={"original_journal": original.journal_number},
                after_state={"reversal_number": reversal.journal_number},
            ))

            await self.publish.execute(LedgerReversed.create(
                company_id=company_id,
                payload={
                    "original_id": str(original.id),
                    "reversal_id": str(reversal.id),
                },
                actor_id=cmd.actor_id,
            ))
        return reversal


# ============================================================
# 4. Handle Domain Events (Listener)
# ============================================================

class InvoiceIssuedLedgerHandler:
    """
    ฟัง InvoiceIssued → post journal

    ตัวอย่าง journal สำหรับขายเชื่อ:
      Dr. ลูกหนี้การค้า           grand_total
        Cr. รายได้จากการขาย       subtotal
        Cr. ภาษีขาย (VAT)         vat_total
    """

    def __init__(self, post_journal: PostJournalUseCase, config):
        self.post_journal = post_journal
        self.config = config

    async def handle(self, event: InvoiceIssued) -> None:
        payload = event.payload
        grand_total = Decimal(payload["grand_total"])
        # ดึง subtotal, vat จาก payload หรือคำนวณใหม่
        ...

        lines = [
            PostJournalLineInput(
                account_code="1100",  # ลูกหนี้การค้า
                debit=grand_total, credit=Decimal("0"),
                description=f"Invoice {payload['invoice_number']}",
                reference_id=event.aggregate_id,
            ),
            PostJournalLineInput(
                account_code="4000",  # รายได้
                debit=Decimal("0"), credit=subtotal,
                description=f"Invoice {payload['invoice_number']}",
                reference_id=event.aggregate_id,
            ),
            PostJournalLineInput(
                account_code="2100",  # ภาษีขาย
                debit=Decimal("0"), credit=vat_total,
                description=f"VAT {payload['invoice_number']}",
                reference_id=event.aggregate_id,
                tax_code="VAT7",
            ),
        ]

        await self.post_journal.execute(PostJournalCommand(
            source=JournalSource.INVOICE,
            source_id=event.aggregate_id,
            posting_date=date.fromisoformat(payload["issue_date"]),
            description=f"Invoice {payload['invoice_number']}",
            lines=lines,
            actor_id=event.actor_id,
            actor_type=ActorType.SYSTEM,
        ))
```

## 5.2.6 Infrastructure — Models

```python
# app/modules/ledger/infrastructure/models.py

from sqlalchemy import (
    Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base


class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_acc_company_code"),
        Index("ix_acc_company_type", "company_id", "account_type"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255))
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    normal_balance: Mapped[str] = mapped_column(String(10), nullable=False)
    parent_account_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_system: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("company_id", "journal_number", name="uq_jn_company_number"),
        Index("ix_jn_company_date", "company_id", "posting_date"),
        Index("ix_jn_source", "company_id", "source", "source_id"),
        Index("ix_jn_status", "company_id", "status"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    journal_number: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    posting_date: Mapped[Date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    reversal_of_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"),
    )
    reversed_by_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    total_debit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_credit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    created_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    posted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    lines: Mapped[list["LedgerLineModel"]] = relationship(
        "LedgerLineModel", back_populates="journal",
        cascade="all, delete-orphan", order_by="LedgerLineModel.line_number",
    )


class LedgerLineModel(Base):
    __tablename__ = "ledger_lines"
    __table_args__ = (
        Index("ix_ll_journal", "journal_id", "line_number", unique=True),
        Index("ix_ll_account", "account_id", "posting_date"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    journal_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"),
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    account_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    account_code: Mapped[str] = mapped_column(String(20))
    account_name: Mapped[str] = mapped_column(String(255))
    debit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    credit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text)
    cost_center_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    tax_code: Mapped[str | None] = mapped_column(String(20))
    reference_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    posting_date: Mapped[Date] = mapped_column(Date, nullable=False)  # denorm for reporting

    journal: Mapped[JournalEntryModel] = relationship(
        "JournalEntryModel", back_populates="lines",
    )


class JournalNumberSequenceModel(Base):
    __tablename__ = "journal_number_sequences"
    __table_args__ = (UniqueConstraint("company_id", "prefix", "year"),)

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    prefix: Mapped[str] = mapped_column(String(10))
    year: Mapped[int] = mapped_column(Integer)
    current_value: Mapped[int] = mapped_column(Integer, default=0)


class AccountingPeriodModel(Base):
    """งวดบัญชี — ปิดแล้วห้าม post"""
    __tablename__ = "accounting_periods"
    __table_args__ = (
        UniqueConstraint("company_id", "year", "month", name="uq_period"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    is_closed: Mapped[bool] = mapped_column(default=False)
    closed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    closed_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
```

## 5.2.7 Database Schema

```sql
CREATE TABLE accounts (
    id                UUID PRIMARY KEY,
    company_id        UUID NOT NULL,
    code              VARCHAR(20) NOT NULL,
    name              VARCHAR(255) NOT NULL,
    name_en           VARCHAR(255),
    account_type      VARCHAR(20) NOT NULL,
    normal_balance    VARCHAR(10) NOT NULL,
    parent_account_id UUID,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_system         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL,
    UNIQUE (company_id, code)
);

CREATE TABLE journal_entries (
    id              UUID PRIMARY KEY,
    company_id      UUID NOT NULL,
    journal_number  VARCHAR(30) NOT NULL,
    source          VARCHAR(20) NOT NULL,
    source_id       UUID,
    posting_date    DATE NOT NULL,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL,
    reversal_of_id  UUID REFERENCES journal_entries(id),
    reversed_by_id  UUID,
    total_debit     NUMERIC(15,2) NOT NULL,
    total_credit    NUMERIC(15,2) NOT NULL,
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    posted_at       TIMESTAMPTZ,
    UNIQUE (company_id, journal_number),
    CHECK (total_debit = total_credit)  -- 🛡️ DB-level invariant
);

CREATE INDEX ix_jn_company_date ON journal_entries (company_id, posting_date DESC);
CREATE INDEX ix_jn_source ON journal_entries (company_id, source, source_id);

CREATE TABLE ledger_lines (
    id              UUID PRIMARY KEY,
    journal_id      UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    line_number     INT NOT NULL,
    account_id      UUID NOT NULL,
    account_code    VARCHAR(20) NOT NULL,
    account_name    VARCHAR(255) NOT NULL,
    debit           NUMERIC(15,2) NOT NULL DEFAULT 0,
    credit          NUMERIC(15,2) NOT NULL DEFAULT 0,
    description     TEXT NOT NULL,
    cost_center_id  UUID,
    tax_code        VARCHAR(20),
    reference_id    UUID,
    posting_date    DATE NOT NULL,
    UNIQUE (journal_id, line_number),
    CHECK ((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0))
);

CREATE INDEX ix_ll_account ON ledger_lines (account_id, posting_date DESC);
CREATE INDEX ix_ll_reference ON ledger_lines (reference_id) WHERE reference_id IS NOT NULL;

CREATE TABLE accounting_periods (
    id         UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    year       INT NOT NULL,
    month      INT NOT NULL,
    is_closed  BOOLEAN NOT NULL DEFAULT FALSE,
    closed_at  TIMESTAMPTZ,
    closed_by  UUID,
    UNIQUE (company_id, year, month)
);
```

## 5.2.8 Presentation — API

```python
# app/modules/ledger/presentation/routers.py

router = APIRouter(prefix="/api/v1/ledger", tags=["Ledger"])


# ---------- Accounts ----------
@router.get("/accounts")
async def list_accounts(user = Depends(require_permission("ledger:read"))):
    """ผังบัญชี"""
    ...

@router.post("/accounts", status_code=201)
async def create_account(user = Depends(require_permission("ledger:post"))):
    ...


# ---------- Journals ----------
@router.get("/journals")
async def list_journals(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    source: str | None = Query(None),
    user = Depends(require_permission("ledger:read")),
):
    ...

@router.get("/journals/{journal_id}")
async def get_journal(journal_id: UUID, ...): ...

@router.post("/journals", status_code=201)
async def post_manual_journal(
    body: PostJournalRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("ledger:post")),
    use_case = Depends(get_post_journal_use_case),
):
    ...

@router.post("/journals/{journal_id}/reverse", status_code=201)
async def reverse_journal(
    journal_id: UUID,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("ledger:reverse")),
    use_case = Depends(get_reverse_journal_use_case),
):
    ...


# ---------- Reports ----------
@router.get("/trial-balance")
async def trial_balance(
    as_of_date: date,
    user = Depends(require_permission("report:read")),
):
    """งบทดลอง — Σ debit = Σ credit"""
    ...

@router.get("/gl/{account_code}")
async def general_ledger(
    account_code: str,
    from_date: date, to_date: date,
    user = Depends(require_permission("report:read")),
):
    ...
```

## 5.2.9 Folder Structure

```text
app/modules/ledger/
├── domain/
│   ├── entities.py            # Account, JournalEntry, LedgerLine
│   ├── value_objects.py       # AccountCode, AccountType, NormalBalance, enums
│   ├── events.py              # LedgerPosted, LedgerReversed, ...
│   ├── chart_of_accounts.py   # DEFAULT_CHART_OF_ACCOUNTS
│   └── errors.py              # UnbalancedJournalError, ...
├── application/
│   ├── interfaces.py          # IAccountRepository, IJournalRepository, IJournalNumberSequence
│   ├── use_cases.py           # PostJournal, ReverseJournal, SeedCOA
│   └── handlers.py            # InvoiceIssuedLedgerHandler, PaymentLedgerHandler
├── infrastructure/
│   ├── models.py              # AccountModel, JournalEntryModel, LedgerLineModel, ...
│   └── repositories.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── domain/
    │   ├── test_double_entry.py    # Σdebit = Σcredit
    │   ├── test_reversal.py
    │   └── test_account_code.py
    ├── application/
    │   ├── test_post_journal.py
    │   └── test_invoice_handler.py
    └── integration/
        └── test_trial_balance.py
```

## 5.2.10 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (stabilize) / 2 (harden) |
| **DoD** | ✅ post journal ตรวจ debit = credit<br>✅ DB CHECK constraint (defense in depth)<br>✅ reversal ทำงาน — ไม่ลบ entry<br>✅ Chart of Accounts seed ครบ<br>✅ Invoice handler post journal อัตโนมัติ<br>✅ Trial balance ผ่าน |

---

# 🧩 Module 5.3 — `tax`

## 5.3.1 Purpose & Scope

**Purpose:** คำนวณภาษีไทย (VAT, WHT, e-Tax Invoice) + เก็บอัตรา/ข้อยกเว้น ตาม config

**Scope:**
- ✅ VAT (7%, 0%, exempt) — ต่อสินค้า
- ✅ WHT (หัก ณ ที่จ่าย — 1%, 3%, 5%)
- ✅ e-Tax Invoice/Receipt (Revenue Dept)
- ✅ Tax report (ภ.พ.30, ภ.ง.ด.53)
- ✅ Tax code (VAT7, VAT0, VATEX, WHT1, WHT3, WHT5)
- ❌ ไม่คำนวณในใบ (invoice ใช้ Money + tax module)
- ❌ ไม่ยื่นภาษี (external)

## 5.3.2 Domain Model

```python
# app/modules/tax/domain/value_objects.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TaxType(str, Enum):
    VAT = "vat"           # ภาษีมูลค่าเพิ่ม
    WHT = "wht"           # ภาษีหัก ณ ที่จ่าย
    SBT = "sbt"           # ภาษีธุรกิจเฉพาะ
    EXCISE = "excise"     # ภาษีสรรพสามิต
    NONE = "none"


class VatOutputInput(str, Enum):
    """VAT ขาเข้า vs ขาออก"""
    OUTPUT = "output"     # ขาย → ภาษีขาย
    INPUT = "input"       # ซื้อ → ภาษีซื้อ


@dataclass(frozen=True, slots=True)
class TaxCode:
    """
    รหัสภาษี
    - VAT7, VAT0, VATEX
    - WHT1, WHT3, WHT5
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("TaxCode ต้องไม่ว่าง")


@dataclass(frozen=True, slots=True)
class WhtCertificate:
    """
    หนังสือรับรองการหักภาษี ณ ที่จ่าย
    """
    book_number: str                # "ว." เลขที่
    certificate_number: str
    issue_date: str
    payee_tax_id: str
    payer_tax_id: str
    amount_paid: Decimal
    wht_rate: Decimal
    wht_amount: Decimal
    income_type: str                # "ค่าบริการ", "ค่าเช่า", ...


class WhtIncomeType(str, Enum):
    """ประเภทเงินได้ — อัตรา WHT"""
    SERVICE = "service"             # ค่าบริการ 3%
    RENTAL = "rental"               # ค่าเช่า 5%
    TRANSPORT = "transport"         # ค่าขนส่ง 1%
    ADVERTISING = "advertising"     # ค่าโฆษณา 2%
    PROFESSIONAL = "professional"   # วิชาชีพ 3%
    COMMISSION = "commission"       # ค่านายหน้า 3%
    INTEREST = "interest"           # ดอกเบี้ย 1%
    DIVIDEND = "dividend"           # เงินปันผล 10%


# อัตรา WHT ตามประเภท
WHT_RATES: dict[WhtIncomeType, Decimal] = {
    WhtIncomeType.SERVICE: Decimal("0.03"),
    WhtIncomeType.RENTAL: Decimal("0.05"),
    WhtIncomeType.TRANSPORT: Decimal("0.01"),
    WhtIncomeType.ADVERTISING: Decimal("0.02"),
    WhtIncomeType.PROFESSIONAL: Decimal("0.03"),
    WhtIncomeType.COMMISSION: Decimal("0.03"),
    WhtIncomeType.INTEREST: Decimal("0.01"),
    WhtIncomeType.DIVIDEND: Decimal("0.10"),
}


class ETaxStatus(str, Enum):
    NONE = "none"
    PENDING = "pending"           # รอส่ง
    SENT = "sent"                 # ส่งแล้ว
    ACCEPTED = "accepted"         # รับแล้ว
    REJECTED = "rejected"         # ปฏิเสธ
```

```python
# app/modules/tax/domain/entities.py

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.modules.tax.domain.value_objects import (
    TaxType, VatOutputInput, TaxCode, WhtIncomeType, ETaxStatus,
)


@dataclass(frozen=True, slots=True)
class TaxRate:
    """
    อัตราภาษี — versioned ต่อ company
    """
    id: UUID
    company_id: UUID
    tax_type: TaxType
    code: TaxCode
    rate: Decimal                    # 0.07 = 7%
    description: str
    effective_from: date
    effective_to: date | None
    is_active: bool


@dataclass
class ETaxSubmission:
    """
    การส่ง e-Tax Invoice
    """
    id: UUID
    company_id: UUID
    invoice_id: UUID
    xml_payload: str                # XML ตาม Revenue Dept spec
    status: ETaxStatus
    reference_number: str | None    # เลขที่ตอบรับ
    submitted_at: datetime | None
    response_message: str | None
    retry_count: int
    created_at: datetime
```

## 5.3.3 Application — Calculators

```python
# app/modules/tax/application/calculators.py

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from app.core.money.domain.value_objects import Money
from app.modules.tax.domain.value_objects import WhtIncomeType, WHT_RATES


class VatCalculatorService:
    """
    Wrapper รอบ core/money VatCalculator
    เพิ่ม logic: เลือกอัตราตาม product, config
    """

    def __init__(self, config):
        self.config = config

    async def get_rate_for_product(
        self, company_id, product_id, is_export: bool = False,
    ) -> Decimal:
        # priority: product override > category > company default
        if is_export:
            return Decimal("0.00")
        # ดึงจาก config
        return await self.config.get_decimal(
            company_id, "tax.vat_standard_rate", Decimal("0.07"),
        )


class WhtCalculatorService:
    """
    คำนวณภาษีหัก ณ ที่จ่าย
    """

    @staticmethod
    def calculate(
        base_amount: Money,
        income_type: WhtIncomeType,
    ) -> Money:
        rate = WHT_RATES[income_type]
        wht_amount = (base_amount.amount * rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP,
        )
        return Money(wht_amount, base_amount.currency)

    @staticmethod
    def net_payment(base_amount: Money, wht_amount: Money) -> Money:
        """ยอดที่จ่ายจริง = base − wht"""
        return base_amount - wht_amount
```

## 5.3.4 Application — Use Cases

```python
# app/modules/tax/application/use_cases.py

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.core.money.domain.value_objects import Money
from app.modules.tax.domain.value_objects import WhtIncomeType, ETaxStatus
from app.modules.tax.domain.entities import ETaxSubmission
from app.modules.tax.application.calculators import WhtCalculatorService


# ============================================================
# 1. Calculate WHT
# ============================================================

@dataclass
class CalculateWhtCommand:
    base_amount: Decimal
    currency: str
    income_type: WhtIncomeType


class CalculateWhtUseCase:
    def execute(self, cmd: CalculateWhtCommand) -> dict:
        base = Money(cmd.base_amount)
        wht = WhtCalculatorService.calculate(base, cmd.income_type)
        net = WhtCalculatorService.net_payment(base, wht)
        return {
            "base": str(base.amount),
            "wht_rate": str(WHT_RATES[cmd.income_type]),
            "wht_amount": str(wht.amount),
            "net_payment": str(net.amount),
        }


# ============================================================
# 2. Submit e-Tax Invoice
# ============================================================

@dataclass
class SubmitETaxCommand:
    invoice_id: UUID
    actor_id: UUID


class SubmitETaxUseCase:
    """
    ส่ง e-Tax Invoice ไป Revenue Dept

    Flow:
    1. โหลด invoice
    2. สร้าง XML ตาม spec
    3. บันทึก submission (status=PENDING)
    4. ส่งผ่าน API (async worker)
    5. อัปเดต status (ACCEPTED/REJECTED)
    6. Retry ถ้า fail
    """

    def __init__(self, invoices, submissions, xml_builder, etax_client, uow):
        ...

    async def execute(self, cmd: SubmitETaxCommand) -> ETaxSubmission:
        invoice = await self.invoices.get_with_lines(cmd.invoice_id)
        if not invoice:
            raise ValueError("ไม่พบ invoice")

        xml = await self.xml_builder.build(invoice)

        submission = ETaxSubmission(
            id=uuid4(),
            company_id=invoice.company_id,
            invoice_id=invoice.id,
            xml_payload=xml,
            status=ETaxStatus.PENDING,
            reference_number=None,
            submitted_at=None,
            response_message=None,
            retry_count=0,
            created_at=datetime.utcnow(),
        )
        async with self.uow.transaction():
            await self.submissions.save(submission)
        return submission


# ============================================================
# 3. Tax Reports (ภ.พ.30)
# ============================================================

@dataclass
class GeneratePp30ReportCommand:
    company_id: UUID
    year: int
    month: int


class GeneratePp30ReportUseCase:
    """
    ภ.พ.30 — รายงานภาษีมูลค่าเพิ่ม
    Output:
    - ภาษีขาย (output VAT)
    - ภาษีซื้อ (input VAT)
    - ภาษีที่ต้องชำระ/ขอคืน
    """

    def __init__(self, invoices, purchases):
        ...

    async def execute(self, cmd: GeneratePp30ReportCommand) -> dict:
        output_vat = await self._aggregate_output_vat(cmd)
        input_vat = await self._aggregate_input_vat(cmd)
        return {
            "period": f"{cmd.year}-{cmd.month:02d}",
            "output_vat": str(output_vat),
            "input_vat": str(input_vat),
            "net_payable": str(max(output_vat - input_vat, Decimal("0"))),
            "net_refundable": str(max(input_vat - output_vat, Decimal("0"))),
        }


# ============================================================
# 4. Tax Codes Lookup
# ============================================================

class GetTaxCodesUseCase:
    """
    ดึง tax codes ที่ active ในบริษัท
    """

    async def execute(self, company_id: UUID) -> list[dict]:
        # อ่านจาก config
        ...
```

## 5.3.5 Tax Codes มาตรฐาน

```python
# app/modules/tax/domain/tax_codes_seed.py

DEFAULT_TAX_CODES = [
    # VAT
    ("VAT7", "vat", Decimal("0.07"), "ภาษีมูลค่าเพิ่ม 7%"),
    ("VAT0", "vat", Decimal("0.00"), "ภาษีมูลค่าเพิ่ม 0% (ส่งออก)"),
    ("VATEX", "vat", Decimal("0.00"), "ยกเว้น VAT (อาหารสด)"),

    # WHT
    ("WHT1", "wht", Decimal("0.01"), "หัก ณ ที่จ่าย 1% (ค่าขนส่ง)"),
    ("WHT2", "wht", Decimal("0.02"), "หัก ณ ที่จ่าย 2% (ค่าโฆษณา)"),
    ("WHT3", "wht", Decimal("0.03"), "หัก ณ ที่จ่าย 3% (ค่าบริการ)"),
    ("WHT5", "wht", Decimal("0.05"), "หัก ณ ที่จ่าย 5% (ค่าเช่า)"),
    ("WHT10", "wht", Decimal("0.10"), "หัก ณ ที่จ่าย 10% (เงินปันผล)"),
]
```

## 5.3.6 Database Schema

```sql
CREATE TABLE tax_rates (
    id             UUID PRIMARY KEY,
    company_id     UUID NOT NULL,
    tax_type       VARCHAR(20) NOT NULL,
    code           VARCHAR(20) NOT NULL,
    rate           NUMERIC(6,4) NOT NULL,
    description    VARCHAR(255),
    effective_from DATE NOT NULL,
    effective_to   DATE,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (company_id, code, effective_from)
);

CREATE INDEX ix_tax_company_type ON tax_rates (company_id, tax_type)
    WHERE is_active = TRUE;

CREATE TABLE etax_submissions (
    id               UUID PRIMARY KEY,
    company_id       UUID NOT NULL,
    invoice_id       UUID NOT NULL,
    xml_payload      TEXT NOT NULL,
    status           VARCHAR(20) NOT NULL,
    reference_number VARCHAR(100),
    submitted_at     TIMESTAMPTZ,
    response_message TEXT,
    retry_count      INT NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL
);

CREATE INDEX ix_etax_company_status ON etax_submissions (company_id, status);
CREATE INDEX ix_etax_invoice ON etax_submissions (invoice_id);
```

## 5.3.7 Presentation — API

```python
# app/modules/tax/presentation/routers.py

router = APIRouter(prefix="/api/v1/tax", tags=["Tax"])


@router.get("/codes")
async def list_tax_codes(user = Depends(require_permission("config:read"))):
    ...


@router.post("/calculate/wht")
async def calculate_wht(
    body: CalculateWhtRequest,
    user = Depends(require_permission("invoice:read")),
    use_case = Depends(get_calculate_wht_use_case),
):
    return use_case.execute(...)


@router.post("/invoices/{invoice_id}/submit-etax")
async def submit_etax(
    invoice_id: UUID,
    user = Depends(require_permission("invoice:create")),
):
    ...


@router.get("/reports/pp30")
async def pp30_report(
    year: int, month: int,
    user = Depends(require_permission("report:read")),
):
    """ภ.พ.30"""
    ...


@router.get("/reports/wht")
async def wht_report(
    year: int, month: int,
    user = Depends(require_permission("report:read")),
):
    """รายงานภาษีหัก ณ ที่จ่าย"""
    ...
```

## 5.3.8 Folder Structure

```text
app/modules/tax/
├── domain/
│   ├── entities.py            # TaxRate, ETaxSubmission
│   ├── value_objects.py       # TaxType, TaxCode, WhtIncomeType, ETaxStatus
│   ├── tax_codes_seed.py      # DEFAULT_TAX_CODES
│   └── errors.py
├── application/
│   ├── calculators.py         # VatCalculatorService, WhtCalculatorService
│   ├── use_cases.py           # CalculateWht, SubmitETax, GeneratePp30Report
│   └── interfaces.py
├── infrastructure/
│   ├── models.py              # TaxRateModel, ETaxSubmissionModel
│   ├── repositories.py
│   └── etax/
│       ├── xml_builder.py     # สร้าง XML ตาม Revenue Dept spec
│       └── rd_client.py       # HTTP client ส่ง e-Tax
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── test_wht_calculator.py
    ├── test_pp30_report.py
    └── test_etax_xml.py
```

## 5.3.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (VAT) / 2 (WHT + e-Tax) |
| **DoD** | ✅ VAT 4 โหมดผ่าน test<br>✅ WHT ทุกประเภทผ่าน test<br>✅ Tax code seed ครบ<br>✅ ภ.พ.30 คำนวณถูก<br>✅ e-Tax XML validate ผ่าน<br>✅ Tax rate versioned |

---

# 📊 PART 5 — สรุป

## Dependency Graph

```text
                    ┌────────────────────┐
                    │  core/money (L0)   │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    │  core/config (L0)  │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    │      tax           │  ← VAT/WHT/e-Tax
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   invoice     │───►│    ledger     │───►│  (payment)    │
│               │    │               │    │  Part 6       │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │
        │ InvoiceIssued       │ LedgerPosted
        ▼                     ▼
  (outbox → Kafka)     (outbox → Kafka)
```

## Integration Flow (ครบ)

```text
1. Order → OrderConfirmed
2. Invoice.create_draft() → add_line() × N → issue()
   ├─ ออกเลข invoice (SELECT FOR UPDATE)
   ├─ คำนวณ VAT (Tax)
   ├─ verify_totals()
   ├─ Read-back
   ├─ Audit: INVOICE_ISSUED
   └─ Publish: InvoiceIssued
3. Ledger.InvoiceIssuedLedgerHandler
   ├─ สร้าง JournalEntry
   │   Dr. ลูกหนี้การค้า     grand_total
   │     Cr. รายได้          subtotal
   │     Cr. ภาษีขาย (VAT)   vat_total
   ├─ post() → verify debit = credit
   ├─ Read-back
   ├─ Audit: LEDGER_POSTED
   └─ Publish: LedgerPosted
4. Payment (Part 6)
   └─ mark_paid() → InvoicePaid → ledger reversal สำหรับ AR
5. Accounting Gateway (Part 6)
   └─ SyncToCloud (outbox → Thai Cloud Accounting)
```

## Checklist รวม Part 5

```text
┌─────────────────────────────────────────────────────────────────┐
│  MONEY PATH CORE — FINAL CHECKLIST                              │
├─────────────────────────────────────────────────────────────────┤
│  invoice                                                        │
│   □ verify_totals ผ่านทุกใบ                                    │
│   □ Read-back verify หลัง issue                                │
│   □ Idempotency: ยิงซ้ำ 100 → 1                                │
│   □ Concurrency: ออกพร้อม 10 thread → เลขไม่ซ้ำ               │
│   □ Cancel → emit InvoiceCancelled                             │
│   □ State machine: DRAFT → ISSUED → PAID/CANCELLED             │
│   □ Invoice number unique per company per year                 │
│   □ Snapshot customer ณ เวลาออก                                │
│   □ Property test: total = Σlines + VAT                        │
├─────────────────────────────────────────────────────────────────┤
│  ledger                                                         │
│   □ post journal ตรวจ debit = credit                           │
│   □ DB CHECK constraint (defense in depth)                     │
│   □ Reversal ทำงาน — ไม่ลบ entry                              │
│   □ Chart of Accounts seed ครบ (Thai standard)                 │
│   □ Invoice handler post journal อัตโนมัติ                     │
│   □ Trial balance: Σdebit = Σcredit                            │
│   □ Period close → block post ย้อนหลัง                         │
├─────────────────────────────────────────────────────────────────┤
│  tax                                                            │
│   □ VAT 4 โหมดผ่าน test                                        │
│   □ WHT ทุกประเภทผ่าน test                                     │
│   □ Tax code seed ครบ                                          │
│   □ ภ.พ.30 คำนวณถูก                                            │
│   □ e-Tax XML validate ผ่าน                                    │
│   □ Tax rate versioned ต่อ company                             │
└─────────────────────────────────────────────────────────────────┘
```

## ลำดับการ Implement

```text
Week 1-2:
  Day 1-3: invoice domain (entities, value_objects, events)
  Day 4-5: invoice use cases (draft, add_line, issue, cancel)
  Day 6-7: invoice infrastructure + presentation
  Day 8-10: ledger domain + use cases
  Day 11-12: ledger handler (ฟัง InvoiceIssued)
  Day 13-14: tax module + integration test
  Day 15: Money path E2E test
```

## Metrics ที่ต้องติดตาม

| Metric | Target | ตรวจโดย |
|--------|--------|---------|
| Invoice issuance success rate | 100% | monitoring |
| Read-back mismatch | 0 | reconciliation |
| Idempotency duplicate | 0 | reconciliation |
| Journal debit ≠ credit | 0 | DB CHECK + recon |
| Orphan ledger entries | 0 | reconciliation |
| VAT error rate | 0 | property test |
| Invoice number collision | 0 | DB constraint |

---

## 🔜 Part 6 (ตอนถัดไป) — Money Path Completion

จะลงรายละเอียด:
- **Payment** — รับชำระ, allocation, refund, partial payment
- **Accounting Gateway** — Outbox pattern, Thai Cloud Accounting sync, retry, reconciliation

พร้อม folder structure, domain model, use case, infrastructure, presentation, tests และ dependencies ครบเหมือน Part 3-5

---
 