## 📄 Module 1.1: `tenancy`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `tenancy` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core |
| **Dependencies** | `tenant_context`, `config`, `audit`, `events` |
| **Domain Concepts** | `Tenant` (entity), `TenantPlan` (VO), `TenantStatus` (enum) |
| **Prefix** | `ten` |
| **Tables** | `public.tenants`, `public.tenant_plans` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `tenancy`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Module นี้เป็น **root tenant management** — สร้าง/ปิด tenant
- Tenant ต้องมี: `slug` (unique), `name`, `plan`, `status`, `schema_name`
- เมื่อสร้าง tenant → สร้าง PostgreSQL schema `tenant_{id}` อัตโนมัติ
- รองรับ plan: `FREE`, `STARTER`, `PROFESSIONAL`, `ENTERPRISE`
- Soft delete เท่านั้น — ห้าม hard delete tenant

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Tenant**
```python
@dataclass
class Tenant(BaseEntity):
    """Tenant entity — เอนทิตีผู้เช่า"""
    slug: str = ""
    name: str = ""
    plan: str = "FREE"
    status: str = "ACTIVE"
    schema_name: str = ""
    owner_email: str = ""
    trial_ends_at: datetime | None = None
    max_users: int = 5
    max_storage_gb: int = 1

    def __post_init__(self):
        self._validate()
        if not self.schema_name:
            self.schema_name = f"tenant_{self.id}"

    def _validate(self) -> None:
        if not self.slug or not re.match(r"^[a-z][a-z0-9-]{2,30}$", self.slug):
            raise DomainError(f"Invalid slug: {self.slug}")
        if not self.name:
            raise DomainError("Tenant name is required")

    def activate(self) -> None:
        if self.status == "ACTIVE":
            raise DomainError("Tenant already active")
        self.status = "ACTIVE"

    def suspend(self, reason: str) -> None:
        if self.status == "SUSPENDED":
            raise DomainError("Tenant already suspended")
        self.status = "SUSPENDED"

    def upgrade_plan(self, new_plan: str) -> None:
        if new_plan not in ("FREE", "STARTER", "PROFESSIONAL", "ENTERPRISE"):
            raise DomainError(f"Invalid plan: {new_plan}")
        self.plan = new_plan

    def is_trial_expired(self) -> bool:
        if self.trial_ends_at is None:
            return False
        return datetime.utcnow() > self.trial_ends_at
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class TenantPlan:
    """Tenant plan VO — วัตถุแผน"""
    code: str
    name: str
    max_users: int
    max_storage_gb: int
    price_monthly: Decimal

    def __post_init__(self):
        if self.max_users <= 0:
            raise DomainError("Max users must be positive")

@dataclass(frozen=True)
class TenantSlug:
    """Tenant slug VO — วัตถุ slug"""
    value: str

    PATTERN = r"^[a-z][a-z0-9-]{2,30}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid slug: {self.value}")
```

**`domain/enums.py`**
```python
class TenantStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    CANCELLED = "CANCELLED"

class TenantPlanCode(str, Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class ITenantRepository(Protocol):
    async def save(self, tenant: Tenant) -> Tenant: ...
    async def get_by_id(self, id: str) -> Tenant | None: ...
    async def get_by_slug(self, slug: str) -> Tenant | None: ...
    async def list(self, page: int, limit: int) -> tuple[list[Tenant], int]: ...

class ITenantCache(Protocol):
    async def get(self, id: str) -> Tenant | None: ...
    async def insert(self, id: str, tenant: Tenant) -> None: ...
    async def delete(self, id: str) -> None: ...

class ISchemaManager(Protocol):
    async def create_schema(self, schema_name: str) -> None: ...
    async def drop_schema(self, schema_name: str) -> None: ...
    async def schema_exists(self, schema_name: str) -> bool: ...
```

