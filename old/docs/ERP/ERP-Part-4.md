# 📙 PART 4 — Foundation Layer Modules

> **Layer 1: Foundation** — 3 modules ที่ทุก module อื่นต้องพึ่ง
> `tenancy` · `authentication` · `user`

---

## 4.0 ภาพรวม Layer 1

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 1: FOUNDATION                                     │
│                                                                              │
│   ┌──────────────────┐                                                       │
│   │    tenancy       │  ← บริษัท สาขา provisioning                          │
│   │  (Company,       │                                                       │
│   │   Branch,        │                                                       │
│   │   Settings)      │                                                       │
│   └────────┬─────────┘                                                       │
│            │                                                                 │
│   ┌────────┴─────────┐  ┌──────────────────┐                                 │
│   │  authentication  │  │       user       │                                 │
│   │  (JWT, API Key,  │─►│  (User, Role,    │                                 │
│   │   Session)       │  │   Permission,    │                                 │
│   │                  │  │   RBAC)          │                                 │
│   └──────────────────┘  └──────────────────┘                                 │
│                                                                              │
│   ลำดับการพึ่ง: tenancy → authentication → user                             │
│   (user ต้องรู้ company, authentication ต้องรู้ user)                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**ความสัมพันธ์กับ Layer 0:**

| Layer 1 module | ใช้ Layer 0 |
|----------------|-------------|
| tenancy | tenant_context, audit, events, config |
| authentication | audit, events, config, tenant_context |
| user | audit, events, tenant_context, config |

---

# 🧩 Module 4.1 — `tenancy`

## 4.1.1 Purpose & Scope

**Purpose:** จัดการบริษัทในเครือ + สาขา + settings ต่อบริษัท รองรับ multi-company ERP

**Scope:**
- ✅ Company (นิติบุคคล) + Branch (สาขา)
- ✅ Provisioning schema ใหม่ให้บริษัท
- ✅ Company settings (เลขผู้เสียภาษี, ที่อยู่, เงื่อนไข)
- ✅ Branch settings (ที่อยู่, เครื่อง POS, GPS)
- ✅ Company lifecycle (active, suspended, closed)
- ✅ Cross-company user assignment
- ❌ ไม่เก็บ user (อยู่ใน `user`)
- ❌ ไม่เก็บ config key-value (อยู่ใน `config`)

## 4.1.2 Domain Model

```python
# app/modules/tenancy/domain/value_objects.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re


@dataclass(frozen=True, slots=True)
class TaxId:
    """
    เลขประจำตัวผู้เสียภาษี 13 หลัก (ไทย)
    Invariants:
    - 13 หลัก
    - checksum ตามสูตรกรมสรรพากร
    """
    value: str

    def __post_init__(self) -> None:
        digits = re.sub(r"\D", "", self.value)
        if len(digits) != 13:
            raise ValueError(f"TaxId ต้อง 13 หลัก, got {len(digits)}")
        if not self._is_valid_checksum(digits):
            raise ValueError(f"TaxId checksum ไม่ถูกต้อง: {digits}")
        object.__setattr__(self, "value", digits)

    @staticmethod
    def _is_valid_checksum(d: str) -> bool:
        # ตัวอย่าง checksum ง่าย (ต้องปรับตามสูตรจริง)
        weights = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        total = sum(int(d[i]) * weights[i] for i in range(12))
        check = (11 - (total % 11)) % 10
        return check == int(d[12])


@dataclass(frozen=True, slots=True)
class CompanyCode:
    """รหัสบริษัท เช่น FOODCO, VEGCO (A-Z, 0-9, 3-20 ตัว)"""
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z0-9]{3,20}$", self.value):
            raise ValueError(f"CompanyCode ไม่ถูกต้อง: {self.value}")


@dataclass(frozen=True, slots=True)
class SchemaName:
    """ชื่อ PostgreSQL schema — snake_case, lowercase, ≤63 chars"""
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[a-z][a-z0-9_]{2,62}$", self.value):
            raise ValueError(f"SchemaName ไม่ถูกต้อง: {self.value}")


@dataclass(frozen=True, slots=True)
class CompanyAddress:
    line1: str
    line2: str | None
    subdistrict: str
    district: str
    province: str
    postal_code: str
    country: str = "TH"


class CompanyType(str, Enum):
    HEAD_OFFICE = "head_office"      # สำนักงานใหญ่
    BRANCH = "branch"                # สาขา
    FACTORY = "factory"              # โรงงาน
    RETAIL = "retail"                # ร้านค้าปลีก
    DISTRIBUTOR = "distributor"      # จัดจำหน่าย


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class BranchType(str, Enum):
    FACTORY = "factory"
    WAREHOUSE = "warehouse"
    RETAIL_STORE = "retail_store"
    OFFICE = "office"
    DISTRIBUTION_CENTER = "dc"
```

```python
# app/modules/tenancy/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.tenancy.domain.value_objects import (
    TaxId, CompanyCode, SchemaName, CompanyAddress,
    CompanyType, CompanyStatus, BranchType,
)


@dataclass
class Company:
    """
    Company (นิติบุคคล) — Aggregate Root

    Invariants:
    - code unique ข้ามระบบ
    - schema_name unique + immutable หลังสร้าง
    - tax_id unique
    - ไม่ลบได้ — เปลี่ยน status = CLOSED แทน
    - 1 company มี ≥ 1 branch (head office เป็น default)
    """
    id: UUID
    code: CompanyCode
    name: str
    name_en: str | None
    tax_id: TaxId
    company_type: CompanyType
    status: CompanyStatus
    schema_name: SchemaName
    address: CompanyAddress
    phone: str | None
    email: str | None
    parent_company_id: UUID | None      # บริษัทแม่ (ถ้าเป็นบริษัทในเครือ)
    fiscal_year_start_month: int        # 1-12
    vat_registered: bool
    created_at: datetime
    updated_at: datetime

    _branches: list["Branch"] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        code: str,
        name: str,
        tax_id: str,
        company_type: CompanyType,
        address: CompanyAddress,
        fiscal_year_start_month: int = 1,
        vat_registered: bool = True,
        parent_company_id: UUID | None = None,
        name_en: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> "Company":
        code_vo = CompanyCode(code)
        schema_vo = SchemaName(f"company_{code.lower()}")
        return cls(
            id=uuid4(),
            code=code_vo,
            name=name,
            name_en=name_en,
            tax_id=TaxId(tax_id),
            company_type=company_type,
            status=CompanyStatus.ACTIVE,
            schema_name=schema_vo,
            address=address,
            phone=phone,
            email=email,
            parent_company_id=parent_company_id,
            fiscal_year_start_month=fiscal_year_start_month,
            vat_registered=vat_registered,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def add_branch(self, branch: "Branch") -> None:
        if branch.company_id != self.id:
            raise ValueError("Branch ไม่ได้สังกัดบริษัทนี้")
        self._branches.append(branch)
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: str) -> None:
        if self.status == CompanyStatus.CLOSED:
            raise ValueError("บริษัทปิดแล้ว — suspend ไม่ได้")
        self.status = CompanyStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def close(self) -> None:
        self.status = CompanyStatus.CLOSED
        self.updated_at = datetime.utcnow()

    @property
    def branches(self) -> list["Branch"]:
        return list(self._branches)


@dataclass
class Branch:
    """
    Branch (สาขา / โรงงาน / โกดัง / ร้าน)

    Invariants:
    - code unique ภายใน company
    - 1 branch มี 1 type
    - retail_store ต้องมี pos_terminal_id
    - warehouse ต้องมี capacity
    """
    id: UUID
    company_id: UUID
    code: str                    # "HQ", "BKK01", "PTY01", "FAC01"
    name: str
    branch_type: BranchType
    address: CompanyAddress
    phone: str | None
    is_active: bool
    opened_at: datetime | None
    pos_terminal_id: str | None  # สำหรับ retail_store
    capacity_kg: float | None    # สำหรับ warehouse
    latitude: float | None       # สำหรับ GPS
    longitude: float | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        code: str,
        name: str,
        branch_type: BranchType,
        address: CompanyAddress,
        pos_terminal_id: str | None = None,
        capacity_kg: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        phone: str | None = None,
    ) -> "Branch":
        if branch_type == BranchType.RETAIL_STORE and not pos_terminal_id:
            raise ValueError("retail_store ต้องมี pos_terminal_id")
        if branch_type == BranchType.WAREHOUSE and capacity_kg is None:
            raise ValueError("warehouse ต้องมี capacity_kg")
        return cls(
            id=uuid4(),
            company_id=company_id,
            code=code,
            name=name,
            branch_type=branch_type,
            address=address,
            phone=phone,
            is_active=True,
            opened_at=None,
            pos_terminal_id=pos_terminal_id,
            capacity_kg=capacity_kg,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
```

