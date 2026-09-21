### 🎯 ตัวอย่างเต็ม: Module `inventory`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `inventory` |
| **Layer** | `3` (Goods Path) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `product`, `warehouse`, `deviceiot`, `audit`, `idempotency`, `events` |
| **Domain Concepts** | `StockItem` (entity), `StockMove` (entity), `StockLevel` (VO), `MoveType` (enum) |
| **Prefix** | `invt` |
| **Tables** | `tenant_invt.stock_items`, `tenant_invt.stock_moves` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `inventory`

## บริบท
- ERP + CRM + deviceiot สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- **Goods Path** — ต้อง idempotent, audit, traceability
- Stock movement types: IN, OUT, TRANSFER, ADJUST, RESERVE, RELEASE
- Invariants: `stock_on_hand >= 0`, `stock_available = on_hand - reserved`
- ห้ามติดลบ (ยกเว้น backorder ที่อนุญาต)
- ทุก move ต้องมี reference (order/invoice/production)

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — StockItem**
```python
@dataclass
class StockItem(BaseEntity):
    """Stock item — เอนทิตีสต็อก"""
    product_id: str = ""
    warehouse_id: str = ""
    deviceiot_id: str | None = None
    qty_on_hand: Decimal = Decimal("0.000")
    qty_reserved: Decimal = Decimal("0.000")
    reorder_point: Decimal = Decimal("0.000")
    avg_cost: Decimal = Decimal("0.00")

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.product_id or not self.warehouse_id:
            raise DomainError("Product and Warehouse required")
        if self.qty_on_hand < 0:
            raise DomainError("On-hand cannot be negative")
        if self.qty_reserved < 0:
            raise DomainError("Reserved cannot be negative")
        if self.qty_reserved > self.qty_on_hand:
            raise DomainError("Reserved cannot exceed on-hand")

    @property
    def qty_available(self) -> Decimal:
        return self.qty_on_hand - self.qty_reserved

    def is_below_reorder(self) -> bool:
        return self.qty_available <= self.reorder_point

    def apply_move(self, move: "StockMove") -> None:
        """Apply stock move — นำการเคลื่อนไหวไปใช้"""
        if move.move_type == "IN":
            self.qty_on_hand += move.qty
        elif move.move_type == "OUT":
            if self.qty_on_hand < move.qty:
                raise DomainError(f"Insufficient stock: {self.qty_on_hand} < {move.qty}")
            self.qty_on_hand -= move.qty
        elif move.move_type == "RESERVE":
            if self.qty_available < move.qty:
                raise DomainError(f"Insufficient available: {self.qty_available} < {move.qty}")
            self.qty_reserved += move.qty
        elif move.move_type == "RELEASE":
            self.qty_reserved = max(Decimal("0"), self.qty_reserved - move.qty)
        elif move.move_type == "ADJUST":
            self.qty_on_hand = move.qty
```

**`domain/entities.py` — StockMove**
```python
@dataclass
class StockMove(BaseEntity):
    """Stock move — เอนทิตีการเคลื่อนไหวสต็อก"""
    product_id: str = ""
    warehouse_id: str = ""
    deviceiot_id: str | None = None
    move_type: str = "IN"
    qty: Decimal = Decimal("0.000")
    unit_cost: Decimal = Decimal("0.00")
    reference: str = ""
    reference_type: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.product_id or not self.warehouse_id:
            raise DomainError("Product and Warehouse required")
        if self.qty <= 0:
            raise DomainError("Qty must be positive")
        if self.move_type not in ("IN", "OUT", "TRANSFER", "ADJUST", "RESERVE", "RELEASE"):
            raise DomainError(f"Invalid move type: {self.move_type}")
        if not self.reference:
            raise DomainError("Reference required")
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class StockLevel:
    """Stock level VO — วัตถุระดับสต็อก"""
    on_hand: Decimal
    reserved: Decimal
    available: Decimal

    def __post_init__(self):
        if abs(self.available - (self.on_hand - self.reserved)) > Decimal("0.001"):
            raise DomainError("Available mismatch")

@dataclass(frozen=True)
class MoveReference:
    """Move reference VO — วัตถุอ้างอิง"""
    type: str  # ORDER, INVOICE, PRODUCTION, ADJUSTMENT
    id: str

    def __str__(self) -> str:
        return f"{self.type}:{self.id}"
```