**`application/use_cases.py`**
```python
class TenancyUseCases:
    """Tenancy use cases — กรณีการใช้งาน tenancy"""

    def __init__(self, repo, cache, schema_mgr, idempotency, audit, events):
        self.repo = repo
        self.cache = cache
        self.schema_mgr = schema_mgr
        self.idempotency = idempotency
        self.audit = audit
        self.events = events

    async def create_tenant(self, payload: dict, idem_key: str) -> Tenant:
        """Create tenant + schema — สร้าง tenant + schema"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            tenant = Tenant(**payload)

            # Check slug uniqueness
            if await self.repo.get_by_slug(tenant.slug):
                raise TenantSlugConflictException(tenant.slug)

            # Create schema
            await self.schema_mgr.create_schema(tenant.schema_name)

            # Save
            tenant = await self.repo.save(tenant)

            # Read-back
            verified = await self.repo.get_by_id(tenant.id)
            if not verified or verified.slug != tenant.slug:
                await self.schema_mgr.drop_schema(tenant.schema_name)
                raise TenancyException("Read-back failed")

            await self.audit.log("tenant.created", tenant.id)
            await self.idempotency.set(idem_key, tenant)
            await self.events.publish("TenantCreated", tenant)

            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_tenant")
            raise TenancyException()

    async def suspend_tenant(self, id: str, reason: str) -> Tenant:
        try:
            tenant = await self.repo.get_by_id(id)
            if not tenant:
                raise TenantNotFoundException()
            tenant.suspend(reason)
            tenant = await self.repo.save(tenant)
            await self.cache.delete(id)
            await self.audit.log("tenant.suspended", id)
            await self.events.publish("TenantSuspended", {"id": id, "reason": reason})
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in suspend_tenant")
            raise TenancyException()

    async def upgrade_plan(self, id: str, new_plan: str) -> Tenant:
        try:
            tenant = await self.repo.get_by_id(id)
            if not tenant:
                raise TenantNotFoundException()
            tenant.upgrade_plan(new_plan)
            tenant = await self.repo.save(tenant)
            await self.cache.delete(id)
            await self.audit.log("tenant.upgraded", id)
            await self.events.publish("TenantPlanUpgraded", {"id": id, "plan": new_plan})
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in upgrade_plan")
            raise TenancyException()
```

**`application/mappers.py`** — `TenantMapper`
**`application/exceptions.py`** — `TenancyException`, `TenantSlugConflictException`, `TenantNotFoundException`
**`application/utils.py`** — `validate_slug()`, `generate_schema_name()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class TenantModel(BaseModel):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    plan = Column(String(20), nullable=False, default="FREE")
    status = Column(String(20), nullable=False, default="ACTIVE")
    schema_name = Column(String(100), unique=True, nullable=False)
    owner_email = Column(String(255), nullable=False)
    trial_ends_at = Column(DateTime(timezone=True))
    max_users = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=1)
```

**`infrastructure/repositories.py`** — `PostgresTenantRepository`
**`infrastructure/caches.py`** — `RedisTenantCache` (TTL 300s, never raises)
**`infrastructure/services.py`**
```python
class PostgresSchemaManager:
    """Schema manager — จัดการ PostgreSQL schema"""
    def __init__(self, session):
        self.session = session

    async def create_schema(self, schema_name: str) -> None:
        try:
            await self.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            await self.session.flush()
        except Exception as e:
            logger.opt(exception=e).error(f"Schema create failed: {schema_name}")
            raise

    async def drop_schema(self, schema_name: str) -> None:
        try:
            await self.session.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
            await self.session.flush()
        except Exception as e:
            logger.opt(exception=e).error(f"Schema drop failed: {schema_name}")
            raise

    async def schema_exists(self, schema_name: str) -> bool:
        result = await self.session.execute(
            text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"),
            {"s": schema_name},
        )
        return result.first() is not None
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/tenants", tags=["Tenancy"])

@router.post("/", status_code=201)
async def create_tenant(
    payload: TenantCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    use_cases: TenancyUseCases = Depends(get_tenancy_use_cases),
): ...

@router.get("/{id}/")
async def get_tenant(id: str, ...): ...

@router.get("/")
async def list_tenants(page: int = 1, limit: int = 20, ...): ...

@router.patch("/{id}/suspend/")
async def suspend_tenant(id: str, payload: SuspendRequest, ...): ...

@router.patch("/{id}/upgrade/")
async def upgrade_plan(id: str, payload: UpgradeRequest, ...): ...
```

**`presentation/schemas.py`** — `TenantCreate`, `TenantResponse`, `SuspendRequest`, `UpgradeRequest`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_tenancy_use_cases()`

### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

### 6. Invariants
- `slug` unique + format `^[a-z][a-z0-9-]{2,30}$`
- `schema_name == f"tenant_{id}"` และ unique
- สร้าง tenant → ต้องสร้าง schema สำเร็จ (atomic)
- ห้าม hard delete tenant
- `plan` ต้องอยู่ในชุดที่กำหนด

### 7. Domain Events
- `TenantCreated`, `TenantSuspended`, `TenantActivated`, `TenantPlanUpgraded`, `TenantDeleted`

### 8. Tests
```python
async def test_create_tenant_with_schema(): ...
async def test_slug_conflict_raises(): ...
async def test_suspend_tenant(): ...
async def test_upgrade_plan(): ...
async def test_property_slug_format(): ...
async def test_property_schema_atomicity():
    """Property: ถ้า save fail → schema ต้องถูก drop"""
    ...
```

## Output
- 23 ไฟล์ (16 Python + 3 SQL + 4 Tests)
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `tenancy`

**`db/migrations/V001__create_tenancy.sql`**
```sql
BEGIN;

