# 📕 PART 8 — Goods Path: Inventory

> **Layer 3: Goods Path** — 3 modules ที่ทำให้สต็อกนิ่ง + traceable
> `inventory` · `warehouse` · `lot`

---

## 8.0 ภาพรวม Goods Path

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                      LAYER 3: GOODS PATH                                      │
│                                                                              │
│   Supplier                                                                   │
│      │                                                                       │
│      │ PO / Receive                                                         │
│      ▼                                                                       │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│   │   warehouse  │◄─────│   inventory  │─────►│     lot      │             │
│   │              │      │              │      │              │             │
│   │ • Warehouse  │      │ • Movement   │      │ • Lot        │             │
│   │ • Zone       │      │ • Balance    │      │ • Expiry     │             │
│   │ • Bin        │      │ • Valuation  │      │ • Trace      │             │
│   │ • Transfer   │      │ • Reservation│      │              │             │
│   └──────┬───────┘      └──────┬───────┘      └──────┬───────┘             │
│          │                     │                     │                     │
│          └─────────────────────┴─────────────────────┘                     │
│                                │                                            │
│                                │ StockPosted                                │
│                                ▼                                            │
│                    ┌───────────────────────┐                               │
│                    │   ledger (Part 5)     │  ← Inventory → COGS           │
│                    │   Dr. COGS            │                               │
│                    │     Cr. Inventory     │                               │
│                    └───────────────────────┘                               │
│                                                                              │
│   Goods Path Invariants:                                                    │
│   • Σ(in) − Σ(out) = balance เสมอ                                          │
│   • ทุก movement ต้องมี reference (PO/SO/Production/Adjustment)            │
│   • Lot expired → ห้าม FEFO หยิบ                                           │
│   • FEFO: หยิบ lot ที่หมดอายุก่อนเสมอ                                      │
│   • Frozen/Chilled: ห้ามข้ามโซนอุณหภูมิ                                    │
│   • Transfer: ต้อง balance ครบ 2 ฝั่ง (from −, to +)                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Goods Path Flow (ครบ):**

```text
   Supplier
      │ PO
      ▼
┌─────────────────┐
│  Receive Stock  │ ①  PO + Lot + Warehouse
│                 │ ②  StockMovement(type=IN)
│                 │ ③  Update StockBalance
│                 │ ④  Update LotBalance
│                 │ ⑤  Ledger: Dr.Inventory / Cr.AP
│                 │ ⑥  Read-back verify
│                 └─────────────────────────────────
        │
        ▼
┌─────────────────┐
│  Production     │ ①  Issue raw materials (FEFO)
│                 │ ②  Consume → Batch
│                 │ ③  Output finished goods
│                 │ ④  Waste
│                 │ ⑤  Ledger: Dr.WIP / Cr.Raw
│                 └─────────────────────────────────
        │
        ▼
┌─────────────────┐
│  Transfer       │ ①  From warehouse → To warehouse
│                 │ ②  StockMovement(OUT) ที่ from
│                 │ ③  StockMovement(IN) ที่ to
│                 │ ④  Atomic (ทั้ง 2 หรือไม่ทำเลย)
│                 └─────────────────────────────────
        │
        ▼
┌─────────────────┐
│  Ship / Sell    │ ①  FEFO pick
│                 │ ②  StockMovement(OUT)
│                 │ ③  Ledger: Dr.COGS / Cr.Inventory
│                 └─────────────────────────────────
```

---

# 🧩 Module 8.1 — `warehouse`

## 8.1.1 Purpose & Scope

**Purpose:** จัดการโครงสร้างทางกายภาพของพื้นที่จัดเก็บ — โกดัง, โซน (อุณหภูมิ), bin, การโอนย้าย

**Scope:**
- ✅ Warehouse (โรงงาน, DC, ร้าน, cold storage)
- ✅ Zone (frozen, chilled, ambient, dry)
- ✅ Bin (ตำแหน่งจัดเก็บ)
- ✅ Transfer (โอนย้ายระหว่าง warehouse)
- ✅ Capacity management
- ✅ Temperature rules
- ❌ ไม่เก็บ stock balance (อยู่ใน `inventory`)
- ❌ ไม่เก็บ lot (อยู่ใน `lot`)

## 8.1.2 Domain Model

```python
# app/modules/warehouse/domain/value_objects.py

from dataclasses import dataclass
from enum import Enum
import re


class WarehouseType(str, Enum):
    FACTORY = "factory"
    DISTRIBUTION_CENTER = "dc"
    RETAIL_STORE = "retail"
    COLD_STORAGE = "cold_storage"
    DARK_KITCHEN = "dark_kitchen"
    TRANSIT = "transit"


class ZoneType(str, Enum):
    """โซนอุณหภูมิ — สำคัญมากสำหรับอาหาร"""
    FROZEN = "frozen"           # -18°C ลงไป
    CHILLED = "chilled"         # 0-8°C
    COOL = "cool"               # 8-15°C
    AMBIENT = "ambient"         # 15-25°C
    DRY = "dry"                 # ห้องแห้ง
    HAZMAT = "hazmat"           # วัตถุอันตราย


ZONE_TEMPERATURE_RANGE: dict[ZoneType, tuple[float, float]] = {
    ZoneType.FROZEN: (-25.0, -18.0),
    ZoneType.CHILLED: (0.0, 8.0),
    ZoneType.COOL: (8.0, 15.0),
    ZoneType.AMBIENT: (15.0, 25.0),
    ZoneType.DRY: (15.0, 30.0),
    ZoneType.HAZMAT: (0.0, 40.0),
}


@dataclass(frozen=True, slots=True)
class WarehouseCode:
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z0-9_-]{2,20}$", self.value):
            raise ValueError(f"WarehouseCode ไม่ถูกต้อง: {self.value}")


@dataclass(frozen=True, slots=True)
class BinCode:
    """
    รหัส bin — รูปแบบ: {zone}-{aisle}-{rack}-{level}
    เช่น FROZEN-A-01-L3
    """
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$", self.value):
            raise ValueError(f"BinCode ไม่ถูกต้อง: {self.value}")


@dataclass(frozen=True, slots=True)
class TemperatureRange:
    min_c: float
    max_c: float
    target_c: float | None = None
    tolerance_c: float = 2.0

    def __post_init__(self) -> None:
        if self.min_c >= self.max_c:
            raise ValueError("min_c ต้อง < max_c")

    def contains(self, temp: float) -> bool:
        return self.min_c <= temp <= self.max_c

    @classmethod
    def for_zone(cls, zone_type: ZoneType) -> "TemperatureRange":
        lo, hi = ZONE_TEMPERATURE_RANGE[zone_type]
        return cls(min_c=lo, max_c=hi)


@dataclass(frozen=True, slots=True)
class Capacity:
    """ความจุ — น้ำหนัก + ปริมาตร + pallets"""
    max_weight_kg: float | None = None
    max_volume_m3: float | None = None
    max_pallets: int | None = None
```

```python
# app/modules/warehouse/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.warehouse.domain.value_objects import (
    WarehouseCode, BinCode, WarehouseType, ZoneType,
    TemperatureRange, Capacity,
)


@dataclass
class Warehouse:
    """
    Warehouse — Aggregate Root

    Invariants:
    - code unique ต่อ company
    - ตอนสร้างต้องมีอย่างน้อย 1 zone
    - cold_storage ต้องมี temperature monitoring
    - ปิด (is_active=False) ได้แต่ห้ามลบถ้ามี stock
    """
    id: UUID
    company_id: UUID
    branch_id: UUID | None
    code: WarehouseCode
    name: str
    warehouse_type: WarehouseType
    address: str
    latitude: float | None
    longitude: float | None
    capacity: Capacity
    is_active: bool
    requires_temperature_monitoring: bool
    created_at: datetime
    updated_at: datetime

    _zones: list["Zone"] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls, *, company_id: UUID, branch_id: UUID | None, code: str,
        name: str, warehouse_type: WarehouseType, address: str,
        capacity: Capacity | None = None,
        latitude: float | None = None, longitude: float | None = None,
    ) -> "Warehouse":
        return cls(
            id=uuid4(),
            company_id=company_id,
            branch_id=branch_id,
            code=WarehouseCode(code),
            name=name,
            warehouse_type=warehouse_type,
            address=address,
            latitude=latitude,
            longitude=longitude,
            capacity=capacity or Capacity(),
            is_active=True,
            requires_temperature_monitoring=warehouse_type in (
                WarehouseType.COLD_STORAGE, WarehouseType.FACTORY,
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def add_zone(self, zone: "Zone") -> None:
        if zone.warehouse_id != self.id:
            raise ValueError("Zone ไม่ได้สังกัด warehouse นี้")
        self._zones.append(zone)
        self.updated_at = datetime.utcnow()

    def find_zone_by_code(self, code: str) -> "Zone | None":
        return next((z for z in self._zones if z.code == code), None)

    @property
    def zones(self) -> list["Zone"]:
        return list(self._zones)


@dataclass
class Zone:
    """
    Zone — พื้นที่ใน warehouse แบ่งตามอุณหภูมิ/ประเภท

    Invariants:
    - code unique ภายใน warehouse
    - temperature range ตาม zone_type
    - 1 zone มี N bins
    """
    id: UUID
    warehouse_id: UUID
    code: str                    # "FROZEN-A", "CHILLED-01"
    name: str
    zone_type: ZoneType
    temperature_range: TemperatureRange
    capacity: Capacity
    is_active: bool
    created_at: datetime

    _bins: list["Bin"] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls, *, warehouse_id: UUID, code: str, name: str,
        zone_type: ZoneType, capacity: Capacity | None = None,
    ) -> "Zone":
        return cls(
            id=uuid4(),
            warehouse_id=warehouse_id,
            code=code,
            name=name,
            zone_type=zone_type,
            temperature_range=TemperatureRange.for_zone(zone_type),
            capacity=capacity or Capacity(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

    def add_bin(self, bin: "Bin") -> None:
        self._bins.append(bin)

    @property
    def bins(self) -> list["Bin"]:
        return list(self._bins)


@dataclass
class Bin:
    """
    Bin — ตำแหน่งจัดเก็บใน zone

    Invariants:
    - code unique ภายใน warehouse
    - ห้ามมี product ที่ temperature ไม่ compatible
    """
    id: UUID
    zone_id: UUID
    warehouse_id: UUID
    code: BinCode
    capacity: Capacity
    is_active: bool
    is_blocked: bool              # ห้าม use ชั่วคราว (เช่น กำลัง QC)
    created_at: datetime

    @classmethod
    def create(
        cls, *, zone_id: UUID, warehouse_id: UUID, code: str,
        capacity: Capacity | None = None,
    ) -> "Bin":
        return cls(
            id=uuid4(),
            zone_id=zone_id,
            warehouse_id=warehouse_id,
            code=BinCode(code),
            capacity=capacity or Capacity(),
            is_active=True,
            is_blocked=False,
            created_at=datetime.utcnow(),
        )

    def block(self, reason: str) -> None:
        self.is_blocked = True

    def unblock(self) -> None:
        self.is_blocked = False
```

## 8.1.3 Domain Events

```python
# app/modules/warehouse/domain/events.py

from app.core.events.domain.entities import DomainEvent


class WarehouseCreated(DomainEvent): ...
class WarehouseDeactivated(DomainEvent): ...
class ZoneCreated(DomainEvent): ...
class BinBlocked(DomainEvent): ...
class TransferInitiated(DomainEvent): ...
class TransferCompleted(DomainEvent): ...
class TransferCancelled(DomainEvent): ...
```

## 8.1.4 Application — Interfaces

