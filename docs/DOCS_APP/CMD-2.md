# 📦 Layer 0: CORE — 6 Prompt Files

ด้านล่างคือ AI Prompt ทั้ง 6 ไฟล์ของ **Layer 0 (Core)** ตาม Template มาตรฐาน — แต่ละไฟล์คือ 1 module

---

## 📄 ไฟล์ 1: `docs/prompts/layer-0-core/money.md`

```markdown
# AI Prompt — Module `money`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `money` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `Money` (VO), `Currency` (enum), `VAT` (VO), `ExchangeRate` (VO) |

---

## 🎯 Prompt

### สร้าง Module `money`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- PostgreSQL 17, Redis 8, Kafka
- Module นี้เป็น **primitive module** — ไม่มี persistence, ไม่มี cache
- ใช้ `Decimal` เท่านั้น (ห้ามใช้ `float`)
- Money is Domain Invariant — ต้องแม่นยำ 100%

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`** — ไม่มี (pure VO module)

**`value_objects.py` — Money**
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
        """Validate money — ตรวจสอบเงิน"""
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
        """Check if zero — ตรวจสอบว่าเป็นศูนย์"""
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        """Check if negative — ตรวจสอบว่าติดลบ"""
        return self.amount < Decimal("0.00")
```

**`value_objects.py` — VAT**
```python
@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุภาษีมูลค่าเพิ่ม"""
    rate: Decimal  # e.g., 0.07

    def calculate(self, base: Money) -> Money:
        """Calculate VAT — คำนวณภาษี"""
        return Money((base.amount * self.rate).quantize(Decimal("0.01")), base.currency)

    def extract(self, total: Money) -> Money:
        """Extract VAT from total — แยกภาษีจากยอดรวม"""
        base = (total.amount / (Decimal("1") + self.rate)).quantize(Decimal("0.01"))
        return Money(total.amount - base, total.currency)
```

**`value_objects.py` — ExchangeRate**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`** — Protocol ว่าง (VO module ไม่มี external deps)

**`use_cases.py`**
```python
class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""

    def add(self, a: Money, b: Money) -> Money: return a + b
    def subtract(self, a: Money, b: Money) -> Money: return a - b
    def multiply(self, a: Money, factor: Decimal) -> Money: return a * factor
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

**`mappers.py`** — `MoneyMapper.to_schema()` / `to_entity()`
**`exceptions.py`** — `MoneyException(StandardException)`
**`utils.py`** — `round_money()`, `zero_money(currency)`

#### 3. Infrastructure Layer (`infrastructure/`)
- **ไม่มี** `models.py` (pure VO)
- **ไม่มี** `repositories.py`
- **ไม่มี** `caches.py`
- **ไม่มี** `services.py`

#### 4. Presentation Layer (`presentation/`)

**`schemas.py`**
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

**`routers.py`**
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

**`docs.py`** — `router_docs` + per-endpoint docs
**`dependencies.py`** — `get_money_use_cases()`

#### 5. Error Handling
- Use cases: **3-branch** (`StandardException` → `DomainError` → `Exception`)
- ไม่มี repository/cache → ไม่มี 2-branch / never-raise

#### 6. Invariants
- `Decimal` quantize 2 ตำแหน่ง (ROUND_HALF_UP)
- `a + b == b + a` (commutative)
- `(a + b) + c == a + (b + c)` (associative)
- `a + Money(0) == a` (identity)
- `a - a == Money(0)` (inverse)
- `VAT.calculate(base) + base == VAT.extract(total)` consistency

#### 7. Domain Events
- `MoneyAdded`, `MoneySubtracted`, `VATCalculated`, `CurrencyConverted`

#### 8. Tests
```python
def test_commutative(): assert a + b == b + a
def test_associative(): assert (a+b)+c == a+(b+c)
def test_identity(): assert a + Money(Decimal("0")) == a
def test_currency_mismatch(): pytest.raises(DomainError)
def test_vat_7_percent(): assert VAT(Decimal("0.07")).calculate(Money(Decimal("100"))) == Money(Decimal("7.00"))
def test_vat_extract_roundtrip(): ...
def test_exchange_rate_convert(): ...
def test_negative_money(): assert Money(Decimal("-10")).is_negative()
def test_zero_money(): assert Money(Decimal("0")).is_zero()
```

**Output:**
- ไฟล์ ~8 ไฟล์ (module เล็ก)
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 2: `docs/prompts/layer-0-core/tenant_context.md`

```markdown
# AI Prompt — Module `tenant_context`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `tenant_context` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `TenantContext` (VO), `TenantScope` (enum), `RequestContext` (VO) |

---

## 🎯 Prompt

### สร้าง Module `tenant_context`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Module นี้เป็น **context propagation** — ใช้ `contextvars` แทน global state
- ทุก request ต้องมี `tenant_id`, `user_id`, `correlation_id`
- PostgreSQL schema-per-tenant → ต้อง switch schema ตาม context
- Redis namespace ต้อง prefix ด้วย `tenant_id`
- Kafka topic ต้อง prefix ด้วย `tenant_id`

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`** — ไม่มี (pure VO)

**`value_objects.py` — TenantContext**
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

**`value_objects.py` — RequestContext**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`**
```python
class ITenantContextProvider(Protocol):
    def get(self) -> TenantContext: ...
    def set(self, ctx: TenantContext) -> None: ...
    def clear(self) -> None: ...

class ITenantResolver(Protocol):
    async def resolve(self, identifier: str) -> TenantContext | None: ...
```

**`use_cases.py`**
```python
class TenantContextUseCases:
    """Tenant context use cases — กรณีการใช้งานบริบทผู้เช่า"""

    def __init__(self, resolver: ITenantResolver):
        self.resolver = resolver

    async def establish(self, tenant_id: str, user_id: str | None, headers: dict) -> TenantContext:
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

**`mappers.py`** — `ContextMapper.to_context()` / `to_headers()`
**`exceptions.py`** — `TenantContextException`, `TenantNotFoundInContext`
**`utils.py`** — `requires_tenant()`, `tenant_scoped()`

#### 3. Infrastructure Layer (`infrastructure/`)

**`models.py`** — ไม่มี (context ไม่ persist)

**`repositories.py`** — `PostgresTenantResolver` (query จาก `public.tenants`)
```python
class PostgresTenantResolver:
    """Resolve tenant from DB — ค้นหา tenant จาก DB"""
    def __init__(self, session): self.session = session

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

**`caches.py` — RedisTenantCache**
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
            await self.redis.setex(f"tenant:lookup:{identifier}", 300, json.dumps(asdict(ctx)))
        except Exception as e:
            logger.opt(exception=e).error("Cache insert failed.")
```

**`services.py`** — `HeaderTenantExtractor` (Protocol impl)

#### 4. Presentation Layer (`presentation/`)

**`routers.py`**
```python
router = APIRouter(prefix="/api/v1/context", tags=["Tenant Context"])

@router.get("/current/")
async def get_current(ctx: TenantContext = Depends(get_tenant_context)): ...

@router.post("/switch/")
async def switch_tenant(tenant_id: str, use_cases: TenantContextUseCases = Depends(...)): ...
```

**`schemas.py`** — `TenantContextSchema`, `SwitchTenantRequest`
**`docs.py`** — router_docs
**`dependencies.py`** — `get_tenant_context()` (FastAPI dependency)

#### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

#### 6. Invariants
- ทุก request ต้องมี `tenant_id` + `correlation_id`
- Context ถูก propagate ผ่าน `contextvars` (async-safe)
- `schema_name == f"tenant_{tenant_id}"`
- Redis keys ขึ้นต้นด้วย `t:{tenant_id}:` เสมอ

#### 7. Domain Events
- `TenantContextEstablished`, `TenantContextCleared`, `TenantSwitched`

#### 8. Tests
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

**Output:**
- ไฟล์ ~12 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 3: `docs/prompts/layer-0-core/audit.md`

```markdown
# AI Prompt — Module `audit`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `audit` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `AuditLog` (entity), `AuditAction` (enum), `ChangeSet` (VO) |

---

## 🎯 Prompt

### สร้าง Module `audit`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- **ทุก action ที่แตะเงิน/สต็อก/ข้อมูลสำคัญ → audit log (append-only)**
- Audit log ต้อง **immutable** — ห้าม UPDATE / DELETE
- ต้องเก็บ `before` / `after` state (ChangeSet)
- Audit log ต้องเป็น event-sourced เพื่อให้ replay ได้
- Retention: 7 ปี (ตามกฎหมายบัญชี)

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`**
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

**`value_objects.py`**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`**
```python
class IAuditRepository(Protocol):
    async def append(self, log: AuditLog) -> AuditLog: ...
    async def query(self, filters: dict, page: int, limit: int) -> tuple[list[AuditLog], int]: ...

class IAuditCache(Protocol):
    async def get(self, id: str) -> AuditLog | None: ...
    async def insert(self, id: str, log: AuditLog) -> None: ...

class IAuditPublisher(Protocol):
    async def publish(self, log: AuditLog) -> None: ...
```

**`use_cases.py`**
```python
class AuditUseCases:
    """Audit use cases — กรณีการใช้งาน audit"""

    def __init__(self, repo, cache, publisher, events):
        self.repo = repo
        self.cache = cache
        self.publisher = publisher
        self.events = events

    async def log(self, action: str, resource_type: str, resource_id: str,
                  before: dict, after: dict) -> AuditLog:
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

**`mappers.py`** — `AuditMapper`
**`exceptions.py`** — `AuditException`, `AuditImmutableViolation`
**`utils.py`** — `auditable()` decorator, `diff_states()`

#### 3. Infrastructure Layer (`infrastructure/`)

**`models.py`**
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

**`repositories.py`** — `PostgresAuditRepository` (`append()` only — no update/delete)
**`caches.py`** — `RedisAuditCache` (read-through, never raises)
**`services.py`** — `AuditPublisher` (Kafka topic `audit.events`)

#### 4. Presentation Layer (`presentation/`)

**`routers.py`**
```python
router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

@router.get("/logs/")      # list + filters
async def list_logs(filters: AuditQuery, ...): ...

@router.get("/logs/{id}/")
async def get_log(id: str, ...): ...

@router.get("/resources/{type}/{id}/history/")
async def resource_history(type: str, id: str, ...): ...
```

**`schemas.py`** — `AuditLogSchema`, `AuditQuery`, `AuditLogPage`
**`docs.py`** — router_docs
**`dependencies.py`** — `get_audit_use_cases()`

#### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

#### 6. Invariants
- Audit log **immutable** — append-only
- ทุก log ต้องมี `actor_id`, `correlation_id`, `occurred_at`
- `diff()` ต้องตรงกับ `before`/`after`
- Retention 7 ปี — ห้ามลบก่อนกำหนด

#### 7. Domain Events
- `AuditLogged`, `AuditQueryExecuted`

#### 8. Tests
```python
async def test_append_only(): ...       # ลอง update ต้อง raise
async def test_diff_accuracy(): ...     # diff ต้องตรง
async def test_actor_required(): ...
async def test_property_diff_symmetric():
    """Property: diff(before, after) == -diff(after, before)"""
    ...
```

**Output:**
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 4: `docs/prompts/layer-0-core/idempotency.md`

```markdown
# AI Prompt — Module `idempotency`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `idempotency` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context`, `config` |
| **Domain Concepts** | `IdempotencyKey` (VO), `IdempotencyRecord` (entity), `IdempotencyStatus` (enum) |

---

## 🎯 Prompt

### สร้าง Module `idempotency`

**บริบท:**
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

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`**
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

**`value_objects.py`**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`**
```python
class IIdempotencyStore(Protocol):
    async def get(self, key: IdempotencyKey, tenant_id: str) -> IdempotencyRecord | None: ...
    async def set(self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord) -> None: ...
    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool: ...
    async def unlock(self, key: IdempotencyKey, tenant_id: str) -> None: ...
```

**`use_cases.py`**
```python
class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency"""

    def __init__(self, store, config):
        self.store = store
        self.ttl = config.IDEMPOTENCY_TTL_SECONDS

    async def check_or_lock(self, raw_key: str, scope: str, payload: dict) -> IdempotencyRecord | None:
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

