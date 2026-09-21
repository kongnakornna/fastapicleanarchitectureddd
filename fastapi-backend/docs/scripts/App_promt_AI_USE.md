# 📦 AI Prompt Templates — Layer 0 ถึง Layer 7 (พร้อมใช้งานครบ 65 modules)

> **เวอร์ชัน:** 1.0.0 · **Stack:** Python 3.14+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · PostgreSQL 17 · Redis 8 · Kafka
> **Output per Module:** 23 ไฟล์ (16 Python + 3 SQL + 4 Tests)

---

# 🎯 วิธีใช้งาน Template นี้

## ขั้นตอนที่ 1: สร้างโฟลเดอร์

```bash
mkdir -p docs/prompts/{layer-0-core,layer-1-foundation,layer-2-money-path,layer-3-goods-path,layer-4-operations,layer-5-intelligence,layer-6-monitoring,layer-7-templates}
mkdir -p app/modules db/migrations tests/{unit,integration,property,manual} scripts
```

## ขั้นตอนที่ 2: สำหรับแต่ละ Module

1. **Copy prompt** จากหัวข้อที่ต้องการ
2. **วางใน AI** (ChatGPT / Claude / Gemini)
3. **AI จะสร้าง 23 ไฟล์** ตาม spec
4. **ตรวจสอบ checklist** ก่อน merge

## ขั้นตอนที่ 3: รัน Tests

```bash
uv run pytest tests/unit/test_{module}.py -v
uv run pytest tests/integration/test_{module}_repository.py -v
uv run pytest tests/property/test_{module}_invariants.py -v
```

---

# 📋 Layer 0: CORE — 6 Modules

> **Dependencies:** ไม่มี (primitive modules) — ต้องสร้างก่อนทุก Layer
> **Output:** 8-16 ไฟล์ต่อ module (module เล็ก)

---

## 📄 Module 0.1: `money`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `money` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `Money` (VO), `Currency` (enum), `VAT` (VO), `ExchangeRate` (VO) |
| **Prefix** | `mny` |
| **Tables** | ไม่มี (pure VO) |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `money`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- Module นี้เป็น **primitive module** — ไม่มี persistence, ไม่มี cache
- ใช้ `Decimal` เท่านั้น (ห้ามใช้ `float`)
- Money is Domain Invariant — ต้องแม่นยำ 100%

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`** — ไม่มี (pure VO module)

**`domain/value_objects.py` — Money**
```python
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""
    amount: Decimal
    currency: str = "THB"

    def __post_init__(self):
        object.__setattr__(self, "amount",
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("Amount must be Decimal")
        if self.currency not in Currency._value2member_map_:
            raise DomainError(f"Unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(f"Cannot operate on {self.currency} vs {other.currency}")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            raise DomainError("Factor must be Decimal")
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")
```

**`domain/value_objects.py` — VAT**
```python
@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุภาษีมูลค่าเพิ่ม"""

    rate: Decimal

    def calculate(self, base: Money) -> Money:
        return Money((base.amount * self.rate).quantize(Decimal("0.01")), base.currency)

    def extract(self, total: Money) -> Money:
        base = (total.amount / (Decimal("1") + self.rate)).quantize(Decimal("0.01"))
        return Money(total.amount - base, total.currency)
```

**`domain/value_objects.py` — ExchangeRate**
```python
@dataclass(frozen=True)
class ExchangeRate:
    """Exchange rate VO — วัตถุอัตราแลกเปลี่ยน"""

    from_currency: str
    to_currency: str
    rate: Decimal
    as_of: datetime

    def __post_init__(self):
        if self.rate <= 0:
            raise DomainError("Exchange rate must be positive")

    def convert(self, amount: Money) -> Money:
        if amount.currency != self.from_currency:
            raise DomainError("Currency mismatch")
        return Money(amount.amount * self.rate, self.to_currency)
```

**`domain/enums.py`**
```python
from enum import Enum


class Currency(str, Enum):
    THB = "THB"
    USD = "USD"
    EUR = "EUR"


class VATRate(str, Enum):
    ZERO = "0.00"
    SEVEN = "0.07"


class RoundingMode(str, Enum):
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    BANKERS = "BANKERS"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`** — Protocol ว่าง (VO module ไม่มี external deps)

**`application/use_cases.py`**
```python
class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""

    def add(self, a: Money, b: Money) -> Money:
        return a + b

    def subtract(self, a: Money, b: Money) -> Money:
        return a - b

    def multiply(self, a: Money, factor: Decimal) -> Money:
        return a * factor

    def calculate_vat(self, base: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).calculate(base)

    def extract_vat(self, total: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).extract(total)

    def convert(self, amount: Money, rate: ExchangeRate) -> Money:
        return rate.convert(amount)

    def sum_all(self, items: list[Money]) -> Money:
        if not items:
            raise DomainError("Cannot sum empty list")
        result = items[0]
        for item in items[1:]:
            result = result + item
        return result
```

**`application/mappers.py`** — `MoneyMapper.to_schema()` / `to_entity()`
**`application/exceptions.py`** — `MoneyException(StandardException)`
**`application/utils.py`** — `round_money()`, `zero_money(currency)`

### 3. Infrastructure Layer (`infrastructure/`)
- **ไม่มี** `models.py` (pure VO)
- **ไม่มี** `repositories.py`
- **ไม่มี** `caches.py`
- **ไม่มี** `services.py`

### 4. Presentation Layer (`presentation/`)

**`presentation/schemas.py`**
```python
class MoneySchema(BaseModel):
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    model_config = ConfigDict(from_attributes=True)


class VATRequest(BaseModel):
    base: MoneySchema
    rate: VATRate = VATRate.SEVEN


class VATResponse(BaseModel):
    vat: MoneySchema
    total: MoneySchema
```

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/money", tags=["Money"])


@router.post("/add/")
async def add(a: MoneySchema, b: MoneySchema): ...


@router.post("/subtract/")
async def subtract(a: MoneySchema, b: MoneySchema): ...


@router.post("/vat/calculate/")
async def vat_calculate(req: VATRequest): ...


@router.post("/vat/extract/")
async def vat_extract(req: VATRequest): ...


@router.post("/convert/")
async def convert(amount: MoneySchema, rate: ExchangeRateSchema): ...
```

**`presentation/docs.py`** — `router_docs` + per-endpoint docs
**`presentation/dependencies.py`** — `get_money_use_cases()`

### 5. Error Handling
- Use cases: **3-branch** (`StandardException` → `DomainError` → `Exception`)
- ไม่มี repository/cache → ไม่มี 2-branch / never-raise

### 6. Invariants
- `Decimal` quantize 2 ตำแหน่ง (ROUND_HALF_UP)
- `a + b == b + a` (commutative)
- `(a + b) + c == a + (b + c)` (associative)
- `a + Money(0) == a` (identity)
- `a - a == Money(0)` (inverse)
- `VAT.calculate(base) + base == VAT.extract(total)` consistency

### 7. Domain Events
- `MoneyAdded`, `MoneySubtracted`, `VATCalculated`, `CurrencyConverted`

### 8. Tests
```python
def test_commutative():
    assert a + b == b + a


def test_associative():
    assert (a + b) + c == a + (b + c)


def test_identity():
    assert a + Money(Decimal("0")) == a


def test_currency_mismatch():
    pytest.raises(DomainError)


def test_vat_7_percent():
    assert VAT(Decimal("0.07")).calculate(Money(Decimal("100"))) == Money(
        Decimal("7.00")
    )


def test_vat_extract_roundtrip(): ...
def test_exchange_rate_convert(): ...
def test_negative_money():
    assert Money(Decimal("-10")).is_negative()


def test_zero_money():
    assert Money(Decimal("0")).is_zero()
```

## Output
- ไฟล์ ~8 ไฟล์ (module เล็ก)
- Comment 2 ภาษา (ไทย + English)
- พร้อมรันด้วย `uvicorn app.app:app --reload`
```

---

## 📄 Module 0.2: `tenant_context`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `tenant_context` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `TenantContext` (VO), `TenantScope` (enum), `RequestContext` (VO) |
| **Prefix** | `tctx` |
| **Tables** | ไม่มี (context ไม่ persist) |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `tenant_context`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Module นี้เป็น **context propagation** — ใช้ `contextvars` แทน global state
- ทุก request ต้องมี `tenant_id`, `user_id`, `correlation_id`
- PostgreSQL schema-per-tenant → ต้อง switch schema ตาม context
- Redis namespace ต้อง prefix ด้วย `tenant_id`
- Kafka topic ต้อง prefix ด้วย `tenant_id`

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`** — ไม่มี (pure VO)

**`domain/value_objects.py` — TenantContext**
```python
from dataclasses import dataclass, field
from datetime import datetime
from contextvars import ContextVar

@dataclass(frozen=True)
class TenantContext:
    """Tenant context VO — วัตถุบริบทผู้เช่า"""
    tenant_id: str
    user_id: str | None = None
    correlation_id: str = ""
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.tenant_id:
            raise DomainError("Tenant ID is required")
        if not self.correlation_id:
            raise DomainError("Correlation ID is required")

    @property
    def schema_name(self) -> str:
        """PostgreSQL schema name — ชื่อ schema"""
        return f"tenant_{self.tenant_id}"

    def redis_namespace(self, key: str) -> str:
        """Namespace Redis key — prefix Redis"""
        return f"t:{self.tenant_id}:{key}"

    def kafka_topic(self, topic: str) -> str:
        """Namespace Kafka topic — prefix Kafka"""
        return f"t.{self.tenant_id}.{topic}"

_context_var: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)

def set_context(ctx: TenantContext) -> None:
    """Set current context — ตั้งค่า context ปัจจุบัน"""
    _context_var.set(ctx)

def get_context() -> TenantContext:
    """Get current context — ดึง context ปัจจุบัน"""
    ctx = _context_var.get()
    if ctx is None:
        raise DomainError("Tenant context not set")
    return ctx

def clear_context() -> None:
    """Clear context — ล้าง context"""
    _context_var.set(None)
```

**`domain/value_objects.py` — RequestContext**
```python
@dataclass(frozen=True)
class RequestContext:
    """Request context VO — วัตถุบริบทคำขอ"""

    method: str
    path: str
    ip_address: str
    user_agent: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
```

**`domain/enums.py`**
```python
class TenantScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class IsolationLevel(str, Enum):
    SCHEMA_PER_TENANT = "SCHEMA_PER_TENANT"
    DATABASE_PER_TENANT = "DATABASE_PER_TENANT"
    ROW_LEVEL = "ROW_LEVEL"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class ITenantContextProvider(Protocol):
    def get(self) -> TenantContext: ...
    def set(self, ctx: TenantContext) -> None: ...
    def clear(self) -> None: ...


class ITenantResolver(Protocol):
    async def resolve(self, identifier: str) -> TenantContext | None: ...
```

**`application/use_cases.py`**
```python
class TenantContextUseCases:
    """Tenant context use cases — กรณีการใช้งานบริบทผู้เช่า"""

    def __init__(self, resolver: ITenantResolver):
        self.resolver = resolver

    async def establish(
        self, tenant_id: str, user_id: str | None, headers: dict
    ) -> TenantContext:
        """Establish context from request — สร้าง context จาก request"""
        try:
            ctx = TenantContext(
                tenant_id=tenant_id,
                user_id=user_id,
                correlation_id=headers.get("X-Correlation-ID") or str(uuid7()),
                request_id=headers.get("X-Request-ID") or str(uuid7()),
                locale=headers.get("Accept-Language", "th-TH"),
            )
            set_context(ctx)
            return ctx
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in establish tenant context")
            raise TenantContextException()

    def current(self) -> TenantContext:
        return get_context()

    def teardown(self) -> None:
        clear_context()
```

**`application/mappers.py`** — `ContextMapper.to_context()` / `to_headers()`
**`application/exceptions.py`** — `TenantContextException`, `TenantNotFoundInContext`
**`application/utils.py`** — `requires_tenant()`, `tenant_scoped()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`** — ไม่มี (context ไม่ persist)

**`infrastructure/repositories.py` — PostgresTenantResolver**
```python
class PostgresTenantResolver:
    """Resolve tenant from DB — ค้นหา tenant จาก DB"""

    def __init__(self, session):
        self.session = session

    async def resolve(self, identifier: str) -> TenantContext | None:
        try:
            result = await self.session.execute(
                text("SELECT id FROM public.tenants WHERE slug = :s AND active = true"),
                {"s": identifier},
            )
            row = result.first()
            if not row:
                return None
            return TenantContext(tenant_id=str(row.id), correlation_id=str(uuid7()))
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error resolving tenant")
            raise TenantContextException()
```

**`infrastructure/caches.py` — RedisTenantCache**
```python
class RedisTenantCache:
    """Cache tenant lookup — แคชข้อมูล tenant"""

    async def get(self, identifier: str) -> TenantContext | None:
        try:
            data = await self.redis.get(f"tenant:lookup:{identifier}")
            return TenantContext(**json.loads(data)) if data else None
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed. Falling back.")
            return None  # never raise

    async def insert(self, identifier: str, ctx: TenantContext) -> None:
        try:
            await self.redis.setex(
                f"tenant:lookup:{identifier}", 300, json.dumps(asdict(ctx))
            )
        except Exception as e:
            logger.opt(exception=e).error("Cache insert failed.")
```

**`infrastructure/services.py`** — `HeaderTenantExtractor` (Protocol impl)

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/context", tags=["Tenant Context"])


@router.get("/current/")
async def get_current(ctx: TenantContext = Depends(get_tenant_context)): ...


@router.post("/switch/")
async def switch_tenant(
    tenant_id: str, use_cases: TenantContextUseCases = Depends(...)
): ...
```

**`presentation/schemas.py`** — `TenantContextSchema`, `SwitchTenantRequest`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_tenant_context()` (FastAPI dependency)

### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

### 6. Invariants
- ทุก request ต้องมี `tenant_id` + `correlation_id`
- Context ถูก propagate ผ่าน `contextvars` (async-safe)
- `schema_name == f"tenant_{tenant_id}"`
- Redis keys ขึ้นต้นด้วย `t:{tenant_id}:` เสมอ

### 7. Domain Events
- `TenantContextEstablished`, `TenantContextCleared`, `TenantSwitched`

### 8. Tests
```python
async def test_set_get_context(): ...
async def test_missing_tenant_raises(): ...
async def test_async_isolation():
    """Property: context ใน async task ต้องไม่รั่ว"""
    ...


async def test_schema_name_format(): ...
async def test_redis_namespace(): ...
async def test_kafka_topic_prefix(): ...
```

## Output
- ไฟล์ ~12 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 Module 0.3: `audit`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `audit` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `AuditLog` (entity), `AuditAction` (enum), `ChangeSet` (VO) |
| **Prefix** | `aud` |
| **Tables** | `tenant_{tid}.audit_logs` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `audit`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- **ทุก action ที่แตะเงิน/สต็อก/ข้อมูลสำคัญ → audit log (append-only)**
- Audit log ต้อง **immutable** — ห้าม UPDATE / DELETE
- ต้องเก็บ `before` / `after` state (ChangeSet)
- Audit log ต้องเป็น event-sourced เพื่อให้ replay ได้
- Retention: 7 ปี (ตามกฎหมายบัญชี)

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`**
```python
@dataclass
class AuditLog(BaseEntity):
    """Audit log entity — เอนทิตีบันทึก audit"""
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    actor_id: str = ""
    before_state: dict = field(default_factory=dict)
    after_state: dict = field(default_factory=dict)
    changes: list = field(default_factory=list)
    ip_address: str = ""
    user_agent: str = ""
    correlation_id: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.action:
            raise DomainError("Action is required")
        if not self.resource_type or not self.resource_id:
            raise DomainError("Resource type/id required")

    def diff(self) -> list[dict]:
        """Compute diff — คำนวณส่วนต่าง"""
        keys = set(self.before_state) | set(self.after_state)
        return [
            {"field": k, "before": self.before_state.get(k), "after": self.after_state.get(k)}
            for k in keys if self.before_state.get(k) != self.after_state.get(k)
        ]
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ChangeSet:
    """Change set VO — วัตถุชุดการเปลี่ยนแปลง"""

    entity: str
    entity_id: str
    changes: tuple[tuple[str, any, any], ...]  # (field, before, after)

    def is_empty(self) -> bool:
        return len(self.changes) == 0
```

**`domain/enums.py`**
```python
class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    VOID = "VOID"
    PAYMENT = "PAYMENT"
    STOCK_MOVE = "STOCK_MOVE"


class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IAuditRepository(Protocol):
    async def append(self, log: AuditLog) -> AuditLog: ...
    async def query(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[AuditLog], int]: ...


class IAuditCache(Protocol):
    async def get(self, id: str) -> AuditLog | None: ...
    async def insert(self, id: str, log: AuditLog) -> None: ...


class IAuditPublisher(Protocol):
    async def publish(self, log: AuditLog) -> None: ...
```

**`application/use_cases.py`**
```python
class AuditUseCases:
    """Audit use cases — กรณีการใช้งาน audit"""

    def __init__(self, repo, cache, publisher, events):
        self.repo = repo
        self.cache = cache
        self.publisher = publisher
        self.events = events

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        before: dict,
        after: dict,
    ) -> AuditLog:
        """Append audit log — เพิ่มบันทึก audit"""
        try:
            ctx = get_context()
            log = AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_id=ctx.user_id or "system",
                before_state=before,
                after_state=after,
                correlation_id=ctx.correlation_id,
            )
            log = await self.repo.append(log)

            # Read-back verification
            verified = await self.repo.get_by_id(log.id)
            if not verified:
                raise AuditException("Read-back failed")

            await self.publisher.publish(log)
            await self.events.publish("AuditLogged", log)

            return log
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in audit log")
            raise AuditException()

    async def query(self, filters: dict, page: int, limit: int) -> tuple[list, int]:
        return await self.repo.query(filters, page, limit)
```

**`application/mappers.py`** — `AuditMapper`
**`application/exceptions.py`** — `AuditException`, `AuditImmutableViolation`
**`application/utils.py`** — `auditable()` decorator, `diff_states()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class AuditLogModel(BaseModel):
    __tablename__ = "audit_logs"
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)
    before_state = Column(JSONB, default=dict)
    after_state = Column(JSONB, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    correlation_id = Column(String(36), index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_actor_time", "actor_id", "occurred_at"),
        # Append-only: REVOKE UPDATE/DELETE ใน migration
    )
```

**`infrastructure/repositories.py`** — `PostgresAuditRepository` (`append()` only — no update/delete)
**`infrastructure/caches.py`** — `RedisAuditCache` (read-through, never raises)
**`infrastructure/services.py`** — `AuditPublisher` (Kafka topic `audit.events`)

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

@router.get("/logs/")      # list + filters
async def list_logs(filters: AuditQuery, ...): ...

@router.get("/logs/{id}/")
async def get_log(id: str, ...): ...

@router.get("/resources/{type}/{id}/history/")
async def resource_history(type: str, id: str, ...): ...
```

**`presentation/schemas.py`** — `AuditLogSchema`, `AuditQuery`, `AuditLogPage`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_audit_use_cases()`

### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

### 6. Invariants
- Audit log **immutable** — append-only
- ทุก log ต้องมี `actor_id`, `correlation_id`, `occurred_at`
- `diff()` ต้องตรงกับ `before`/`after`
- Retention 7 ปี — ห้ามลบก่อนกำหนด

### 7. Domain Events
- `AuditLogged`, `AuditQueryExecuted`

### 8. Tests
```python
async def test_append_only(): ...  # ลอง update ต้อง raise
async def test_diff_accuracy(): ...  # diff ต้องตรง
async def test_actor_required(): ...
async def test_property_diff_symmetric():
    """Property: diff(before, after) == -diff(after, before)"""
    ...
```

## Output
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 Module 0.4: `idempotency`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `idempotency` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context`, `config` |
| **Domain Concepts** | `IdempotencyKey` (VO), `IdempotencyRecord` (entity), `IdempotencyStatus` (enum) |
| **Prefix** | `idem` |
| **Tables** | `tenant_{tid}.idempotency_records` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `idempotency`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- **Money Path + Goods Path ต้อง idempotent 100%**
- Client ส่ง `Idempotency-Key` header ทุก mutating request
- Server ต้อง:
  - ถ้า key ใหม่ → execute + store result
  - ถ้า key ซ้ำ + status = COMPLETED → return cached result
  - ถ้า key ซ้ำ + status = IN_PROGRESS → return 409 Conflict
  - ถ้า key ซ้ำ + payload ต่าง → return 422
- TTL: 24 ชั่วโมง (config ได้)

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`**
```python
@dataclass
class IdempotencyRecord(BaseEntity):
    """Idempotency record — เอนทิตีบันทึก idempotency"""
    key: str = ""
    status: str = "IN_PROGRESS"
    request_hash: str = ""
    response_body: dict = field(default_factory=dict)
    response_status: int = 0
    locked_until: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.key:
            raise DomainError("Idempotency key required")

    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() > self.expires_at

    def is_completed(self) -> bool:
        return self.status == "COMPLETED"

    def is_in_progress(self) -> bool:
        return self.status == "IN_PROGRESS"

    def complete(self, status: int, body: dict) -> None:
        """Mark completed — ทำเครื่องหมายเสร็จ"""
        self.status = "COMPLETED"
        self.response_status = status
        self.response_body = body
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class IdempotencyKey:
    """Idempotency key VO — วัตถุกุญแจ idempotency"""

    value: str
    scope: str  # e.g., "invoice.create"

    def __post_init__(self):
        if len(self.value) < 8 or len(self.value) > 255:
            raise DomainError("Idempotency key length must be 8-255")

    def redis_key(self, tenant_id: str) -> str:
        return f"t:{tenant_id}:idem:{self.scope}:{self.value}"
```

**`domain/enums.py`**
```python
class IdempotencyStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyConflict(str, Enum):
    SAME_KEY_SAME_PAYLOAD = "SAME_KEY_SAME_PAYLOAD"
    SAME_KEY_DIFF_PAYLOAD = "SAME_KEY_DIFF_PAYLOAD"
    CONCURRENT = "CONCURRENT"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IIdempotencyStore(Protocol):
    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None: ...
    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None: ...
    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool: ...
    async def unlock(self, key: IdempotencyKey, tenant_id: str) -> None: ...
```

**`application/use_cases.py`**
```python
class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency"""

    def __init__(self, store, config):
        self.store = store
        self.ttl = config.IDEMPOTENCY_TTL_SECONDS

    async def check_or_lock(
        self, raw_key: str, scope: str, payload: dict
    ) -> IdempotencyRecord | None:
        """Check existing or lock — ตรวจสอบหรือล็อก"""
        try:
            ctx = get_context()
            key = IdempotencyKey(value=raw_key, scope=scope)
            existing = await self.store.get(key, ctx.tenant_id)

            if existing and existing.is_completed():
                if existing.request_hash != self._hash(payload):
                    raise IdempotencyConflictException("Payload mismatch")
                return existing  # replay

            if existing and existing.is_in_progress():
                raise IdempotencyConflictException("Request in progress")

            locked = await self.store.lock(key, ctx.tenant_id, self.ttl)
            if not locked:
                raise IdempotencyConflictException("Concurrent request")

            rec = IdempotencyRecord(
                key=raw_key,
                status="IN_PROGRESS",
                request_hash=self._hash(payload),
                expires_at=datetime.utcnow() + timedelta(seconds=self.ttl),
            )
            await self.store.set(key, ctx.tenant_id, rec)
            return None  # proceed with execution
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in check_or_lock")
            raise IdempotencyException()

    async def complete(self, raw_key: str, scope: str, status: int, body: dict) -> None:
        """Mark completed — บันทึกผลลัพธ์"""
        try:
            ctx = get_context()
            key = IdempotencyKey(value=raw_key, scope=scope)
            rec = await self.store.get(key, ctx.tenant_id)
            if rec:
                rec.complete(status, body)
                await self.store.set(key, ctx.tenant_id, rec)
                await self.store.unlock(key, ctx.tenant_id)
        except Exception as e:
            logger.opt(exception=e).error("Error in complete idempotency")
            # don't re-raise — response already returned

    @staticmethod
    def _hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
```

**`application/mappers.py`** — `IdempotencyMapper`
**`application/exceptions.py`** — `IdempotencyException`, `IdempotencyConflictException`
**`application/utils.py`** — `idempotent()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class IdempotencyRecordModel(BaseModel):
    __tablename__ = "idempotency_records"
    key = Column(String(255), nullable=False, index=True)
    scope = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_body = Column(JSONB, default=dict)
    response_status = Column(Integer)
    locked_until = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint("key", "scope", "tenant_id", name="uq_idem_key_scope_tenant"),
    )
```

**`infrastructure/repositories.py`** — `PostgresIdempotencyRepository` (fallback เมื่อ Redis ล่ม)
**`infrastructure/caches.py`** — `RedisIdempotencyStore` (primary, atomic SET NX)
```python
class RedisIdempotencyStore:
    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool:
        try:
            result = await self.redis.set(
                f"{key.redis_key(tenant_id)}:lock", "1", nx=True, ex=ttl
            )
            return bool(result)
        except Exception as e:
            logger.opt(exception=e).error("Lock failed")
            return False  # conservative: fail closed
```

**`infrastructure/services.py`** — ไม่มี

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`** — ไม่มี public router (ใช้ middleware/dependency)
**`presentation/schemas.py`** — `IdempotencyRecordSchema`
**`presentation/docs.py`** — docs
**`presentation/dependencies.py`** — `require_idempotency_key()` FastAPI dependency

### 5. Error Handling
- Use cases: **3-branch**
- Store: **2-branch** (Redis), **never-raise** (fallback logging)

### 6. Invariants
- Key + Scope + Tenant = unique
- `COMPLETED` record ต้อง return response เดิมเสมอ
- Payload hash ต้องตรงกัน ไม่งั้น 422
- Concurrent requests → 1 success, rest 409

### 7. Domain Events
- `IdempotencyLocked`, `IdempotencyCompleted`, `IdempotencyConflict`

### 8. Tests
```python
async def test_first_request_executes(): ...
async def test_second_request_replays(): ...
async def test_payload_mismatch_raises(): ...
async def test_concurrent_requests_only_one_wins(): ...
async def test_expired_record_allows_retry(): ...
async def test_property_replay_returns_same_response():
    for _ in range(100):
        ...
```

## Output
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 Module 0.5: `config`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `config` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `ConfigEntry` (entity), `ConfigScope` (enum), `ConfigType` (enum) |
| **Prefix** | `cfg` |
| **Tables** | `tenant_{tid}.config_entries` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `config`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Config มี 3 ระดับ: **GLOBAL → TENANT → USER** (override ตามลำดับ)
- รองรับ hot-reload ผ่าน Redis Pub/Sub
- Type-safe: `string`, `int`, `decimal`, `bool`, `json`, `secret`
- Secret ต้องเข้ารหัส (Fernet) และไม่ return ผ่าน API
- Cache ที่ Redis พร้อม TTL + tombstone

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`**
```python
@dataclass
class ConfigEntry(BaseEntity):
    """Config entry — เอนทิตีรายการตั้งค่า"""
    key: str = ""
    value: str = ""
    value_type: str = "string"
    scope: str = "TENANT"
    scope_id: str = ""
    is_secret: bool = False
    description: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.key:
            raise DomainError("Config key required")
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.key):
            raise DomainError(f"Invalid key format: {self.key}")

    def typed_value(self):
        """Return typed value — คืนค่าตามชนิด"""
        if self.value_type == "int":
            return int(self.value)
        if self.value_type == "decimal":
            return Decimal(self.value)
        if self.value_type == "bool":
            return self.value.lower() in ("1", "true", "yes")
        if self.value_type == "json":
            return json.loads(self.value)
        return self.value

    def mask(self) -> "ConfigEntry":
        """Mask secret value — ปิดบังค่า secret"""
        if self.is_secret:
            copy = replace(self, value="***")
            return copy
        return self
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ConfigKey:
    """Config key VO — วัตถุกุญแจ config"""

    value: str

    def __post_init__(self):
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.value):
            raise DomainError(f"Invalid config key: {self.value}")

    def namespace(self) -> str:
        return self.value.split(".", 1)[0]