```python
# app/modules/warehouse/application/interfaces.py

from typing import Protocol
from uuid import UUID

from app.modules.warehouse.domain.entities import Warehouse, Zone, Bin


class IWarehouseRepository(Protocol):
    async def get_by_id(self, wid: UUID) -> Warehouse | None: ...
    async def get_by_code(self, company_id: UUID, code: str) -> Warehouse | None: ...
    async def list_by_company(
        self, company_id: UUID, *, active_only: bool = True,
    ) -> list[Warehouse]: ...
    async def exists_by_code(self, company_id: UUID, code: str) -> bool: ...
    async def save(self, w: Warehouse) -> None: ...
    async def update(self, w: Warehouse) -> None: ...
    async def get_with_zones(self, wid: UUID) -> Warehouse | None: ...


class IZoneRepository(Protocol):
    async def get_by_id(self, zid: UUID) -> Zone | None: ...
    async def list_by_warehouse(self, warehouse_id: UUID) -> list[Zone]: ...
    async def save(self, z: Zone) -> None: ...


class IBinRepository(Protocol):
    async def get_by_id(self, bid: UUID) -> Bin | None: ...
    async def get_by_code(self, warehouse_id: UUID, code: str) -> Bin | None: ...
    async def list_by_zone(self, zone_id: UUID) -> list[Bin]: ...
    async def find_available(
        self, zone_id: UUID, *, skip_blocked: bool = True,
    ) -> list[Bin]: ...
    async def save(self, b: Bin) -> None: ...
```

## 8.1.5 Application — Use Cases

```python
# app/modules/warehouse/application/use_cases.py

from dataclasses import dataclass
from uuid import UUID

from app.modules.warehouse.domain.entities import Warehouse, Zone, Bin
from app.modules.warehouse.domain.value_objects import (
    WarehouseType, ZoneType, Capacity,
)
from app.modules.warehouse.application.interfaces import (
    IWarehouseRepository, IZoneRepository, IBinRepository,
)
from app.core.audit.application.use_cases import (
    RecordAuditUseCase, RecordAuditCommand,
)
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.modules.warehouse.domain.events import (
    WarehouseCreated, ZoneCreated,
)
from app.core.tenant_context.domain.context import get_company_id


# ============================================================
# 1. Create Warehouse
# ============================================================

@dataclass
class CreateWarehouseCommand:
    code: str
    name: str
    warehouse_type: WarehouseType
    address: str
    branch_id: UUID | None = None
    capacity: Capacity | None = None
    latitude: float | None = None
    longitude: float | None = None
    actor_id: UUID = None  # type: ignore


class CreateWarehouseUseCase:
    def __init__(
        self, warehouses: IWarehouseRepository,
        audit: RecordAuditUseCase, publish: PublishEventUseCase, uow,
    ):
        self.warehouses = warehouses
        self.audit = audit
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: CreateWarehouseCommand) -> Warehouse:
        company_id = get_company_id()
        if await self.warehouses.exists_by_code(company_id, cmd.code):
            raise ValueError(f"Warehouse code ซ้ำ: {cmd.code}")

        wh = Warehouse.create(
            company_id=company_id,
            branch_id=cmd.branch_id,
            code=cmd.code,
            name=cmd.name,
            warehouse_type=cmd.warehouse_type,
            address=cmd.address,
            capacity=cmd.capacity,
            latitude=cmd.latitude,
            longitude=cmd.longitude,
        )

        async with self.uow.transaction():
            await self.warehouses.save(wh)
            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.CONFIG_CHANGED,
                entity_type="warehouse",
                entity_id=wh.id,
                after_state={
                    "code": cmd.code, "name": cmd.name,
                    "type": cmd.warehouse_type.value,
                },
            ))
            await self.publish.execute(WarehouseCreated.create(
                company_id=company_id,
                payload={"warehouse_id": str(wh.id), "code": cmd.code},
                actor_id=cmd.actor_id,
            ))
        return wh


# ============================================================
# 2. Create Zone
# ============================================================

@dataclass
class CreateZoneCommand:
    warehouse_id: UUID
    code: str
    name: str
    zone_type: ZoneType
    capacity: Capacity | None = None
    actor_id: UUID = None  # type: ignore


class CreateZoneUseCase:
    def __init__(
        self, warehouses, zones, audit, publish, uow,
    ):
        self.warehouses = warehouses
        self.zones = zones
        self.audit = audit
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: CreateZoneCommand) -> Zone:
        company_id = get_company_id()
        wh = await self.warehouses.get_with_zones(cmd.warehouse_id)
        if not wh:
            raise ValueError("ไม่พบ warehouse")

        if wh.find_zone_by_code(cmd.code):
            raise ValueError(f"Zone code ซ้ำ: {cmd.code}")

        zone = Zone.create(
            warehouse_id=cmd.warehouse_id,
            code=cmd.code,
            name=cmd.name,
            zone_type=cmd.zone_type,
            capacity=cmd.capacity,
        )

        async with self.uow.transaction():
            await self.zones.save(zone)
            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.CONFIG_CHANGED,
                entity_type="zone",
                entity_id=zone.id,
                after_state={
                    "warehouse_id": str(cmd.warehouse_id),
                    "code": cmd.code,
                    "zone_type": cmd.zone_type.value,
                },
            ))
            await self.publish.execute(ZoneCreated.create(
                company_id=company_id,
                payload={"zone_id": str(zone.id), "code": cmd.code},
                actor_id=cmd.actor_id,
            ))
        return zone


# ============================================================
# 3. Create Bin
# ============================================================

@dataclass
class CreateBinCommand:
    zone_id: UUID
    code: str
    capacity: Capacity | None = None
    actor_id: UUID = None  # type: ignore


class CreateBinUseCase:
    def __init__(self, zones, bins, audit, uow):
        ...

    async def execute(self, cmd: CreateBinCommand) -> Bin:
        zone = await self.zones.get_by_id(cmd.zone_id)
        if not zone:
            raise ValueError("ไม่พบ zone")

        bin_ = Bin.create(
            zone_id=cmd.zone_id,
            warehouse_id=zone.warehouse_id,
            code=cmd.code,
            capacity=cmd.capacity,
        )
        async with self.uow.transaction():
            await self.bins.save(bin_)
        return bin_


# ============================================================
# 4. Find Available Bin
# ============================================================

@dataclass
class FindAvailableBinQuery:
    warehouse_id: UUID
    zone_type: ZoneType


class FindAvailableBinUseCase:
    """
    หา bin ว่างในโซนที่ compatible — ใช้ตอน receive stock
    """

    def __init__(self, warehouses, zones, bins):
        self.warehouses = warehouses
        self.zones = zones
        self.bins = bins

    async def execute(self, q: FindAvailableBinQuery) -> Bin | None:
        zones = await self.zones.list_by_warehouse(q.warehouse_id)
        compatible = [z for z in zones if z.zone_type == q.zone_type and z.is_active]
        for zone in compatible:
            available = await self.bins.find_available(zone.id, skip_blocked=True)
            if available:
                return available[0]
        return None
```

## 8.1.6 Transfer Use Case (Core)

```python
# app/modules/warehouse/application/use_cases.py (ต่อ)

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import date


@dataclass
class TransferLineInput:
    product_id: UUID
    lot_id: UUID | None
    quantity: Decimal
    unit: str


@dataclass
class InitiateTransferCommand:
    from_warehouse_id: UUID
    to_warehouse_id: UUID
    lines: list[TransferLineInput]
    transfer_date: date
    reason: str | None = None
    actor_id: UUID = None  # type: ignore
    idempotency_key: str = ""


class InitiateTransferUseCase:
    """
    🎯 โอนย้ายสต็อกระหว่าง warehouses

    Flow:
    1.  ตรวจ warehouses (ต่างกัน, active)
    2.  ตรวจ temperature compatibility (frozen → chilled = ห้าม)
    3.  สร้าง Transfer (status=PENDING)
    4.  Reserve stock ที่ from
    5.  Return transfer
    """

    def __init__(
        self, warehouses, transfers, inventory_port,
        audit, publish, idempotency, uow,
    ):
        self.warehouses = warehouses
        self.transfers = transfers
        self.inventory = inventory_port
        self.audit = audit
        self.publish = publish
        self.idempotency = idempotency
        self.uow = uow

    async def execute(self, cmd: InitiateTransferCommand) -> "Transfer":
        company_id = get_company_id()

        if cmd.from_warehouse_id == cmd.to_warehouse_id:
            raise ValueError("from และ to ต้องต่างกัน")

        from_wh = await self.warehouses.get_with_zones(cmd.from_warehouse_id)
        to_wh = await self.warehouses.get_with_zones(cmd.to_warehouse_id)
        if not from_wh or not to_wh:
            raise ValueError("ไม่พบ warehouse")
        if not from_wh.is_active or not to_wh.is_active:
            raise ValueError("warehouse ถูกปิด")

        # temperature compatibility
        self._assert_temperature_compatible(from_wh, to_wh)

        # ตรวจ stock พอ
        for line in cmd.lines:
            available = await self.inventory.get_available_quantity(
                cmd.from_warehouse_id, line.product_id, line.lot_id,
            )
            if available < line.quantity:
                raise ValueError(
                    f"สต็อกไม่พอ: product {line.product_id} "
                    f"(ต้องการ {line.quantity}, มี {available})"
                )

        transfer = Transfer.create(
            company_id=company_id,
            from_warehouse_id=cmd.from_warehouse_id,
            to_warehouse_id=cmd.to_warehouse_id,
            transfer_date=cmd.transfer_date,
            reason=cmd.reason,
            created_by=cmd.actor_id,
        )
        for ln in cmd.lines:
            transfer.add_line(
                product_id=ln.product_id,
                lot_id=ln.lot_id,
                quantity=ln.quantity,
                unit=ln.unit,
            )

        async with self.uow.transaction():
            await self.transfers.save(transfer)

            # reserve stock ที่ from
            for ln in cmd.lines:
                await self.inventory.reserve(
                    warehouse_id=cmd.from_warehouse_id,
                    product_id=ln.product_id,
                    lot_id=ln.lot_id,
                    quantity=ln.quantity,
                    reference_type="transfer",
                    reference_id=transfer.id,
                )

            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.STOCK_TRANSFERRED,
                entity_type="transfer",
                entity_id=transfer.id,
                after_state={
                    "from": str(cmd.from_warehouse_id),
                    "to": str(cmd.to_warehouse_id),
                    "line_count": len(cmd.lines),
                },
            ))

        return transfer

    @staticmethod
    def _assert_temperature_compatible(from_wh, to_wh) -> None:
        """Frozen → Chilled = ห้าม (ต้อง temper ก่อน)"""
        from_zones = {z.zone_type for z in from_wh.zones}
        to_zones = {z.zone_type for z in to_wh.zones}

        # ถ้า from มี frozen และ to ไม่มี frozen เลย → เตือน
        if ZoneType.FROZEN in from_zones and ZoneType.FROZEN not in to_zones:
            raise ValueError(
                "ห้ามโอนจาก Frozen ไปยัง warehouse ที่ไม่มี Frozen zone "
                "(ต้อง temper หรือมี cold chain)"
            )


@dataclass
class CompleteTransferCommand:
    transfer_id: UUID
    actor_id: UUID
    idempotency_key: str


class CompleteTransferUseCase:
    """
    ยืนยันการโอน — สร้าง movements ทั้ง 2 ฝั่งแบบ atomic
    """

    def __init__(
        self, transfers, inventory_port,
        audit, publish, idempotency, uow,
    ):
        ...

    async def execute(self, cmd: CompleteTransferCommand) -> "Transfer":
        async with self.uow.transaction():
            transfer = await self.transfers.get_with_lines(cmd.transfer_id)
            if not transfer:
                raise ValueError("ไม่พบ transfer")

            # 1. Post OUT ที่ from
            # 2. Post IN ที่ to
            # 3. Update transfer status
            # 4. Read-back
            # 5. Audit + Publish

            for ln in transfer.lines:
                await self.inventory.release_reservation(
                    warehouse_id=transfer.from_warehouse_id,
                    product_id=ln.product_id,
                    lot_id=ln.lot_id,
                    quantity=ln.quantity,
                    reference_id=transfer.id,
                )
                await self.inventory.post_movement(
                    movement_type="TRANSFER_OUT",
                    warehouse_id=transfer.from_warehouse_id,
                    product_id=ln.product_id,
                    lot_id=ln.lot_id,
                    quantity=ln.quantity,
                    reference_type="transfer",
                    reference_id=transfer.id,
                )
                await self.inventory.post_movement(
                    movement_type="TRANSFER_IN",
                    warehouse_id=transfer.to_warehouse_id,
                    product_id=ln.product_id,
                    lot_id=ln.lot_id,
                    quantity=ln.quantity,
                    reference_type="transfer",
                    reference_id=transfer.id,
                )

            transfer.complete()
            await self.transfers.update(transfer)

        return transfer
```

