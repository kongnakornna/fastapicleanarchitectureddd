from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Request schemas
# =============================================================================

class ControlRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="MQTT topic to publish to")
    message: str = Field(..., min_length=1, description="MQTT message payload")

    model_config = ConfigDict(extra="forbid")


class DeviceListRequest(BaseModel):
    bucket: str = Field(default="", description="Filter by bucket name")
    hardware_id: int = Field(default=0, description="Filter by hardware type ID")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    model_config = ConfigDict(extra="forbid")


class SenserChartRequest(BaseModel):
    measurement: str = Field(default="temperature", description="InfluxDB measurement")
    field: str = Field(default="value", description="InfluxDB field name")
    bucket: str = Field(default="iot_sensors", description="InfluxDB bucket")
    start: str = Field(default="-1h", description="Start time range")
    stop: str = Field(default="now()", description="Stop time range")
    limit: int = Field(default=1000, ge=1, le=10000, description="Max data points")

    model_config = ConfigDict(extra="forbid")


class AlarmDeviceStatusRequest(BaseModel):
    bucket: str = Field(default="iot_sensors", description="InfluxDB bucket")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=1000, ge=1, le=5000)
    measurement: str = Field(default="temperature")
    device_id: str = Field(default="", description="Filter by device ID")
    type_id: int = Field(default=0, description="Filter by type ID")
    hardware_id: int = Field(default=0, description="Filter by hardware ID")
    keyword: str = Field(default="", description="Search keyword")

    model_config = ConfigDict(extra="forbid")


class MonitorDeviceGroupRequest(BaseModel):
    bucket: str = Field(default="iot_sensors", description="InfluxDB bucket")
    location_id: int = Field(default=0, description="Filter by location")
    hardware_id: int = Field(default=0, description="Filter by hardware type")
    lang: str = Field(default="en", pattern="^(en|th)$", description="Language: en or th")
    del_cache: int = Field(default=0, ge=0, le=1, description="Delete cache before query")

    model_config = ConfigDict(extra="forbid")


class MonitorDeviceChartRequest(BaseModel):
    bucket: str = Field(default="iot_sensors", description="InfluxDB bucket")
    measurement: str = Field(default="temperature")
    field: str = Field(default="value")
    start: str = Field(default="-10m")
    stop: str = Field(default="now()")
    limit: int = Field(default=100, ge=1, le=10000)

    model_config = ConfigDict(extra="forbid")


class TopicDataDeviceChartRequest(BaseModel):
    bucket: str = Field(default="iot_sensors")
    topic: str = Field(default="", description="MQTT topic (default: {bucket}/DATA)")
    measurement: str = Field(default="temperature")
    field: str = Field(default="value")
    start: str = Field(default="-10m")
    stop: str = Field(default="now()")
    limit: int = Field(default=100, ge=1, le=10000)

    model_config = ConfigDict(extra="forbid")


class UpdateDeviceStatusRequest(BaseModel):
    battery: float | None = Field(default=None, ge=0, le=100)
    signal: float | None = Field(default=None, ge=0)
    firmware: str | None = None
    location: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class UpdateDeviceConfigRequest(BaseModel):
    config: dict[str, Any] = Field(..., description="Configuration to merge")

    model_config = ConfigDict(extra="forbid")


class ProcessMqttDataRequest(BaseModel):
    device_id: str = Field(..., min_length=1)
    raw_data: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class ExportDataRequest(BaseModel):
    device_id: str = Field(default="")
    start_date: str = Field(default="", description="ISO date string")
    end_date: str = Field(default="", description="ISO date string")
    format: str = Field(default="json", pattern="^(json|csv)$")

    model_config = ConfigDict(extra="forbid")


class BatchProcessItem(BaseModel):
    device_id: str = Field(..., min_length=1)
    raw_data: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class BatchProcessRequest(BaseModel):
    items: list[BatchProcessItem] = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(extra="forbid")


# =============================================================================
# Response schemas
# =============================================================================

class TopicDataResponse(BaseModel):
    topic: str
    payload: Any = None
    from_source: str = Field(alias="from")
    cache: bool

    model_config = ConfigDict(extra="forbid")


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


class ExportDataResponse(BaseModel):
    format: str
    content_type: str
    filename: str
    data: str

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