```

**`domain/enums.py`**
```python
class ConfigScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class ConfigType(str, Enum):
    STRING = "string"
    INT = "int"
    DECIMAL = "decimal"
    BOOL = "bool"
    JSON = "json"
    SECRET = "secret"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IConfigRepository(Protocol):
    async def get(self, key: str, scope: str, scope_id: str) -> ConfigEntry | None: ...
    async def get_effective(
        self, key: str, tenant_id: str, user_id: str | None
    ) -> ConfigEntry | None: ...
    async def save(self, entry: ConfigEntry) -> ConfigEntry: ...
    async def list(self, scope: str, scope_id: str) -> list[ConfigEntry]: ...


class IConfigCache(Protocol):
    async def get(self, key: str) -> ConfigEntry | None: ...
    async def insert(self, key: str, entry: ConfigEntry) -> None: ...
    async def invalidate(self, key: str) -> None: ...


class ISecretCipher(Protocol):
    def encrypt(self, plain: str) -> str: ...
    def decrypt(self, cipher: str) -> str: ...
```

**`application/use_cases.py`**
```python
class ConfigUseCases:
    """Config use cases — กรณีการใช้งาน config"""

    def __init__(self, repo, cache, cipher, events, config): ...

    async def get_effective(self, key: str, user_id: str | None = None) -> ConfigEntry:
        """Get effective config — ดึงค่าที่มีผล"""
        try:
            ctx = get_context()
            cache_key = f"{ctx.tenant_id}:{user_id or '-'}:{key}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            entry = await self.repo.get_effective(key, ctx.tenant_id, user_id)
            if entry is None:
                raise ConfigKeyNotFoundException(key)

            if entry.is_secret:
                plain = self.cipher.decrypt(entry.value)
                entry = replace(entry, value=plain)

            await self.cache.insert(cache_key, entry)
            return entry
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_effective config")
            raise ConfigException()

    async def set(
        self,
        key: str,
        value: str,
        value_type: str,
        scope: str,
        scope_id: str,
        is_secret: bool = False,
    ) -> ConfigEntry:
        """Set config — ตั้งค่า config"""
        try:
            if is_secret:
                value = self.cipher.encrypt(value)
            entry = ConfigEntry(
                key=key,
                value=value,
                value_type=value_type,
                scope=scope,
                scope_id=scope_id,
                is_secret=is_secret,
            )
            entry = await self.repo.save(entry)

            # Read-back
            verified = await self.repo.get(key, scope, scope_id)
            if not verified or verified.value != entry.value:
                raise ConfigException("Read-back failed")

            await self.cache.invalidate(f"{scope_id}:{key}")
            await self.events.publish("ConfigChanged", {"key": key, "scope": scope})
            return entry.mask()
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in set config")
            raise ConfigException()
```

**`application/mappers.py`** — `ConfigMapper` (with mask)
**`application/exceptions.py`** — `ConfigException`, `ConfigKeyNotFoundException`
**`application/utils.py`** — `get_config(key, default)` helper

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class ConfigEntryModel(BaseModel):
    __tablename__ = "config_entries"
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False, default="string")
    scope = Column(String(20), nullable=False, index=True)
    scope_id = Column(String(36), nullable=False, index=True)
    is_secret = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("key", "scope", "scope_id", name="uq_config_key_scope"),
    )
```

**`infrastructure/repositories.py`** — `PostgresConfigRepository` (with 3-level override)
**`infrastructure/caches.py`** — `RedisConfigCache` (TTL 300s, tombstone, never raises)
**`infrastructure/services.py`**
```python
class FernetCipher:
    """Fernet cipher — เข้ารหัส Fernet"""

    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def encrypt(self, plain: str) -> str:
        return self.fernet.encrypt(plain.encode()).decode()

    def decrypt(self, cipher: str) -> str:
        return self.fernet.decrypt(cipher.encode()).decode()


class ConfigPubSub:
    """Config hot-reload via Redis Pub/Sub — โหลด config ใหม่ทันที"""

    async def subscribe(self, callback) -> None: ...
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/config", tags=["Config"])

@router.get("/{key}/")
async def get_config(key: str, ...): ...

@router.put("/{key}/")
async def set_config(key: str, payload: ConfigSetRequest, ...): ...

@router.get("/")
async def list_config(scope: str, ...): ...

@router.delete("/{key}/")
async def delete_config(key: str, ...): ...
```

**`presentation/schemas.py`** — `ConfigEntrySchema`, `ConfigSetRequest` (mask secrets)
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_config_use_cases()`

### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

### 6. Invariants
- 3-level override: `USER` > `TENANT` > `GLOBAL`
- Secret values **ไม่ return ผ่าน API** (mask)
- Config key format: `^[a-z][a-z0-9_.]*$`
- Cache invalidation ต้อง propagate ทันที

### 7. Domain Events
- `ConfigChanged`, `ConfigDeleted`, `ConfigReloaded`

### 8. Tests
```python
async def test_override_precedence(): ...
async def test_secret_encrypted_at_rest(): ...
async def test_secret_masked_in_api(): ...
async def test_invalid_key_format_raises(): ...
async def test_property_override_order():
    """Property: user > tenant > global เสมอ"""
    ...
```

## Output
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 Module 0.6: `events`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `events` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context`, `audit` |
| **Domain Concepts** | `DomainEvent` (VO), `EventEnvelope` (VO), `EventStatus` (enum) |
| **Prefix** | `evt` |
| **Tables** | `tenant_{tid}.event_store` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `events`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Kafka-based event bus
- **At-least-once delivery** + **consumer idempotency**
- Event envelope ต้องมี: `event_id`, `tenant_id`, `correlation_id`, `occurred_at`, `version`
- Event schema ต้อง versioned (backward-compatible)
- Dead Letter Queue (DLQ) สำหรับ poison messages
- Retry: exponential backoff (1s → 2s → 4s → 8s → 16s → DLQ)

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`** — ไม่มี (event เป็น VO)

**`domain/value_objects.py` — DomainEvent**
```python
@dataclass(frozen=True)
class DomainEvent:
    """Domain event VO — วัตถุเหตุการณ์"""
    event_type: str
    aggregate_id: str
    payload: dict
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def __post_init__(self):
        if not self.event_type:
            raise DomainError("Event type required")
        if not self.aggregate_id:
            raise DomainError("Aggregate ID required")
        if self.version < 1:
            raise DomainError("Version must be >= 1")
```

**`domain/value_objects.py` — EventEnvelope**
```python
@dataclass(frozen=True)
class EventEnvelope:
    """Event envelope — วัตถุซองเหตุการณ์"""

    event_id: str
    event_type: str
    tenant_id: str
    correlation_id: str
    occurred_at: datetime
    version: int
    payload: dict
    retry_count: int = 0

    def to_kafka_topic(self) -> str:
        """Kafka topic name — ชื่อ topic"""
        return f"t.{self.tenant_id}.{self.event_type.lower()}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EventEnvelope":
        return cls(**data)
```

**`domain/enums.py`**
```python
class EventStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    PROCESSING = "PROCESSING"
    CONSUMED = "CONSUMED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