## 4.1.3 Domain Events

```python
# app/modules/tenancy/domain/events.py

from app.core.events.domain.entities import DomainEvent
from uuid import uuid4
from datetime import datetime


class CompanyCreated(DomainEvent):
    event_type = "tenancy.company.created"
    aggregate_type = "company"

class CompanyProvisioned(DomainEvent):
    event_type = "tenancy.company.provisioned"

class CompanySuspended(DomainEvent):
    event_type = "tenancy.company.suspended"

class CompanyClosed(DomainEvent):
    event_type = "tenancy.company.closed"

class BranchCreated(DomainEvent):
    event_type = "tenancy.branch.created"

class BranchDeactivated(DomainEvent):
    event_type = "tenancy.branch.deactivated"
```

## 4.1.4 Application — Use Cases

```python
# app/modules/tenancy/application/interfaces.py

from typing import Protocol
from uuid import UUID
from app.modules.tenancy.domain.entities import Company, Branch


class ICompanyRepository(Protocol):
    async def get_by_id(self, company_id: UUID) -> Company | None: ...
    async def get_by_code(self, code: str) -> Company | None: ...
    async def get_by_tax_id(self, tax_id: str) -> Company | None: ...
    async def exists_by_code(self, code: str) -> bool: ...
    async def list_all(self, *, include_closed: bool = False) -> list[Company]: ...
    async def save(self, company: Company) -> None: ...
    async def update(self, company: Company) -> None: ...


class IBranchRepository(Protocol):
    async def get_by_id(self, branch_id: UUID) -> Branch | None: ...
    async def list_by_company(self, company_id: UUID) -> list[Branch]: ...
    async def exists_by_code(self, company_id: UUID, code: str) -> bool: ...
    async def save(self, branch: Branch) -> None: ...


class ISchemaProvisioner(Protocol):
    async def create_schema(self, schema_name: str) -> None: ...
    async def run_migrations(self, schema_name: str) -> None: ...
    async def seed_chart_of_accounts(self, schema_name: str) -> None: ...
    async def seed_default_config(self, schema_name: str) -> None: ...
    async def drop_schema(self, schema_name: str) -> None: ...  # ⚠️ dangerous
```

```python
# app/modules/tenancy/application/use_cases.py

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from app.modules.tenancy.domain.entities import Company, Branch
from app.modules.tenancy.domain.value_objects import CompanyType, BranchType, CompanyAddress
from app.modules.tenancy.application.interfaces import (
    ICompanyRepository, IBranchRepository, ISchemaProvisioner,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction
from app.core.events.application.use_cases import PublishEventUseCase
from app.modules.tenancy.domain.events import CompanyCreated, CompanyProvisioned


# ---------- Create Company (full provisioning) ----------

@dataclass
class CreateCompanyCommand:
    code: str
    name: str
    tax_id: str
    company_type: CompanyType
    address: CompanyAddress
    actor_id: UUID
    fiscal_year_start_month: int = 1
    vat_registered: bool = True
    parent_company_id: UUID | None = None
    name_en: str | None = None
    phone: str | None = None
    email: str | None = None


class CreateCompanyUseCase:
    """
    สร้างบริษัทใหม่ + provision schema + seed

    Flow:
    1. ตรวจ duplicate (code, tax_id)
    2. สร้าง Company entity
    3. Save ลง public.companies
    4. Provision schema (create schema, migrations, seed)
    5. Audit + Event
    """

    def __init__(
        self,
        companies: ICompanyRepository,
        branches: IBranchRepository,
        provisioner: ISchemaProvisioner,
        audit: RecordAuditUseCase,
        publish: PublishEventUseCase,
        uow,
    ) -> None:
        self.companies = companies
        self.branches = branches
        self.provisioner = provisioner
        self.audit = audit
        self.publish = publish
        self.uow = uow

    async def execute(self, cmd: CreateCompanyCommand) -> Company:
        if await self.companies.exists_by_code(cmd.code):
            raise ValueError(f"Company code ซ้ำ: {cmd.code}")

        company = Company.create(
            code=cmd.code,
            name=cmd.name,
            name_en=cmd.name_en,
            tax_id=cmd.tax_id,
            company_type=cmd.company_type,
            address=cmd.address,
            fiscal_year_start_month=cmd.fiscal_year_start_month,
            vat_registered=cmd.vat_registered,
            parent_company_id=cmd.parent_company_id,
            phone=cmd.phone,
            email=cmd.email,
        )

        async with self.uow.transaction():
            # 1. save company
            await self.companies.save(company)

            # 2. create head office branch
            ho = Branch.create(
                company_id=company.id,
                code="HQ",
                name=f"{company.name} (สำนักงานใหญ่)",
                branch_type=BranchType.OFFICE,
                address=cmd.address,
            )
            await self.branches.save(ho)

            # 3. audit
            await self.audit.execute(RecordAuditCommand(
                company_id=company.id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.CONFIG_CHANGED,  # หรือสร้าง COMPANY_CREATED ใหม่
                entity_type="company",
                entity_id=company.id,
                after_state={"code": cmd.code, "name": cmd.name, "tax_id": cmd.tax_id},
            ))

            # 4. publish event (outbox)
            await self.publish.execute(CompanyCreated.create(
                company_id=company.id,
                payload={"code": cmd.code, "name": cmd.name},
                actor_id=cmd.actor_id,
            ))

        # 5. provision schema (นอก transaction — ถ้าพังต้อง retry แยก)
        try:
            await self.provisioner.create_schema(company.schema_name.value)
            await self.provisioner.run_migrations(company.schema_name.value)
            await self.provisioner.seed_chart_of_accounts(company.schema_name.value)
            await self.provisioner.seed_default_config(company.schema_name.value)

            await self.publish.execute(CompanyProvisioned.create(
                company_id=company.id,
                payload={"schema": company.schema_name.value},
                actor_id=cmd.actor_id,
            ))
        except Exception as e:
            # mark company as provisioning_failed
            # (ควรมี status แยก)
            raise

        return company


# ---------- Create Branch ----------

@dataclass
class CreateBranchCommand:
    company_id: UUID
    code: str
    name: str
    branch_type: BranchType
    address: CompanyAddress
    actor_id: UUID
    pos_terminal_id: str | None = None
    capacity_kg: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None


class CreateBranchUseCase:
    def __init__(self, companies, branches, audit, publish, uow):
        ...

    async def execute(self, cmd: CreateBranchCommand) -> Branch:
        company = await self.companies.get_by_id(cmd.company_id)
        if not company:
            raise ValueError("ไม่พบบริษัท")

        if await self.branches.exists_by_code(cmd.company_id, cmd.code):
            raise ValueError(f"Branch code ซ้ำ: {cmd.code}")

        branch = Branch.create(
            company_id=cmd.company_id,
            code=cmd.code,
            name=cmd.name,
            branch_type=cmd.branch_type,
            address=cmd.address,
            pos_terminal_id=cmd.pos_terminal_id,
            capacity_kg=cmd.capacity_kg,
            latitude=cmd.latitude,
            longitude=cmd.longitude,
            phone=cmd.phone,
        )

        async with self.uow.transaction():
            await self.branches.save(branch)
            await self.audit.execute(RecordAuditCommand(
                company_id=cmd.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.CONFIG_CHANGED,
                entity_type="branch",
                entity_id=branch.id,
                after_state={"code": cmd.code, "name": cmd.name},
            ))
            await self.publish.execute(BranchCreated.create(
                company_id=cmd.company_id,
                payload={"branch_id": str(branch.id), "code": cmd.code},
                actor_id=cmd.actor_id,
            ))
        return branch


# ---------- List / Get / Suspend / Close ----------

class GetCompanyUseCase: ...
class ListCompaniesUseCase: ...
class SuspendCompanyUseCase: ...
class CloseCompanyUseCase: ...
class UpdateCompanyUseCase: ...
```

