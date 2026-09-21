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
    async def get(self, key: IdempotencyKey, tenant_id: str) -> IdempotencyRecord | None: ...
    async def set(self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord) -> None: ...
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
                f"{key.redis_key(tenant_id)}:lock",
                "1", nx=True, ex=ttl
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
