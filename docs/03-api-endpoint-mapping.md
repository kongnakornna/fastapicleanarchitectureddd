# API Endpoint Mapping
## Go Chi Router -> FastAPI Router

---

## 1. Router Registration

### Go (Chi)

```go
// internal/modules/iot/delivery/http/routes.go
func Routes(r *chi.Mux, h *MQTT3Handler) {
    r.Route("/mqtt3", func(r chi.Router) {
        r.Get("/topic-data", h.GetTopicData)
        r.Post("/device-control", h.DeviceControl)
        r.Post("/device-controls", h.DeviceControls)
        r.Get("/device-list", h.GetDeviceList)
        r.Get("/device-list-page", h.GetDeviceListPage)
        r.Get("/device-buckets", h.GetDeviceBuckets)
        r.Get("/device-list-by-location", h.GetDeviceListByLocation)
        r.Get("/senser-charts", h.GetSenserCharts)
        r.Get("/senser-data", h.GetSenserData)
        r.Get("/senser-data-chart", h.GetSenserDataChart)
        r.Get("/device-senser-charts", h.GetDeviceSenserCharts)
        r.Get("/alarm-device-status", h.GetAlarmDeviceStatus)
        r.Get("/alarm-device-status-control", h.GetAlarmDeviceStatusControl)
        r.Get("/monitor-device-group", h.GetMonitorDeviceGroup)
        r.Get("/monitor-device-chart", h.GetMonitorDeviceChart)
        r.Get("/topic-data-device-chart", h.GetTopicDataDeviceChart)
        r.Get("/device-status/{id}", h.GetDeviceStatus)
        r.Patch("/device-status/{id}", h.UpdateDeviceStatus)
        r.Get("/device-config/{id}", h.GetDeviceConfig)
        r.Patch("/device-config/{id}", h.UpdateDeviceConfig)
        r.Post("/process-mqtt-data", h.ProcessMqttData)
        r.Get("/latest-data", h.GetLatestData)
        r.Get("/data-by-range", h.GetDataByDateRange)
        r.Get("/list-iot-data", h.ListIotData)
        r.Get("/device-stats", h.GetDeviceStats)
        r.Post("/export-data", h.ExportData)
        r.Delete("/cleanup-old", h.CleanupOldData)
    })
}
```

### Python (FastAPI)