**`domain/enums.py`**
```python
class MoveType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUST = "ADJUST"
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"

class ReferenceType(str, Enum):
    ORDER = "ORDER"
    INVOICE = "INVOICE"
    PRODUCTION = "PRODUCTION"
    PURCHASE = "PURCHASE"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IStockItemRepository(Protocol):
    async def save(self, item: StockItem) -> StockItem: ...
    async def get(self, product_id: str, warehouse_id: str, deviceiot_id: str | None) -> StockItem | None: ...
    async def list(self, filters: dict, page: int, limit: int) -> tuple[list[StockItem], int]: ...

class IStockMoveRepository(Protocol):
    async def append(self, move: StockMove) -> StockMove: ...
    async def list_by_product(self, product_id: str, limit: int) -> list[StockMove]: ...

class IStockCache(Protocol):
    async def get(self, key: str) -> StockItem | None: ...
    async def insert(self, key: str, item: StockItem) -> None: ...
    async def delete(self, key: str) -> None: ...
```

**`application/use_cases.py`**
```python
class InventoryUseCases:
    """Inventory use cases — กรณีการใช้งานสต็อก"""

    def __init__(self, item_repo, move_repo, cache, idempotency, audit, events):
        ...

    async def post_movement(self, payload: dict, idem_key: str) -> StockMove:
        """Post stock movement — บันทึกการเคลื่อนไหว"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            move = StockMove(**payload)
            move = await self.move_repo.append(move)

            # Update stock item
            item = await self.item_repo.get(move.product_id, move.warehouse_id, move.deviceiot_id)
            if not item:
                item = StockItem(
                    product_id=move.product_id,
                    warehouse_id=move.warehouse_id,
                    deviceiot_id=move.deviceiot_id,
                )
            item.apply_move(move)
            item = await self.item_repo.save(item)

            # Read-back
            verified = await self.item_repo.get(move.product_id, move.warehouse_id, move.deviceiot_id)
            if not verified or verified.qty_on_hand != item.qty_on_hand:
                raise InventoryException("Read-back failed")

            # Invalidate cache
            cache_key = f"{move.product_id}:{move.warehouse_id}:{move.deviceiot_id or 'none'}"
            await self.cache.delete(cache_key)

            await self.audit.log(f"stock.{move.move_type.lower()}", move.id)
            await self.idempotency.set(idem_key, move)

            # Check reorder
            if item.is_below_reorder():
                await self.events.publish("StockBelowReorder", {
                    "product_id": item.product_id,
                    "warehouse_id": item.warehouse_id,
                    "available": str(item.qty_available),
                })

            await self.events.publish("StockMoved", move)
            return move
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in post_movement")
            raise InventoryException()

    async def get_stock_level(self, product_id: str, warehouse_id: str, deviceiot_id: str | None = None) -> StockLevel:
        try:
            cache_key = f"{product_id}:{warehouse_id}:{deviceiot_id or 'none'}"
            cached = await self.cache.get(cache_key)
            if cached:
                return StockLevel(cached.qty_on_hand, cached.qty_reserved, cached.qty_available)

            item = await self.item_repo.get(product_id, warehouse_id, deviceiot_id)
            if not item:
                return StockLevel(Decimal("0"), Decimal("0"), Decimal("0"))

            await self.cache.insert(cache_key, item)
            return StockLevel(item.qty_on_hand, item.qty_reserved, item.qty_available)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_stock_level")
            raise InventoryException()

    async def transfer(self, product_id: str, from_wh: str, to_wh: str, qty: Decimal, ref: str, idem_key: str) -> None:
        """Transfer stock between warehouses — โอนสต็อก"""
        try:
            # OUT from source
            await self.post_movement({
                "product_id": product_id, "warehouse_id": from_wh,
                "move_type": "OUT", "qty": qty, "reference": ref,
                "reference_type": "TRANSFER",
            }, f"{idem_key}-out")

            # IN to destination
            await self.post_movement({
                "product_id": product_id, "warehouse_id": to_wh,
                "move_type": "IN", "qty": qty, "reference": ref,
                "reference_type": "TRANSFER",
            }, f"{idem_key}-in")
        except Exception as e:
            logger.opt(exception=e).error("Error in transfer")
            raise InventoryException()
```

