# Plan 2: File-by-File Implementation Details
## Detailed Code Translation Reference

---

## 1. Core Files

### 1.1 `app/core/influxdb_client.py`

**Source:** `pkg/influxdb/client.go` (625 lines)

**Key structures to translate:**
- `InfluxClient` struct -> `InfluxDBClientWrapper` class
- `QueryParams` struct -> `QueryParams` dataclass
- `StatisticalResult` struct -> `StatisticalResult` dataclass
- `SummaryStats` struct -> `SummaryStats` dataclass
- `QueryMetadata` struct -> `QueryMetadata` dataclass
- `MeanCalculationResult` struct -> `MeanCalculationResult` dataclass
- `CountResult` struct -> `CountResult` dataclass
- `Client` interface -> `InfluxDBClientProtocol` (optional)

**Methods to translate:**
| Go Method | Python Method | Lines |
|-----------|---------------|-------|
| `NewInfluxClient()` | `__init__()` | 65-90 |
| `Close()` | `close()` | 92-94 |
| `WriteData()` | `write_data()` | 96-103 |
| `WritePoint()` | `write_point()` | 106-110 |
| `QueryFilterData()` | `query_filter_data()` | 113-135 |
| `Querydevicechart()` | `query_device_chart()` | 138-160 |
| `QueryFilterDataRs()` | `query_filter_data_rs()` | 163-188 |
| `CountRows()` | `count_rows()` | 190-215 |
| `CalculateStatistics()` | `calculate_statistics()` | 217-350 |
| `calculateSummary()` | `_calculate_summary()` | 352-420 |
| `executeQuery()` | `_execute_query()` | 440-480 |
| `New()` | (factory function) | 550-580 |

**Key differences:**
- Go: `influxdb2.NewClientWithOptions()` -> Python: `InfluxDBClient()`
- Go: `i.queryApi.Query(ctx, fluxQuery)` -> Python: `self._query_api.query(flux_query, org=self._org)`
- Go: `result.Record()` -> Python: `record.get_time()`, `record.get_value()`
- Go: context timeout -> Python: timeout in client constructor

---

### 1.2 `app/core/mqtt_client.py`

**Source:** `pkg/mqtt/client.go` (441 lines)

**Key structures to translate:**
- `mqttClient` struct -> `MQTTClient` class
- `requestManager` struct -> internal `_PendingRequest` + lock-based manager
- `pendingRequest` struct -> `_PendingRequest` dataclass

**Methods to translate:**
| Go Method | Python Method | Lines |
|-----------|---------------|-------|
| `New()` | `__init__()` | 200-250 |
| `Connect()` | `connect()` | 252-270 |
| `Disconnect()` | `disconnect()` | 272-280 |
| `Publish()` | `publish()` | 282-295 |
| `Subscribe()` | `subscribe()` | 297-310 |
| `SubscribeMultiple()` | (removed, use multiple subscribe) | - |
| `Unsubscribe()` | `unsubscribe()` | 312-318 |
| `IsConnected()` | `is_connected()` | 320-322 |
| `RequestData()` | `request_data()` | 324-380 |
| `getTopic()` | `_get_topic()` | 100-180 |
| `GetDataFromTopic()` | `get_data_from_topic()` | 382-441 |
| `incrementSubscription()` | `_increment_subscription()` | 182-200 |
| `decrementSubscription()` | `_decrement_subscription()` | 202-218 |

**Key differences:**
- Go: `paho.mqtt.golang` callbacks -> Python: `paho.mqtt.client` callbacks
- Go: goroutines + channels -> Python: threads + Events
- Go: `token.Wait()` -> Python: `result.wait_for_publish()`
- Go: `mqtt.Client` -> Python: `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)`

---

### 1.3 `app/core/queue/manager.py`

**Source:** `internal/modules/queue/manager.go` (329 lines)

**Key structures to translate:**
- `RedisQueue` struct -> `RedisQueue` class
- `QueueMessage` struct -> `QueueMessage` dataclass

**Methods to translate:**
| Go Method | Python Method | Lines |
|-----------|---------------|-------|
| `NewRedisQueue()` | `__init__()` | 15-40 |
| `Publish()` | `publish()` | 42-65 |
| `Consume()` | `consume()` | 67-95 |
| `Complete()` | `complete()` | 97-115 |
| `Retry()` | `retry()` | 117-135 |
| `MoveToDLQ()` | `_move_to_dlq()` | 137-160 |
| `GetStats()` | `get_stats()` | 162-175 |
| `ProcessMessages()` | `process_messages()` | 177-200 |

