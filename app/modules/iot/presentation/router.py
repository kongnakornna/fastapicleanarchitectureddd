from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect

from app.core.websocket_hub import ws_manager
from app.modules.iot.application.use_case import IoTUseCase
from app.modules.iot.presentation.dependencies import get_iot_use_case
from app.modules.iot.presentation.schemas import (
    AlarmDeviceStatusRequest,
    AlarmDeviceStatusResponse,
    BatchProcessRequest,
    CleanupResponse,
    ControlRequest,
    DeviceBucketsResponse,
    DeviceConfigResponse,
    DeviceDetailResponse,
    DeviceListResponse,
    DeviceStatsResponse,
    DeviceStatusResponse,
    ExportDataRequest,
    MonitorDeviceGroupRequest,
    MonitorDeviceGroupResponse,
    PaginatedDataResponse,
    ProcessMqttDataRequest,
    SenserChartResponse,
    TopicDataResponse,
    UpdateDeviceConfigRequest,
    UpdateDeviceStatusRequest,
)

router = APIRouter(prefix="/iot", tags=["IoT"])


@router.get("/status")
async def get_connection_status(
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return {
        "mqtt_connected": use_case.is_connected(),
        "cache_enabled": use_case.is_cache_enabled(),
    }


@router.post("/topic-data")
async def get_topic_data(
    topic: str,
    del_cache: bool = False,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> TopicDataResponse:
    result = await use_case.get_topic_data(topic, del_cache)
    return TopicDataResponse(**result)


@router.post("/control")
async def device_control(
    payload: ControlRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, bool]:
    success = await use_case.device_control(payload.topic, payload.message)
    return {"success": success}


@router.post("/controls")
async def device_controls(
    payload: ControlRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, bool]:
    success = await use_case.device_controls(payload.topic, payload.message)
    return {"success": success}


@router.get("/devices")
async def get_device_list(
    bucket: str = "",
    hardware_id: int = 0,
    page: int = 1,
    page_size: int = 20,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceListResponse:
    devices, total = await use_case.get_device_list(bucket, hardware_id, page, page_size)
    return DeviceListResponse(
        devices=[
            DeviceDetailResponse(
                device_id=str(d.id),
                device_name=d.device_name,
                hardware_id=d.hardware_id,
                unit=d.unit,
                status=d.status,
            )
            for d in devices
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/devices/page")
async def get_device_list_page(
    bucket: str = "",
    hardware_id: int = 0,
    page: int = 1,
    page_size: int = 20,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceListResponse:
    devices, total = await use_case.get_device_list_page(bucket, hardware_id, page, page_size)
    return DeviceListResponse(
        devices=[
            DeviceDetailResponse(
                device_id=str(d.id),
                device_name=d.device_name,
                hardware_id=d.hardware_id,
                unit=d.unit,
                status=d.status,
            )
            for d in devices
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/devices/buckets/{bucket}")
async def get_device_buckets(
    bucket: str,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceBucketsResponse:
    devices, _ = await use_case.get_device_list(bucket=bucket)
    return DeviceBucketsResponse(
        bucket=bucket,
        devices=[
            DeviceDetailResponse(
                device_id=str(d.id),
                device_name=d.device_name,
                hardware_id=d.hardware_id,
                unit=d.unit,
            )
            for d in devices
        ],
    )


@router.get("/devices/location/{location_id}")
async def get_device_list_by_location(
    location_id: int,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> list[DeviceDetailResponse]:
    devices = await use_case.get_device_list_by_location(location_id)
    return [
        DeviceDetailResponse(
            device_id=str(d.id),
            device_name=d.device_name,
            hardware_id=d.hardware_id,
            unit=d.unit,
        )
        for d in devices
    ]


@router.get("/senser-charts")
async def get_senser_charts(
    measurement: str = "temperature",
    field: str = "value",
    bucket: str = "iot_sensors",
    start: str = "-1h",
    stop: str = "now()",
    limit: int = 1000,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> SenserChartResponse:
    result = await use_case.get_senser_charts(measurement, field, bucket, start, stop, limit)
    return SenserChartResponse(**result)


@router.get("/senser-data-chart")
async def get_senser_data_chart(
    measurement: str = "temperature",
    field: str = "value",
    bucket: str = "iot_sensors",
    start: str = "-1h",
    stop: str = "now()",
    limit: int = 1000,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> SenserChartResponse:
    result = await use_case.get_senser_data_chart(
        measurement=measurement, field=field, bucket=bucket, start=start, stop=stop, limit=limit
    )
    return SenserChartResponse(**result)


@router.get("/senser-data")
async def get_senser_data(
    measurement: str = "temperature",
    field: str = "value",
    bucket: str = "iot_sensors",
    start: str = "-1h",
    stop: str = "now()",
    limit: int = 1000,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> SenserChartResponse:
    result = await use_case.get_senser_data(
        measurement=measurement, field=field, bucket=bucket, start=start, stop=stop, limit=limit
    )
    return SenserChartResponse(**result)


@router.get("/device-senser-charts")
async def get_device_senser_charts(
    measurement: str = "temperature",
    field: str = "value",
    bucket: str = "iot_sensors",
    start: str = "-1h",
    stop: str = "now()",
    limit: int = 1000,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> SenserChartResponse:
    result = await use_case.get_device_senser_charts(
        measurement=measurement, field=field, bucket=bucket, start=start, stop=stop, limit=limit
    )
    return SenserChartResponse(**result)


@router.post("/alarm-device-status")
async def get_alarm_device_status(
    payload: AlarmDeviceStatusRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> AlarmDeviceStatusResponse:
    result = await use_case.get_alarm_device_status(
        bucket=payload.bucket,
        page=payload.page,
        page_size=payload.page_size,
        measurement=payload.measurement,
    )
    return AlarmDeviceStatusResponse(**result)


@router.post("/alarm-device-status-control")
async def get_alarm_device_status_control(
    payload: AlarmDeviceStatusRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> AlarmDeviceStatusResponse:
    result = await use_case.get_alarm_device_status_control(
        bucket=payload.bucket,
        page=payload.page,
        page_size=payload.page_size,
        measurement=payload.measurement,
    )
    return AlarmDeviceStatusResponse(**result)


@router.post("/monitor-device-group")
async def get_monitor_device_group(
    payload: MonitorDeviceGroupRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> MonitorDeviceGroupResponse:
    result = await use_case.get_monitor_device_group(
        bucket=payload.bucket,
        location_id=payload.location_id,
        hardware_id=payload.hardware_id,
        lang=payload.lang,
        del_cache=payload.del_cache,
    )
    return MonitorDeviceGroupResponse(**result)


@router.get("/monitor-device-chart")
async def get_monitor_device_chart(
    bucket: str = "iot_sensors",
    measurement: str = "temperature",
    field: str = "value",
    start: str = "-10m",
    stop: str = "now()",
    limit: int = 100,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await use_case.get_monitor_device_chart(bucket, measurement, field, start, stop, limit)


@router.get("/topic-data-device-chart")
async def get_topic_data_device_chart(
    bucket: str = "iot_sensors",
    topic: str = "",
    measurement: str = "temperature",
    field: str = "value",
    start: str = "-10m",
    stop: str = "now()",
    limit: int = 100,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await use_case.get_topic_data_device_chart(
        bucket, topic, measurement, field, start, stop, limit
    )


@router.get("/devices/{device_id}/status")
async def get_device_status(
    device_id: str,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceStatusResponse:
    result = await use_case.get_device_status(device_id)
    return DeviceStatusResponse(**result)


@router.put("/devices/{device_id}/status")
async def update_device_status(
    device_id: str,
    payload: UpdateDeviceStatusRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, bool]:
    data = payload.model_dump(exclude_none=True)
    success = await use_case.update_device_status(device_id, data)
    return {"success": success}


@router.get("/devices/{device_id}/config")
async def get_device_config(
    device_id: str,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceConfigResponse:
    result = await use_case.get_device_config(device_id)
    return DeviceConfigResponse(**result)


@router.put("/devices/{device_id}/config")
async def update_device_config(
    device_id: str,
    payload: UpdateDeviceConfigRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, bool]:
    success = await use_case.update_device_config(device_id, payload.config)
    return {"success": success}


@router.post("/process-mqtt-data")
async def process_mqtt_data(
    payload: ProcessMqttDataRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    return await use_case.process_mqtt_data(payload.device_id, payload.raw_data)


@router.get("/data/latest")
async def get_latest_data(
    device_id: str = "",
    limit: int = 10,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> list[dict[str, Any]]:
    data = await use_case.get_latest_data(device_id, limit)
    return [
        {
            "id": str(d.id),
            "device_id": d.device_id,
            "data": d.data_json,
            "timestamp": d.created_at.isoformat() if d.created_at else "",
        }
        for d in data
    ]


@router.get("/data/date-range")
async def get_data_by_date_range(
    device_id: str = "",
    start: str = "",
    end: str = "",
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> list[dict[str, Any]]:
    data = await use_case.get_data_by_date_range(device_id, start, end)
    return [
        {
            "id": str(d.id),
            "device_id": d.device_id,
            "data": d.data_json,
            "timestamp": d.created_at.isoformat() if d.created_at else "",
        }
        for d in data
    ]


@router.get("/data/list")
async def list_iot_data(
    device_id: str = "",
    page: int = 1,
    limit: int = 50,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> PaginatedDataResponse:
    result = await use_case.list_iot_data(device_id, page, limit)
    return PaginatedDataResponse(**result)


@router.get("/devices/{device_id}/stats")
async def get_device_stats(
    device_id: str,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> DeviceStatsResponse:
    result = await use_case.get_device_stats(device_id)
    return DeviceStatsResponse(**result)


@router.post("/export")
async def export_data(
    payload: ExportDataRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> Response:
    data, content_type = await use_case.export_data(
        device_id=payload.device_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        format=payload.format,
    )
    filename = f"iot_export_{payload.device_id or 'all'}.{payload.format}"
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = 90,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> CleanupResponse:
    count = await use_case.cleanup_old_data(days)
    return CleanupResponse(
        deleted_count=count,
        message=f"Cleaned up {count} records older than {days} days",
    )


# ============================================================
# WebSocket
# ============================================================


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str = "default") -> None:
    await ws_manager.connect(websocket, room)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            msg_type = msg.get("type", "")

            if msg_type == "subscribe":
                topic = msg.get("topic", "")
                await ws_manager.subscribe(websocket, topic)
                await websocket.send_text(
                    json.dumps({"event": "subscribed", "topic": topic})
                )

            elif msg_type == "unsubscribe":
                topic = msg.get("topic", "")
                await ws_manager.unsubscribe(websocket, topic)
                await websocket.send_text(
                    json.dumps({"event": "unsubscribed", "topic": topic})
                )

            elif msg_type == "join_room":
                new_room = msg.get("room", "default")
                await ws_manager.disconnect(websocket, room)
                room = new_room
                await ws_manager.connect(websocket, room)
                await websocket.send_text(
                    json.dumps({"event": "joined_room", "room": room})
                )

            elif msg_type == "message":
                topic = msg.get("topic", "")
                payload = msg.get("data", {})
                await ws_manager.broadcast_to_room(room, "message", payload)
                if topic:
                    await ws_manager.broadcast_to_topic(topic, payload)

            else:
                await websocket.send_text(
                    json.dumps({"error": f"Unknown type: {msg_type}"})
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, room)


@router.get("/ws/rooms")
async def get_ws_rooms() -> dict[str, Any]:
    rooms = ws_manager.get_rooms()
    return {
        "rooms": [{"name": r, "clients": c} for r, c in rooms.items()],
        "total_connections": ws_manager.get_total_connections(),
    }


@router.get("/ws/rooms/{room}/stats")
async def get_ws_room_stats(room: str) -> dict[str, Any]:
    return {
        "room": room,
        "clients": ws_manager.get_clients_in_room(room),
    }


# ============================================================
# Batch Processing
# ============================================================


@router.post("/batch/process")
async def batch_process(
    payload: BatchProcessRequest,
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for item in payload.items:
        try:
            result = await use_case.process_mqtt_data(item.device_id, item.raw_data)
            results.append({"device_id": item.device_id, "status": "ok", "data": result})
        except Exception as exc:
            results.append({"device_id": item.device_id, "status": "error", "error": str(exc)})

    success_count = sum(1 for r in results if r["status"] == "ok")
    return {
        "total": len(payload.items),
        "success": success_count,
        "failed": len(payload.items) - success_count,
        "results": results,
    }


@router.post("/batch/control")
async def batch_control(
    items: list[ControlRequest],
    use_case: IoTUseCase = Depends(get_iot_use_case),
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for item in items:
        try:
            success = await use_case.device_control(item.topic, item.message)
            results.append({"topic": item.topic, "success": success})
        except Exception as exc:
            results.append({"topic": item.topic, "success": False, "error": str(exc)})

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "total": len(items),
        "success": success_count,
        "failed": len(items) - success_count,
        "results": results,
    }