## 8.1.7 Infrastructure — Models

```python
# app/modules/warehouse/infrastructure/models.py

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base


class WarehouseModel(Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_wh_company_code"),
        Index("ix_wh_company_type", "company_id", "warehouse_type"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    branch_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    warehouse_type: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(Text)

    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))

    max_weight_kg: Mapped[float | None] = mapped_column(Numeric(15, 3))
    max_volume_m3: Mapped[float | None] = mapped_column(Numeric(15, 3))
    max_pallets: Mapped[int | None] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_temperature_monitoring: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    zones: Mapped[list["ZoneModel"]] = relationship(
        "ZoneModel", back_populates="warehouse", cascade="all, delete-orphan",
    )


class ZoneModel(Base):
    __tablename__ = "warehouse_zones"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "code", name="uq_zone_wh_code"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"),
    )
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(20), nullable=False)

    temp_min_c: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    temp_max_c: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    temp_target_c: Mapped[float | None] = mapped_column(Numeric(6, 2))

    max_weight_kg: Mapped[float | None] = mapped_column(Numeric(15, 3))
    max_volume_m3: Mapped[float | None] = mapped_column(Numeric(15, 3))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    warehouse: Mapped[WarehouseModel] = relationship("WarehouseModel", back_populates="zones")
    bins: Mapped[list["BinModel"]] = relationship(
        "BinModel", back_populates="zone", cascade="all, delete-orphan",
    )


class BinModel(Base):
    __tablename__ = "warehouse_bins"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "code", name="uq_bin_wh_code"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    zone_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouse_zones.id", ondelete="CASCADE"),
    )
    warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    code: Mapped[str] = mapped_column(String(50), nullable=False)

    max_weight_kg: Mapped[float | None] = mapped_column(Numeric(15, 3))
    max_volume_m3: Mapped[float | None] = mapped_column(Numeric(15, 3))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    zone: Mapped[ZoneModel] = relationship("ZoneModel", back_populates="bins")


class TransferModel(Base):
    __tablename__ = "stock_transfers"
    __table_args__ = (
        UniqueConstraint("company_id", "transfer_number", name="uq_transfer_number"),
        Index("ix_transfer_company_date", "company_id", "transfer_date"),
        Index("ix_transfer_status", "company_id", "status"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    transfer_number: Mapped[str] = mapped_column(String(30), nullable=False)
    from_warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    to_warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    transfer_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    lines: Mapped[list["TransferLineModel"]] = relationship(
        "TransferLineModel", back_populates="transfer", cascade="all, delete-orphan",
    )


class TransferLineModel(Base):
    __tablename__ = "stock_transfer_lines"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    transfer_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("stock_transfers.id", ondelete="CASCADE"),
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20))

    transfer: Mapped[TransferModel] = relationship("TransferModel", back_populates="lines")
```

## 8.1.8 Database Schema

```sql
CREATE TABLE warehouses (
    id                             UUID PRIMARY KEY,
    company_id                     UUID NOT NULL,
    branch_id                      UUID,
    code                           VARCHAR(20) NOT NULL,
    name                           VARCHAR(255) NOT NULL,
    warehouse_type                 VARCHAR(30) NOT NULL,
    address                        TEXT NOT NULL,
    latitude                       NUMERIC(10,7),
    longitude                      NUMERIC(10,7),
    max_weight_kg                  NUMERIC(15,3),
    max_volume_m3                  NUMERIC(15,3),
    max_pallets                    INT,
    is_active                      BOOLEAN NOT NULL DEFAULT TRUE,
    requires_temperature_monitoring BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                     TIMESTAMPTZ NOT NULL,
    updated_at                     TIMESTAMPTZ NOT NULL,
    UNIQUE (company_id, code)
);

CREATE TABLE warehouse_zones (
    id              UUID PRIMARY KEY,
    warehouse_id    UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    code            VARCHAR(30) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    zone_type       VARCHAR(20) NOT NULL,
    temp_min_c      NUMERIC(6,2) NOT NULL,
    temp_max_c      NUMERIC(6,2) NOT NULL,
    temp_target_c   NUMERIC(6,2),
    max_weight_kg   NUMERIC(15,3),
    max_volume_m3   NUMERIC(15,3),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (warehouse_id, code)
);

CREATE TABLE warehouse_bins (
    id              UUID PRIMARY KEY,
    zone_id         UUID NOT NULL REFERENCES warehouse_zones(id) ON DELETE CASCADE,
    warehouse_id    UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    max_weight_kg   NUMERIC(15,3),
    max_volume_m3   NUMERIC(15,3),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_blocked      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (warehouse_id, code)
);

CREATE TABLE stock_transfers (
    id                 UUID PRIMARY KEY,
    company_id         UUID NOT NULL,
    transfer_number    VARCHAR(30) NOT NULL,
    from_warehouse_id  UUID NOT NULL,
    to_warehouse_id    UUID NOT NULL,
    transfer_date      TIMESTAMPTZ NOT NULL,
    status             VARCHAR(20) NOT NULL,
    reason             TEXT,
    created_by         UUID NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL,
    completed_at       TIMESTAMPTZ,
    cancelled_at       TIMESTAMPTZ,
    UNIQUE (company_id, transfer_number)
);

CREATE INDEX ix_transfer_company_date ON stock_transfers (company_id, transfer_date DESC);
CREATE INDEX ix_transfer_status ON stock_transfers (company_id, status);

CREATE TABLE stock_transfer_lines (
    id           UUID PRIMARY KEY,
    transfer_id  UUID NOT NULL REFERENCES stock_transfers(id) ON DELETE CASCADE,
    line_number  INT NOT NULL,
    product_id   UUID NOT NULL,
    lot_id       UUID,
    quantity     NUMERIC(15,3) NOT NULL,
    unit         VARCHAR(20) NOT NULL,
    UNIQUE (transfer_id, line_number)
);
```

## 8.1.9 Presentation — API

```python
# app/modules/warehouse/presentation/routers.py

router = APIRouter(prefix="/api/v1/warehouses", tags=["Warehouse"])


@router.post("/", status_code=201)
async def create_warehouse(
    body: CreateWarehouseRequest,
    user = Depends(require_permission("stock:adjust")),
    use_case = Depends(get_create_warehouse_use_case),
):
    ...


@router.get("/")
async def list_warehouses(
    active_only: bool = Query(True),
    user = Depends(require_permission("stock:read")),
):
    ...


@router.get("/{warehouse_id}")
async def get_warehouse(warehouse_id: UUID, ...): ...


@router.post("/{warehouse_id}/zones", status_code=201)
async def create_zone(
    warehouse_id: UUID,
    body: CreateZoneRequest,
    user = Depends(require_permission("stock:adjust")),
):
    ...


@router.get("/{warehouse_id}/zones")
async def list_zones(warehouse_id: UUID, ...): ...


@router.post("/{warehouse_id}/zones/{zone_id}/bins", status_code=201)
async def create_bin(...): ...


# ---------- Transfers ----------

@router.post("/transfers", status_code=201)
async def initiate_transfer(
    body: InitiateTransferRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("stock:transfer")),
    use_case = Depends(get_initiate_transfer_use_case),
):
    ...


@router.post("/transfers/{transfer_id}/complete")
async def complete_transfer(
    transfer_id: UUID,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("stock:transfer")),
):
    ...


@router.post("/transfers/{transfer_id}/cancel")
async def cancel_transfer(...): ...


@router.get("/transfers")
async def list_transfers(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    status: str | None = Query(None),
    user = Depends(require_permission("stock:read")),
):
    ...
```

## 8.1.10 Folder Structure

```text
app/modules/warehouse/
├── domain/
│   ├── entities.py            # Warehouse, Zone, Bin, Transfer, TransferLine
│   ├── value_objects.py       # WarehouseCode, BinCode, ZoneType, TemperatureRange
│   ├── events.py
│   └── errors.py
├── application/
│   ├── interfaces.py          # IWarehouseRepository, IZoneRepository, ...
│   └── use_cases.py           # Create, CreateZone, CreateBin, Transfer
├── infrastructure/
│   ├── models.py
│   └── repositories.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── domain/
    ├── application/
    │   └── test_transfer_temperature.py
    └── integration/
```

## 8.1.11 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Month 2) |
| **DoD** | ✅ Warehouse + Zone + Bin ครบ<br>✅ Temperature compatibility check<br>✅ Transfer atomic (2 ฝั่ง)<br>✅ Reserve + Release<br>✅ Cold chain validation |

---

# 🧩 Module 8.2 — `inventory`

## 8.2.1 Purpose & Scope

**Purpose:** หัวใจของ Goods Path — จัดการ stock movement, balance, valuation (FIFO/FEFO), reservation และ post ledger

**Scope:**
- ✅ StockMovement (ทุกความเคลื่อนไหว)
- ✅ StockBalance (ยอดคงเหลือ current)
- ✅ StockReservation
- ✅ Valuation (FIFO/FEFO/AVG)
- ✅ Ledger integration (Dr.COGS/Cr.Inventory)
- ✅ Cycle count / adjustment
- ✅ Reorder point / safety stock
- ❌ ไม่เก็บ lot detail (อยู่ใน `lot`)
- ❌ ไม่เก็บ warehouse structure (อยู่ใน `warehouse`)

## 8.2.2 Domain Model

```python
# app/modules/inventory/domain/value_objects.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class MovementType(str, Enum):
    """ประเภท movement — ครอบคลุมทุกกรณี"""
    # IN
    PURCHASE_RECEIVE = "purchase_receive"       # รับจาก PO
    PRODUCTION_OUTPUT = "production_output"     # ผลผลิต
    TRANSFER_IN = "transfer_in"                 # โอนเข้า
    RETURN_FROM_CUSTOMER = "return_in"          # ลูกค้าคืน
    ADJUSTMENT_IN = "adjustment_in"             # ปรับเพิ่ม
    OPENING_BALANCE = "opening"                 # ยกมา

    # OUT
    SALE = "sale"                               # ขาย
    PRODUCTION_ISSUE = "production_issue"       # เบิกผลิต
    TRANSFER_OUT = "transfer_out"               # โอนออก
    RETURN_TO_SUPPLIER = "return_out"           # คืน supplier
    ADJUSTMENT_OUT = "adjustment_out"           # ปรับลด
    WASTE = "waste"                             # ของเสีย
    EXPIRY_WRITE_OFF = "expiry_write_off"       # หมดอายุ

    # INTERNAL
    RESERVE = "reserve"
    RELEASE = "release"
    RESERVATION_CONSUME = "res_consume"


INBOUND_TYPES = {
    MovementType.PURCHASE_RECEIVE,
    MovementType.PRODUCTION_OUTPUT,
    MovementType.TRANSFER_IN,
    MovementType.RETURN_FROM_CUSTOMER,
    MovementType.ADJUSTMENT_IN,
    MovementType.OPENING_BALANCE,
}

OUTBOUND_TYPES = {
    MovementType.SALE,
    MovementType.PRODUCTION_ISSUE,
    MovementType.TRANSFER_OUT,
    MovementType.RETURN_TO_SUPPLIER,
    MovementType.ADJUSTMENT_OUT,
    MovementType.WASTE,
    MovementType.EXPIRY_WRITE_OFF,
}


class ValuationMethod(str, Enum):
    FIFO = "fifo"
    FEFO = "fefo"           # สำหรับอาหาร — first expired first out
    AVG = "avg"             # weighted average
    STANDARD = "standard"   # ราคามาตรฐาน


@dataclass(frozen=True, slots=True)
class MovementQuantity:
    """ปริมาณ movement — บวก = IN, ลบ = OUT"""
    quantity: Decimal
    unit: str

    def __post_init__(self) -> None:
        if not isinstance(self.quantity, Decimal):
            raise TypeError("quantity ต้องเป็น Decimal")

    @property
    def is_inbound(self) -> bool:
        return self.quantity > 0

    @property
    def is_outbound(self) -> bool:
        return self.quantity < 0


@dataclass(frozen=True, slots=True)
class StockKey:
    """Compound key ของ stock"""
    company_id: str
    warehouse_id: str
    product_id: str
    lot_id: str | None      # None = ไม่ track lot

    def as_tuple(self) -> tuple:
        return (self.company_id, self.warehouse_id,
                self.product_id, self.lot_id or "")
```