---

## 2. Domain Files

### 2.1 `app/modules/iot/domain/entities/device.py`

**Source:** `internal/modules/iot/models/device.go`

**Go struct fields -> Python dataclass fields:**
```go
DeviceID      int      `json:"device_id" gorm:"column:device_id;primaryKey"`
TypeID        int      `json:"type_id" gorm:"column:type_id"`
LocationID    int      `json:"location_id" gorm:"column:location_id"`
HardwareID    int      `json:"hardware_id" gorm:"column:hardware_id"`
SN            string   `json:"sn" gorm:"column:sn"`
DeviceName    string   `json:"device_name" gorm:"column:device_name"`
MQTTID        int      `json:"mqtt_id" gorm:"column:mqtt_id"`
MQTTMainID    int      `json:"mqtt_main_id" gorm:"column:mqtt_main_id"`
MQTTTopic     string   `json:"mqtt_topic" gorm:"column:mqtt_topic"`
MQTTName      string   `json:"mqtt_name" gorm:"column:mqtt_name"`
MQTTUsername   string   `json:"mqtt_username" gorm:"column:mqtt_username"`
MQTTPassword  string   `json:"mqtt_password" gorm:"column:mqtt_password"`
Unit          string   `json:"unit" gorm:"column:unit"`
Status        string   `json:"status" gorm:"column:status"`
Icon          string   `json:"icon" gorm:"column:icon"`
IconColor     string   `json:"icon_color" gorm:"column:icon_color"`
```

**Python translation:**
```python
@dataclass
class Device(BaseEntity):
    hardware_id: int = 0
    type_id: int = 0
    location_id: int = 0
    device_sn: str = ""
    device_name: str = ""
    mqtt_id: int = 0
    mqtt_main_id: int = 0
    mqtt_topic: str = ""
    mqtt_name: str = ""
    mqtt_username: str = ""
    mqtt_password: str = ""
    unit: str = ""
    status: str = "offline"
    icon: str = ""
    icon_color: str = ""
```

---

### 2.2 `app/modules/iot/domain/helpers/alarm_logic.py`

**Source:** `pkg/helpers/iot.go` (405 lines)

**Key function to translate:**
- `processAlarmDetail()` -> `evaluate_alarm()`
- `AlarmDetailValidate()` -> `evaluate_alarm(..., lang="th")`
- `AlarmDetailValidateEn()` -> `evaluate_alarm(..., lang="en")`
- `AlarmDetailValidateTh()` -> `evaluate_alarm(..., lang="th")`

**Helper functions:**
- `toInt()` -> `_to_int()`
- `toFloat()` -> `_to_float()`
- `normalizeSensorValue()` -> `_normalize_sensor_value()`
- `StringConcat()` -> f-string (Python native)

**Message maps:**
- `thaiMessages` -> `_THAI_MESSAGES`
- `englishMessages` -> `_ENGLISH_MESSAGES`

---

## 3. Repository Files

### 3.1 `app/modules/iot/infrastructure/device_repository.py`

**Source:** `internal/modules/iot/repository/device_repo.go` (431 lines)

**Go methods -> Python methods:**
| Go Method | Python Method | GORM -> SQLAlchemy |
|-----------|---------------|-------------------|
| `GetDeviceByID()` | `find_by_id()` | `db.Where().First()` -> `select().where().scalar_one_or_none()` |
| `GetDevicesByBucket()` | `find_by_bucket()` | `db.Where().Find()` -> `select().where().scalars().all()` |
| `GetDevicesByLocation()` | `find_by_location()` | `db.Where().Find()` -> `select().where().scalars().all()` |
| `ListDevices()` | `find_all_paginated()` | `db.Offset().Limit().Find()` -> `select().offset().limit().scalars().all()` |
| `ListDevicesWithAlarm()` | `find_all_with_alarm()` | Complex join query |
| `CreateDevice()` | `create()` | `db.Create()` -> `session.add()` + `session.flush()` |
| `UpdateDevice()` | `update()` | `db.Save()` -> `session.flush()` |
| `DeleteDevice()` | `delete()` | `db.Delete()` -> soft delete |

---

## 4. UseCase File

### 4.1 `app/modules/iot/application/use_case.py`

**Source:** `internal/modules/iot/usecase/usecase.go` (1924 lines)