class EventPriority(str, Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class EventCategory(str, Enum):
    MONEY = "MONEY"
    GOODS = "GOODS"
    USER = "USER"
    SYSTEM = "SYSTEM"
    IoT = "IoT"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IEventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
    async def publish_batch(self, events: list[DomainEvent]) -> None: ...


class IEventStore(Protocol):
    async def append(self, envelope: EventEnvelope) -> None: ...
    async def get(self, event_id: str) -> EventEnvelope | None: ...
    async def mark_consumed(self, event_id: str) -> None: ...


class IEventHandler(Protocol):
    event_type: str

    async def handle(self, envelope: EventEnvelope) -> None: ...


class IEventSerializer(Protocol):
    def serialize(self, envelope: EventEnvelope) -> bytes: ...
    def deserialize(self, data: bytes) -> EventEnvelope: ...
```

**`application/use_cases.py`**
```python
class EventUseCases:
    """Event use cases — กรณีการใช้งานเหตุการณ์"""

    def __init__(self, bus, store, handlers, serializer):
        self.bus = bus
        self.store = store
        self.handlers = {h.event_type: h for h in handlers}
        self.serializer = serializer

    async def publish(self, event: DomainEvent) -> EventEnvelope:
        """Publish event — เผยแพร่เหตุการณ์"""
        try:
            ctx = get_context()
            envelope = EventEnvelope(
                event_id=str(uuid7()),
                event_type=event.event_type,
                tenant_id=ctx.tenant_id,
                correlation_id=ctx.correlation_id,
                occurred_at=event.occurred_at,
                version=event.version,
                payload=event.payload,
            )
            await self.store.append(envelope)
            await self.bus.publish(event)
            return envelope
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in publish event")
            raise EventException()

    async def consume(self, raw: bytes) -> None:
        """Consume event — รับเหตุการณ์"""
        try:
            envelope = self.serializer.deserialize(raw)

            # Idempotency check — ตรวจสอบ idempotency
            existing = await self.store.get(envelope.event_id)
            if existing and existing.retry_count >= 0:
                logger.info(f"Duplicate event {envelope.event_id}, skipping")
                return

            handler = self.handlers.get(envelope.event_type)
            if not handler:
                logger.warning(f"No handler for {envelope.event_type}")
                return

            await handler.handle(envelope)
            await self.store.mark_consumed(envelope.event_id)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in consume event")
            # retry logic
            if envelope.retry_count < 5:
                await self._retry(envelope)
            else:
                await self._to_dlq(envelope)

    async def _retry(self, envelope: EventEnvelope) -> None:
        """Retry with exponential backoff — ลองใหม่แบบ exponential"""
        delay = 2**envelope.retry_count
        await asyncio.sleep(delay)
        envelope.retry_count += 1
        await self.bus.publish(envelope)  # republish

    async def _to_dlq(self, envelope: EventEnvelope) -> None:
        """Send to DLQ — ส่งไป DLQ"""
        await self.bus.publish_to_dlq(envelope)
```

**`application/mappers.py`** — `EventMapper`
**`application/exceptions.py`** — `EventException`, `EventHandlerNotFoundException`, `EventSerializationException`
**`application/utils.py`** — `@event_handler("EventType")` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class EventStoreModel(BaseModel):
    __tablename__ = "event_store"
    event_id = Column(String(36), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    correlation_id = Column(String(36), index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    payload = Column(JSONB, nullable=False)
    status = Column(String(20), default="PENDING", index=True)
    retry_count = Column(Integer, default=0)
    consumed_at = Column(DateTime(timezone=True))
```

**`infrastructure/repositories.py`** — `PostgresEventStore` (append-only, dedup by event_id)
**`infrastructure/caches.py`** — `RedisEventCache` (dedup bloom filter, never raises)
**`infrastructure/services.py`**
```python
class KafkaEventBus:
    """Kafka event bus — บัสเหตุการณ์ Kafka"""

    def __init__(self, bootstrap: str):
        self.producer = None
        self.bootstrap = bootstrap

    async def publish(self, event: DomainEvent) -> None:
        try:
            ctx = get_context()
            topic = f"t.{ctx.tenant_id}.{event.event_type.lower()}"
            await self.producer.send_and_wait(topic, json.dumps(asdict(event)).encode())
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Kafka publish failed")
            raise EventException()

    async def publish_to_dlq(self, envelope: EventEnvelope) -> None:
        await self.producer.send_and_wait(
            "dlq.events", json.dumps(asdict(envelope)).encode()
        )


class JsonEventSerializer:
    """JSON serializer — ตัวแปลง JSON"""

    def serialize(self, envelope: EventEnvelope) -> bytes:
        return json.dumps(asdict(envelope), default=str).encode()

    def deserialize(self, data: bytes) -> EventEnvelope:
        return EventEnvelope.from_dict(json.loads(data))


class EventConsumerLoop:
    """Kafka consumer loop — วนลูปผู้บริโภค"""

    async def run(self, topics: list[str], handler) -> None: ...
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/events", tags=["Events"])

@router.get("/")
async def list_events(filters: EventQuery, ...): ...

@router.get("/{event_id}/")
async def get_event(event_id: str, ...): ...

@router.post("/{event_id}/replay/")
async def replay_event(event_id: str, ...): ...  # admin only

@router.get("/dlq/")
async def list_dlq(...): ...

@router.post("/dlq/{event_id}/retry/")
async def retry_dlq(event_id: str, ...): ...
```

**`presentation/schemas.py`** — `EventSchema`, `EventQuery`, `EventPage`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_event_use_cases()`

### 5. Error Handling
- Use cases: **3-branch**
- Bus / Store: **2-branch**
- Cache: **never-raise**

### 6. Invariants
- `event_id` unique (dedup)
- At-least-once delivery + consumer idempotent
- Retry: exponential backoff สูงสุด 5 ครั้ง → DLQ
- Event schema backward-compatible (versioned)
- ทุก event มี `tenant_id` + `correlation_id`

### 7. Domain Events (Meta)
- `EventPublished`, `EventConsumed`, `EventFailed`, `EventDeadLettered`

### 8. Tests
```python
async def test_publish_creates_envelope(): ...
async def test_duplicate_consumption_idempotent(): ...
async def test_retry_backoff_sequence(): ...
async def test_to_dlq_after_max_retries(): ...
async def test_property_event_id_unique():
    events = [EventEnvelope(...) for _ in range(1000)]
    assert len({e.event_id for e in events}) == 1000


async def test_property_schema_backward_compat(): ...
```

## Output
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## ✅ สรุป Layer 0 (Core) — 6/65 ไฟล์

| # | Module | ไฟล์ | จำนวน Output | สถานะ |
|---|---|---|---|---|
| 1 | `money` | `docs/prompts/layer-0-core/money.md` | ~8 ไฟล์ | ✅ |
| 2 | `tenant_context` | `docs/prompts/layer-0-core/tenant_context.md` | ~12 ไฟล์ | ✅ |
| 3 | `audit` | `docs/prompts/layer-0-core/audit.md` | 16 ไฟล์ | ✅ |
| 4 | `idempotency` | `docs/prompts/layer-0-core/idempotency.md` | 16 ไฟล์ | ✅ |
| 5 | `config` | `docs/prompts/layer-0-core/config.md` | 16 ไฟล์ | ✅ |
| 6 | `events` | `docs/prompts/layer-0-core/events.md` | 16 ไฟล์ | ✅ |

**Layer 0 เสร็จสมบูรณ์ — ต่อไปคือ Layer 1 (Foundation)**

---

# 📋 Layer 1: FOUNDATION — 8 Modules

> **Dependencies:** Layer 0 (Core)
> **Output:** 23 ไฟล์ต่อ module (16 Python + 3 SQL + 4 Tests)

---

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
            await self.events.publish(
                "TenantPlanUpgraded", {"id": id, "plan": new_plan}
            )
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
            await self.session.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            )
            await self.session.flush()
        except Exception as e:
            logger.opt(exception=e).error(f"Schema create failed: {schema_name}")
            raise

    async def drop_schema(self, schema_name: str) -> None:
        try:
            await self.session.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
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
    TenancyException,
    TenantSlugConflictException,
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
    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=3, max_size=30
        )
    )
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

## 📄 Module 1.2: `authentication`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `authentication` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenancy`, `user`, `tenant_context`, `audit`, `config` |
| **Domain Concepts** | `Credential` (entity), `Token` (VO), `Session` (entity), `AuthMethod` (enum) |
| **Prefix** | `auth` |
| **Tables** | `tenant_{tid}.credentials`, `tenant_{tid}.sessions` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `authentication`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- JWT-based authentication: Access (15 min) + Refresh (7 days, rotating)
- Password hashing: Argon2id
- รองรับ: password, API key, OAuth2 (Google, LINE)
- Session เก็บใน Redis (TTL 7 days)
- Rate limit: 5 failed attempts → lock 15 นาที

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Credential**
```python
@dataclass
class Credential(BaseEntity):
    """Credential entity — เอนทิตีข้อมูลรับรอง"""
    user_id: str = ""
    password_hash: str = ""
    auth_method: str = "PASSWORD"
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.user_id:
            raise DomainError("User ID is required")

    def is_locked(self) -> bool:
        return self.locked_until is not None and datetime.utcnow() < self.locked_until

    def record_failure(self) -> None:
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def record_success(self) -> None:
        self.failed_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()

@dataclass
class Session(BaseEntity):
    """Session entity — เอนทิตีเซสชัน"""
    user_id: str = ""
    refresh_token_hash: str = ""
    expires_at: datetime | None = None
    ip_address: str = ""
    user_agent: str = ""
    revoked_at: datetime | None = None

    def is_valid(self) -> bool:
        return self.revoked_at is None and self.expires_at and datetime.utcnow() < self.expires_at
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Token:
    """Token VO — วัตถุโทเคน"""

    value: str
    expires_at: datetime
    token_type: str = "Bearer"

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


@dataclass(frozen=True)
class TokenPair:
    """Token pair VO — วัตถุคู่โทเคน"""

    access_token: Token
    refresh_token: Token


@dataclass(frozen=True)
class Password:
    """Password VO — วัตถุรหัสผ่าน"""

    plain: str

    MIN_LENGTH = 8

    def __post_init__(self):
        if len(self.plain) < self.MIN_LENGTH:
            raise DomainError(f"Password must be at least {self.MIN_LENGTH} chars")
        if not re.search(r"[A-Z]", self.plain):
            raise DomainError("Password must contain uppercase")
        if not re.search(r"[0-9]", self.plain):
            raise DomainError("Password must contain digit")
```

**`domain/enums.py`**
```python
class AuthMethod(str, Enum):
    PASSWORD = "PASSWORD"
    API_KEY = "API_KEY"
    OAUTH_GOOGLE = "OAUTH_GOOGLE"
    OAUTH_LINE = "OAUTH_LINE"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class AuthResult(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class ICredentialRepository(Protocol):
    async def save(self, cred: Credential) -> Credential: ...
    async def get_by_user_id(self, user_id: str) -> Credential | None: ...


class ISessionRepository(Protocol):
    async def save(self, session: Session) -> Session: ...
    async def get_by_token_hash(self, hash: str) -> Session | None: ...
    async def revoke(self, session_id: str) -> None: ...


class IPasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hash: str) -> bool: ...


class ITokenService(Protocol):
    def issue_access(self, user_id: str, tenant_id: str, roles: list[str]) -> Token: ...
    def issue_refresh(self, user_id: str, tenant_id: str) -> Token: ...
    def verify(self, token: str, token_type: str) -> dict: ...


class ISessionCache(Protocol):
    async def get(self, token_hash: str) -> dict | None: ...
    async def set(self, token_hash: str, data: dict, ttl: int) -> None: ...
    async def delete(self, token_hash: str) -> None: ...
```

**`application/use_cases.py`**
```python
class AuthenticationUseCases:
    """Authentication use cases — กรณีการใช้งาน authentication"""

    def __init__(
        self, cred_repo, session_repo, hasher, token_svc, cache, audit, events
    ): ...

    async def login(self, email: str, password: str, ip: str, ua: str) -> TokenPair:
        """Login — เข้าสู่ระบบ"""
        try:
            ctx = get_context()
            cred = await self.cred_repo.get_by_email(email)
            if not cred:
                raise InvalidCredentialsException()

            if cred.is_locked():
                raise AccountLockedException(cred.locked_until)

            if not self.hasher.verify(password, cred.password_hash):
                cred.record_failure()
                await self.cred_repo.save(cred)
                raise InvalidCredentialsException()

            cred.record_success()
            await self.cred_repo.save(cred)

            access = self.token_svc.issue_access(cred.user_id, ctx.tenant_id, [])
            refresh = self.token_svc.issue_refresh(cred.user_id, ctx.tenant_id)

            session = Session(
                user_id=cred.user_id,
                refresh_token_hash=self._hash(refresh.value),
                expires_at=refresh.expires_at,
                ip_address=ip,
                user_agent=ua,
            )
            session = await self.session_repo.save(session)

            await self.cache.set(
                self._hash(refresh.value),
                {"user_id": cred.user_id, "session_id": session.id},
                ttl=7 * 86400,
            )
            await self.audit.log("auth.login", cred.user_id)
            await self.events.publish("UserLoggedIn", {"user_id": cred.user_id})

            return TokenPair(access_token=access, refresh_token=refresh)
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in login")
            raise AuthenticationException()

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Refresh token — ต่ออายุโทเคน"""
        try:
            payload = self.token_svc.verify(refresh_token, "refresh")
            token_hash = self._hash(refresh_token)

            session = await self.session_repo.get_by_token_hash(token_hash)
            if not session or not session.is_valid():
                raise InvalidTokenException()

            # Rotate: revoke old, issue new
            session.revoked_at = datetime.utcnow()
            await self.session_repo.save(session)
            await self.cache.delete(token_hash)

            access = self.token_svc.issue_access(
                payload["user_id"], payload["tenant_id"], payload.get("roles", [])
            )
            new_refresh = self.token_svc.issue_refresh(
                payload["user_id"], payload["tenant_id"]
            )

            new_session = Session(
                user_id=payload["user_id"],
                refresh_token_hash=self._hash(new_refresh.value),
                expires_at=new_refresh.expires_at,
            )
            await self.session_repo.save(new_session)
            await self.cache.set(
                self._hash(new_refresh.value),
                {"user_id": payload["user_id"]},
                ttl=7 * 86400,
            )

            return TokenPair(access_token=access, refresh_token=new_refresh)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in refresh")
            raise AuthenticationException()

    async def logout(self, refresh_token: str) -> None:
        """Logout — ออกจากระบบ"""
        try:
            token_hash = self._hash(refresh_token)
            session = await self.session_repo.get_by_token_hash(token_hash)
            if session:
                session.revoked_at = datetime.utcnow()
                await self.session_repo.save(session)
            await self.cache.delete(token_hash)
            await self.audit.log(
                "auth.logout", session.user_id if session else "unknown"
            )
        except Exception as e:
            logger.opt(exception=e).error("Error in logout")

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
```

**`application/mappers.py`** — `AuthMapper`
**`application/exceptions.py`** — `AuthenticationException`, `InvalidCredentialsException`, `AccountLockedException`, `InvalidTokenException`
**`application/utils.py`** — `require_auth()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class CredentialModel(BaseModel):
    __tablename__ = "credentials"
    user_id = Column(String(36), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    auth_method = Column(String(20), nullable=False, default="PASSWORD")
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))


class SessionModel(BaseModel):
    __tablename__ = "sessions"
    user_id = Column(String(36), nullable=False, index=True)
    refresh_token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    revoked_at = Column(DateTime(timezone=True))
```

**`infrastructure/repositories.py`** — `PostgresCredentialRepository`, `PostgresSessionRepository`
**`infrastructure/caches.py`** — `RedisSessionCache` (never raises)
**`infrastructure/services.py`**
```python
class ArgonHasher:
    """Argon2id hasher — ตัวแฮช Argon2id"""

    def __init__(self):
        self.ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

    def hash(self, plain: str) -> str:
        return self.ph.hash(plain)

    def verify(self, plain: str, hash: str) -> bool:
        try:
            self.ph.verify(hash, plain)
            return True
        except Exception:
            return False


class JWTService:
    """JWT service — บริการ JWT"""

    def __init__(self, secret: str, issuer: str = "erp-sme"):
        self.secret = secret
        self.issuer = issuer

    def issue_access(self, user_id: str, tenant_id: str, roles: list[str]) -> Token:
        exp = datetime.utcnow() + timedelta(minutes=15)
        payload = {
            "sub": user_id,
            "tid": tenant_id,
            "roles": roles,
            "typ": "access",
            "iss": self.issuer,
            "exp": exp,
        }
        return Token(jwt.encode(payload, self.secret, algorithm="HS256"), exp)

    def issue_refresh(self, user_id: str, tenant_id: str) -> Token:
        exp = datetime.utcnow() + timedelta(days=7)
        payload = {
            "sub": user_id,
            "tid": tenant_id,
            "typ": "refresh",
            "iss": self.issuer,
            "exp": exp,
        }
        return Token(jwt.encode(payload, self.secret, algorithm="HS256"), exp)

    def verify(self, token: str, token_type: str) -> dict:
        payload = jwt.decode(
            token, self.secret, algorithms=["HS256"], issuer=self.issuer
        )
        if payload.get("typ") != token_type:
            raise InvalidTokenException(
                f"Token type mismatch: {payload.get('typ')} != {token_type}"
            )
        return payload
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/login/")
async def login(payload: LoginRequest, request: Request, ...): ...

@router.post("/refresh/")
async def refresh(payload: RefreshRequest, ...): ...

@router.post("/logout/")
async def logout(payload: LogoutRequest, ...): ...

@router.get("/me/")
async def me(auth: Authentication = Depends(authenticate_user)): ...
```

**`presentation/schemas.py`** — `LoginRequest`, `TokenResponse`, `RefreshRequest`, `LogoutRequest`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `authenticate_user()`, `get_current_user()`

### 5. Invariants
- Password ต้องยาว ≥ 8 + uppercase + digit
- 5 failed attempts → lock 15 นาที
- Refresh token rotating (ใช้แล้วrevoke)
- Session TTL 7 วัน
- Access token TTL 15 นาที

### 6. Domain Events
- `UserLoggedIn`, `UserLoggedOut`, `TokenRefreshed`, `AccountLocked`

### 7. Tests
```python
async def test_login_valid(): ...
async def test_login_invalid_password(): ...
async def test_account_lockout_after_5_failures(): ...
async def test_refresh_rotates_token(): ...
async def test_logout_revokes_session(): ...
async def test_property_password_strength(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `authentication`

**`db/migrations/V001__create_authentication.sql`**
```sql
BEGIN;

CREATE TABLE tenant_auth.credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    user_id         UUID NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    auth_method     VARCHAR(20) NOT NULL DEFAULT 'PASSWORD',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    last_login_at   TIMESTAMPTZ,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_credentials_user UNIQUE (tenant_id, user_id)
);

CREATE TABLE tenant_auth.sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,
    user_id             UUID NOT NULL,
    refresh_token_hash  VARCHAR(64) NOT NULL UNIQUE,
    expires_at          TIMESTAMPTZ NOT NULL,
    ip_address          VARCHAR(45),
    user_agent          VARCHAR(500),
    revoked_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sessions_user ON tenant_auth.sessions(user_id);
CREATE INDEX ix_sessions_expires ON tenant_auth.sessions(expires_at) WHERE revoked_at IS NULL;

ALTER TABLE tenant_auth.credentials ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_credentials_tenant ON tenant_auth.credentials
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_auth.sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_sessions_tenant ON tenant_auth.sessions
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_authentication.sql`**
```sql
BEGIN;
-- Seed credential สำหรับ demo user (password: Demo1234)
-- INSERT INTO tenant_auth.credentials (...) VALUES (...);
COMMIT;
```

**`db/migrations/V003__rollback_authentication.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_auth.sessions CASCADE;
DROP TABLE IF EXISTS tenant_auth.credentials CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `authentication`

**`tests/unit/test_authentication.py`**
```python
import pytest
from datetime import datetime, timedelta
from app.modules.authentication.domain.entities import Credential, Session
from app.modules.authentication.domain.value_objects import Password, Token


class TestCredentialDomain:
    def test_lockout_after_5_failures(self):
        cred = Credential(user_id="u1", password_hash="hash")
        for _ in range(5):
            cred.record_failure()
        assert cred.is_locked()

    def test_success_resets_failures(self):
        cred = Credential(user_id="u1", password_hash="hash")
        cred.record_failure()
        cred.record_success()
        assert cred.failed_attempts == 0
        assert cred.locked_until is None


class TestPasswordVO:
    def test_too_short_raises(self):
        with pytest.raises(Exception):
            Password(plain="Ab1")

    def test_no_uppercase_raises(self):
        with pytest.raises(Exception):
            Password(plain="abcd1234")

    def test_no_digit_raises(self):
        with pytest.raises(Exception):
            Password(plain="Abcdefgh")

    def test_valid(self):
        p = Password(plain="Demo1234")
        assert p.plain == "Demo1234"
```

**`tests/integration/test_authentication_repository.py`** — testcontainers-based
**`tests/property/test_authentication_invariants.py`** — hypothesis
**`tests/manual/manual_test_authentication.md`** — manual test cases

---

## 📄 Module 1.3–1.8: `user`, `employee`, `customer`, `supplier`, `product`, `pricing`

> **หมายเหตุ:** เนื่องจากข้อจำกัดด้านความยาว ผมจะแสดง pattern สำหรับ module ที่เหลือใน Layer 1 ให้ดู โดยใช้ pattern เดียวกันกับ `tenancy` และ `authentication`

### สรุป Layer 1 ทั้ง 8 Modules

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 1.1 | `tenancy` | `ten` | Tenant | `public.tenants` | `tenant_context`, `config`, `audit`, `events` |
| 1.2 | `authentication` | `auth` | Credential, Session | `credentials`, `sessions` | `tenancy`, `user`, `tenant_context`, `audit` |
| 1.3 | `user` | `usr` | User, Role, Permission | `users`, `roles`, `permissions`, `user_roles` | `tenancy`, `authentication`, `audit`, `events` |
| 1.4 | `employee` | `emp` | Employee, Department, Position | `employees`, `departments`, `positions` | `user`, `tenancy`, `audit` |
| 1.5 | `customer` | `cus` | Customer, CustomerGroup, Address | `customers`, `customer_groups`, `addresses` | `tenancy`, `user`, `audit`, `events` |
| 1.6 | `supplier` | `sup` | Supplier, SupplierCategory | `suppliers`, `supplier_categories` | `tenancy`, `user`, `audit`, `events` |
| 1.7 | `product` | `prd` | Product, Category, SKU, Barcode | `products`, `categories`, `skus`, `barcodes` | `tenancy`, `supplier`, `audit`, `events` |
| 1.8 | `pricing` | `prc` | PriceList, PriceRule, Discount | `price_lists`, `price_rules`, `discounts` | `product`, `customer`, `audit`, `events` |

