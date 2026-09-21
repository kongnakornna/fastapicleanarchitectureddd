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
        delay = 2 ** envelope.retry_count
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
