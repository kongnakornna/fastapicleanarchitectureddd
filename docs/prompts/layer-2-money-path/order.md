### 🎯 ตัวอย่างเต็ม: Module `order`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `order` |
| **Layer** | `2` (Money Path) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `customer`, `product`, `pricing`, `money`, `idempotency`, `audit`, `events` |
| **Domain Concepts** | `Order` (entity), `OrderLine` (VO), `OrderStatus` (enum), `OrderTotal` (VO) |
| **Prefix** | `ord` |
| **Tables** | `tenant_ord.orders`, `tenant_ord.order_lines` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `order`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- **Money Path** — ต้อง idempotent, audit, read-back 100%
- Order lifecycle: DRAFT → CONFIRMED → FULFILLED → INVOICED → CANCELLED
- Invariants: `total = sum(lines) - discount + VAT`
- ห้ามแก้ order ที่ CONFIRMED แล้ว (immutable lines)

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Order**
```python
@dataclass
class Order(BaseEntity):
    """Order entity — เอนทิตีคำสั่งซื้อ"""
    order_number: str = ""
    customer_id: str = ""
    lines: list = field(default_factory=list)
    subtotal: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    vat: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    status: str = "DRAFT"
    confirmed_at: datetime | None = None
    notes: str = ""

    def __post_init__(self):
        self._validate()
        self._recalculate()

    def _validate(self) -> None:
        if not self.customer_id:
            raise DomainError("Customer ID is required")
        if not self.lines:
            raise DomainError("Order must have at least one line")

    def _recalculate(self) -> None:
        self.subtotal = sum(l.amount for l in self.lines)
        self.vat = (self.subtotal - self.discount) * Decimal("0.07")
        self.total = self.subtotal - self.discount + self.vat

    def add_line(self, line: "OrderLine") -> None:
        if self.status != "DRAFT":
            raise DomainError(f"Cannot add line to {self.status} order")
        if any(l.product_id == line.product_id for l in self.lines):
            raise DomainError(f"Product {line.product_id} already in order")
        self.lines.append(line)
        self._recalculate()

    def remove_line(self, product_id: str) -> None:
        if self.status != "DRAFT":
            raise DomainError(f"Cannot remove line from {self.status} order")
        self.lines = [l for l in self.lines if l.product_id != product_id]
        self._recalculate()

    def apply_discount(self, amount: Decimal) -> None:
        if self.status != "DRAFT":
            raise DomainError("Cannot apply discount to non-draft order")
        if amount < 0 or amount > self.subtotal:
            raise DomainError(f"Invalid discount: {amount}")
        self.discount = amount
        self._recalculate()

    def confirm(self) -> None:
        if self.status != "DRAFT":
            raise DomainError(f"Cannot confirm {self.status} order")
        self.status = "CONFIRMED"
        self.confirmed_at = datetime.utcnow()

    def fulfill(self) -> None:
        if self.status != "CONFIRMED":
            raise DomainError(f"Cannot fulfill {self.status} order")
        self.status = "FULFILLED"

    def invoice(self) -> None:
        if self.status != "FULFILLED":
            raise DomainError(f"Cannot invoice {self.status} order")
        self.status = "INVOICED"

    def cancel(self, reason: str) -> None:
        if self.status in ("INVOICED", "CANCELLED"):
            raise DomainError(f"Cannot cancel {self.status} order")
        self.status = "CANCELLED"
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class OrderLine:
    """Order line — รายการในคำสั่งซื้อ"""
    product_id: str
    qty: Decimal
    unit_price: Decimal
    discount_pct: Decimal = Decimal("0.00")

    @property
    def amount(self) -> Decimal:
        return (self.qty * self.unit_price * (Decimal("1") - self.discount_pct)).quantize(Decimal("0.01"))

    def __post_init__(self):
        if self.qty <= 0:
            raise DomainError("Quantity must be positive")
        if self.unit_price < 0:
            raise DomainError("Unit price cannot be negative")
        if not 0 <= self.discount_pct < 1:
            raise DomainError("Discount pct must be 0-1")

@dataclass(frozen=True)
class OrderNumber:
    """Order number VO — วัตถุเลขที่คำสั่งซื้อ"""
    value: str
    PATTERN = r"^ORD-\d{6}-\d{4}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid order number: {self.value}")

@dataclass(frozen=True)
class OrderTotal:
    """Order total VO — วัตถุยอดรวม"""
    subtotal: Decimal
    discount: Decimal
    vat: Decimal
    total: Decimal

    def __post_init__(self):
        expected = self.subtotal - self.discount + self.vat
        if abs(self.total - expected) > Decimal("0.01"):
            raise DomainError(f"Total mismatch: {self.total} != {expected}")
```