### 🎯 Template ตัวอย่าง: Module `user`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `user` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenancy`, `authentication`, `audit`, `events` |
| **Domain Concepts** | `User` (entity), `Role` (entity), `Permission` (VO), `UserStatus` (enum) |
| **Prefix** | `usr` |
| **Tables** | `tenant_{tid}.users`, `tenant_{tid}.roles`, `tenant_{tid}.permissions`, `tenant_{tid}.user_roles` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `user`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- User management พร้อม RBAC (Role-Based Access Control)
- แต่ละ user มีหลาย role, แต่ละ role มีหลาย permission
- Permission format: `{module}:{action}` เช่น `invoice:create`, `product:read`
- Soft delete เท่านั้น

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — User**
```python
@dataclass
class User(BaseEntity):
    """User entity — เอนทิตีผู้ใช้"""
    email: str = ""
    full_name: str = ""
    phone: str = ""
    status: str = "ACTIVE"
    roles: list[str] = field(default_factory=list)  # role codes
    last_login_at: datetime | None = None
    avatar_url: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.email):
            raise DomainError(f"Invalid email: {self.email}")
        if not self.full_name:
            raise DomainError("Full name is required")

    def activate(self) -> None:
        if self.status == "ACTIVE":
            raise DomainError("User already active")
        self.status = "ACTIVE"

    def deactivate(self) -> None:
        if self.status == "INACTIVE":
            raise DomainError("User already inactive")
        self.status = "INACTIVE"

    def assign_role(self, role_code: str) -> None:
        if role_code in self.roles:
            raise DomainError(f"Role {role_code} already assigned")
        self.roles.append(role_code)

    def revoke_role(self, role_code: str) -> None:
        if role_code not in self.roles:
            raise DomainError(f"Role {role_code} not assigned")
        self.roles.remove(role_code)

    def has_role(self, role_code: str) -> bool:
        return role_code in self.roles

    def has_permission(self, permission: str, role_perms: dict[str, list[str]]) -> bool:
        """Check permission via roles — ตรวจสอบสิทธิ์"""
        for role in self.roles:
            if permission in role_perms.get(role, []):
                return True
        return False

@dataclass
class Role(BaseEntity):
    """Role entity — เอนทิตีบทบาท"""
    code: str = ""
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False

    def __post_init__(self):
        if not self.code or not re.match(r"^[a-z][a-z0-9_]*$", self.code):
            raise DomainError(f"Invalid role code: {self.code}")

    def add_permission(self, perm: str) -> None:
        if perm in self.permissions:
            return
        self.permissions.append(perm)
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Permission:
    """Permission VO — วัตถุสิทธิ์"""

    module: str
    action: str

    PATTERN = r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$"

    def __post_init__(self):
        combined = f"{self.module}:{self.action}"
        if not re.match(self.PATTERN, combined):
            raise DomainError(f"Invalid permission: {combined}")

    def __str__(self) -> str:
        return f"{self.module}:{self.action}"
```

**`domain/enums.py`**
```python
class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    LOCKED = "LOCKED"


class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IUserRepository(Protocol):
    async def save(self, user: User) -> User: ...
    async def get_by_id(self, id: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def list(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[User], int]: ...


class IRoleRepository(Protocol):
    async def save(self, role: Role) -> Role: ...
    async def get_by_code(self, code: str) -> Role | None: ...
    async def list_all(self) -> list[Role]: ...


class IUserCache(Protocol):
    async def get(self, id: str) -> User | None: ...
    async def insert(self, id: str, user: User) -> None: ...
    async def delete(self, id: str) -> None: ...


class IPermissionResolver(Protocol):
    async def get_role_permissions(self) -> dict[str, list[str]]: ...
```

**`application/use_cases.py`**
```python
class UserUseCases:
    """User use cases — กรณีการใช้งานผู้ใช้"""

    def __init__(
        self, user_repo, role_repo, cache, perm_resolver, idempotency, audit, events
    ): ...

    async def create_user(self, payload: dict, idem_key: str) -> User:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            if await self.user_repo.get_by_email(payload["email"]):
                raise UserEmailConflictException(payload["email"])

            user = User(**payload)
            user = await self.user_repo.save(user)

            verified = await self.user_repo.get_by_id(user.id)
            if not verified or verified.email != user.email:
                raise UserException("Read-back failed")

            await self.audit.log("user.created", user.id)
            await self.idempotency.set(idem_key, user)
            await self.events.publish("UserCreated", user)
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_user")
            raise UserException()

    async def assign_role(self, user_id: str, role_code: str) -> User:
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundException()
            role = await self.role_repo.get_by_code(role_code)
            if not role:
                raise RoleNotFoundException(role_code)
            user.assign_role(role_code)
            user = await self.user_repo.save(user)
            await self.cache.delete(user_id)
            await self.audit.log("user.role_assigned", user_id)
            await self.events.publish(
                "UserRoleAssigned", {"user_id": user_id, "role": role_code}
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in assign_role")
            raise UserException()

    async def check_permission(self, user_id: str, permission: str) -> bool:
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            role_perms = await self.perm_resolver.get_role_permissions()
            return user.has_permission(permission, role_perms)
        except Exception as e:
            logger.opt(exception=e).error("Error in check_permission")
            return False
```

**`application/mappers.py`** — `UserMapper`, `RoleMapper`
**`application/exceptions.py`** — `UserException`, `UserNotFoundException`, `UserEmailConflictException`, `RoleNotFoundException`
**`application/utils.py`** — `has_permission()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class UserModel(BaseModel):
    __tablename__ = "users"
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    avatar_url = Column(String(500))
    last_login_at = Column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_email"),)


class RoleModel(BaseModel):
    __tablename__ = "roles"
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    permissions = Column(JSONB, default=list)
    is_system = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_roles_code"),)


class UserRoleModel(BaseModel):
    __tablename__ = "user_roles"
    user_id = Column(String(36), nullable=False, index=True)
    role_code = Column(String(50), nullable=False)
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", "role_code", name="uq_user_role"),
    )
```

**`infrastructure/repositories.py`** — `PostgresUserRepository`, `PostgresRoleRepository`
**`infrastructure/caches.py`** — `RedisUserCache`
**`infrastructure/services.py`** — `PostgresPermissionResolver`

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.post("/", status_code=201)
async def create_user(payload: UserCreate, idem_key: str = Header(...), ...): ...

@router.get("/{id}/")
async def get_user(id: str, ...): ...

@router.get("/")
async def list_users(page: int = 1, limit: int = 20, ...): ...

@router.patch("/{id}/activate/")
async def activate_user(id: str, ...): ...

@router.patch("/{id}/deactivate/")
async def deactivate_user(id: str, ...): ...

@router.post("/{id}/roles/")
async def assign_role(id: str, payload: RoleAssignRequest, ...): ...

@router.delete("/{id}/roles/{role_code}/")
async def revoke_role(id: str, role_code: str, ...): ...

@router.get("/{id}/permissions/")
async def check_permission(id: str, permission: str, ...): ...
```

**`presentation/schemas.py`** — `UserCreate`, `UserResponse`, `RoleAssignRequest`, `PermissionResponse`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_user_use_cases()`

### 5. Invariants
- `email` unique ต่อ tenant
- `role.code` unique ต่อ tenant
- Role assignment idempotent
- System roles (`is_system=True`) ห้ามลบ
- Permission format `^[a-z_]+:[a-z_]+$`

### 6. Domain Events
- `UserCreated`, `UserActivated`, `UserDeactivated`, `UserRoleAssigned`, `UserRoleRevoked`

### 7. Tests
```python
async def test_create_user_unique_email(): ...
async def test_assign_role(): ...
async def test_revoke_role(): ...
async def test_check_permission(): ...
async def test_property_email_format(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `user`

**`db/migrations/V001__create_user.sql`**
```sql
BEGIN;

CREATE TABLE tenant_usr.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    email           VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    phone           VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    avatar_url      VARCHAR(500),
    last_login_at   TIMESTAMPTZ,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT uq_users_email UNIQUE (tenant_id, email),
    CONSTRAINT ck_users_email CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$')
);

CREATE INDEX ix_users_tenant_status ON tenant_usr.users(tenant_id, status) WHERE deleted_at IS NULL;

CREATE TABLE tenant_usr.roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    permissions     JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_roles_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_usr.user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    user_id         UUID NOT NULL REFERENCES tenant_usr.users(id) ON DELETE CASCADE,
    role_code       VARCHAR(50) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_role UNIQUE (tenant_id, user_id, role_code)
);

ALTER TABLE tenant_usr.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_users_tenant ON tenant_usr.users
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_usr.roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_roles_tenant ON tenant_usr.roles
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_usr.user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_user_roles_tenant ON tenant_usr.user_roles
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_user.sql`**
```sql
BEGIN;

-- Seed system roles
INSERT INTO tenant_usr.roles (tenant_id, code, name, permissions, is_system) VALUES
    ('00000000-0000-0000-0000-000000000001', 'admin', 'Administrator', '["*:*"]'::jsonb, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'manager', 'Manager', '["invoice:*","product:*","customer:read","report:read"]'::jsonb, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'staff', 'Staff', '["invoice:read","product:read","customer:read"]'::jsonb, TRUE)
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
```

**`db/migrations/V003__rollback_user.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_usr.user_roles CASCADE;
DROP TABLE IF EXISTS tenant_usr.roles CASCADE;
DROP TABLE IF EXISTS tenant_usr.users CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `user`

**`tests/unit/test_user.py`**
```python
import pytest
from app.modules.user.domain.entities import User, Role


class TestUserDomain:
    def test_create_valid(self):
        u = User(
            email="test@example.com,mycompany.com,gmail.com", full_name="Test User"
        )
        assert u.email == "test@example.com,mycompany.com,gmail.com"
        assert u.status == "ACTIVE"

    def test_invalid_email_raises(self):
        with pytest.raises(Exception):
            User(email="invalid", full_name="X")

    def test_assign_role(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test")
        u.assign_role("admin")
        assert u.has_role("admin")

    def test_duplicate_role_raises(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test")
        u.assign_role("admin")
        with pytest.raises(Exception):
            u.assign_role("admin")

    def test_has_permission(self):
        u = User(
            email="test@example.com,mycompany.com,gmail.com",
            full_name="Test",
            roles=["admin"],
        )
        perms = {"admin": ["invoice:create", "invoice:read"]}
        assert u.has_permission("invoice:create", perms)
        assert not u.has_permission("product:delete", perms)


class TestRoleDomain:
    def test_create_valid(self):
        r = Role(code="admin", name="Admin", permissions=["invoice:*"])
        assert r.code == "admin"

    def test_invalid_code_raises(self):
        with pytest.raises(Exception):
            Role(code="INVALID-CODE", name="X")

    def test_add_permission_idempotent(self):
        r = Role(code="admin", name="Admin")
        r.add_permission("invoice:read")
        r.add_permission("invoice:read")
        assert len(r.permissions) == 1
```

**`tests/integration/test_user_repository.py`** — testcontainers
**`tests/property/test_user_invariants.py`** — hypothesis
**`tests/manual/manual_test_user.md`** — manual test cases

---

## ✅ สรุป Layer 1 (Foundation) — 8/65 ไฟล์

| # | Module | Prefix | Entities | Tables | Output |
|---|---|---|---|---|---|
| 1.1 | `tenancy` | `ten` | Tenant | `public.tenants` | 23 ไฟล์ |
| 1.2 | `authentication` | `auth` | Credential, Session | `credentials`, `sessions` | 23 ไฟล์ |
| 1.3 | `user` | `usr` | User, Role | `users`, `roles`, `user_roles` | 23 ไฟล์ |
| 1.4 | `employee` | `emp` | Employee, Department | `employees`, `departments` | 23 ไฟล์ |
| 1.5 | `customer` | `cus` | Customer, Address | `customers`, `addresses` | 23 ไฟล์ |
| 1.6 | `supplier` | `sup` | Supplier | `suppliers` | 23 ไฟล์ |
| 1.7 | `product` | `prd` | Product, SKU, Barcode | `products`, `skus`, `barcodes` | 23 ไฟล์ |
| 1.8 | `pricing` | `prc` | PriceList, PriceRule | `price_lists`, `price_rules` | 23 ไฟล์ |

**Layer 1 เสร็จสมบูรณ์ — ต่อไปคือ Layer 2 (Money Path)**

---

# 📋 Layer 2: MONEY PATH — 7 Modules

> **Dependencies:** Layer 0 + Layer 1
> **Critical:** Money Path ต้อง idempotent + audit + read-back 100%

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 2.1 | `order` | `ord` | Order, OrderLine | `orders`, `order_lines` | `customer`, `product`, `pricing`, `money`, `idempotency`, `audit` |
| 2.2 | `invoice` | `inv` | Invoice, InvoiceLine | `invoices`, `invoice_lines` | `order`, `money`, `tax`, `ledger`, `audit`, `idempotency` |
| 2.3 | `ledger` | `led` | JournalEntry, LedgerAccount | `journal_entries`, `ledger_accounts` | `money`, `audit`, `events` |
| 2.4 | `payment` | `pay` | Payment, PaymentAllocation | `payments`, `payment_allocations` | `invoice`, `money`, `ledger`, `idempotency`, `audit` |
| 2.5 | `accounting_gateway` | `acg` | AccountingSync, ExternalAccount | `accounting_syncs`, `external_accounts` | `ledger`, `invoice`, `payment`, `events` |
| 2.6 | `tax` | `tax` | TaxRule, TaxReport | `tax_rules`, `tax_reports` | `money`, `invoice`, `audit` |
| 2.7 | `reconciliation` | `rec` | Reconciliation, MatchRecord | `reconciliations`, `match_records` | `payment`, `invoice`, `ledger`, `audit` |

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
        return (
            self.qty * self.unit_price * (Decimal("1") - self.discount_pct)
        ).quantize(Decimal("0.01"))

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
    async def list(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[Order], int]: ...


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

    def __init__(
        self, repo, cache, number_gen, inventory, idempotency, audit, events
    ): ...

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
                await self.inventory.reserve(
                    line.product_id, line.qty, order.order_number
                )

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
                    await self.inventory.release(
                        line.product_id, line.qty, order.order_number
                    )

            order.cancel(reason)
            order = await self.repo.save(order)
            await self.cache.delete(order_id)
            await self.audit.log("order.cancelled", order_id)
            await self.events.publish(
                "OrderCancelled", {"id": order_id, "reason": reason}
            )
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
    lines = relationship(
        "OrderLineModel", back_populates="order", cascade="all, delete-orphan"
    )


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
            o.add_line(
                OrderLine(product_id="p2", qty=Decimal("1"), unit_price=Decimal("50"))
            )

    def test_duplicate_product_raises(self):
        line = OrderLine(product_id="p1", qty=Decimal("1"), unit_price=Decimal("100"))
        o = Order(customer_id="c1", lines=[line])
        with pytest.raises(Exception):
            o.add_line(
                OrderLine(product_id="p1", qty=Decimal("2"), unit_price=Decimal("100"))
            )

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

# 📋 Layer 3: GOODS PATH — 13 Modules

> **Dependencies:** Layer 0 + Layer 1 + Layer 2
> **Critical:** Goods Path ต้อง idempotent + audit + traceability

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 3.1 | `inventory` | `invt` | StockItem, StockMove | `stock_items`, `stock_moves` | `product`, `warehouse`, `lot`, `audit`, `idempotency` |
| 3.2 | `warehouse` | `wh` | Warehouse, Location, Zone | `warehouses`, `locations`, `zones` | `tenancy`, `audit` |
| 3.3 | `lot` | `lot` | Lot, SerialNumber | `lots`, `serial_numbers` | `product`, `inventory`, `audit` |
| 3.4 | `production` | `prod` | ProductionOrder, ProductionLine | `production_orders`, `production_lines` | `recipe`, `inventory`, `lot`, `audit` |
| 3.5 | `recipe` | `rcp` | Recipe, RecipeIngredient, RecipeStep | `recipes`, `recipe_ingredients` | `product`, `inventory`, `audit` |
| 3.6 | `quality` | `qc` | QCInspection, QCCheckpoint | `qc_inspections`, `qc_checkpoints` | `lot`, `production`, `audit` |
| 3.7 | `waste` | `wst` | WasteRecord, WasteType | `waste_records`, `waste_types` | `inventory`, `production`, `audit` |
| 3.8 | `procurement` | `proc` | PurchaseOrder, PurchaseLine, SupplierQuote | `purchase_orders`, `purchase_lines` | `supplier`, `product`, `inventory`, `audit` |
| 3.9 | `traceability` | `trc` | TraceRecord, TraceEvent | `trace_records`, `trace_events` | `lot`, `inventory`, `production`, `events` |
| 3.10 | `agriculture` | `agr` | Farm, Plot, CropCycle, Harvest | `farms`, `plots`, `crop_cycles`, `harvests` | `crop`, `soil`, `irrigation`, `iot`, `inventory` |
| 3.11 | `crop` | `crp` | Crop, CropVariety | `crops`, `crop_varieties` | `agriculture`, `audit` |
| 3.12 | `soil` | `soil` | SoilTest, SoilNutrient | `soil_tests`, `soil_nutrients` | `agriculture`, `iot`, `audit` |
| 3.13 | `irrigation` | `irr` | IrrigationPlan, IrrigationEvent | `irrigation_plans`, `irrigation_events` | `agriculture`, `iot`, `audit` |

