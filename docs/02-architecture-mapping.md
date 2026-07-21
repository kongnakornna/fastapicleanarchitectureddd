# Architecture Mapping
## Go Struct -> Python Model Translation

---

## 1. Go Models -> Python Domain Entities

### 1.1 Device (Go: `internal/modules/iot/models/device.go`)

```go
// Go Struct
type Device struct {
    gorm.Model
    HardwareID   int            `json:"hardware_id" gorm:"column:hardware_id"`
    DeviceName   string         `json:"device_name" gorm:"column:device_name"`
    DeviceType   string         `json:"device_type" gorm:"column:device_type"`
    LocationID   int            `json:"location_id" gorm:"column:location_id"`
    LocationName string         `json:"location_name" gorm:"column:location_name"`
    MqttTopic    string         `json:"mqtt_topic" gorm:"column:mqtt_topic"`
    MqttName     string         `json:"mqtt_name" gorm:"column:mqtt_name"`
    Unit         string         `json:"unit" gorm:"column:unit"`
    Status       string         `json:"status" gorm:"column:status"`
    IsActive     bool           `json:"is_active" gorm:"column:is_active"`
    DeviceConfig *DeviceConfig  `json:"device_config" gorm:"foreignKey:DeviceID"`
    DeviceStatus *DeviceStatus  `json:"device_status" gorm:"foreignKey:DeviceID"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/device.py
from dataclasses import dataclass, field
from datetime import datetime
from app.modules.shared.base import BaseEntity

@dataclass
class Device(BaseEntity):
    hardware_id: int
    device_name: str
    device_type: str
    mqtt_topic: str
    mqtt_name: str = ""
    unit: str = ""
    location_id: int | None = None
    location_name: str = ""
    status: str = "offline"
    is_active: bool = True

    # Related entities (not persisted directly)
    device_config: "DeviceConfig | None" = None
    device_status: "DeviceStatus | None" = None
