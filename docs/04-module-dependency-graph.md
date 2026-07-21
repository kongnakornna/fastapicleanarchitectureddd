# Module Dependency Graph
## Go -> Python Component Dependencies

---

## 1. Go Module Dependencies (Source)

```
icmongolang/
├── main.go
│   └── depends on: config, internal/modules/*
│
├── config/
│   └── depends on: viper, env
│
├── internal/modules/iot/
│   ├── delivery/http/
│   │   ├── handler.go ──→ usecase, presenter, httpErrors
│   │   └── routes.go ──→ handler
│   │
│   ├── usecase/
│   │   └── usecase.go ──→ repository, mqtt, influxdb, redis, iothelper, helpers, config
│   │
│   ├── repository/
│   │   ├── device_repo.go ──→ models, gorm
│   │   ├── device_config_repo.go ──→ models, gorm
│   │   ├── device_status_repo.go ──→ models, gorm
│   │   ├── device_alert_repo.go ──→ models, gorm
│   │   ├── iot_data_repo.go ──→ models, gorm
│   │   ├── alarm_log_repo.go ──→ models, gorm
│   │   ├── activity_log_repo.go ──→ models, gorm
│   │   └── schedule_repo.go ──→ models, gorm
│   │
│   ├── models/
│   │   └── * (44 files) ──→ gorm
│   │
│   ├── iothelper/
│   │   └── alarm.go ──→ helpers
│   │
│   └── presenter/
│       └── presenter.go ──→ (standalone DTOs)
│
├── internal/modules/queue/
│   ├── manager.go ──→ redis
│   └── noop_queue.go ──→ (standalone)
│
├── pkg/
│   ├── influxdb/
│   │   └── client.go ──→ influxdb-client-go, config, logger
│   │
│   ├── mqtt/
│   │   └── client.go ──→ paho.mqtt.golang, config, logger
│   │
│   ├── httpErrors/
│   │   └── httpErrors.go ──→ gorm, errors
│   │
│   ├── utils/
│   │   ├── validator.go ──→ go-playground/validator
│   │   └── form.go ──→ net/http, encoding/json
│   │
│   └── helpers/
│       └── iot.go ──→ (standalone, no deps)
```

---

## 2. Python Module Dependencies (Target)

```
fastapiddd/
├── app.py
│   └── depends on: core/*, modules/*
│
├── core/
│   ├── config.py
│   │   └── depends on: pydantic-settings, dotenv
│   │
│   ├── database.py
│   │   └── depends on: sqlalchemy, asyncpg, config
│   │
│   ├── influxdb_client.py (NEW)
│   │   └── depends on: influxdb-client, config, logger
│   │
│   ├── mqtt_client.py (NEW)
│   │   └── depends on: paho-mqtt, asyncio-mqtt, config, logger
│   │
│   ├── queue/ (NEW)
│   │   ├── manager.py
│   │   │   └── depends on: redis, celery/arq
│   │   └── noop_queue.py
│   │       └── (standalone)
│   │
│   ├── redis.py
│   │   └── depends on: redis-py, config
│   │
│   ├── security.py
│   │   └── depends on: jwcrypto, pwdlib, config
│   │
│   └── ...
│
├── modules/
│   ├── shared/
│   │   ├── exceptions.py (MERGE from httpErrors)
│   │   │   └── depends on: fastapi
│   │   │
│   │   ├── base.py
│   │   │   └── depends on: sqlalchemy
│   │   │
│   │   └── schemas.py
│   │       └── depends on: pydantic
│   │
│   └── iot/ (NEW)
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── device.py ──→ base.py
│       │   │   ├── device_config.py ──→ base.py
│       │   │   ├── device_status.py ──→ base.py
│       │   │   ├── device_alert.py ──→ base.py
│       │   │   ├── iot_data.py ──→ base.py
│       │   │   ├── alarm_log.py ──→ base.py
│       │   │   ├── activity_log.py ──→ base.py
│       │   │   └── schedule.py ──→ base.py
│       │   │
│       │   ├── value_objects/
│       │   │   ├── alarm.py ──→ (standalone)
│       │   │   ├── mqtt.py ──→ (standalone)
│       │   │   └── location.py ──→ (standalone)
│       │   │
│       │   └── helpers/
│       │       └── alarm_logic.py ──→ value_objects/alarm
│       │
│       ├── application/
│       │   └── use_case.py ──→ repositories, mqtt_client, influxdb_client, redis, logger
│       │
│       ├── infrastructure/
│       │   ├── device_repository.py ──→ entities/device, sqlalchemy
│       │   ├── device_config_repository.py ──→ entities/device_config, sqlalchemy
│       │   ├── device_status_repository.py ──→ entities/device_status, sqlalchemy
│       │   ├── device_alert_repository.py ──→ entities/device_alert, sqlalchemy
│       │   ├── iot_data_repository.py ──→ entities/iot_data, sqlalchemy
│       │   ├── alarm_log_repository.py ──→ entities/alarm_log, sqlalchemy
│       │   ├── activity_log_repository.py ──→ entities/activity_log, sqlalchemy
│       │   └── schedule_repository.py ──→ entities/schedule, sqlalchemy
│       │
│       └── presentation/
│           ├── router.py ──→ use_case, schemas, dependencies
│           └── schemas.py ──→ pydantic
```