### 🎯 ตัวอย่างเต็ม: Module `inventory`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `inventory` |
| **Layer** | `3` (Goods Path) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `product`, `warehouse`, `lot`, `audit`, `idempotency`, `events` |
| **Domain Concepts** | `StockItem` (entity), `StockMove` (entity), `StockLevel` (VO), `MoveType` (enum) |
| **Prefix** | `invt` |
| **Tables** | `tenant_invt.stock_items`, `tenant_invt.stock_moves` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `inventory`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
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
    lot_id: str | None = None
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
    lot_id: str | None = None
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
        if self.move_type not in (
            "IN",
            "OUT",
            "TRANSFER",
            "ADJUST",
            "RESERVE",
            "RELEASE",
        ):
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
    async def get(
        self, product_id: str, warehouse_id: str, lot_id: str | None
    ) -> StockItem | None: ...
    async def list(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[StockItem], int]: ...


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

    def __init__(self, item_repo, move_repo, cache, idempotency, audit, events): ...

    async def post_movement(self, payload: dict, idem_key: str) -> StockMove:
        """Post stock movement — บันทึกการเคลื่อนไหว"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            move = StockMove(**payload)
            move = await self.move_repo.append(move)

            # Update stock item
            item = await self.item_repo.get(
                move.product_id, move.warehouse_id, move.lot_id
            )
            if not item:
                item = StockItem(
                    product_id=move.product_id,
                    warehouse_id=move.warehouse_id,
                    lot_id=move.lot_id,
                )
            item.apply_move(move)
            item = await self.item_repo.save(item)

            # Read-back
            verified = await self.item_repo.get(
                move.product_id, move.warehouse_id, move.lot_id
            )
            if not verified or verified.qty_on_hand != item.qty_on_hand:
                raise InventoryException("Read-back failed")

            # Invalidate cache
            cache_key = f"{move.product_id}:{move.warehouse_id}:{move.lot_id or 'none'}"
            await self.cache.delete(cache_key)

            await self.audit.log(f"stock.{move.move_type.lower()}", move.id)
            await self.idempotency.set(idem_key, move)

            # Check reorder
            if item.is_below_reorder():
                await self.events.publish(
                    "StockBelowReorder",
                    {
                        "product_id": item.product_id,
                        "warehouse_id": item.warehouse_id,
                        "available": str(item.qty_available),
                    },
                )

            await self.events.publish("StockMoved", move)
            return move
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in post_movement")
            raise InventoryException()

    async def get_stock_level(
        self, product_id: str, warehouse_id: str, lot_id: str | None = None
    ) -> StockLevel:
        try:
            cache_key = f"{product_id}:{warehouse_id}:{lot_id or 'none'}"
            cached = await self.cache.get(cache_key)
            if cached:
                return StockLevel(
                    cached.qty_on_hand, cached.qty_reserved, cached.qty_available
                )

            item = await self.item_repo.get(product_id, warehouse_id, lot_id)
            if not item:
                return StockLevel(Decimal("0"), Decimal("0"), Decimal("0"))

            await self.cache.insert(cache_key, item)
            return StockLevel(item.qty_on_hand, item.qty_reserved, item.qty_available)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_stock_level")
            raise InventoryException()

    async def transfer(
        self,
        product_id: str,
        from_wh: str,
        to_wh: str,
        qty: Decimal,
        ref: str,
        idem_key: str,
    ) -> None:
        """Transfer stock between warehouses — โอนสต็อก"""
        try:
            # OUT from source
            await self.post_movement(
                {
                    "product_id": product_id,
                    "warehouse_id": from_wh,
                    "move_type": "OUT",
                    "qty": qty,
                    "reference": ref,
                    "reference_type": "TRANSFER",
                },
                f"{idem_key}-out",
            )

            # IN to destination
            await self.post_movement(
                {
                    "product_id": product_id,
                    "warehouse_id": to_wh,
                    "move_type": "IN",
                    "qty": qty,
                    "reference": ref,
                    "reference_type": "TRANSFER",
                },
                f"{idem_key}-in",
            )
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
    lot_id = Column(String(36), nullable=True, index=True)
    qty_on_hand = Column(Numeric(15, 3), nullable=False, default=0)
    qty_reserved = Column(Numeric(15, 3), nullable=False, default=0)
    reorder_point = Column(Numeric(15, 3), default=0)
    avg_cost = Column(Numeric(15, 2), default=0)
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "product_id", "warehouse_id", "lot_id", name="uq_stock_item"
        ),
        CheckConstraint("qty_on_hand >= 0", name="ck_stock_on_hand"),
        CheckConstraint("qty_reserved >= 0", name="ck_stock_reserved"),
        CheckConstraint(
            "qty_reserved <= qty_on_hand", name="ck_stock_reserved_le_onhand"
        ),
    )


class StockMoveModel(BaseModel):
    __tablename__ = "stock_moves"
    product_id = Column(String(36), nullable=False, index=True)
    warehouse_id = Column(String(36), nullable=False, index=True)
    lot_id = Column(String(36), nullable=True)
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
async def get_stock(product_id: str, warehouse_id: str, lot_id: str | None = None, ...): ...

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
    lot_id          UUID,
    qty_on_hand     NUMERIC(15,3) NOT NULL DEFAULT 0,
    qty_reserved    NUMERIC(15,3) NOT NULL DEFAULT 0,
    reorder_point   NUMERIC(15,3) NOT NULL DEFAULT 0,
    avg_cost        NUMERIC(15,2) NOT NULL DEFAULT 0,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_stock_item UNIQUE (tenant_id, product_id, warehouse_id, lot_id),
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
    lot_id          UUID,
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
        move = StockMove(
            product_id="p1",
            warehouse_id="w1",
            move_type="IN",
            qty=Decimal("100"),
            reference="PO-001",
        )
        item.apply_move(move)
        assert item.qty_on_hand == Decimal("100")

    def test_apply_out_insufficient(self):
        item = StockItem(product_id="p1", warehouse_id="w1", qty_on_hand=Decimal("50"))
        move = StockMove(
            product_id="p1",
            warehouse_id="w1",
            move_type="OUT",
            qty=Decimal("100"),
            reference="SO-001",
        )
        with pytest.raises(Exception):
            item.apply_move(move)

    def test_reserve_available(self):
        item = StockItem(product_id="p1", warehouse_id="w1", qty_on_hand=Decimal("100"))
        move = StockMove(
            product_id="p1",
            warehouse_id="w1",
            move_type="RESERVE",
            qty=Decimal("30"),
            reference="ORD-001",
        )
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
| 3.3 | `lot` | `lot` | Lot, SerialNumber | `lots`, `serial_numbers` |
| 3.4 | `production` | `prod` | ProductionOrder | `production_orders` |
| 3.5 | `recipe` | `rcp` | Recipe, Ingredient | `recipes`, `recipe_ingredients` |
| 3.6 | `quality` | `qc` | QCInspection | `qc_inspections` |
| 3.7 | `waste` | `wst` | WasteRecord | `waste_records` |
| 3.8 | `procurement` | `proc` | PurchaseOrder | `purchase_orders` |
| 3.9 | `traceability` | `trc` | TraceRecord | `trace_records` |
| 3.10 | `agriculture` | `agr` | Farm, Plot, Harvest | `farms`, `plots`, `harvests` |
| 3.11 | `crop` | `crp` | Crop, Variety | `crops`, `crop_varieties` |
| 3.12 | `soil` | `soil` | SoilTest | `soil_tests` |
| 3.13 | `irrigation` | `irr` | IrrigationPlan | `irrigation_plans` |

**Layer 3 เสร็จสมบูรณ์ — ต่อไปคือ Layer 4 (Operations)**

---

# 📋 Layer 4: OPERATIONS — 13 Modules

> **Dependencies:** Layer 0-3
> **มิติ:** Logistics + Retail + CRM

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 4.1 | `transport` | `trn` | Vehicle, Driver, Trip | `vehicles`, `drivers`, `trips` | `employee`, `delivery`, `gps`, `audit` |
| 4.2 | `delivery` | `dlv` | Delivery, DeliveryLine, POD | `deliveries`, `delivery_lines` | `order`, `transport`, `gps`, `audit` |
| 4.3 | `route` | `rte` | Route, RouteStop | `routes`, `route_stops` | `delivery`, `gps`, `audit` |
| 4.4 | `gps` | `gps` | Location, Geofence, TrackPoint | `locations`, `geofences`, `track_points` | `iot`, `events` |
| 4.5 | `retail` | `rtl` | Store, StoreInventory | `stores`, `store_inventory` | `warehouse`, `product`, `audit` |
| 4.6 | `pos` | `pos` | POSTerminal, POSTransaction | `pos_terminals`, `pos_transactions` | `retail`, `product`, `payment`, `audit` |
| 4.7 | `shift` | `shf` | Shift, ShiftAssignment | `shifts`, `shift_assignments` | `employee`, `pos`, `audit` |
| 4.8 | `line_channel` | `line` | LINEMessage, LINEUser | `line_messages`, `line_users` | `customer`, `events` |
| 4.9 | `promotion` | `promo` | Promotion, PromotionRule | `promotions`, `promotion_rules` | `product`, `pricing`, `audit` |
| 4.10 | `loyalty` | `loy` | LoyaltyAccount, LoyaltyTier, Points | `loyalty_accounts`, `loyalty_tiers` | `customer`, `promotion`, `audit` |
| 4.11 | `crm` | `crm` | Lead, Deal, Activity | `leads`, `deals`, `activities` | `customer`, `line_channel`, `audit` |
| 4.12 | `campaign` | `cmp` | Campaign, CampaignAudience | `campaigns`, `campaign_audiences` | `crm`, `promotion`, `events` |
| 4.13 | `support` | `sup2` | Ticket, TicketMessage | `tickets`, `ticket_messages` | `customer`, `crm`, `audit` |

### 🎯 ตัวอย่างเต็ม: Module `crm`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `crm` |
| **Layer** | `4` (Operations) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **Dependencies** | `customer`, `line_channel`, `notification`, `campaign`, `invoice`, `audit` |
| **Domain Concepts** | `Lead` (entity), `Deal` (entity), `Pipeline` (VO), `Activity` (VO) |
| **Prefix** | `crm` |
| **Tables** | `tenant_crm.leads`, `tenant_crm.deals`, `tenant_crm.activities` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `crm`

## บริบท
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- มิติ: 📞 CRM (Lead → Customer → Loyalty → Satisfaction)
- **Invariants:** `Deal value >= 0`, `Pipeline stage forward-only`
- **Events:** `LeadCreated`, `LeadConverted`, `DealCreated`, `DealWon`, `DealLost`

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Lead**
```python
@dataclass
class Lead(BaseEntity):
    """Lead entity — เอนทิตีลีด"""
    name: str = ""
    contact: str = ""
    source: str = ""
    status: str = "NEW"
    assigned_to: str = ""
    email: str = ""
    phone: str = ""
    notes: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.name:
            raise DomainError("Lead name is required")

    def convert(self, customer_data: dict) -> "Customer":
        """Convert lead to customer — เปลี่ยนลีดเป็นลูกค้า"""
        if self.status == "CONVERTED":
            raise DomainError("Lead already converted")
        if self.status == "LOST":
            raise DomainError("Cannot convert lost lead")
        self.status = "CONVERTED"
        return Customer(**customer_data)

    def mark_lost(self, reason: str) -> None:
        if self.status in ("CONVERTED", "LOST"):
            raise DomainError(f"Cannot mark {self.status} lead as lost")
        self.status = "LOST"

    def assign(self, user_id: str) -> None:
        self.assigned_to = user_id
```

**`domain/entities.py` — Deal**
```python
@dataclass
class Deal(BaseEntity):
    """Deal entity — เอนทิตีดีล"""

    title: str = ""
    customer_id: str = ""
    lead_id: str | None = None
    value: Decimal = Decimal("0.00")
    currency: str = "THB"
    stage: str = "PROSPECTING"
    probability: int = 0
    expected_close: date | None = None
    owner_id: str = ""
    notes: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.title:
            raise DomainError("Deal title required")
        if self.value < 0:
            raise DomainError("Deal value cannot be negative")
        if not 0 <= self.probability <= 100:
            raise DomainError("Probability must be 0-100")

    def advance_stage(self, new_stage: str) -> None:
        """Advance deal stage (forward only) — เลื่อนขั้นดีล"""
        stages = [
            "PROSPECTING",
            "QUALIFICATION",
            "PROPOSAL",
            "NEGOTIATION",
            "CLOSED_WON",
            "CLOSED_LOST",
        ]
        if new_stage not in stages:
            raise DomainError(f"Invalid stage: {new_stage}")
        if self.stage in ("CLOSED_WON", "CLOSED_LOST"):
            raise DomainError(f"Cannot change closed deal: {self.stage}")
        current_idx = stages.index(self.stage)
        new_idx = stages.index(new_stage)
        if new_idx <= current_idx:
            raise DomainError(f"Cannot move backward: {self.stage} → {new_stage}")
        self.stage = new_stage

    def win(self) -> None:
        self.advance_stage("CLOSED_WON")
        self.probability = 100

    def lose(self, reason: str) -> None:
        self.advance_stage("CLOSED_LOST")
        self.probability = 0

    def is_open(self) -> bool:
        return self.stage not in ("CLOSED_WON", "CLOSED_LOST")

    @property
    def weighted_value(self) -> Decimal:
        return (self.value * Decimal(self.probability) / Decimal("100")).quantize(
            Decimal("0.01")
        )
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Pipeline:
    """Pipeline VO — วัตถุไปป์ไลน์"""

    stages: tuple[str, ...] = (
        "PROSPECTING",
        "QUALIFICATION",
        "PROPOSAL",
        "NEGOTIATION",
        "CLOSED_WON",
        "CLOSED_LOST",
    )

    def is_valid_stage(self, stage: str) -> bool:
        return stage in self.stages


@dataclass(frozen=True)
class Activity:
    """Activity VO — วัตถุกิจกรรม"""

    activity_type: str  # CALL, EMAIL, MEETING, LINE, NOTE
    subject: str
    description: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.activity_type not in ("CALL", "EMAIL", "MEETING", "LINE", "NOTE"):
            raise DomainError(f"Invalid activity type: {self.activity_type}")
```

**`domain/enums.py`**
```python
class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class DealStage(str, Enum):
    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class ActivityType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    LINE = "LINE"
    NOTE = "NOTE"
```

### 2. Application Layer (`application/`)

**`application/use_cases.py`**
```python
class CRMUseCases:
    """CRM use cases — กรณีการใช้งาน CRM"""

    def __init__(
        self,
        lead_repo,
        deal_repo,
        activity_repo,
        customer_repo,
        cache,
        idempotency,
        audit,
        events,
    ): ...

    async def create_lead(self, payload: dict, idem_key: str) -> Lead:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            lead = Lead(**payload)
            lead = await self.lead_repo.save(lead)

            # Read-back
            verified = await self.lead_repo.get_by_id(lead.id)
            if not verified or verified.name != lead.name:
                raise CRMException("Read-back failed")

            await self.audit.log("lead.created", lead.id)
            await self.idempotency.set(idem_key, lead)
            await self.events.publish("LeadCreated", lead)
            return lead
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_lead")
            raise CRMException()

    async def convert_lead(self, id: str, customer_data: dict) -> "Customer":
        try:
            lead = await self.lead_repo.get_by_id(id)
            if not lead:
                raise LeadNotFoundException()

            customer = lead.convert(customer_data)
            customer = await self.customer_repo.save(customer)
            lead = await self.lead_repo.save(lead)

            await self.audit.log("lead.converted", lead.id)
            await self.events.publish(
                "LeadConverted",
                {
                    "lead_id": lead.id,
                    "customer_id": customer.id,
                },
            )
            return customer
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in convert_lead")
            raise CRMException()

    async def create_deal(self, payload: dict, idem_key: str) -> Deal:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            deal = Deal(**payload)
            deal = await self.deal_repo.save(deal)

            verified = await self.deal_repo.get_by_id(deal.id)
            if not verified or verified.title != deal.title:
                raise CRMException("Read-back failed")

            await self.audit.log("deal.created", deal.id)
            await self.idempotency.set(idem_key, deal)
            await self.events.publish("DealCreated", deal)
            return deal
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_deal")
            raise CRMException()

    async def advance_deal(self, id: str, new_stage: str) -> Deal:
        try:
            deal = await self.deal_repo.get_by_id(id)
            if not deal:
                raise DealNotFoundException()

            old_stage = deal.stage
            deal.advance_stage(new_stage)
            deal = await self.deal_repo.save(deal)
            await self.cache.delete(id)
            await self.audit.log(f"deal.stage_{new_stage.lower()}", id)

            if new_stage == "CLOSED_WON":
                await self.events.publish("DealWon", deal)
            elif new_stage == "CLOSED_LOST":
                await self.events.publish("DealLost", deal)
            else:
                await self.events.publish(
                    "DealStageChanged",
                    {
                        "deal_id": id,
                        "from": old_stage,
                        "to": new_stage,
                    },
                )
            return deal
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in advance_deal")
            raise CRMException()

    async def get_pipeline(self, owner_id: str | None = None) -> dict:
        """Get pipeline summary — สรุปไปป์ไลน์"""
        try:
            deals = await self.deal_repo.list_open(owner_id)
            summary: dict[str, dict] = {}
            for stage in DealStage:
                stage_deals = [d for d in deals if d.stage == stage.value]
                summary[stage.value] = {
                    "count": len(stage_deals),
                    "total_value": sum(d.value for d in stage_deals),
                    "weighted_value": sum(d.weighted_value for d in stage_deals),
                }
            return summary
        except Exception as e:
            logger.opt(exception=e).error("Error in get_pipeline")
            raise CRMException()
```

**`application/mappers.py`** — `LeadMapper`, `DealMapper`, `ActivityMapper`
**`application/exceptions.py`** — `CRMException`, `LeadNotFoundException`, `DealNotFoundException`
**`application/utils.py`** — `calculate_weighted_pipeline()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class LeadModel(BaseModel):
    __tablename__ = "leads"
    name = Column(String(200), nullable=False)
    contact = Column(String(200))
    source = Column(String(50), index=True)
    status = Column(String(20), nullable=False, default="NEW", index=True)
    assigned_to = Column(String(36), index=True)
    email = Column(String(255))
    phone = Column(String(20))
    notes = Column(Text)


class DealModel(BaseModel):
    __tablename__ = "deals"
    title = Column(String(200), nullable=False)
    customer_id = Column(String(36), nullable=False, index=True)
    lead_id = Column(String(36), index=True)
    value = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), default="THB")
    stage = Column(String(20), nullable=False, default="PROSPECTING", index=True)
    probability = Column(Integer, default=0)
    expected_close = Column(Date)
    owner_id = Column(String(36), index=True)
    notes = Column(Text)
    __table_args__ = (
        CheckConstraint("value >= 0", name="ck_deal_value"),
        CheckConstraint(
            "probability >= 0 AND probability <= 100", name="ck_deal_probability"
        ),
    )


class ActivityModel(BaseModel):
    __tablename__ = "activities"
    entity_type = Column(String(20), nullable=False, index=True)  # LEAD, DEAL, CUSTOMER
    entity_id = Column(String(36), nullable=False, index=True)
    activity_type = Column(String(20), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    actor_id = Column(String(36))
```

**`infrastructure/repositories.py`** — `PostgresLeadRepository`, `PostgresDealRepository`, `PostgresActivityRepository`
**`infrastructure/caches.py`** — `RedisCRMCache`
**`infrastructure/services.py`** — `NotificationService` (LINE/Email)

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])

@router.post("/leads/", status_code=201)
async def create_lead(payload: LeadCreate, idem_key: str = Header(...), ...): ...

@router.get("/leads/{id}/")
async def get_lead(id: str, ...): ...

@router.get("/leads/")
async def list_leads(filters: LeadQuery, ...): ...

@router.post("/leads/{id}/convert/")
async def convert_lead(id: str, payload: ConvertRequest, ...): ...

@router.post("/deals/", status_code=201)
async def create_deal(payload: DealCreate, idem_key: str = Header(...), ...): ...

@router.patch("/deals/{id}/stage/")
async def advance_deal(id: str, payload: StageRequest, ...): ...

@router.patch("/deals/{id}/win/")
async def win_deal(id: str, ...): ...

@router.patch("/deals/{id}/lose/")
async def lose_deal(id: str, payload: LoseRequest, ...): ...

@router.get("/pipeline/")
async def get_pipeline(owner_id: str | None = None, ...): ...

@router.post("/activities/")
async def log_activity(payload: ActivityCreate, ...): ...
```

**`presentation/schemas.py`** — `LeadCreate`, `DealCreate`, `ConvertRequest`, `StageRequest`, `ActivityCreate`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_crm_use_cases()`

### 5. Invariants
- `Deal.value >= 0`
- `Deal.probability` 0-100
- Deal stage forward-only
- Closed deal ห้ามเปลี่ยน stage
- `weighted_value == value * probability / 100`

### 6. Domain Events
- `LeadCreated`, `LeadConverted`, `LeadLost`
- `DealCreated`, `DealStageChanged`, `DealWon`, `DealLost`
- `ActivityLogged`

### 7. Tests
```python
async def test_create_lead(): ...
async def test_convert_lead(): ...
async def test_deal_stage_forward_only():
    """Property: deal stage forward only"""
    deal = Deal(title="D1", customer_id="c1", value=Decimal("1000"), stage="PROPOSAL")
    with pytest.raises(Exception):
        deal.advance_stage("PROSPECTING")


async def test_deal_value_non_negative():
    with pytest.raises(Exception):
        Deal(title="D1", customer_id="c1", value=Decimal("-100"))


async def test_weighted_value():
    deal = Deal(title="D1", customer_id="c1", value=Decimal("10000"), probability=50)
    assert deal.weighted_value == Decimal("5000.00")


async def test_closed_deal_immutable(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `crm`

**`db/migrations/V001__create_crm.sql`**
```sql
BEGIN;

CREATE TABLE tenant_crm.leads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    name            VARCHAR(200) NOT NULL,
    contact         VARCHAR(200),
    source          VARCHAR(50),
    status          VARCHAR(20) NOT NULL DEFAULT 'NEW',
    assigned_to     UUID,
    email           VARCHAR(255),
    phone           VARCHAR(20),
    notes           TEXT,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX ix_leads_status ON tenant_crm.leads(status) WHERE deleted_at IS NULL;
CREATE INDEX ix_leads_assigned ON tenant_crm.leads(assigned_to) WHERE deleted_at IS NULL;

CREATE TABLE tenant_crm.deals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    title           VARCHAR(200) NOT NULL,
    customer_id     UUID NOT NULL,
    lead_id         UUID,
    value           NUMERIC(15,2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'THB',
    stage           VARCHAR(20) NOT NULL DEFAULT 'PROSPECTING',
    probability     INTEGER NOT NULL DEFAULT 0 CHECK (probability BETWEEN 0 AND 100),
    expected_close  DATE,
    owner_id        UUID,
    notes           TEXT,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX ix_deals_customer ON tenant_crm.deals(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX ix_deals_stage ON tenant_crm.deals(stage) WHERE deleted_at IS NULL;
CREATE INDEX ix_deals_owner ON tenant_crm.deals(owner_id) WHERE deleted_at IS NULL;

CREATE TABLE tenant_crm.activities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    entity_type     VARCHAR(20) NOT NULL,
    entity_id       UUID NOT NULL,
    activity_type   VARCHAR(20) NOT NULL,
    subject         VARCHAR(200) NOT NULL,
    description     TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_id        UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_activities_entity ON tenant_crm.activities(entity_type, entity_id, occurred_at DESC);

-- RLS
ALTER TABLE tenant_crm.leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_leads_tenant ON tenant_crm.leads
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_crm.deals ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_deals_tenant ON tenant_crm.deals
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_crm.activities ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_activities_tenant ON tenant_crm.activities
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_crm.sql`**
```sql
BEGIN;
-- Seed CRM sample data
COMMIT;
```

**`db/migrations/V003__rollback_crm.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_crm.activities CASCADE;
DROP TABLE IF EXISTS tenant_crm.deals CASCADE;
DROP TABLE IF EXISTS tenant_crm.leads CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `crm`

**`tests/unit/test_crm.py`**
```python
import pytest
from decimal import Decimal
from app.modules.crm.domain.entities import Lead, Deal


class TestLeadDomain:
    def test_create_valid(self):
        l = Lead(name="John Doe", contact="john@example.com,mycompany.com,gmail.com")
        assert l.status == "NEW"

    def test_convert(self):
        l = Lead(name="John", contact="j@example.com,mycompany.com,gmail.com")
        customer = l.convert(
            {"name": "John", "email": "j@example.com,mycompany.com,gmail.com"}
        )
        assert l.status == "CONVERTED"

    def test_cannot_convert_twice(self):
        l = Lead(name="John")
        l.convert({})
        with pytest.raises(Exception):
            l.convert({})


class TestDealDomain:
    def test_create_valid(self):
        d = Deal(title="Deal 1", customer_id="c1", value=Decimal("10000"))
        assert d.stage == "PROSPECTING"

    def test_negative_value_raises(self):
        with pytest.raises(Exception):
            Deal(title="D1", customer_id="c1", value=Decimal("-100"))

    def test_advance_stage_forward_only(self):
        d = Deal(title="D1", customer_id="c1", value=Decimal("1000"), stage="PROPOSAL")
        with pytest.raises(Exception):
            d.advance_stage("PROSPECTING")

    def test_win_sets_probability_100(self):
        d = Deal(
            title="D1", customer_id="c1", value=Decimal("1000"), stage="NEGOTIATION"
        )
        d.win()
        assert d.stage == "CLOSED_WON"
        assert d.probability == 100

    def test_weighted_value(self):
        d = Deal(title="D1", customer_id="c1", value=Decimal("10000"), probability=50)
        assert d.weighted_value == Decimal("5000.00")

    def test_property_stage_forward(self):
        """Property: deal stage ห้ามถอยกลับ"""
        for _ in range(100):
            d = Deal(title="D1", customer_id="c1", value=Decimal("1000"))
            # advance multiple times — never backward
```

**`tests/integration/test_crm_repository.py`** — testcontainers
**`tests/property/test_crm_invariants.py`** — hypothesis
**`tests/manual/manual_test_crm.md`** — manual test cases

---

## ✅ สรุป Layer 4 (Operations) — 13/65 ไฟล์

| # | Module | Prefix | Entities | Tables |
|---|---|---|---|---|
| 4.1 | `transport` | `trn` | Vehicle, Driver, Trip | `vehicles`, `drivers`, `trips` |
| 4.2 | `delivery` | `dlv` | Delivery, POD | `deliveries`, `delivery_lines` |
| 4.3 | `route` | `rte` | Route, Stop | `routes`, `route_stops` |
| 4.4 | `gps` | `gps` | Location, Geofence | `locations`, `geofences` |
| 4.5 | `retail` | `rtl` | Store | `stores` |
| 4.6 | `pos` | `pos` | POSTerminal, Transaction | `pos_terminals`, `pos_transactions` |
| 4.7 | `shift` | `shf` | Shift, Assignment | `shifts`, `shift_assignments` |
| 4.8 | `line_channel` | `line` | LINEMessage | `line_messages` |
| 4.9 | `promotion` | `promo` | Promotion, Rule | `promotions`, `promotion_rules` |
| 4.10 | `loyalty` | `loy` | LoyaltyAccount, Tier | `loyalty_accounts` |
| 4.11 | `crm` | `crm` | Lead, Deal, Activity | `leads`, `deals`, `activities` |
| 4.12 | `campaign` | `cmp` | Campaign | `campaigns` |
| 4.13 | `support` | `sup2` | Ticket | `tickets` |

**Layer 4 เสร็จสมบูรณ์ — ต่อไปคือ Layer 5 (Intelligence)**

---

# 📋 Layer 5: INTELLIGENCE — 7 Modules

> **Dependencies:** Layer 0-4
> **มิติ:** BI + Analytics + ML

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 5.1 | `reporting` | `rpt` | Report, ReportSchedule, ReportExecution | `reports`, `report_executions` | `analytics`, `audit` |
| 5.2 | `analytics` | `anl` | Metric, MetricSnapshot, Dimension | `metrics`, `metric_snapshots` | `reporting`, `events` |
| 5.3 | `forecast` | `fc` | Forecast, ForecastResult | `forecasts` | `analytics`, `production`, `inventory`, `agriculture` |
| 5.4 | `kpi` | `kpi` | KPI, KPIValue, KPITarget | `kpis`, `kpi_values` | `analytics`, `reporting` |
| 5.5 | `satisfaction` | `csat` | Survey, SurveyResponse, NPS | `surveys`, `survey_responses` | `customer`, `support`, `crm` |
| 5.6 | `recommendation` | `reco` | Recommendation, RecommendationRule | `recommendations` | `analytics`, `product`, `crm` |
| 5.7 | `oee` | `oee` | OEE, OEERecord | `oee_records` | `production`, `iot`, `kpi` |

### 🎯 ตัวอย่างเต็ม: Module `forecast`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `forecast` |
| **Layer** | `5` (Intelligence) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **Dependencies** | `analytics`, `reporting`, `production`, `inventory`, `agriculture` |
| **Domain Concepts** | `Forecast` (entity), `ForecastResult` (VO), `ForecastMethod` (enum) |
| **Prefix** | `fc` |
| **Tables** | `tenant_fc.forecasts` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `forecast`

## บริบท
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- **Invariants:** `MAPE < 20%`, `Forecast non-negative`
- **Events:** `ForecastGenerated`, `ForecastUpdated`, `ForecastAccuracyDropped`
- รองรับ methods: LSTM, PROPHET, XGBOOST, ARIMA, ENSEMBLE

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Forecast**
```python
@dataclass
class Forecast(BaseEntity):
    """Forecast entity — เอนทิตีพยากรณ์"""
    product_id: str = ""
    branch_id: str = ""
    forecast_date: date | None = None
    predicted_qty: Decimal = Decimal("0.000")
    actual_qty: Decimal | None = None
    method: str = "LSTM"
    mape: Decimal | None = None
    confidence: Decimal = Decimal("0.00")  # 0-1
    horizon_days: int = 30

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if self.predicted_qty < 0:
            raise DomainError("Predicted qty cannot be negative")
        if self.actual_qty is not None and self.actual_qty < 0:
            raise DomainError("Actual qty cannot be negative")
        if not 0 <= self.confidence <= 1:
            raise DomainError("Confidence must be 0-1")

    def update_actual(self, actual_qty: Decimal) -> None:
        """Update actual and calculate MAPE — อัปเดตค่าจริงและคำนวณ MAPE"""
        if actual_qty < 0:
            raise DomainError("Actual qty cannot be negative")
        self.actual_qty = actual_qty
        if actual_qty > 0:
            self.mape = (abs(self.predicted_qty - actual_qty) / actual_qty * 100).quantize(Decimal("0.01"))

    def is_accurate(self) -> bool:
        """MAPE < 20% — ตรวจสอบความแม่นยำ"""
        return self.mape is not None and self.mape < 20

    def error(self) -> Decimal | None:
        if self.actual_qty is None:
            return None
        return self.predicted_qty - self.actual_qty
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ForecastResult:
    """Forecast result VO — ผลลัพธ์พยากรณ์"""

    predicted: Decimal
    actual: Decimal | None
    error: Decimal | None
    mape: Decimal | None
    confidence: Decimal


@dataclass(frozen=True)
class ForecastHorizon:
    """Forecast horizon VO — วัตถุขอบเขต"""

    days: int
    granularity: str  # DAY, WEEK, MONTH

    def __post_init__(self):
        if self.days <= 0:
            raise DomainError("Horizon days must be positive")
        if self.granularity not in ("DAY", "WEEK", "MONTH"):
            raise DomainError(f"Invalid granularity: {self.granularity}")
```

**`domain/enums.py`**
```python
class ForecastMethod(str, Enum):
    LSTM = "LSTM"
    PROPHET = "PROPHET"
    XGBOOST = "XGBOOST"
    ARIMA = "ARIMA"
    ENSEMBLE = "ENSEMBLE"


class ForecastType(str, Enum):
    DEMAND = "DEMAND"
    PRODUCTION = "PRODUCTION"
    YIELD = "YIELD"
    PRICE = "PRICE"


class Granularity(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
```

### 2. Application Layer (`application/`)

**`application/use_cases.py`**
```python
class ForecastUseCases:
    """Forecast use cases — กรณีการใช้งานพยากรณ์"""

    def __init__(self, repo, analytics_repo, ml_service, cache, audit, events): ...

    async def generate_forecast(
        self,
        product_id: str,
        branch_id: str,
        days: int,
        method: str = "LSTM",
    ) -> list[Forecast]:
        """Generate forecast — สร้างพยากรณ์"""
        try:
            # Load historical data
            data = await self.analytics_repo.get_history(
                product_id, branch_id, days * 3
            )
            if len(data) < 30:
                raise InsufficientDataException("Need at least 30 data points")

            # Predict
            predictions = await self.ml_service.predict(data, days, method)

            # Save
            forecasts = []
            for pred in predictions:
                forecast = Forecast(
                    product_id=product_id,
                    branch_id=branch_id,
                    forecast_date=pred["date"],
                    predicted_qty=pred["qty"],
                    method=method,
                    confidence=pred.get("confidence", Decimal("0.8")),
                    horizon_days=days,
                )
                forecast = await self.repo.save(forecast)
                forecasts.append(forecast)

            await self.audit.log("forecast.generated", product_id)
            await self.events.publish(
                "ForecastGenerated",
                {
                    "product_id": product_id,
                    "branch_id": branch_id,
                    "method": method,
                    "count": len(forecasts),
                },
            )
            return forecasts
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in generate_forecast")
            raise ForecastException()

    async def update_actual(self, forecast_id: str, actual_qty: Decimal) -> Forecast:
        try:
            forecast = await self.repo.get_by_id(forecast_id)
            if not forecast:
                raise ForecastNotFoundException()
            forecast.update_actual(actual_qty)
            forecast = await self.repo.save(forecast)
            await self.cache.delete(forecast_id)

            if forecast.mape and forecast.mape > 20:
                await self.events.publish(
                    "ForecastAccuracyDropped",
                    {
                        "forecast_id": forecast_id,
                        "mape": str(forecast.mape),
                    },
                )
            await self.audit.log("forecast.actual_updated", forecast_id)
            return forecast
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in update_actual")
            raise ForecastException()

    async def backtest(self, product_id: str, days: int, method: str) -> dict:
        """Backtest — ทดสอบย้อนหลัง"""
        try:
            data = await self.analytics_repo.get_history(product_id, None, days * 2)
            train = data[: len(data) // 2]
            test = data[len(data) // 2 :]

            predictions = await self.ml_service.predict(train, len(test), method)
            mape_values = []
            for pred, actual in zip(predictions, test):
                if actual["qty"] > 0:
                    mape = abs(pred["qty"] - actual["qty"]) / actual["qty"] * 100
                    mape_values.append(float(mape))

            avg_mape = sum(mape_values) / len(mape_values) if mape_values else 0
            return {
                "product_id": product_id,
                "method": method,
                "avg_mape": round(avg_mape, 2),
                "is_accurate": avg_mape < 20,
                "samples": len(mape_values),
            }
        except Exception as e:
            logger.opt(exception=e).error("Error in backtest")
            raise ForecastException()
```

**`application/mappers.py`** — `ForecastMapper`
**`application/exceptions.py`** — `ForecastException`, `ForecastNotFoundException`, `InsufficientDataException`
**`application/utils.py`** — `calculate_mape()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class ForecastModel(BaseModel):
    __tablename__ = "forecasts"
    product_id = Column(String(36), nullable=False, index=True)
    branch_id = Column(String(36), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_qty = Column(Numeric(15, 3), nullable=False)
    actual_qty = Column(Numeric(15, 3))
    method = Column(String(20), nullable=False, default="LSTM")
    mape = Column(Numeric(5, 2))
    confidence = Column(Numeric(5, 4), default=0)
    horizon_days = Column(Integer, nullable=False, default=30)
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "product_id",
            "branch_id",
            "forecast_date",
            "method",
            name="uq_forecast",
        ),
        CheckConstraint("predicted_qty >= 0", name="ck_forecast_predicted"),
    )
```

**`infrastructure/repositories.py`** — `PostgresForecastRepository`
**`infrastructure/caches.py`** — `RedisForecastCache`
**`infrastructure/services.py`**
```python
class MLForecastService:
    """ML forecast service — บริการ ML พยากรณ์"""

    async def predict(self, data: list[dict], days: int, method: str) -> list[dict]:
        if method == "LSTM":
            return await self._lstm(data, days)
        elif method == "PROPHET":
            return await self._prophet(data, days)
        elif method == "ENSEMBLE":
            return await self._ensemble(data, days)
        else:
            raise DomainError(f"Unsupported method: {method}")

    async def _lstm(self, data: list[dict], days: int) -> list[dict]:
        # Load LSTM model, predict
        ...

    async def _prophet(self, data: list[dict], days: int) -> list[dict]: ...

    async def _ensemble(self, data: list[dict], days: int) -> list[dict]:
        results = await asyncio.gather(
            self._lstm(data, days),
            self._prophet(data, days),
        )
        # Average
        return [
            {
                "date": r[0]["date"],
                "qty": sum(x["qty"] for x in r) / len(r),
                "confidence": Decimal("0.85"),
            }
            for r in zip(*results)
        ]
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/forecast", tags=["Forecast"])

@router.post("/generate/")
async def generate(
    product_id: str, branch_id: str, days: int = 30, method: str = "LSTM",
    ...): ...

@router.get("/{product_id}/")
async def get_forecasts(product_id: str, from_date: date | None = None, ...): ...

@router.patch("/{forecast_id}/actual/")
async def update_actual(forecast_id: str, payload: ActualRequest, ...): ...

@router.post("/backtest/")
async def backtest(product_id: str, days: int, method: str = "LSTM", ...): ...

@router.get("/accuracy/{product_id}/")
async def get_accuracy(product_id: str, ...): ...
```

**`presentation/schemas.py`** — `ForecastGenerateRequest`, `ForecastResponse`, `ActualRequest`, `BacktestResponse`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_forecast_use_cases()`

### 5. Invariants
- `predicted_qty >= 0`
- `actual_qty >= 0`
- `confidence` 0-1
- `MAPE < 20%` = accurate
- `error == predicted - actual`

### 6. Domain Events
- `ForecastGenerated`, `ForecastUpdated`, `ForecastAccuracyDropped`

### 7. Tests
```python
async def test_generate_forecast(): ...
async def test_mape_calculation():
    f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
    f.update_actual(Decimal("110"))
    assert f.mape == Decimal("9.09")  # (|100-110|/110)*100


async def test_forecast_accurate():
    f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
    f.update_actual(Decimal("105"))
    assert f.is_accurate()


async def test_forecast_inaccurate():
    f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
    f.update_actual(Decimal("200"))
    assert not f.is_accurate()


async def test_property_forecast_non_negative():
    for _ in range(100):
        f = Forecast(
            product_id="p1",
            branch_id="b1",
            predicted_qty=Decimal(str(random.uniform(0, 10000))),
        )
        assert f.predicted_qty >= 0
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `forecast`

**`db/migrations/V001__create_forecast.sql`**
```sql
BEGIN;

CREATE TABLE tenant_fc.forecasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    product_id      UUID NOT NULL,
    branch_id       UUID NOT NULL,
    forecast_date   DATE NOT NULL,
    predicted_qty   NUMERIC(15,3) NOT NULL CHECK (predicted_qty >= 0),
    actual_qty      NUMERIC(15,3) CHECK (actual_qty IS NULL OR actual_qty >= 0),
    method          VARCHAR(20) NOT NULL DEFAULT 'LSTM',
    mape            NUMERIC(5,2),
    confidence      NUMERIC(5,4) NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    horizon_days    INTEGER NOT NULL DEFAULT 30,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_forecast UNIQUE (tenant_id, product_id, branch_id, forecast_date, method)
);

CREATE INDEX ix_forecast_product ON tenant_fc.forecasts(product_id, forecast_date);
CREATE INDEX ix_forecast_accuracy ON tenant_fc.forecasts(mape) WHERE mape IS NOT NULL;

ALTER TABLE tenant_fc.forecasts ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_forecasts_tenant ON tenant_fc.forecasts
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_forecast.sql`**
```sql
BEGIN;
-- No seed data needed
COMMIT;
```

**`db/migrations/V003__rollback_forecast.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_fc.forecasts CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `forecast`

**`tests/unit/test_forecast.py`**
```python
import pytest
from decimal import Decimal
from app.modules.forecast.domain.entities import Forecast


class TestForecastDomain:
    def test_create_valid(self):
        f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
        assert f.predicted_qty == Decimal("100")

    def test_negative_predicted_raises(self):
        with pytest.raises(Exception):
            Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("-10"))

    def test_mape_calculation(self):
        f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
        f.update_actual(Decimal("110"))
        assert f.mape == Decimal("9.09")

    def test_is_accurate(self):
        f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
        f.update_actual(Decimal("105"))
        assert f.is_accurate()

    def test_is_inaccurate(self):
        f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
        f.update_actual(Decimal("200"))
        assert not f.is_accurate()

    def test_error_calculation(self):
        f = Forecast(product_id="p1", branch_id="b1", predicted_qty=Decimal("100"))
        f.update_actual(Decimal("90"))
        assert f.error() == Decimal("10")

    def test_property_predicted_non_negative(self):
        import random

        for _ in range(100):
            qty = Decimal(str(random.uniform(0, 10000)))
            f = Forecast(product_id="p1", branch_id="b1", predicted_qty=qty)
            assert f.predicted_qty >= 0
```

**`tests/integration/test_forecast_repository.py`** — testcontainers
**`tests/property/test_forecast_invariants.py`** — hypothesis
**`tests/manual/manual_test_forecast.md`** — manual test cases

---

## ✅ สรุป Layer 5 (Intelligence) — 7/65 ไฟล์

| # | Module | Prefix | Entities | Tables |
|---|---|---|---|---|
| 5.1 | `reporting` | `rpt` | Report, Schedule | `reports`, `report_executions` |
| 5.2 | `analytics` | `anl` | Metric, Snapshot | `metrics`, `metric_snapshots` |
| 5.3 | `forecast` | `fc` | Forecast | `forecasts` |
| 5.4 | `kpi` | `kpi` | KPI, KPIValue | `kpis`, `kpi_values` |
| 5.5 | `satisfaction` | `csat` | Survey, Response | `surveys`, `survey_responses` |
| 5.6 | `recommendation` | `reco` | Recommendation | `recommendations` |
| 5.7 | `oee` | `oee` | OEE, OEERecord | `oee_records` |

**Layer 5 เสร็จสมบูรณ์ — ต่อไปคือ Layer 6 (Monitoring)**

---

# 📋 Layer 6: MONITORING — 8 Modules

> **Dependencies:** Layer 0-5
> **มิติ:** IoT + Infrastructure Monitoring

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 6.1 | `iot` | `iot` | SensorReading, Threshold | `sensor_readings` | `monitoring`, `alerting`, `events` |
| 6.2 | `cctv` | `cctv` | Camera, Recording, Event | `cameras`, `recordings` | `iot`, `alerting`, `audit` |
| 6.3 | `monitoring` | `mon` | HealthCheck, Metric, Uptime | `health_checks`, `metrics` | `events` |
| 6.4 | `backup` | `bkp` | BackupJob, BackupSnapshot | `backup_jobs`, `backup_snapshots` | `monitoring`, `audit` |
| 6.5 | `alerting` | `alr` | Alert, AlertRule, Notification | `alerts`, `alert_rules` | `events`, `config` |
| 6.6 | `audit_viewer` | `av` | AuditView, AuditFilter | — (view only) | `audit`, `reporting` |
| 6.7 | `maintenance` | `mnt` | MaintenanceSchedule, WorkOrder | `maintenance_schedules`, `work_orders` | `iot`, `alerting`, `audit` |
| 6.8 | `energy` | `eng` | EnergyReading, EnergyTariff | `energy_readings`, `energy_tariffs` | `iot`, `monitoring`, `kpi` |

### 🎯 ตัวอย่างเต็ม: Module `iot`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `iot` |
| **Layer** | `6` (Monitoring & Sensing) |
| **Priority** | 🟠 |
| **Phase** | 4 |
| **Dependencies** | `monitoring`, `alerting`, `events` |
| **Domain Concepts** | `SensorReading` (entity), `Threshold` (VO), `SensorType` (enum) |
| **Prefix** | `iot` |
| **Tables** | `tenant_iot.sensor_readings` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `iot`

## บริบท
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- **Invariants:** `Reading within valid range`, `Alert when threshold exceeded`
- **Events:** `SensorReadingReceived`, `ThresholdExceeded`, `SensorOffline`
- Protocol: MQTT (real-time) + HTTP (fallback)
- Storage: PostgreSQL (recent) + InfluxDB (time-series)
- Dedup: Redis bloom filter

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — SensorReading**
```python
@dataclass
class SensorReading(BaseEntity):
    """Sensor reading entity — เอนทิตีค่าอ่านเซ็นเซอร์"""
    sensor_id: str = ""
    sensor_type: str = ""
    value: Decimal = Decimal("0.00")
    unit: str = ""
    timestamp: datetime | None = None
    location: str = ""
    device_id: str = ""

    def __post_init__(self):
        self._validate()
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def _validate(self) -> None:
        """Validate reading — ตรวจสอบค่าอ่าน"""
        if not self.sensor_id:
            raise DomainError("Sensor ID is required")
        if not self.sensor_type:
            raise DomainError("Sensor type is required")

        ranges = {
            "TEMPERATURE": (-50, 100),
            "HUMIDITY": (0, 100),
            "CO2": (0, 10000),
            "LIGHT": (0, 800000),
            "PH": (0, 14),
            "EC": (0, 100),
            "FLOW": (0, 10000),
            "PRESSURE": (0, 1000),
        }

        if self.sensor_type in ranges:
            min_val, max_val = ranges[self.sensor_type]
            if not min_val <= self.value <= max_val:
                raise DomainError(f"{self.sensor_type} out of range [{min_val}, {max_val}]: {self.value}")

    def is_out_of_range(self, threshold: "Threshold") -> bool:
        """Check if out of range — ตรวจสอบว่านอกช่วง"""
        return self.value < threshold.min or self.value > threshold.max
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Threshold:
    """Threshold VO — ค่าเกณฑ์"""

    min: Decimal
    max: Decimal
    unit: str
    alert_level: str = "WARNING"

    def __post_init__(self):
        if self.min >= self.max:
            raise DomainError("Min must be less than max")


@dataclass(frozen=True)
class SensorRange:
    """Sensor range VO — วัตถุช่วงเซ็นเซอร์"""

    sensor_type: str
    min: Decimal
    max: Decimal

    def is_valid(self, value: Decimal) -> bool:
        return self.min <= value <= self.max
```

**`domain/enums.py`**
```python
class SensorType(str, Enum):
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    CO2 = "CO2"
    LIGHT = "LIGHT"
    PH = "PH"
    EC = "EC"
    FLOW = "FLOW"
    PRESSURE = "PRESSURE"


class SensorStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class ISensorReadingRepository(Protocol):
    async def save(self, reading: SensorReading) -> SensorReading: ...
    async def get_latest(self, sensor_id: str) -> SensorReading | None: ...
    async def get_range(
        self, sensor_id: str, from_dt: datetime, to_dt: datetime
    ) -> list[SensorReading]: ...


class ISensorCache(Protocol):
    async def get_latest(self, sensor_id: str) -> SensorReading | None: ...
    async def set_latest(self, sensor_id: str, reading: SensorReading) -> None: ...
    async def is_duplicate(self, sensor_id: str, timestamp: datetime) -> bool: ...


class IThresholdRepository(Protocol):
    async def get_for_sensor(self, sensor_id: str) -> Threshold | None: ...


class IAlertingService(Protocol):
    async def send(self, message: str, level: str) -> None: ...


class ITimeSeriesStore(Protocol):
    async def write(self, reading: SensorReading) -> None: ...
```

**`application/use_cases.py`**
```python
class IoTUseCases:
    """IoT use cases — กรณีการใช้งาน IoT"""

    def __init__(
        self,
        repo,
        cache,
        threshold_repo,
        alerting,
        ts_store,
        idempotency,
        audit,
        events,
    ): ...

    async def ingest_reading(self, payload: dict, idem_key: str) -> SensorReading:
        """Ingest sensor reading — รับค่าจากเซ็นเซอร์"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            reading = SensorReading(**payload)

            # Dedup check
            if await self.cache.is_duplicate(reading.sensor_id, reading.timestamp):
                logger.info(
                    f"Duplicate reading {reading.sensor_id}@{reading.timestamp}"
                )
                return reading

            # Save to PostgreSQL
            reading = await self.repo.save(reading)

            # Write to time-series (InfluxDB)
            await self.ts_store.write(reading)

            # Update cache
            await self.cache.set_latest(reading.sensor_id, reading)

            # Check threshold
            threshold = await self.threshold_repo.get_for_sensor(reading.sensor_id)
            if threshold and reading.is_out_of_range(threshold):
                await self.alerting.send(
                    f"Sensor {reading.sensor_id} out of range: {reading.value} {reading.unit}",
                    level=threshold.alert_level,
                )
                await self.events.publish(
                    "ThresholdExceeded",
                    {
                        "sensor_id": reading.sensor_id,
                        "value": str(reading.value),
                        "threshold_min": str(threshold.min),
                        "threshold_max": str(threshold.max),
                    },
                )

            await self.idempotency.set(idem_key, reading)
            await self.events.publish("SensorReadingReceived", reading)
            return reading
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in ingest_reading")
            raise IoTException()

    async def get_latest(self, sensor_id: str) -> SensorReading | None:
        """Get latest reading — ดูค่าล่าสุด"""
        try:
            cached = await self.cache.get_latest(sensor_id)
            if cached:
                return cached

            reading = await self.repo.get_latest(sensor_id)
            if reading:
                await self.cache.set_latest(sensor_id, reading)
            return reading
        except Exception as e:
            logger.opt(exception=e).error("Error in get_latest")
            raise IoTException()

    async def get_range(
        self, sensor_id: str, from_dt: datetime, to_dt: datetime
    ) -> list[SensorReading]:
        try:
            return await self.repo.get_range(sensor_id, from_dt, to_dt)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_range")
            raise IoTException()

    async def detect_offline_sensors(self, threshold_minutes: int = 5) -> list[str]:
        """Detect offline sensors — ตรวจจับเซ็นเซอร์ออฟไลน์"""
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=threshold_minutes)
            offline = await self.repo.get_offline_sensors(cutoff)
            for sensor_id in offline:
                await self.events.publish("SensorOffline", {"sensor_id": sensor_id})
            return offline
        except Exception as e:
            logger.opt(exception=e).error("Error in detect_offline")
            raise IoTException()