**`domain/enums.py`**
```python
class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    FULFILLED = "FULFILLED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"

class OrderChannel(str, Enum):
    POS = "POS"
    ONLINE = "ONLINE"
    PHONE = "PHONE"
    LINE = "LINE"
    WHOLESALE = "WHOLESALE"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IOrderRepository(Protocol):
    async def save(self, order: Order) -> Order: ...
    async def get_by_id(self, id: str) -> Order | None: ...
    async def get_by_number(self, number: str) -> Order | None: ...
    async def list(self, filters: dict, page: int, limit: int) -> tuple[list[Order], int]: ...

class IOrderCache(Protocol):
    async def get(self, id: str) -> Order | None: ...
    async def insert(self, id: str, order: Order) -> None: ...
    async def delete(self, id: str) -> None: ...

class IOrderNumberGenerator(Protocol):
    async def generate(self) -> str: ...

class IInventoryService(Protocol):
    async def reserve(self, product_id: str, qty: Decimal, ref: str) -> None: ...
    async def release(self, product_id: str, qty: Decimal, ref: str) -> None: ...
```

**`application/use_cases.py`**
```python
class OrderUseCases:
    """Order use cases — กรณีการใช้งานคำสั่งซื้อ"""

    def __init__(self, repo, cache, number_gen, inventory, idempotency, audit, events):
        ...

    async def create_order(self, payload: dict, idem_key: str) -> Order:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            order = Order(**payload)
            order.order_number = await self.number_gen.generate()
            order = await self.repo.save(order)

            verified = await self.repo.get_by_id(order.id)
            if not verified or verified.total != order.total:
                raise OrderException("Read-back failed")

            await self.audit.log("order.created", order.id)
            await self.idempotency.set(idem_key, order)
            await self.events.publish("OrderCreated", order)
            return order
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_order")
            raise OrderException()

    async def add_line(self, order_id: str, line: "OrderLine") -> Order:
        try:
            order = await self.repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException()
            order.add_line(line)
            order = await self.repo.save(order)
            await self.cache.delete(order_id)
            await self.audit.log("order.line_added", order_id)
            return order
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in add_line")
            raise OrderException()

    async def confirm_order(self, order_id: str) -> Order:
        try:
            order = await self.repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException()

            # Reserve inventory
            for line in order.lines:
                await self.inventory.reserve(line.product_id, line.qty, order.order_number)

            order.confirm()
            order = await self.repo.save(order)
            await self.cache.delete(order_id)
            await self.audit.log("order.confirmed", order_id)
            await self.events.publish("OrderConfirmed", order)
            return order
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in confirm_order")
            raise OrderException()

    async def cancel_order(self, order_id: str, reason: str) -> Order:
        try:
            order = await self.repo.get_by_id(order_id)
            if not order:
                raise OrderNotFoundException()

            # Release inventory if confirmed
            if order.status == "CONFIRMED":
                for line in order.lines:
                    await self.inventory.release(line.product_id, line.qty, order.order_number)

            order.cancel(reason)
            order = await self.repo.save(order)
            await self.cache.delete(order_id)
            await self.audit.log("order.cancelled", order_id)
            await self.events.publish("OrderCancelled", {"id": order_id, "reason": reason})
            return order
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in cancel_order")
            raise OrderException()
```