---

## 3. Dependency Injection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Request                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Presentation Layer                         │
│  router.py → schemas.py (Pydantic validation)               │
└─────────────────────────┬───────────────────────────────────┘
                          │ Depends()
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                          │
│  use_case.py (Business Logic)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Dependencies:                                        │   │
│  │  - device_repository (PostgreSQL)                    │   │
│  │  - device_config_repository (PostgreSQL)             │   │
│  │  - device_status_repository (PostgreSQL)             │   │
│  │  - device_alert_repository (PostgreSQL)              │   │
│  │  - iot_data_repository (PostgreSQL)                  │   │
│  │  - alarm_log_repository (PostgreSQL)                 │   │
│  │  - activity_log_repository (PostgreSQL)              │   │
│  │  - mqtt_client (MQTT Broker)                         │   │
│  │  - influxdb_client (InfluxDB)                        │   │
│  │  - redis_client (Redis Cache)                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  repositories/ (SQLAlchemy 2.0 async)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Services                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │ InfluxDB │  │  Redis   │  │   MQTT   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Diagrams

### 4.1 MQTT Data Processing Flow

```
MQTT Broker
    │
    │ Subscribe
    ▼
MQTT Client (paho-mqtt)
    │
    ├──→ On message received
    │         │
    │         ▼
    │    Process MQTT Data
    │         │
    │    ┌────┴────┐
    │    │         │
    │    ▼         ▼
    │  Redis    InfluxDB
    │  Cache    Write
    │    │         │
    │    │         ▼
    │    │    PostgreSQL
    │    │    (device_status,
    │    │     alarm_logs)
    │    │
    │    ▼
    │  API Response
    │  (cached 5s)
```

### 4.2 Alarm Evaluation Flow

```
GetAlarmDeviceStatus()
    │
    ├─→ Load all devices (PostgreSQL)
    │
    ├─→ For each device:
    │       │
    │       ├─→ Get device_config (PostgreSQL)
    │       │
    │       ├─→ Get MQTT data (Redis Cache → MQTT)
    │       │
    │       ├─→ Evaluate alarm:
    │       │   - Compare value_data vs max/min
    │       │   - Check status_warning/alert thresholds
    │       │   - Check recovery conditions
    │       │
    │       ├─→ Create DeviceAlert (PostgreSQL)
    │       │
    │       └─→ Create AlarmLog (PostgreSQL)
    │
    └─→ Return aggregated alarm results
```

### 4.3 Monitor Device Group Flow

```
GetMonitorDeviceGroup(location_id)
    │
    ├─→ Load devices by location (PostgreSQL)
    │
    ├─→ For each device:
    │       │
    │       ├─→ Get device_config (PostgreSQL)
    │       │
    │       ├─→ Get MQTT data (Redis → MQTT)
    │       │
    │       ├─→ Apply calibration:
    │       │   value = (raw_value × multiplier) + offset
    │       │
    │       ├─→ Evaluate alarm (alarm_logic.py)
    │       │
    │       └─→ Enrich device data
    │
    └─→ Group by location/type
    └─→ Return structured response
```