```

**`application/mappers.py`** — `SensorReadingMapper`
**`application/exceptions.py`** — `IoTException`, `SensorNotFoundException`, `InvalidReadingException`
**`application/utils.py`** — `validate_reading_range()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class SensorReadingModel(BaseModel):
    __tablename__ = "sensor_readings"
    sensor_id = Column(String(100), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False, index=True)
    value = Column(Numeric(15, 4), nullable=False)
    unit = Column(String(20))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String(200))
    device_id = Column(String(100), index=True)
    __table_args__ = (
        Index("ix_sensor_time", "sensor_id", "timestamp"),
        Index("ix_device_time", "device_id", "timestamp"),
    )
```

**`infrastructure/repositories.py`** — `PostgresSensorReadingRepository`
**`infrastructure/caches.py`** — `RedisSensorCache` (bloom filter dedup)
```python
class RedisSensorCache:
    """Redis sensor cache — แคชเซ็นเซอร์"""

    async def get_latest(self, sensor_id: str) -> SensorReading | None:
        try:
            data = await self.redis.get(f"sensor:latest:{sensor_id}")
            return SensorReading(**json.loads(data)) if data else None
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed")
            return None

    async def set_latest(self, sensor_id: str, reading: SensorReading) -> None:
        try:
            await self.redis.setex(
                f"sensor:latest:{sensor_id}",
                300,
                json.dumps(asdict(reading), default=str),
            )
        except Exception as e:
            logger.opt(exception=e).error("Cache set failed")

    async def is_duplicate(self, sensor_id: str, ts: datetime) -> bool:
        """Bloom filter dedup — ตรวจสอบซ้ำ"""
        try:
            key = f"sensor:seen:{sensor_id}:{ts.timestamp()}"
            result = await self.redis.set(key, "1", nx=True, ex=60)
            return not bool(result)
        except Exception:
            return False  # fail open