**`mappers.py`** — `IdempotencyMapper`
**`exceptions.py`** — `IdempotencyException`, `IdempotencyConflictException`
**`utils.py`** — `idempotent()` decorator

#### 3. Infrastructure Layer (`infrastructure/`)

**`models.py`**
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

**`repositories.py`** — `PostgresIdempotencyRepository` (fallback เมื่อ Redis ล่ม)
**`caches.py`** — `RedisIdempotencyStore` (primary, atomic SET NX)
```python
class RedisIdempotencyStore:
    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool:
        try:
            result = await self.redis.set(
                f"{key.redis_key(tenant_id)}:lock",
                "1", nx=True, ex=ttl
            )
            return bool(result)
        except Exception as e:
            logger.opt(exception=e).error("Lock failed")
            return False  # conservative: fail closed
```

**`services.py`** — ไม่มี

#### 4. Presentation Layer (`presentation/`)

**`routers.py`** — ไม่มี public router (ใช้ middleware/dependency)
**`schemas.py`** — `IdempotencyRecordSchema`
**`docs.py`** — docs
**`dependencies.py`** — `require_idempotency_key()` FastAPI dependency

#### 5. Error Handling
- Use cases: **3-branch**
- Store: **2-branch** (Redis), **never-raise** (fallback logging)

