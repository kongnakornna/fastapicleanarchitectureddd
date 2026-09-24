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

#!/usr/bin/env python3
"""
create_module_iot.py — iot Module Generator v2.1

สร้าง iot module ตาม Clean Architecture + DDD + Event-Driven
รองรับ 9 งาน:
  1. create_module       — สร้าง module structure (iot) 4 layers
  2. activate_module     — register router ใน app/app.py + models ใน migrations/env.py
  3. create_sql          — สร้าง SQL migrations V001/V002/V003
  4. update_app          — อัปเดต app/app.py
  5. update_env          — อัปเดต migrations/env.py
  6. create_migration    — สร้าง Alembic migration (8 tables + triggers + RLS)
  7. create_swagger      — สร้าง OpenAPI docs
  8. create_postman      — สร้าง Postman collection
  9. all                 — ทำทุกอย่าง

Usage:
    python create_module_iot.py <action> <module> [layer] [prefix] [options]

Examples:
    python create_module_iot.py all iot 6 iot
    python create_module_iot.py create iot 6 iot --force
    python create_module_iot.py sql iot iot
    python create_module_iot.py alembic iot iot
    python create_module_iot.py activate iot
    python create_module_iot.py update-env iot
    python create_module_iot.py help
"""
from __future__ import annotations

import argparse
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
LAYER_NAMES = {
    "0": "0-Core", "1": "1-Foundation", "2": "2-Money",
    "3": "3-Goods", "4": "4-Ops", "5": "5-Intel",
    "6": "6-Monitor", "7": "7-Template",
}

ACTIONS = {
    "create", "activate", "sql", "alembic",
    "swagger", "postman", "update", "update-env",
    "all", "help",
}

