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
                    components.append(ComponentHealth(
                        name=checker.name,
                        status="UNHEALTHY",
                        message=str(result),
                    ))
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
                name=self.name, status="HEALTHY", latency_ms=latency,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return ComponentHealth(
                name=self.name, status="UNHEALTHY",
                latency_ms=latency, message=str(e),
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
                name=self.name, status="UNHEALTHY",
                latency_ms=latency, message=str(e),
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
                name=self.name, status="UNHEALTHY",
                latency_ms=latency, message=str(e),
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
                name=self.name, status=status,
                details={"usage_pct": round(pct, 2), "free_gb": round(usage.free / 1e9, 2)},
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
                name=self.name, status=status,
                details={"usage_pct": mem.percent, "available_mb": round(mem.available / 1e6, 2)},
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
        uc = HealthUseCases([FakeChecker("db", "HEALTHY"), FakeChecker("redis", "HEALTHY")])
        report = await uc.check_all()
        assert report.overall.is_healthy()

    async def test_one_unhealthy(self):
        uc = HealthUseCases([FakeChecker("db", "HEALTHY"), FakeChecker("redis", "UNHEALTHY")])
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
