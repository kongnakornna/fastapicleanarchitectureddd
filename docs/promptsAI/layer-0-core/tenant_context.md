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

**`application/mappers.py`** — `ContextMapper.to_context()` / `to_headers()`
**`application/exceptions.py`** — `TenantContextException`, `TenantNotFoundInContext`
**`application/utils.py`** — `requires_tenant()`, `tenant_scoped()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`** — ไม่มี (context ไม่ persist)

**`infrastructure/repositories.py` — PostgresTenantResolver**
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
            await self.redis.setex(f"tenant:lookup:{identifier}", 300, json.dumps(asdict(ctx)))
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
async def switch_tenant(tenant_id: str, use_cases: TenantContextUseCases = Depends(...)): ...
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