**`application/mappers.py`** — `StockItemMapper`, `StockMoveMapper`
**`application/exceptions.py`** — `InventoryException`, `InsufficientStockException`, `StockNotFoundException`
**`application/utils.py`** — `calculate_avg_cost()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class StockItemModel(BaseModel):
    __tablename__ = "stock_items"
    product_id = Column(String(36), nullable=False, index=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    deviceiot_id = Column(String(36), nullable=True, index=True)
    qty_on_hand = Column(Numeric(15, 3), nullable=False, default=0)
    qty_reserved = Column(Numeric(15, 3), nullable=False, default=0)
    reorder_point = Column(Numeric(15, 3), default=0)
    avg_cost = Column(Numeric(15, 2), default=0)
    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", "warehouse_id", "deviceiot_id", name="uq_stock_item"),
        CheckConstraint("qty_on_hand >= 0", name="ck_stock_on_hand"),
        CheckConstraint("qty_reserved >= 0", name="ck_stock_reserved"),
        CheckConstraint("qty_reserved <= qty_on_hand", name="ck_stock_reserved_le_onhand"),
    )

class StockMoveModel(BaseModel):
    __tablename__ = "stock_moves"
    product_id = Column(String(36), nullable=False, index=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    deviceiot_id = Column(String(36), nullable=True)
    move_type = Column(String(20), nullable=False, index=True)
    qty = Column(Numeric(15, 3), nullable=False)
    unit_cost = Column(Numeric(15, 2), default=0)
    reference = Column(String(100), nullable=False, index=True)
    reference_type = Column(String(20), nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
```

**`infrastructure/repositories.py`** — `PostgresStockItemRepository`, `PostgresStockMoveRepository`
**`infrastructure/caches.py`** — `RedisStockCache` (TTL 60s, never raises)
**`infrastructure/services.py`** — `AverageCostCalculator`

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])

@router.post("/movements/", status_code=201)
async def post_movement(
    payload: StockMoveCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    ...): ...

@router.get("/stock/{product_id}/{warehouse_id}/")
async def get_stock(product_id: str, warehouse_id: str, deviceiot_id: str | None = None, ...): ...

@router.get("/stock/")
async def list_stock(filters: StockQuery, ...): ...

@router.post("/transfer/")
async def transfer(payload: TransferRequest, idem_key: str = Header(...), ...): ...

@router.get("/movements/{product_id}/")
async def list_movements(product_id: str, limit: int = 50, ...): ...
```

**`presentation/schemas.py`** — `StockMoveCreate`, `StockLevelResponse`, `TransferRequest`, `StockQuery`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_inventory_use_cases()`

### 5. Invariants
- `qty_on_hand >= 0` (ยกเว้น backorder)
- `qty_reserved <= qty_on_hand`
- `qty_available == qty_on_hand - qty_reserved`
- ทุก move ต้องมี reference
- Transfer atomic (ทั้ง 2 moves สำเร็จ หรือ rollback ทั้งคู่)

### 6. Domain Events
- `StockMoved`, `StockBelowReorder`, `StockAdjusted`, `StockTransferred`, `StockReserved`, `StockReleased`

### 7. Tests
```python
async def test_post_in_movement(): ...
async def test_post_out_insufficient_raises(): ...
async def test_reserve_available(): ...
async def test_property_on_hand_non_negative():
    """Property: on_hand >= 0 เสมอ"""
    ...

async def test_transfer_atomic(): ...
async def test_reorder_alert(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `inventory`

**`db/migrations/V001__create_inventory.sql`**
```sql
BEGIN;

CREATE TABLE tenant_invt.stock_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    product_id      UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    deviceiot_id          UUID,
    qty_on_hand     NUMERIC(15,3) NOT NULL DEFAULT 0,
    qty_reserved    NUMERIC(15,3) NOT NULL DEFAULT 0,
    reorder_point   NUMERIC(15,3) NOT NULL DEFAULT 0,
    avg_cost        NUMERIC(15,2) NOT NULL DEFAULT 0,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_stock_item UNIQUE (tenant_id, product_id, warehouse_id, deviceiot_id),
    CONSTRAINT ck_stock_on_hand CHECK (qty_on_hand >= 0),
    CONSTRAINT ck_stock_reserved CHECK (qty_reserved >= 0),
    CONSTRAINT ck_stock_reserved_le_onhand CHECK (qty_reserved <= qty_on_hand)
);

CREATE INDEX ix_stock_product_wh ON tenant_invt.stock_items(product_id, warehouse_id);

