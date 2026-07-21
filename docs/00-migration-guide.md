# Go -> Python Migration Guide
## ICMON (IoT Monitoring) System Migration

---

## 1. Overview

### Source: Go (`icmongolang`)
### Target: Python/FastAPI (`fastapiddd`)

| Aspect | Go | Python |
|--------|-----|--------|
| Framework | Chi router | FastAPI |
| ORM | GORM + raw SQL | SQLAlchemy 2.0 (async) |
| DB | PostgreSQL | PostgreSQL 17 |
| Cache | go-redis | redis-py (async) |
| MQTT | paho.mqtt.golang | asyncio-mqtt / paho-mqtt |
| InfluxDB | influxdb-client-go v2 | influxdb-client-python v2 |
| Queue | Custom Redis queue | Celery / ARQ / custom |
| Auth | JWT (custom) | JWT (jwcrypto + nested JWS/JWE) |
| Config | Viper | pydantic-settings |
| Logging | Custom logger | Loguru |
| Validation | go-playground/validator | Pydantic v2 |

---

## 2. Module Mapping

### 2.1 Internal Modules

```
Go (icmongolang)                          Python (fastapiddd)
─────────────────────────────────────────────────────────────
internal/modules/iot/                →   app/modules/iot/ (NEW)
  ├── delivery/http/handler.go       →   ├── presentation/router.py
  ├── delivery/http/routes.go        │   │
  ├── usecase/usecase.go             →   ├── application/use_case.py
  ├── repository/                    →   ├── infrastructure/
  │   ├── device_repo.go             │   │   ├── device_repository.py
  │   ├── device_config_repo.go      │   │   ├── device_config_repository.py
  │   ├── device_status_repo.go      │   │   ├── device_status_repository.py
  │   ├── device_alert_repo.go       │   │   ├── device_alert_repository.py
  │   ├── iot_data_repo.go           │   │   ├── iot_data_repository.py
  │   ├── alarm_log_repo.go          │   │   ├── alarm_log_repository.py
  │   ├── activity_log_repo.go       │   │   └── activity_log_repository.py
  │   └── schedule_repo.go           │   │   └── schedule_repository.py
  ├── models/                        →   ├── domain/
  │   ├── device.go                  │   │   ├── entities/
  │   ├── device_config.go           │   │   │   ├── device.py
  │   ├── device_status.go           │   │   │   ├── device_config.py
  │   ├── device_alert.go            │   │   │   ├── device_status.py
  │   ├── iot_data.go                │   │   │   ├── device_alert.py
  │   ├── alarm_log.go               │   │   │   ├── iot_data.py
  │   ├── activity_log.go            │   │   │   ├── alarm_log.py
  │   ├── schedule.go                │   │   │   ├── activity_log.py
  │   ├── alarm.go                   │   │   │   └── schedule.py
  │   ├── mqtt.go                    │   │   ├── value_objects/
  │   ├── location.go                │   │   │   ├── alarm.py
  │   └── common.go                  │   │   │   ├── mqtt.py
  ├── iothelper/                     │   │   │   ├── location.py
  │   └── alarm.go                   │   │   │   └── sensor.py
  └── presenter/                     →   └── presentation/
      └── presenter.go               │       ├── schemas.py
                                      │       └── router.py

internal/modules/queue/             →   app/core/queue/ (NEW)
  ├── manager.go                     →   ├── manager.py
  └── noop_queue.go                  │   └── noop_queue.py

internal/modules/influxdb/          →   (pkg/influxdb/ moved)
internal/modules/mqtt/              →   (pkg/mqtt/ moved)
```

### 2.2 Package Layer Mapping

```
Go (icmongolang/pkg)                  Python (fastapiddd)
─────────────────────────────────────────────────────────────
pkg/influxdb/client.go              →   app/core/influxdb_client.py
pkg/mqtt/client.go                  →   app/core/mqtt_client.py
pkg/httpErrors/httpErrors.go        →   app/modules/shared/exceptions.py (MERGE)
pkg/utils/validator.go              →   app/core/ (Pydantic handles)
pkg/utils/form.go                   →   app/core/ (FastAPI handles)
pkg/helpers/iot.go                  →   app/modules/iot/domain/helpers/alarm.py
```

---

## 3. Project Structure (Target)