```python
# app/modules/inventory/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.money.domain.value_objects import Money
from app.modules.inventory.domain.value_objects import (
    MovementType, MovementQuantity, ValuationMethod,
    INBOUND_TYPES, OUTBOUND_TYPES,
)


@dataclass
class StockMovement:
    """
    StockMovement — บันทึกทุกความเคลื่อนไหว (append-only)

    Invariants:
    1.  quantity ≠ 0
    2.  INBOUND → quantity > 0, OUTBOUND → quantity < 0
    3.  ต้องมี reference (reference_type + reference_id)
    4.  posted_at ต้องมีเมื่อ status=POSTED
    5.  ห้ามลบ — ถ้าผิดต้อง post reversal
    """
    id: UUID
    company_id: UUID
    movement_number: str           # "MV-2026-00001"
    movement_type: MovementType
    movement_date: date

    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None
    bin_id: UUID | None

    quantity: Decimal              # + หรือ −
    unit: str

    unit_cost: Money | None        # ต้นทุนต่อหน่วย ณ เวลานั้น
    total_cost: Money | None

    reference_type: str            # "po", "so", "production", "transfer", "adjustment"
    reference_id: UUID
    reference_number: str | None

    status: str                    # "posted" | "reversed"
    posted_at: datetime | None
    reversed_by_id: UUID | None

    note: str | None
    created_by: UUID
    created_at: datetime

    @classmethod
    def create(
        cls, *, company_id: UUID, movement_number: str,
        movement_type: MovementType, movement_date: date,
        warehouse_id: UUID, product_id: UUID,
        lot_id: UUID | None, bin_id: UUID | None,
        quantity: Decimal, unit: str,
        unit_cost: Money | None, reference_type: str,
        reference_id: UUID, reference_number: str | None = None,
        note: str | None = None, created_by: UUID,
    ) -> "StockMovement":
        if quantity == 0:
            raise ValueError("quantity ต้อง ≠ 0")

        if movement_type in INBOUND_TYPES and quantity < 0:
            raise ValueError(f"{movement_type.value} ต้อง quantity > 0")
        if movement_type in OUTBOUND_TYPES and quantity > 0:
            raise ValueError(f"{movement_type.value} ต้อง quantity < 0")

        total_cost = (
            Money(unit_cost.amount * abs(quantity)) if unit_cost else None
        )

        return cls(
            id=uuid4(),
            company_id=company_id,
            movement_number=movement_number,
            movement_type=movement_type,
            movement_date=movement_date,
            warehouse_id=warehouse_id,
            product_id=product_id,
            lot_id=lot_id,
            bin_id=bin_id,
            quantity=quantity,
            unit=unit,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            status="posted",
            posted_at=datetime.utcnow(),
            reversed_by_id=None,
            note=note,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )


@dataclass
class StockBalance:
    """
    StockBalance — ยอดคงเหลือ (denormalized)

    Invariants:
    1.  quantity_on_hand = Σ(movements) เสมอ
    2.  quantity_available = on_hand − reserved
    3.  quantity_available ≥ 0 (ยกเว้น negative stock allowed ในบาง config)
    4.  updated_at เปลี่ยนทุกครั้งที่ movement
    """
    id: UUID
    company_id: UUID
    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None

    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal      # on_hand − reserved

    unit: str
    average_cost: Money | None       # สำหรับ AVG method
    last_movement_at: datetime | None
    last_counted_at: datetime | None

    updated_at: datetime

    @property
    def is_negative(self) -> bool:
        return self.quantity_on_hand < Decimal("0")

    @property
    def is_zero(self) -> bool:
        return self.quantity_on_hand == Decimal("0")


@dataclass
class StockReservation:
    """
    StockReservation — จองสต็อก (เช่น รับ order แล้ว ยังไม่ ship)

    Invariants:
    - quantity_reserved > 0
    - reference ต้องมี
    - released_at หรือ consumed_at อย่างใดอย่างหนึ่ง
    """
    id: UUID
    company_id: UUID
    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None

    quantity: Decimal
    reference_type: str           # "order", "transfer", "production"
    reference_id: UUID

    reserved_at: datetime
    expires_at: datetime | None
    released_at: datetime | None
    consumed_at: datetime | None

    created_by: UUID
```

## 8.2.3 Domain Events

```python
# app/modules/inventory/domain/events.py

from app.core.events.domain.entities import DomainEvent


class StockPosted(DomainEvent):
    """Post movement สำเร็จ"""
    ...


class StockLow(DomainEvent):
    """ต่ำกว่า reorder point"""
    ...


class StockOut(DomainEvent):
    """สต็อกหมด"""
    ...


class NegativeStockDetected(DomainEvent):
    """🚨 สต็อกติดลบ"""
    ...


class StockAdjusted(DomainEvent):
    """ปรับสต็อกจาก cycle count"""
    ...
```

## 8.2.4 Application — Interfaces

```python
# app/modules/inventory/application/interfaces.py

from typing import Protocol
from decimal import Decimal
from uuid import UUID
from datetime import date

from app.modules.inventory.domain.entities import (
    StockMovement, StockBalance, StockReservation,
)
from app.modules.inventory.domain.value_objects import MovementType


class IStockMovementRepository(Protocol):
    async def get_by_id(self, mid: UUID) -> StockMovement | None: ...
    async def list_by_reference(
        self, company_id: UUID, ref_type: str, ref_id: UUID,
    ) -> list[StockMovement]: ...
    async def list_by_product(
        self, company_id: UUID, product_id: UUID, *,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 500,
    ) -> list[StockMovement]: ...
    async def save(self, m: StockMovement) -> None: ...


class IStockBalanceRepository(Protocol):
    async def get(
        self, company_id: UUID, warehouse_id: UUID,
        product_id: UUID, lot_id: UUID | None,
    ) -> StockBalance | None: ...
    async def list_by_warehouse(
        self, company_id: UUID, warehouse_id: UUID, *,
        product_id: UUID | None = None,
        only_available: bool = False,
        limit: int = 1000,
    ) -> list[StockBalance]: ...
    async def upsert(self, b: StockBalance) -> None: ...
    async def lock_for_update(
        self, company_id: UUID, warehouse_id: UUID,
        product_id: UUID, lot_id: UUID | None,
    ) -> StockBalance | None: ...


class IStockReservationRepository(Protocol):
    async def get_active(
        self, company_id: UUID, warehouse_id: UUID,
        product_id: UUID, lot_id: UUID | None,
    ) -> list[StockReservation]: ...
    async def save(self, r: StockReservation) -> None: ...
    async def release(self, rid: UUID) -> None: ...


class ILotFefoPicker(Protocol):
    """
    Port — ให้ inventory module ดึง lot ตาม FEFO
    (implemented โดย lot module)
    """
    async def pick_fefo(
        self, *, company_id: UUID, warehouse_id: UUID,
        product_id: UUID, required_qty: Decimal,
    ) -> list[dict]: ...
```

## 8.2.5 Application — Core Use Cases