**Go interface methods -> Python methods:**
| Go Method | Python Method | Complexity |
|-----------|---------------|------------|
| `IsConnected()` | `is_connected()` | Simple |
| `IsCacheEnabled()` | `is_cache_enabled()` | Simple |
| `GetTopicData()` | `get_topic_data()` | Medium (Redis + MQTT) |
| `DeviceControl()` | `device_control()` | Medium |
| `DeviceControls()` | `device_controls()` | Simple (loop) |
| `GetDeviceList()` | `get_device_list()` | Simple |
| `GetDeviceListPage()` | `get_device_list_page()` | Simple |
| `GetDeviceBuckets()` | `get_device_buckets()` | Simple |
| `GetDeviceListByLocation()` | `get_device_list_by_location()` | Simple |
| `GetSenserCharts()` | `get_senser_charts()` | Medium (InfluxDB) |
| `GetSenserDataChart()` | `get_senser_data_chart()` | Medium |
| `GetSenserData()` | `get_senser_data()` | Medium |
| `GetDeviceSenserCharts()` | `get_device_senser_charts()` | Medium |
| `GetAlarmDeviceStatus()` | `get_alarm_device_status()` | **Complex** (alarm eval) |
| `GetAlarmDeviceStatusControl()` | `get_alarm_device_status_control()` | Simple wrapper |
| `GetMonitorDeviceGroup()` | `get_monitor_device_group()` | **Complex** (grouping) |
| `GetMonitorDeviceChart()` | `get_monitor_device_chart()` | Medium |
| `GetTopicDataDeviceChart()` | `get_topic_data_device_chart()` | Medium |
| `GetDeviceStatus()` | `get_device_status()` | Simple |
| `UpdateDeviceStatus()` | `update_device_status()` | Simple |
| `GetDeviceConfig()` | `get_device_config()` | Simple |
| `UpdateDeviceConfig()` | `update_device_config()` | Simple |
| `ProcessMqttData()` | `process_mqtt_data()` | Medium |
| `GetLatestData()` | `get_latest_data()` | Simple |
| `GetDataByDateRange()` | `get_data_by_date_range()` | Simple |
| `ListIotData()` | `list_iot_data()` | Simple |
| `GetDeviceStats()` | `get_device_stats()` | Medium |
| `ExportData()` | `export_data()` | Simple |
| `CleanupOldData()` | `cleanup_old_data()` | Simple |

---

## 5. Error Handling Mapping

### 5.1 Go `pkg/httpErrors` -> Python `app/modules/shared/exceptions.py`

```go
// Go
var ErrorNotFound = errors.New("not_found")
func ErrNotFound(err error) ErrRest {
    return &ErrResponse{
        Err:        err,
        Status:     http.StatusNotFound,
        StatusText: ErrorNotFound.Error(),
        Msg:        err.Error(),
    }
}
```

```python
# Python
class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

# Usage
raise NotFoundException(detail="Device not found")
```

**Error mapping:**
| Go Error | HTTP Status | Python Exception |
|----------|-------------|------------------|
| `ErrorBadRequest` | 400 | `BadRequestException` |
| `ErrorNotFound` | 404 | `NotFoundException` |
| `ErrorUnauthorized` | 401 | `UnauthorizedException` |
| `ErrorInternalServerError` | 500 | `InternalServerException` |
| `ErrorRequestTimeoutError` | 408 | `RequestTimeoutException` |
| `ErrorValidation` | 422 | `ValidationException` |
| `ErrorWrongPassword` | 401 | `UnauthorizedException` |
| `ErrorInactiveUser` | 403 | `ForbiddenException` |
| `ErrorNotEnoughPrivileges` | 403 | `ForbiddenException` |

---

## 6. Validation Mapping

### 6.1 Go `pkg/utils/validator.go` -> Python Pydantic

```go
// Go
var validate *validator.Validate
func ValidateStruct(ctx context.Context, s interface{}) error {
    return validate.StructCtx(ctx, s)
}
```

```python
# Python (Pydantic handles validation automatically)
from pydantic import BaseModel, Field, field_validator

class DeviceControlRequest(BaseModel):
    device_id: int = Field(..., gt=0)
    command: str = Field(..., min_length=1, max_length=100)

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        allowed = {"on", "off", "restart", "status"}
        if v.lower() not in allowed:
            raise ValueError(f"Command must be one of: {allowed}")
        return v.lower()
```

---

## 7. Config Mapping

### 7.1 Go `config/config.go` -> Python `app/core/settings.py`

```go
// Go
type Config struct {
    Postgres PostgresConfig
    Redis    RedisConfig
    MQTT     MQTTConfig
    InfluxDB InfluxDBConfig
}
```