CREATE TABLE public.tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    plan            VARCHAR(20) NOT NULL DEFAULT 'FREE',
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    schema_name     VARCHAR(100) NOT NULL UNIQUE,
    owner_email     VARCHAR(255) NOT NULL,
    trial_ends_at   TIMESTAMPTZ,
    max_users       INTEGER NOT NULL DEFAULT 5,
    max_storage_gb  INTEGER NOT NULL DEFAULT 1,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT ck_tenants_slug CHECK (slug ~ '^[a-z][a-z0-9-]{2,30}$')
);

CREATE INDEX ix_tenants_slug ON public.tenants(slug) WHERE deleted_at IS NULL;
CREATE INDEX ix_tenants_status ON public.tenants(status) WHERE deleted_at IS NULL;

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tenants_updated_at
    BEFORE UPDATE ON public.tenants
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

COMMIT;
```

**`db/migrations/V002__seed_tenancy.sql`**
```sql
BEGIN;

INSERT INTO public.tenants (slug, name, plan, status, schema_name, owner_email)
VALUES
    ('demo', 'Demo Company', 'FREE', 'ACTIVE', 'tenant_demo', 'demo@example.com,mycompany.com,gmail.com'),
    ('acme', 'ACME Corp', 'STARTER', 'ACTIVE', 'tenant_acme', 'admin@acme.com')
ON CONFLICT (slug) DO NOTHING;

COMMIT;
```

**`db/migrations/V003__rollback_tenancy.sql`**
```sql
BEGIN;

DROP TRIGGER IF EXISTS trg_tenants_updated_at ON public.tenants;
DROP INDEX IF EXISTS ix_tenants_status;
DROP INDEX IF EXISTS ix_tenants_slug;
DROP TABLE IF EXISTS public.tenants CASCADE;

COMMIT;
```

### 🧪 Tests สำหรับ `tenancy`

**`tests/unit/test_tenancy.py`**
```python
import pytest
from decimal import Decimal
from app.modules.tenancy.domain.entities import Tenant
from app.modules.tenancy.application.exceptions import (
    TenancyException, TenantSlugConflictException,
)

class TestTenantDomain:
    def test_create_valid(self):
        """Test create valid tenant — ทดสอบสร้าง tenant"""
        t = Tenant(slug="acme", name="ACME Corp", owner_email="admin@acme.com")
        assert t.slug == "acme"
        assert t.status == "ACTIVE"
        assert t.schema_name.startswith("tenant_")

    def test_invalid_slug_raises(self):
        """Test invalid slug — ทดสอบ slug ไม่ถูกต้อง"""
        with pytest.raises(Exception):
            Tenant(slug="AB", name="X", owner_email="x@x.com")

    def test_suspend(self):
        """Test suspend — ทดสอบระงับ"""
        t = Tenant(slug="acme", name="ACME", owner_email="x@x.com")
        t.suspend("payment overdue")
        assert t.status == "SUSPENDED"

    def test_upgrade_plan(self):
        """Test upgrade plan — ทดสอบอัปเกรด"""
        t = Tenant(slug="acme", name="ACME", owner_email="x@x.com")
        t.upgrade_plan("PROFESSIONAL")
        assert t.plan == "PROFESSIONAL"

    def test_property_slug_format(self):
        """Property: slug ต้อง match pattern เสมอ"""
        import re
        for slug in ["abc", "acme-corp", "test123"]:
            t = Tenant(slug=slug, name="X", owner_email="x@x.com")
            assert re.match(r"^[a-z][a-z0-9-]{2,30}$", t.slug)
```

**`tests/integration/test_tenancy_repository.py`**
```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:17") as pg:
        yield pg

class TestPostgresTenantRepository:
    async def test_save_and_get(self, postgres): ...
    async def test_slug_unique(self, postgres): ...
    async def test_flush_not_commit(self, postgres): ...
```

**`tests/property/test_tenancy_invariants.py`**
```python
import pytest
from hypothesis import given, strategies as st

class TestTenancyInvariants:
    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=3, max_size=30))
    def test_slug_pattern(self, slug): ...
```

**`tests/manual/manual_test_tenancy.md`**
```markdown
# Manual Test Cases — tenancy

## TC-01: Create Tenant
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | POST /api/v1/tenants/ with valid payload | 201 + tenant_id | ☐ Pass ☐ Fail |
| 2 | ตรวจสอบ schema `tenant_{id}` ถูกสร้าง | schema exists | ☐ Pass ☐ Fail |

## TC-02: Slug Conflict
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | POST ซ้ำด้วย slug เดิม | 409 Conflict | ☐ Pass ☐ Fail |

## TC-03: Suspend Tenant
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | PATCH /{id}/suspend/ | 200 + status=SUSPENDED | ☐ Pass ☐ Fail |
```

---
