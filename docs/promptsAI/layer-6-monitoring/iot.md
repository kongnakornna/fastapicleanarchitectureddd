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
    async def get_range(self, sensor_id: str, from_dt: datetime, to_dt: datetime) -> list[SensorReading]: ...

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

    def __init__(self, repo, cache, threshold_repo, alerting, ts_store,
                 idempotency, audit, events):
        ...

    async def ingest_reading(self, payload: dict, idem_key: str) -> SensorReading:
        """Ingest sensor reading — รับค่าจากเซ็นเซอร์"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            reading = SensorReading(**payload)

            # Dedup check
            if await self.cache.is_duplicate(reading.sensor_id, reading.timestamp):
                logger.info(f"Duplicate reading {reading.sensor_id}@{reading.timestamp}")
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
                await self.events.publish("ThresholdExceeded", {
                    "sensor_id": reading.sensor_id,
                    "value": str(reading.value),
                    "threshold_min": str(threshold.min),
                    "threshold_max": str(threshold.max),
                })

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

    async def get_range(self, sensor_id: str, from_dt: datetime, to_dt: datetime) -> list[SensorReading]:
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

    async def query_range(self, sensor_id: str, from_dt: datetime, to_dt: datetime) -> list:
        ...
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
        r = SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("25"))
        assert r.value == Decimal("25")

    def test_temperature_out_of_range_raises(self):
        with pytest.raises(Exception):
            SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("200"))

    def test_humidity_out_of_range_raises(self):
        with pytest.raises(Exception):
            SensorReading(sensor_id="s1", sensor_type="HUMIDITY", value=Decimal("150"))

    def test_ph_valid(self):
        r = SensorReading(sensor_id="s1", sensor_type="PH", value=Decimal("7"))
        assert r.value == Decimal("7")

    def test_is_out_of_range(self):
        r = SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("50"))
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