```python
# Python
class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MQTT
    MQTT_BROKER: str = "tcp://localhost:1883"
    MQTT_CLIENT_ID: str = ""
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_KEEPALIVE: int = 30

    # InfluxDB
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = ""
    INFLUXDB_ORG: str = "my-org"
    INFLUXDB_BUCKET: str = "iot_sensors"
    INFLUXDB_TIMEOUT: int = 30

    class Config:
        env_file = ".env"
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# test/unit/iot/domain/test_alarm_logic.py
import pytest
from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO

class TestAlarmLogic:
    def test_normal_status(self):
        dto = AlarmDetailDTO(
            hardware_id=1,
            value_data=25.0,
            value_alarm=0,
            max_value=100.0,
            min_value=0.0,
            status_alert=80,
            status_warning=60,
        )
        result = evaluate_alarm(dto, lang="en")
        assert result.status == 5
        assert result.title == "Normal"

    def test_critical_max_exceeded(self):
        dto = AlarmDetailDTO(
            hardware_id=1,
            value_data=105.0,
            value_alarm=0,
            max_value=100.0,
            min_value=0.0,
            status_alert=80,
            status_warning=60,
        )
        result = evaluate_alarm(dto, lang="en")
        assert result.status == 2
        assert "Critical" in result.title

    def test_warning_threshold(self):
        dto = AlarmDetailDTO(
            hardware_id=1,
            value_data=65.0,
            value_alarm=0,
            max_value=100.0,
            min_value=0.0,
            status_alert=80,
            status_warning=60,
        )
        result = evaluate_alarm(dto, lang="en")
        assert result.status == 1
        assert result.title == "Warning"
```

### 8.2 Integration Tests

```python
# test/integration/iot/test_device_repository.py
import pytest
from app.modules.iot.infrastructure.device_repository import DeviceRepository

@pytest.mark.asyncio
class TestDeviceRepository:
    async def test_find_by_id(self, db_session):
        repo = DeviceRepository(db_session)
        device = await repo.find_by_id(1)
        assert device is not None
        assert device.hardware_id > 0

    async def test_find_all_active(self, db_session):
        repo = DeviceRepository(db_session)
        devices = await repo.find_all_active()
        assert isinstance(devices, list)
```

---

## 9. Dependency Injection Setup

```python
# app/modules/shared/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.redis import get_redis_client
from app.core.influxdb_client import InfluxDBClientWrapper
from app.core.mqtt_client import MQTTClient
from app.core.settings import settings

from app.modules.iot.infrastructure.device_repository import DeviceRepository
from app.modules.iot.infrastructure.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.iot_data_repository import IoTDataRepository
from app.modules.iot.infrastructure.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.activity_log_repository import ActivityLogRepository
from app.modules.iot.application.use_case import IoTUseCase


# Singleton instances
_influxdb_client: InfluxDBClientWrapper | None = None
_mqtt_client: MQTTClient | None = None


def get_influxdb_client() -> InfluxDBClientWrapper:
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


def get_mqtt_client() -> MQTTClient | None:
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
        except Exception as e:
            import logging
            logging.warning(f"MQTT connection failed: {e}")
            return None
    return _mqtt_client


async def get_iot_use_case(
    session: AsyncSession = Depends(get_async_session),
    redis_client = Depends(get_redis_client),
    influxdb_client: InfluxDBClientWrapper = Depends(get_influxdb_client),
    mqtt_client: MQTTClient | None = Depends(get_mqtt_client),
) -> IoTUseCase:
    return IoTUseCase(
        device_repository=DeviceRepository(session),
        device_config_repository=DeviceConfigRepository(session),
        device_status_repository=DeviceStatusRepository(session),
        device_alert_repository=DeviceAlertRepository(session),
        iot_data_repository=IoTDataRepository(session),
        alarm_log_repository=AlarmLogRepository(session),
        activity_log_repository=ActivityLogRepository(session),
        mqtt_client=mqtt_client,
        influxdb_client=influxdb_client,
        redis_client=redis_client,
    )
```

---

## 10. Router Registration

```python
# app/app.py - เพิ่ม IoT routes
from app.modules.iot.presentation.router import router as iot_router

def create_app() -> FastAPI:
    app = FastAPI(title="IoT Monitoring API")

    # ... existing middleware, routes ...

    # IoT module
    app.include_router(iot_router, prefix="/api/v1", tags=["IoT"])

    return app
```