```

### 1.2 DeviceConfig (Go: `models/device_config.go`)

```go
type DeviceConfig struct {
    gorm.Model
    DeviceID           int      `json:"device_id" gorm:"column:device_id"`
    MaxValue           float64  `json:"max_value" gorm:"column:max_value"`
    MinValue           float64  `json:"min_value" gorm:"column:min_value"`
    WarningThreshold   float64  `json:"warning_threshold" gorm:"column:warning_threshold"`
    AlertThreshold     float64  `json:"alert_threshold" gorm:"column:alert_threshold"`
    RecoveryWarning    float64  `json:"recovery_warning" gorm:"column:recovery_warning"`
    RecoveryAlert      float64  `json:"recovery_alert" gorm:"column:recovery_alert"`
    CalibrationOffset  float64  `json:"calibration_offset" gorm:"column:calibration_offset"`
    CalibrationMultiplier float64 `json:"calibration_multiplier" gorm:"column:calibration_multiplier"`
    MqttControlOn      string   `json:"mqtt_control_on" gorm:"column:mqtt_control_on"`
    MqttControlOff     string   `json:"mqtt_control_off" gorm:"column:mqtt_control_off"`
    ActionName         string   `json:"action_name" gorm:"column:action_name"`
    IsActive           bool     `json:"is_active" gorm:"column:is_active"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/device_config.py
@dataclass
class DeviceConfig(BaseEntity):
    device_id: int
    max_value: float = 0.0
    min_value: float = 0.0
    warning_threshold: float = 0.0
    alert_threshold: float = 0.0
    recovery_warning: float = 0.0
    recovery_alert: float = 0.0
    calibration_offset: float = 0.0
    calibration_multiplier: float = 1.0
    mqtt_control_on: str = ""
    mqtt_control_off: str = ""
    action_name: str = ""
    is_active: bool = True
```

### 1.3 DeviceStatus (Go: `models/device_status.go`)

```go
type DeviceStatus struct {
    gorm.Model
    DeviceID   int       `json:"device_id" gorm:"column:device_id"`
    Status     string    `json:"status" gorm:"column:status"`
    LastValue  float64   `json:"last_value" gorm:"column:last_value"`
    LastSeen   time.Time `json:"last_seen" gorm:"column:last_seen"`
    Event      int       `json:"event" gorm:"column:event"`
    CountAlarm int       `json:"count_alarm" gorm:"column:count_alarm"`
    IsOnline   bool      `json:"is_online" gorm:"column:is_online"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/device_status.py
from datetime import datetime

@dataclass
class DeviceStatus(BaseEntity):
    device_id: int
    status: str = "offline"
    last_value: float = 0.0
    last_seen: datetime | None = None
    event: int = 0
    count_alarm: int = 0
    is_online: bool = False
```

### 1.4 DeviceAlert (Go: `models/device_alert.go`)

```go
type DeviceAlert struct {
    gorm.Model
    DeviceID     int    `json:"device_id" gorm:"column:device_id"`
    AlarmStatus  int    `json:"alarm_status" gorm:"column:alarm_status"`
    AlarmType    int    `json:"alarm_type" gorm:"column:alarm_type"`
    ValueData    float64 `json:"value_data" gorm:"column:value_data"`
    ValueAlarm   float64 `json:"value_alarm" gorm:"column:value_alarm"`
    Title        string `json:"title" gorm:"column:title"`
    Subject      string `json:"subject" gorm:"column:subject"`
    Content      string `json:"content" gorm:"column:content"`
    DataAlarm    int    `json:"data_alarm" gorm:"column:data_alarm"`
    IsActive     bool   `json:"is_active" gorm:"column:is_active"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/device_alert.py
@dataclass
class DeviceAlert(BaseEntity):
    device_id: int
    alarm_status: int = 0
    alarm_type: int = 0
    value_data: float = 0.0
    value_alarm: float = 0.0
    title: str = ""
    subject: str = ""
    content: str = ""
    data_alarm: int = 0
    is_active: bool = True
```

### 1.5 IoTData (Go: `models/iot_data.go`)

```go
type IoTData struct {
    gorm.Model
    DeviceID    int       `json:"device_id" gorm:"column:device_id"`
    HardwareID  int       `json:"hardware_id" gorm:"column:hardware_id"`
    ValueData   float64   `json:"value_data" gorm:"column:value_data"`
    ValueAlarm  float64   `json:"value_alarm" gorm:"column:value_alarm"`
    ValueRelay  float64   `json:"value_relay" gorm:"column:value_relay"`
    Unit        string    `json:"unit" gorm:"column:unit"`
    MqttTopic   string    `json:"mqtt_topic" gorm:"column:mqtt_topic"`
    RecordedAt  time.Time `json:"recorded_at" gorm:"column:recorded_at"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/iot_data.py
from datetime import datetime

@dataclass
class IoTData(BaseEntity):
    device_id: int
    hardware_id: int
    value_data: float = 0.0
    value_alarm: float = 0.0
    value_relay: float = 0.0
    unit: str = ""
    mqtt_topic: str = ""
    recorded_at: datetime | None = None
```

### 1.6 AlarmLog (Go: `models/alarm_log.go`)

```go
type AlarmLog struct {
    gorm.Model
    DeviceID            int       `json:"device_id" gorm:"column:device_id"`
    AlarmStatus         int       `json:"alarm_status" gorm:"column:alarm_status"`
    AlarmType           int       `json:"alarm_type" gorm:"column:alarm_type"`
    ValueData           float64   `json:"value_data" gorm:"column:value_data"`
    ValueAlarm          float64   `json:"value_alarm" gorm:"column:value_alarm"`
    Title               string    `json:"title" gorm:"column:title"`
    Subject             string    `json:"subject" gorm:"column:subject"`
    Content             string    `json:"content" gorm:"column:content"`
    DataAlarm           int       `json:"data_alarm" gorm:"column:data_alarm"`
    DataAlarmRaw        int       `json:"data_alarm_raw" gorm:"column:data_alarm_raw"`
    EventControl        int       `json:"event_control" gorm:"column:event_control"`
    MessageMqttControl  string    `json:"message_mqtt_control" gorm:"column:message_mqtt_control"`
}
```

```python
# Python Domain Entity: app/modules/iot/domain/entities/alarm_log.py
@dataclass
class AlarmLog(BaseEntity):
    device_id: int
    alarm_status: int = 0
    alarm_type: int = 0
    value_data: float = 0.0
    value_alarm: float = 0.0
    title: str = ""
    subject: str = ""
    content: str = ""
    data_alarm: int = 0
    data_alarm_raw: int = 0
    event_control: int = 0
    message_mqtt_control: str = ""
```

---

## 2. Go Value Objects -> Python Value Objects

### 2.1 AlarmDetailDto (Go: `pkg/helpers/iot.go`)

```go
type AlarmDetailDto struct {
    HardwareID        interface{}
    ValueData         interface{}
    ValueAlarm        interface{}
    ValueRelay        interface{}
    ValueControlRelay interface{}
    Max               interface{}
    Min               interface{}
    StatusAlert       interface{}
    StatusWarning     interface{}
    RecoveryWarning   interface{}
    RecoveryAlert     interface{}
    DeviceName        string
    ActionName        string
    MqttName          string
    MqttControlOn     string
    MqttControlOff    string
    CountAlarm        interface{}
    Event             interface{}
    Unit              string
    SensorValueData   interface{}
}
```

```python
# Python Value Object: app/modules/iot/domain/value_objects/alarm.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class AlarmDetailDTO:
    hardware_id: Any
    value_data: Any
    value_alarm: Any
    value_relay: Any = None
    value_control_relay: Any = None
    max: Any = None
    min: Any = None
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
    max: Any
    min: Any
    event_control: int
    message_mqtt_control: str
    sensor_data: Any
    count_alarm: int
    mqtt_name: str
    device_name: str
    unit: str
    sensor_value: Any
    status_alert_val: int = 0
    status_warning_val: int = 0
    recovery_warning_val: int = 0
    recovery_alert_val: int = 0
```

### 2.2 MQTT Config (Go: `config/config.go`)

```go
type MQTTConfig struct {
    Broker   string
    ClientID string
    Username string
    Password string
}
```

```python
# Python Value Object: app/modules/iot/domain/value_objects/mqtt.py
from dataclasses import dataclass

@dataclass(frozen=True)
class MQTTConfig:
    broker: str
    client_id: str = ""
    username: str = ""
    password: str = ""
    keepalive: int = 30
    clean_session: bool = True
```

### 2.3 InfluxDB Config (Go: `config/config.go`)

```go
type InfluxDBConfig struct {
    URL     string
    Token   string
    Org     string
    Bucket  string
    Timeout int
}
```

```python
# Python Value Object: app/modules/iot/domain/value_objects/influxdb.py
from dataclasses import dataclass

@dataclass(frozen=True)
class InfluxDBConfig:
    url: str
    token: str
    org: str
    bucket: str
    timeout: int = 30
```

---

## 3. Go Interfaces -> Python Protocols

### 3.1 MQTT Client Interface

```go
// Go Interface
type Client interface {
    Connect(ctx context.Context) error
    Disconnect(quiesce uint)
    Publish(topic string, qos byte, retained bool, payload interface{}) error
    Subscribe(topic string, qos byte, callback mqtt.MessageHandler) error
    SubscribeMultiple(topics map[string]byte, callback mqtt.MessageHandler) error
    Unsubscribe(topics ...string) error
    IsConnected() bool
    RequestData(requestTopic string, responseTopic string, payload interface{}, timeout time.Duration) (interface{}, error)
    GetDataFromTopic(ctx context.Context, topic string, timeout time.Duration) ([]byte, error)
}
```

```python
# Python Protocol: app/core/mqtt_client.py
from typing import Protocol, Any
from collections.abc import Callable

class MQTTClientProtocol(Protocol):
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> None: ...
    def subscribe(self, topic: str, callback: Callable | None = None, qos: int = 0) -> None: ...
    def unsubscribe(self, topic: str) -> None: ...
    def is_connected(self) -> bool: ...
    def request_data(self, request_topic: str, response_topic: str, payload: Any, timeout: float = 30.0) -> Any: ...
    def get_data_from_topic(self, topic: str, timeout: float = 30.0) -> bytes: ...
```

### 3.2 InfluxDB Client Interface

```go
type Client interface {
    WritePoint(measurement string, tags map[string]string, fields map[string]interface{}, t time.Time) error
    Close()
}
```

```python
# Python Protocol: app/core/influxdb_client.py
from typing import Protocol
from datetime import datetime

class InfluxDBClientProtocol(Protocol):
    def write_point(self, measurement: str, tags: dict[str, str], fields: dict[str, Any], timestamp: datetime) -> None: ...
    def close(self) -> None: ...
    def query_filter_data(self, params: dict[str, Any]) -> list[dict[str, Any]]: ...
    def calculate_statistics(self, params: dict[str, Any]) -> dict[str, Any]: ...
```

---

## 4. Go Repository -> Python Repository

### 4.1 Device Repository Pattern

```go
// Go: internal/modules/iot/repository/device_repo.go
type DeviceRepo struct {
    db *gorm.DB
}

func NewDeviceRepo(db *gorm.DB) *DeviceRepo {
    return &DeviceRepo{db: db}
}

func (r *DeviceRepo) FindByID(id int) (*models.Device, error) {
    var device models.Device
    err := r.db.Preload("DeviceConfig").Preload("DeviceStatus").
        Where("id = ?", id).First(&device).Error
    return &device, err
}

func (r *DeviceRepo) FindByHardwareID(hardwareID int) (*models.Device, error) {
    var device models.Device
    err := r.db.Where("hardware_id = ?", hardwareID).First(&device).Error
    return &device, err
}

func (r *DeviceRepo) FindAll(page, pageSize int) ([]models.Device, int64, error) {
    var devices []models.Device
    var total int64
    r.db.Model(&models.Device{}).Count(&total)
    err := r.db.Offset((page - 1) * pageSize).Limit(pageSize).
        Preload("DeviceConfig").Preload("DeviceStatus").Find(&devices).Error
    return devices, total, err
}
```

```python
# Python: app/modules/iot/infrastructure/device_repository.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.iot.domain.entities.device import Device

class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, device_id: int) -> Device | None:
        result = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def find_by_hardware_id(self, hardware_id: int) -> Device | None:
        result = await self.session.execute(
            select(Device).where(Device.hardware_id == hardware_id)
        )
        return result.scalar_one_or_none()

    async def find_all(self, page: int = 1, page_size: int = 20) -> tuple[list[Device], int]:
        count_query = select(func.count()).select_from(Device)
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            select(Device)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        devices = list(result.scalars().all())
        return devices, total
```

---

## 5. Go UseCase -> Python UseCase

### 5.1 Interface Mapping

```go
// Go: internal/modules/iot/usecase/usecase.go
type MQTT3UseCase interface {
    IsConnected() bool
    IsCacheEnabled() bool
    GetTopicData(topic string) (interface{}, error)
    DeviceControl(deviceID int, command string) (interface{}, error)
    DeviceControls(deviceIDs []int, command string) (interface{}, error)
    GetDeviceList() (interface{}, error)
    GetDeviceListPage(page, pageSize int) (interface{}, int64, error)
    GetDeviceBuckets() (interface{}, error)
    GetDeviceListByLocation(locationID int) (interface{}, error)
    GetSenserCharts(deviceID int, startTime, endTime string, limit int) (interface{}, error)
    GetSenserDataChart(deviceID int, field, startTime, endTime string, limit int) (interface{}, error)
    GetSenserData(deviceID int, field string, limit int) (interface{}, error)
    GetDeviceSenserCharts(deviceID int, limit int) (interface{}, error)
    GetAlarmDeviceStatus() (interface{}, error)
    GetAlarmDeviceStatusControl() (interface{}, error)
    GetMonitorDeviceGroup(locationID int) (interface{}, error)
    GetMonitorDeviceChart(locationID int, field, startTime, endTime string) (interface{}, error)
    GetTopicDataDeviceChart(topic string, field, startTime, endTime string) (interface{}, error)
    GetDeviceStatus(deviceID int) (interface{}, error)
    UpdateDeviceStatus(deviceID int, status string) (interface{}, error)
    GetDeviceConfig(deviceID int) (interface{}, error)
    UpdateDeviceConfig(deviceID int, config interface{}) (interface{}, error)
    ProcessMqttData(topic string, payload []byte) (interface{}, error)
    GetLatestData(deviceID int, limit int) (interface{}, error)
    GetDataByDateRange(deviceID int, start, end string) (interface{}, error)
    ListIotData(page, pageSize int) (interface{}, int64, error)
    GetDeviceStats(deviceID int) (interface{}, error)
    ExportData(deviceIDs []int, start, end, format string) (interface{}, error)
    CleanupOldData(days int) (interface{}, error)
}
```

```python
# Python: app/modules/iot/application/use_case.py
from typing import Any

class IoTUseCase:
    def __init__(
        self,
        device_repository: DeviceRepository,
        device_config_repository: DeviceConfigRepository,
        device_status_repository: DeviceStatusRepository,
        device_alert_repository: DeviceAlertRepository,
        iot_data_repository: IoTDataRepository,
        alarm_log_repository: AlarmLogRepository,
        activity_log_repository: ActivityLogRepository,
        mqtt_client: MQTTClientProtocol,
        influxdb_client: InfluxDBClientProtocol,
        redis_client: Redis,
        logger: Logger,
    ):
        # ... inject dependencies

    async def get_topic_data(self, topic: str) -> dict[str, Any]:
        # Redis cache check first
        cached = await self.redis_client.get(f"mqtt:topic:{topic}")
        if cached:
            return json.loads(cached)

        # MQTT request
        result = await self.mqtt_client.request_data(topic, topic, "", timeout=5.0)

        # Cache result
        await self.redis_client.setex(f"mqtt:topic:{topic}", 5, json.dumps(result))
        return result

    async def get_alarm_device_status(self) -> list[dict[str, Any]]:
        # Complex alarm evaluation logic
        devices = await self.device_repository.find_all_active()
        alarm_results = []

        for device in devices:
            # Get device config
            config = await self.device_config_repository.find_by_device_id(device.id)

            # Get MQTT data
            mqtt_data = await self.get_topic_data(device.mqtt_topic)

            # Evaluate alarm
            alarm_result = evaluate_alarm(
                AlarmDetailDTO(
                    hardware_id=device.hardware_id,
                    value_data=mqtt_data.get("value"),
                    value_alarm=mqtt_data.get("alarm"),
                    max=config.max_value if config else 0,
                    min=config.min_value if config else 0,
                    # ... more fields
                )
            )
            alarm_results.append(alarm_result)

        return alarm_results
```

---

## 6. Go Handler -> Python Router

### 6.1 HTTP Handler Mapping

```go
// Go: internal/modules/iot/delivery/http/handler.go
func (h *MQTT3Handler) GetTopicData(c *gin.Context) {
    topic := c.Query("topic")
    result, err := h.usecase.GetTopicData(topic)
    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, result)
}
```

```python
# Python: app/modules/iot/presentation/router.py
from fastapi import APIRouter, Depends, Query
from app.modules.iot.application.use_case import IoTUseCase
from app.modules.shared.dependencies import get_current_user

