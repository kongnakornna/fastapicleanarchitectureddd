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
    async def query(self, filters: dict, page: int, limit: int) -> tuple[list[AuditLog], int]: ...

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
async def test_append_only(): ...       # ลอง update ต้อง raise
async def test_diff_accuracy(): ...     # diff ต้องตรง
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