#### 6. Invariants
- Key + Scope + Tenant = unique
- `COMPLETED` record ต้อง return response เดิมเสมอ
- Payload hash ต้องตรงกัน ไม่งั้น 422
- Concurrent requests → 1 success, rest 409

#### 7. Domain Events
- `IdempotencyLocked`, `IdempotencyCompleted`, `IdempotencyConflict`

#### 8. Tests
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

**Output:**
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 5: `docs/prompts/layer-0-core/config.md`

```markdown
# AI Prompt — Module `config`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `config` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `ConfigEntry` (entity), `ConfigScope` (enum), `ConfigType` (enum) |

---

## 🎯 Prompt

### สร้าง Module `config`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Config มี 3 ระดับ: **GLOBAL → TENANT → USER** (override ตามลำดับ)
- รองรับ hot-reload ผ่าน Redis Pub/Sub
- Type-safe: `string`, `int`, `decimal`, `bool`, `json`, `secret`
- Secret ต้องเข้ารหัส (Fernet) และไม่ return ผ่าน API
- Cache ที่ Redis พร้อม TTL + tombstone

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`**
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

**`value_objects.py`**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`**
```python
class IConfigRepository(Protocol):
    async def get(self, key: str, scope: str, scope_id: str) -> ConfigEntry | None: ...
    async def get_effective(self, key: str, tenant_id: str, user_id: str | None) -> ConfigEntry | None: ...
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