## 4.1.5 Infrastructure

```python
# app/modules/tenancy/infrastructure/models.py

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import Base


class CompanyModel(Base):
    """ตาราง companies — เก็บใน public schema"""
    __tablename__ = "companies"
    __table_args__ = (
        Index("ix_companies_code", "code", unique=True),
        Index("ix_companies_tax_id", "tax_id", unique=True),
        Index("ix_companies_schema", "schema_name", unique=True),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255))
    tax_id: Mapped[str] = mapped_column(String(13), nullable=False)
    company_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    schema_name: Mapped[str] = mapped_column(String(63), nullable=False)
    parent_company_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )

    # address (flatten)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(255))
    subdistrict: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="TH")

    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    fiscal_year_start_month: Mapped[int] = mapped_column(Integer, default=1)
    vat_registered: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    branches: Mapped[list["BranchModel"]] = relationship(
        "BranchModel", back_populates="company", cascade="all, delete-orphan",
    )


class BranchModel(Base):
    """ตาราง branches — เก็บใน public schema"""
    __tablename__ = "branches"
    __table_args__ = (
        Index("ix_branches_company_code", "company_id", "code", unique=True),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch_type: Mapped[str] = mapped_column(String(20), nullable=False)

    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(255))
    subdistrict: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    opened_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    pos_terminal_id: Mapped[str | None] = mapped_column(String(50))
    capacity_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    company: Mapped[CompanyModel] = relationship("CompanyModel", back_populates="branches")
```

```python
# app/modules/tenancy/infrastructure/repositories.py

from uuid import UUID
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tenancy.domain.entities import Company, Branch
from app.modules.tenancy.domain.value_objects import (
    CompanyCode, TaxId, SchemaName, CompanyAddress,
    CompanyType, CompanyStatus, BranchType,
)
from app.modules.tenancy.infrastructure.models import CompanyModel, BranchModel


class PostgresCompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, company_id: UUID) -> Company | None:
        stmt = (
            select(CompanyModel)
            .where(CompanyModel.id == company_id)
            .options(selectinload(CompanyModel.branches))
        )
        m = (await self.session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_code(self, code: str) -> Company | None: ...
    async def get_by_tax_id(self, tax_id: str) -> Company | None: ...

    async def exists_by_code(self, code: str) -> bool:
        stmt = select(exists().where(CompanyModel.code == code))
        return (await self.session.execute(stmt)).scalar()

    async def list_all(self, *, include_closed: bool = False) -> list[Company]:
        stmt = select(CompanyModel).options(selectinload(CompanyModel.branches))
        if not include_closed:
            stmt = stmt.where(CompanyModel.status != "closed")
        result = await self.session.execute(stmt.order_by(CompanyModel.code))
        return [self._to_entity(m) for m in result.scalars()]

    async def save(self, company: Company) -> None:
        m = CompanyModel(
            id=company.id,
            code=company.code.value,
            name=company.name,
            name_en=company.name_en,
            tax_id=company.tax_id.value,
            company_type=company.company_type.value,
            status=company.status.value,
            schema_name=company.schema_name.value,
            parent_company_id=company.parent_company_id,
            address_line1=company.address.line1,
            address_line2=company.address.line2,
            subdistrict=company.address.subdistrict,
            district=company.address.district,
            province=company.address.province,
            postal_code=company.address.postal_code,
            country=company.address.country,
            phone=company.phone,
            email=company.email,
            fiscal_year_start_month=company.fiscal_year_start_month,
            vat_registered=company.vat_registered,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )
        self.session.add(m)

    async def update(self, company: Company) -> None:
        m = await self.session.get(CompanyModel, company.id)
        if not m:
            raise LookupError(f"ไม่พบบริษัท {company.id}")
        m.name = company.name
        m.name_en = company.name_en
        m.status = company.status.value
        m.updated_at = company.updated_at
        # ... update อื่น ๆ

    @staticmethod
    def _to_entity(m: CompanyModel) -> Company:
        return Company(
            id=m.id,
            code=CompanyCode(m.code),
            name=m.name,
            name_en=m.name_en,
            tax_id=TaxId(m.tax_id),
            company_type=CompanyType(m.company_type),
            status=CompanyStatus(m.status),
            schema_name=SchemaName(m.schema_name),
            address=CompanyAddress(
                line1=m.address_line1, line2=m.address_line2,
                subdistrict=m.subdistrict, district=m.district,
                province=m.province, postal_code=m.postal_code,
                country=m.country,
            ),
            phone=m.phone,
            email=m.email,
            parent_company_id=m.parent_company_id,
            fiscal_year_start_month=m.fiscal_year_start_month,
            vat_registered=m.vat_registered,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class PostgresBranchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, branch_id: UUID) -> Branch | None: ...
    async def list_by_company(self, company_id: UUID) -> list[Branch]: ...
    async def exists_by_code(self, company_id: UUID, code: str) -> bool: ...
    async def save(self, branch: Branch) -> None: ...
```