```python
# app/modules/inventory/application/use_cases.py

from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID

from app.core.money.domain.value_objects import Money
from app.modules.inventory.domain.entities import (
    StockMovement, StockBalance, StockReservation,
)
from app.modules.inventory.domain.value_objects import (
    MovementType, INBOUND_TYPES, OUTBOUND_TYPES,
)
from app.modules.inventory.domain.events import (
    StockPosted, StockLow, StockOut, NegativeStockDetected,
)
from app.modules.inventory.application.interfaces import (
    IStockMovementRepository, IStockBalanceRepository,
    IStockReservationRepository, ILotFefoPicker,
)
from app.core.audit.application.use_cases import (
    RecordAuditUseCase, RecordAuditCommand,
)
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.core.tenant_context.domain.context import get_company_id
from app.core.config.application.use_cases import GetConfigUseCase


# ============================================================
# 1. Post Movement (CORE — หัวใจของ inventory)
# ============================================================

@dataclass
class PostMovementCommand:
    movement_type: MovementType
    movement_date: date
    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None
    bin_id: UUID | None
    quantity: Decimal
    unit: str
    unit_cost: Money | None
    reference_type: str
    reference_id: UUID
    reference_number: str | None = None
    note: str | None = None
    actor_id: UUID | None = None
    actor_type: ActorType = ActorType.SYSTEM
    allow_negative: bool = False


class PostMovementUseCase:
    """
    🎯 Post stock movement — ปรับ balance + verify + ledger trigger

    Flow:
    1.  ตรวจ quantity + type
    2.  Lock balance (SELECT FOR UPDATE)
    3.  ตรวจ available stock (ถ้า outbound)
    4.  คำนวณ unit_cost (ถ้าไม่มี → FEFO/FIFO)
    5.  ออกเลข movement
    6.  สร้าง StockMovement + save
    7.  Update StockBalance
    8.  Read-back verify (balance = Σ movements)
    9.  Audit + Publish (trigger ledger)
    """

    def __init__(
        self,
        movements: IStockMovementRepository,
        balances: IStockBalanceRepository,
        sequence: "IMovementNumberSequence",
        fefo: ILotFefoPicker,
        config: GetConfigUseCase,
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        uow,
    ):
        self.movements = movements
        self.balances = balances
        self.sequence = sequence
        self.fefo = fefo
        self.config = config
        self.audit = audit
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: PostMovementCommand) -> StockMovement:
        company_id = get_company_id()

        if cmd.quantity == 0:
            raise ValueError("quantity ต้อง ≠ 0")

        is_inbound = cmd.movement_type in INBOUND_TYPES
        is_outbound = cmd.movement_type in OUTBOUND_TYPES

        async with self.uow.transaction():
            # 1. Lock balance
            balance = await self.balances.lock_for_update(
                company_id=company_id,
                warehouse_id=cmd.warehouse_id,
                product_id=cmd.product_id,
                lot_id=cmd.lot_id,
            )

            # 2. ตรวจ available (ถ้า outbound)
            if is_outbound:
                available = (
                    balance.quantity_available if balance else Decimal("0")
                )
                required = abs(cmd.quantity)
                if available < required and not cmd.allow_negative:
                    raise ValueError(
                        f"สต็อกไม่พอ: ต้องการ {required}, "
                        f"available {available}"
                    )

            # 3. Resolve unit_cost
            unit_cost = cmd.unit_cost
            if unit_cost is None and is_outbound:
                # ดึงจาก FEFO/FIFO
                unit_cost = await self._resolve_unit_cost(
                    company_id, cmd,
                )

            # 4. ออกเลข
            number = await self.sequence.next_number(
                company_id=company_id,
                prefix="MV",
                year=cmd.movement_date.year,
            )

            # 5. สร้าง movement
            movement = StockMovement.create(
                company_id=company_id,
                movement_number=number,
                movement_type=cmd.movement_type,
                movement_date=cmd.movement_date,
                warehouse_id=cmd.warehouse_id,
                product_id=cmd.product_id,
                lot_id=cmd.lot_id,
                bin_id=cmd.bin_id,
                quantity=cmd.quantity,
                unit=cmd.unit,
                unit_cost=unit_cost,
                reference_type=cmd.reference_type,
                reference_id=cmd.reference_id,
                reference_number=cmd.reference_number,
                note=cmd.note,
                created_by=cmd.actor_id,
            )

            await self.movements.save(movement)

            # 6. Update balance
            new_balance = self._apply_movement(balance, movement)
            await self.balances.upsert(new_balance)

            # 7. Read-back verify
            persisted = await self.balances.get(
                company_id, cmd.warehouse_id, cmd.product_id, cmd.lot_id,
            )
            if persisted is None:
                raise RuntimeError("read-back: balance หาย")
            if persisted.quantity_on_hand != new_balance.quantity_on_hand:
                raise RuntimeError(
                    f"read-back mismatch: {persisted.quantity_on_hand} ≠ "
                    f"{new_balance.quantity_on_hand}"
                )

            # 8. ตรวจ negative
            if persisted.is_negative:
                await self.publish.execute(NegativeStockDetected.create(
                    company_id=company_id,
                    payload={
                        "warehouse_id": str(cmd.warehouse_id),
                        "product_id": str(cmd.product_id),
                        "lot_id": str(cmd.lot_id) if cmd.lot_id else None,
                        "quantity": str(persisted.quantity_on_hand),
                    },
                ))

            # 9. ตรวจ reorder point
            await self._check_reorder(company_id, persisted)

            # 10. Audit
            await self.audit.execute(RecordAuditCommand(
                company_id=company_id,
                actor_id=cmd.actor_id,
                actor_type=cmd.actor_type,
                action=(
                    AuditAction.STOCK_RECEIVED if is_inbound
                    else AuditAction.STOCK_ISSUED
                ),
                entity_type="stock_movement",
                entity_id=movement.id,
                after_state={
                    "movement_number": movement.movement_number,
                    "type": cmd.movement_type.value,
                    "quantity": str(cmd.quantity),
                    "warehouse_id": str(cmd.warehouse_id),
                    "product_id": str(cmd.product_id),
                    "balance_after": str(persisted.quantity_on_hand),
                },
            ))

            # 11. Publish — ledger จะฟัง
            await self.publish.execute(StockPosted.create(
                company_id=company_id,
                payload={
                    "movement_id": str(movement.id),
                    "movement_number": movement.movement_number,
                    "movement_type": cmd.movement_type.value,
                    "quantity": str(cmd.quantity),
                    "unit_cost": str(unit_cost.amount) if unit_cost else None,
                    "total_cost": (
                        str(movement.total_cost.amount)
                        if movement.total_cost else None
                    ),
                    "warehouse_id": str(cmd.warehouse_id),
                    "product_id": str(cmd.product_id),
                    "reference_type": cmd.reference_type,
                    "reference_id": str(cmd.reference_id),
                },
                actor_id=cmd.actor_id,
            ))

        return movement

    def _apply_movement(
        self, balance: StockBalance | None, movement: StockMovement,
    ) -> StockBalance:
        from uuid import uuid4
        if balance is None:
            balance = StockBalance(
                id=uuid4(),
                company_id=movement.company_id,
                warehouse_id=movement.warehouse_id,
                product_id=movement.product_id,
                lot_id=movement.lot_id,
                quantity_on_hand=Decimal("0"),
                quantity_reserved=Decimal("0"),
                quantity_available=Decimal("0"),
                unit=movement.unit,
                average_cost=None,
                last_movement_at=None,
                last_counted_at=None,
                updated_at=datetime.utcnow(),
            )

        balance.quantity_on_hand += movement.quantity
        balance.quantity_available = (
            balance.quantity_on_hand - balance.quantity_reserved
        )
        balance.last_movement_at = datetime.utcnow()
        balance.updated_at = datetime.utcnow()
        return balance

    async def _resolve_unit_cost(
        self, company_id: UUID, cmd: PostMovementCommand,
    ) -> Money:
        method = await self.config.execute(
            company_id, "inventory.valuation_method", "fifo",
        )
        if method.upper() == "FEFO":
            lots = await self.fefo.pick_fefo(
                company_id=company_id,
                warehouse_id=cmd.warehouse_id,
                product_id=cmd.product_id,
                required_qty=abs(cmd.quantity),
            )
            if lots:
                return Money(Decimal(str(lots[0]["unit_cost"])))
        # fallback — use average
        bal = await self.balances.get(
            company_id, cmd.warehouse_id, cmd.product_id, cmd.lot_id,
        )
        if bal and bal.average_cost:
            return bal.average_cost
        return Money(Decimal("0"))

    async def _check_reorder(
        self, company_id: UUID, balance: StockBalance,
    ) -> None:
        """ตรวจ reorder point"""
        threshold = await self.config.get_decimal(
            company_id, "inventory.low_threshold_pct", Decimal("0.2"),
        )
        # lookup product reorder_point
        # ถ้า available < reorder_point → publish StockLow
        ...


# ============================================================
# 2. Reserve / Release
# ============================================================

@dataclass
class ReserveStockCommand:
    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None
    quantity: Decimal
    reference_type: str
    reference_id: UUID
    expires_at: datetime | None = None
    actor_id: UUID | None = None


class ReserveStockUseCase:
    """
    จองสต็อก — เพิ่ม quantity_reserved, ลด quantity_available
    """

    def __init__(
        self, balances, reservations, movements, uow,
    ):
        ...

    async def execute(self, cmd: ReserveStockCommand) -> StockReservation:
        company_id = get_company_id()
        async with self.uow.transaction():
            balance = await self.balances.lock_for_update(
                company_id, cmd.warehouse_id, cmd.product_id, cmd.lot_id,
            )
            if not balance:
                raise ValueError("ไม่พบ stock balance")

            if balance.quantity_available < cmd.quantity:
                raise ValueError(
                    f"available ไม่พอ: {balance.quantity_available} < {cmd.quantity}"
                )

            balance.quantity_reserved += cmd.quantity
            balance.quantity_available -= cmd.quantity
            balance.updated_at = datetime.utcnow()
            await self.balances.upsert(balance)

            reservation = StockReservation(
                id=uuid4(),
                company_id=company_id,
                warehouse_id=cmd.warehouse_id,
                product_id=cmd.product_id,
                lot_id=cmd.lot_id,
                quantity=cmd.quantity,
                reference_type=cmd.reference_type,
                reference_id=cmd.reference_id,
                reserved_at=datetime.utcnow(),
                expires_at=cmd.expires_at,
                released_at=None,
                consumed_at=None,
                created_by=cmd.actor_id,
            )
            await self.reservations.save(reservation)
        return reservation


@dataclass
class ReleaseReservationCommand:
    reservation_id: UUID
    actor_id: UUID


class ReleaseReservationUseCase:
    """
    ปล่อย reservation — คืน available
    """

    def __init__(self, balances, reservations, uow):
        ...

    async def execute(self, cmd: ReleaseReservationCommand) -> None:
        company_id = get_company_id()
        async with self.uow.transaction():
            reservation = await self.reservations.get_by_id(cmd.reservation_id)
            if not reservation:
                raise ValueError("ไม่พบ reservation")
            if reservation.released_at or reservation.consumed_at:
                raise ValueError("reservation ถูก release/consume แล้ว")

            balance = await self.balances.lock_for_update(
                company_id, reservation.warehouse_id,
                reservation.product_id, reservation.lot_id,
            )
            if balance:
                balance.quantity_reserved -= reservation.quantity
                balance.quantity_available += reservation.quantity
                balance.updated_at = datetime.utcnow()
                await self.balances.upsert(balance)

            await self.reservations.release(cmd.reservation_id)


# ============================================================
# 3. Cycle Count / Adjustment
# ============================================================

@dataclass
class AdjustStockCommand:
    warehouse_id: UUID
    product_id: UUID
    lot_id: UUID | None
    counted_quantity: Decimal
    reason: str
    actor_id: UUID
    idempotency_key: str


class AdjustStockUseCase:
    """
    ปรับสต็อกจาก cycle count

    Flow:
    1.  Lock balance
    2.  คำนวณส่วนต่าง
    3.  Post ADJUSTMENT_IN หรือ ADJUSTMENT_OUT
    4.  Audit + Publish
    """

    def __init__(
        self, balances, post_movement_uc,
        audit, publish, idempotency, uow,
    ):
        ...

    async def execute(self, cmd: AdjustStockCommand) -> StockMovement | None:
        company_id = get_company_id()

        async def _do() -> tuple[int, dict]:
            async with self.uow.transaction():
                balance = await self.balances.lock_for_update(
                    company_id, cmd.warehouse_id, cmd.product_id, cmd.lot_id,
                )
                current = (
                    balance.quantity_on_hand if balance else Decimal("0")
                )
                diff = cmd.counted_quantity - current
                if diff == 0:
                    return 200, {"status": "no_change"}

                mtype = (
                    MovementType.ADJUSTMENT_IN if diff > 0
                    else MovementType.ADJUSTMENT_OUT
                )

                movement = await self.post_movement_uc.execute(PostMovementCommand(
                    movement_type=mtype,
                    movement_date=date.today(),
                    warehouse_id=cmd.warehouse_id,
                    product_id=cmd.product_id,
                    lot_id=cmd.lot_id,
                    bin_id=None,
                    quantity=diff,
                    unit="pcs",
                    unit_cost=None,
                    reference_type="adjustment",
                    reference_id=uuid4(),
                    note=f"Cycle count: {cmd.reason}",
                    actor_id=cmd.actor_id,
                    actor_type=ActorType.USER,
                    allow_negative=True,
                ))

                await self.publish.execute(StockAdjusted.create(
                    company_id=company_id,
                    payload={
                        "movement_id": str(movement.id),
                        "product_id": str(cmd.product_id),
                        "warehouse_id": str(cmd.warehouse_id),
                        "before": str(current),
                        "after": str(cmd.counted_quantity),
                        "diff": str(diff),
                        "reason": cmd.reason,
                    },
                    actor_id=cmd.actor_id,
                ))
                return 201, {"movement_id": str(movement.id)}

        await self.idempotency.execute(
            key=cmd.idempotency_key,
            company_id=company_id,
            endpoint=f"/api/v1/inventory/adjust/{cmd.product_id}",
            method="POST",
            body={"product_id": str(cmd.product_id), "qty": str(cmd.counted_quantity)},
            scope=IdempotencyScope.LONG,
            action=_do,
        )
        return None
```

## 8.2.6 Ledger Handler