**`use_cases.py`**
```python
class ConfigUseCases:
    """Config use cases — กรณีการใช้งาน config"""

    def __init__(self, repo, cache, cipher, events, config):
        ...

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

    async def set(self, key: str, value: str, value_type: str, scope: str,
                  scope_id: str, is_secret: bool = False) -> ConfigEntry:
        """Set config — ตั้งค่า config"""
        try:
            if is_secret:
                value = self.cipher.encrypt(value)
            entry = ConfigEntry(
                key=key, value=value, value_type=value_type,
                scope=scope, scope_id=scope_id, is_secret=is_secret,
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

**`mappers.py`** — `ConfigMapper` (with mask)
**`exceptions.py`** — `ConfigException`, `ConfigKeyNotFoundException`
**`utils.py`** — `get_config(key, default)` helper

#### 3. Infrastructure Layer (`infrastructure/`)

**`models.py`**
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

**`repositories.py`** — `PostgresConfigRepository` (with 3-level override)
**`caches.py`** — `RedisConfigCache` (TTL 300s, tombstone, never raises)
**`services.py`**
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

#### 4. Presentation Layer (`presentation/`)

**`routers.py`**
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

**`schemas.py`** — `ConfigEntrySchema`, `ConfigSetRequest` (mask secrets)
**`docs.py`** — router_docs
**`dependencies.py`** — `get_config_use_cases()`

#### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

#### 6. Invariants
- 3-level override: `USER` > `TENANT` > `GLOBAL`
- Secret values **ไม่ return ผ่าน API** (mask)
- Config key format: `^[a-z][a-z0-9_.]*$`
- Cache invalidation ต้อง propagate ทันที

#### 7. Domain Events
- `ConfigChanged`, `ConfigDeleted`, `ConfigReloaded`

#### 8. Tests
```python
async def test_override_precedence(): ...
async def test_secret_encrypted_at_rest(): ...
async def test_secret_masked_in_api(): ...
async def test_invalid_key_format_raises(): ...
async def test_property_override_order():
    """Property: user > tenant > global เสมอ"""
    ...
```

**Output:**
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 6: `docs/prompts/layer-0-core/events.md`

```markdown
# AI Prompt — Module `events`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `events` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context`, `audit` |
| **Domain Concepts** | `DomainEvent` (VO), `EventEnvelope` (VO), `EventStatus` (enum) |

---

## 🎯 Prompt