```python
# app/modules/tenancy/infrastructure/provisioner.py

from sqlalchemy import text
from app.core.tenant_context.application.interfaces import ISchemaProvisioner


class PostgresSchemaProvisioner:
    """
    Provision schema ใหม่สำหรับบริษัท
    """

    def __init__(self, engine, alembic_config) -> None:
        self.engine = engine
        self.alembic_config = alembic_config

    async def create_schema(self, schema_name: str) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    async def run_migrations(self, schema_name: str) -> None:
        """รัน alembic upgrade head ใน schema นั้น"""
        from alembic import command
        cfg = self.alembic_config
        cfg.set_main_option("version_table_schema", schema_name)
        cfg.set_main_option("include_schemas", "true")
        # ใช้ env var ALEMBIC_TARGET_SCHEMA
        import os
        os.environ["ALEMBIC_TARGET_SCHEMA"] = schema_name
        command.upgrade(cfg, "head")

    async def seed_chart_of_accounts(self, schema_name: str) -> None:
        """Seed ผังบัญชีมาตรฐานไทย"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f'SET search_path TO "{schema_name}", public'))
            # insert COA ตาม ผังบัญชีมาตรฐาน
            ...

    async def seed_default_config(self, schema_name: str) -> None:
        """Seed config เริ่มต้น"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f'SET search_path TO "{schema_name}", public'))
            # insert config entries เริ่มต้น (VAT 7%, waste 5%, ...)
            ...

    async def drop_schema(self, schema_name: str) -> None:
        """⚠️ ใช้ตอนปิดบริษัทถาวร — ต้อง confirm"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
```

## 4.1.6 Database Schema

```sql
-- public schema (shared)

CREATE TABLE companies (
    id                     UUID PRIMARY KEY,
    code                   VARCHAR(20) UNIQUE NOT NULL,
    name                   VARCHAR(255) NOT NULL,
    name_en                VARCHAR(255),
    tax_id                 VARCHAR(13) UNIQUE NOT NULL,
    company_type           VARCHAR(20) NOT NULL,
    status                 VARCHAR(20) NOT NULL DEFAULT 'active',
    schema_name            VARCHAR(63) UNIQUE NOT NULL,
    parent_company_id      UUID REFERENCES companies(id),

    address_line1          VARCHAR(255) NOT NULL,
    address_line2          VARCHAR(255),
    subdistrict            VARCHAR(100) NOT NULL,
    district               VARCHAR(100) NOT NULL,
    province               VARCHAR(100) NOT NULL,
    postal_code            VARCHAR(10) NOT NULL,
    country                VARCHAR(2) NOT NULL DEFAULT 'TH',

    phone                  VARCHAR(20),
    email                  VARCHAR(255),
    fiscal_year_start_month INT NOT NULL DEFAULT 1,
    vat_registered         BOOLEAN NOT NULL DEFAULT TRUE,

    created_at             TIMESTAMPTZ NOT NULL,
    updated_at             TIMESTAMPTZ NOT NULL
);

CREATE TABLE branches (
    id               UUID PRIMARY KEY,
    company_id       UUID NOT NULL REFERENCES companies(id),
    code             VARCHAR(20) NOT NULL,
    name             VARCHAR(255) NOT NULL,
    branch_type      VARCHAR(20) NOT NULL,

    address_line1    VARCHAR(255) NOT NULL,
    address_line2    VARCHAR(255),
    subdistrict      VARCHAR(100) NOT NULL,
    district         VARCHAR(100) NOT NULL,
    province         VARCHAR(100) NOT NULL,
    postal_code      VARCHAR(10) NOT NULL,

    phone            VARCHAR(20),
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    opened_at        TIMESTAMPTZ,
    pos_terminal_id  VARCHAR(50),
    capacity_kg      NUMERIC(12,3),
    latitude         NUMERIC(10,7),
    longitude        NUMERIC(10,7),

    created_at       TIMESTAMPTZ NOT NULL,
    updated_at       TIMESTAMPTZ NOT NULL,

    UNIQUE (company_id, code)
);
```

## 4.1.7 Presentation — API

```python
# app/modules/tenancy/presentation/routers.py

router = APIRouter(prefix="/api/v1/companies", tags=["Tenancy"])


@router.post("/", status_code=201)
async def create_company(
    body: CreateCompanyRequest,
    current_user = Depends(authenticate_admin),
    use_case = Depends(get_create_company_use_case),
):
    """สร้างบริษัทใหม่ (ADMIN เท่านั้น) — provision schema"""
    return await use_case.execute(CreateCompanyCommand(
        code=body.code,
        name=body.name,
        name_en=body.name_en,
        tax_id=body.tax_id,
        company_type=body.company_type,
        address=body.address.to_vo(),
        fiscal_year_start_month=body.fiscal_year_start_month,
        vat_registered=body.vat_registered,
        parent_company_id=body.parent_company_id,
        phone=body.phone,
        email=body.email,
        actor_id=current_user.id,
    ))


@router.get("/")
async def list_companies(
    include_closed: bool = Query(False),
    current_user = Depends(authenticate_user),
    use_case = Depends(get_list_companies_use_case),
):
    """ดูรายชื่อบริษัททั้งหมด (ที่ user เข้าถึงได้)"""
    ...


@router.get("/{company_id}")
async def get_company(company_id: UUID, ...): ...


@router.patch("/{company_id}")
async def update_company(company_id: UUID, body: UpdateCompanyRequest, ...): ...


@router.post("/{company_id}/suspend")
async def suspend_company(company_id: UUID, body: SuspendRequest, ...): ...


@router.post("/{company_id}/close")
async def close_company(company_id: UUID, ...): ...


# ---------- Branches ----------

@router.post("/{company_id}/branches", status_code=201)
async def create_branch(company_id: UUID, body: CreateBranchRequest, ...): ...


@router.get("/{company_id}/branches")
async def list_branches(company_id: UUID, ...): ...


@router.get("/{company_id}/branches/{branch_id}")
async def get_branch(company_id: UUID, branch_id: UUID, ...): ...
```

## 4.1.8 Folder Structure

```text
app/modules/tenancy/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── entities.py            # Company, Branch
│   ├── value_objects.py       # TaxId, CompanyCode, SchemaName, CompanyAddress, enums
│   ├── events.py              # CompanyCreated, BranchCreated, ...
│   └── errors.py              # DuplicateCompanyCodeError, ...
├── application/
│   ├── __init__.py
│   ├── interfaces.py          # ICompanyRepository, IBranchRepository, ISchemaProvisioner
│   └── use_cases.py           # CreateCompany, CreateBranch, Get, List, Suspend, Close
├── infrastructure/
│   ├── __init__.py
│   ├── models.py              # CompanyModel, BranchModel
│   ├── repositories.py        # PostgresCompanyRepository, PostgresBranchRepository
│   └── provisioner.py         # PostgresSchemaProvisioner
├── presentation/
│   ├── __init__.py
│   ├── routers.py             # /api/v1/companies/*
│   ├── schemas.py             # CreateCompanyRequest, CompanyResponse, ...
│   └── dependencies.py
└── tests/
    ├── domain/
    │   ├── test_entities.py
    │   └── test_value_objects.py
    ├── application/
    │   └── test_use_cases.py
    └── integration/
        └── test_provisioning.py
```

## 4.1.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (ออกแบบ) / 6 (implement เต็ม) |
| **DoD** | ✅ TaxId validate checksum<br>✅ Company create → provision schema สำเร็จ<br>✅ Branch types ครบ (factory, warehouse, retail, office, dc)<br>✅ Parent-child company ทำงาน<br>✅ Isolation test ผ่าน |

---

# 🧩 Module 4.2 — `authentication`

## 4.2.1 Purpose & Scope

**Purpose:** Authentication ตาม template — JWT (JWS+JWE nested) + API Key + Session + Redis blacklist

