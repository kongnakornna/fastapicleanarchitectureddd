# 📘 คู่มือสร้าง Module `iot`  

> **Module:** `iot` · **Layer:** `6-Monitoring` · **Prefix:** `iot`
> **Stack:** Python 3.11+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · PostgreSQL 16 · Redis 7 · MQTT · InfluxDB
> **Pattern:** DDD + Clean Architecture + Event-Driven

---

## 📑 สารบัญ

1. [ภาพรวม](#1-ภาพรวม)
2. [ไฟล์ที่ต้องเตรียม](#2-ไฟล์ที่ต้องเตรียม)
3. [Prerequisites](#3-prerequisites)
4. [โครงสร้าง Output (56 ไฟล์)](#4-โครงสร้าง-output-56-ไฟล์)
5. [7 งานหลัก](#5-7-งานหลัก)
6. [วิธีใช้งาน — ทีละขั้นตอน](#6-วิธีใช้งาน--ทีละขั้นตอน)
7. [รายละเอียดแต่ละ Action](#7-รายละเอียดแต่ละ-action)
8. [SQL Migrations (V001/V002/V003)](#8-sql-migrations-v001v002v003)
9. [Alarm Logic (Hardware 1-4)](#9-alarm-logic-hardware-1-4)
10. [Endpoints ทั้งหมด](#10-endpoints-ทั้งหมด)
11. [การทดสอบ](#11-การทดสอบ)
12. [Troubleshooting](#12-troubleshooting)
13. [FAQ](#13-faq)
14. [Checklist ก่อน Deploy](#14-checklist-ก่อน-deploy)

---

## 1. ภาพรวม

### 1.1 Module `iot` คืออะไร

`iot` เป็น **Real-time Sensor & Alarm Monitoring Platform** ทำหน้าที่:

| ฟังก์ชัน | รายละเอียด |
|---|---|
| **MQTT Ingest** | รับข้อมูลจาก sensor ผ่าน MQTT broker |
| **Alarm Evaluation** | ประเมิน threshold ตาม `hardware_id` 1-4 |
| **Cold-chain Monitoring** | ติดตามอุณหภูมิห้องเย็น/ตู้แช่ (PDPA/อย.) |
| **Device Control** | ส่งคำสั่ง ON/OFF ผ่าน MQTT |
| **Time-series Storage** | เก็บข้อมูลใน InfluxDB |
| **Real-time Push** | WebSocket broadcast ให้ dashboard |
| **Alert Notification** | LINE/Email/SMS ผ่าน alerting module |
| **Audit Trail** | บันทึก activity log ทุก action |

### 1.2 Metadata

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `CREATE_iot` |
| **Module** | `iot` |
| **Layer** | `6-Monitoring` |
| **Prefix** | `iot` |
| **Phase** | `4` |
| **Priority** | 🟠 |
| **Dependencies** | `tenant`, `user`, `auth`, `audit`, `events`, `idempotency`, `alerting` |
| **Tables** | 8 tables ใน schema `tenant_iot` |
| **Endpoints** | ~30 endpoints + WebSocket |
| **Events** | `DeviceCreated`, `DeviceStatusChanged`, `AlarmTriggered`, `AlarmRecovered`, `iotDataReceived`, `DeviceOffline`, `ColdChainAlert` |

### 1.3 Data Flow

```
Sensor → MQTT Broker → iotUseCase
                          │
                          ├─→ parse CSV payload
                          ├─→ evaluate_alarm(dto) → AlarmDetailResult
                          ├─→ if alarm: log + alert
                          ├─→ InfluxDB write_points()
                          ├─→ Redis cache (TTL 10s)
                          ├─→ PostgreSQL iot_data
                          └─→ WebSocket broadcast

Dashboard ← REST API ← iotUseCase.get_monitor_device_group()
                            │
                            ├─→ Redis cache check
                            ├─→ MQTT fetch (fallback)
                            ├─→ InfluxDB query
                            └─→ enrich + group by hardware_id
```

### 1.4 State Machines

```
Device:       ACTIVE → OFFLINE → ACTIVE
              ↓
              MAINTENANCE → ACTIVE

AlarmStatus:  NORMAL(5) → WARNING(1) → CRITICAL(2) → RECOVERY(3,4) → NORMAL(5)

DeviceStatus: OFFLINE → ONLINE → OFFLINE
```

---

## 2. ไฟล์ที่ต้องเตรียม

วางไฟล์เหล่านี้ไว้ที่ **root ของ project** (โฟลเดอร์เดียวกับ `app/`):

| # | ไฟล์ | Platform | หน้าที่ |
|---|---|---|---|
| 1 | `create_module_iot.py` | Python | **Implementation หลัก** (cross-platform) |
| 2 | `create_module_iot.bat` | Windows (cmd) | Wrapper — เรียก Python |
| 3 | `create_module_iot.ps1` | PowerShell | Implementation สำหรับ Windows |
| 4 | `update_app_py.py` | Python | Inject router เข้า `app/app.py` |
| 5 | `update_env_py.py` | Python | Inject models เข้า `migrations/env.py` |
| 6 | `create_postman.py` | Python | สร้าง Postman collection |
| 7 | `modules_iot_opencode.md` | — | Spec + Prompt สำหรับ iot |
| 8 | `manual_module_iot.md` | — | เอกสารนี้ |

### โครงสร้างโฟลเดอร์เริ่มต้น

```
fastapi-backend/                    ← PROJECT_ROOT
├── app/
│   ├── __init__.py
│   ├── app.py                      ← จะถูกแก้โดย activate
│   ├── routes.py                   ← จะถูกแก้
│   ├── core/
│   ├── modules/
│   │   └── shared/
│   └── ...
├── db/
│   └── migrations/                 ← จะสร้าง V001/V002/V003
├── alembic/
│   └── versions/                   ← จะสร้าง iot_001_*.py
├── migrations/
│   └── env.py                      ← จะถูกแก้โดย update_env_py.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── property/
├── docs/
│   └── postman/                    ← จะสร้าง iot.json
├── requirements.txt
├── create_module_iot.py            ← วางไฟล์ generator ที่นี่
├── create_module_iot.bat
├── create_module_iot.ps1
├── update_app_py.py
├── update_env_py.py
├── create_postman.py
└── modules_iot_opencode.md
```

---

## 3. Prerequisites

### 3.1 Software Requirements

| Software | Version | ตรวจสอบ |
|---|---|---|
| Python | ≥ 3.11 | `python --version` |
| PostgreSQL | ≥ 16 | `psql --version` |
| Redis | ≥ 7 | `redis-cli ping` → PONG |
| MQTT Broker (Mosquitto) | ≥ 2.0 | `mosquitto -v` |
| InfluxDB | ≥ 2.7 | `influx version` |
| Alembic | latest | `alembic --version` |

### 3.2 Python Packages

```bash
pip install fastapi uvicorn pydantic sqlalchemy asyncpg alembic \
            redis paho-mqtt influxdb-client structlog loguru \
            pytest pytest-asyncio hypothesis
```

### 3.3 Environment Variables (`.env`)

```bash
# Database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/erp"

# Redis
REDIS_URL="redis://localhost:6379/0"

# MQTT
MQTT_BROKER="localhost:1888"
MQTT_CLIENT_ID="iot-service"
MQTT_USERNAME=""
MQTT_PASSWORD=""
MQTT_KEEPALIVE=30

# InfluxDB
INFLUXDB_URL="http://localhost:8086"
INFLUXDB_TOKEN="your-influxdb-token"
INFLUXDB_ORG="your-org"
INFLUXDB_BUCKET="iot_sensors"
INFLUXDB_TIMEOUT=30
```

### 3.4 ตั้งค่า `MODULE_PROJECT_ROOT` (ถ้าต้องการ)

**Windows cmd:**
```bat
set MODULE_PROJECT_ROOT=C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
```

**PowerShell:**
```powershell
$env:MODULE_PROJECT_ROOT = "C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend"
```

**ถ้าไม่ตั้ง** → ใช้ค่า default จาก `create_module_iot.bat`:
```
C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
```

---

## 4. โครงสร้าง Output (56 ไฟล์)

### 4.1 Module Structure

```
app/modules/iot/
├── __init__.py
│
├── domain/                                    (20 ไฟล์)
│   ├── __init__.py
│   ├── enums.py                               HardwareType, AlarmStatus, AlertSeverity
│   ├── exceptions.py                          iotError, DeviceNotFoundError, ...
│   ├── events.py                              DeviceCreated, AlarmTriggered, ...
│   ├── entities/                              (8 entities)
│   │   ├── __init__.py
│   │   ├── device.py                          Device
│   │   ├── device_config.py                   DeviceConfig
│   │   ├── device_status.py                   DeviceStatus
│   │   ├── device_alert.py                    DeviceAlert
│   │   ├── iot_data.py                        iotData
│   │   ├── alarm_log.py                       AlarmLog
│   │   ├── activity_log.py                    ActivityLog
│   │   └── schedule.py                        Schedule
│   ├── value_objects/                         (4 ไฟล์)
│   │   ├── __init__.py
│   │   ├── alarm.py                           AlarmDetailDTO, AlarmDetailResult
│   │   ├── mqtt.py                            MQTTTopicData, MQTTDeviceInfo
│   │   └── location.py                        LocationConfig
│   └── helpers/                               (2 ไฟล์)
│       ├── __init__.py
│       └── alarm_logic.py                     evaluate_alarm()
│
├── application/                               (6 ไฟล์)
│   ├── __init__.py
│   ├── use_case.py                            iotUseCase
│   ├── interfaces.py                          DeviceRepository, MQTTClient, ...
│   ├── mappers.py
│   ├── exceptions.py
│   └── utils.py                               parse_csv_payload, sanitize_payload
│
├── infrastructure/                            (11 ไฟล์)
│   ├── __init__.py
│   ├── models.py                              (8 SQLAlchemy models)
│   ├── device_repository.py
│   ├── device_config_repository.py
│   ├── device_status_repository.py
│   ├── device_alert_repository.py
│   ├── iot_data_repository.py
│   ├── alarm_log_repository.py
│   ├── activity_log_repository.py
│   ├── schedule_repository.py
│   ├── caches.py                              RedisiotCache
│   └── services.py                            KafkaEventBus, AlertService
│
└── presentation/                              (6 ไฟล์)
    ├── __init__.py
    ├── router.py                              HTTP + WebSocket routers
    ├── schemas.py                             Pydantic v2
    ├── docs.py                                OpenAPI examples
    ├── dependencies.py                        DI container
    └── ws.py                                  WebSocket helpers

db/migrations/                                 (3 ไฟล์)
├── V001__create_iot.sql
├── V002__seed_iot.sql
└── V003__rollback_iot.sql

alembic/versions/                              (1 ไฟล์)
└── iot_001_add_iot_tables.py

tests/                                         (7 ไฟล์)
├── unit/
│   ├── test_iot.py
│   └── test_alarm_logic.py
├── integration/
│   ├── test_iot_repository.py
│   └── test_mqtt_ingest.py
├── property/
│   └── test_iot_invariants.py
└── manual/
    └── manual_test_iot.md

docs/                                          (3 ไฟล์)
├── README_iot.md
└── postman/
    └── iot.json

app/routes.py              (แก้)
app/app.py                 (แก้)
migrations/env.py          (แก้)

**รวม: 56 ไฟล์**
```

### 4.2 ตาราง Entities

| Entity | หน้าที่ | Key Fields |
|---|---|---|
| `Device` | อุปกรณ์ iot | id, tenant_id, hardware_id (1-4), device_name, mqtt_topic, status |
| `DeviceConfig` | Config thresholds | max_value, min_value, warning_threshold, alert_threshold, recovery_* |
| `DeviceStatus` | Status ปัจจุบัน | is_online, last_seen, last_value, count_alarm |
| `DeviceAlert` | Alert | alert_type, severity, title, message, resolved |
| `iotData` | Time-series data | device_id, data_json, timestamp |
| `AlarmLog` | Alarm history | alarm_type, alarm_status, title, subject |
| `ActivityLog` | Activity audit | log_type, device_id, user_id, severity |
| `Schedule` | ตารางเวลา control | start_time, end_time, monday..sunday |

### 4.3 Enums

```python
class HardwareType(IntEnum):
    SENSOR = 1            # Analog sensor (temp/humidity)
    IO_SENSOR = 2         # Digital input
    IO_CONTROL = 3        # Relay control
    CRITICAL_SENSOR = 4   # Critical sensor (fire, gas)

class AlarmStatus(IntEnum):
    NORMAL = 5
    WARNING = 1
    CRITICAL = 2
    RECOVERY_WARNING = 3
    RECOVERY_CRITICAL = 4

class AlertSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

---

## 5. 7 งานหลัก

| # | Action | หน้าที่ | Output |
|---|---|---|---|
| 1 | `create` | สร้าง module 4 layers | `app/modules/iot/` (39 ไฟล์) |
| 2 | `activate` | Register router ใน app | `app/app.py` updated |
| 3 | `sql` | สร้าง SQL migrations | `db/migrations/V001-V003` |
| 4 | `alembic` | สร้าง Alembic migration | `alembic/versions/iot_001_*.py` |
| 5 | `swagger` | สร้าง OpenAPI metadata | `presentation/swagger.py` |
| 6 | `postman` | สร้าง Postman collection | `docs/postman/iot.json` |
| 7 | `test` | สร้าง tests | `tests/` (7 ไฟล์) |
| + | `docs` | สร้าง README | `docs/README_iot.md` |
| + | `all` | ทำทุกอย่าง | ทั้งหมด |

---

## 6. วิธีใช้งาน — ทีละขั้นตอน

### 6.1 Quick Start (แนะนำ)

**Linux / macOS / Windows (Python):**
```bash
cd /path/to/fastapi-backend
python create_module_iot.py all iot 6 iot
```

**Windows (cmd):**
```bat
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
create_module_iot.bat all iot 6 iot
```

**PowerShell:**
```powershell
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
.\create_module_iot.ps1 all iot 6 iot -Force
```

### 6.2 Step-by-Step (แนะนำสำหรับ Production)

```bash
# ─── Step 1: ดู help ──────────────────────────
python create_module_iot.py help

# ─── Step 2: สร้าง module structure ───────────
python create_module_iot.py create iot 6 iot

# ─── Step 3: สร้าง SQL migrations ─────────────
python create_module_iot.py sql iot iot

# ─── Step 4: สร้าง Alembic migration ──────────
python create_module_iot.py alembic iot iot

# ─── Step 5: สร้าง Swagger metadata ───────────
python create_module_iot.py swagger iot

# ─── Step 6: สร้าง Postman collection ─────────
python create_module_iot.py postman iot

# ─── Step 7: สร้าง tests ──────────────────────
python create_module_iot.py test iot

# ─── Step 8: สร้าง docs ───────────────────────
python create_module_iot.py docs iot

# ─── Step 9: Register router ─────────────────
python create_module_iot.py activate iot

# ─── Step 10: Inject models เข้า env.py ──────
python update_env_py.py iot

# ─── Step 11: Verify app.py ──────────────────
python update_app_py.py iot --check
```

### 6.3 Apply กับ Database

```bash
# ─── 1. Apply SQL ────────────────────────────
psql $DATABASE_URL -f db/migrations/V001__create_iot.sql
psql $DATABASE_URL -f db/migrations/V002__seed_iot.sql

# ─── 2. Apply Alembic ────────────────────────
alembic upgrade head

# ─── 3. Verify ───────────────────────────────
psql $DATABASE_URL -c "\dt tenant_iot.*"
# → ต้องเห็น 8 tables
```

### 6.4 Start Services

```bash
# ─── MQTT ────────────────────────────────────
mosquitto -c /etc/mosquitto/mosquitto.conf

# ─── InfluxDB ────────────────────────────────
influxd

# ─── Redis ───────────────────────────────────
redis-server

# ─── FastAPI ─────────────────────────────────
uvicorn app.main:app --reload --port 8000
```

### 6.5 Verify

```bash
# ─── Health ──────────────────────────────────
curl http://localhost:8000/api/v1/iot/status
# → {"mqtt_connected": true, "cache_enabled": true}

# ─── Swagger ─────────────────────────────────
open http://localhost:8000/docs
# → เห็น tag "iot"
```

---

## 7. รายละเอียดแต่ละ Action

### 7.1 `create` — สร้าง Module

```bash
python create_module_iot.py create iot 6 iot
```

**Output:**
- `app/modules/iot/domain/` — 20 ไฟล์
- `app/modules/iot/application/` — 6 ไฟล์
- `app/modules/iot/infrastructure/` — 11 ไฟล์
- `app/modules/iot/presentation/` — 6 ไฟล์
- `app/modules/iot/__init__.py`

**Options:**
| Option | คำอธิบาย |
|---|---|
| `--force` | เขียนทับไฟล์เดิม (สร้าง `.bak` อัตโนมัติ) |
| `--template A-G` | Template (default A) |

---

### 7.2 `activate` — Register Router

```bash
python create_module_iot.py activate iot
```

**แก้ `app/app.py`:**
```python
# เพิ่ม import
from app.modules.iot.presentation.router import router as iot_router

# เพิ่ม include
app.include_router(iot_router, prefix="/api/v1")

# เพิ่ม OpenAPI tag
{"name": "iot", "description": "..."}
```

**Backup:** `app/app.py.bak`

---

### 7.3 `sql` — สร้าง SQL Migrations

```bash
python create_module_iot.py sql iot iot
```

**Output:**
- `db/migrations/V001__create_iot.sql` — 8 tables + RLS + Trigger
- `db/migrations/V002__seed_iot.sql` — sample devices
- `db/migrations/V003__rollback_iot.sql` — rollback

---

### 7.4 `alembic` — สร้าง Alembic Migration

```bash
python create_module_iot.py alembic iot iot
```

**Output:** `alembic/versions/iot_001_add_iot_tables.py`

จะ auto-detect head revision จากไฟล์เดิม

---

### 7.5 `swagger` — OpenAPI Metadata

```bash
python create_module_iot.py swagger iot
```

**Output:** `app/modules/iot/presentation/swagger.py`

---

### 7.6 `postman` — Postman Collection

```bash
python create_module_iot.py postman iot
```

**Output:** `docs/postman/iot.json` (8 folders, ~25 requests)

---

### 7.7 `test` — Tests

```bash
python create_module_iot.py test iot
```

**Output:**
- `tests/unit/test_iot.py`
- `tests/unit/test_alarm_logic.py`
- `tests/integration/test_iot_repository.py`
- `tests/property/test_iot_invariants.py`
- `tests/manual/manual_test_iot.md`

---

### 7.8 `docs` — README

```bash
python create_module_iot.py docs iot
```

**Output:** `docs/README_iot.md`

---

### 7.9 `all` — ทำทุกอย่าง

```bash
python create_module_iot.py all iot 6 iot
```

เทียบเท่ากับ:
```
create → sql → alembic → swagger → postman → test → docs → activate
```

---

### 7.10 `update_env_py.py` — Inject Models

```bash
# ─── Inject ──────────────────────────────────
python update_env_py.py iot

# ─── Check ───────────────────────────────────
python update_env_py.py iot --check

# ─── Dry-run ─────────────────────────────────
python update_env_py.py iot --dry-run

# ─── Force replace ───────────────────────────
python update_env_py.py iot --force
```

**แก้ `migrations/env.py`:**
```python
# --- module iot (8 models) ---
try:
    from app.modules.iot.infrastructure.models import (  # noqa: F401
        ActivityLogModel,
        AlarmLogModel,
        DeviceAlertModel,
        DeviceConfigModel,
        DeviceModel,
        DeviceStatusModel,
        ScheduleModel,
        iotDataModel,
    )
except ImportError:
    pass
```

---

## 8. SQL Migrations (V001/V002/V003)

### 8.1 V001 — Create Tables

**8 tables ใน `tenant_iot` schema:**

| Table | หน้าที่ | Index |
|---|---|---|
| `devices` | อุปกรณ์ | ix_iot_device_tenant, ix_iot_device_hardware, ix_iot_device_topic |
| `device_configs` | Thresholds | UNIQUE(tenant_id, device_id) |
| `device_statuses` | Status ปัจจุบัน | UNIQUE(tenant_id, device_id) |
| `device_alerts` | Alert | ix_iot_alert_device, ix_iot_alert_severity |
| `iot_data` | Time-series | ix_iot_data_device_time, ix_iot_data_tenant |
| `alarm_logs` | Alarm history | ix_iot_alarm_device, ix_iot_alarm_status |
| `activity_logs` | Audit | ix_iot_activity_device, ix_iot_activity_type |
| `schedules` | ตารางเวลา | ix_iot_schedule_device |

**ทุก table มี:**
- `id UUID PK DEFAULT gen_random_uuid()`
- `tenant_id UUID NOT NULL`
- `created_at`, `updated_at TIMESTAMPTZ`
- RLS policy `p_iot_*` (tenant isolation)
- Trigger `trg_iot_*_updated` (auto updated_at)

**ตัวอย่าง:**
```sql
CREATE TABLE tenant_iot.devices (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID NOT NULL,
    hardware_id       INTEGER NOT NULL,
    device_name       VARCHAR(255) NOT NULL,
    mqtt_topic        VARCHAR(500) NOT NULL DEFAULT '',
    status            VARCHAR(50) NOT NULL DEFAULT 'offline',
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_iot_hardware CHECK (hardware_id IN (1,2,3,4))
);

ALTER TABLE tenant_iot.devices ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_device ON tenant_iot.devices
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
```

### 8.2 V002 — Seed

```sql
INSERT INTO tenant_iot.devices (tenant_id, hardware_id, device_name, ...)
VALUES
    ('00000000-0000-0000-0000-000000000001', 1, 'Cold Room 1 Temp', ...),
    ('00000000-0000-0000-0000-000000000001', 1, 'Cold Room 1 Humidity', ...),
    ('00000000-0000-0000-0000-000000000001', 3, 'Cold Room 1 Door', ...),
    ('00000000-0000-0000-0000-000000000001', 4, 'Fire Sensor A', ...)
ON CONFLICT DO NOTHING;
```

### 8.3 V003 — Rollback

```sql
BEGIN;
DROP TRIGGER IF EXISTS trg_iot_device_updated ON tenant_iot.devices;
-- ... ทุก table
DROP POLICY IF EXISTS p_iot_device ON tenant_iot.devices;
-- ... ทุก policy
DROP TABLE IF EXISTS tenant_iot.devices CASCADE;
-- ... ทุก table
COMMIT;
```

### 8.4 Apply

```bash
# ─── Create ──────────────────────────────────
psql $DATABASE_URL -f db/migrations/V001__create_iot.sql
psql $DATABASE_URL -f db/migrations/V002__seed_iot.sql

# ─── Rollback ────────────────────────────────
psql $DATABASE_URL -f db/migrations/V003__rollback_iot.sql
```

---

## 9. Alarm Logic (Hardware 1-4)

### 9.1 หลักการ

`evaluate_alarm(dto, lang)` ใน `domain/helpers/alarm_logic.py`

| Hardware | Type | Logic |
|---|---|---|
| **1** | Analog Sensor | max/min + warning/alert thresholds + recovery |
| **2** | IO Sensor (digital) | value_alarm 0/1 |
| **3** | IO Control (relay) | ON/OFF normal |
| **4** | Critical Sensor | fire/gas → immediate critical |

### 9.2 Status Codes

| Status | ความหมาย |
|---|---|
| `5` | NORMAL |
| `1` | WARNING |
| `2` | CRITICAL |
| `3` | RECOVERY_WARNING |
| `4` | RECOVERY_CRITICAL |

### 9.3 ตัวอย่างการใช้งาน

```python
from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO

# ─── Hardware 1: Analog sensor ───────────────
dto = AlarmDetailDTO(
    hardware_id=1,
    value_data="55.0",       # อุณหภูมิ 55°C
    value_alarm=0,
    max_value=50,            # max 50°C
    min_value=0,
    device_name="Cold Room 1",
    unit="°C",
)
result = evaluate_alarm(dto, lang="th")
# → result.status = 2 (CRITICAL)
# → result.title = "วิกฤต มีค่าสูงเกินกำหนด"

# ─── Hardware 4: Fire sensor ─────────────────
dto = AlarmDetailDTO(
    hardware_id=4,
    value_data="0",          # 0 = ตรวจพบไฟ
    value_alarm=0,
    device_name="Fire Sensor A",
)
result = evaluate_alarm(dto, lang="th")
# → result.status = 2 (CRITICAL)
```

---

## 10. Endpoints ทั้งหมด

### 10.1 Connection & Data

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/iot/status` | MQTT connection status |
| `POST` | `/api/v1/iot/topic-data` | รับข้อมูลจาก topic |
| `POST` | `/api/v1/iot/control` | ส่งคำสั่ง control |
| `POST` | `/api/v1/iot/controls` | ส่งคำสั่ง control (alias) |

### 10.2 Device Management

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/iot/devices` | List devices (paginated) |
| `GET` | `/api/v1/iot/devices/page` | List devices (alias) |
| `GET` | `/api/v1/iot/devices/buckets/{bucket}` | Devices by bucket |
| `GET` | `/api/v1/iot/devices/location/{location_id}` | Devices by location |
| `GET` | `/api/v1/iot/devices/{device_id}/status` | Get device status |
| `PUT` | `/api/v1/iot/devices/{device_id}/status` | Update device status |
| `GET` | `/api/v1/iot/devices/{device_id}/config` | Get device config |
| `PUT` | `/api/v1/iot/devices/{device_id}/config` | Update device config |
| `GET` | `/api/v1/iot/devices/{device_id}/stats` | Device statistics |

### 10.3 Charts & Monitoring

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/iot/senser-charts` | Sensor chart data |
| `GET` | `/api/v1/iot/senser-data-chart` | Sensor data chart |
| `GET` | `/api/v1/iot/senser-data` | Sensor data |
| `GET` | `/api/v1/iot/device-senser-charts` | Device sensor charts |
| `POST` | `/api/v1/iot/alarm-device-status` | Alarm device status |
| `POST` | `/api/v1/iot/alarm-device-status-control` | Alarm + control |
| `POST` | `/api/v1/iot/monitor-device-group` | Monitor device group |
| `GET` | `/api/v1/iot/monitor-device-chart` | Monitor device chart |
| `GET` | `/api/v1/iot/topic-data-device-chart` | Topic data + chart |

### 10.4 Data Management

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/iot/process-mqtt-data` | Process MQTT data |
| `GET` | `/api/v1/iot/data/latest` | Latest data |
| `GET` | `/api/v1/iot/data/date-range` | Data by date range |
| `GET` | `/api/v1/iot/data/list` | List iot data (paginated) |
| `POST` | `/api/v1/iot/export` | Export data (JSON/CSV) |
| `DELETE` | `/api/v1/iot/cleanup` | Cleanup old data |

### 10.5 WebSocket

| Method | Path | Description |
|---|---|---|
| `WS` | `/api/v1/iot/ws/{room}` | WebSocket endpoint |
| `GET` | `/api/v1/iot/ws/rooms` | List WS rooms |
| `GET` | `/api/v1/iot/ws/rooms/{room}/stats` | Room stats |

### 10.6 Batch

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/iot/batch/process` | Batch process MQTT |
| `POST` | `/api/v1/iot/batch/control` | Batch control |

### 10.7 ตัวอย่าง cURL

```bash
# ─── Status ──────────────────────────────────
curl http://localhost:8000/api/v1/iot/status

# ─── Get Topic Data ──────────────────────────
curl -X POST "http://localhost:8000/api/v1/iot/topic-data?topic=iot/coldroom1/DATA"

# ─── Device Control ──────────────────────────
curl -X POST http://localhost:8000/api/v1/iot/control \
  -H "Content-Type: application/json" \
  -d '{"topic": "iot/coldroom1/CTRL", "message": "ON"}'

# ─── List Devices ────────────────────────────
curl "http://localhost:8000/api/v1/iot/devices?page=1&page_size=20"

# ─── Monitor Device Group ────────────────────
curl -X POST http://localhost:8000/api/v1/iot/monitor-device-group \
  -H "Content-Type: application/json" \
  -d '{"bucket": "iot_sensors", "hardware_id": 1, "lang": "th"}'

# ─── Alarm Device Status ─────────────────────
curl -X POST http://localhost:8000/api/v1/iot/alarm-device-status \
  -H "Content-Type: application/json" \
  -d '{"bucket": "iot_sensors", "measurement": "temperature"}'

# ─── Process MQTT Data ───────────────────────
curl -X POST http://localhost:8000/api/v1/iot/process-mqtt-data \
  -H "Content-Type: application/json" \
  -d '{"device_id": "1", "raw_data": "25.5,60.0"}'

# ─── Export CSV ──────────────────────────────
curl -X POST http://localhost:8000/api/v1/iot/export \
  -H "Content-Type: application/json" \
  -d '{"device_id": "1", "format": "csv"}' \
  -o export.csv
```

### 10.8 MQTT Topic Pattern

```
iot/{location}/{type}/DATA      # Data from sensors
iot/{location}/{type}/CTRL      # Control commands
iot/{location}/{type}/STATUS    # Status updates
```

**Payload format (CSV):**
```
25.5,60.0,1,0
```

**Test publish:**
```bash
mosquitto_pub -h localhost -t "iot/coldroom1/DATA" -m "25.5,60.0"
```

---

## 11. การทดสอบ

### 11.1 Unit Tests

```bash
# ─── Domain ──────────────────────────────────
pytest tests/unit/test_iot.py -v

# ─── Alarm Logic (≥ 8 tests) ─────────────────
pytest tests/unit/test_alarm_logic.py -v

# ─── ทั้งหมด ─────────────────────────────────
pytest tests/unit/ -v
```

### 11.2 Integration Tests

```bash
pytest tests/integration/test_iot_repository.py -v
pytest tests/integration/test_mqtt_ingest.py -v
```

### 11.3 Property Tests

```bash
pytest tests/property/test_iot_invariants.py -v
```

### 11.4 Coverage

```bash
pytest --cov=app.modules.iot --cov-report=html --cov-fail-under=85
open htmlcov/index.html
```

### 11.5 Manual Test (12 scenarios)

ดู `tests/manual/manual_test_iot.md`:

| # | Scenario | Method | Endpoint |
|---|---|---|---|
| 1 | MQTT connected | GET | `/api/v1/iot/status` |
| 2 | Get topic data | POST | `/api/v1/iot/topic-data` |
| 3 | Device control ON | POST | `/api/v1/iot/control` |
| 4 | List devices | GET | `/api/v1/iot/devices` |
| 5 | Monitor device group | POST | `/api/v1/iot/monitor-device-group` |
| 6 | Alarm device status | POST | `/api/v1/iot/alarm-device-status` |
| 7 | Process MQTT data | POST | `/api/v1/iot/process-mqtt-data` |
| 8 | Get latest data | GET | `/api/v1/iot/data/latest` |
| 9 | Export CSV | POST | `/api/v1/iot/export` |
| 10 | Cleanup old data | DELETE | `/api/v1/iot/cleanup?days=90` |
| 11 | WebSocket connect | WS | `/api/v1/iot/ws/default` |
| 12 | Cross-tenant device | GET | other tenant → 404 |

### 11.6 Postman

```bash
# ─── Import ──────────────────────────────────
# 1. เปิด Postman
# 2. File → Import → docs/postman/iot.json
# 3. ตั้งค่า base_url = http://localhost:8000
# 4. รัน Collection Runner
```

---

## 12. Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `[ERROR] Python not found` | ไม่มี Python | ติดตั้ง Python ≥ 3.11 |
| `[ERROR] Project root not found` | path ผิด | ตรวจ `MODULE_PROJECT_ROOT` |
| `[ERROR] create_module_iot.py not found` | ไฟล์ไม่อยู่ที่ root | ย้ายไปที่ root |
| `[!!] skip (exists)` | ไฟล์มีอยู่ | ใช้ `--force` |
| `UnicodeEncodeError` (Windows) | encoding | `chcp 65001` |
| `ModuleNotFoundError: app.modules.iot` | ยังไม่ activate | รัน `activate` |
| `IndentationError` ในไฟล์ generated | template ผิด | ตรวจ `dedent()` |
| `FileNotFoundError app/app.py` | ไม่มี app.py | สร้างก่อน |
| `alembic: command not found` | ไม่มี alembic | `pip install alembic` |
| `mqtt_connected: false` | MQTT broker down | `mosquitto -v` |
| `payload: null` | Topic ไม่มีข้อมูล | publish test |
| Alarm ไม่ trigger | Config ไม่ครบ | ตรวจ `device_configs` |
| InfluxDB query fail | Token ผิด | ตรวจ `INFLUXDB_TOKEN` |
| Cache miss ทุกครั้ง | Redis down | `redis-cli ping` |
| WebSocket ไม่ push | Room ผิด | ตรวจ subscribe room |
| RLS block | `tenant_id` ผิด | ตรวจ `X-Tenant-Id` |
| `MQTTNotConnectedError` | Reconnect fail | ตรวจ network + credentials |
| Slow query | ไม่มี index | ตรวจ `ix_iot_data_device_time` |
| Duplicate alert | Race condition | ใช้ idempotency key |

### 12.1 Debug Mode

```bash
# ─── Python ──────────────────────────────────
python -v create_module_iot.py create iot 6 iot

# ─── PowerShell ──────────────────────────────
$DebugPreference = "Continue"
.\create_module_iot.ps1 create iot 6 iot -Verbose

# ─── MQTT ────────────────────────────────────
mosquitto_sub -h localhost -t 'iot/#' -v -d

# ─── Logs ────────────────────────────────────
tail -f logs/app.log | jq 'select(.module=="iot")'
```

### 12.2 Reset Module

```bash
# 1. Rollback DB
psql $DATABASE_URL -f db/migrations/V003__rollback_iot.sql

# 2. Rollback Alembic
alembic downgrade -1

# 3. ลบไฟล์
rm -rf app/modules/iot
rm db/migrations/V00*__iot.sql
rm alembic/versions/iot_001*.py
rm tests/unit/test_iot.py tests/unit/test_alarm_logic.py
rm tests/integration/test_iot_repository.py
rm tests/property/test_iot_invariants.py
rm docs/README_iot.md docs/postman/iot.json

# 4. Regenerate
python create_module_iot.py all iot 6 iot --force
```

---

## 13. FAQ

**Q: ต้องใช้ MQTT broker อะไร?**
A: Mosquitto (แนะนำ), EMQX, HiveMQ — รองรับ MQTT 3.1.1/5.0

**Q: ต้องใช้ InfluxDB ไหม?**
A: ไม่บังคับ — ถ้าไม่มีจะ fallback ไป PostgreSQL (`iot_data` table)

**Q: รองรับกี่ device?**
A: > 10,000 devices (MQTT + Redis cache + InfluxDB time-series)

**Q: Cold-chain monitoring ทำงานยังไง?**
A: hardware_id=1 sensor → evaluate_alarm → ถ้า temp out-of-range → alert

**Q: WebSocket รับได้กี่ connection?**
A: > 1000 concurrent (ใช้ asyncio + Redis pub/sub)

**Q: เพิ่ม alert channel ใหม่ยังไง?**
A: แก้ `AlertService` ใน `infrastructure/services.py` เพิ่ม `_send_to_channel` branch

**Q: Test MQTT ยังไง?**
A:
```bash
mosquitto_pub -h localhost -t "iot/coldroom1/DATA" -m "25.5,60.0"
```

**Q: Deploy production ยังไง?**
A:
```bash
# 1. Docker build
docker build -t iot-service:latest .

# 2. Run migrations
docker run iot-service:latest alembic upgrade head

# 3. Run service
docker run -p 8000:8000 \
  -e MQTT_BROKER=mqtt://broker:1888 \
  -e INFLUXDB_URL=http://influx:8086 \
  iot-service:latest
```

**Q: อ่าน alarm logic ยังไง?**
A: `domain/helpers/alarm_logic.py` → `evaluate_alarm(dto, lang)`

**Q: เพิ่ม language ใหม่?**
A: แก้ `_THAI_MESSAGES` / `_ENGLISH_MESSAGES` + เพิ่ม dict ใหม่

**Q: ต่างระหว่าง `.py`, `.bat`, `.ps1`?**
A: `.py` = cross-platform (แนะนำ), `.bat` = Windows cmd wrapper, `.ps1` = PowerShell

**Q: รันซ้ำได้ไหม?**
A: ได้ — ใช้ `--force` (สร้าง `.bak` อัตโนมัติ)

---

## 14. Checklist ก่อน Deploy

### 14.1 Before

- [ ] Python ≥ 3.11
- [ ] PostgreSQL ≥ 16
- [ ] Redis running
- [ ] MQTT broker running
- [ ] InfluxDB running
- [ ] ไฟล์ generator ครบที่ root

### 14.2 Generate

- [ ] `create` — module structure (39 ไฟล์)
- [ ] `sql` — V001/V002/V003
- [ ] `alembic` — iot_001 migration
- [ ] `swagger` — OpenAPI metadata
- [ ] `postman` — collection
- [ ] `test` — unit tests
- [ ] `docs` — README
- [ ] `activate` — register router
- [ ] `update_env_py.py iot` — inject models

### 14.3 Apply Database

- [ ] `psql -f db/migrations/V001__create_iot.sql`
- [ ] `psql -f db/migrations/V002__seed_iot.sql`
- [ ] `alembic upgrade head`
- [ ] Verify: `psql -c "\dt tenant_iot.*"` → 8 tables

### 14.4 Verify

- [ ] Review code: `tree app/modules/iot`
- [ ] Run tests: `pytest tests/unit/test_iot.py -v`
- [ ] Coverage: `pytest --cov=app.modules.iot --cov-fail-under=85`
- [ ] Check Swagger: `http://localhost:8000/docs` → tag "iot"
- [ ] Test MQTT: `mosquitto_pub -t "iot/coldroom1/DATA" -m "25.5,60.0"`
- [ ] Test WebSocket: `wscat -c ws://localhost:8000/api/v1/iot/ws/default`
- [ ] Import Postman collection
- [ ] Test cross-tenant (RLS): ต้อง 404

### 14.5 Maintenance

- [ ] Backup DB ก่อน migrate
- [ ] ตรวจ `.bak` files
- [ ] Update docs
- [ ] Tag version: `git tag -a v1.0.0-iot`
- [ ] Set retention policy: 90 days default
- [ ] Monitor: `curl /api/v1/iot/status` ทุก 1 นาที

---

## 📋 สรุปคำสั่งทั้งหมด (Copy-Paste)

```bash
# ═══════════════════════════════════════════════════════════════
#  iot Module — Complete Setup
# ═══════════════════════════════════════════════════════════════

# ─── 1. Navigate ─────────────────────────────
cd /path/to/fastapi-backend

# ─── 2. Generate (one command) ───────────────
python create_module_iot.py all iot 6 iot

# ─── 3. Inject models เข้า env.py ────────────
python update_env_py.py iot

# ─── 4. Apply SQL ────────────────────────────
psql $DATABASE_URL -f db/migrations/V001__create_iot.sql
psql $DATABASE_URL -f db/migrations/V002__seed_iot.sql

# ─── 5. Apply Alembic ────────────────────────
alembic upgrade head

# ─── 6. Verify ───────────────────────────────
python update_app_py.py iot --check
python update_env_py.py iot --check
pytest tests/unit/test_iot.py -v
pytest tests/unit/test_alarm_logic.py -v

# ─── 7. Start services ───────────────────────
mosquitto -v &
influxd &
redis-server &
uvicorn app.main:app --reload --port 8000

# ─── 8. Test ─────────────────────────────────
curl http://localhost:8000/api/v1/iot/status
curl http://localhost:8000/docs
mosquitto_pub -h localhost -t "iot/coldroom1/DATA" -m "25.5,60.0"
```

---

**Version:** 1.0.0
**Last Updated:** 2025
**Maintainer:** Dev Team
**Status:** ✅ พร้อมใช้งาน



-- ----------------------------
-- Table structure for iot_activity_logs
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_activity_logs";
CREATE TABLE "tenant_iot"."iot_activity_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "log_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "device_id" uuid,
  "user_id" uuid,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'info'::character varying,
  "data_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_alarm_logs
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_alarm_logs";
CREATE TABLE "tenant_iot"."iot_alarm_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL DEFAULT 0,
  "alarm_type" int4 NOT NULL DEFAULT 0,
  "alarm_status" int4 NOT NULL DEFAULT 0,
  "value_data" float8 NOT NULL DEFAULT '0'::double precision,
  "value_alarm" float8 NOT NULL DEFAULT '0'::double precision,
  "title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "subject" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "content" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "data_alarm" int4 NOT NULL DEFAULT 0,
  "data_alarm_raw" int4 NOT NULL DEFAULT 0,
  "event_control" int4 NOT NULL DEFAULT 0,
  "message_mqtt_control" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_data
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_data";
CREATE TABLE "tenant_iot"."iot_data" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "data_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "timestamp" timestamptz(6),
  "location_id" int4 NOT NULL DEFAULT 0,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_device_alerts
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_device_alerts";
CREATE TABLE "tenant_iot"."iot_device_alerts" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "alert_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'low'::character varying,
  "title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "message" varchar(1000) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "value_data" float8 NOT NULL DEFAULT '0'::double precision,
  "value_alarm" float8 NOT NULL DEFAULT '0'::double precision,
  "resolved" bool NOT NULL DEFAULT false,
  "acknowledged" bool NOT NULL DEFAULT false,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_device_configs
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_device_configs";
CREATE TABLE "tenant_iot"."iot_device_configs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "max_value" float8 NOT NULL DEFAULT '0'::double precision,
  "min_value" float8 NOT NULL DEFAULT '0'::double precision,
  "warning_threshold" float8 NOT NULL DEFAULT '0'::double precision,
  "alert_threshold" float8 NOT NULL DEFAULT '0'::double precision,
  "recovery_warning" float8 NOT NULL DEFAULT '0'::double precision,
  "recovery_alert" float8 NOT NULL DEFAULT '0'::double precision,
  "calibration_offset" float8 NOT NULL DEFAULT '0'::double precision,
  "calibration_multiplier" float8 NOT NULL DEFAULT '1'::double precision,
  "mqtt_control_on" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mqtt_control_off" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "action_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "config_json" varchar(2000) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_device_statuses
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_device_statuses";
CREATE TABLE "tenant_iot"."iot_device_statuses" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "device_id" uuid NOT NULL,
  "is_online" bool NOT NULL DEFAULT false,
  "last_seen" timestamptz(6),
  "last_value" float8 NOT NULL DEFAULT '0'::double precision,
  "last_alarm" int4 NOT NULL DEFAULT 0,
  "count_alarm" int4 NOT NULL DEFAULT 0,
  "event" int4 NOT NULL DEFAULT 0,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'offline'::character varying,
  "sensor_data" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "sensor_min" float8 NOT NULL DEFAULT '0'::double precision,
  "sensor_max" float8 NOT NULL DEFAULT '0'::double precision,
  "sensor_avg" float8 NOT NULL DEFAULT '0'::double precision,
  "battery" float8 NOT NULL DEFAULT '0'::double precision,
  "rssi" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_devices
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_devices";
CREATE TABLE "tenant_iot"."iot_devices" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "hardware_id" int4 NOT NULL,
  "type_id" int4 NOT NULL DEFAULT 0,
  "location_id" int4 NOT NULL DEFAULT 0,
  "device_sn" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "device_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "device_type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "location_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mqtt_id" int4 NOT NULL DEFAULT 0,
  "mqtt_main_id" int4 NOT NULL DEFAULT 0,
  "mqtt_topic" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mqtt_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mqtt_username" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mqtt_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "unit" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'offline'::character varying,
  "icon" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "icon_color" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "description" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "firmware_version" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Table structure for iot_schedules
-- ----------------------------
DROP TABLE IF EXISTS "tenant_iot"."iot_schedules";
CREATE TABLE "tenant_iot"."iot_schedules" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "schedule_id" int4 NOT NULL DEFAULT 0,
  "device_id" uuid NOT NULL,
  "start_time" varchar(10) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "end_time" varchar(10) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "event" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "monday" bool NOT NULL DEFAULT false,
  "tuesday" bool NOT NULL DEFAULT false,
  "wednesday" bool NOT NULL DEFAULT false,
  "thursday" bool NOT NULL DEFAULT false,
  "friday" bool NOT NULL DEFAULT false,
  "saturday" bool NOT NULL DEFAULT false,
  "sunday" bool NOT NULL DEFAULT false,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Indexes structure for table iot_activity_logs
-- ----------------------------
CREATE INDEX "ix_iot_activity_device" ON "tenant_iot"."iot_activity_logs" USING btree (
  "device_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_activity_type" ON "tenant_iot"."iot_activity_logs" USING btree (
  "log_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_activity_logs
-- ----------------------------
CREATE TRIGGER "trg_iot_activity_logs_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_activity_logs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Primary Key structure for table iot_activity_logs
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_activity_logs" ADD CONSTRAINT "iot_activity_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_alarm_logs
-- ----------------------------
CREATE INDEX "ix_iot_alarm_device" ON "tenant_iot"."iot_alarm_logs" USING btree (
  "device_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_alarm_status" ON "tenant_iot"."iot_alarm_logs" USING btree (
  "alarm_status" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_alarm_logs
-- ----------------------------
CREATE TRIGGER "trg_iot_alarm_logs_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_alarm_logs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Primary Key structure for table iot_alarm_logs
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_alarm_logs" ADD CONSTRAINT "iot_alarm_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_data
-- ----------------------------
CREATE INDEX "ix_iot_data_device_time" ON "tenant_iot"."iot_data" USING btree (
  "device_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_data_tenant" ON "tenant_iot"."iot_data" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_data
-- ----------------------------
CREATE TRIGGER "trg_iot_data_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_data"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Primary Key structure for table iot_data
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_data" ADD CONSTRAINT "iot_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_device_alerts
-- ----------------------------
CREATE INDEX "ix_iot_alert_device" ON "tenant_iot"."iot_device_alerts" USING btree (
  "device_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "resolved" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_alert_severity" ON "tenant_iot"."iot_device_alerts" USING btree (
  "severity" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_device_alerts
-- ----------------------------
CREATE TRIGGER "trg_iot_device_alerts_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_device_alerts"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Checks structure for table iot_device_alerts
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_alerts" ADD CONSTRAINT "ck_iot_severity" CHECK (severity::text = ANY (ARRAY['info'::character varying, 'low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[]));

-- ----------------------------
-- Primary Key structure for table iot_device_alerts
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_alerts" ADD CONSTRAINT "iot_device_alerts_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table iot_device_configs
-- ----------------------------
CREATE TRIGGER "trg_iot_device_configs_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_device_configs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Uniques structure for table iot_device_configs
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_configs" ADD CONSTRAINT "uq_iot_config_device" UNIQUE ("tenant_id", "device_id");

-- ----------------------------
-- Primary Key structure for table iot_device_configs
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_configs" ADD CONSTRAINT "iot_device_configs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table iot_device_statuses
-- ----------------------------
CREATE TRIGGER "trg_iot_device_statuses_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_device_statuses"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Uniques structure for table iot_device_statuses
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_statuses" ADD CONSTRAINT "uq_iot_status_device" UNIQUE ("tenant_id", "device_id");

-- ----------------------------
-- Primary Key structure for table iot_device_statuses
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_device_statuses" ADD CONSTRAINT "iot_device_statuses_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_devices
-- ----------------------------
CREATE INDEX "ix_iot_device_hardware" ON "tenant_iot"."iot_devices" USING btree (
  "hardware_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_device_location" ON "tenant_iot"."iot_devices" USING btree (
  "location_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_device_tenant" ON "tenant_iot"."iot_devices" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_device_topic" ON "tenant_iot"."iot_devices" USING btree (
  "mqtt_topic" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_devices
-- ----------------------------
CREATE TRIGGER "trg_iot_devices_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_devices"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Checks structure for table iot_devices
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_devices" ADD CONSTRAINT "ck_iot_hardware" CHECK (hardware_id = ANY (ARRAY[1, 2, 3, 4]));
ALTER TABLE "tenant_iot"."iot_devices" ADD CONSTRAINT "ck_iot_status" CHECK (status::text = ANY (ARRAY['online'::character varying, 'offline'::character varying, 'error'::character varying, 'maintenance'::character varying]::text[]));

-- ----------------------------
-- Primary Key structure for table iot_devices
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_devices" ADD CONSTRAINT "iot_devices_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_schedules
-- ----------------------------
CREATE INDEX "ix_iot_schedule_device" ON "tenant_iot"."iot_schedules" USING btree (
  "device_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table iot_schedules
-- ----------------------------
CREATE TRIGGER "trg_iot_schedules_updated_at" BEFORE UPDATE ON "tenant_iot"."iot_schedules"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_iot"();

-- ----------------------------
-- Primary Key structure for table iot_schedules
-- ----------------------------
ALTER TABLE "tenant_iot"."iot_schedules" ADD CONSTRAINT "iot_schedules_pkey" PRIMARY KEY ("id");