```python
# app/modules/inventory/application/handlers.py

class StockPostedLedgerHandler:
    """
    ฟัง StockPosted → post journal

    - Purchase Receive: Dr.Inventory / Cr.AP
    - Sale: Dr.COGS / Cr.Inventory
    - Waste: Dr.Waste Expense / Cr.Inventory
    - Adjustment: Dr/Cr Inventory + Adjustment Gain/Loss
    """

    def __init__(self, post_journal, config):
        self.post_journal = post_journal
        self.config = config

    async def handle(self, event: StockPosted) -> None:
        p = event.payload
        mtype = p["movement_type"]
        total_cost = Decimal(p.get("total_cost") or "0")

        if total_cost == 0:
            return

        lines = self._build_lines(mtype, total_cost, p)

        if not lines:
            return

        await self.post_journal.execute(PostJournalCommand(
            source=JournalSource.STOCK,
            source_id=UUID(p["movement_id"]),
            posting_date=date.fromisoformat(p.get("movement_date", str(date.today()))),
            description=f"Stock {mtype} {p['movement_number']}",
            lines=lines,
            actor_id=event.actor_id,
            actor_type=ActorType.SYSTEM,
        ))

    @staticmethod
    def _build_lines(mtype: str, total_cost: Decimal, p: dict) -> list:
        from app.modules.ledger.application.use_cases import PostJournalLineInput

        if mtype == "purchase_receive":
            return [
                PostJournalLineInput(
                    account_code="1200",  # สินค้าคงเหลือ
                    debit=total_cost, credit=Decimal("0"),
                    description="รับสินค้า", reference_id=UUID(p["movement_id"]),
                ),
                PostJournalLineInput(
                    account_code="2000",  # เจ้าหนี้การค้า
                    debit=Decimal("0"), credit=total_cost,
                    description="รับสินค้า", reference_id=UUID(p["movement_id"]),
                ),
            ]

        if mtype == "sale":
            return [
                PostJournalLineInput(
                    account_code="6000",  # ต้นทุนขาย
                    debit=total_cost, credit=Decimal("0"),
                    description="ต้นทุนขาย", reference_id=UUID(p["movement_id"]),
                ),
                PostJournalLineInput(
                    account_code="1200",  # สินค้าคงเหลือ
                    debit=Decimal("0"), credit=total_cost,
                    description="ตัดสต็อก", reference_id=UUID(p["movement_id"]),
                ),
            ]

        if mtype == "waste" or mtype == "expiry_write_off":
            return [
                PostJournalLineInput(
                    account_code="5300",  # ค่าของเสีย
                    debit=total_cost, credit=Decimal("0"),
                    description="ตัดของเสีย", reference_id=UUID(p["movement_id"]),
                ),
                PostJournalLineInput(
                    account_code="1200",
                    debit=Decimal("0"), credit=total_cost,
                    description="ตัดสต็อก", reference_id=UUID(p["movement_id"]),
                ),
            ]

        if mtype == "production_issue":
            return [
                PostJournalLineInput(
                    account_code="6010",  # ต้นทุนวัตถุดิบ
                    debit=total_cost, credit=Decimal("0"),
                    description="เบิกวัตถุดิบ", reference_id=UUID(p["movement_id"]),
                ),
                PostJournalLineInput(
                    account_code="1210",  # วัตถุดิบ
                    debit=Decimal("0"), credit=total_cost,
                    description="เบิกวัตถุดิบ", reference_id=UUID(p["movement_id"]),
                ),
            ]

        if mtype == "production_output":
            return [
                PostJournalLineInput(
                    account_code="1230",  # สินค้าสำเร็จรูป
                    debit=total_cost, credit=Decimal("0"),
                    description="ผลผลิต", reference_id=UUID(p["movement_id"]),
                ),
                PostJournalLineInput(
                    account_code="6020",  # ต้นทุนการผลิต
                    debit=Decimal("0"), credit=total_cost,
                    description="ผลผลิต", reference_id=UUID(p["movement_id"]),
                ),
            ]

        return []
```

## 8.2.7 Infrastructure — Models

```python
# app/modules/inventory/infrastructure/models.py

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class StockMovementModel(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        UniqueConstraint("company_id", "movement_number", name="uq_mv_company_number"),
        Index("ix_mv_company_date", "company_id", "movement_date"),
        Index("ix_mv_warehouse_product", "warehouse_id", "product_id", "movement_date"),
        Index("ix_mv_lot", "lot_id") ,
        Index("ix_mv_reference", "company_id", "reference_type", "reference_id"),
        CheckConstraint("quantity <> 0", name="ck_mv_quantity_nonzero"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    movement_number: Mapped[str] = mapped_column(String(30), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    movement_date: Mapped[Date] = mapped_column(Date, nullable=False)

    warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    bin_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20))
    unit_cost: Mapped[float | None] = mapped_column(Numeric(15, 4))
    total_cost: Mapped[float | None] = mapped_column(Numeric(15, 2))

    reference_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(String(20), nullable=False)
    posted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    reversed_by_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class StockBalanceModel(Base):
    __tablename__ = "stock_balances"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "warehouse_id", "product_id", "lot_id",
            name="uq_balance_key",
        ),
        Index("ix_bal_warehouse_product", "warehouse_id", "product_id"),
        Index("ix_bal_available", "company_id", "quantity_available")
        if False else Index("ix_bal_company", "company_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    quantity_on_hand: Mapped[float] = mapped_column(Numeric(15, 3), default=0)
    quantity_reserved: Mapped[float] = mapped_column(Numeric(15, 3), default=0)
    quantity_available: Mapped[float] = mapped_column(Numeric(15, 3), default=0)

    unit: Mapped[str] = mapped_column(String(20))
    average_cost: Mapped[float | None] = mapped_column(Numeric(15, 4))
    last_movement_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    last_counted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class StockReservationModel(Base):
    __tablename__ = "stock_reservations"
    __table_args__ = (
        Index("ix_res_company_product", "company_id", "product_id"),
        Index("ix_res_reference", "reference_type", "reference_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    reference_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    reserved_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    released_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    created_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))


class MovementNumberSequenceModel(Base):
    __tablename__ = "stock_movement_sequences"
    __table_args__ = (UniqueConstraint("company_id", "prefix", "year"),)

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    prefix: Mapped[str] = mapped_column(String(10))
    year: Mapped[int] = mapped_column(Integer)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
```

## 8.2.8 Database Schema

```sql
CREATE TABLE stock_movements (
    id                UUID PRIMARY KEY,
    company_id        UUID NOT NULL,
    movement_number   VARCHAR(30) NOT NULL,
    movement_type     VARCHAR(30) NOT NULL,
    movement_date     DATE NOT NULL,

    warehouse_id      UUID NOT NULL,
    product_id        UUID NOT NULL,
    lot_id            UUID,
    bin_id            UUID,

    quantity          NUMERIC(15,3) NOT NULL,
    unit              VARCHAR(20) NOT NULL,
    unit_cost         NUMERIC(15,4),
    total_cost        NUMERIC(15,2),

    reference_type    VARCHAR(30) NOT NULL,
    reference_id      UUID NOT NULL,
    reference_number  VARCHAR(50),

    status            VARCHAR(20) NOT NULL,
    posted_at         TIMESTAMPTZ,
    reversed_by_id    UUID,

    note              TEXT,
    created_by        UUID,
    created_at        TIMESTAMPTZ NOT NULL,

    UNIQUE (company_id, movement_number),
    CHECK (quantity <> 0)
);

CREATE INDEX ix_mv_company_date ON stock_movements (company_id, movement_date DESC);
CREATE INDEX ix_mv_warehouse_product
    ON stock_movements (warehouse_id, product_id, movement_date DESC);
CREATE INDEX ix_mv_lot ON stock_movements (lot_id) WHERE lot_id IS NOT NULL;
CREATE INDEX ix_mv_reference
    ON stock_movements (company_id, reference_type, reference_id);

-- 🛡️ Append-only
CREATE OR REPLACE FUNCTION prevent_movement_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'stock_movements is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mv_no_delete
BEFORE DELETE ON stock_movements
FOR EACH ROW EXECUTE FUNCTION prevent_movement_delete();

CREATE TABLE stock_balances (
    id                  UUID PRIMARY KEY,
    company_id          UUID NOT NULL,
    warehouse_id        UUID NOT NULL,
    product_id          UUID NOT NULL,
    lot_id              UUID,

    quantity_on_hand    NUMERIC(15,3) NOT NULL DEFAULT 0,
    quantity_reserved   NUMERIC(15,3) NOT NULL DEFAULT 0,
    quantity_available  NUMERIC(15,3) NOT NULL DEFAULT 0,

    unit                VARCHAR(20),
    average_cost        NUMERIC(15,4),
    last_movement_at    TIMESTAMPTZ,
    last_counted_at     TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ NOT NULL,

    UNIQUE (company_id, warehouse_id, product_id, lot_id)
);

CREATE INDEX ix_bal_warehouse_product ON stock_balances (warehouse_id, product_id);
CREATE INDEX ix_bal_available ON stock_balances (company_id, quantity_available)
    WHERE quantity_available > 0;

CREATE TABLE stock_reservations (
    id              UUID PRIMARY KEY,
    company_id      UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    product_id      UUID NOT NULL,
    lot_id          UUID,
    quantity        NUMERIC(15,3) NOT NULL,
    reference_type  VARCHAR(30) NOT NULL,
    reference_id    UUID NOT NULL,
    reserved_at     TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ,
    released_at     TIMESTAMPTZ,
    consumed_at     TIMESTAMPTZ,
    created_by      UUID
);

CREATE INDEX ix_res_company_product ON stock_reservations (company_id, product_id);
CREATE INDEX ix_res_reference ON stock_reservations (reference_type, reference_id);

CREATE TABLE stock_movement_sequences (
    id             UUID PRIMARY KEY,
    company_id     UUID NOT NULL,
    prefix         VARCHAR(10) NOT NULL,
    year           INT NOT NULL,
    current_value  INT NOT NULL DEFAULT 0,
    UNIQUE (company_id, prefix, year)
);
```

## 8.2.9 Presentation — API

```python
# app/modules/inventory/presentation/routers.py

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


# ---------- Balances ----------
@router.get("/balances")
async def list_balances(
    warehouse_id: UUID | None = Query(None),
    product_id: UUID | None = Query(None),
    only_available: bool = Query(False),
    user = Depends(require_permission("stock:read")),
):
    ...


@router.get("/balances/{warehouse_id}/{product_id}")
async def get_balance(...): ...


# ---------- Movements ----------
@router.get("/movements")
async def list_movements(
    warehouse_id: UUID | None = Query(None),
    product_id: UUID | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    movement_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    user = Depends(require_permission("stock:read")),
):
    ...


@router.post("/movements", status_code=201)
async def post_movement(
    body: PostMovementRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("stock:adjust")),
    use_case = Depends(get_post_movement_use_case),
):
    """Post manual movement (ปกติระบบ auto-post)"""
    ...


# ---------- Reserve ----------
@router.post("/reservations", status_code=201)
async def reserve(...): ...


@router.delete("/reservations/{rid}")
async def release_reservation(...): ...


# ---------- Adjustment ----------
@router.post("/adjust")
async def adjust_stock(
    body: AdjustStockRequest,
    idempotency_key: str = Depends(require_idempotency_key),
    user = Depends(require_permission("stock:adjust")),
):
    """Cycle count adjustment"""
    ...


# ---------- Reports ----------
@router.get("/stock-card/{product_id}")
async def stock_card(
    product_id: UUID,
    warehouse_id: UUID,
    from_date: date, to_date: date,
    user = Depends(require_permission("stock:read")),
):
    """บัญชีคุมสินค้า"""
    ...


@router.get("/expiring")
async def list_expiring(
    days: int = Query(7, le=90),
    user = Depends(require_permission("stock:read")),
):
    """สินค้าใกล้หมดอายุ"""
    ...


@router.get("/low-stock")
async def list_low_stock(
    user = Depends(require_permission("stock:read")),
):
    ...
```

## 8.2.10 Folder Structure