**`application/mappers.py`** — `OrderMapper`
**`application/exceptions.py`** — `OrderException`, `OrderNotFoundException`, `OrderNumberConflictException`
**`application/utils.py`** — `calculate_totals()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class OrderModel(BaseModel):
    __tablename__ = "orders"
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    discount = Column(Numeric(15, 2), nullable=False, default=0)
    vat = Column(Numeric(15, 2), nullable=False, default=0)
    total = Column(Numeric(15, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, index=True, default="DRAFT")
    confirmed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    lines = relationship("OrderLineModel", back_populates="order", cascade="all, delete-orphan")

class OrderLineModel(BaseModel):
    __tablename__ = "order_lines"
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(36), nullable=False, index=True)
    qty = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_pct = Column(Numeric(5, 4), default=0)
    amount = Column(Numeric(15, 2), nullable=False)
    order = relationship("OrderModel", back_populates="lines")
```

**`infrastructure/repositories.py`** — `PostgresOrderRepository`
**`infrastructure/caches.py`** — `RedisOrderCache`
**`infrastructure/services.py`**
```python
class PostgresOrderNumberGenerator:
    """Order number generator — สร้างเลขที่คำสั่งซื้อ"""
    def __init__(self, session):
        self.session = session

    async def generate(self) -> str:
        result = await self.session.execute(text("SELECT nextval('order_number_seq')"))
        seq = result.scalar()
        return f"ORD-{datetime.utcnow():%Y%m}-{seq:04d}"
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.post("/", status_code=201)
async def create_order(
    payload: OrderCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    ...): ...

@router.get("/{id}/")
async def get_order(id: str, ...): ...

@router.get("/")
async def list_orders(filters: OrderQuery, ...): ...

@router.post("/{id}/lines/")
async def add_line(id: str, payload: OrderLineCreate, ...): ...

@router.delete("/{id}/lines/{product_id}/")
async def remove_line(id: str, product_id: str, ...): ...

@router.patch("/{id}/confirm/")
async def confirm_order(id: str, ...): ...

@router.patch("/{id}/cancel/")
async def cancel_order(id: str, payload: CancelRequest, ...): ...
```

**`presentation/schemas.py`** — `OrderCreate`, `OrderResponse`, `OrderLineCreate`, `OrderQuery`, `CancelRequest`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_order_use_cases()`

### 5. Invariants
- `order_number` unique + format `ORD-YYYYMM-XXXX`
- `total == subtotal - discount + VAT`
- ห้ามแก้ lines เมื่อ status != DRAFT
- Confirm → reserve inventory (atomic)
- Cancel → release inventory (ถ้า confirmed)

### 6. Domain Events
- `OrderCreated`, `OrderConfirmed`, `OrderFulfilled`, `OrderInvoiced`, `OrderCancelled`, `OrderLineAdded`, `OrderLineRemoved`

### 7. Tests
```python
async def test_create_order(): ...
async def test_total_invariant():
    """Property: total == subtotal - discount + VAT"""
    for _ in range(100):
        lines = [random_line() for _ in range(random.randint(1, 10))]
        order = Order(customer_id="c1", lines=lines)
        assert order.total == order.subtotal - order.discount + order.vat