```
fastapiddd/
├── app/
│   ├── __init__.py
│   ├── app.py                          # FastAPI app factory
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                   # Settings (pydantic-settings)
│   │   ├── database.py                 # SQLAlchemy async engine
│   │   ├── influxdb_client.py          # ← NEW from pkg/influxdb
│   │   ├── mqtt_client.py             # ← NEW from pkg/mqtt
│   │   ├── queue/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py             # ← NEW from internal/modules/queue
│   │   │   └── noop_queue.py          # ← NEW from internal/modules/queue
│   │   ├── redis.py
│   │   ├── security.py
│   │   ├── key_management.py
│   │   ├── logging.py
│   │   ├── middleware.py
│   │   ├── exception_handler.py
│   │   ├── resources.py
│   │   └── migrations.py
│   └── modules/
│       ├── shared/                     # ← MERGE httpErrors here
│       │   ├── exceptions.py           # Unified error handling
│       │   ├── schemas.py
│       │   └── base.py
│       ├── authentication/
│       ├── user/
│       ├── health/
│       ├── example/
│       ├── blank/
│       └── iot/                        # ← NEW MODULE
│           ├── __init__.py
│           ├── domain/
│           │   ├── __init__.py
│           │   ├── entities/
│           │   │   ├── __init__.py
│           │   │   ├── device.py
│           │   │   ├── device_config.py
│           │   │   ├── device_status.py
│           │   │   ├── device_alert.py
│           │   │   ├── iot_data.py
│           │   │   ├── alarm_log.py
│           │   │   ├── activity_log.py
│           │   │   └── schedule.py
│           │   ├── value_objects/
│           │   │   ├── __init__.py
│           │   │   ├── alarm.py
│           │   │   ├── mqtt.py
│           │   │   └── location.py
│           │   └── helpers/
│           │       └── alarm_logic.py
│           ├── application/
│           │   ├── __init__.py
│           │   └── use_case.py
│           ├── infrastructure/
│           │   ├── __init__.py
│           │   ├── device_repository.py
│           │   ├── device_config_repository.py
│           │   ├── device_status_repository.py
│           │   ├── device_alert_repository.py
│           │   │   ├── iot_data_repository.py
│           │   │   ├── alarm_log_repository.py
│           │   │   ├── activity_log_repository.py
│           │   │   └── schedule_repository.py
│           └── presentation/
│               ├── __init__.py
│               ├── router.py
│               └── schemas.py
├── migrations/                         # Alembic
├── test/
├── docs/                               # ← YOU ARE HERE
└── docker-compose.yaml
```

---

## 4. Database Setup

详见 [01-database-setup.md](./01-database-setup.md)

---

## 5. Dependencies to Add

### pyproject.toml

```toml
dependencies = [
    # ... existing deps ...
    "influxdb-client[async]>=1.40.0",     # InfluxDB
    "paho-mqtt>=2.1.0",                   # MQTT client
    "asyncio-mqtt>=0.16.2",               # Async MQTT wrapper
    "celery[redis]>=5.4.0",               # Task queue (alternative: arq)
]
```

### Environment Variables (.env additions)

```env
# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=your-bucket
INFLUXDB_TIMEOUT=30

# MQTT
MQTT_BROKER=tcp://localhost:1883
MQTT_CLIENT_ID=fastapi-iot-client
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=30
MQTT_CLEAN_SESSION=true

# Queue (if using Celery)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

---

## 6. API Endpoint Mapping

### Go Chi Routes -> FastAPI Router

```python
# Go: internal/modules/iot/delivery/http/routes.go
# Chi Router → FastAPI APIRouter

from fastapi import APIRouter
from app.modules.iot.presentation.router import router as iot_router