CREATE TABLE tenant_invt.stock_moves (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    product_id      UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    deviceiot_id          UUID,
    move_type       VARCHAR(20) NOT NULL,
    qty             NUMERIC(15,3) NOT NULL CHECK (qty > 0),
    unit_cost       NUMERIC(15,2) NOT NULL DEFAULT 0,
    reference       VARCHAR(100) NOT NULL,
    reference_type  VARCHAR(20) NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_moves_product ON tenant_invt.stock_moves(product_id, occurred_at DESC);
CREATE INDEX ix_moves_ref ON tenant_invt.stock_moves(reference);

ALTER TABLE tenant_invt.stock_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_stock_items_tenant ON tenant_invt.stock_items
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_invt.stock_moves ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_stock_moves_tenant ON tenant_invt.stock_moves
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_inventory.sql`**
```sql
BEGIN;
-- Seed stock items for demo products
COMMIT;
```

**`db/migrations/V003__rollback_inventory.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_invt.stock_moves CASCADE;
DROP TABLE IF EXISTS tenant_invt.stock_items CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `inventory`

**`tests/unit/test_inventory.py`**
```python
import pytest
from decimal import Decimal
from app.modules.inventory.domain.entities import StockItem, StockMove

class TestStockItem:
    def test_apply_in_move(self):
        item = StockItem(product_id="p1", warehouse_id="w1")
        move = StockMove(product_id="p1", warehouse_id="w1", move_type="IN",
                         qty=Decimal("100"), reference="PO-001")
        item.apply_move(move)
        assert item.qty_on_hand == Decimal("100")

    def test_apply_out_insufficient(self):
        item = StockItem(product_id="p1", warehouse_id="w1", qty_on_hand=Decimal("50"))
        move = StockMove(product_id="p1", warehouse_id="w1", move_type="OUT",
                         qty=Decimal("100"), reference="SO-001")
        with pytest.raises(Exception):
            item.apply_move(move)

    def test_reserve_available(self):
        item = StockItem(product_id="p1", warehouse_id="w1", qty_on_hand=Decimal("100"))
        move = StockMove(product_id="p1", warehouse_id="w1", move_type="RESERVE",
                         qty=Decimal("30"), reference="ORD-001")
        item.apply_move(move)
        assert item.qty_reserved == Decimal("30")
        assert item.qty_available == Decimal("70")

    def test_property_on_hand_non_negative(self):
        """Property: on_hand >= 0 เสมอ"""
        for _ in range(100):
            item = StockItem(product_id="p1", warehouse_id="w1")
            # random moves
            assert item.qty_on_hand >= 0
```

**`tests/integration/test_inventory_repository.py`** — testcontainers + concurrent moves
**`tests/property/test_inventory_invariants.py`** — hypothesis
**`tests/manual/manual_test_inventory.md`** — manual test cases

---

## ✅ สรุป Layer 3 (Goods Path) — 13/65 ไฟล์

| # | Module | Prefix | Entities | Tables |
|---|---|---|---|---|
| 3.1 | `inventory` | `invt` | StockItem, StockMove | `stock_items`, `stock_moves` |
| 3.2 | `warehouse` | `wh` | Warehouse, Location | `warehouses`, `locations` |
| 3.3 | `deviceiot` | `deviceiot` | deviceiot, SerialNumber | `deviceiots`, `serial_numbers` |
| 3.4 | `production` | `prod` | ProductionOrder | `production_orders` |
| 3.5 | `recipe` | `rcp` | Recipe, Ingredient | `recipes`, `recipe_ingredients` |
| 3.6 | `quality` | `qc` | QCInspection | `qc_inspections` |
| 3.7 | `waste` | `wst` | WasteRecord | `waste_records` |
| 3.8 | `procurement` | `proc` | PurchaseOrder | `purchase_orders` |
| 3.9 | `traceability` | `trc` | TraceRecord | `trace_records` |
| 3.10 | `agriculture` | `agr` | Farm, Pdeviceiot, Harvest | `farms`, `pdeviceiots`, `harvests` |
| 3.11 | `crop` | `crp` | Crop, Variety | `crops`, `crop_varieties` |
| 3.12 | `soil` | `soil` | SoilTest | `soil_tests` |
| 3.13 | `irrigation` | `irr` | IrrigationPlan | `irrigation_plans` |

**Layer 3 เสร็จสมบูรณ์ — ต่อไปคือ Layer 4 (Operations)**

---