```text
app/modules/inventory/
├── domain/
│   ├── entities.py            # StockMovement, StockBalance, StockReservation
│   ├── value_objects.py       # MovementType, ValuationMethod, StockKey
│   ├── events.py              # StockPosted, StockLow, NegativeStockDetected
│   └── errors.py
├── application/
│   ├── interfaces.py
│   ├── use_cases.py           # PostMovement, Reserve, Release, Adjust
│   └── handlers.py            # StockPostedLedgerHandler
├── infrastructure/
│   ├── models.py
│   ├── repositories.py
│   └── valuation/
│       ├── fifo.py
│       ├── fefo.py
│       └── average.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── domain/
    │   └── test_movement_invariants.py
    ├── application/
    │   ├── test_post_movement.py
    │   ├── test_balance_readback.py
    │   ├── test_reserve_release.py
    │   ├── test_concurrent_post.py
    │   └── test_negative_stock.py
    └── integration/
        └── test_stock_to_ledger.py
```

## 8.2.11 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Month 2) |
| **DoD** | ✅ Append-only trigger<br>✅ Balance = Σ movements (recon pass)<br>✅ Read-back verify หลัง post<br>✅ FEFO/FIFO valuation<br>✅ Reserve + Release atomic<br>✅ Negative stock → alert<br>✅ Concurrency test (10 threads) → balance ถูก<br>✅ Ledger handler post journal |

---

# 🧩 Module 8.3 — `lot`

## 8.3.1 Purpose & Scope

**Purpose:** จัดการ lot/expiry + traceability foundation (เชื่อมกับ Part 11 QR/RFID)

**Scope:**
- ✅ Lot (batch number, mfg date, expiry)
- ✅ Lot balance (per warehouse)
- ✅ FEFO picking
- ✅ Traceability (forward + backward)
- ✅ Expiry alert
- ✅ Recall support
- ❌ ไม่เก็บ stock movement (อยู่ใน `inventory`)
- ❌ ไม่ render QR (อยู่ใน `traceability` Part 11)

## 8.3.2 Domain Model

```python
# app/modules/lot/domain/value_objects.py

from dataclasses import dataclass
from datetime import date
from enum import Enum
import re


class LotStatus(str, Enum):
    ACTIVE = "active"
    QUARANTINE = "quarantine"   # รอ QC
    RELEASED = "released"       # ผ่าน QC
    REJECTED = "rejected"
    EXPIRED = "expired"
    RECALLED = "recalled"
    CONSUMED = "consumed"       # ใช้หมด


class ExpiryBucket(str, Enum):
    """bucket สำหรับ FEFO / alert"""
    FRESH = "fresh"             # > 30 วัน
    WARNING = "warning"         # 7-30 วัน
    CRITICAL = "critical"       # 1-7 วัน
    EXPIRING_TODAY = "today"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class LotNumber:
    """
    เลข lot — รูปแบบ: {PREFIX}-{YYMMDD}-{SEQ}
    เช่น LOT-260115-0001
    """
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z0-9]+-\d{6}-\d{4,6}$", self.value):
            raise ValueError(f"LotNumber ไม่ถูกต้อง: {self.value}")


@dataclass(frozen=True, slots=True)
class ExpiryInfo:
    """ข้อมูลหมดอายุ"""
    manufacture_date: date | None
    expiry_date: date
    best_before_date: date | None = None

    def __post_init__(self) -> None:
        if self.manufacture_date and self.manufacture_date > self.expiry_date:
            raise ValueError("manufacture_date ต้อง ≤ expiry_date")

    def days_to_expiry(self, today: date | None = None) -> int:
        return (self.expiry_date - (today or date.today())).days

    def bucket(self, today: date | None = None) -> ExpiryBucket:
        days = self.days_to_expiry(today)
        if days < 0:
            return ExpiryBucket.EXPIRED
        if days == 0:
            return ExpiryBucket.EXPIRING_TODAY
        if days <= 7:
            return ExpiryBucket.CRITICAL
        if days <= 30:
            return ExpiryBucket.WARNING
        return ExpiryBucket.FRESH
```

```python
# app/modules/lot/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.modules.lot.domain.value_objects import (
    LotNumber, LotStatus, ExpiryInfo, ExpiryBucket,
)


@dataclass
class Lot:
    """
    Lot — Aggregate Root

    Invariants:
    1.  lot_number unique ต่อ company ต่อ product
    2.  expiry_date ต้อง > manufacture_date
    3.  RECALLED → ห้ามใช้ใน FEFO
    4.  QUARANTINE → ห้ามใช้ใน FEFO
    5.  RECALLED → ต้อง trace forward หาลูกค้า
    """
    id: UUID
    company_id: UUID
    product_id: UUID
    lot_number: LotNumber
    status: LotStatus

    manufacture_date: date | None
    expiry_date: date
    best_before_date: date | None

    supplier_id: UUID | None      # supplier ที่ส่ง lot นี้
    purchase_id: UUID | None      # PO ที่มา
    production_batch_id: UUID | None  # ถ้าผลิตเอง

    notes: str | None
    qc_checked_at: datetime | None
    qc_checked_by: UUID | None
    recalled_at: datetime | None
    recall_reason: str | None

    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls, *, company_id: UUID, product_id: UUID,
        lot_number: str, expiry_date: date,
        manufacture_date: date | None = None,
        best_before_date: date | None = None,
        supplier_id: UUID | None = None,
        purchase_id: UUID | None = None,
        production_batch_id: UUID | None = None,
        notes: str | None = None,
        created_by: UUID,
    ) -> "Lot":
        return cls(
            id=uuid4(),
            company_id=company_id,
            product_id=product_id,
            lot_number=LotNumber(lot_number),
            status=LotStatus.ACTIVE,
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            best_before_date=best_before_date,
            supplier_id=supplier_id,
            purchase_id=purchase_id,
            production_batch_id=production_batch_id,
            notes=notes,
            qc_checked_at=None,
            qc_checked_by=None,
            recalled_at=None,
            recall_reason=None,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def release_qc(self, *, by_user: UUID) -> None:
        if self.status != LotStatus.QUARANTINE:
            raise ValueError("release_qc ได้เฉพาะ QUARANTINE")
        self.status = LotStatus.RELEASED
        self.qc_checked_at = datetime.utcnow()
        self.qc_checked_by = by_user
        self.updated_at = datetime.utcnow()

    def reject_qc(self, reason: str) -> None:
        self.status = LotStatus.REJECTED
        self.notes = f"{self.notes or ''}\nREJECTED: {reason}"
        self.updated_at = datetime.utcnow()

    def recall(self, reason: str) -> None:
        """🚨 Recall — ต้อง trace forward"""
        self.status = LotStatus.RECALLED
        self.recalled_at = datetime.utcnow()
        self.recall_reason = reason
        self.updated_at = datetime.utcnow()

    def is_usable(self, today: date | None = None) -> bool:
        if self.status not in (LotStatus.ACTIVE, LotStatus.RELEASED):
            return False
        if self.is_expired(today):
            return False
        return True

    def is_expired(self, today: date | None = None) -> bool:
        return self.expiry_date < (today or date.today())

    def expiry_bucket(self, today: date | None = None) -> ExpiryBucket:
        return ExpiryInfo(
            manufacture_date=self.manufacture_date,
            expiry_date=self.expiry_date,
            best_before_date=self.best_before_date,
        ).bucket(today)


@dataclass
class LotBalance:
    """
    LotBalance — ยอดคงเหลือของ lot ในแต่ละ warehouse
    (denormalized จาก stock_balances + lots)
    """
    id: UUID
    company_id: UUID
    lot_id: UUID
    warehouse_id: UUID
    quantity: Decimal
    unit: str
    updated_at: datetime
```

## 8.3.3 Domain Events

```python
# app/modules/lot/domain/events.py

class LotCreated(DomainEvent): ...
class LotReleased(DomainEvent): ...
class LotRejected(DomainEvent): ...
class LotRecalled(DomainEvent):
    """🚨 Recall — trigger trace forward + alert"""
    ...
class LotExpiringSoon(DomainEvent): ...
class LotExpired(DomainEvent): ...
```

## 8.3.4 Application — FEFO Picker (สำคัญ)

```python
# app/modules/lot/application/use_cases.py

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from uuid import UUID

from app.modules.lot.domain.entities import Lot
from app.modules.lot.domain.value_objects import LotStatus
from app.modules.lot.application.interfaces import (
    ILotRepository, ILotBalanceRepository,
)


@dataclass
class FefoPickResult:
    lot_id: UUID
    lot_number: str
    expiry_date: date
    quantity: Decimal
    unit_cost: Decimal


class PickFefoUseCase:
    """
    🎯 FEFO picker — หยิบ lot ที่หมดอายุก่อน

    ใช้โดย inventory ตอน post OUT movement

    Logic:
    1.  ดึง lot ที่ usable ใน warehouse นั้น
    2.  เรียงตาม expiry_date ASC
    3.  ตัด lot ที่ status ไม่ USEABLE
    4.  ถ้า quantity ที่ต้องการ > lot แรก → ตัดข้าม lot ถัดไป
    """

    def __init__(
        self, lots: ILotRepository, lot_balances: ILotBalanceRepository,
    ):
        self.lots = lots
        self.lot_balances = lot_balances

    async def pick(
        self, *, company_id: UUID, warehouse_id: UUID,
        product_id: UUID, required_qty: Decimal,
    ) -> list[FefoPickResult]:
        # 1. หา lot ที่ available
        candidates = await self.lot_balances.list_available_in_warehouse(
            company_id=company_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            min_quantity=Decimal("0.001"),
        )

        # 2. filter usable
        today = date.today()
        usable = []
        for c in candidates:
            lot = await self.lots.get_by_id(c.lot_id)
            if not lot or not lot.is_usable(today):
                continue
            usable.append((lot, c))

        # 3. sort by expiry ASC (FEFO)
        usable.sort(key=lambda x: x[0].expiry_date)

        # 4. pick
        picks: list[FefoPickResult] = []
        remaining = required_qty
        for lot, balance in usable:
            if remaining <= 0:
                break
            take = min(remaining, balance.quantity)
            picks.append(FefoPickResult(
                lot_id=lot.id,
                lot_number=lot.lot_number.value,
                expiry_date=lot.expiry_date,
                quantity=take,
                unit_cost=Decimal("0"),  # จะ resolve จาก valuation
            ))
            remaining -= take

        if remaining > 0:
            raise ValueError(
                f"FEFO: lot usable ไม่พอ — ขาด {remaining}"
            )
        return picks


# ============================================================
# Traceability
# ============================================================

@dataclass
class TraceForwardQuery:
    """ไปข้างหน้า — lot นี้ไปถึงใคร"""
    lot_id: UUID


class TraceForwardUseCase:
    """
    ไล่จาก lot → shipment → customer

    ใช้ตอน recall: ลูกค้าคนไหนได้ lot นี้ไป
    """

    def __init__(self, lots, movements, shipments_port, customers_port):
        ...

    async def execute(self, q: TraceForwardQuery) -> dict:
        lot = await self.lots.get_by_id(q.lot_id)
        if not lot:
            raise ValueError("ไม่พบ lot")

        # 1. หา movements ของ lot นี้
        moves = await self.movements.list_by_lot(
            lot.company_id, q.lot_id,
        )

        # 2. filter outbound → ship/sale
        shipments = []
        for m in moves:
            if m.movement_type.value in ("sale", "transfer_out"):
                shipment = await self.shipments_port.find_by_movement(m.id)
                if shipment:
                    shipments.append({
                        "movement_id": str(m.id),
                        "shipment_id": str(shipment["id"]),
                        "customer_id": shipment["customer_id"],
                        "customer_name": shipment["customer_name"],
                        "quantity": str(m.quantity),
                        "shipped_at": shipment["shipped_at"],
                    })

        return {
            "lot": {
                "id": str(lot.id),
                "lot_number": lot.lot_number.value,
                "product_id": str(lot.product_id),
                "expiry_date": str(lot.expiry_date),
                "status": lot.status.value,
            },
            "outbound_shipments": shipments,
            "total_customers": len({s["customer_id"] for s in shipments}),
        }


@dataclass
class TraceBackwardQuery:
    """ย้อนกลับ — lot นี้มาจากไหน"""
    lot_id: UUID


class TraceBackwardUseCase:
    """
    ไล่จาก lot → PO → supplier / batch → raw materials
    """

    def __init__(self, lots, movements, po_port, batch_port):
        ...

    async def execute(self, q: TraceBackwardQuery) -> dict:
        lot = await self.lots.get_by_id(q.lot_id)
        if not lot:
            raise ValueError("ไม่พบ lot")

        source = {}
        if lot.purchase_id:
            po = await self.po_port.get_by_id(lot.purchase_id)
            source = {
                "type": "purchase",
                "po_id": str(lot.purchase_id),
                "po_number": po["po_number"] if po else None,
                "supplier_id": po["supplier_id"] if po else None,
                "supplier_name": po["supplier_name"] if po else None,
            }
        elif lot.production_batch_id:
            batch = await self.batch_port.get_by_id(lot.production_batch_id)
            # recursive — raw materials ของ batch
            source = {
                "type": "production",
                "batch_id": str(lot.production_batch_id),
                "batch_number": batch["batch_number"] if batch else None,
                "raw_lots": batch["input_lots"] if batch else [],
            }

        return {
            "lot": {
                "id": str(lot.id),
                "lot_number": lot.lot_number.value,
                "product_id": str(lot.product_id),
            },
            "source": source,
        }
```