# ═══════════════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════════════
class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, project_root: Path, force: bool = False, backup: bool = True):
        self.root = project_root
        self.force = force
        self.backup = backup
        self.written: list[Path] = []
        self.skipped: list[Path] = []
        self.backups: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())
            self.backups.append(bak)
            ok(f"backup: {rel_path}.bak")

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class iotModuleGenerator:
    def __init__(
        self,
        project_root: Path,
        module: str = "iot",
        layer: str = "6",
        prefix: str = "iot",
        template: str = "A",
        force: bool = False,
    ):
        self.root = project_root
        self.module = module.lower()
        self.layer = layer
        self.prefix = prefix.lower()
        self.template = template
        self.layer_name = LAYER_NAMES.get(layer, "6-Monitor")
        self.writer = FileWriter(project_root, force=force)

        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.alembic_dir = "migrations/versions"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"

    # ───────────────────────────────────────────────────────────
    #  1. CREATE MODULE
    # ───────────────────────────────────────────────────────────
    def create_module(self) -> None:
        info(f"[CREATE] module: {self.module} (Layer {self.layer_name})")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN LAYER ───────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """iot domain layer — ชั้นโดเมน iot"""
            from .entities import (
                ActivityLog, AlarmLog, Device, DeviceAlert,
                DeviceConfig, DeviceStatus, iotData, Schedule,
            )
            from .enums import (
                AlarmStatus, AlertSeverity, DataSource,
                DeviceStatusEnum, HardwareType,
            )
            from .events import (
                AlarmRecovered, AlarmTriggered, ColdChainAlert,
                DeviceCreated, DeviceOffline, DeviceStatusChanged,
                iotDataReceived,
            )
            from .exceptions import (
                AlarmThresholdError, DeviceControlError,
                DeviceNotFoundError, DeviceOfflineError,
                InfluxDBQueryError, InvalidHardwareTypeError,
                iotError, MQTTNotConnectedError, ScheduleConflictError,
            )

            __all__ = [
                "ActivityLog", "AlarmLog", "Device", "DeviceAlert",
                "DeviceConfig", "DeviceStatus", "iotData", "Schedule",
                "AlarmStatus", "AlertSeverity", "DataSource",
                "DeviceStatusEnum", "HardwareType",
                "AlarmRecovered", "AlarmTriggered", "ColdChainAlert",
                "DeviceCreated", "DeviceOffline", "DeviceStatusChanged",
                "iotDataReceived",
                "AlarmThresholdError", "DeviceControlError",
                "DeviceNotFoundError", "DeviceOfflineError",
                "InfluxDBQueryError", "InvalidHardwareTypeError",
                "iotError", "MQTTNotConnectedError", "ScheduleConflictError",
            ]
        '''))

        self.writer.write(f"{base}/enums.py", dedent('''\
            """iot enums — Enum ของ iot"""
            from __future__ import annotations
            from enum import IntEnum, StrEnum


            class HardwareType(IntEnum):
                """TH: ประเภท hardware | EN: Hardware type"""
                SENSOR = 1
                IO_SENSOR = 2
                IO_CONTROL = 3
                CRITICAL_SENSOR = 4


            class AlarmStatus(IntEnum):
                """TH: สถานะ alarm | EN: Alarm status"""
                NORMAL = 5
                WARNING = 1
                CRITICAL = 2
                RECOVERY_WARNING = 3
                RECOVERY_CRITICAL = 4


            class DeviceStatusEnum(StrEnum):
                """TH: สถานะ device | EN: Device status"""
                ACTIVE = "ACTIVE"
                OFFLINE = "OFFLINE"
                MAINTENANCE = "MAINTENANCE"
                ERROR = "ERROR"


            class AlertSeverity(StrEnum):
                """TH: ระดับความรุนแรง | EN: Alert severity"""
                INFO = "info"
                LOW = "low"
                MEDIUM = "medium"
                HIGH = "high"
                CRITICAL = "critical"


            class DataSource(StrEnum):
                """TH: แหล่งข้อมูล | EN: Data source"""
                MQTT = "mqtt"
                CACHE = "cache"
                CACHE_FALLBACK = "cache_fallback"
                INFLUXDB = "influxdb"
                POSTGRES = "postgres"
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """iot domain exceptions — ข้อยกเว้นโดเมน iot"""
            from __future__ import annotations


            class iotError(Exception):
                """TH: base error | EN: base error"""


            class DeviceNotFoundError(iotError):
                """TH: ไม่พบ device | EN: device not found"""


            class DeviceOfflineError(iotError):
                """TH: device offline | EN: device offline"""


            class MQTTNotConnectedError(iotError):
                """TH: MQTT ไม่เชื่อมต่อ | EN: MQTT not connected"""


            class InvalidHardwareTypeError(iotError):
                """TH: hardware type ไม่ถูกต้อง | EN: invalid hardware type"""


            class AlarmThresholdError(iotError):
                """TH: threshold ผิดพลาด | EN: alarm threshold error"""


            class ScheduleConflictError(iotError):
                """TH: schedule ทับซ้อน | EN: schedule conflict"""


            class InfluxDBQueryError(iotError):
                """TH: InfluxDB query ล้มเหลว | EN: InfluxDB query failed"""


            class DeviceControlError(iotError):
                """TH: ส่งคำสั่ง control ล้มเหลว | EN: device control failed"""
        '''))

        self.writer.write(f"{base}/events.py", dedent('''\
            """iot domain events — เหตุการณ์โดเมน iot"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime


            @dataclass(frozen=True, slots=True)
            class DeviceCreated:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                device_name: str
                hardware_id: int
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class DeviceStatusChanged:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                old_status: str
                iot_status: str
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class iotDataReceived:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                raw_payload: str
                data_map: dict
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class AlarmTriggered:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                alarm_type: int
                alarm_status: int
                title: str
                subject: str
                value_data: float
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class AlarmRecovered:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                alarm_type: int
                recovery_status: int
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class DeviceOffline:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                last_seen: datetime
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


            @dataclass(frozen=True, slots=True)
            class ColdChainAlert:
                device_id: uuid.UUID
                tenant_id: uuid.UUID
                temperature: float
                threshold: float
                location_name: str
                occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """iot entities — เอนทิตี"""
            from app.modules.iot.domain.entities.activity_log import ActivityLog
            from app.modules.iot.domain.entities.alarm_log import AlarmLog
            from app.modules.iot.domain.entities.device import Device
            from app.modules.iot.domain.entities.device_alert import DeviceAlert
            from app.modules.iot.domain.entities.device_config import DeviceConfig
            from app.modules.iot.domain.entities.device_status import DeviceStatus
            from app.modules.iot.domain.entities.iot_data import iotData
            from app.modules.iot.domain.entities.schedule import Schedule

            __all__ = [
                "ActivityLog", "AlarmLog", "Device", "DeviceAlert",
                "DeviceConfig", "DeviceStatus", "iotData", "Schedule",
            ]
        '''))

        self.writer.write(f"{base}/entities/device.py", dedent('''\
            """Device entity — อุปกรณ์ iot"""
            from __future__ import annotations
            from sqlalchemy import Integer, String
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class Device(BaseModel):
                """TH: อุปกรณ์ iot | EN: iot device entity"""
                __tablename__ = "iot_devices"

                hardware_id: Mapped[int] = mapped_column(
                    Integer, name="hardware_id", comment="Hardware type (1-4)"
                )
                type_id: Mapped[int] = mapped_column(
                    Integer, name="type_id", default=0, comment="Device type ID"
                )
                location_id: Mapped[int] = mapped_column(
                    Integer, name="location_id", default=0, comment="Location ID"
                )
                device_sn: Mapped[str] = mapped_column(
                    String(100), name="device_sn", default="", comment="Serial number"
                )
                device_name: Mapped[str] = mapped_column(
                    String(255), name="device_name", comment="Device name"
                )
                device_type: Mapped[str] = mapped_column(
                    String(100), name="device_type", default="", comment="Device type"
                )
                location_name: Mapped[str] = mapped_column(
                    String(255), name="location_name", default="", comment="Location name"
                )
                mqtt_id: Mapped[int] = mapped_column(
                    Integer, name="mqtt_id", default=0, comment="MQTT config ID"
                )
                mqtt_main_id: Mapped[int] = mapped_column(
                    Integer, name="mqtt_main_id", default=0, comment="MQTT main broker ID"
                )
                mqtt_topic: Mapped[str] = mapped_column(
                    String(500), name="mqtt_topic", default="", comment="MQTT topic"
                )
                mqtt_name: Mapped[str] = mapped_column(
                    String(255), name="mqtt_name", default="", comment="MQTT display name"
                )
                mqtt_username: Mapped[str] = mapped_column(
                    String(255), name="mqtt_username", default="", comment="MQTT username"
                )
                mqtt_password: Mapped[str] = mapped_column(
                    String(255), name="mqtt_password", default="", comment="MQTT password"
                )
                unit: Mapped[str] = mapped_column(
                    String(50), name="unit", default="", comment="Measurement unit"
                )
                status: Mapped[str] = mapped_column(
                    String(50), name="status", default="offline", comment="Device status"
                )
                icon: Mapped[str] = mapped_column(
                    String(255), name="icon", default="", comment="Icon name"
                )
                icon_color: Mapped[str] = mapped_column(
                    String(50), name="icon_color", default="", comment="Icon color"
                )
                description: Mapped[str] = mapped_column(
                    String(500), name="description", default="", comment="Description"
                )
                firmware_version: Mapped[str] = mapped_column(
                    String(50), name="firmware_version", default="", comment="Firmware version"
                )
        '''))

        self.writer.write(f"{base}/entities/device_config.py", dedent('''\
            """DeviceConfig entity — config thresholds"""
            from __future__ import annotations
            from sqlalchemy import Float, Integer, String, UniqueConstraint
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class DeviceConfig(BaseModel):
                """TH: config ของ device | EN: device config"""
                __tablename__ = "iot_device_configs"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "device_id", name="uq_iot_config_device"),
                )

                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                max_value: Mapped[float] = mapped_column(Float, name="max_value", default=0.0)
                min_value: Mapped[float] = mapped_column(Float, name="min_value", default=0.0)
                warning_threshold: Mapped[float] = mapped_column(Float, name="warning_threshold", default=0.0)
                alert_threshold: Mapped[float] = mapped_column(Float, name="alert_threshold", default=0.0)
                recovery_warning: Mapped[float] = mapped_column(Float, name="recovery_warning", default=0.0)
                recovery_alert: Mapped[float] = mapped_column(Float, name="recovery_alert", default=0.0)
                calibration_offset: Mapped[float] = mapped_column(Float, name="calibration_offset", default=0.0)
                calibration_multiplier: Mapped[float] = mapped_column(Float, name="calibration_multiplier", default=1.0)
                mqtt_control_on: Mapped[str] = mapped_column(String(255), name="mqtt_control_on", default="")
                mqtt_control_off: Mapped[str] = mapped_column(String(255), name="mqtt_control_off", default="")
                action_name: Mapped[str] = mapped_column(String(255), name="action_name", default="")
                config_json: Mapped[str] = mapped_column(String(2000), name="config_json", default="{}")
        '''))

        self.writer.write(f"{base}/entities/device_status.py", dedent('''\
            """DeviceStatus entity — status ปัจจุบัน"""
            from __future__ import annotations
            from datetime import datetime
            from sqlalchemy import Boolean, DateTime, Float, Integer, String, UniqueConstraint
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class DeviceStatus(BaseModel):
                """TH: สถานะ device | EN: device status"""
                __tablename__ = "iot_device_statuses"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "device_id", name="uq_iot_status_device"),
                )

                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                is_online: Mapped[bool] = mapped_column(Boolean, name="is_online", default=False)
                last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
                last_value: Mapped[float] = mapped_column(Float, name="last_value", default=0.0)
                last_alarm: Mapped[int] = mapped_column(Integer, name="last_alarm", default=0)
                count_alarm: Mapped[int] = mapped_column(Integer, name="count_alarm", default=0)
                event: Mapped[int] = mapped_column(Integer, name="event", default=0)
                status: Mapped[str] = mapped_column(String(50), name="status", default="offline")
                sensor_data: Mapped[str] = mapped_column(String(500), name="sensor_data", default="")
                sensor_min: Mapped[float] = mapped_column(Float, name="sensor_min", default=0.0)
                sensor_max: Mapped[float] = mapped_column(Float, name="sensor_max", default=0.0)
                sensor_avg: Mapped[float] = mapped_column(Float, name="sensor_avg", default=0.0)
                battery: Mapped[float] = mapped_column(Float, name="battery", default=0.0)
                rssi: Mapped[int] = mapped_column(Integer, name="rssi", default=0)
        '''))

        self.writer.write(f"{base}/entities/device_alert.py", dedent('''\
            """DeviceAlert entity — alert"""
            from __future__ import annotations
            from sqlalchemy import Boolean, Float, Integer, String
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class DeviceAlert(BaseModel):
                """TH: alert ของ device | EN: device alert"""
                __tablename__ = "iot_device_alerts"

                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                alert_type: Mapped[str] = mapped_column(String(50), name="alert_type", default="")
                severity: Mapped[str] = mapped_column(String(20), name="severity", default="low")
                title: Mapped[str] = mapped_column(String(255), name="title", default="")
                message: Mapped[str] = mapped_column(String(1000), name="message", default="")
                value_data: Mapped[float] = mapped_column(Float, name="value_data", default=0.0)
                value_alarm: Mapped[float] = mapped_column(Float, name="value_alarm", default=0.0)
                resolved: Mapped[bool] = mapped_column(Boolean, name="resolved", default=False)
                acknowledged: Mapped[bool] = mapped_column(Boolean, name="acknowledged", default=False)
        '''))

        self.writer.write(f"{base}/entities/iot_data.py", dedent('''\
            """iotData entity — time-series data"""
            from __future__ import annotations
            from datetime import datetime
            from sqlalchemy import DateTime, Integer, Text
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class iotData(BaseModel):
                """TH: ข้อมูล iot | EN: iot data record"""
                __tablename__ = "iot_data"

                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                data_json: Mapped[str] = mapped_column(Text, name="data_json", default="{}")
                timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
                location_id: Mapped[int] = mapped_column(Integer, name="location_id", default=0)
                metadata_json: Mapped[str] = mapped_column(Text, name="metadata_json", default="{}")
        '''))

        self.writer.write(f"{base}/entities/alarm_log.py", dedent('''\
            """AlarmLog entity — alarm history"""
            from __future__ import annotations
            from sqlalchemy import Float, Integer, String, Text
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class AlarmLog(BaseModel):
                """TH: log ของ alarm | EN: alarm log"""
                __tablename__ = "iot_alarm_logs"

                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                alarm_action_id: Mapped[int] = mapped_column(Integer, name="alarm_action_id", default=0)
                alarm_type: Mapped[int] = mapped_column(Integer, name="alarm_type", default=0)
                alarm_status: Mapped[int] = mapped_column(Integer, name="alarm_status", default=0)
                value_data: Mapped[float] = mapped_column(Float, name="value_data", default=0.0)
                value_alarm: Mapped[float] = mapped_column(Float, name="value_alarm", default=0.0)
                title: Mapped[str] = mapped_column(String(255), name="title", default="")
                subject: Mapped[str] = mapped_column(String(500), name="subject", default="")
                content: Mapped[str] = mapped_column(Text, name="content", default="")
                data_alarm: Mapped[int] = mapped_column(Integer, name="data_alarm", default=0)
                data_alarm_raw: Mapped[int] = mapped_column(Integer, name="data_alarm_raw", default=0)
                event_control: Mapped[int] = mapped_column(Integer, name="event_control", default=0)
                message_mqtt_control: Mapped[str] = mapped_column(String(500), name="message_mqtt_control", default="")
        '''))

        self.writer.write(f"{base}/entities/activity_log.py", dedent('''\
            """ActivityLog entity — activity audit"""
            from __future__ import annotations
            from sqlalchemy import Integer, String, Text
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class ActivityLog(BaseModel):
                """TH: activity log | EN: activity log"""
                __tablename__ = "iot_activity_logs"

                log_type: Mapped[str] = mapped_column(String(50), name="log_type", default="")
                device_id: Mapped[int] = mapped_column(Integer, name="device_id", default=0)
                user_id: Mapped[int] = mapped_column(Integer, name="user_id", default=0)
                severity: Mapped[str] = mapped_column(String(20), name="severity", default="info")
                data_json: Mapped[str] = mapped_column(Text, name="data_json", default="{}")
                description: Mapped[str] = mapped_column(Text, name="description", default="")
        '''))

        self.writer.write(f"{base}/entities/schedule.py", dedent('''\
            """Schedule entity — ตารางเวลา control"""
            from __future__ import annotations
            from sqlalchemy import Boolean, Integer, String
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.shared.infrastructure.models import BaseModel


            class Schedule(BaseModel):
                """TH: ตารางเวลา | EN: schedule"""
                __tablename__ = "iot_schedules"

                schedule_id: Mapped[int] = mapped_column(Integer, name="schedule_id", default=0)
                device_id: Mapped[int] = mapped_column(Integer, name="device_id")
                start_time: Mapped[str] = mapped_column(String(10), name="start_time", default="")
                end_time: Mapped[str] = mapped_column(String(10), name="end_time", default="")
                event: Mapped[str] = mapped_column(String(50), name="event", default="")
                monday: Mapped[bool] = mapped_column(Boolean, default=False)
                tuesday: Mapped[bool] = mapped_column(Boolean, default=False)
                wednesday: Mapped[bool] = mapped_column(Boolean, default=False)
                thursday: Mapped[bool] = mapped_column(Boolean, default=False)
                friday: Mapped[bool] = mapped_column(Boolean, default=False)
                saturday: Mapped[bool] = mapped_column(Boolean, default=False)
                sunday: Mapped[bool] = mapped_column(Boolean, default=False)
        '''))

        # ─── value_objects ───────────────────────────
        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """iot value objects"""
            from app.modules.iot.domain.value_objects.alarm import (
                AlarmDetailDTO, AlarmDetailResult,
                InfluxDBConfig, Location, MQTTConfig,
            )
            from app.modules.iot.domain.value_objects.location import LocationConfig
            from app.modules.iot.domain.value_objects.mqtt import (
                MQTTDeviceInfo, MQTTTopicData,
            )

            __all__ = [
                "AlarmDetailDTO", "AlarmDetailResult",
                "InfluxDBConfig", "Location", "MQTTConfig",
                "LocationConfig",
                "MQTTDeviceInfo", "MQTTTopicData",
            ]
        '''))

        self.writer.write(f"{base}/value_objects/alarm.py", dedent('''\
            """Alarm value objects"""
            from __future__ import annotations
            from dataclasses import dataclass
            from typing import Any


            @dataclass(frozen=True)
            class AlarmDetailDTO:
                """TH: alarm input | EN: alarm input DTO"""
                hardware_id: Any
                value_data: Any
                value_alarm: Any
                value_relay: Any = None
                value_control_relay: Any = None
                max_value: Any = None
                min_value: Any = None
                status_alert: Any = None
                status_warning: Any = None
                recovery_warning: Any = None
                recovery_alert: Any = None
                device_name: str = ""
                action_name: str = ""
                mqtt_name: str = ""
                mqtt_control_on: str = ""
                mqtt_control_off: str = ""
                count_alarm: Any = 0
                event: Any = 0
                unit: str = ""
                sensor_value_data: Any = None


            @dataclass(frozen=True)
            class AlarmDetailResult:
                """TH: alarm output | EN: alarm output DTO"""
                status: int
                status_control: int
                alarm_type_id: int
                type_id: int
                hardware_id: int
                alarm_status_set: int
                title: str
                subject: str
                content: str
                value_data: Any
                value_alarm: Any
                value_relay: Any
                value_control_relay: Any
                data_alarm: int
                data_alarm_raw: int
                max_value: Any
                min_value: Any
                event_control: int
                message_mqtt_control: str
                sensor_data: Any
                count_alarm: int
                mqtt_name: str
                mqtt_name_str: str
                device_name_str: str
                mqtt_control_on_str: str
                unit: str
                sensor_value: Any
                status_alert_val: int = 0
                status_warning_val: int = 0
                recovery_warning_val: int = 0
                recovery_alert_val: int = 0
                device_name_val: str = ""
                alarm_action_name: str = ""
                mqtt_control_on_val: str = ""
                mqtt_control_off_val: str = ""
                event_val: int = 0
                timestamp: str = ""
                lang: str = ""


            @dataclass(frozen=True)
            class MQTTConfig:
                """TH: MQTT config | EN: MQTT config VO"""
                broker: str
                client_id: str = ""
                username: str = ""
                password: str = ""
                keepalive: int = 30
                clean_session: bool = True


            @dataclass(frozen=True)
            class InfluxDBConfig:
                """TH: InfluxDB config | EN: InfluxDB config VO"""
                url: str
                token: str
                org: str
                bucket: str
                timeout: int = 30


            @dataclass(frozen=True)
            class Location:
                """TH: location | EN: location VO"""
                location_id: int = 0
                location_name: str = ""
                config_data: str = ""
        '''))

        self.writer.write(f"{base}/value_objects/location.py", dedent('''\
            """Location value object"""
            from __future__ import annotations
            from dataclasses import dataclass


            @dataclass(frozen=True)
            class LocationConfig:
                """TH: location config | EN: location config VO"""
                location_id: int = 0
                location_name: str = ""
                latitude: float = 0.0
                longitude: float = 0.0
                config_data: str = ""
        '''))

        self.writer.write(f"{base}/value_objects/mqtt.py", dedent('''\
            """MQTT value objects"""
            from __future__ import annotations
            from dataclasses import dataclass


            @dataclass(frozen=True)
            class MQTTTopicData:
                """TH: MQTT topic data | EN: MQTT topic data VO"""
                topic: str
                payload: dict
                timestamp: float = 0.0


            @dataclass(frozen=True)
            class MQTTDeviceInfo:
                """TH: MQTT device info | EN: MQTT device info VO"""
                device_id: int
                topic: str
                name: str = ""
                broker: str = ""
                username: str = ""
                password: str = ""
        '''))

        # ─── helpers ─────────────────────────────────
        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """iot domain helpers"""
            from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm

            __all__ = ["evaluate_alarm"]
        '''))

        self.writer.write(f"{base}/helpers/alarm_logic.py", dedent('''\
            """Alarm evaluation logic — ประเมิน threshold"""
            from __future__ import annotations
            from typing import Any

            from app.modules.iot.domain.value_objects.alarm import (
                AlarmDetailDTO, AlarmDetailResult,
            )

            _THAI_MESSAGES: dict[str, str] = {
                "warning": "คำเตือน มีความผิดปกติ",
                "critical": "ภาวะวิกฤตต้องแก้ไขทันที",
                "recovery_warning": "คืนสู่ภาวะปกติ (คำเตือน)",
                "recovery_critical": "คืนสู่ภาวะปกติ (วิกฤต)",
                "normal": "ปกติ",
                "critical_max": "วิกฤต มีค่าสูงเกินกำหนด",
                "critical_min": "วิกฤต มีค่าต่ำกว่ากำหนด",
            }

            _ENGLISH_MESSAGES: dict[str, str] = {
                "warning": "Warning", "critical": "Critical",
                "recovery_warning": "Recovery Warning",
                "recovery_critical": "Recovery Critical",
                "normal": "Normal",
                "critical_max": "Critical! Maximum limit.",
                "critical_min": "Critical! Minimum limit",
            }


            def _to_int(value: Any) -> int:
                if value is None:
                    return 0
                try:
                    return int(float(str(value)))
                except (ValueError, TypeError):
                    return 0


            def _to_float(value: Any) -> float:
                if value is None:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0


            def _normalize_sensor_value(value: Any) -> Any:
                if isinstance(value, str):
                    if value.upper() in ("ON", "OFF"):
                        return value.upper()
                    try:
                        return float(value)
                    except ValueError:
                        return value
                return value


            def evaluate_alarm(
                dto: AlarmDetailDTO, lang: str = "th",
            ) -> AlarmDetailResult:
                """TH: ประเมิน alarm | EN: Evaluate alarm"""
                messages = _THAI_MESSAGES if lang == "th" else _ENGLISH_MESSAGES

                hardware_id = _to_int(dto.hardware_id)
                type_id = hardware_id
                sensor_value = _normalize_sensor_value(dto.value_data)
                max_val = _to_float(dto.max_value)
                min_val = _to_float(dto.min_value)
                status_alert = _to_int(dto.status_alert)
                status_warning = _to_int(dto.status_warning)
                recovery_warning = _to_int(dto.recovery_warning)
                recovery_alert = _to_int(dto.recovery_alert)
                count_alarm = _to_int(dto.count_alarm)
                event = _to_int(dto.event)

                unit = dto.unit
                mqtt_name = dto.mqtt_name
                device_name = dto.device_name
                alarm_action_name = dto.action_name
                mqtt_control_on = dto.mqtt_control_on
                mqtt_control_off = dto.mqtt_control_off
                value_alarm = dto.value_alarm
                value_relay = dto.value_relay
                value_control_relay = dto.value_control_relay

                sensor_data: Any = None
                value_data: Any = None

                if hardware_id == 1:
                    sensor_data = dto.value_data
                    value_data = dto.value_data
                elif hardware_id == 2:
                    if _to_int(dto.value_alarm) == 1:
                        sensor_data = 1
                        value_data = 1
                        sensor_value = 1
                    else:
                        sensor_data = _to_int(dto.value_alarm)
                        value_data = _to_int(dto.value_alarm)
                        sensor_value = _to_int(dto.value_alarm)
                elif hardware_id == 3:
                    sensor_data = _to_int(dto.value_alarm)
                    value_data = dto.value_data
                    sensor_value = dto.value_data
                elif hardware_id == 4:
                    sensor_data = dto.value_data
                    value_data = dto.value_data
                else:
                    sensor_data = _to_int(dto.value_alarm)
                    value_data = dto.value_data

                alarm_status_set = 999
                data_alarm = 0
                data_alarm_raw = 0
                event_control = event
                message_mqtt_control = mqtt_control_off
                if event == 1:
                    message_mqtt_control = mqtt_control_on

                status = 5
                title = messages["normal"]
                subject = messages["normal"]
                content = messages["normal"] + " "

                if hardware_id == 3 and sensor_value in (1, 0, "ON", "OFF", "on", "off"):
                    alarm_status_set = 999
                    title = messages["normal"]
                    subject = messages["normal"]
                    content = f"{messages['normal']} {sensor_value} {unit}"
                    status = 5

                elif hardware_id == 4 and sensor_value != 1:
                    alarm_status_set = 2
                    title = messages["critical"]
                    subject = f"{mqtt_name} {messages['critical']} {device_name} : {sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['critical']} {device_name} :{sensor_value} {unit}"
                    data_alarm = status_warning
                    data_alarm_raw = status_warning
                    status = 2

                elif hardware_id == 4 and sensor_value == 1:
                    alarm_status_set = 999
                    title = messages["normal"]
                    subject = messages["normal"]
                    content = f"{messages['normal']} {sensor_value} {unit}"
                    status = 5

                elif max_val != 0 and _to_float(sensor_value) >= max_val and hardware_id in (1, 2):
                    alarm_status_set = 2
                    title = messages["critical_max"]
                    subject = f"{mqtt_name} {messages['critical_max']} {device_name} : {sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['critical_max']} {device_name} :{sensor_value} {unit}"
                    data_alarm = status_warning
                    data_alarm_raw = status_warning
                    status = 2

                elif min_val != 0 and _to_float(sensor_value) <= min_val and hardware_id in (1, 2):
                    alarm_status_set = 1
                    title = messages["critical_min"]
                    subject = f"{mqtt_name} {messages['critical_min']} {device_name} : {sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['critical_min']} {device_name} :{sensor_value} {unit}"
                    data_alarm = status_warning
                    data_alarm_raw = status_warning
                    status = 1

                elif (hardware_id == 1 and status_warning > 0
                      and _to_float(sensor_value) >= float(status_warning)
                      and _to_float(sensor_value) < float(status_alert)):
                    alarm_status_set = 1
                    title = messages["warning"]
                    subject = f"{mqtt_name} {messages['warning']} : {device_name} : {sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['warning']}: {device_name} :{sensor_value} {unit}"
                    data_alarm = status_warning
                    data_alarm_raw = status_warning
                    status = 1

                elif (hardware_id == 1 and status_alert > 0
                      and _to_float(sensor_value) >= float(status_alert)):
                    alarm_status_set = 2
                    title = messages["critical"]
                    subject = f"{mqtt_name} {messages['critical']} : {device_name} :{sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['critical']}: {device_name} :{sensor_value} {unit}"
                    data_alarm = status_alert
                    data_alarm_raw = status_alert
                    status = 2

                elif _to_int(value_alarm) == 0 and hardware_id in (2, 3, 4):
                    is_critical = hardware_id == 4
                    if is_critical:
                        alarm_status_set = 2
                        title = messages["critical"]
                    else:
                        alarm_status_set = 1
                        title = messages["warning"]
                    subject = f"{mqtt_name} {title} : {device_name} : {sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {title}: {device_name} :{sensor_value} {unit}"
                    if is_critical:
                        data_alarm = status_alert
                        data_alarm_raw = status_alert
                    else:
                        data_alarm = status_warning
                        data_alarm_raw = status_warning
                    status = 2 if is_critical else 1

                elif (count_alarm >= 1 and recovery_warning > 0
                      and _to_float(sensor_value) <= float(recovery_warning)
                      and hardware_id in (1, 2)):
                    alarm_status_set = 3
                    title = messages["recovery_warning"]
                    subject = f"{mqtt_name} {messages['recovery_warning']} : {device_name} :{sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['recovery_warning']}: {device_name} :{sensor_value} {unit}"
                    data_alarm = recovery_warning
                    data_alarm_raw = recovery_warning
                    event_control = 0
                    if event == 1:
                        event_control = 1
                        message_mqtt_control = mqtt_control_off
                    else:
                        message_mqtt_control = mqtt_control_on
                    status = 3

                elif (count_alarm >= 1 and recovery_alert > 0
                      and _to_float(sensor_value) <= float(recovery_alert)
                      and hardware_id in (1, 2)):
                    alarm_status_set = 4
                    title = f"{mqtt_name} {messages['recovery_critical']}"
                    subject = f"{mqtt_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
                    data_alarm = recovery_alert
                    data_alarm_raw = recovery_alert
                    event_control = 0
                    if event == 1:
                        event_control = 1
                        message_mqtt_control = mqtt_control_off
                    else:
                        message_mqtt_control = mqtt_control_on
                    status = 4

                elif (count_alarm >= 1 and _to_int(value_alarm) >= 1
                      and hardware_id in (2, 3, 4)):
                    alarm_status_set = 4
                    title = f"{mqtt_name} {messages['recovery_critical']}"
                    subject = f"{mqtt_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
                    content = f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
                    data_alarm = recovery_alert
                    data_alarm_raw = recovery_alert
                    event_control = 0
                    if event == 1:
                        event_control = 1
                        message_mqtt_control = mqtt_control_off
                    else:
                        message_mqtt_control = mqtt_control_on
                    status = 4

                else:
                    alarm_status_set = 999
                    title = messages["normal"]
                    subject = messages["normal"]
                    content = messages["normal"] + " "
                    data_alarm = 0
                    data_alarm_raw = 0
                    status = 5

                return AlarmDetailResult(
                    status=status, status_control=status,
                    alarm_type_id=hardware_id, type_id=type_id,
                    hardware_id=hardware_id, alarm_status_set=alarm_status_set,
                    title=title, subject=subject, content=content,
                    value_data=value_data, value_alarm=value_alarm,
                    value_relay=value_relay, value_control_relay=value_control_relay,
                    data_alarm=data_alarm, data_alarm_raw=data_alarm_raw,
                    max_value=max_val, min_value=min_val,
                    event_control=event_control, message_mqtt_control=message_mqtt_control,
                    sensor_data=sensor_data, count_alarm=count_alarm,
                    mqtt_name=mqtt_name, mqtt_name_str=mqtt_name,
                    device_name_str=device_name, mqtt_control_on_str=mqtt_control_on,
                    unit=unit, sensor_value=sensor_value,
                    status_alert_val=status_alert, status_warning_val=status_warning,
                    recovery_warning_val=recovery_warning, recovery_alert_val=recovery_alert,
                    device_name_val=device_name, alarm_action_name=alarm_action_name,
                    mqtt_control_on_val=mqtt_control_on,
                    mqtt_control_off_val=mqtt_control_off,
                    event_val=event, timestamp="", lang=lang,
                )
        '''))

    # ─── APPLICATION LAYER ──────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """iot application layer — ชั้นแอปพลิเคชัน iot"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """iot application exceptions"""
            from __future__ import annotations


            class ApplicationError(Exception):
                """TH: base | EN: base"""


            class DeviceNotFoundAppError(ApplicationError):
                """TH: ไม่พบ device | EN: device not found"""


            class DuplicateDeviceError(ApplicationError):
                """TH: device ซ้ำ | EN: duplicate device"""


            class MQTTNotConnectedAppError(ApplicationError):
                """TH: MQTT ไม่เชื่อมต่อ | EN: MQTT not connected"""


            class InfluxDBQueryAppError(ApplicationError):
                """TH: InfluxDB query ล้มเหลว | EN: InfluxDB query failed"""
        '''))

        self.writer.write(f"{base}/interfaces.py", dedent('''\
            """iot application ports — อินเทอร์เฟซ"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from typing import Any, Protocol

            from app.modules.iot.domain.entities import (
                ActivityLog, AlarmLog, Device, DeviceAlert,
                DeviceConfig, DeviceStatus, iotData, Schedule,
            )


            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> uuid.UUID | None: ...


            class DeviceRepository(ABC):
                @abstractmethod
                async def save(self, ctx: RequestContext, device: Device) -> Device: ...
                @abstractmethod
                async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> Device | None: ...
                @abstractmethod
                async def find_by_hardware_id(self, ctx: RequestContext, hardware_id: int) -> Device | None: ...
                @abstractmethod
                async def find_by_mqtt_topic(self, ctx: RequestContext, topic: str) -> Device | None: ...
                @abstractmethod
                async def find_by_location(self, ctx: RequestContext, location_id: int) -> list[Device]: ...
                @abstractmethod
                async def find_all_active(self, ctx: RequestContext) -> list[Device]: ...
                @abstractmethod
                async def find_all_paginated(
                    self, ctx: RequestContext, page: int, page_size: int,
                ) -> tuple[list[Device], int]: ...
                @abstractmethod
                async def update(self, ctx: RequestContext, device: Device) -> Device: ...
                @abstractmethod
                async def delete(self, ctx: RequestContext, id: uuid.UUID) -> bool: ...


            class DeviceConfigRepository(ABC):
                @abstractmethod
                async def find_by_device_id(
                    self, ctx: RequestContext, device_id: int,
                ) -> DeviceConfig | None: ...
                @abstractmethod
                async def upsert(
                    self, ctx: RequestContext, config: DeviceConfig,
                ) -> DeviceConfig: ...


            class DeviceStatusRepository(ABC):
                @abstractmethod
                async def find_by_device_id(
                    self, ctx: RequestContext, device_id: int,
                ) -> DeviceStatus | None: ...
                @abstractmethod
                async def upsert(
                    self, ctx: RequestContext, status: DeviceStatus,
                ) -> DeviceStatus: ...
                @abstractmethod
                async def update_last_seen(
                    self, ctx: RequestContext, device_id: int,
                ) -> None: ...


            class DeviceAlertRepository(ABC):
                @abstractmethod
                async def create(
                    self, ctx: RequestContext, alert: DeviceAlert,
                ) -> DeviceAlert: ...
                @abstractmethod
                async def find_unresolved(
                    self, ctx: RequestContext, device_id: int,
                ) -> list[DeviceAlert]: ...
                @abstractmethod
                async def resolve(
                    self, ctx: RequestContext, alert_id: uuid.UUID,
                ) -> DeviceAlert | None: ...


            class iotDataRepository(ABC):
                @abstractmethod
                async def create(
                    self, ctx: RequestContext, data: iotData,
                ) -> iotData: ...
                @abstractmethod
                async def find_latest(
                    self, ctx: RequestContext, device_id: int, limit: int,
                ) -> list[iotData]: ...
                @abstractmethod
                async def find_by_date_range(
                    self, ctx: RequestContext, device_id: int,
                    start: str, end: str,
                ) -> list[iotData]: ...
                @abstractmethod
                async def find_paginated(
                    self, ctx: RequestContext, page: int, page_size: int,
                ) -> tuple[list[iotData], int]: ...
                @abstractmethod
                async def cleanup_old(
                    self, ctx: RequestContext, days: int,
                ) -> int: ...


            class AlarmLogRepository(ABC):
                @abstractmethod
                async def create(
                    self, ctx: RequestContext, log: AlarmLog,
                ) -> AlarmLog: ...
                @abstractmethod
                async def count_by_device(
                    self, ctx: RequestContext, device_id: int,
                ) -> int: ...
                @abstractmethod
                async def find_by_device(
                    self, ctx: RequestContext, device_id: int, limit: int,
                ) -> list[AlarmLog]: ...


            class ActivityLogRepository(ABC):
                @abstractmethod
                async def create(
                    self, ctx: RequestContext, log: ActivityLog,
                ) -> ActivityLog: ...


            class ScheduleRepository(ABC):
                @abstractmethod
                async def find_active_schedules(
                    self, ctx: RequestContext,
                ) -> list[Schedule]: ...
                @abstractmethod
                async def find_by_device_id(
                    self, ctx: RequestContext, device_id: int,
                ) -> list[Schedule]: ...


            class MQTTClient(Protocol):
                def is_connected(self) -> bool: ...
                def publish(self, topic: str, message: str, qos: int = 1) -> bool: ...
                def get_data_from_topic(self, topic: str, timeout: int = 5) -> str | None: ...


            class InfluxDBClient(Protocol):
                def query_filter_data(self, params: Any) -> list[dict]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...


            class IdempotencyStore(ABC):
                @abstractmethod
                async def check_or_lock(
                    self, key: str, scope: str, payload: dict[str, Any],
                ) -> dict[str, Any] | None: ...
                @abstractmethod
                async def complete(
                    self, key: str, scope: str,
                    status: int, body: dict[str, Any],
                ) -> None: ...


            class InventoryCache(ABC):
                @abstractmethod
                async def get(self, key: str) -> Any | None: ...
                @abstractmethod
                async def set(self, key: str, value: Any, ttl: int = 300) -> bool: ...
                @abstractmethod
                async def invalidate(self, key: str) -> bool: ...


            class AlertService(ABC):
                @abstractmethod
                async def send_alert(self, notification: Any) -> dict[str, bool]: ...
        '''))

        self.writer.write(f"{base}/mappers.py", dedent('''\
            """iot mappers — ORM ↔ domain"""
            from __future__ import annotations
            from typing import Any


            def device_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "device_id": str(row.id),
                    "device_name": row.device_name,
                    "hardware_id": row.hardware_id,
                    "type_id": row.type_id,
                    "unit": row.unit,
                    "status": row.status,
                    "location_name": row.location_name,
                }


            def alarm_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "device_id": str(row.device_id),
                    "alarm_type": row.alarm_type,
                    "alarm_status": row.alarm_status,
                    "title": row.title,
                    "subject": row.subject,
                    "value_data": row.value_data,
                    "created_at": row.created_at.isoformat() if row.created_at else "",
                }
        '''))

        self.writer.write(f"{base}/utils.py", dedent('''\
            """iot application utils"""
            from __future__ import annotations
            from typing import Any


            def parse_csv_payload(raw: str) -> dict[str, Any]:
                """TH: parse CSV payload → dict | EN: parse CSV payload"""
                result: dict[str, Any] = {}
                for i, val in enumerate(raw.split(",")):
                    trimmed = val.strip()
                    try:
                        result[str(i)] = float(trimmed)
                    except ValueError:
                        result[str(i)] = trimmed
                result["raw"] = raw
                return result


            def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
                """TH: ทำความสะอาด payload | EN: sanitize payload"""
                MASK = {"password", "token", "secret", "mqtt_password"}
                return {k: ("***" if k in MASK else v) for k, v in data.items()}
        '''))

        # use_case.py — full content (จากไฟล์ต้นฉบับ)
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _use_case_content(self) -> str:
        """use_case.py content — แยกออกมาเพราะยาวมาก"""
        return dedent('''\
            """iot use cases — กรณีการใช้งาน iot"""
            from __future__ import annotations

            import contextlib
            import csv
            import io
            import json
            from datetime import UTC, datetime, timedelta
            from typing import Any

            from loguru import logger

            from app.modules.iot.domain.entities import iotData
            from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
            from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO

            MQTTClient = Any
            RedisClient = Any
            InfluxDBClient = Any


            class iotUseCase:
                """iot use cases — รวมทุก operation"""

                def __init__(
                    self,
                    device_repository: Any,
                    device_config_repository: Any,
                    device_status_repository: Any,
                    device_alert_repository: Any,
                    iot_data_repository: Any,
                    alarm_log_repository: Any,
                    activity_log_repository: Any,
                    mqtt_client: MQTTClient | None = None,
                    influxdb_client: InfluxDBClient | None = None,
                    redis_client: RedisClient | None = None,
                ) -> None:
                    self._device_repo = device_repository
                    self._device_config_repo = device_config_repository
                    self._device_status_repo = device_status_repository
                    self._device_alert_repo = device_alert_repository
                    self._iot_data_repo = iot_data_repository
                    self._alarm_log_repo = alarm_log_repository
                    self._activity_log_repo = activity_log_repository
                    self._mqtt_client = mqtt_client
                    self._influxdb_client = influxdb_client
                    self._redis_client = redis_client

                def is_connected(self) -> bool:
                    if self._mqtt_client is None:
                        return False
                    return self._mqtt_client.is_connected()

                def is_cache_enabled(self) -> bool:
                    return self._redis_client is not None

                async def get_topic_data(
                    self, topic: str, del_cache: bool = False,
                ) -> dict[str, Any]:
                    cache_key = f"mqtt_topic:{topic}"
                    cache_enabled = self.is_cache_enabled()

                    if cache_enabled and del_cache:
                        try:
                            self._redis_client.delete(cache_key)
                        except Exception as exc:
                            logger.warning(f"cache delete failed: {exc}")

                    if cache_enabled and not del_cache:
                        try:
                            cached = self._redis_client.get(cache_key)
                            if cached:
                                payload = (
                                    json.loads(cached)
                                    if isinstance(cached, (str, bytes))
                                    else cached
                                )
                                return {"topic": topic, "payload": payload,
                                        "from": "cache", "cache": True}
                        except Exception:
                            pass

                    if self._mqtt_client is None or not self._mqtt_client.is_connected():
                        return {"topic": topic, "payload": None,
                                "from": "mqtt_disconnected", "cache": False}

                    try:
                        data = self._mqtt_client.get_data_from_topic(topic, timeout=5)
                        if data:
                            payload = json.loads(data) if isinstance(data, str) else data
                            if cache_enabled:
                                with contextlib.suppress(Exception):
                                    self._redis_client.set(
                                        cache_key,
                                        json.dumps(payload) if isinstance(payload, dict) else str(payload),
                                        ex=10,
                                    )
                            return {"topic": topic, "payload": payload,
                                    "from": "mqtt", "cache": False}
                    except Exception as exc:
                        logger.warning(f"MQTT fetch failed: {exc}")

                    if cache_enabled:
                        try:
                            cached = self._redis_client.get(cache_key)
                            if cached:
                                payload = (
                                    json.loads(cached)
                                    if isinstance(cached, (str, bytes))
                                    else cached
                                )
                                return {"topic": topic, "payload": payload,
                                        "from": "cache_fallback", "cache": True}
                        except Exception:
                            pass

                    return {"topic": topic, "payload": None,
                            "from": "mqtt_error", "cache": False}

                async def device_control(self, topic: str, message: str) -> bool:
                    if self._mqtt_client is None or not self._mqtt_client.is_connected():
                        return False
                    return self._mqtt_client.publish(topic, message, qos=1)

                async def device_controls(self, topic: str, message: str) -> bool:
                    return await self.device_control(topic, message)

                async def get_device_list(
                    self, bucket: str = "", hardware_id: int = 0,
                    page: int = 1, page_size: int = 20,
                ) -> tuple[list[Any], int]:
                    return await self._device_repo.find_all_paginated(page, page_size)

                async def get_device_list_page(
                    self, bucket: str = "", hardware_id: int = 0,
                    page: int = 1, page_size: int = 20,
                ) -> tuple[list[Any], int]:
                    return await self.get_device_list(bucket, hardware_id, page, page_size)

                async def get_device_list_by_location(self, location_id: int) -> list[Any]:
                    return await self._device_repo.find_by_location(location_id)

                async def get_senser_charts(
                    self, measurement: str = "temperature",
                    field: str = "value", bucket: str = "iot_sensors",
                    start: str = "-1h", stop: str = "now()", limit: int = 1000,
                ) -> dict[str, Any]:
                    if self._influxdb_client is None:
                        return {"data": [], "date": [], "cache": "no cache"}
                    try:
                        from app.core.influxdb_client import QueryParams
                        params = QueryParams(
                            measurement=measurement, field=field, bucket=bucket,
                            start=start, stop=stop, limit=limit,
                        )
                        results = self._influxdb_client.query_filter_data(params)
                        data_points: list[float] = []
                        time_points: list[str] = []
                        for record in results:
                            if "_value" in record:
                                data_points.append(float(record["_value"]))
                            if "_time" in record:
                                time_points.append(str(record["_time"]))
                        return {"data": data_points, "date": time_points, "cache": "no cache"}
                    except Exception as exc:
                        logger.error(f"InfluxDB failed: {exc}")
                        return {"data": [], "date": [], "cache": "error", "error": str(exc)}

                async def get_senser_data_chart(self, **kwargs: Any) -> dict[str, Any]:
                    return await self.get_senser_charts(**kwargs)

                async def get_senser_data(self, **kwargs: Any) -> dict[str, Any]:
                    return await self.get_senser_charts(**kwargs)

                async def get_device_senser_charts(self, **kwargs: Any) -> dict[str, Any]:
                    return await self.get_senser_charts(**kwargs)

                async def get_alarm_device_status(
                    self, bucket: str = "iot_sensors",
                    page: int = 1, page_size: int = 1000,
                    measurement: str = "temperature", **filters: Any,
                ) -> dict[str, Any]:
                    mqtt_connected = self.is_connected()
                    check_connection_mqtt = {
                        "isConnected": mqtt_connected,
                        "connected": mqtt_connected,
                        "status": 1 if mqtt_connected else 0,
                        "msg": "MQTT Connection Status: Connected" if mqtt_connected
                               else "MQTT Connection Status: Disconnected",
                    }
                    devices = await self._device_repo.find_all_active()
                    device_sensors = [d for d in devices if d.hardware_id == 1]
                    device_io = [d for d in devices if d.hardware_id == 2]
                    device_io_info = [
                        {"device_id": str(dev.id), "type_id": dev.type_id,
                         "status": dev.status, "device_name": dev.device_name,
                         "timestamp": datetime.now(UTC).isoformat(),
                         "subject": "", "value_data": 0, "data_alarm": 0,
                         "event_control": 1, "value_data_msg": ""}
                        for dev in devices
                    ]
                    mqtt_data: dict[str, Any] = {}
                    mqttrs: dict[str, Any] = {
                        "case": 0, "status": 0, "msg": "No data available",
                        "fromCache": False, "time": 0,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "isConnected": mqtt_connected,
                    }
                    if mqtt_connected and devices:
                        first_dev = devices[0]
                        topic = first_dev.mqtt_topic or f"{bucket}/DATA"
                        try:
                            payload = self._mqtt_client.get_data_from_topic(topic, timeout=5)
                            if payload:
                                for i, val in enumerate(str(payload).split(",")):
                                    trimmed = val.strip()
                                    try:
                                        mqtt_data[str(i)] = float(trimmed)
                                    except ValueError:
                                        mqtt_data[str(i)] = trimmed
                                mqttrs = {
                                    "case": 1, "status": 1, "msg": str(payload),
                                    "fromCache": False, "time": 0,
                                    "timestamp": datetime.now(UTC).isoformat(),
                                    "isConnected": mqtt_connected,
                                }
                        except Exception as exc:
                            logger.warning(f"MQTT failed: {exc}")
                    chart_data: dict[str, Any] = {
                        "bucket": bucket, "field": "value", "info": {},
                        "data": [], "date": [], "name": "value", "cache": "no cache",
                    }
                    if self._influxdb_client:
                        now = datetime.now(UTC)
                        start = (now - timedelta(minutes=15)).isoformat()
                        stop = now.isoformat()
                        try:
                            from app.core.influxdb_client import QueryParams
                            params = QueryParams(
                                measurement=measurement, field="value", bucket=bucket,
                                start=start, stop=stop, limit=150,
                            )
                            results = self._influxdb_client.query_filter_data(params)
                            data_points: list[float] = []
                            time_points: list[str] = []
                            for record in results:
                                if "_value" in record:
                                    data_points.append(float(record["_value"]))
                                if "_time" in record:
                                    time_points.append(str(record["_time"]))
                            chart_data["data"] = data_points
                            chart_data["date"] = time_points
                            chart_data["info"] = {
                                "bucket": bucket, "measurement": measurement,
                                "result": "last", "table": 0, "field": "value",
                                "start": start, "stop": stop,
                                "time": datetime.now(UTC).isoformat(),
                                "value": data_points[-1] if data_points else None,
                            }
                        except Exception as exc:
                            logger.warning(f"Influx failed: {exc}")

                    def _to_dict_list(devs: list[Any]) -> list[dict[str, Any]]:
                        return [
                            {"device_id": str(d.id), "device_name": d.device_name,
                             "hardware_id": d.hardware_id, "type_id": d.type_id,
                             "unit": d.unit, "status": d.status}
                            for d in devs
                        ]

                    return {
                        "statuscode": 200, "status": "success",
                        "Mqttstatus": 1 if mqtt_connected else 0,
                        "payload": {
                            "checkConnectionMqtt": check_connection_mqtt,
                            "mqttrs": mqttrs, "mqttname": "", "bucket": bucket,
                            "time": datetime.now(UTC).isoformat(),
                            "mqttdata": mqtt_data, "deviceioinfo": device_io_info,
                            "devicesensor": _to_dict_list(device_sensors),
                            "deviceio": _to_dict_list(device_io),
                            "cache": "cache", "chart": chart_data,
                        },
                        "message": "check Connection Status Mqtt",
                        "message_th": "check Connection Status Mqtt",
                    }

                async def get_alarm_device_status_control(
                    self, bucket: str = "iot_sensors", **filters: Any,
                ) -> dict[str, Any]:
                    return await self.get_alarm_device_status(bucket=bucket, **filters)

                async def get_monitor_device_group(
                    self, bucket: str = "iot_sensors", location_id: int = 0,
                    hardware_id: int = 0, lang: str = "en", del_cache: int = 0,
                ) -> dict[str, Any]:
                    mqtt_connected = self.is_connected()
                    cache_enabled = self.is_cache_enabled()
                    devices = await self._device_repo.find_all_active()
                    if hardware_id:
                        devices = [d for d in devices if d.hardware_id == hardware_id]
                    if location_id:
                        devices = [d for d in devices if d.location_id == location_id]

                    mqtt_data_map: dict[str, Any] = {}
                    mqtt_raw_payload = ""

                    if mqtt_connected and devices:
                        first_dev = devices[0]
                        topic = first_dev.mqtt_topic or f"{bucket}/DATA"
                        mqtt_cache_key = f"mqtt_payload:{bucket}"
                        if cache_enabled:
                            try:
                                cached = self._redis_client.get(mqtt_cache_key)
                                if cached:
                                    mqtt_raw_payload = str(cached)
                            except Exception:
                                pass
                        if not mqtt_raw_payload:
                            try:
                                payload = self._mqtt_client.get_data_from_topic(topic, timeout=5)
                                if payload:
                                    mqtt_raw_payload = str(payload)
                                    if cache_enabled:
                                        with contextlib.suppress(Exception):
                                            self._redis_client.set(mqtt_cache_key, mqtt_raw_payload, ex=30)
                            except Exception as exc:
                                logger.warning(f"MQTT failed: {exc}")
                        if mqtt_raw_payload:
                            for i, val in enumerate(mqtt_raw_payload.split(",")):
                                mqtt_data_map[str(i)] = val.strip()

                    enriched_devices = []
                    group_names = {1: "Sensor", 2: "IO Sensor",
                                   3: "IO Control", 4: "Critical Sensor"}

                    for dev in devices:
                        raw_value: Any = "0"
                        if mqtt_data_map:
                            measurement = dev.mqtt_name or ""
                            if measurement in mqtt_data_map:
                                raw_value = mqtt_data_map[measurement]
                        try:
                            value_data_float = float(raw_value) if raw_value != "0" else 0.0
                        except (ValueError, TypeError):
                            value_data_float = 0.0
                        value_data_str = (
                            f"{value_data_float:.2f}" if dev.hardware_id == 1 else str(raw_value)
                        )
                        alarm_dto = AlarmDetailDTO(
                            hardware_id=dev.hardware_id, value_data=value_data_str,
                            value_alarm=0, max_value=0, min_value=0,
                            status_alert=0, status_warning=0,
                            recovery_warning=0, recovery_alert=0,
                            device_name=dev.device_name, action_name=dev.mqtt_name,
                            mqtt_name=dev.mqtt_name, mqtt_control_on="",
                            mqtt_control_off="", count_alarm=0, event=1,
                            unit=dev.unit,
                        )
                        alarm_result = evaluate_alarm(alarm_dto, lang=lang)
                        control_url = ""
                        device_data = ""
                        icon_access = dev.icon
                        if dev.hardware_id > 1:
                            device_data = "OFF" if value_data_float >= 1 else "ON"
                            icon_access = ""
                        else:
                            device_data = f"{value_data_str} {dev.unit}"

                        enriched_devices.append({
                            "device_id": str(dev.id), "device_name": dev.device_name,
                            "hardware_id": dev.hardware_id, "type_id": dev.type_id,
                            "type_name": "", "location_name": dev.location_name,
                            "unit": dev.unit, "status": dev.status,
                            "value_data": value_data_str,
                            "alarm_title": alarm_result.title,
                            "alarm_subject": alarm_result.subject,
                            "alarm_status": alarm_result.status,
                            "control": control_url, "devicedata": device_data,
                            "icon_access": icon_access,
                            "timestamp": datetime.now(UTC).isoformat(),
                            "mqtt_connected": mqtt_connected,
                        })

                    groups: dict[int, list[dict[str, Any]]] = {}
                    for ed in enriched_devices:
                        groups.setdefault(ed["hardware_id"], []).append(ed)

                    response_groups = [
                        {"group_id": hw_id, "group_name": group_names.get(hw_id, "Unknown"),
                         "count": len(devs), "devices": devs}
                        for hw_id, devs in groups.items()
                    ]

                    layout = (enriched_devices[0].get("layout", 2)
                              if enriched_devices else 2)

                    return {
                        "bucket": bucket,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "device_count": len(enriched_devices),
                        "layout": layout, "layout_name": "Card",
                        "group_name": group_names.get(hardware_id, ""),
                        "device_type": group_names.get(hardware_id, ""),
                        "data": response_groups, "mqtt_connected": mqtt_connected,
                        "mqtt_raw_payload": mqtt_raw_payload, "cache_used": False,
                    }

                async def get_monitor_device_chart(
                    self, bucket: str = "iot_sensors",
                    measurement: str = "temperature", field: str = "value",
                    start: str = "-10m", stop: str = "now()", limit: int = 100,
                ) -> dict[str, Any]:
                    if self._influxdb_client is None:
                        return {"data": [], "date": [], "cache": "no cache"}
                    try:
                        from app.core.influxdb_client import QueryParams
                        params = QueryParams(measurement=measurement, field=field,
                                             bucket=bucket, start=start, stop=stop,
                                             limit=limit)
                        results = self._influxdb_client.query_filter_data(params)
                        data_points: list[float] = []
                        time_points: list[str] = []
                        for record in results:
                            if "_value" in record:
                                data_points.append(float(record["_value"]))
                            if "_time" in record:
                                time_points.append(str(record["_time"]))
                        return {"data": data_points, "date": time_points, "cache": "no cache"}
                    except Exception as exc:
                        logger.error(f"Influx failed: {exc}")
                        return {"data": [], "date": [], "cache": "error", "error": str(exc)}

                async def get_topic_data_device_chart(
                    self, bucket: str = "iot_sensors", topic: str = "",
                    measurement: str = "temperature", field: str = "value",
                    start: str = "-10m", stop: str = "now()", limit: int = 100,
                ) -> dict[str, Any]:
                    topic = topic or f"{bucket}/DATA"
                    chart_response = await self.get_monitor_device_chart(
                        bucket=bucket, measurement=measurement, field=field,
                        start=start, stop=stop, limit=limit,
                    )
                    mqtt_payload = None
                    mqtt_from = ""
                    if self._redis_client:
                        try:
                            cached = self._redis_client.get(f"mqtt_topic:{topic}")
                            if cached:
                                mqtt_payload = json.loads(cached) if isinstance(cached, (str, bytes)) else cached
                                mqtt_from = "cache"
                        except Exception:
                            pass
                    if mqtt_from == "" and self._mqtt_client and self._mqtt_client.is_connected():
                        try:
                            data = self._mqtt_client.get_data_from_topic(topic, timeout=5)
                            if data:
                                mqtt_payload = json.loads(data) if isinstance(data, str) else data
                                mqtt_from = "mqtt"
                        except Exception as exc:
                            logger.warning(f"MQTT failed: {exc}")
                    return {
                        "topic": topic, "chart": chart_response,
                        "latest_payload": mqtt_payload, "latest_from": mqtt_from,
                        "cache": "cache" if mqtt_from == "cache" else "no cache",
                    }

                async def get_device_status(self, device_id: str) -> dict[str, Any]:
                    return {
                        "device_id": device_id, "is_online": False, "is_active": True,
                        "last_seen": datetime.now(UTC).isoformat(),
                        "battery_level": None, "signal_strength": None,
                        "firmware_version": None, "location": None,
                        "last_data": None, "uptime": "0s",
                    }

                async def update_device_status(
                    self, device_id: str, data: dict[str, Any],
                ) -> bool:
                    logger.info(f"UpdateDeviceStatus: device_id={device_id}")
                    return True

                async def get_device_config(self, device_id: str) -> dict[str, Any]:
                    return {
                        "device_id": device_id,
                        "config": {
                            "general": {"deviceName": "", "timezone": "Asia/Bangkok"},
                            "reporting": {"enabled": True, "interval": 300, "format": "json"},
                            "thresholds": {
                                "temperature": {"min": 15, "max": 40},
                                "humidity": {"min": 30, "max": 80},
                            },
                            "alerts": {"enabled": True, "email": [], "sms": []},
                        },
                        "status": "active",
                    }

                async def update_device_config(
                    self, device_id: str, config: dict[str, Any],
                ) -> bool:
                    logger.info(f"UpdateDeviceConfig: device_id={device_id}")
                    return True

                async def process_mqtt_data(
                    self, device_id: str, raw_data: str,
                ) -> dict[str, Any]:
                    parts = raw_data.split(",")
                    data_map: dict[str, Any] = {}
                    for i, val in enumerate(parts):
                        trimmed = val.strip()
                        try:
                            data_map[str(i)] = float(trimmed)
                        except ValueError:
                            data_map[str(i)] = trimmed
                    data_map["raw"] = raw_data
                    data = iotData(device_id=int(device_id),
                                   data_json=json.dumps(data_map))
                    await self._iot_data_repo.create(data)
                    return {
                        "device_id": device_id, "data": data_map,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }

                async def get_latest_data(
                    self, device_id: str, limit: int = 10,
                ) -> list[Any]:
                    return await self._iot_data_repo.find_latest(int(device_id), limit)

                async def get_data_by_date_range(
                    self, device_id: str, start: str, end: str,
                ) -> list[Any]:
                    return await self._iot_data_repo.find_by_date_range(
                        int(device_id), start, end)

                async def list_iot_data(
                    self, device_id: str = "",
                    page: int = 1, limit: int = 50,
                ) -> dict[str, Any]:
                    if limit <= 0:
                        limit = 50
                    if page <= 0:
                        page = 1
                    items, total = await self._iot_data_repo.find_paginated(page, limit)
                    pages = (total + limit - 1) // limit
                    return {
                        "data": [
                            {"id": str(item.id), "device_id": item.device_id,
                             "data": item.data_json,
                             "timestamp": item.created_at.isoformat() if item.created_at else ""}
                            for item in items
                        ],
                        "pagination": {"total": total, "page": page,
                                       "limit": limit, "pages": pages},
                    }

                async def get_device_stats(self, device_id: str) -> dict[str, Any]:
                    data = await self._iot_data_repo.find_latest(int(device_id), 1000)
                    stats: dict[str, Any] = {"count": len(data)}
                    if data:
                        stats["last_record"] = (
                            data[0].created_at.isoformat() if data[0].created_at else None
                        )
                        stats["first_record"] = (
                            data[-1].created_at.isoformat() if data[-1].created_at else None
                        )
                    return stats

                async def export_data(
                    self, device_id: str = "",
                    start_date: str = "", end_date: str = "",
                    export_format: str = "json",
                ) -> tuple[str, str]:
                    if not start_date or not end_date:
                        now = datetime.now(UTC)
                        end_date = now.isoformat()
                        start_date = (now - timedelta(days=7)).isoformat()
                    data = await self._iot_data_repo.find_by_date_range(
                        int(device_id) if device_id else 0, start_date, end_date)
                    if export_format == "csv":
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerow(["timestamp", "device_id", "data"])
                        for d in data:
                            writer.writerow([
                                d.created_at.isoformat() if d.created_at else "",
                                d.device_id, d.data_json,
                            ])
                        return output.getvalue(), "text/csv"
                    json_data = json.dumps([
                        {"id": str(d.id), "device_id": d.device_id,
                         "data": d.data_json,
                         "timestamp": d.created_at.isoformat() if d.created_at else ""}
                        for d in data
                    ], default=str)
                    return json_data, "application/json"

                async def cleanup_old_data(self, days: int = 90) -> int:
                    return await self._iot_data_repo.cleanup_old(days)
        ''')

    # ─── INFRASTRUCTURE LAYER ───────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """iot infrastructure layer — ชั้นโครงสร้างพื้นฐาน"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self._create_repositories()
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent('''\
            """iot SQLAlchemy 2.0 models — รวมทุก model"""
            from __future__ import annotations
            import uuid
            from datetime import datetime

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Float, Index,
                Integer, String, Text, UniqueConstraint, func,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


            class Base(DeclarativeBase):
                """TH: declarative base | EN: declarative base"""


            class DeviceModel(Base):
                __tablename__ = "iot_devices"
                __table_args__ = (
                    CheckConstraint("hardware_id IN (1,2,3,4)", name="ck_iot_hardware"),
                    Index("ix_iot_device_tenant", "tenant_id"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                hardware_id: Mapped[int] = mapped_column(Integer, nullable=False)
                type_id: Mapped[int] = mapped_column(Integer, default=0)
                location_id: Mapped[int] = mapped_column(Integer, default=0)
                device_sn: Mapped[str] = mapped_column(String(100), default="")
                device_name: Mapped[str] = mapped_column(String(255), nullable=False)
                device_type: Mapped[str] = mapped_column(String(100), default="")
                location_name: Mapped[str] = mapped_column(String(255), default="")
                mqtt_id: Mapped[int] = mapped_column(Integer, default=0)
                mqtt_main_id: Mapped[int] = mapped_column(Integer, default=0)
                mqtt_topic: Mapped[str] = mapped_column(String(500), default="")
                mqtt_name: Mapped[str] = mapped_column(String(255), default="")
                mqtt_username: Mapped[str] = mapped_column(String(255), default="")
                mqtt_password: Mapped[str] = mapped_column(String(255), default="")
                unit: Mapped[str] = mapped_column(String(50), default="")
                status: Mapped[str] = mapped_column(String(50), default="offline")
                icon: Mapped[str] = mapped_column(String(255), default="")
                icon_color: Mapped[str] = mapped_column(String(50), default="")
                description: Mapped[str] = mapped_column(String(500), default="")
                firmware_version: Mapped[str] = mapped_column(String(50), default="")
                is_active: Mapped[bool] = mapped_column(Boolean, default=True)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class DeviceConfigModel(Base):
                __tablename__ = "iot_device_configs"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "device_id", name="uq_iot_config_device"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                max_value: Mapped[float] = mapped_column(Float, default=0.0)
                min_value: Mapped[float] = mapped_column(Float, default=0.0)
                warning_threshold: Mapped[float] = mapped_column(Float, default=0.0)
                alert_threshold: Mapped[float] = mapped_column(Float, default=0.0)
                recovery_warning: Mapped[float] = mapped_column(Float, default=0.0)
                recovery_alert: Mapped[float] = mapped_column(Float, default=0.0)
                calibration_offset: Mapped[float] = mapped_column(Float, default=0.0)
                calibration_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
                mqtt_control_on: Mapped[str] = mapped_column(String(255), default="")
                mqtt_control_off: Mapped[str] = mapped_column(String(255), default="")
                action_name: Mapped[str] = mapped_column(String(255), default="")
                config_json: Mapped[str] = mapped_column(String(2000), default="{}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class DeviceStatusModel(Base):
                __tablename__ = "iot_device_statuses"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "device_id", name="uq_iot_status_device"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                is_online: Mapped[bool] = mapped_column(Boolean, default=False)
                last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
                last_value: Mapped[float] = mapped_column(Float, default=0.0)
                last_alarm: Mapped[int] = mapped_column(Integer, default=0)
                count_alarm: Mapped[int] = mapped_column(Integer, default=0)
                event: Mapped[int] = mapped_column(Integer, default=0)
                status: Mapped[str] = mapped_column(String(50), default="offline")
                sensor_data: Mapped[str] = mapped_column(String(500), default="")
                sensor_min: Mapped[float] = mapped_column(Float, default=0.0)
                sensor_max: Mapped[float] = mapped_column(Float, default=0.0)
                sensor_avg: Mapped[float] = mapped_column(Float, default=0.0)
                battery: Mapped[float] = mapped_column(Float, default=0.0)
                rssi: Mapped[int] = mapped_column(Integer, default=0)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class DeviceAlertModel(Base):
                __tablename__ = "iot_device_alerts"
                __table_args__ = (
                    CheckConstraint(
                        "severity IN ('info','low','medium','high','critical')",
                        name="ck_iot_severity"),
                    Index("ix_iot_alert_device", "device_id", "resolved"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                alert_type: Mapped[str] = mapped_column(String(50), default="")
                severity: Mapped[str] = mapped_column(String(20), default="low")
                title: Mapped[str] = mapped_column(String(255), default="")
                message: Mapped[str] = mapped_column(String(1000), default="")
                value_data: Mapped[float] = mapped_column(Float, default=0.0)
                value_alarm: Mapped[float] = mapped_column(Float, default=0.0)
                resolved: Mapped[bool] = mapped_column(Boolean, default=False)
                acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class iotDataModel(Base):
                __tablename__ = "iot_data"
                __table_args__ = (
                    Index("ix_iot_data_device_time", "device_id", "created_at"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                data_json: Mapped[str] = mapped_column(Text, default="{}")
                timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
                location_id: Mapped[int] = mapped_column(Integer, default=0)
                metadata_json: Mapped[str] = mapped_column(Text, default="{}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class AlarmLogModel(Base):
                __tablename__ = "iot_alarm_logs"
                __table_args__ = (
                    Index("ix_iot_alarm_device", "device_id", "created_at"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                alarm_action_id: Mapped[int] = mapped_column(Integer, default=0)
                alarm_type: Mapped[int] = mapped_column(Integer, default=0)
                alarm_status: Mapped[int] = mapped_column(Integer, default=0)
                value_data: Mapped[float] = mapped_column(Float, default=0.0)
                value_alarm: Mapped[float] = mapped_column(Float, default=0.0)
                title: Mapped[str] = mapped_column(String(255), default="")
                subject: Mapped[str] = mapped_column(String(500), default="")
                content: Mapped[str] = mapped_column(Text, default="")
                data_alarm: Mapped[int] = mapped_column(Integer, default=0)
                data_alarm_raw: Mapped[int] = mapped_column(Integer, default=0)
                event_control: Mapped[int] = mapped_column(Integer, default=0)
                message_mqtt_control: Mapped[str] = mapped_column(String(500), default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class ActivityLogModel(Base):
                __tablename__ = "iot_activity_logs"
                __table_args__ = (
                    Index("ix_iot_activity_device", "device_id", "created_at"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                log_type: Mapped[str] = mapped_column(String(50), default="")
                device_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
                user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
                severity: Mapped[str] = mapped_column(String(20), default="info")
                data_json: Mapped[str] = mapped_column(Text, default="{}")
                description: Mapped[str] = mapped_column(Text, default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())


            class ScheduleModel(Base):
                __tablename__ = "iot_schedules"
                __table_args__ = (
                    Index("ix_iot_schedule_device", "device_id", "is_active"),
                    {"schema": "tenant_iot"},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                schedule_id: Mapped[int] = mapped_column(Integer, default=0)
                device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                start_time: Mapped[str] = mapped_column(String(10), default="")
                end_time: Mapped[str] = mapped_column(String(10), default="")
                event: Mapped[str] = mapped_column(String(50), default="")
                monday: Mapped[bool] = mapped_column(Boolean, default=False)
                tuesday: Mapped[bool] = mapped_column(Boolean, default=False)
                wednesday: Mapped[bool] = mapped_column(Boolean, default=False)
                thursday: Mapped[bool] = mapped_column(Boolean, default=False)
                friday: Mapped[bool] = mapped_column(Boolean, default=False)
                saturday: Mapped[bool] = mapped_column(Boolean, default=False)
                sunday: Mapped[bool] = mapped_column(Boolean, default=False)
                is_active: Mapped[bool] = mapped_column(Boolean, default=True)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """iot infrastructure cache — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class RedisiotCache:
                """TH: cache ด้วย Redis | EN: Redis cache"""

                def __init__(self, redis: object, ttl: int = 300) -> None:
                    self._redis = redis
                    self._ttl = ttl

                async def get(self, key: str) -> Any | None:
                    try:
                        raw = await self._redis.get(key)
                        return json.loads(raw) if raw else None
                    except Exception as e:
                        log.warning("cache.get_failed", key=key, err=str(e))
                        return None

                async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
                    try:
                        await self._redis.set(
                            key, json.dumps(value, default=str), ex=(ttl or self._ttl))
                        return True
                    except Exception as e:
                        log.warning("cache.set_failed", key=key, err=str(e))
                        return False

                async def invalidate(self, key: str) -> bool:
                    try:
                        await self._redis.delete(key)
                        return True
                    except Exception as e:
                        log.warning("cache.invalidate_failed", key=key, err=str(e))
                        return False
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """iot infrastructure services — Kafka · Alert"""
            from __future__ import annotations
            from dataclasses import dataclass, field
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class KafkaEventBus:
                """TH: Kafka event bus | EN: Kafka event bus"""

                def __init__(self, producer: object, topic: str = "iot.events") -> None:
                    self._producer = producer
                    self._topic = topic

                async def publish(self, event: object) -> None:
                    try:
                        payload = {
                            "type": type(event).__name__,
                            "data": {k: str(v) for k, v in vars(event).items()},
                        }
                        await self._producer.send_and_wait(self._topic, payload)
                        log.info("event.published", type=type(event).__name__)
                    except Exception as e:
                        log.warning("event.publish_failed", err=str(e))


            @dataclass
            class AlertChannel:
                enabled: bool = False
                webhook_url: str = ""
                api_key: str = ""
                recipients: list[str] = field(default_factory=list)


            @dataclass
            class AlertNotification:
                device_id: int
                device_name: str
                alarm_status: int
                title: str
                subject: str
                content: str
                value_data: float
                value_alarm: float
                severity: str = "info"
                channels: list[str] = field(default_factory=list)


            class AlertService:
                """TH: ส่ง alert | EN: Alert service"""

                def __init__(
                    self, email_config: AlertChannel | None = None,
                    line_config: AlertChannel | None = None,
                    telegram_config: AlertChannel | None = None,
                    sms_config: AlertChannel | None = None,
                ) -> None:
                    self._channels: dict[str, AlertChannel] = {}
                    if email_config:
                        self._channels["email"] = email_config
                    if line_config:
                        self._channels["line"] = line_config
                    if telegram_config:
                        self._channels["telegram"] = telegram_config
                    if sms_config:
                        self._channels["sms"] = sms_config

                async def send_alert(
                    self, notification: AlertNotification,
                ) -> dict[str, bool]:
                    results: dict[str, bool] = {}
                    target = notification.channels or list(self._channels.keys())
                    for name in target:
                        if name not in self._channels:
                            results[name] = False
                            continue
                        channel = self._channels[name]
                        if not channel.enabled:
                            results[name] = False
                            continue
                        try:
                            await self._send_to_channel(name, channel, notification)
                            results[name] = True
                            log.info(f"alert.sent via {name}: {notification.title}")
                        except Exception as exc:
                            log.error(f"alert.failed via {name}: {exc}")
                            results[name] = False
                    return results

                async def _send_to_channel(
                    self, name: str, channel: AlertChannel,
                    notification: AlertNotification,
                ) -> None:
                    log.debug(f"alert.{name}", title=notification.title)

                def get_channel_status(self) -> dict[str, dict[str, Any]]:
                    return {
                        name: {"enabled": ch.enabled,
                               "recipients_count": len(ch.recipients)}
                        for name, ch in self._channels.items()
                    }


            alert_service = AlertService()
        ''')

    def _create_repositories(self) -> None:
        # ย่อ — เนื้อหาเหมือนเวอร์ชันก่อน (device_repository, device_config_repository, ...)
        base = f"{self.mod_root}/infrastructure"
        for name, content in self._repository_files().items():
            self.writer.write(f"{base}/{name}", content)

    def _repository_files(self) -> dict[str, str]:
        """คืน dict ของ repos — ย่อโค้ดไว้เท่าเดิม"""
        return {
            "device_repository.py": self._device_repo_content(),
            "device_config_repository.py": self._device_config_repo_content(),
            "device_status_repository.py": self._device_status_repo_content(),
            "device_alert_repository.py": self._device_alert_repo_content(),
            "iot_data_repository.py": self._iot_data_repo_content(),
            "alarm_log_repository.py": self._alarm_log_repo_content(),
            "activity_log_repository.py": self._activity_log_repo_content(),
            "schedule_repository.py": self._schedule_repo_content(),
        }

    def _device_repo_content(self) -> str:
        return dedent('''\
            """Device repository — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import DeviceModel


            class DeviceRepository:
                """TH: device repo | EN: device repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, device_id: uuid.UUID) -> DeviceModel | None:
                    result = await self._session.execute(
                        select(DeviceModel).where(DeviceModel.id == device_id))
                    return result.scalar_one_or_none()

                async def find_by_hardware_id(self, hardware_id: int) -> DeviceModel | None:
                    result = await self._session.execute(
                        select(DeviceModel).where(DeviceModel.hardware_id == hardware_id))
                    return result.scalar_one_or_none()

                async def find_by_mqtt_topic(self, topic: str) -> DeviceModel | None:
                    result = await self._session.execute(
                        select(DeviceModel).where(DeviceModel.mqtt_topic == topic))
                    return result.scalar_one_or_none()

                async def find_by_location(self, location_id: int) -> list[DeviceModel]:
                    result = await self._session.execute(
                        select(DeviceModel).where(
                            DeviceModel.location_id == location_id,
                            DeviceModel.is_active.is_(True),
                        ))
                    return list(result.scalars().all())

                async def find_all_active(self) -> list[DeviceModel]:
                    result = await self._session.execute(
                        select(DeviceModel).where(DeviceModel.is_active.is_(True)))
                    return list(result.scalars().all())

                async def find_all_paginated(
                    self, page: int = 1, page_size: int = 20,
                ) -> tuple[list[DeviceModel], int]:
                    count_result = await self._session.execute(
                        select(func.count()).select_from(DeviceModel).where(
                            DeviceModel.is_active.is_(True)))
                    total = count_result.scalar() or 0
                    query = (
                        select(DeviceModel)
                        .where(DeviceModel.is_active.is_(True))
                        .order_by(DeviceModel.created_at.desc())
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                    result = await self._session.execute(query)
                    return list(result.scalars().all()), total

                async def create(self, device: DeviceModel) -> DeviceModel:
                    logger.info(f"Creating device: {device.device_name}")
                    self._session.add(device)
                    await self._session.flush()
                    return device

                async def update(self, device: DeviceModel) -> DeviceModel:
                    await self._session.flush()
                    return device

                async def delete(self, device_id: uuid.UUID) -> bool:
                    device = await self.find_by_id(device_id)
                    if device:
                        device.is_active = False
                        await self._session.flush()
                        return True
                    return False
        ''')

    def _device_config_repo_content(self) -> str:
        return dedent('''\
            """DeviceConfig repository"""
            from __future__ import annotations
            import uuid

            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import DeviceConfigModel


            class DeviceConfigRepository:
                """TH: device config repo | EN: device config repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_device_id(
                    self, device_id: uuid.UUID,
                ) -> DeviceConfigModel | None:
                    result = await self._session.execute(
                        select(DeviceConfigModel).where(
                            DeviceConfigModel.device_id == device_id))
                    return result.scalar_one_or_none()

                async def upsert(self, config: DeviceConfigModel) -> DeviceConfigModel:
                    existing = await self.find_by_device_id(config.device_id)
                    if existing:
                        for key, value in vars(config).items():
                            if key not in ("id", "created_at", "_sa_instance_state") and value is not None:
                                setattr(existing, key, value)
                        await self._session.flush()
                        return existing
                    self._session.add(config)
                    await self._session.flush()
                    return config
        ''')

    def _device_status_repo_content(self) -> str:
        return dedent('''\
            """DeviceStatus repository"""
            from __future__ import annotations
            import uuid
            from datetime import UTC, datetime

            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import DeviceStatusModel


            class DeviceStatusRepository:
                """TH: device status repo | EN: device status repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_device_id(
                    self, device_id: uuid.UUID,
                ) -> DeviceStatusModel | None:
                    result = await self._session.execute(
                        select(DeviceStatusModel).where(
                            DeviceStatusModel.device_id == device_id))
                    return result.scalar_one_or_none()

                async def upsert(self, status: DeviceStatusModel) -> DeviceStatusModel:
                    existing = await self.find_by_device_id(status.device_id)
                    if existing:
                        for key, value in vars(status).items():
                            if key not in ("id", "created_at", "_sa_instance_state") and value is not None:
                                setattr(existing, key, value)
                        await self._session.flush()
                        return existing
                    self._session.add(status)
                    await self._session.flush()
                    return status

                async def update_last_seen(self, device_id: uuid.UUID) -> None:
                    status = await self.find_by_device_id(device_id)
                    if status:
                        status.last_seen = datetime.now(UTC)
                        status.is_online = True
                        await self._session.flush()
        ''')

    def _device_alert_repo_content(self) -> str:
        return dedent('''\
            """DeviceAlert repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import DeviceAlertModel


            class DeviceAlertRepository:
                """TH: device alert repo | EN: device alert repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, alert: DeviceAlertModel) -> DeviceAlertModel:
                    logger.info(f"Creating alert for device: {alert.device_id}")
                    self._session.add(alert)
                    await self._session.flush()
                    return alert

                async def find_unresolved(
                    self, device_id: uuid.UUID,
                ) -> list[DeviceAlertModel]:
                    result = await self._session.execute(
                        select(DeviceAlertModel).where(
                            DeviceAlertModel.device_id == device_id,
                            DeviceAlertModel.resolved.is_(False)))
                    return list(result.scalars().all())

                async def resolve(
                    self, alert_id: uuid.UUID,
                ) -> DeviceAlertModel | None:
                    result = await self._session.execute(
                        select(DeviceAlertModel).where(
                            DeviceAlertModel.id == alert_id))
                    alert = result.scalar_one_or_none()
                    if alert:
                        alert.resolved = True
                        await self._session.flush()
                    return alert
        ''')

    def _iot_data_repo_content(self) -> str:
        return dedent('''\
            """iotData repository"""
            from __future__ import annotations
            from datetime import UTC, datetime, timedelta

            from sqlalchemy import func, select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import iotDataModel


            class iotDataRepository:
                """TH: iot data repo | EN: iot data repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, data: iotDataModel) -> iotDataModel:
                    self._session.add(data)
                    await self._session.flush()
                    return data

                async def find_latest(
                    self, device_id: int, limit: int = 10,
                ) -> list[iotDataModel]:
                    result = await self._session.execute(
                        select(iotDataModel)
                        .where(iotDataModel.device_id == device_id)
                        .order_by(iotDataModel.created_at.desc())
                        .limit(limit))
                    return list(result.scalars().all())

                async def find_by_date_range(
                    self, device_id: int, start: str, end: str,
                ) -> list[iotDataModel]:
                    result = await self._session.execute(
                        select(iotDataModel).where(
                            iotDataModel.device_id == device_id,
                            iotDataModel.created_at >= start,
                            iotDataModel.created_at <= end,
                        ).order_by(iotDataModel.created_at.desc()))
                    return list(result.scalars().all())

                async def find_paginated(
                    self, page: int = 1, page_size: int = 20,
                ) -> tuple[list[iotDataModel], int]:
                    count_result = await self._session.execute(
                        select(func.count()).select_from(iotDataModel))
                    total = count_result.scalar() or 0
                    query = (
                        select(iotDataModel)
                        .order_by(iotDataModel.created_at.desc())
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                    result = await self._session.execute(query)
                    return list(result.scalars().all()), total

                async def cleanup_old(self, days: int) -> int:
                    cutoff = datetime.now(UTC) - timedelta(days=days)
                    result = await self._session.execute(
                        select(iotDataModel).where(iotDataModel.created_at < cutoff))
                    old = list(result.scalars().all())
                    for item in old:
                        await self._session.delete(item)
                    await self._session.flush()
                    return len(old)
        ''')

    def _alarm_log_repo_content(self) -> str:
        return dedent('''\
            """AlarmLog repository"""
            from __future__ import annotations

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import AlarmLogModel


            class AlarmLogRepository:
                """TH: alarm log repo | EN: alarm log repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, log: AlarmLogModel) -> AlarmLogModel:
                    logger.info(f"Creating alarm log for device: {log.device_id}")
                    self._session.add(log)
                    await self._session.flush()
                    return log

                async def count_by_device(self, device_id: int) -> int:
                    result = await self._session.execute(
                        select(func.count())
                        .select_from(AlarmLogModel)
                        .where(AlarmLogModel.device_id == device_id))
                    return result.scalar() or 0

                async def find_by_device(
                    self, device_id: int, limit: int = 100,
                ) -> list[AlarmLogModel]:
                    result = await self._session.execute(
                        select(AlarmLogModel)
                        .where(AlarmLogModel.device_id == device_id)
                        .order_by(AlarmLogModel.created_at.desc())
                        .limit(limit))
                    return list(result.scalars().all())
        ''')

    def _activity_log_repo_content(self) -> str:
        return dedent('''\
            """ActivityLog repository"""
            from __future__ import annotations

            from loguru import logger
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import ActivityLogModel


            class ActivityLogRepository:
                """TH: activity log repo | EN: activity log repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, log: ActivityLogModel) -> ActivityLogModel:
                    logger.debug(f"Creating activity log: {log.log_type}")
                    self._session.add(log)
                    await self._session.flush()
                    return log
        ''')

    def _schedule_repo_content(self) -> str:
        return dedent('''\
            """Schedule repository"""
            from __future__ import annotations

            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.iot.infrastructure.models import ScheduleModel


            class ScheduleRepository:
                """TH: schedule repo | EN: schedule repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_active_schedules(self) -> list[ScheduleModel]:
                    result = await self._session.execute(
                        select(ScheduleModel).where(ScheduleModel.is_active.is_(True)))
                    return list(result.scalars().all())

                async def find_by_device_id(
                    self, device_id: int,
                ) -> list[ScheduleModel]:
                    result = await self._session.execute(
                        select(ScheduleModel).where(
                            ScheduleModel.device_id == device_id,
                            ScheduleModel.is_active.is_(True)))
                    return list(result.scalars().all())
        ''')

    # ─── PRESENTATION LAYER ─────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """iot presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/docs.py", self._docs_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/routers.py", self._routers_content())
        self.writer.write(f"{base}/ws.py", self._ws_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """iot Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class ControlRequest(BaseModel):
                topic: str = Field(..., min_length=1)
                message: str = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class DeviceListRequest(BaseModel):
                bucket: str = ""
                hardware_id: int = 0
                page: int = Field(default=1, ge=1)
                page_size: int = Field(default=20, ge=1, le=100)
                model_config = ConfigDict(extra="forbid")


            class SenserChartRequest(BaseModel):
                measurement: str = "temperature"
                field: str = "value"
                bucket: str = "iot_sensors"
                start: str = "-1h"
                stop: str = "now()"
                limit: int = Field(default=1000, ge=1, le=10000)
                model_config = ConfigDict(extra="forbid")


            class AlarmDeviceStatusRequest(BaseModel):
                bucket: str = "iot_sensors"
                page: int = Field(default=1, ge=1)
                page_size: int = Field(default=1000, ge=1, le=5000)
                measurement: str = "temperature"
                device_id: str = ""
                type_id: int = 0
                hardware_id: int = 0
                keyword: str = ""
                model_config = ConfigDict(extra="forbid")


            class MonitorDeviceGroupRequest(BaseModel):
                bucket: str = "iot_sensors"
                location_id: int = 0
                hardware_id: int = 0
                lang: str = Field(default="en", pattern="^(en|th)$")
                del_cache: int = Field(default=0, ge=0, le=1)
                model_config = ConfigDict(extra="forbid")


            class MonitorDeviceChartRequest(BaseModel):
                bucket: str = "iot_sensors"
                measurement: str = "temperature"
                field: str = "value"
                start: str = "-10m"
                stop: str = "now()"
                limit: int = Field(default=100, ge=1, le=10000)
                model_config = ConfigDict(extra="forbid")


            class TopicDataDeviceChartRequest(BaseModel):
                bucket: str = "iot_sensors"
                topic: str = ""
                measurement: str = "temperature"
                field: str = "value"
                start: str = "-10m"
                stop: str = "now()"
                limit: int = Field(default=100, ge=1, le=10000)
                model_config = ConfigDict(extra="forbid")


            class UpdateDeviceStatusRequest(BaseModel):
                battery: float | None = Field(default=None, ge=0, le=100)
                signal: float | None = Field(default=None, ge=0)
                firmware: str | None = None
                location: dict[str, Any] | None = None
                model_config = ConfigDict(extra="forbid")


            class UpdateDeviceConfigRequest(BaseModel):
                config: dict[str, Any] = Field(...)
                model_config = ConfigDict(extra="forbid")


            class ProcessMqttDataRequest(BaseModel):
                device_id: str = Field(..., min_length=1)
                raw_data: str = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class ExportDataRequest(BaseModel):
                device_id: str = ""
                start_date: str = ""
                end_date: str = ""
                format: str = Field(default="json", pattern="^(json|csv)$")
                model_config = ConfigDict(extra="forbid")


            class BatchProcessItem(BaseModel):
                device_id: str = Field(..., min_length=1)
                raw_data: str = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class BatchProcessRequest(BaseModel):
                items: list[BatchProcessItem] = Field(..., min_length=1, max_length=100)
                model_config = ConfigDict(extra="forbid")


            # ─── Responses ───────────────────────────────
            class TopicDataResponse(BaseModel):
                topic: str
                payload: Any = None
                from_source: str = Field(alias="from")
                cache: bool
                model_config = ConfigDict(extra="forbid", populate_by_name=True)


            class DeviceDetailResponse(BaseModel):
                device_id: str
                device_name: str
                type_name: str = ""
                unit: str = ""
                status: str = ""
                hardware_id: int = 0
                model_config = ConfigDict(extra="forbid")


            class DeviceListResponse(BaseModel):
                devices: list[DeviceDetailResponse]
                total: int
                page: int
                page_size: int
                model_config = ConfigDict(extra="forbid")


            class DeviceBucketsResponse(BaseModel):
                bucket: str
                devices: list[DeviceDetailResponse]
                model_config = ConfigDict(extra="forbid")


            class SenserChartResponse(BaseModel):
                data: list[float]
                date: list[str]
                cache: str = "no cache"
                model_config = ConfigDict(extra="forbid")


            class DeviceStatusResponse(BaseModel):
                device_id: str
                is_online: bool
                is_active: bool
                last_seen: str = ""
                battery_level: float | None = None
                signal_strength: float | None = None
                firmware_version: str | None = None
                location: dict[str, Any] | None = None
                last_data: dict[str, Any] | None = None
                uptime: str = "0s"
                model_config = ConfigDict(extra="forbid")


            class DeviceConfigResponse(BaseModel):
                device_id: str
                config: dict[str, Any]
                status: str = "active"
                model_config = ConfigDict(extra="forbid")


            class PaginatedDataResponse(BaseModel):
                data: list[dict[str, Any]]
                pagination: dict[str, int]
                model_config = ConfigDict(extra="forbid")


            class DeviceStatsResponse(BaseModel):
                count: int
                last_record: str | None = None
                first_record: str | None = None
                model_config = ConfigDict(extra="forbid")


            class CleanupResponse(BaseModel):
                deleted_count: int
                message: str
                model_config = ConfigDict(extra="forbid")


            class MonitorDeviceGroupResponse(BaseModel):
                bucket: str
                timestamp: str
                device_count: int
                layout: int
                layout_name: str
                group_name: str
                device_type: str
                data: list[dict[str, Any]]
                mqtt_connected: bool
                mqtt_raw_payload: str = ""
                cache_used: bool
                model_config = ConfigDict(extra="forbid")


            class AlarmDeviceStatusResponse(BaseModel):
                statuscode: int
                status: str
                Mqttstatus: int
                payload: dict[str, Any]
                message: str
                message_th: str
                model_config = ConfigDict(extra="forbid")
        ''')

    def _docs_content(self) -> str:
        return dedent('''\
            """iot OpenAPI metadata"""
            from __future__ import annotations

            RESPONSE_CREATE_201 = {
                "description": "สร้างสำเร็จ",
                "content": {"application/json": {"example": {
                    "device_id": "...", "device_name": "Cold Room 1",
                    "hardware_id": 1, "status": "online",
                }}},
            }
            RESPONSE_ERROR_400 = {
                "description": "Domain error",
                "content": {"application/json": {"example": {
                    "detail": "invalid hardware type", "code": "DOMAIN_ERROR",
                }}},
            }
            RESPONSE_ERROR_404 = {
                "description": "ไม่พบ device",
                "content": {"application/json": {"example": {
                    "detail": "device not found", "code": "NOT_FOUND",
                }}},
            }
            RESPONSE_ERROR_503 = {
                "description": "MQTT/InfluxDB ไม่พร้อม",
                "content": {"application/json": {"example": {
                    "detail": "MQTT not connected", "code": "SERVICE_UNAVAILABLE",
                }}},
            }
            RESPONSE_ERROR_422 = {
                "description": "Validation error",
                "content": {"application/json": {"example": {
                    "detail": [{"loc": ["body"], "msg": "invalid"}],
                }}},
            }
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """iot DI container"""
            from __future__ import annotations
            from typing import Any

            from fastapi import Depends
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.core.database import get_async_session
            from app.core.influxdb_client import InfluxDBClientWrapper
            from app.core.mqtt_client import MQTTClient
            from app.core.settings import settings
            from app.modules.iot.application.use_case import iotUseCase
            from app.modules.iot.infrastructure.activity_log_repository import (
                ActivityLogRepository,
            )
            from app.modules.iot.infrastructure.alarm_log_repository import (
                AlarmLogRepository,
            )
            from app.modules.iot.infrastructure.device_alert_repository import (
                DeviceAlertRepository,
            )
            from app.modules.iot.infrastructure.device_config_repository import (
                DeviceConfigRepository,
            )
            from app.modules.iot.infrastructure.device_repository import DeviceRepository
            from app.modules.iot.infrastructure.device_status_repository import (
                DeviceStatusRepository,
            )
            from app.modules.iot.infrastructure.iot_data_repository import (
                iotDataRepository,
            )

            _influxdb_client: InfluxDBClientWrapper | None = None
            _mqtt_client: MQTTClient | None = None


            def _get_influxdb_client() -> InfluxDBClientWrapper:
                global _influxdb_client
                if _influxdb_client is None:
                    _influxdb_client = InfluxDBClientWrapper(
                        url=settings.INFLUXDB_URL,
                        token=settings.INFLUXDB_TOKEN,
                        org=settings.INFLUXDB_ORG,
                        bucket=settings.INFLUXDB_BUCKET,
                        timeout=settings.INFLUXDB_TIMEOUT,
                    )
                return _influxdb_client


            def _get_mqtt_client() -> MQTTClient | None:
                global _mqtt_client
                if _mqtt_client is None:
                    try:
                        _mqtt_client = MQTTClient(
                            broker=settings.MQTT_BROKER,
                            client_id=settings.MQTT_CLIENT_ID,
                            username=settings.MQTT_USERNAME,
                            password=settings.MQTT_PASSWORD,
                            keepalive=settings.MQTT_KEEPALIVE,
                        )
                        _mqtt_client.connect()
                    except Exception as exc:
                        import logging
                        logging.warning(f"MQTT connection failed: {exc}")
                        return None
                return _mqtt_client


            def _get_redis_client() -> Any:
                try:
                    import redis
                    return redis.from_url(settings.REDIS_URL, decode_responses=True)
                except Exception:
                    return None


            async def get_iot_use_case(
                session: AsyncSession = Depends(get_async_session),
            ) -> iotUseCase:
                return iotUseCase(
                    device_repository=DeviceRepository(session),
                    device_config_repository=DeviceConfigRepository(session),
                    device_status_repository=DeviceStatusRepository(session),
                    device_alert_repository=DeviceAlertRepository(session),
                    iot_data_repository=iotDataRepository(session),
                    alarm_log_repository=AlarmLogRepository(session),
                    activity_log_repository=ActivityLogRepository(session),
                    mqtt_client=_get_mqtt_client(),
                    influxdb_client=_get_influxdb_client(),
                    redis_client=_get_redis_client(),
                )
        ''')

    def _routers_content(self) -> str:
        # ใช้เนื้อหาเดิมจากไฟล์ routers.py (ยาว) — ย่อให้สั้น
        return dedent('''\
            """iot HTTP + WebSocket routers"""
            from __future__ import annotations
            import json
            from typing import Any

            from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect

            from app.core.websocket_hub import ws_manager
            from app.modules.iot.application.use_case import iotUseCase
            from app.modules.iot.presentation.dependencies import get_iot_use_case
            from app.modules.iot.presentation.schemas import (
                AlarmDeviceStatusRequest, AlarmDeviceStatusResponse,
                BatchProcessRequest, CleanupResponse, ControlRequest,
                DeviceBucketsResponse, DeviceConfigResponse,
                DeviceDetailResponse, DeviceListResponse,
                DeviceStatsResponse, DeviceStatusResponse, ExportDataRequest,
                MonitorDeviceGroupRequest, MonitorDeviceGroupResponse,
                PaginatedDataResponse, ProcessMqttDataRequest,
                SenserChartResponse, TopicDataResponse,
                UpdateDeviceConfigRequest, UpdateDeviceStatusRequest,
            )

            router = APIRouter(prefix="/iot", tags=["iot"])


            @router.get("/status")
            async def get_connection_status(
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> dict[str, Any]:
                return {
                    "mqtt_connected": use_case.is_connected(),
                    "cache_enabled": use_case.is_cache_enabled(),
                }


            @router.post("/topic-data")
            async def get_topic_data(
                topic: str,
                del_cache: bool = False,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> TopicDataResponse:
                result = await use_case.get_topic_data(topic, del_cache)
                return TopicDataResponse(**result)


            @router.post("/control")
            async def device_control(
                payload: ControlRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> dict[str, bool]:
                success = await use_case.device_control(payload.topic, payload.message)
                return {"success": success}


            @router.post("/controls")
            async def device_controls(
                payload: ControlRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> dict[str, bool]:
                success = await use_case.device_controls(payload.topic, payload.message)
                return {"success": success}


            @router.get("/devices")
            async def get_device_list(
                bucket: str = "", hardware_id: int = 0,
                page: int = 1, page_size: int = 20,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> DeviceListResponse:
                devices, total = await use_case.get_device_list(
                    bucket, hardware_id, page, page_size)
                return DeviceListResponse(
                    devices=[
                        DeviceDetailResponse(
                            device_id=str(d.id), device_name=d.device_name,
                            hardware_id=d.hardware_id, unit=d.unit, status=d.status,
                        ) for d in devices
                    ],
                    total=total, page=page, page_size=page_size,
                )


            @router.get("/devices/page")
            async def get_device_list_page(
                bucket: str = "", hardware_id: int = 0,
                page: int = 1, page_size: int = 20,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> DeviceListResponse:
                devices, total = await use_case.get_device_list_page(
                    bucket, hardware_id, page, page_size)
                return DeviceListResponse(
                    devices=[
                        DeviceDetailResponse(
                            device_id=str(d.id), device_name=d.device_name,
                            hardware_id=d.hardware_id, unit=d.unit, status=d.status,
                        ) for d in devices
                    ],
                    total=total, page=page, page_size=page_size,
                )


            @router.get("/devices/buckets/{bucket}")
            async def get_device_buckets(
                bucket: str,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> DeviceBucketsResponse:
                devices, _ = await use_case.get_device_list(bucket=bucket)
                return DeviceBucketsResponse(
                    bucket=bucket,
                    devices=[
                        DeviceDetailResponse(
                            device_id=str(d.id), device_name=d.device_name,
                            hardware_id=d.hardware_id, unit=d.unit,
                        ) for d in devices
                    ],
                )


            @router.get("/devices/location/{location_id}")
            async def get_device_list_by_location(
                location_id: int,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> list[DeviceDetailResponse]:
                devices = await use_case.get_device_list_by_location(location_id)
                return [
                    DeviceDetailResponse(
                        device_id=str(d.id), device_name=d.device_name,
                        hardware_id=d.hardware_id, unit=d.unit,
                    ) for d in devices
                ]


            @router.get("/senser-charts")
            async def get_senser_charts(
                measurement: str = "temperature", field: str = "value",
                bucket: str = "iot_sensors", start: str = "-1h",
                stop: str = "now()", limit: int = 1000,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> SenserChartResponse:
                result = await use_case.get_senser_charts(
                    measurement, field, bucket, start, stop, limit)
                return SenserChartResponse(**result)


            @router.post("/alarm-device-status")
            async def get_alarm_device_status(
                payload: AlarmDeviceStatusRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> AlarmDeviceStatusResponse:
                result = await use_case.get_alarm_device_status(
                    bucket=payload.bucket, page=payload.page,
                    page_size=payload.page_size,
                    measurement=payload.measurement)
                return AlarmDeviceStatusResponse(**result)


            @router.post("/monitor-device-group")
            async def get_monitor_device_group(
                payload: MonitorDeviceGroupRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> MonitorDeviceGroupResponse:
                result = await use_case.get_monitor_device_group(
                    bucket=payload.bucket, location_id=payload.location_id,
                    hardware_id=payload.hardware_id, lang=payload.lang,
                    del_cache=payload.del_cache)
                return MonitorDeviceGroupResponse(**result)


            @router.post("/process-mqtt-data")
            async def process_mqtt_data(
                payload: ProcessMqttDataRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> dict[str, Any]:
                return await use_case.process_mqtt_data(
                    payload.device_id, payload.raw_data)


            @router.post("/export")
            async def export_data(
                payload: ExportDataRequest,
                use_case: iotUseCase = Depends(get_iot_use_case),
            ) -> Response:
                data, content_type = await use_case.export_data(
                    device_id=payload.device_id,
                    start_date=payload.start_date,
                    end_date=payload.end_date,
                    export_format=payload.format)
                filename = f"iot_export_{payload.device_id or 'all'}.{payload.format}"
                return Response(
                    content=data, media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"},
                )


            @router.websocket("/ws/{room}")
            async def websocket_endpoint(
                websocket: WebSocket, room: str = "default",
            ) -> None:
                await ws_manager.connect(websocket, room)
                try:
                    while True:
                        raw = await websocket.receive_text()
                        try:
                            msg = json.loads(raw)
                        except json.JSONDecodeError:
                            await websocket.send_text(
                                json.dumps({"error": "Invalid JSON"}))
                            continue
                        msg_type = msg.get("type", "")
                        if msg_type == "subscribe":
                            topic = msg.get("topic", "")
                            await ws_manager.subscribe(websocket, topic)
                            await websocket.send_text(
                                json.dumps({"event": "subscribed", "topic": topic}))
                        elif msg_type == "join_room":
                            iot_room = msg.get("room", "default")
                            await ws_manager.disconnect(websocket, room)
                            room = iot_room
                            await ws_manager.connect(websocket, room)
                            await websocket.send_text(
                                json.dumps({"event": "joined_room", "room": room}))
                        elif msg_type == "message":
                            payload = msg.get("data", {})
                            await ws_manager.broadcast_to_room(room, "message", payload)
                except WebSocketDisconnect:
                    await ws_manager.disconnect(websocket, room)
        ''')

    def _ws_content(self) -> str:
        return dedent('''\
            """iot WebSocket helpers"""
            from __future__ import annotations

            import structlog

            from app.core.websocket_hub import ws_manager

            log = structlog.get_logger()


            async def broadcast_alarm(
                room: str, device_id: str, title: str, value: float,
            ) -> None:
                try:
                    await ws_manager.broadcast_to_room(room, "alarm", {
                        "device_id": device_id, "title": title, "value": value,
                    })
                except Exception as e:
                    log.warning("ws.broadcast_failed", err=str(e))


            async def broadcast_data(
                room: str, device_id: str, data: dict,
            ) -> None:
                try:
                    await ws_manager.broadcast_to_room(room, "data", {
                        "device_id": device_id, "data": data,
                    })
                except Exception as e:
                    log.warning("ws.broadcast_failed", err=str(e))
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent('''\
            """iot module — โมดูล iot"""
            from .presentation.routers import router as iot_router

            __all__ = ["iot_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. ACTIVATE — register router + models
    # ═══════════════════════════════════════════════════════════
    def activate_module(self) -> None:
        info("[2/7] ACTIVATE — register router in app/app.py + models in migrations/env.py")
        self._update_app_py()
        self._update_env_py()

    # ═══════════════════════════════════════════════════════════
    #  4. UPDATE APP
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info("[4/7] UPDATE APP — app/app.py")
        self._update_app_py()

    def _update_app_py(self) -> None:
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content
        import_line = (
            "from app.modules.iot.presentation.routers "
            "import router as iot_router"
        )

        # ── 1. Import injection — หลัง health_router (ตาม alphabet) ──
        if import_line not in content:
            lines = content.split("\n")
            insert_at = None
            for i, line in enumerate(lines):
                if "from app.modules.health.presentation.routers import" in line:
                    insert_at = i + 1
                    break
            if insert_at is None:
                # fallback: after last import
                last = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last = i
                insert_at = last + 1
            lines.insert(insert_at, import_line)
            content = "\n".join(lines)
            ok(f"added import: {import_line}")

        # ── 2. Router list injection ──
        if "iot_router" not in content.split("for router in routers")[0].split("routers = [")[-1]:
            # locate routers = [ ... ]
            m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
            if m:
                inner = m.group(2)
                if "iot_router" not in inner:
                    # แทรกหลัง health_router,
                    if "health_router," in inner:
                        inner_new = inner.replace(
                            "    health_router,\n",
                            "    health_router,\n    iot_router,    # iot module (Layer 6-Monitor)\n",
                            1,
                        )
                    else:
                        inner_new = inner.rstrip() + "\n    iot_router,    # iot module\n"
                    content = content[:m.start(2)] + inner_new + content[m.end(2):]
                    ok("added iot_router to routers list")

        # ── 3. OpenAPI tag ──
        if '"name": "iot"' not in content:
            tag_line = (
                '            {"name": "iot", "description": '
                '"iot Module — Real-time Sensor & Alarm Monitoring '
                '(MQTT / InfluxDB / WebSocket)."},\n'
            )
            # insert หลัง Health tag
            m = re.search(
                r'(\{"name":\s*"Health"[^\}]*\},\s*\n)',
                content,
            )
            if m:
                content = content[:m.end(1)] + tag_line + content[m.end(1):]
                ok("added OpenAPI tag: iot")
            else:
                warn("Health tag not found — skip OpenAPI tag injection")

        # ── Save ──
        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            ok(f"backup: {self.app_py}.bak")
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")
        else:
            skip(f"{self.app_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  5. UPDATE ENV — register iot models in migrations/env.py
    # ═══════════════════════════════════════════════════════════
    def update_env(self) -> None:
        info("[5/7] UPDATE ENV — migrations/env.py")
        self._update_env_py()

    def _update_env_py(self) -> None:
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found — skipping")
            return

        content = env_file.read_text(encoding="utf-8")
        original = content

        marker = "# --- module iot (Device / Config / Status / Alert / Data / Alarm / Activity / Schedule) ---"
        if marker in content:
            skip("iot models block already present in env.py")
            return

        # block ที่จะแทรก — วางต่อจาก pdpa block
        iot_block = f'''{marker}
# TH: iot module — 8 models (Layer 6-Monitor)
# EN: iot module — 8 models (Layer 6-Monitor)
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


'''

        # หา anchor: หลัง pdpa block (บรรทัดว่างหลัง pass ที่ตามหลัง pdpa)
        # ลองหาด้วย regex — หลัง pdpa block มี "except ImportError:\n    pass\n"
        pattern = re.compile(
            r"(# --- module pdpa.*?except ImportError:\s*\n\s*pass\s*\n)",
            re.S,
        )
        m = pattern.search(content)
        if m:
            insert_at = m.end(1)
            content = content[:insert_at] + "\n" + iot_block + content[insert_at:]
        else:
            # fallback: แทรกก่อน "config = context.config"
            anchor = "config = context.config"
            idx = content.find(anchor)
            if idx == -1:
                warn("Cannot find anchor in env.py — skipping")
                return
            content = content[:idx] + iot_block + content[idx:]

        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            ok(f"backup: {self.env_py}.bak")
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated — registered iot models")
        else:
            skip(f"{self.env_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  3. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[3/7] SQL — {self.module} (prefix={self.prefix})")
        self._create_v001()
        self._create_v002()
        self._create_v003()

    def _create_v001(self) -> None:
        content = self._v001_sql()
        self.writer.write(f"{self.sql_dir}/V001__create_{self.module}.sql", content)

    def _create_v002(self) -> None:
        content = self._v002_sql()
        self.writer.write(f"{self.sql_dir}/V002__seed_{self.module}.sql", content)

    def _create_v003(self) -> None:
        content = self._v003_sql()
        self.writer.write(f"{self.sql_dir}/V003__rollback_{self.module}.sql", content)

    def _v001_sql(self) -> str:
        p = self.prefix
        return f"""-- ═══════════════════════════════════════════════════════════════
-- V001__create_{self.module}.sql | Module: {self.module} | Prefix: {p}
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE SCHEMA IF NOT EXISTS tenant_{p};

-- ─── devices ─────────────────────────────────────
CREATE TABLE tenant_{p}.devices (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID NOT NULL,
    hardware_id       INTEGER NOT NULL,
    type_id           INTEGER NOT NULL DEFAULT 0,
    location_id       INTEGER NOT NULL DEFAULT 0,
    device_sn         VARCHAR(100) NOT NULL DEFAULT '',
    device_name       VARCHAR(255) NOT NULL,
    device_type       VARCHAR(100) NOT NULL DEFAULT '',
    location_name     VARCHAR(255) NOT NULL DEFAULT '',
    mqtt_id           INTEGER NOT NULL DEFAULT 0,
    mqtt_main_id      INTEGER NOT NULL DEFAULT 0,
    mqtt_topic        VARCHAR(500) NOT NULL DEFAULT '',
    mqtt_name         VARCHAR(255) NOT NULL DEFAULT '',
    mqtt_username     VARCHAR(255) NOT NULL DEFAULT '',
    mqtt_password     VARCHAR(255) NOT NULL DEFAULT '',
    unit              VARCHAR(50) NOT NULL DEFAULT '',
    status            VARCHAR(50) NOT NULL DEFAULT 'offline',
    icon              VARCHAR(255) NOT NULL DEFAULT '',
    icon_color        VARCHAR(50) NOT NULL DEFAULT '',
    description       VARCHAR(500) NOT NULL DEFAULT '',
    firmware_version  VARCHAR(50) NOT NULL DEFAULT '',
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_iot_hardware CHECK (hardware_id IN (1,2,3,4)),
    CONSTRAINT ck_iot_status CHECK (status IN ('online','offline','error','maintenance'))
);

CREATE INDEX ix_iot_device_tenant ON tenant_{p}.devices(tenant_id);
CREATE INDEX ix_iot_device_hardware ON tenant_{p}.devices(hardware_id, is_active);
CREATE INDEX ix_iot_device_topic ON tenant_{p}.devices(mqtt_topic);
CREATE INDEX ix_iot_device_location ON tenant_{p}.devices(location_id);

-- ─── device_configs ──────────────────────────────
CREATE TABLE tenant_{p}.device_configs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL,
    device_id               UUID NOT NULL,
    max_value               DOUBLE PRECISION NOT NULL DEFAULT 0,
    min_value               DOUBLE PRECISION NOT NULL DEFAULT 0,
    warning_threshold       DOUBLE PRECISION NOT NULL DEFAULT 0,
    alert_threshold         DOUBLE PRECISION NOT NULL DEFAULT 0,
    recovery_warning        DOUBLE PRECISION NOT NULL DEFAULT 0,
    recovery_alert          DOUBLE PRECISION NOT NULL DEFAULT 0,
    calibration_offset      DOUBLE PRECISION NOT NULL DEFAULT 0,
    calibration_multiplier  DOUBLE PRECISION NOT NULL DEFAULT 1,
    mqtt_control_on         VARCHAR(255) NOT NULL DEFAULT '',
    mqtt_control_off        VARCHAR(255) NOT NULL DEFAULT '',
    action_name             VARCHAR(255) NOT NULL DEFAULT '',
    config_json             VARCHAR(2000) NOT NULL DEFAULT '{{}}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_iot_config_device UNIQUE (tenant_id, device_id)
);

-- ─── device_statuses ─────────────────────────────
CREATE TABLE tenant_{p}.device_statuses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    device_id       UUID NOT NULL,
    is_online       BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen       TIMESTAMPTZ,
    last_value      DOUBLE PRECISION NOT NULL DEFAULT 0,
    last_alarm      INTEGER NOT NULL DEFAULT 0,
    count_alarm     INTEGER NOT NULL DEFAULT 0,
    event           INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(50) NOT NULL DEFAULT 'offline',
    sensor_data     VARCHAR(500) NOT NULL DEFAULT '',
    sensor_min      DOUBLE PRECISION NOT NULL DEFAULT 0,
    sensor_max      DOUBLE PRECISION NOT NULL DEFAULT 0,
    sensor_avg      DOUBLE PRECISION NOT NULL DEFAULT 0,
    battery         DOUBLE PRECISION NOT NULL DEFAULT 0,
    rssi            INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_iot_status_device UNIQUE (tenant_id, device_id)
);

-- ─── device_alerts ───────────────────────────────
CREATE TABLE tenant_{p}.device_alerts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL,
    device_id     UUID NOT NULL,
    alert_type    VARCHAR(50) NOT NULL DEFAULT '',
    severity      VARCHAR(20) NOT NULL DEFAULT 'low',
    title         VARCHAR(255) NOT NULL DEFAULT '',
    message       VARCHAR(1000) NOT NULL DEFAULT '',
    value_data    DOUBLE PRECISION NOT NULL DEFAULT 0,
    value_alarm   DOUBLE PRECISION NOT NULL DEFAULT 0,
    resolved      BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_iot_severity CHECK (severity IN ('info','low','medium','high','critical'))
);

CREATE INDEX ix_iot_alert_device ON tenant_{p}.device_alerts(device_id, resolved);
CREATE INDEX ix_iot_alert_severity ON tenant_{p}.device_alerts(severity, created_at DESC);

-- ─── iot_data ────────────────────────────────────
CREATE TABLE tenant_{p}.iot_data (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID NOT NULL,
    device_id      UUID NOT NULL,
    data_json      TEXT NOT NULL DEFAULT '{{}}',
    timestamp      TIMESTAMPTZ,
    location_id    INTEGER NOT NULL DEFAULT 0,
    metadata_json  TEXT NOT NULL DEFAULT '{{}}',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_iot_data_device_time ON tenant_{p}.iot_data(device_id, created_at DESC);
CREATE INDEX ix_iot_data_tenant ON tenant_{p}.iot_data(tenant_id);

-- ─── alarm_logs ──────────────────────────────────
CREATE TABLE tenant_{p}.alarm_logs (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID NOT NULL,
    device_id             UUID NOT NULL,
    alarm_action_id       INTEGER NOT NULL DEFAULT 0,
    alarm_type            INTEGER NOT NULL DEFAULT 0,
    alarm_status          INTEGER NOT NULL DEFAULT 0,
    value_data            DOUBLE PRECISION NOT NULL DEFAULT 0,
    value_alarm           DOUBLE PRECISION NOT NULL DEFAULT 0,
    title                 VARCHAR(255) NOT NULL DEFAULT '',
    subject               VARCHAR(500) NOT NULL DEFAULT '',
    content               TEXT NOT NULL DEFAULT '',
    data_alarm            INTEGER NOT NULL DEFAULT 0,
    data_alarm_raw        INTEGER NOT NULL DEFAULT 0,
    event_control         INTEGER NOT NULL DEFAULT 0,
    message_mqtt_control  VARCHAR(500) NOT NULL DEFAULT '',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_iot_alarm_device ON tenant_{p}.alarm_logs(device_id, created_at DESC);
CREATE INDEX ix_iot_alarm_status ON tenant_{p}.alarm_logs(alarm_status, created_at DESC);

-- ─── activity_logs ───────────────────────────────
CREATE TABLE tenant_{p}.activity_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL,
    log_type      VARCHAR(50) NOT NULL DEFAULT '',
    device_id     UUID,
    user_id       UUID,
    severity      VARCHAR(20) NOT NULL DEFAULT 'info',
    data_json     TEXT NOT NULL DEFAULT '{{}}',
    description   TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_iot_activity_device ON tenant_{p}.activity_logs(device_id, created_at DESC);
CREATE INDEX ix_iot_activity_type ON tenant_{p}.activity_logs(log_type, created_at DESC);

-- ─── schedules ───────────────────────────────────
CREATE TABLE tenant_{p}.schedules (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL,
    schedule_id   INTEGER NOT NULL DEFAULT 0,
    device_id     UUID NOT NULL,
    start_time    VARCHAR(10) NOT NULL DEFAULT '',
    end_time      VARCHAR(10) NOT NULL DEFAULT '',
    event         VARCHAR(50) NOT NULL DEFAULT '',
    monday        BOOLEAN NOT NULL DEFAULT FALSE,
    tuesday       BOOLEAN NOT NULL DEFAULT FALSE,
    wednesday     BOOLEAN NOT NULL DEFAULT FALSE,
    thursday      BOOLEAN NOT NULL DEFAULT FALSE,
    friday        BOOLEAN NOT NULL DEFAULT FALSE,
    saturday      BOOLEAN NOT NULL DEFAULT FALSE,
    sunday        BOOLEAN NOT NULL DEFAULT FALSE,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_iot_schedule_device ON tenant_{p}.schedules(device_id, is_active);

-- ─── Trigger ─────────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_updated_at_{p}()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_iot_device_updated BEFORE UPDATE ON tenant_{p}.devices
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_config_updated BEFORE UPDATE ON tenant_{p}.device_configs
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_status_updated BEFORE UPDATE ON tenant_{p}.device_statuses
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_alert_updated BEFORE UPDATE ON tenant_{p}.device_alerts
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_data_updated BEFORE UPDATE ON tenant_{p}.iot_data
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_alarm_updated BEFORE UPDATE ON tenant_{p}.alarm_logs
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_activity_updated BEFORE UPDATE ON tenant_{p}.activity_logs
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();
CREATE TRIGGER trg_iot_schedule_updated BEFORE UPDATE ON tenant_{p}.schedules
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{p}();

-- ─── RLS ─────────────────────────────────────────
ALTER TABLE tenant_{p}.devices ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_device ON tenant_{p}.devices
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.device_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_config ON tenant_{p}.device_configs
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.device_statuses ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_status ON tenant_{p}.device_statuses
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.device_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_alert ON tenant_{p}.device_alerts
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.iot_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_data ON tenant_{p}.iot_data
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.alarm_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_alarm ON tenant_{p}.alarm_logs
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.activity_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_activity ON tenant_{p}.activity_logs
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

ALTER TABLE tenant_{p}.schedules ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_iot_schedule ON tenant_{p}.schedules
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        p = self.prefix
        return f"""-- ═══════════════════════════════════════════════════════════════
-- V002__seed_{self.module}.sql
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO tenant_{p}.devices
    (tenant_id, hardware_id, device_name, device_type, unit, mqtt_topic, mqtt_name)
VALUES
    ('00000000-0000-0000-0000-000000000001', 1, 'Cold Room 1 Temp', 'temperature', '°C', 'iot/coldroom1/DATA', 'temp1'),
    ('00000000-0000-0000-0000-000000000001', 1, 'Cold Room 1 Humidity', 'humidity', '%', 'iot/coldroom1/DATA', 'hum1'),
    ('00000000-0000-0000-0000-000000000001', 3, 'Cold Room 1 Door', 'relay', '', 'iot/coldroom1/DATA', 'door1'),
    ('00000000-0000-0000-0000-000000000001', 4, 'Fire Sensor A', 'fire', '', 'iot/fire/DATA', 'fire_a')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        p = self.prefix
        return f"""-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_{self.module}.sql
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_iot_schedule_updated ON tenant_{p}.schedules;
DROP TRIGGER IF EXISTS trg_iot_activity_updated ON tenant_{p}.activity_logs;
DROP TRIGGER IF EXISTS trg_iot_alarm_updated ON tenant_{p}.alarm_logs;
DROP TRIGGER IF EXISTS trg_iot_data_updated ON tenant_{p}.iot_data;
DROP TRIGGER IF EXISTS trg_iot_alert_updated ON tenant_{p}.device_alerts;
DROP TRIGGER IF EXISTS trg_iot_status_updated ON tenant_{p}.device_statuses;
DROP TRIGGER IF EXISTS trg_iot_config_updated ON tenant_{p}.device_configs;
DROP TRIGGER IF EXISTS trg_iot_device_updated ON tenant_{p}.devices;

DROP POLICY IF EXISTS p_iot_schedule ON tenant_{p}.schedules;
DROP POLICY IF EXISTS p_iot_activity ON tenant_{p}.activity_logs;
DROP POLICY IF EXISTS p_iot_alarm ON tenant_{p}.alarm_logs;
DROP POLICY IF EXISTS p_iot_data ON tenant_{p}.iot_data;
DROP POLICY IF EXISTS p_iot_alert ON tenant_{p}.device_alerts;
DROP POLICY IF EXISTS p_iot_status ON tenant_{p}.device_statuses;
DROP POLICY IF EXISTS p_iot_config ON tenant_{p}.device_configs;
DROP POLICY IF EXISTS p_iot_device ON tenant_{p}.devices;

DROP TABLE IF EXISTS tenant_{p}.schedules CASCADE;
DROP TABLE IF EXISTS tenant_{p}.activity_logs CASCADE;
DROP TABLE IF EXISTS tenant_{p}.alarm_logs CASCADE;
DROP TABLE IF EXISTS tenant_{p}.iot_data CASCADE;
DROP TABLE IF EXISTS tenant_{p}.device_alerts CASCADE;
DROP TABLE IF EXISTS tenant_{p}.device_statuses CASCADE;
DROP TABLE IF EXISTS tenant_{p}.device_configs CASCADE;
DROP TABLE IF EXISTS tenant_{p}.devices CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_{p}();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  6. ALEMBIC MIGRATION
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[6/7] ALEMBIC — {self.module} (8 tables)")
        rev = f"{self.prefix}_001"
        prev = self._get_head_revision()

        table_names = [
            "devices", "device_configs", "device_statuses", "device_alerts",
            "iot_data", "alarm_logs", "activity_logs", "schedules",
        ]

        create_block = "\n\n".join([
            self._sql_devices(),
            self._sql_device_configs(),
            self._sql_device_statuses(),
            self._sql_device_alerts(),
            self._sql_iot_data(),
            self._sql_alarm_logs(),
            self._sql_activity_logs(),
            self._sql_schedules(),
        ])

        trigger_block = "\n".join(
            f'''        op.execute(f"""
            CREATE TRIGGER trg_{tbl}_updated_at
                BEFORE UPDATE ON {{SCHEMA}}.{tbl}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{self.prefix}();
        """)'''
            for tbl in table_names
        )

        rls_loop = "\n".join(f'        "{t}",' for t in table_names)

        drop_block = "\n".join(
            f'''        op.execute(f"DROP POLICY IF EXISTS p_{tbl}_tenant ON {{SCHEMA}}.{tbl};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{tbl}_updated_at ON {{SCHEMA}}.{tbl};")
        op.execute(f"DROP TABLE IF EXISTS {{SCHEMA}}.{tbl} CASCADE;")'''
            for tbl in reversed(table_names)
        )

        content = f'''"""add {self.module} tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: สร้างตาราง {self.module} 8 ตาราง (devices, device_configs, device_statuses,
    device_alerts, iot_data, alarm_logs, activity_logs, schedules)
    + indexes + triggers + RLS
EN: create 8 {self.module} tables + indexes + triggers + RLS
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "{rev}"
down_revision: Union[str, None] = "{prev}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "tenant_{self.prefix}"


def upgrade() -> None:
    """TH: สร้างตาราง {self.module} | EN: create {self.module} tables"""

    op.execute(f"CREATE SCHEMA IF NOT EXISTS {{SCHEMA}}")

{create_block}

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_{self.prefix}()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

{trigger_block}

    for tbl in (
{rls_loop}
    ):
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    """TH: ลบตาราง {self.module} | EN: drop {self.module} tables"""

{drop_block}

    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_{self.prefix}();")
    # ⚠️ ไม่ drop schema — เพราะอาจมีตารางอื่น
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py",
            content,
        )

    # ─── table builders — ย่อ (เนื้อหาเดียวกับเวอร์ชันก่อน) ───
    def _sql_devices(self) -> str:
        return '''    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hardware_id", sa.Integer, nullable=False),
        sa.Column("type_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("location_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("device_sn", sa.String(100), nullable=False, server_default=""),
        sa.Column("device_name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(100), nullable=False, server_default=""),
        sa.Column("location_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("mqtt_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("mqtt_main_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("mqtt_topic", sa.String(500), nullable=False, server_default=""),
        sa.Column("mqtt_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("mqtt_username", sa.String(255), nullable=False, server_default=""),
        sa.Column("mqtt_password", sa.String(255), nullable=False, server_default=""),
        sa.Column("unit", sa.String(50), nullable=False, server_default=""),
        sa.Column("status", sa.String(50), nullable=False, server_default="offline"),
        sa.Column("icon", sa.String(255), nullable=False, server_default=""),
        sa.Column("icon_color", sa.String(50), nullable=False, server_default=""),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("firmware_version", sa.String(50), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("hardware_id IN (1,2,3,4)", name="ck_iot_hardware"),
        sa.CheckConstraint(
            "status IN ('online','offline','error','maintenance')",
            name="ck_iot_status",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_device_tenant", "devices",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_iot_device_hardware", "devices",
                    ["hardware_id", "is_active"], schema=SCHEMA)
    op.create_index("ix_iot_device_topic", "devices",
                    ["mqtt_topic"], schema=SCHEMA)
    op.create_index("ix_iot_device_location", "devices",
                    ["location_id"], schema=SCHEMA)'''

    def _sql_device_configs(self) -> str:
        return '''    op.create_table(
        "device_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("max_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("min_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("warning_threshold", sa.Float, nullable=False, server_default="0"),
        sa.Column("alert_threshold", sa.Float, nullable=False, server_default="0"),
        sa.Column("recovery_warning", sa.Float, nullable=False, server_default="0"),
        sa.Column("recovery_alert", sa.Float, nullable=False, server_default="0"),
        sa.Column("calibration_offset", sa.Float, nullable=False, server_default="0"),
        sa.Column("calibration_multiplier", sa.Float, nullable=False, server_default="1"),
        sa.Column("mqtt_control_on", sa.String(255), nullable=False, server_default=""),
        sa.Column("mqtt_control_off", sa.String(255), nullable=False, server_default=""),
        sa.Column("action_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("config_json", sa.String(2000), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "device_id", name="uq_iot_config_device"),
        schema=SCHEMA,
    )'''

    def _sql_device_statuses(self) -> str:
        return '''    op.create_table(
        "device_statuses",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_online", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("last_alarm", sa.Integer, nullable=False, server_default="0"),
        sa.Column("count_alarm", sa.Integer, nullable=False, server_default="0"),
        sa.Column("event", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="offline"),
        sa.Column("sensor_data", sa.String(500), nullable=False, server_default=""),
        sa.Column("sensor_min", sa.Float, nullable=False, server_default="0"),
        sa.Column("sensor_max", sa.Float, nullable=False, server_default="0"),
        sa.Column("sensor_avg", sa.Float, nullable=False, server_default="0"),
        sa.Column("battery", sa.Float, nullable=False, server_default="0"),
        sa.Column("rssi", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "device_id", name="uq_iot_status_device"),
        schema=SCHEMA,
    )'''

    def _sql_device_alerts(self) -> str:
        return '''    op.create_table(
        "device_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alert_type", sa.String(50), nullable=False, server_default=""),
        sa.Column("severity", sa.String(20), nullable=False, server_default="low"),
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
        sa.Column("message", sa.String(1000), nullable=False, server_default=""),
        sa.Column("value_data", sa.Float, nullable=False, server_default="0"),
        sa.Column("value_alarm", sa.Float, nullable=False, server_default="0"),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("acknowledged", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "severity IN ('info','low','medium','high','critical')",
            name="ck_iot_severity",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_alert_device", "device_alerts",
                    ["device_id", "resolved"], schema=SCHEMA)
    op.create_index("ix_iot_alert_severity", "device_alerts",
                    ["severity", "created_at"], schema=SCHEMA)'''

    def _sql_iot_data(self) -> str:
        return '''    op.create_table(
        "iot_data",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_data_device_time", "iot_data",
                    ["device_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_iot_data_tenant", "iot_data",
                    ["tenant_id"], schema=SCHEMA)'''

    def _sql_alarm_logs(self) -> str:
        return '''    op.create_table(
        "alarm_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alarm_action_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("alarm_type", sa.Integer, nullable=False, server_default="0"),
        sa.Column("alarm_status", sa.Integer, nullable=False, server_default="0"),
        sa.Column("value_data", sa.Float, nullable=False, server_default="0"),
        sa.Column("value_alarm", sa.Float, nullable=False, server_default="0"),
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
        sa.Column("subject", sa.String(500), nullable=False, server_default=""),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("data_alarm", sa.Integer, nullable=False, server_default="0"),
        sa.Column("data_alarm_raw", sa.Integer, nullable=False, server_default="0"),
        sa.Column("event_control", sa.Integer, nullable=False, server_default="0"),
        sa.Column("message_mqtt_control", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_alarm_device", "alarm_logs",
                    ["device_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_iot_alarm_status", "alarm_logs",
                    ["alarm_status", "created_at"], schema=SCHEMA)'''

    def _sql_activity_logs(self) -> str:
        return '''    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("log_type", sa.String(50), nullable=False, server_default=""),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("data_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_activity_device", "activity_logs",
                    ["device_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_iot_activity_type", "activity_logs",
                    ["log_type", "created_at"], schema=SCHEMA)'''

    def _sql_schedules(self) -> str:
        return '''    op.create_table(
        "schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schedule_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_time", sa.String(10), nullable=False, server_default=""),
        sa.Column("end_time", sa.String(10), nullable=False, server_default=""),
        sa.Column("event", sa.String(50), nullable=False, server_default=""),
        sa.Column("monday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("tuesday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("wednesday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("thursday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("friday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("saturday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("sunday", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_iot_schedule_device", "schedules",
                    ["device_id", "is_active"], schema=SCHEMA)'''

    def _get_head_revision(self) -> str:
        for candidate in ("migrations/versions", "alembic/versions"):
            versions = self.root / candidate
            if not versions.exists():
                continue

            revisions: set[str] = set()
            down_revisions: set[str] = set()
            for f in versions.glob("*.py"):
                content = f.read_text(encoding="utf-8")
                m = re.search(
                    r'^revision\s*(?::\s*str)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if m:
                    revisions.add(m.group(1))
                d = re.search(
                    r'^down_revision\s*(?::[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if d:
                    down_revisions.add(d.group(1))

            heads = revisions - down_revisions
            if heads:
                return next(iter(heads))

        return "None"

    # ═══════════════════════════════════════════════════════════
    #  7. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[7/7] SWAGGER — {self.module}")
        content = f'''"""OpenAPI docs — {self.module} module"""
from __future__ import annotations
from typing import Any


def register_{self.module}_openapi(app: object) -> None:
    """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "{self.module}" for t in tags):
            tags.append({{
                "name": "{self.module}",
                "description": (
                    "โมดูล {self.module} — Real-time Sensor & Alarm Monitoring\\n\\n"
                    "• MQTT Ingest\\n"
                    "• Alarm Evaluation (hardware_id 1-4)\\n"
                    "• Device Control\\n"
                    "• Time-series (InfluxDB)\\n"
                    "• WebSocket Real-time"
                ),
                "externalDocs": {{
                    "description": "iot Module README",
                    "url": "/docs/README_{self.module}.md",
                }},
            }})
        schema["info"] = schema.get("info", {{}})
        schema["info"].setdefault("x-module", "{self.module}")
        schema["info"].setdefault("x-layer", "{self.layer_name}")
        schema["info"].setdefault("x-prefix", "{self.prefix}")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
'''
        self.writer.write(f"{self.mod_root}/presentation/swagger.py", content)

    # ═══════════════════════════════════════════════════════════
    #  8. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[8/8] POSTMAN — {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json",
            self._postman_json(),
        )

    def _postman_json(self) -> str:
        return f'''{{
  "info": {{
    "name": "{self.module} API",
    "_postman_id": "{uuid.uuid4()}",
    "description": "iot Module — Real-time Sensor & Alarm Monitoring Platform",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }},
    {{ "key": "device_id", "value": "" }},
    {{ "key": "topic", "value": "iot/coldroom1/DATA" }},
    {{ "key": "bucket", "value": "iot_sensors" }}
  ],
  "item": [
    {{
      "name": "Connection",
      "item": [
        {{
          "name": "Connection Status",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/status",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "status"]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Topic Data",
      "item": [
        {{
          "name": "Get Topic Data",
          "request": {{
            "method": "POST",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/topic-data?topic={{{{topic}}}}",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "topic-data"],
              "query": [{{ "key": "topic", "value": "{{{{topic}}}}" }}]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Device Control",
      "item": [
        {{
          "name": "Control Device",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/control",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "control"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"topic\\": \\"iot/coldroom1/CTRL\\",\\n  \\"message\\": \\"ON\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Device Management",
      "item": [
        {{
          "name": "List Devices",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/devices?page=1&page_size=20",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "devices"],
              "query": [
                {{ "key": "page", "value": "1" }},
                {{ "key": "page_size", "value": "20" }}
              ]
            }}
          }}
        }},
        {{
          "name": "Monitor Device Group",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/monitor-device-group",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "monitor-device-group"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"bucket\\": \\"iot_sensors\\",\\n  \\"hardware_id\\": 1,\\n  \\"lang\\": \\"th\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Alarm",
      "item": [
        {{
          "name": "Alarm Device Status",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/alarm-device-status",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "alarm-device-status"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"bucket\\": \\"iot_sensors\\",\\n  \\"measurement\\": \\"temperature\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Data",
      "item": [
        {{
          "name": "Export Data (JSON)",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/iot/export",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "iot", "export"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"device_id\\": \\"1\\",\\n  \\"format\\": \\"json\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  RUN ALL
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.activate_module()   # ← app.py + env.py

    # ═══════════════════════════════════════════════════════════
    #  SUMMARY
    # ═══════════════════════════════════════════════════════════
    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — module: {self.module}")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Skipped : {len(self.writer.skipped)} files")
        info(f"  Backups : {len(self.writer.backups)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Review:    tree app/modules/{self.module}")
        print(f"    2. Alembic:   alembic upgrade head")
        print(f"    3. Swagger:   http://localhost:8000/docs")
        print(f"    4. Postman:   docs/postman/{self.module}.json")
        print()


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = """
═══════════════════════════════════════════════════════════════
  create_module_iot.py — iot Module Generator v2.1
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_iot.py <action> <module> [layer] [prefix] [options]

  ACTIONS (9 งาน)
    create      [1] สร้าง module structure (domain/application/
                    infrastructure/presentation)
    activate    [2] Register router ใน app/app.py + models ใน migrations/env.py
    sql         [3] สร้าง SQL migrations V001/V002/V003 + RLS
    update      [4] Update app/app.py อย่างเดียว
    update-env  [5] Update migrations/env.py อย่างเดียว
    alembic     [6] สร้าง Alembic migration (8 tables + triggers + RLS)
    swagger     [7] สร้าง OpenAPI docs (tag: iot)
    postman     [8] สร้าง Postman collection
    all         ทำทั้งหมด
    help        แสดง help

  POSITIONAL
    module      ชื่อ module (default: iot)
    layer       Layer number 0-7 (default: 6)
    prefix      3-char DB prefix (default: iot)

  OPTIONS
    --force              เขียนทับไฟล์เดิม
    --template <A-G>     Template (default: A)
    --project-root <path> Project root path

  EXAMPLES
    python create_module_iot.py all iot 6 iot
    python create_module_iot.py create iot 6 iot --force
    python create_module_iot.py activate iot
    python create_module_iot.py update-env iot
    python create_module_iot.py alembic iot iot
    python create_module_iot.py help
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="iot")
    parser.add_argument("layer", nargs="?", default="6")
    parser.add_argument("prefix", nargs="?", default="iot")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--template", default="A")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"Project root not found: {root}")
        return 1

    gen = iotModuleGenerator(
        project_root=root,
        module=args.module,
        layer=args.layer,
        prefix=args.prefix,
        template=args.template,
        force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  LAYER   : {gen.layer} ({gen.layer_name})")
    info(f"  PREFIX  : {gen.prefix}")
    info(f"  ACTION  : {args.action}")
    info(f"  FORCE   : {args.force}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "activate": gen.activate_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "all": gen.run_all,
    }

    if args.action not in action_map:
        err(f"Unknown action: {args.action}")
        print(HELP)
        return 1

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