```python
# app/modules/iot/presentation/router.py
from fastapi import APIRouter, Depends, Query, Path
from app.modules.iot.application.use_case import IoTUseCase
from app.modules.shared.dependencies import get_current_user
from app.modules.iot.presentation import schemas as iot_schemas

router = APIRouter(prefix="/mqtt3", tags=["IoT"])

# Dependency injection
def get_iot_use_case() -> IoTUseCase:
    # Wire up dependencies here
    ...

@router.get("/topic-data")
async def get_topic_data(
    topic: str = Query(..., description="MQTT topic to read"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get data from MQTT topic with Redis caching"""
    return await use_case.get_topic_data(topic)

@router.post("/device-control")
async def device_control(
    request: iot_schemas.DeviceControlRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Send control command to a single device"""
    return await use_case.device_control(request.device_id, request.command)

@router.post("/device-controls")
async def device_controls(
    request: iot_schemas.DeviceControlsRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Send control command to multiple devices"""
    return await use_case.device_controls(request.device_ids, request.command)

@router.get("/device-list")
async def get_device_list(
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get list of all devices"""
    return await use_case.get_device_list()

@router.get("/device-list-page")
async def get_device_list_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get paginated list of devices"""
    return await use_case.get_device_list_page(page, page_size)

@router.get("/device-buckets")
async def get_device_buckets(
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get InfluxDB buckets for devices"""
    return await use_case.get_device_buckets()

@router.get("/device-list-by-location")
async def get_device_list_by_location(
    location_id: int = Query(..., description="Location ID"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get devices filtered by location"""
    return await use_case.get_device_list_by_location(location_id)

@router.get("/senser-charts")
async def get_senser_charts(
    device_id: int = Query(..., description="Device ID"),
    start_time: str = Query("-1h", description="Start time range"),
    end_time: str = Query("now()", description="End time range"),
    limit: int = Query(100, ge=1),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get sensor chart data from InfluxDB"""
    return await use_case.get_senser_charts(device_id, start_time, end_time, limit)

@router.get("/senser-data")
async def get_senser_data(
    device_id: int = Query(...),
    field: str = Query("_value"),
    limit: int = Query(100, ge=1),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get raw sensor data"""
    return await use_case.get_senser_data(device_id, field, limit)

@router.get("/senser-data-chart")
async def get_senser_data_chart(
    device_id: int = Query(...),
    field: str = Query("_value"),
    start_time: str = Query("-1h"),
    end_time: str = Query("now()"),
    limit: int = Query(100, ge=1),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get sensor data chart with time range"""
    return await use_case.get_senser_data_chart(device_id, field, start_time, end_time, limit)

@router.get("/device-senser-charts")
async def get_device_senser_charts(
    device_id: int = Query(...),
    limit: int = Query(100, ge=1),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get device sensor charts"""
    return await use_case.get_device_senser_charts(device_id, limit)

@router.get("/alarm-device-status")
async def get_alarm_device_status(
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get alarm status for all devices"""
    return await use_case.get_alarm_device_status()

@router.get("/alarm-device-status-control")
async def get_alarm_device_status_control(
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get alarm status with control info"""
    return await use_case.get_alarm_device_status_control()

@router.get("/monitor-device-group")
async def get_monitor_device_group(
    location_id: int = Query(...),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get monitor data grouped by device"""
    return await use_case.get_monitor_device_group(location_id)

@router.get("/monitor-device-chart")
async def get_monitor_device_chart(
    location_id: int = Query(...),
    field: str = Query("_value"),
    start_time: str = Query("-1h"),
    end_time: str = Query("now()"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get monitor chart data"""
    return await use_case.get_monitor_device_chart(location_id, field, start_time, end_time)

@router.get("/topic-data-device-chart")
async def get_topic_data_device_chart(
    topic: str = Query(...),
    field: str = Query("_value"),
    start_time: str = Query("-1h"),
    end_time: str = Query("now()"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get topic data for device chart"""
    return await use_case.get_topic_data_device_chart(topic, field, start_time, end_time)

@router.get("/device-status/{device_id}")
async def get_device_status(
    device_id: int = Path(..., description="Device ID"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get device status by ID"""
    return await use_case.get_device_status(device_id)

@router.patch("/device-status/{device_id}")
async def update_device_status(
    device_id: int = Path(...),
    request: iot_schemas.UpdateDeviceStatusRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Update device status"""
    return await use_case.update_device_status(device_id, request.status)

@router.get("/device-config/{device_id}")
async def get_device_config(
    device_id: int = Path(...),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get device configuration"""
    return await use_case.get_device_config(device_id)

@router.patch("/device-config/{device_id}")
async def update_device_config(
    device_id: int = Path(...),
    request: iot_schemas.UpdateDeviceConfigRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Update device configuration"""
    return await use_case.update_device_config(device_id, request.model_dump())

@router.post("/process-mqtt-data")
async def process_mqtt_data(
    request: iot_schemas.ProcessMqttDataRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Process incoming MQTT data"""
    return await use_case.process_mqtt_data(request.topic, request.payload.encode())

@router.get("/latest-data")
async def get_latest_data(
    device_id: int = Query(...),
    limit: int = Query(10, ge=1),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get latest IoT data"""
    return await use_case.get_latest_data(device_id, limit)

@router.get("/data-by-range")
async def get_data_by_date_range(
    device_id: int = Query(...),
    start: str = Query(..., description="ISO datetime"),
    end: str = Query(..., description="ISO datetime"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get IoT data by date range"""
    return await use_case.get_data_by_date_range(device_id, start, end)

@router.get("/list-iot-data")
async def list_iot_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """List IoT data with pagination"""
    return await use_case.list_iot_data(page, page_size)

@router.get("/device-stats")
async def get_device_stats(
    device_id: int = Query(...),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Get device statistics"""
    return await use_case.get_device_stats(device_id)

@router.post("/export-data")
async def export_data(
    request: iot_schemas.ExportDataRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Export IoT data in various formats"""
    return await use_case.export_data(
        request.device_ids, request.start, request.end, request.format
    )

@router.delete("/cleanup-old")
async def cleanup_old_data(
    days: int = Query(90, ge=1, description="Delete data older than N days"),
    use_case: IoTUseCase = Depends(get_iot_use_case),
    current_user = Depends(get_current_user),
):
    """Cleanup old IoT data"""
    return await use_case.cleanup_old_data(days)
```