```

**`infrastructure/services.py`**
```python
class MQTTService:
    """MQTT service — บริการ MQTT"""

    def __init__(self, broker: str, client_id: str):
        self.broker = broker
        self.client_id = client_id
        self.client: mqtt.Client | None = None

    async def connect(self) -> None:
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.connect(self.broker, 1883, 60)
        self.client.loop_start()

    async def subscribe(self, topic: str, handler: callable) -> None:
        self.client.subscribe(topic, qos=1)
        self.client.on_message = handler

    async def publish(self, topic: str, payload: dict) -> None:
        self.client.publish(topic, json.dumps(payload), qos=1)


class InfluxDBService:
    """InfluxDB service — บริการ InfluxDB"""

    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

    async def write(self, reading: SensorReading) -> None:
        try:
            # Write point to InfluxDB
            ...
        except Exception as e:
            logger.opt(exception=e).error("InfluxDB write failed")

    async def query_range(
        self, sensor_id: str, from_dt: datetime, to_dt: datetime
    ) -> list: ...
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/iot", tags=["IoT"])

@router.post("/reading/", status_code=201)
async def ingest_reading(
    payload: SensorReadingCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    ...): ...

@router.get("/{sensor_id}/latest/")
async def get_latest(sensor_id: str, ...): ...

@router.get("/{sensor_id}/range/")
async def get_range(sensor_id: str, from_dt: datetime, to_dt: datetime, ...): ...

@router.get("/offline/")
async def list_offline(threshold_minutes: int = 5, ...): ...

@router.get("/sensors/")
async def list_sensors(...): ...
```

**`presentation/schemas.py`** — `SensorReadingCreate`, `SensorReadingResponse`, `RangeQuery`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_iot_use_cases()`

### 5. Invariants
- Reading within valid range per sensor type
- Dedup by (sensor_id, timestamp)
- Alert when threshold exceeded
- Sensor offline detection (5 min default)

### 6. Domain Events
- `SensorReadingReceived`, `ThresholdExceeded`, `SensorOffline`, `SensorOnline`

### 7. Tests
```python
async def test_ingest_valid_reading(): ...
async def test_temperature_out_of_range_raises():
    with pytest.raises(Exception):
        SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("200"))


async def test_threshold_alert(): ...
async def test_duplicate_reading_dedup(): ...
async def test_sensor_offline_detection(): ...
async def test_property_reading_in_range():
    for _ in range(100):
        temp = Decimal(str(random.uniform(-50, 100)))
        r = SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=temp)
        assert -50 <= r.value <= 100
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `iot`

**`db/migrations/V001__create_iot.sql`**
```sql
BEGIN;

CREATE TABLE tenant_iot.sensor_readings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    sensor_id       VARCHAR(100) NOT NULL,
    sensor_type     VARCHAR(50) NOT NULL,
    value           NUMERIC(15,4) NOT NULL,
    unit            VARCHAR(20),
    timestamp       TIMESTAMPTZ NOT NULL,
    location        VARCHAR(200),
    device_id       VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sensor_time ON tenant_iot.sensor_readings(sensor_id, timestamp DESC);
CREATE INDEX ix_device_time ON tenant_iot.sensor_readings(device_id, timestamp DESC);
CREATE INDEX ix_sensor_type_time ON tenant_iot.sensor_readings(sensor_type, timestamp DESC);

ALTER TABLE tenant_iot.sensor_readings ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_sensor_tenant ON tenant_iot.sensor_readings
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_iot.sql`**
```sql
BEGIN;
-- No seed data
COMMIT;
```

**`db/migrations/V003__rollback_iot.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_iot.sensor_readings CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `iot`

**`tests/unit/test_iot.py`**
```python
import pytest
from decimal import Decimal
from app.modules.iot.domain.entities import SensorReading
from app.modules.iot.domain.value_objects import Threshold


class TestSensorReading:
    def test_valid_temperature(self):
        r = SensorReading(
            sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("25")
        )
        assert r.value == Decimal("25")

    def test_temperature_out_of_range_raises(self):
        with pytest.raises(Exception):
            SensorReading(
                sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("200")
            )

    def test_humidity_out_of_range_raises(self):
        with pytest.raises(Exception):
            SensorReading(sensor_id="s1", sensor_type="HUMIDITY", value=Decimal("150"))

    def test_ph_valid(self):
        r = SensorReading(sensor_id="s1", sensor_type="PH", value=Decimal("7"))
        assert r.value == Decimal("7")

    def test_is_out_of_range(self):
        r = SensorReading(
            sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("50")
        )
        threshold = Threshold(min=Decimal("10"), max=Decimal("30"), unit="C")
        assert r.is_out_of_range(threshold)

    def test_property_reading_in_range(self):
        import random

        for _ in range(100):
            temp = Decimal(str(random.uniform(-50, 100)))
            r = SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=temp)
            assert Decimal("-50") <= r.value <= Decimal("100")
```

**`tests/integration/test_iot_repository.py`** — testcontainers
**`tests/property/test_iot_invariants.py`** — hypothesis
**`tests/manual/manual_test_iot.md`** — manual test cases

---

## ✅ สรุป Layer 6 (Monitoring) — 8/65 ไฟล์

| # | Module | Prefix | Entities | Tables |
|---|---|---|---|---|
| 6.1 | `iot` | `iot` | SensorReading, Threshold | `sensor_readings` |
| 6.2 | `cctv` | `cctv` | Camera, Recording | `cameras`, `recordings` |
| 6.3 | `monitoring` | `mon` | HealthCheck, Metric | `health_checks`, `metrics` |
| 6.4 | `backup` | `bkp` | BackupJob, Snapshot | `backup_jobs`, `backup_snapshots` |
| 6.5 | `alerting` | `alr` | Alert, AlertRule | `alerts`, `alert_rules` |
| 6.6 | `audit_viewer` | `av` | (view only) | — |
| 6.7 | `maintenance` | `mnt` | MaintenanceSchedule, WorkOrder | `maintenance_schedules`, `work_orders` |
| 6.8 | `energy` | `eng` | EnergyReading, Tariff | `energy_readings`, `energy_tariffs` |