router = APIRouter()
router.include_router(iot_router, prefix="/api/v1/iot", tags=["IoT"])
```

### Endpoints

| Go Method | Go Path | Python Path | Description |
|-----------|---------|-------------|-------------|
| GET | /mqtt3/topic-data | /mqtt3/topic-data | Get MQTT topic data |
| POST | /mqtt3/device-control | /mqtt3/device-control | Control device |
| POST | /mqtt3/device-controls | /mqtt3/device-controls | Control multiple devices |
| GET | /mqtt3/device-list | /mqtt3/device-list | List devices |
| GET | /mqtt3/device-list-page | /mqtt3/device-list-page | Paginated devices |
| GET | /mqtt3/senser-charts | /mqtt3/senser-charts | Sensor chart data |
| GET | /mqtt3/senser-data | /mqtt3/senser-data | Sensor data |
| GET | /mqtt3/device-senser-charts | /mqtt3/device-senser-charts | Device sensor charts |
| GET | /mqtt3/alarm-device-status | /mqtt3/alarm-device-status | Alarm status |
| GET | /mqtt3/monitor-device-group | /mqtt3/monitor-device-group | Monitor grouped devices |
| GET | /mqtt3/monitor-device-chart | /mqtt3/monitor-device-chart | Monitor chart |
| GET | /mqtt3/topic-data-device-chart | /mqtt3/topic-data-device-chart | Topic data chart |
| GET | /mqtt3/device-status/{id} | /mqtt3/device-status/{id} | Device status |
| PATCH | /mqtt3/device-status/{id} | /mqtt3/device-status/{id} | Update device status |
| GET | /mqtt3/device-config/{id} | /mqtt3/device-config/{id} | Device config |
| PATCH | /mqtt3/device-config/{id} | /mqtt3/device-config/{id} | Update device config |
| POST | /mqtt3/process-mqtt-data | /mqtt3/process-mqtt-data | Process MQTT data |
| GET | /mqtt3/latest-data | /mqtt3/latest-data | Latest IoT data |
| GET | /mqtt3/data-by-range | /mqtt3/data-by-range | Data by date range |
| GET | /mqtt3/list-iot-data | /mqtt3/list-iot-data | List IoT data |
| GET | /mqtt3/device-stats | /mqtt3/device-stats | Device statistics |
| POST | /mqtt3/export-data | /mqtt3/export-data | Export data |
| DELETE | /mqtt3/cleanup-old | /mqtt3/cleanup-old | Cleanup old data |

---

## 7. Key Go -> Python Code Patterns

### 7.1 Error Handling

```go
// Go: pkg/httpErrors
restErr := httpErrors.ErrNotFound(errors.New("device not found"))
```

```python
# Python: app/modules/shared/exceptions.py
from app.modules.shared.exceptions import NotFoundException
raise NotFoundException(detail="device not found")
```

### 7.2 Repository Pattern

```go
// Go: GORM
type DeviceRepo struct { db *gorm.DB }
func (r *DeviceRepo) FindByID(id int) (*models.Device, error) {
    var device models.Device
    err := r.db.Where("id = ?", id).First(&device).Error
    return &device, err
}
```

```python
# Python: SQLAlchemy 2.0 async
class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, device_id: int) -> Device | None:
        result = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()
```

### 7.3 MQTT Client

```go
// Go: paho.mqtt.golang
client := mqtt.NewClient(opts)
token := client.Connect()
token.Wait()
client.Publish(topic, qos, retained, payload)
```

```python
# Python: asyncio-mqtt or paho-mqtt
import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, port, keepalive)
client.publish(topic, payload, qos, retain)
```

### 7.4 InfluxDB Query

```go
// Go: influxdb-client-go v2
queryAPI := client.QueryAPI(org)
result, err := queryAPI.Query(ctx, fluxQuery)
```

```python
# Python: influxdb-client-python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()
tables = query_api.query(flux_query, org=org)
```

### 7.5 Queue Manager

```go
// Go: custom Redis queue
type RedisQueue struct {
    client     *redis.Client
    topic      string
    maxRetries int
}
```

```python
# Python: Celery or custom
from celery import Celery

app = Celery('iot_queue', broker='redis://localhost:6379/1')

@app.task(bind=True, max_retries=3)
def process_mqtt_message(self, topic: str, payload: dict):
    try:
        # process...
    except Exception as exc:
        self.retry(exc=exc, countdown=5)
```

---

## 8. Database Tables (New for IoT)

The IoT module requires these additional PostgreSQL tables:

```sql
-- See 01-database-setup.md for full DDL
- devices
- device_configs
- device_statuses
- device_alerts
- iot_data
- alarm_logs
- activity_logs
- schedules
- command_logs
- device_status_histories
```

InfluxDB remains as-is for time-series sensor data (not migrated to PostgreSQL).

---

## 9. Migration Order

### Phase 1: Core Infrastructure
1. Add new dependencies (influxdb-client, paho-mqtt, asyncio-mqtt)
2. Create `app/core/influxdb_client.py`
3. Create `app/core/mqtt_client.py`
4. Create `app/core/queue/` module

### Phase 2: IoT Domain
5. Create `app/modules/iot/domain/entities/` (all models)
6. Create `app/modules/iot/domain/value_objects/`
7. Create `app/modules/iot/domain/helpers/alarm_logic.py`
8. Create `app/modules/iot/infrastructure/` (all repositories)
9. Create `app/modules/iot/application/use_case.py`
10. Create `app/modules/iot/presentation/schemas.py`
11. Create `app/modules/iot/presentation/router.py`

### Phase 3: Database & Migrations
12. Create Alembic migrations for new tables
13. Seed data scripts

### Phase 4: Integration
14. Wire up dependencies (FastAPI Depends)
15. Register router in app.py
16. Integration testing

---

## 10. Notes

- **InfluxDB** data stays in InfluxDB (time-series). Do NOT migrate to PostgreSQL.
- **Redis cache** pattern is preserved. Go's `go-redis` maps to Python's `redis-py`.
- **MQTT** uses same broker. Only client library changes.
- **Auth/JWT** is already built in fastapiddd. No need to port from Go.
- **Validation** uses Pydantic v2 instead of go-playground/validator.
- **Logging** uses Loguru instead of custom Go logger.