---

## 2. Request/Response Schemas

```python
# app/modules/iot/presentation/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

# Request Schemas
class DeviceControlRequest(BaseModel):
    device_id: int
    command: str

class DeviceControlsRequest(BaseModel):
    device_ids: list[int]
    command: str

class UpdateDeviceStatusRequest(BaseModel):
    status: str

class UpdateDeviceConfigRequest(BaseModel):
    max_value: float | None = None
    min_value: float | None = None
    warning_threshold: float | None = None
    alert_threshold: float | None = None
    recovery_warning: float | None = None
    recovery_alert: float | None = None
    calibration_offset: float | None = None
    calibration_multiplier: float | None = None
    mqtt_control_on: str | None = None
    mqtt_control_off: str | None = None
    action_name: str | None = None

class ProcessMqttDataRequest(BaseModel):
    topic: str
    payload: str

class ExportDataRequest(BaseModel):
    device_ids: list[int]
    start: str
    end: str
    format: str = "json"  # json, csv

# Response Schemas
class DeviceResponse(BaseModel):
    id: int
    hardware_id: int
    device_name: str
    device_type: str
    mqtt_topic: str
    mqtt_name: str
    unit: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class DeviceListResponse(BaseModel):
    devices: list[DeviceResponse]
    total: int
    page: int
    page_size: int

class AlarmStatusResponse(BaseModel):
    device_id: int
    device_name: str
    alarm_status: int
    title: str
    subject: str
    content: str
    value_data: Any
    status: int
    timestamp: str

class IoTDataResponse(BaseModel):
    id: int
    device_id: int
    hardware_id: int
    value_data: float
    value_alarm: float
    unit: str
    recorded_at: datetime

class IoTDataListResponse(BaseModel):
    data: list[IoTDataResponse]
    total: int
    page: int
    page_size: int

class DeviceStatsResponse(BaseModel):
    device_id: int
    total_readings: int
    avg_value: float
    min_value: float
    max_value: float
    alarm_count: int
    last_seen: datetime | None

class InfluxDBQueryResponse(BaseModel):
    time: str
    measurement: str
    field: str
    value: Any

class StatisticsResponse(BaseModel):
    type: str
    value: Any
    time: str | None = None
    data_points: int | None = None
```

---

## 3. Dependency Wiring

```python
# app/modules/shared/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.redis import get_redis_client
from app.core.influxdb_client import get_influxdb_client
from app.core.mqtt_client import get_mqtt_client

from app.modules.iot.infrastructure.device_repository import DeviceRepository
from app.modules.iot.infrastructure.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.iot_data_repository import IoTDataRepository
from app.modules.iot.infrastructure.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.activity_log_repository import ActivityLogRepository
from app.modules.iot.application.use_case import IoTUseCase


async def get_iot_use_case(
    session: AsyncSession = Depends(get_async_session),
    redis = Depends(get_redis_client),
    influxdb = Depends(get_influxdb_client),
    mqtt = Depends(get_mqtt_client),
) -> IoTUseCase:
    return IoTUseCase(
        device_repository=DeviceRepository(session),
        device_config_repository=DeviceConfigRepository(session),
        device_status_repository=DeviceStatusRepository(session),
        device_alert_repository=DeviceAlertRepository(session),
        iot_data_repository=IoTDataRepository(session),
        alarm_log_repository=AlarmLogRepository(session),
        activity_log_repository=ActivityLogRepository(session),
        mqtt_client=mqtt,
        influxdb_client=influxdb,
        redis_client=redis,
    )
```