router = APIRouter()

@router.get("/topic-data")
async def get_topic_data(
    topic: str = Query(..., description="MQTT topic"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    result = await use_case.get_topic_data(topic)
    return result
```

---

## 7. Error Handling Mapping

### 7.1 Go Error -> Python Exception

```go
// Go: pkg/httpErrors
restErr := httpErrors.ErrNotFound(errors.New("device not found"))
// Returns: {"status": 404, "statusText": "not_found", "msg": "device not found"}
```

```python
# Python: app/modules/shared/exceptions.py
from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)

class InternalServerException(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)

# Usage
raise NotFoundException(detail="device not found")
raise BadRequestException(detail="invalid MQTT topic")
```

---

## 8. Configuration Mapping

### 8.1 Go Config -> Python Settings

```go
// Go: config/config.go
type Config struct {
    Postgres PostgresConfig
    Redis    RedisConfig
    MQTT     MQTTConfig
    InfluxDB InfluxDBConfig
}

type PostgresConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    DBName   string
}
```

```python
# Python: app/core/config.py
from pydantic_settings import BaseSettings

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
    MQTT_CLIENT_ID: str = "fastapi-iot-client"
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

## 9. Summary Table

| Go Component | Python Component | File Path |
|-------------|------------------|-----------|
| `models/device.go` | `Device` entity | `app/modules/iot/domain/entities/device.py` |
| `models/device_config.go` | `DeviceConfig` entity | `app/modules/iot/domain/entities/device_config.py` |
| `models/device_status.go` | `DeviceStatus` entity | `app/modules/iot/domain/entities/device_status.py` |
| `models/device_alert.go` | `DeviceAlert` entity | `app/modules/iot/domain/entities/device_alert.py` |
| `models/iot_data.go` | `IoTData` entity | `app/modules/iot/domain/entities/iot_data.py` |
| `models/alarm_log.go` | `AlarmLog` entity | `app/modules/iot/domain/entities/alarm_log.py` |
| `models/activity_log.go` | `ActivityLog` entity | `app/modules/iot/domain/entities/activity_log.py` |
| `models/schedule.go` | `Schedule` entity | `app/modules/iot/domain/entities/schedule.py` |
| `pkg/helpers/iot.go` | `AlarmDetailDTO` | `app/modules/iot/domain/value_objects/alarm.py` |
| `pkg/influxdb/client.go` | `InfluxDBClient` | `app/core/influxdb_client.py` |
| `pkg/mqtt/client.go` | `MQTTClient` | `app/core/mqtt_client.py` |
| `repository/device_repo.go` | `DeviceRepository` | `app/modules/iot/infrastructure/device_repository.py` |
| `usecase/usecase.go` | `IoTUseCase` | `app/modules/iot/application/use_case.py` |
| `delivery/http/handler.go` | `router.py` | `app/modules/iot/presentation/router.py` |
| `presenter/presenter.go` | `schemas.py` | `app/modules/iot/presentation/schemas.py` |
| `pkg/httpErrors/httpErrors.go` | `exceptions.py` | `app/modules/shared/exceptions.py` |
| `config/config.go` | `Settings` | `app/core/config.py` |