## 8.3.5 Infrastructure — Models

```python
# app/modules/lot/infrastructure/models.py

from sqlalchemy import (
    Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class LotModel(Base):
    __tablename__ = "lots"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "product_id", "lot_number",
            name="uq_lot_company_product_number",
        ),
        Index("ix_lot_company_expiry", "company_id", "expiry_date"),
        Index("ix_lot_product", "product_id", "status"),
        Index("ix_lot_status", "company_id", "status"),
        Index("ix_lot_batch", "production_batch_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    manufacture_date: Mapped[Date | None] = mapped_column(Date)
    expiry_date: Mapped[Date] = mapped_column(Date, nullable=False)
    best_before_date: Mapped[Date | None] = mapped_column(Date)

    supplier_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    purchase_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    production_batch_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))

    notes: Mapped[str | None] = mapped_column(Text)
    qc_checked_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    qc_checked_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
    recalled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    recall_reason: Mapped[str | None] = mapped_column(Text)

    created_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class LotBalanceModel(Base):
    __tablename__ = "lot_balances"
    __table_args__ = (
        UniqueConstraint("lot_id", "warehouse_id", name="uq_lot_balance"),
        Index("ix_lotbal_company_warehouse", "company_id", "warehouse_id"),
        Index("ix_lotbal_lot", "lot_id"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    lot_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    warehouse_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(15, 3), default=0)
    unit: Mapped[str] = mapped_column(String(20))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
```

## 8.3.6 Database Schema

```sql
CREATE TABLE lots (
    id                    UUID PRIMARY KEY,
    company_id            UUID NOT NULL,
    product_id            UUID NOT NULL,
    lot_number            VARCHAR(50) NOT NULL,
    status                VARCHAR(20) NOT NULL,

    manufacture_date      DATE,
    expiry_date           DATE NOT NULL,
    best_before_date      DATE,

    supplier_id           UUID,
    purchase_id           UUID,
    production_batch_id   UUID,

    notes                 TEXT,
    qc_checked_at         TIMESTAMPTZ,
    qc_checked_by         UUID,
    recalled_at           TIMESTAMPTZ,
    recall_reason         TEXT,

    created_by            UUID NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL,
    updated_at            TIMESTAMPTZ NOT NULL,

    UNIQUE (company_id, product_id, lot_number)
);

CREATE INDEX ix_lot_company_expiry ON lots (company_id, expiry_date);
CREATE INDEX ix_lot_product_status ON lots (product_id, status);
CREATE INDEX ix_lot_batch ON lots (production_batch_id) WHERE production_batch_id IS NOT NULL;
CREATE INDEX ix_lot_status ON lots (company_id, status)
    WHERE status IN ('quarantine', 'recalled');

CREATE TABLE lot_balances (
    id              UUID PRIMARY KEY,
    company_id      UUID NOT NULL,
    lot_id          UUID NOT NULL REFERENCES lots(id),
    warehouse_id    UUID NOT NULL,
    quantity        NUMERIC(15,3) NOT NULL DEFAULT 0,
    unit            VARCHAR(20) NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (lot_id, warehouse_id)
);

CREATE INDEX ix_lotbal_company_warehouse ON lot_balances (company_id, warehouse_id);
CREATE INDEX ix_lotbal_expiring_soon ON lot_balances (warehouse_id, quantity)
    WHERE quantity > 0;
```

## 8.3.7 Presentation — API

```python
# app/modules/lot/presentation/routers.py

router = APIRouter(prefix="/api/v1/lots", tags=["Lot"])


@router.post("/", status_code=201)
async def create_lot(
    body: CreateLotRequest,
    user = Depends(require_permission("stock:receive")),
):
    ...


@router.get("/")
async def list_lots(
    product_id: UUID | None = Query(None),
    status: str | None = Query(None),
    expiring_within_days: int | None = Query(None),
    user = Depends(require_permission("stock:read")),
):
    ...


@router.get("/{lot_id}")
async def get_lot(lot_id: UUID, ...): ...


@router.post("/{lot_id}/release-qc")
async def release_qc(
    lot_id: UUID,
    user = Depends(require_permission("quality:approve")),
):
    ...


@router.post("/{lot_id}/recall")
async def recall_lot(
    lot_id: UUID,
    body: RecallRequest,
    user = Depends(require_permission("quality:approve")),
):
    """🚨 Recall — trigger trace + alert"""
    ...


# ---------- FEFO ----------
@router.post("/pick-fefo")
async def pick_fefo(
    body: FefoRequest,
    user = Depends(require_permission("stock:read")),
):
    """จำลอง FEFO pick"""
    ...


# ---------- Traceability ----------
@router.get("/{lot_id}/trace-forward")
async def trace_forward(
    lot_id: UUID,
    user = Depends(require_permission("stock:read")),
):
    """ไปข้างหน้า: lot → shipment → customer"""
    ...


@router.get("/{lot_id}/trace-backward")
async def trace_backward(
    lot_id: UUID,
    user = Depends(require_permission("stock:read")),
):
    """ย้อนกลับ: lot → PO/batch → supplier"""
    ...


@router.get("/expiring")
async def list_expiring(
    days: int = Query(7, le=90),
    user = Depends(require_permission("stock:read")),
):
    """lot ที่ใกล้หมดอายุ"""
    ...


@router.get("/expired")
async def list_expired(
    user = Depends(require_permission("stock:read")),
):
    ...
```

## 8.3.8 Folder Structure

```text
app/modules/lot/
├── domain/
│   ├── entities.py            # Lot, LotBalance
│   ├── value_objects.py       # LotNumber, LotStatus, ExpiryInfo, ExpiryBucket
│   ├── events.py
│   └── errors.py
├── application/
│   ├── interfaces.py
│   └── use_cases.py           # PickFefo, TraceForward, TraceBackward, Recall
├── infrastructure/
│   ├── models.py
│   └── repositories.py
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── domain/
    │   └── test_expiry_bucket.py
    ├── application/
    │   ├── test_fefo_picker.py
    │   ├── test_fefo_skips_expired.py
    │   ├── test_fefo_skips_recalled.py
    │   ├── test_trace_forward.py
    │   └── test_trace_backward.py
    └── integration/
        └── test_recall_flow.py
```

## 8.3.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Month 2) |
| **DoD** | ✅ Lot number unique<br>✅ Expiry validation<br>✅ FEFO picker ทำงาน<br>✅ FEFO skip expired/recalled<br>✅ Trace forward + backward<br>✅ Recall → alert + trace<br>✅ Expiry alert (7/30 วัน) |

---

# 📊 PART 8 — สรุป

## Dependency Graph

```text
                    ┌──────────────────┐
                    │  core/money (L0) │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  warehouse    │◄───│   inventory   │───►│     lot       │
│               │    │               │    │               │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        │                    │ StockPosted        │
        │                    ▼                    │
        │            ┌───────────────┐            │
        │            │ ledger (L2)   │            │
        │            │ Dr.COGS       │            │
        │            │   Cr.Inventory│            │
        │            └───────────────┘            │
        │                                          │
        └──────────────────┬───────────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │ reconciliation (L2)        │
              │ INVENTORY.001-007          │
              │ PRODUCTION.001-005         │
              └────────────────────────────┘
```

## Goods Path → Checks Mapping

| Module | Checks ที่ตรวจ |
|--------|---------------|
| warehouse | — |
| inventory | `INVENTORY.001` (balance ≠ Σmovement)<br>`INVENTORY.003` (negative)<br>`INVENTORY.004` (no reference)<br>`INVENTORY.005` (timestamp anomaly) |
| lot | `INVENTORY.002` (expired with balance)<br>`INVENTORY.006` (no warehouse)<br>`INVENTORY.007` (duplicate lot) |
| production (Part 9) | `PRODUCTION.001` (yield)<br>`PRODUCTION.002` (long open)<br>`PRODUCTION.003` (BOM)<br>`PRODUCTION.004` (no recipe)<br>`PRODUCTION.005` (waste) |

## Checklist รวม Part 8

```text
┌─────────────────────────────────────────────────────────────────┐
│  GOODS PATH — FINAL CHECKLIST                                   │
├─────────────────────────────────────────────────────────────────┤
│  warehouse                                                      │
│   □ Warehouse + Zone + Bin                                      │
│   □ Temperature compatibility (frozen → chilled ห้าม)          │
│   □ Transfer atomic (2 ฝั่ง)                                    │
│   □ Reserve + Release                                           │
├─────────────────────────────────────────────────────────────────┤
│  inventory                                                      │
│   □ Append-only movement                                        │
│   □ Balance = Σ movements (recon)                               │
│   □ Read-back verify หลัง post                                  │
│   □ FEFO/FIFO valuation                                         │
│   □ Reserve + Release atomic                                    │
│   □ Negative stock → alert                                      │
│   □ Concurrency: 10 threads → balance ถูก                       │
│   □ Ledger handler post journal                                 │
│   □ Cycle count / adjustment                                    │
├─────────────────────────────────────────────────────────────────┤
│  lot                                                            │
│   □ Lot number unique                                           │
│   □ Expiry validation                                           │
│   □ FEFO picker                                                 │
│   □ Skip expired/recalled                                       │
│   □ Trace forward + backward                                    │
│   □ Recall → alert + trace                                      │
│   □ Expiry alert (7/30 วัน)                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics ที่ติดตาม

| Metric | Target | ตรวจโดย |
|--------|--------|---------|
| Stock accuracy (balance vs count) | ≥ 99% | Cycle count + INVENTORY.001 |
| Negative stock occurrences | 0 | INVENTORY.003 |
| Expired stock with balance | 0 | INVENTORY.002 |
| FEFO compliance rate | ≥ 99% | Audit log |
| Trace forward coverage | 100% | TraceForwardUseCase |
| Trace backward coverage | 100% | TraceBackwardUseCase |
| Transfer atomicity | 100% | Integration test |
| Reservation leak | 0 | Reconciliation |
| Lot expiry alert latency | < 1h | Monitoring |

## ลำดับการ Implement

```text
Week 1-2 (Month 2):
  Day 1-3: warehouse domain (Warehouse, Zone, Bin)
  Day 4-5: warehouse use cases + transfer
  Day 6-7: inventory domain (Movement, Balance, Reservation)
  Day 8-10: inventory use cases (PostMovement, Reserve, Adjust)
  Day 11-12: lot module (Lot, FEFO, Trace)
  Day 13: inventory + ledger handler
  Day 14: integration test (receive → stock → ledger)
  Day 15: deploy staging + รันกับข้อมูลจริง
```

---
 