**Scope:**
- ✅ Login / Logout / Refresh / Register
- ✅ JWT nested (sign RS256 + encrypt RSA-OAEP-256/A256GCM)
- ✅ API Key auth
- ✅ Session tracking (device, ip, user_agent)
- ✅ Token blacklist (Redis)
- ✅ Multi-company (user มีหลาย company ได้)
- ❌ ไม่เก็บ permission (อยู่ใน `user`)
- ❌ ไม่ทำ authorization (middleware อื่นทำ)

> **หมายเหตุ:** Module นี้ implement ตาม template ที่ให้มา (`app/core/security.py` + `app/modules/authentication/`) — ผมจะสรุปเฉพาะส่วนที่ปรับเพิ่มเพื่อรองรับ multi-company

## 4.2.2 สิ่งที่ปรับจาก Template

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Template เดิม                          ปรับเพิ่มเพื่อ Food ERP          │
├──────────────────────────────────────────────────────────────────────────┤
│  Claims: iss, sub, aud, ...             + company_id, branch_id         │
│  Session: user_id, device, ip           + company_id (session ต่อบริษัท) │
│  Login: username + password             + company_code (optional)       │
│  RBAC: ADMIN/MANAGER/USER               + tenant-scoped roles           │
│  API Key: single default admin          + per-company API key           │
└──────────────────────────────────────────────────────────────────────────┘
```

## 4.2.3 Domain Model (ส่วนที่เพิ่ม)

```python
# app/modules/authentication/domain/value_objects.py (เพิ่มจาก template)

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Claims:
    """
    JWT claims (ขยายจาก template)
    """
    iss: str
    sub: str                    # user_id
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: str
    grant_id: str
    scope: str
    # ---- Food ERP additions ----
    company_id: UUID            # บริษัทที่ login เข้า
    branch_id: UUID | None      # สาขา (ถ้า login แบบ POS)
    roles: list[str]            # roles ในบริษัทนั้น


@dataclass(frozen=True, slots=True)
class RefreshClaims:
    iss: str
    sub: str
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: str
    grant_id: str
    company_id: UUID
```

## 4.2.4 Session Model (ปรับ)

```python
# app/modules/authentication/infrastructure/models.py (เพิ่ม company_id)

class SessionModel(Base):
    __tablename__ = "app_sessions"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)  # NEW
    branch_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))            # NEW

    device_id: Mapped[str | None] = mapped_column(String(100))
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    location: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    access_tokens: Mapped[list["AccessTokenModel"]] = relationship(...)
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(...)
```

## 4.2.5 Login Flow (ปรับสำหรับ multi-company)

```python
# app/modules/authentication/application/use_cases.py

@dataclass
class LoginCommand:
    username: str
    password: str
    company_code: str | None = None   # ถ้าไม่ระบุ → ใช้ default company ของ user
    branch_code: str | None = None    # สำหรับ POS login
    device_id: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None


class AuthenticationUseCases:
    async def login(self, cmd: LoginCommand) -> LoginResult:
        # 1. หา user
        user = await self.user_repo.get_by_username(cmd.username)
        if not user:
            raise InvalidCredentialsException()

        # 2. ตรวจ password
        if not self.hasher.verify(cmd.password, user.password_hash):
            raise InvalidCredentialsException()

        # 3. resolve company
        #    - ถ้าระบุ company_code → ตรวจว่า user มีสิทธิ์ในบริษัทนั้น
        #    - ถ้าไม่ระบุ → ใช้ default company
        company_id = await self._resolve_company(user, cmd.company_code)

        # 4. resolve branch (ถ้าเป็น POS login)
        branch_id = None
        if cmd.branch_code:
            branch = await self.tenancy_repo.get_branch_by_code(company_id, cmd.branch_code)
            if not branch:
                raise InvalidBranchException()
            branch_id = branch.id

        # 5. ดึง roles ของ user ในบริษัทนี้
        roles = await self.user_repo.get_roles(user.id, company_id)

        # 6. สร้าง/หมุนเวียน session
        session = await self._get_or_create_session(
            user_id=user.id,
            company_id=company_id,
            branch_id=branch_id,
            device_id=cmd.device_id,
        )

        # 7. สร้าง tokens (nested JWT)
        access_token, refresh_token = await self._issue_tokens(
            user=user,
            company_id=company_id,
            branch_id=branch_id,
            roles=roles,
            session=session,
        )

        # 8. audit
        await self.audit.execute(RecordAuditCommand(
            company_id=company_id,
            actor_id=user.id,
            actor_type=ActorType.USER,
            action=AuditAction.USER_LOGIN,
            entity_type="session",
            entity_id=session.id,
            metadata={"device_id": cmd.device_id, "ip": cmd.ip_address},
        ))

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.id,
            company_id=company_id,
            branch_id=branch_id,
            expires_in=self.settings.access_token_ttl,
        )
```

## 4.2.6 API Key (ปรับ)

```python
# app/modules/authentication/domain/entities.py (เพิ่ม)

@dataclass
class ApiKey:
    """
    API Key — ผูกกับ company
    ใช้สำหรับ integration: LINE, IoT, หรือ ERP ของบริษัทในเครือ
    """
    id: UUID
    company_id: UUID
    name: str               # "LINE bot production"
    key_hash: str           # hashed (ไม่เก็บ plaintext)
    scopes: list[str]       # ["invoice:read", "stock:read"]
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    created_by: UUID
```

## 4.2.7 Dependencies (ปรับ)

```python
# app/modules/authentication/presentation/dependencies.py

from fastapi import Depends, Header, HTTPException
from app.core.security import decode_jwt
from app.core.tenant_context.domain.context import TenantContext, set_tenant