---

## 5. File Count Summary

| Component | Go Files | Python Files | Notes |
|-----------|----------|--------------|-------|
| Domain Entities | 44 models | 8 entities | Reduced scope |
| Value Objects | 1 helpers | 3 value_objects | alarm, mqtt, location |
| Repositories | 8 repos | 8 repositories | Direct mapping |
| Use Case | 1 usecase (1924 lines) | 1 use_case | Will be split |
| HTTP Handlers | 2 files (919 lines) | 1 router + 1 schemas | Merged |
| MQTT Client | 1 file (441 lines) | 1 client | Direct mapping |
| InfluxDB Client | 1 file (625 lines) | 1 client | Direct mapping |
| Queue Manager | 2 files (363 lines) | 2 files | Direct mapping |
| Error Handling | 1 file (308 lines) | 1 exceptions.py | Merged with shared |
| Helpers | 1 file (405 lines) | 1 alarm_logic.py | Direct mapping |
| Config | 1 file (213 lines) | 1 config.py | Extended |
| **TOTAL** | **64+ files** | **~30 files** | **50% reduction** |

---

## 6. Migration Checklist

### Core Infrastructure
- [ ] Add influxdb-client, paho-mqtt dependencies
- [ ] Create `app/core/influxdb_client.py`
- [ ] Create `app/core/mqtt_client.py`
- [ ] Create `app/core/queue/` module
- [ ] Update `app/core/config.py` with new settings
- [ ] Update `app/core/redis.py` for IoT cache

### IoT Module - Domain
- [ ] Create `app/modules/iot/__init__.py`
- [ ] Create `app/modules/iot/domain/__init__.py`
- [ ] Create `app/modules/iot/domain/entities/device.py`
- [ ] Create `app/modules/iot/domain/entities/device_config.py`
- [ ] Create `app/modules/iot/domain/entities/device_status.py`
- [ ] Create `app/modules/iot/domain/entities/device_alert.py`
- [ ] Create `app/modules/iot/domain/entities/iot_data.py`
- [ ] Create `app/modules/iot/domain/entities/alarm_log.py`
- [ ] Create `app/modules/iot/domain/entities/activity_log.py`
- [ ] Create `app/modules/iot/domain/entities/schedule.py`
- [ ] Create `app/modules/iot/domain/value_objects/alarm.py`
- [ ] Create `app/modules/iot/domain/value_objects/mqtt.py`
- [ ] Create `app/modules/iot/domain/value_objects/location.py`
- [ ] Create `app/modules/iot/domain/helpers/alarm_logic.py`

### IoT Module - Infrastructure
- [ ] Create `app/modules/iot/infrastructure/device_repository.py`
- [ ] Create `app/modules/iot/infrastructure/device_config_repository.py`
- [ ] Create `app/modules/iot/infrastructure/device_status_repository.py`
- [ ] Create `app/modules/iot/infrastructure/device_alert_repository.py`
- [ ] Create `app/modules/iot/infrastructure/iot_data_repository.py`
- [ ] Create `app/modules/iot/infrastructure/alarm_log_repository.py`
- [ ] Create `app/modules/iot/infrastructure/activity_log_repository.py`
- [ ] Create `app/modules/iot/infrastructure/schedule_repository.py`

### IoT Module - Application
- [ ] Create `app/modules/iot/application/use_case.py`

### IoT Module - Presentation
- [ ] Create `app/modules/iot/presentation/router.py`
- [ ] Create `app/modules/iot/presentation/schemas.py`

### Database
- [ ] Create Alembic migration for IoT tables
- [ ] Create seed data script
- [ ] Update docker-compose.yaml with InfluxDB + MQTT

### Integration
- [ ] Register IoT router in app.py
- [ ] Wire up dependencies
- [ ] Update .env with new settings
- [ ] Integration testing

### Testing
- [ ] Unit tests for alarm_logic.py
- [ ] Unit tests for repositories
- [ ] Unit tests for use_case
- [ ] Integration tests for API endpoints
- [ ] MQTT integration tests
- [ ] InfluxDB integration tests