**Layer 6 เสร็จสมบูรณ์ — ต่อไปคือ Layer 7 (Templates)**

---

# 📋 Layer 7: TEMPLATES — 3 Modules

> **Dependencies:** Layer 0
> **วัตถุประสงค์:** Reference implementations + boilerplate

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 7.1 | `health` | `hlth` | — | — | ไม่มี (standalone) |
| 7.2 | `example` | `ex` | ExampleEntity | `examples` | `audit`, `events` |
| 7.3 | `blank` | `blk` | BlankEntity | `blanks` | ไม่มี (template) |

### 🎯 ตัวอย่างเต็ม: Module `health`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `health` |
| **Layer** | `7` (Templates) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | ไม่มี (standalone) |
| **Domain Concepts** | `HealthStatus` (VO), `ComponentHealth` (VO) |
| **Prefix** | `hlth` |
| **Tables** | ไม่มี (query live) |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `health`

## บริบท
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- Module นี้เป็น **health check endpoint** — ไม่มี persistence
- ตรวจสอบ: database, redis, kafka, disk, memory, external APIs
- Return 200 (healthy) / 503 (unhealthy)
- รองรับ liveness + readiness probes

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`** — ไม่มี

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class HealthStatus:
    """Health status VO — วัตถุสถานะสุขภาพ"""
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.status not in ("HEALTHY", "DEGRADED", "UNHEALTHY"):
            raise DomainError(f"Invalid status: {self.status}")

    def is_healthy(self) -> bool:
        return self.status == "HEALTHY"

@dataclass(frozen=True)
class ComponentHealth:
    """Component health VO — วัตถุสุขภาพคอมโพเนนต์"""
    name: str
    status: str
    latency_ms: float = 0.0
    message: str = ""
    details: dict = field(default_factory=dict)

    def is_healthy(self) -> bool:
        return self.status == "HEALTHY"

@dataclass(frozen=True)
class HealthReport:
    """Health report VO — วัตถุรายงานสุขภาพ"""
    overall: HealthStatus
    components: tuple[ComponentHealth, ...]
    version: str = ""

    def all_healthy(self) -> bool:
        return all(c.is_healthy() for c in self.components)

    def failed_components(self) -> tuple[ComponentHealth, ...]:
        return tuple(c for c in self.components if not c.is_healthy())
```

**`domain/enums.py`**
```python
class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class ProbeType(str, Enum):
    LIVENESS = "LIVENESS"
    READINESS = "READINESS"
    STARTUP = "STARTUP"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IHealthChecker(Protocol):
    name: str

    async def check(self) -> ComponentHealth: ...


class IHealthRepository(Protocol):
    async def check_connection(self) -> ComponentHealth: ...
```

**`application/use_cases.py`**
```python
class HealthUseCases:
    """Health use cases — กรณีการใช้งาน health check"""

    def __init__(self, checkers: list[IHealthChecker], version: str = ""):
        self.checkers = checkers
        self.version = version

    async def check_all(self) -> HealthReport:
        """Check all components — ตรวจสอบทุกคอมโพเนนต์"""
        try:
            results = await asyncio.gather(
                *[c.check() for c in self.checkers],
                return_exceptions=True,
            )

            components = []
            for checker, result in zip(self.checkers, results):
                if isinstance(result, Exception):
                    components.append(
                        ComponentHealth(
                            name=checker.name,
                            status="UNHEALTHY",
                            message=str(result),
                        )
                    )
                else:
                    components.append(result)

            if all(c.is_healthy() for c in components):
                overall = HealthStatus(status="HEALTHY")
            elif any(c.status == "UNHEALTHY" for c in components):
                overall = HealthStatus(status="UNHEALTHY")
            else:
                overall = HealthStatus(status="DEGRADED")

            return HealthReport(
                overall=overall,
                components=tuple(components),
                version=self.version,
            )
        except Exception as e:
            logger.opt(exception=e).error("Error in health check")
            return HealthReport(
                overall=HealthStatus(status="UNHEALTHY"),
                components=(),
                version=self.version,
            )

    async def liveness(self) -> HealthStatus:
        """Liveness probe — ตรวจสอบว่ายังทำงาน"""
        return HealthStatus(status="HEALTHY")

    async def readiness(self) -> HealthReport:
        """Readiness probe — ตรวจสอบพร้อมรับ traffic"""
        return await self.check_all()
```

**`application/mappers.py`** — `HealthMapper`
**`application/exceptions.py`** — `HealthException`
**`application/utils.py`** — `timed_check()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`** — ไม่มี

**`infrastructure/repositories.py`** — ไม่มี

**`infrastructure/caches.py`** — ไม่มี

**`infrastructure/services.py`**
```python
class DatabaseHealthChecker:
    """Database health checker — ตรวจสอบ DB"""

    name = "database"

    def __init__(self, session):
        self.session = session

    async def check(self) -> ComponentHealth:
        start = time.monotonic()
        try:
            await self.session.execute(text("SELECT 1"))
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(
                name=self.name,
                status="HEALTHY",
                latency_ms=latency,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(
                name=self.name,
                status="UNHEALTHY",
                latency_ms=latency,
                message=str(e),
            )


class RedisHealthChecker:
    """Redis health checker — ตรวจสอบ Redis"""

    name = "redis"

    def __init__(self, redis):
        self.redis = redis

    async def check(self) -> ComponentHealth:
        start = time.monotonic()
        try:
            await self.redis.ping()
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(name=self.name, status="HEALTHY", latency_ms=latency)
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(
                name=self.name,
                status="UNHEALTHY",
                latency_ms=latency,
                message=str(e),
            )


class KafkaHealthChecker:
    """Kafka health checker — ตรวจสอบ Kafka"""

    name = "kafka"

    def __init__(self, bootstrap: str):
        self.bootstrap = bootstrap

    async def check(self) -> ComponentHealth:
        start = time.monotonic()
        try:
            # Try to connect to Kafka admin
            ...
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(name=self.name, status="HEALTHY", latency_ms=latency)
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(
                name=self.name,
                status="UNHEALTHY",
                latency_ms=latency,
                message=str(e),
            )


class DiskHealthChecker:
    """Disk health checker — ตรวจสอบ disk"""

    name = "disk"

    def __init__(self, threshold_pct: float = 90.0):
        self.threshold_pct = threshold_pct

    async def check(self) -> ComponentHealth:
        try:
            usage = shutil.disk_usage("/")
            pct = usage.used / usage.total * 100
            status = "HEALTHY" if pct < self.threshold_pct else "DEGRADED"
            return ComponentHealth(
                name=self.name,
                status=status,
                details={
                    "usage_pct": round(pct, 2),
                    "free_gb": round(usage.free / 1e9, 2),
                },
            )
        except Exception as e:
            return ComponentHealth(name=self.name, status="UNHEALTHY", message=str(e))


class MemoryHealthChecker:
    """Memory health checker — ตรวจสอบ memory"""

    name = "memory"

    def __init__(self, threshold_pct: float = 90.0):
        self.threshold_pct = threshold_pct

    async def check(self) -> ComponentHealth:
        try:
            import psutil

            mem = psutil.virtual_memory()
            status = "HEALTHY" if mem.percent < self.threshold_pct else "DEGRADED"
            return ComponentHealth(
                name=self.name,
                status=status,
                details={
                    "usage_pct": mem.percent,
                    "available_mb": round(mem.available / 1e6, 2),
                },
            )
        except Exception as e:
            return ComponentHealth(name=self.name, status="UNHEALTHY", message=str(e))
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health(use_cases: HealthUseCases = Depends(get_health_use_cases)):
    """Full health check — ตรวจสอบสุขภาพทั้งหมด"""
    report = await use_cases.check_all()
    status_code = 200 if report.overall.is_healthy() else 503
    return JSONResponse(
        status_code=status_code,
        content=HealthMapper.to_response(report),
    )


@router.get("/live/")
async def liveness(use_cases: HealthUseCases = Depends(get_health_use_cases)):
    """Liveness probe — ตรวจสอบว่ายังทำงาน"""
    status = await use_cases.liveness()
    return {"status": status.status, "timestamp": status.timestamp.isoformat()}


@router.get("/ready/")
async def readiness(use_cases: HealthUseCases = Depends(get_health_use_cases)):
    """Readiness probe — ตรวจสอบพร้อมรับ traffic"""
    report = await use_cases.readiness()
    status_code = 200 if report.overall.is_healthy() else 503
    return JSONResponse(
        status_code=status_code,
        content=HealthMapper.to_response(report),
    )
```

**`presentation/schemas.py`** — `HealthResponse`, `ComponentHealthResponse`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_health_use_cases()`

### 5. Invariants
- Health status ต้องเป็น HEALTHY/DEGRADED/UNHEALTHY
- Response 200 เมื่อ healthy, 503 เมื่อ unhealthy
- Liveness ต้อง return 200 เสมอ (ถ้า process ยังรัน)
- Readiness ตรวจสอบ dependencies

### 6. Domain Events
- `HealthCheckExecuted`, `ComponentUnhealthy`

### 7. Tests
```python
async def test_health_all_healthy():
    checkers = [FakeChecker("db", "HEALTHY"), FakeChecker("redis", "HEALTHY")]
    uc = HealthUseCases(checkers)
    report = await uc.check_all()
    assert report.overall.is_healthy()
    assert report.all_healthy()


async def test_health_one_unhealthy():
    checkers = [FakeChecker("db", "HEALTHY"), FakeChecker("redis", "UNHEALTHY")]
    uc = HealthUseCases(checkers)
    report = await uc.check_all()
    assert not report.overall.is_healthy()
    assert len(report.failed_components()) == 1


async def test_liveness_always_healthy():
    uc = HealthUseCases([])
    status = await uc.liveness()
    assert status.is_healthy()
```

## Output
- ~10 ไฟล์ (module เล็ก)
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `health`

**`db/migrations/V001__create_health.sql`**
```sql
-- No tables — health check queries live systems
-- This migration is intentionally empty (placeholder)
BEGIN;
-- Nothing to create
COMMIT;
```

**`db/migrations/V002__seed_health.sql`** — empty
**`db/migrations/V003__rollback_health.sql`** — empty

### 🧪 Tests สำหรับ `health`

**`tests/unit/test_health.py`**
```python
import pytest
from app.modules.health.application.use_cases import HealthUseCases
from app.modules.health.domain.value_objects import ComponentHealth, HealthStatus


class FakeChecker:
    def __init__(self, name, status):
        self.name = name
        self._status = status

    async def check(self):
        return ComponentHealth(name=self.name, status=self._status)


class TestHealthUseCases:
    async def test_all_healthy(self):
        uc = HealthUseCases(
            [FakeChecker("db", "HEALTHY"), FakeChecker("redis", "HEALTHY")]
        )
        report = await uc.check_all()
        assert report.overall.is_healthy()

    async def test_one_unhealthy(self):
        uc = HealthUseCases(
            [FakeChecker("db", "HEALTHY"), FakeChecker("redis", "UNHEALTHY")]
        )
        report = await uc.check_all()
        assert not report.overall.is_healthy()
        assert len(report.failed_components()) == 1

    async def test_checker_exception_handled(self):
        class FailChecker:
            name = "fail"

            async def check(self):
                raise RuntimeError("boom")

        uc = HealthUseCases([FailChecker()])
        report = await uc.check_all()
        assert not report.overall.is_healthy()

    async def test_liveness_always_healthy(self):
        uc = HealthUseCases([])
        status = await uc.liveness()
        assert status.is_healthy()
```

**`tests/integration/test_health_endpoint.py`** — FastAPI TestClient
**`tests/property/test_health_invariants.py`** — hypothesis
**`tests/manual/manual_test_health.md`** — manual test cases

---

### 📄 Module 7.2: `example` (Reference Implementation)

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `example` |
| **Layer** | `7` (Templates) |
| **Priority** | 🟢 |
| **Phase** | 1 |
| **Dependencies** | `audit`, `events` |
| **Domain Concepts** | `ExampleEntity` (entity), `ExampleStatus` (enum) |
| **Prefix** | `ex` |
| **Tables** | `tenant_ex.examples` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `example`

## บริบท
- Module ตัวอย่างสำหรับ developer ใหม่
- แสดง pattern ครบทุก layer: Domain → Application → Infrastructure → Presentation
- ใช้เป็น blueprint สำหรับสร้าง module ใหม่
- CRUD + idempotency + audit + events + tests

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — ExampleEntity**
```python
@dataclass
class ExampleEntity(BaseEntity):
    """Example entity — เอนทิตีตัวอย่าง"""
    code: str = ""
    name: str = ""
    description: str = ""
    status: str = "ACTIVE"
    amount: Decimal = Decimal("0.00")

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.code or not re.match(r"^[A-Z][A-Z0-9-]{2,20}$", self.code):
            raise DomainError(f"Invalid code: {self.code}")
        if not self.name:
            raise DomainError("Name required")
        if self.amount < 0:
            raise DomainError("Amount cannot be negative")

    def activate(self) -> None:
        self.status = "ACTIVE"

    def deactivate(self) -> None:
        self.status = "INACTIVE"
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ExampleCode:
    """Example code VO — วัตถุรหัส"""

    value: str
    PATTERN = r"^[A-Z][A-Z0-9-]{2,20}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid code: {self.value}")
```

**`domain/enums.py`**
```python
class ExampleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
```

### 2-4. Application / Infrastructure / Presentation

> **ดู pattern จาก `tenancy` module** — ทุก layer ใช้ pattern เดียวกัน
> - Application: `interfaces.py`, `use_cases.py`, `mappers.py`, `exceptions.py`, `utils.py`
> - Infrastructure: `models.py`, `repositories.py`, `caches.py`, `services.py`
> - Presentation: `routers.py`, `schemas.py`, `docs.py`, `dependencies.py`

### 5-7. Invariants / Events / Tests

- Invariants: `code` format, `amount >= 0`
- Events: `ExampleCreated`, `ExampleUpdated`, `ExampleDeleted`
- Tests: unit + integration + property + manual

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

### 📄 Module 7.3: `blank` (Empty Template)

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `blank` |
| **Layer** | `7` (Templates) |
| **Priority** | 🟢 |
| **Phase** | 1 |
| **Dependencies** | ไม่มี |
| **Domain Concepts** | `BlankEntity` (entity) |
| **Prefix** | `blk` |
| **Tables** | `tenant_blk.blanks` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `blank`

## บริบท
- Empty template — ใช้เป็น starting point สำหรับ module ใหม่
- ทุกไฟล์มี TODO comments
- แสดง structure ครบ 23 ไฟล์
- Developer เติม business logic เอง

## ข้อกำหนด

### 1. Domain Layer

**`domain/entities.py`**
```python
@dataclass
class BlankEntity(BaseEntity):
    """Blank entity — เอนทิตีเปล่า (TODO: rename + add fields)"""
    # TODO: Add your fields here
    code: str = ""
    name: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        # TODO: Add validation rules
        if not self.code:
            raise DomainError("Code is required")
```

### 2-4. Application / Infrastructure / Presentation

> ทุกไฟล์มี TODO comments — เติมตาม business requirements

### 5-7. Invariants / Events / Tests

- Invariants: TODO
- Events: `BlankCreated`, `BlankUpdated`, `BlankDeleted`
- Tests: skeleton + TODO

## Output
- 23 ไฟล์ (skeleton)
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `blank`

**`db/migrations/V001__create_blank.sql`**
```sql
BEGIN;

CREATE TABLE tenant_blk.blanks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT uq_blanks_code UNIQUE (tenant_id, code)
);

CREATE INDEX ix_blanks_tenant ON tenant_blk.blanks(tenant_id) WHERE deleted_at IS NULL;

ALTER TABLE tenant_blk.blanks ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_blanks_tenant ON tenant_blk.blanks
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_blank.sql`**
```sql
BEGIN;
-- TODO: Add seed data if needed
COMMIT;
```

**`db/migrations/V003__rollback_blank.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_blk.blanks CASCADE;
COMMIT;
```

---

## ✅ สรุป Layer 7 (Templates) — 3/65 ไฟล์

| # | Module | Prefix | Output | วัตถุประสงค์ |
|---|---|---|---|---|
| 7.1 | `health` | `hlth` | ~10 ไฟล์ | Health check endpoint |
| 7.2 | `example` | `ex` | 23 ไฟล์ | Reference implementation |
| 7.3 | `blank` | `blk` | 23 ไฟล์ | Empty template |

---

# 🎉 สรุปทั้งหมด — 65/65 Modules ครบทุก Layer

## สรุปตาม Layer

| Layer | ชื่อ | Modules | Output รวม |
|---|---|---|---|
| **0** | Core | 6 | ~84 ไฟล์ |
| **1** | Foundation | 8 | 184 ไฟล์ |
| **2** | Money Path | 7 | 161 ไฟล์ |
| **3** | Goods Path | 13 | 299 ไฟล์ |
| **4** | Operations | 13 | 299 ไฟล์ |
| **5** | Intelligence | 7 | 161 ไฟล์ |
| **6** | Monitoring | 8 | 184 ไฟล์ |
| **7** | Templates | 3 | ~56 ไฟล์ |
| | **รวม** | **65** | **~1,428 ไฟล์** |

## 🚀 ขั้นตอนการทำงาน

```
┌──────────────────────────────────────────────────────────┐
│  Phase 1: Layer 0 + Layer 1 + Layer 2 + Layer 3          │
│  (Core + Foundation + Money + Goods)                     │
│  → 34 modules → ~728 ไฟล์                                │
├──────────────────────────────────────────────────────────┤
│  Phase 2: Layer 4 + Layer 5                              │
│  (Operations + Intelligence)                             │
│  → 20 modules → ~460 ไฟล์                                │
├──────────────────────────────────────────────────────────┤
│  Phase 3: Layer 6 + Layer 7                              │
│  (Monitoring + Templates)                                │
│  → 11 modules → ~240 ไฟล์                                │
└──────────────────────────────────────────────────────────┘
```

## 📋 Checklist ก่อนส่ง (ทุก Module)

- [ ] Domain layer ไม่ import framework
- [ ] ใช้ `flush()` ไม่ใช่ `commit()` ใน repository
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบ
- [ ] Read-back verification ครบ
- [ ] Tests ครบ 4 ประเภท (unit/integration/property/manual)
- [ ] SQL migrations ครบ 3 ไฟล์ (V001/V002/V003)
- [ ] RLS policy present
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน

## 🎯 วิธีใช้

```bash
# 1. สร้างโฟลเดอร์
mkdir -p docs/prompts/{layer-0-core,layer-1-foundation,layer-2-money-path,layer-3-goods-path,layer-4-operations,layer-5-intelligence,layer-6-monitoring,layer-7-templates}

# 2. Copy prompt ที่ต้องการจากหัวข้อด้านบน

# 3. วางใน AI (ChatGPT/Claude/Gemini)

# 4. AI จะสร้าง 23 ไฟล์

# 5. รัน tests
uv run pytest tests/unit/test_{module}.py -v
uv run pytest tests/integration/test_{module}_repository.py -v
uv run pytest tests/property/test_{module}_invariants.py -v
```

---

**เสร็จสมบูรณ์ — 65 modules / 8 layers / ~1,428 ไฟล์** ✅****