async def authenticate_user(
    authorization: str | None = Header(None),
    x_company_id: str | None = Header(None),
) -> "AuthenticatedUser":
    """
    อ่าน JWT → decode → verify → return AuthenticatedUser
    (company_id มาจาก claim เสมอ — ห้ามให้ client override)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "ต้อง login")

    token = authorization.removeprefix("Bearer ")
    claims = await decode_jwt(token)

    # ตรวจ blacklist
    if await is_blacklisted(claims["jti"]):
        raise HTTPException(401, "Token ถูกยกเลิก")

    user = AuthenticatedUser(
        id=UUID(claims["sub"]),
        company_id=UUID(claims["company_id"]),
        branch_id=UUID(claims["branch_id"]) if claims.get("branch_id") else None,
        roles=claims["roles"],
        jti=claims["jti"],
        session_id=UUID(claims["grant_id"]),
    )

    # ตั้ง tenant context
    schema_name = await resolve_schema(user.company_id)
    set_tenant(TenantContext(
        company_id=user.company_id,
        schema_name=schema_name,
        user_id=user.id,
    ))

    return user


async def authenticate_admin(user = Depends(authenticate_user)):
    if "admin" not in user.roles:
        raise HTTPException(403, "ต้องเป็น admin")
    return user


async def authenticate_manager(user = Depends(authenticate_user)):
    if not any(r in user.roles for r in ("admin", "manager")):
        raise HTTPException(403, "ต้องเป็น manager ขึ้นไป")
    return user
```

## 4.2.8 Folder Structure (เทียบกับ template)

```text
app/modules/authentication/
├── domain/
│   ├── entities.py            # Session, AccessToken, RefreshToken, ApiKey (NEW)
│   ├── value_objects.py       # Claims (เพิ่ม company_id, branch_id, roles)
│   ├── mappers.py
│   └── services.py
├── application/
│   ├── enums.py
│   ├── interfaces.py          # IAuthenticationRepository, IApiKeyRepository (NEW)
│   └── use_cases.py           # login (ปรับ), refresh, logout, register
├── infrastructure/
│   ├── models.py              # SessionModel (+company_id, branch_id), ApiKeyModel (NEW)
│   └── repositories.py
└── presentation/
    ├── dependencies.py
    ├── routers.py
    ├── schemas.py
    ├── exceptions.py
    └── docs.py
```

## 4.2.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 |
| **DoD** | ✅ login ได้พร้อม company context<br>✅ JWT เก็บ company_id + roles<br>✅ session แยกตาม company<br>✅ API key ผูก company<br>✅ blacklist + refresh ทำงาน |

---

# 🧩 Module 4.3 — `user`

## 4.3.1 Purpose & Scope

**Purpose:** จัดการ user + RBAC (roles, permissions) แบบ tenant-scoped

**Scope:**
- ✅ User (part of company ผ่าน user_company_roles)
- ✅ Role (tenant-scoped)
- ✅ Permission (global + tenant-scoped)
- ✅ RBAC: user × role × company
- ✅ User profile, password change, deactivate
- ❌ ไม่เก็บ session (อยู่ใน `authentication`)
- ❌ ไม่เก็บ employee HR data (อยู่ใน `employee`)

## 4.3.2 Domain Model

```python
# app/modules/user/domain/entities.py

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4
from enum import Enum

from app.modules.user.domain.value_objects import Name, Email, Phone


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """
    User — ระบบ-level user (ไม่ใช่ employee HR)

    Invariants:
    - email unique ข้ามระบบ
    - username unique ข้ามระบบ
    - 1 user อยู่ได้หลาย company ผ่าน UserCompanyRole
    - password_hash ไม่เก็บ plaintext
    - deactivate ได้ — ห้ามลบ
    """
    id: UUID
    username: str
    email: Email
    name: Name
    phone: Phone | None
    gender: Gender
    birthdate: date | None
    password_hash: str
    status: UserStatus
    is_super_admin: bool          # super admin ข้ามบริษัท
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    _company_roles: list["UserCompanyRole"] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password_hash: str,
        gender: Gender = Gender.OTHER,
        birthdate: date | None = None,
        phone: str | None = None,
        is_super_admin: bool = False,
    ) -> "User":
        return cls(
            id=uuid4(),
            username=username,
            email=Email(email),
            name=Name(first_name, last_name),
            phone=Phone(phone) if phone else None,
            gender=gender,
            birthdate=birthdate,
            password_hash=password_hash,
            status=UserStatus.ACTIVE,
            is_super_admin=is_super_admin,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login_at=None,
        )

    def assign_role(self, company_id: UUID, role_id: UUID) -> None:
        if any(
            cr.company_id == company_id and cr.role_id == role_id
            for cr in self._company_roles
        ):
            return
        self._company_roles.append(UserCompanyRole(
            user_id=self.id,
            company_id=company_id,
            role_id=role_id,
            assigned_at=datetime.utcnow(),
        ))
        self.updated_at = datetime.utcnow()

    def has_role_in(self, company_id: UUID, role_name: str) -> bool:
        return any(
            cr.company_id == company_id and cr.role_name == role_name
            for cr in self._company_roles
        )

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()


@dataclass
class Role:
    """
    Role — tenant-scoped
    - super_admin สร้างได้ทุกบริษัท (is_system_role=True)
    - บริษัทสร้าง role เองได้
    """
    id: UUID
    company_id: UUID | None       # None = system role ใช้ได้ทุกบริษัท
    name: str                     # "admin", "manager", "cashier", "accountant"
    description: str
    is_system_role: bool
    permissions: list["Permission"]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Permission:
    """
    Permission — global (resource:action)
    """
    id: UUID
    resource: str                 # "invoice", "stock", "customer", ...
    action: str                   # "read", "create", "update", "delete", "approve"
    description: str

    @property
    def code(self) -> str:
        return f"{self.resource}:{self.action}"


@dataclass
class UserCompanyRole:
    """ความสัมพันธ์ user × company × role"""
    user_id: UUID
    company_id: UUID
    role_id: UUID
    role_name: str
    assigned_at: datetime
    assigned_by: UUID | None
```

## 4.3.3 Seed Permissions (ครอบทุก Module)

```python
# app/modules/user/domain/permissions_seed.py

"""
Permission มาตรฐาน — ใช้ seed ครั้งเดียว
resource:action
"""

PERMISSIONS = [
    # Invoice
    ("invoice", "read"), ("invoice", "create"), ("invoice", "update"),
    ("invoice", "cancel"), ("invoice", "approve"),

    # Ledger
    ("ledger", "read"), ("ledger", "post"), ("ledger", "reverse"),

    # Payment
    ("payment", "read"), ("payment", "create"), ("payment", "refund"),

    # Inventory
    ("stock", "read"), ("stock", "receive"), ("stock", "issue"),
    ("stock", "adjust"), ("stock", "transfer"),

    # Production
    ("production", "read"), ("production", "plan"),
    ("production", "execute"), ("production", "abort"),

    # Procurement
    ("po", "read"), ("po", "create"), ("po", "approve"),

    # Delivery / Transport
    ("shipment", "read"), ("shipment", "dispatch"), ("shipment", "deliver"),

    # Retail
    ("pos", "sell"), ("pos", "void"), ("pos", "refund"),
    ("shift", "open"), ("shift", "close"),

    # Customer
    ("customer", "read"), ("customer", "create"), ("customer", "update"),

    # Supplier
    ("supplier", "read"), ("supplier", "create"), ("supplier", "update"),

    # Product / Pricing
    ("product", "read"), ("product", "create"), ("product", "update"),
    ("pricing", "read"), ("pricing", "update"),

    # Config
    ("config", "read"), ("config", "update"),

    # User
    ("user", "read"), ("user", "create"), ("user", "update"), ("user", "disable"),
    ("role", "read"), ("role", "assign"),

    # Reporting
    ("report", "read"), ("report", "export"),

    # Audit
    ("audit", "read"),
]
```

## 4.3.4 Application — Use Cases

```python
# app/modules/user/application/use_cases.py

from dataclasses import dataclass
from uuid import UUID

from app.modules.user.domain.entities import User, Gender
from app.modules.user.application.interfaces import (
    IUserRepository, IRoleRepository, IPasswordHasher,
)
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction


# ---------- Create User ----------

@dataclass
class CreateUserCommand:
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    company_id: UUID              # company แรกที่ assign
    role_id: UUID
    actor_id: UUID
    gender: Gender = Gender.OTHER
    phone: str | None = None


class CreateUserUseCase:
    def __init__(
        self,
        users: IUserRepository,
        roles: IRoleRepository,
        hasher: IPasswordHasher,
        audit: RecordAuditUseCase,
        uow,
    ):
        self.users = users
        self.roles = roles
        self.hasher = hasher
        self.audit = audit
        self.uow = uow

    async def execute(self, cmd: CreateUserCommand) -> User:
        if await self.users.exists_by_email(cmd.email):
            raise ValueError(f"Email ซ้ำ: {cmd.email}")
        if await self.users.exists_by_username(cmd.username):
            raise ValueError(f"Username ซ้ำ: {cmd.username}")

        password_hash = self.hasher.hash(cmd.password)

        user = User.create(
            username=cmd.username,
            email=cmd.email,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            password_hash=password_hash,
            gender=cmd.gender,
            phone=cmd.phone,
        )
        user.assign_role(cmd.company_id, cmd.role_id)

        async with self.uow.transaction():
            await self.users.save(user)
            await self.audit.execute(RecordAuditCommand(
                company_id=cmd.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.USER_CREATED,
                entity_type="user",
                entity_id=user.id,
                after_state={"username": user.username, "email": str(user.email)},
            ))
        return user


# ---------- Assign Role ----------

@dataclass
class AssignRoleCommand:
    user_id: UUID
    company_id: UUID
    role_id: UUID
    actor_id: UUID


class AssignRoleUseCase:
    """ให้ user มี role ในบริษัทหนึ่ง"""
    ...


# ---------- Change Password ----------

@dataclass
class ChangePasswordCommand:
    user_id: UUID
    old_password: str
    new_password: str
    actor_id: UUID


class ChangePasswordUseCase:
    """
    เปลี่ยน password — audit + revoke ทุก session
    """
    ...


# ---------- Get Permissions ----------

class GetPermissionsUseCase:
    """
    ดึง permission ของ user ในบริษัทหนึ่ง
    ใช้ cache (per user × company)
    """

    def __init__(self, users: IUserRepository, cache):
        self.users = users
        self.cache = cache

    async def execute(self, user_id: UUID, company_id: UUID) -> list[str]:
        cache_key = f"perm:{user_id}:{company_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        perms = await self.users.get_permissions(user_id, company_id)
        await self.cache.set(cache_key, perms, ttl=300)
        return perms
```

## 4.3.5 Infrastructure

```python
# app/modules/user/infrastructure/models.py

class UserModel(Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    gender: Mapped[str] = mapped_column(String(20), default="other")
    birthdate: Mapped[date | None] = mapped_column(Date)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))


class RoleModel(Base):
    __tablename__ = "app_roles"
    __table_args__ = (
        Index("ix_roles_company_name", "company_id", "name", unique=True),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))  # NULL = system role
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class PermissionModel(Base):
    __tablename__ = "app_permissions"
    __table_args__ = (
        Index("ix_perm_resource_action", "resource", "action", unique=True),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255))


class RolePermissionModel(Base):
    __tablename__ = "app_role_permissions"

    role_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("app_roles.id"), primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("app_permissions.id"), primary_key=True,
    )


class UserCompanyRoleModel(Base):
    """user × company × role"""
    __tablename__ = "app_user_company_roles"
    __table_args__ = (
        Index("ix_ucr_user_company", "user_id", "company_id"),
        Index("ix_ucr_unique", "user_id", "company_id", "role_id", unique=True),
    )

    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("app_users.id"), primary_key=True,
    )
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    role_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("app_roles.id"), primary_key=True,
    )
    assigned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    assigned_by: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True))
```

```python
# app/modules/user/infrastructure/repositories.py

class PostgresUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_username(self, username: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def exists_by_username(self, username: str) -> bool: ...
    async def exists_by_email(self, email: str) -> bool: ...
    async def save(self, user: User) -> None: ...
    async def update(self, user: User) -> None: ...

    async def get_roles(self, user_id: UUID, company_id: UUID) -> list[str]:
        """role names ของ user ในบริษัท"""
        stmt = (
            select(RoleModel.name)
            .join(UserCompanyRoleModel, UserCompanyRoleModel.role_id == RoleModel.id)
            .where(
                UserCompanyRoleModel.user_id == user_id,
                UserCompanyRoleModel.company_id == company_id,
            )
        )
        return list((await self.session.execute(stmt)).scalars())

    async def get_permissions(self, user_id: UUID, company_id: UUID) -> list[str]:
        """
        permission codes ของ user ในบริษัท
        = permission ของ role ทั้งหมดที่ user มีในบริษัทนี้
        """
        stmt = (
            select(PermissionModel.resource, PermissionModel.action)
            .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id)
            .join(UserCompanyRoleModel, UserCompanyRoleModel.role_id == RolePermissionModel.role_id)
            .where(
                UserCompanyRoleModel.user_id == user_id,
                UserCompanyRoleModel.company_id == company_id,
            )
            .distinct()
        )
        rows = await self.session.execute(stmt)
        return [f"{r}:{a}" for r, a in rows]

    async def list_companies(self, user_id: UUID) -> list[UUID]:
        """บริษัทที่ user เข้าถึงได้"""
        stmt = (
            select(UserCompanyRoleModel.company_id)
            .where(UserCompanyRoleModel.user_id == user_id)
            .distinct()
        )
        return list((await self.session.execute(stmt)).scalars())
```

## 4.3.6 Database Schema

```sql
CREATE TABLE app_users (
    id              UUID PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    gender          VARCHAR(20) NOT NULL DEFAULT 'other',
    birthdate       DATE,
    password_hash   VARCHAR(255) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    is_super_admin  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    last_login_at   TIMESTAMPTZ
);

CREATE TABLE app_roles (
    id              UUID PRIMARY KEY,
    company_id      UUID,                    -- NULL = system role
    name            VARCHAR(50) NOT NULL,
    description     VARCHAR(255) NOT NULL,
    is_system_role  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL
);

CREATE UNIQUE INDEX ix_roles_company_name
    ON app_roles (COALESCE(company_id, '00000000-0000-0000-0000-000000000000'::uuid), name);

CREATE TABLE app_permissions (
    id          UUID PRIMARY KEY,
    resource    VARCHAR(50) NOT NULL,
    action      VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    UNIQUE (resource, action)
);

CREATE TABLE app_role_permissions (
    role_id       UUID NOT NULL REFERENCES app_roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES app_permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE app_user_company_roles (
    user_id     UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    company_id  UUID NOT NULL,
    role_id     UUID NOT NULL REFERENCES app_roles(id),
    assigned_at TIMESTAMPTZ NOT NULL,
    assigned_by UUID,
    PRIMARY KEY (user_id, company_id, role_id)
);

CREATE INDEX ix_ucr_user_company ON app_user_company_roles (user_id, company_id);
```

## 4.3.7 Authorization Dependency

```python
# app/modules/user/presentation/dependencies.py

from fastapi import Depends, HTTPException


def require_permission(permission: str):
    """
    Dependency factory — ใช้กับ endpoint ที่ต้องการ permission

    Usage:
        @router.post("/invoices", dependencies=[Depends(require_permission("invoice:create"))])
    """
    async def checker(
        user = Depends(authenticate_user),
        get_perms = Depends(get_get_permissions_use_case),
    ):
        if user.is_super_admin:
            return user
        perms = await get_perms.execute(user.id, user.company_id)
        if permission not in perms:
            raise HTTPException(403, f"ต้องมี permission: {permission}")
        return user
    return checker
```

**ใช้จริง:**

```python
@router.post("/api/v1/invoices/")
async def create_invoice(
    body: CreateInvoiceRequest,
    user = Depends(require_permission("invoice:create")),
    use_case = Depends(get_issue_invoice_use_case),
):
    ...
```

## 4.3.8 Seed System Roles

```python
# seed/system_roles.py

SYSTEM_ROLES = {
    "super_admin": ["*:*"],   # ทุก permission
    "admin": [
        "invoice:*", "ledger:*", "payment:*", "stock:*",
        "production:*", "po:*", "shipment:*", "pos:*", "shift:*",
        "customer:*", "supplier:*", "product:*", "pricing:*",
        "config:*", "user:*", "role:*", "report:*", "audit:read",
    ],
    "manager": [
        "invoice:read", "invoice:create", "invoice:approve",
        "stock:read", "stock:adjust",
        "production:read", "production:plan",
        "customer:*", "supplier:read", "product:read",
        "report:read", "report:export",
    ],
    "accountant": [
        "invoice:*", "ledger:*", "payment:*",
        "customer:read", "supplier:read",
        "report:read", "report:export",
        "config:read",
    ],
    "cashier": [
        "pos:sell", "pos:void", "shift:open", "shift:close",
        "customer:read", "product:read", "invoice:read",
    ],
    "warehouse_staff": [
        "stock:read", "stock:receive", "stock:issue", "stock:transfer",
        "product:read",
    ],
    "production_staff": [
        "production:read", "production:execute",
        "stock:read", "stock:issue",
    ],
    "driver": [
        "shipment:read", "shipment:deliver",
        "customer:read",
    ],
}
```

## 4.3.9 Presentation — API

```python
# app/modules/user/presentation/routers.py

router = APIRouter(prefix="/api/v1/users", tags=["User"])


@router.post("/", status_code=201)
async def create_user(
    body: CreateUserRequest,
    user = Depends(require_permission("user:create")),
    use_case = Depends(get_create_user_use_case),
):
    ...


@router.get("/me")
async def get_me(user = Depends(authenticate_user)):
    """โปรไฟล์ตัวเอง + permissions"""
    return {
        "id": user.id,
        "username": user.username,
        "company_id": user.company_id,
        "roles": user.roles,
        "permissions": await get_perms.execute(user.id, user.company_id),
    }


@router.get("/me/companies")
async def list_my_companies(user = Depends(authenticate_user)):
    """บริษัทที่ user เข้าถึงได้"""
    ...


@router.post("/{user_id}/roles")
async def assign_role(
    user_id: UUID,
    body: AssignRoleRequest,
    user = Depends(require_permission("role:assign")),
):
    ...


@router.post("/me/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user = Depends(authenticate_user),
):
    ...


# ---------- Roles ----------

@router.get("/roles")
async def list_roles(user = Depends(require_permission("role:read"))): ...

@router.post("/roles", status_code=201)
async def create_role(user = Depends(require_permission("role:assign"))): ...


# ---------- Permissions ----------

@router.get("/permissions")
async def list_permissions(user = Depends(require_permission("role:read"))): ...
```

## 4.3.10 Folder Structure

```text
app/modules/user/
├── domain/
│   ├── entities.py            # User, Role, Permission, UserCompanyRole
│   ├── value_objects.py       # Name, Email, Phone
│   ├── permission_entities.py
│   ├── permission_mappers.py
│   ├── permissions_seed.py    # PERMISSIONS constant
│   └── errors.py
├── application/
│   ├── enums.py               # Gender, UserStatus
│   ├── interfaces.py          # IUserRepository, IRoleRepository, IPasswordHasher
│   └── use_cases.py           # CreateUser, AssignRole, ChangePassword, GetPermissions
├── infrastructure/
│   ├── models.py              # UserModel, RoleModel, PermissionModel, ...
│   ├── permission_models.py
│   └── repositories.py        # PostgresUserRepository, PostgresRoleRepository
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   ├── dependencies.py        # require_permission
│   └── exceptions.py
└── tests/
    ├── domain/
    ├── application/
    └── integration/
        └── test_rbac.py       # ทดสอบ tenant-scoped RBAC
```

## 4.3.11 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 |
| **DoD** | ✅ user × company × role ทำงาน<br>✅ permission code ครบทุก module<br>✅ require_permission dependency ใช้ได้<br>✅ tenant-scoped RBAC (user A ใน company X ≠ Y)<br>✅ seed system roles ครบ<br>✅ super_admin ข้ามบริษัท |

---

# 📊 PART 4 — สรุป

## Dependency Graph

```text
                    ┌──────────────────┐
                    │    tenancy       │  ← นิยาม Company, Branch
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ authentication   │  ← login + session (ต่อ company)
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      user        │  ← RBAC (user × company × role)
                    └──────────────────┘
                             │
                             ▼
              ทุก module ที่ต้อง auth/permission
```

## Integration ระหว่าง 3 Modules

```text
Login Flow:
  1. authentication.login()
     ├─ user.get_by_username()  [จาก user module]
     ├─ tenancy.resolve_company()  [จาก tenancy module]
     ├─ user.get_roles(user, company)  [จาก user module]
     └─ issue JWT (company_id, roles)

API Request Flow:
  1. authenticate_user()  [authentication]
     ├─ decode JWT → company_id
     ├─ set_tenant(company_id, schema)  [tenant_context]
     └─ return AuthenticatedUser
  2. require_permission("invoice:create")  [user]
     ├─ GetPermissions(user, company)  [cached]
     └─ ตรวจว่ามี permission หรือไม่
  3. UseCase.execute()
     ├─ ทุก query อยู่ใต้ schema ของ company
     └─ audit บันทึก company_id
```

## Checklist รวม Part 4

```text
┌─────────────────────────────────────────────────────────────────┐
│  FOUNDATION LAYER — FINAL CHECKLIST                             │
├─────────────────────────────────────────────────────────────────┤
│  tenancy                                                        │
│   □ TaxId validate checksum                                    │
│   □ Company create → provision schema สำเร็จ                   │
│   □ Branch types ครบ                                            │
│   □ Parent-child company                                        │
│   □ Isolation test ผ่าน                                         │
├─────────────────────────────────────────────────────────────────┤
│  authentication                                                 │
│   □ Login พร้อม company context                                 │
│   □ JWT เก็บ company_id + roles                                │
│   □ Session แยกตาม company                                      │
│   □ API key ผูก company                                         │
│   □ Blacklist + refresh                                         │
│   □ Multi-company user (login เข้าได้หลายบริษัท)               │
├─────────────────────────────────────────────────────────────────┤
│  user                                                           │
│   □ user × company × role                                       │
│   □ Permission code ครบทุก module                              │
│   □ require_permission ใช้ได้                                   │
│   □ Tenant-scoped RBAC                                          │
│   □ Seed system roles                                           │
│   □ super_admin ข้ามบริษัท                                      │
└─────────────────────────────────────────────────────────────────┘
```

## ลำดับการ Implement

```text
Week 1 (Phase 1):
  Day 1-3: tenancy (Company, Branch, provisioner)
  Day 4-7: authentication (ปรับจาก template + multi-company)
  Day 8-10: user (RBAC + permission seed)
  Day 11-12: Integration test (login → permission → use case)
  Day 13-14: Seed + documentation
```

---

## 🔜 Part 5 (ตอนถัดไป) — Money Path Core

จะลงรายละเอียด:
- **Invoice** — Invoice, InvoiceLine, numbering, VAT, cancel/reversal
- **Ledger** — JournalEntry, LedgerLine, double-entry, reversal
- **Tax** — VAT, WHT, e-Tax Invoice

พร้อม folder structure, domain model, use case, infrastructure, presentation, tests และ dependencies ครบเหมือน Part 3-4

---

