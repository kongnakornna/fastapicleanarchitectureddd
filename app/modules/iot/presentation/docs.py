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

# Route names / paths that appear under /iot (matches Go routes.go)
IOT_ROUTE_PATHS = [
    "/iot/topic",
    "/iot/topicdevicechart",
    "/iot/controls",
    "/iot/control",
    "/iot/monitordevicegroup",
    "/iot/monitordevicechart",
    "/iot/device",
    "/iot/devicebuckets",
    "/iot/sensercharts",
    "/iot/devicesensercharts",
    "/iot/locationdevice",
    "/iot/alarmdevicestatus",
    "/iot/alarmdevicestatuscontrol",
    "/iot/devicemqtt",
    "/iot/devicestatus",
    "/iot/deviceconfig",
    "/iot/updatedeviceconfig",
    "/iot/deviceiotdata",
    "/iot/devicestats",
    "/iot/devicedataexport",
    "/iot/devicedatacleanup",
]

IOT_TAG = {
    "name": "iot",
    "description": (
        "โมดูล iot — Real-time Sensor & Alarm Monitoring\n\n"
        "• MQTT Ingest\n"
        "• Alarm Evaluation (hardware_id 1-4)\n"
        "• Device Control\n"
        "• Time-series (InfluxDB)\n"
        "• WebSocket Real-time"
    ),
    "externalDocs": {
        "description": "iot Module README",
        "url": "/docs/README_iot.md",
    },
}