### สร้าง Module `events`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Kafka-based event bus
- **At-least-once delivery** + **consumer idempotency**
- Event envelope ต้องมี: `event_id`, `tenant_id`, `correlation_id`, `occurred_at`, `version`
- Event schema ต้อง versioned (backward-compatible)
- Dead Letter Queue (DLQ) สำหรับ poison messages
- Retry: exponential backoff (1s → 2s → 4s → 8s → 16s → DLQ)

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)

**`entities.py`** — ไม่มี (event เป็น VO)

**`value_objects.py` — DomainEvent**
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

**`value_objects.py` — EventEnvelope**
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

**`enums.py`**
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

#### 2. Application Layer (`application/`)

**`interfaces.py`**
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

**`use_cases.py`**
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
        delay = 2 ** envelope.retry_count
        await asyncio.sleep(delay)
        envelope.retry_count += 1
        await self.bus.publish(envelope)  # republish

    async def _to_dlq(self, envelope: EventEnvelope) -> None:
        """Send to DLQ — ส่งไป DLQ"""
        await self.bus.publish_to_dlq(envelope)
```

**`mappers.py`** — `EventMapper`
**`exceptions.py`** — `EventException`, `EventHandlerNotFoundException`, `EventSerializationException`
**`utils.py`** — `@event_handler("EventType")` decorator

#### 3. Infrastructure Layer (`infrastructure/`)

**`models.py`**
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

**`repositories.py`** — `PostgresEventStore` (append-only, dedup by event_id)
**`caches.py`** — `RedisEventCache` (dedup bloom filter, never raises)
**`services.py`**
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
        await self.producer.send_and_wait("dlq.events", json.dumps(asdict(envelope)).encode())

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

#### 4. Presentation Layer (`presentation/`)

**`routers.py`**
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

**`schemas.py`** — `EventSchema`, `EventQuery`, `EventPage`
**`docs.py`** — router_docs
**`dependencies.py`** — `get_event_use_cases()`

#### 5. Error Handling
- Use cases: **3-branch**
- Bus / Store: **2-branch**
- Cache: **never-raise**

#### 6. Invariants
- `event_id` unique (dedup)
- At-least-once delivery + consumer idempotent
- Retry: exponential backoff สูงสุด 5 ครั้ง → DLQ
- Event schema backward-compatible (versioned)
- ทุก event มี `tenant_id` + `correlation_id`

#### 7. Domain Events (Meta)
- `EventPublished`, `EventConsumed`, `EventFailed`, `EventDeadLettered`

#### 8. Tests
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

**Output:**
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## ✅ สรุป Layer 0 (Core) — 6/65 ไฟล์

| # | Module | ไฟล์ | สถานะ |
|---|---|---|---|
| 1 | `money` | `docs/prompts/layer-0-core/money.md` | ✅ |
| 2 | `tenant_context` | `docs/prompts/layer-0-core/tenant_context.md` | ✅ |
| 3 | `audit` | `docs/prompts/layer-0-core/audit.md` | ✅ |
| 4 | `idempotency` | `docs/prompts/layer-0-core/idempotency.md` | ✅ |
| 5 | `config` | `docs/prompts/layer-0-core/config.md` | ✅ |
| 6 | `events` | `docs/prompts/layer-0-core/events.md` | ✅ |

---

## 📌 แผนถัดไป

Layer 0 เสร็จแล้ว ✅ — ต่อไปคือ:

- **Layer 1: Foundation** (8 modules): `tenancy`, `authentication`, `user`, `employee`, `customer`, `supplier`, `product`, `pricing`
- **Layer 2: Money Path** (7 modules): `order`, `invoice`, `ledger`, `payment`, `accounting_gateway`, `tax`, `reconciliation`
- **Layer 3: Goods Path** (13 modules)
- **Layer 4: Operations** (13 modules)
- **Layer 5: Intelligence** (7 modules)
- **Layer 6: Monitoring** (8 modules)
- **Layer 7: Templates** (3 modules)

**ต้องการให้ผมสร้าง Layer 1 (8 ไฟล์) ต่อเลยไหมครับ?** พิมพ์ "ต่อ Layer 1" หรือ "continue" เพื่อดำเนินการต่อ

> หมายเหตุ: เนื่องจากข้อจำกัดความยาวของข้อความ ผมแนะนำให้ทำทีละ Layer เพื่อให้ไฟล์มีคุณภาพครบถ้วนตาม Template