---

## 4. App Registration

```python
# app/app.py
from fastapi import FastAPI
from app.modules.iot.presentation.router import router as iot_router

def create_app() -> FastAPI:
    app = FastAPI(title="IoT Monitoring API")

    # Register IoT routes
    app.include_router(iot_router, prefix="/api/v1", tags=["IoT"])

    return app
```

---

## 5. Endpoint Summary

| # | Method | Go Path | Python Path | Auth | Description |
|---|--------|---------|-------------|------|-------------|
| 1 | GET | /mqtt3/topic-data | /api/v1/mqtt3/topic-data | Yes | Get MQTT topic data |
| 2 | POST | /mqtt3/device-control | /api/v1/mqtt3/device-control | Yes | Control single device |
| 3 | POST | /mqtt3/device-controls | /api/v1/mqtt3/device-controls | Yes | Control multiple devices |
| 4 | GET | /mqtt3/device-list | /api/v1/mqtt3/device-list | Yes | List all devices |
| 5 | GET | /mqtt3/device-list-page | /api/v1/mqtt3/device-list-page | Yes | Paginated device list |
| 6 | GET | /mqtt3/device-buckets | /api/v1/mqtt3/device-buckets | Yes | Get InfluxDB buckets |
| 7 | GET | /mqtt3/device-list-by-location | /api/v1/mqtt3/device-list-by-location | Yes | Devices by location |
| 8 | GET | /mqtt3/senser-charts | /api/v1/mqtt3/senser-charts | Yes | Sensor chart data |
| 9 | GET | /mqtt3/senser-data | /api/v1/mqtt3/senser-data | Yes | Raw sensor data |
| 10 | GET | /mqtt3/senser-data-chart | /api/v1/mqtt3/senser-data-chart | Yes | Sensor data chart |
| 11 | GET | /mqtt3/device-senser-charts | /api/v1/mqtt3/device-senser-charts | Yes | Device sensor charts |
| 12 | GET | /mqtt3/alarm-device-status | /api/v1/mqtt3/alarm-device-status | Yes | Alarm status |
| 13 | GET | /mqtt3/alarm-device-status-control | /api/v1/mqtt3/alarm-device-status-control | Yes | Alarm with control |
| 14 | GET | /mqtt3/monitor-device-group | /api/v1/mqtt3/monitor-device-group | Yes | Monitor grouped |
| 15 | GET | /mqtt3/monitor-device-chart | /api/v1/mqtt3/monitor-device-chart | Yes | Monitor chart |
| 16 | GET | /mqtt3/topic-data-device-chart | /api/v1/mqtt3/topic-data-device-chart | Yes | Topic data chart |
| 17 | GET | /mqtt3/device-status/{id} | /api/v1/mqtt3/device-status/{id} | Yes | Get device status |
| 18 | PATCH | /mqtt3/device-status/{id} | /api/v1/mqtt3/device-status/{id} | Yes | Update device status |
| 19 | GET | /mqtt3/device-config/{id} | /api/v1/mqtt3/device-config/{id} | Yes | Get device config |
| 20 | PATCH | /mqtt3/device-config/{id} | /api/v1/mqtt3/device-config/{id} | Yes | Update device config |
| 21 | POST | /mqtt3/process-mqtt-data | /api/v1/mqtt3/process-mqtt-data | Yes | Process MQTT data |
| 22 | GET | /mqtt3/latest-data | /api/v1/mqtt3/latest-data | Yes | Latest IoT data |
| 23 | GET | /mqtt3/data-by-range | /api/v1/mqtt3/data-by-range | Yes | Data by date range |
| 24 | GET | /mqtt3/list-iot-data | /api/v1/mqtt3/list-iot-data | Yes | List IoT data |
| 25 | GET | /mqtt3/device-stats | /api/v1/mqtt3/device-stats | Yes | Device statistics |
| 26 | POST | /mqtt3/export-data | /api/v1/mqtt3/export-data | Yes | Export data |
| 27 | DELETE | /mqtt3/cleanup-old | /api/v1/mqtt3/cleanup-old | Yes | Cleanup old data |