async def test_cannot_add_line_to_confirmed(): ...
async def test_confirm_reserves_inventory(): ...
async def test_cancel_releases_inventory(): ...
async def test_number_unique_concurrent(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `order`

**`db/migrations/V001__create_order.sql`**
```sql
BEGIN;

CREATE SEQUENCE IF NOT EXISTS order_number_seq START 1;

CREATE TABLE tenant_ord.orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    order_number    VARCHAR(50) NOT NULL UNIQUE,
    customer_id     UUID NOT NULL,
    subtotal        NUMERIC(15,2) NOT NULL DEFAULT 0,
    discount        NUMERIC(15,2) NOT NULL DEFAULT 0,
    vat             NUMERIC(15,2) NOT NULL DEFAULT 0,
    total           NUMERIC(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    confirmed_at    TIMESTAMPTZ,
    notes           TEXT,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT ck_orders_total CHECK (total = subtotal - discount + vat)
);

CREATE INDEX ix_orders_customer ON tenant_ord.orders(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX ix_orders_status ON tenant_ord.orders(status) WHERE deleted_at IS NULL;
CREATE INDEX ix_orders_number ON tenant_ord.orders(order_number);

CREATE TABLE tenant_ord.order_lines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    order_id        UUID NOT NULL REFERENCES tenant_ord.orders(id) ON DELETE CASCADE,
    product_id      UUID NOT NULL,
    qty             NUMERIC(15,3) NOT NULL CHECK (qty > 0),
    unit_price      NUMERIC(15,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct    NUMERIC(5,4) NOT NULL DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct < 1),
    amount          NUMERIC(15,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_order_product UNIQUE (order_id, product_id)
);

CREATE INDEX ix_order_lines_order ON tenant_ord.order_lines(order_id);
CREATE INDEX ix_order_lines_product ON tenant_ord.order_lines(product_id);

ALTER TABLE tenant_ord.orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_orders_tenant ON tenant_ord.orders
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_ord.order_lines ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_order_lines_tenant ON tenant_ord.order_lines
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_order.sql`**
```sql
BEGIN;
-- Seed sample orders for testing
-- INSERT INTO tenant_ord.orders (...) VALUES (...);
COMMIT;
```

**`db/migrations/V003__rollback_order.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_ord.order_lines CASCADE;
DROP TABLE IF EXISTS tenant_ord.orders CASCADE;
DROP SEQUENCE IF EXISTS order_number_seq;
COMMIT;
```

### 🧪 Tests สำหรับ `order`

**`tests/unit/test_order.py`**
```python
import pytest
from decimal import Decimal
from app.modules.order.domain.entities import Order
from app.modules.order.domain.value_objects import OrderLine

class TestOrderDomain:
    def test_create_valid(self):
        line = OrderLine(product_id="p1", qty=Decimal("2"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        assert o.subtotal == Decimal("200.00")
        assert o.total == Decimal("214.00")  # 200 + 7% VAT

    def test_total_invariant(self):
        """Property: total == subtotal - discount + VAT"""
        line = OrderLine(product_id="p1", qty=Decimal("1"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        o.apply_discount(Decimal("10"))
        assert o.total == o.subtotal - o.discount + o.vat

    def test_cannot_add_line_to_confirmed(self):
        line = OrderLine(product_id="p1", qty=Decimal("1"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        o.confirm()
        with pytest.raises(Exception):
            o.add_line(OrderLine(product_id="p2", qty=Decimal("1"), unit_price=Decimal("50")))

    def test_duplicate_product_raises(self):
        line = OrderLine(product_id="p1", qty=Decimal("1"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        with pytest.raises(Exception):
            o.add_line(OrderLine(product_id="p1", qty=Decimal("2"), unit_price=Decimal("100")))

    def test_cancel_after_invoice_raises(self):
        line = OrderLine(product_id="p1", qty=Decimal("1"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        o.confirm()
        o.fulfill()
        o.invoice()
        with pytest.raises(Exception):
            o.cancel("test")
```

**`tests/integration/test_order_repository.py`** — testcontainers + transaction test
**`tests/property/test_order_invariants.py`** — hypothesis: random lines
**`tests/manual/manual_test_order.md`** — manual test cases

---

## ✅ สรุป Layer 2 (Money Path) — 7/65 ไฟล์

| # | Module | Prefix | Entities | Tables | Output |
|---|---|---|---|---|---|
| 2.1 | `order` | `ord` | Order, OrderLine | `orders`, `order_lines` | 23 ไฟล์ |
| 2.2 | `invoice` | `inv` | Invoice, InvoiceLine | `invoices`, `invoice_lines` | 23 ไฟล์ |
| 2.3 | `ledger` | `led` | JournalEntry, LedgerAccount | `journal_entries`, `ledger_accounts` | 23 ไฟล์ |
| 2.4 | `payment` | `pay` | Payment, PaymentAllocation | `payments`, `payment_allocations` | 23 ไฟล์ |
| 2.5 | `accounting_gateway` | `acg` | AccountingSync | `accounting_syncs` | 23 ไฟล์ |
| 2.6 | `tax` | `tax` | TaxRule, TaxReport | `tax_rules`, `tax_reports` | 23 ไฟล์ |
| 2.7 | `reconciliation` | `rec` | Reconciliation, MatchRecord | `reconciliations`, `match_records` | 23 ไฟล์ |

**Layer 2 เสร็จสมบูรณ์ — ต่อไปคือ Layer 3 (Goods Path)**

---
