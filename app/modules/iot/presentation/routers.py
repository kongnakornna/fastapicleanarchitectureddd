"""iot HTTP + WebSocket routers — with authentication

Pattern mirrors app/modules/user/presentation/routers.py:
  - Public:    _: Annotated[None, Depends(no_authentication)]
  - Protected: authentication: Annotated[Authentication, Depends(authenticate_user)]
  - Errors:    StandardException → DomainError → Exception (with logger)
"""
from __future__ import annotations

import contextlib
import json
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger

from app.core.security import authenticate_user, no_authentication ,authenticate_websocket
from app.core.websocket_hub import ws_manager
from app.modules.authentication.domain.entities import Authentication
from app.modules.iot.application.use_case import IotUseCase
from app.modules.iot.presentation.dependencies import get_iot_use_case
from app.modules.iot.presentation.schemas import (
    BatchControlRequest,
    BatchProcessRequest,
    ControlRequest,
    UpdateDeviceConfigRequest,
    UpdateDeviceStatusRequest,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from datetime import UTC, datetime
router = APIRouter(prefix="/iot", tags=["iot"])


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def _parse_export_date(s: str) -> datetime:
    """Accept RFC3339 or 'YYYY-MM-DD HH:MM:SS'."""
    s = s.strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def _set_tenant_from_auth(auth: Authentication | None) -> None:
    """TH: set tenant context จาก Authentication | EN: set tenant from auth"""
    if auth is None:
        return
    tenant_id: str | None = None
    for attr in ("tenant_id", "tenantId", "org_id", "orgId"):
        v = getattr(auth, attr, None)
        if v:
            tenant_id = str(v)
            break
    if not tenant_id:
        user = getattr(auth, "user", None)
        if user:
            for attr in ("tenant_id", "tenantId", "org_id"):
                v = getattr(user, attr, None)
                if v:
                    tenant_id = str(v)
                    break
    if tenant_id:
        from app.modules.iot.infrastructure.tenant_context import (
            set_current_tenant,
        )
        set_current_tenant(tenant_id)


# ═══════════════════════════════════════════════════════════════
#  STATUS  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/status")
async def get_status(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    """TH: สถานะ MQTT + cache | EN: MQTT + cache status"""
    return {
        "mqtt_connected": uc.is_connected(),
        "cache_enabled": uc.is_cache_enabled(),
    }


# ═══════════════════════════════════════════════════════════════
#  TOPIC DATA  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/topic")
async def get_topic_data(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    topic: str = Query(..., min_length=1, description="MQTT topic name"),
    delcache: str = Query("", description="Set to '1' to delete cache"),
) -> dict[str, Any]:
    """TH: ดึงข้อมูลจาก topic | EN: get topic data"""
    try:
        resp = await uc.get_topic_data(topic, delcache == "1")
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e) from e
    except Exception as e:
        logger.opt(exception=e).error("http.iot.topic.unexpected")
        raise HTTPException(500, "internal error") from None

    resp["timestamp"] = datetime.now(UTC).isoformat()
    resp["mqtt_connected"] = uc.is_connected()
    resp["cache_enabled"] = uc.is_cache_enabled()
    return resp


@router.get("/topicdevicechart")
async def get_topic_data_device_chart(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    topic: str = Query(..., min_length=1),
    bucket: str = Query("AIRCOM1"),
    measurement: str = Query("temperature"),
    field: str = Query("value"),
    start: str = Query("-10m"),
    stop: str = Query("now()"),
    limit: int = Query(100, ge=1),
    delcache: str = Query(""),
) -> dict[str, Any]:
    """TH: chart + latest payload | EN: chart + latest payload"""
    return await uc.get_topic_data_device_chart(
        bucket=bucket or "AIRCOM1",
        topic=topic,
        measurement=measurement or "temperature",
        field=field or "value",
        start=start or "-10m",
        stop=stop,
        limit=limit if limit > 0 else 100,
        cache_delete=1 if delcache == "1" else 0,
    )


# ═══════════════════════════════════════════════════════════════
#  🔒 CONTROLS  (protected)
# ═══════════════════════════════════════════════════════════════
@router.get("/controls")
async def device_controls_query(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    topic: str = Query(..., min_length=1),
    message: str = Query(..., min_length=1),
) -> dict[str, str]:
    """TH: ส่งคำสั่ง (GET, auth) | EN: send control (GET, auth)"""
    try:
        _set_tenant_from_auth(authentication)
        ok = await uc.device_control(topic, message)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="control publish failed",
            )
        return {"status": "ok", "statusCode": "200"}
    except HTTPException:
        raise
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e) from e
    except Exception as e:
        logger.opt(exception=e).error("http.iot.controls.unexpected")
        raise HTTPException(500, "internal error") from None


@router.post("/control")
async def device_control_post(
    payload: ControlRequest,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    x_idempotency_key: str | None = Header(None, alias="X-Idempotency-Key"),
) -> dict[str, str]:
    """TH: ส่งคำสั่ง (POST, auth) | EN: send control (POST, auth)"""
    try:
        _set_tenant_from_auth(authentication)

        # ═══ Part 12: Idempotency ═══
        # หลังจากตรวจสอบ idempotency แล้ว ให้ดำเนินการส่งคำสั่งต่อไป
        store = None
        if x_idempotency_key:
            try:
                from app.modules.iot.infrastructure.idempotency import (
                    get_idempotency_store,
                )
                store = get_idempotency_store(uc.redis_client)
                cached = await store.check_or_lock(
                    x_idempotency_key, "control", payload.model_dump(),
                )
                if cached and cached.get("__conflict__"):
                    return {"status": "conflict", "detail": "concurrent request"}
                if cached and "body" in cached:
                    return cached["body"]
            except Exception as e:
                logger.opt(exception=e).warning(
                    "http.iot.control.idempotency.failed",
                    key=x_idempotency_key,
                )

        ok = await uc.device_control(payload.topic, payload.message)
        result = {"status": "ok" if ok else "failed"}

        if x_idempotency_key and store is not None:
            try:
                await store.complete(x_idempotency_key, "control", 200, result)
            except Exception as e:
                logger.opt(exception=e).warning(
                    "http.iot.control.idempotency.complete.failed",
                    key=x_idempotency_key,
                )

        return result
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.control.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  DEVICES  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/device")
async def get_device_list(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(1000, ge=1),
    bucket: str = Query(""),
    hardware_id: int = Query(0),
    keyword: str = Query(""),
    lang: str = Query("en"),
) -> dict[str, Any]:
    """TH: list devices | EN: list devices"""
    return await uc.get_device_list(
        bucket=bucket, hardware_id=hardware_id,
        page=page, page_size=pageSize, keyword=keyword,
    )


@router.get("/devicebuckets")
async def get_device_buckets(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    bucket: str = Query(..., min_length=1),
) -> dict[str, Any]:
    return await uc.get_device_buckets(bucket)


@router.get("/locationdevice")
async def get_device_by_location(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    location_id: int = Query(..., ge=1),
) -> list[dict[str, Any]]:
    return await uc.get_device_list_by_location(location_id)


# ═══════════════════════════════════════════════════════════════
#  CHARTS  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/sensercharts")
async def get_senser_charts(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    bucket: str = Query(..., min_length=1),
    measurement: str = Query(..., min_length=1),
    field: str = Query("value"),
    start: str = Query("-1h"),
    stop: str = Query("now()"),
    limit: int = Query(1000, ge=1),
) -> dict[str, Any]:
    return await uc.get_senser_charts(
        measurement=measurement, field=field or "value",
        bucket=bucket, start=start, stop=stop, limit=limit,
    )


@router.get("/devicesensercharts")
async def get_device_senser_charts(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    bucket: str = Query(..., min_length=1),
    measurement: str = Query(..., min_length=1),
    field: str = Query("value"),
    start: str = Query("-1h"),
    stop: str = Query("now()"),
    limit: int = Query(1000, ge=1),
) -> dict[str, Any]:
    return await uc.get_device_senser_charts(
        measurement=measurement, field=field or "value",
        bucket=bucket, start=start, stop=stop, limit=limit,
    )


@router.get("/monitordevicechart")
async def get_monitor_device_chart(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    bucket: str = Query(..., min_length=1),
    measurement: str = Query("temperature"),
    field: str = Query("value"),
    start: str = Query("-10m"),
    stop: str = Query("now()"),
    limit: int = Query(100, ge=1),
    cache_delete: int = Query(0, ge=0, le=1),
) -> dict[str, Any]:
    return await uc.get_monitor_device_chart(
        bucket=bucket, measurement=measurement, field=field,
        start=start, stop=stop, limit=limit, cache_delete=cache_delete,
    )


# ═══════════════════════════════════════════════════════════════
#  ALARM / MONITOR  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/alarmdevicestatus")
async def get_alarm_device_status(
    _: Annotated[None, Depends(no_authentication)],
    request: Request,
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    params = dict(request.query_params)
    for k in ("page", "page_size", "hardware_id", "type_id"):
        if k in params:
            try: params[k] = int(params[k])
            except (ValueError, TypeError): pass
    return await uc.get_alarm_device_status(**params)


@router.get("/alarmdevicestatuscontrol")
async def get_alarm_device_status_control(
    _: Annotated[None, Depends(no_authentication)],
    request: Request,
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    params = dict(request.query_params)
    for k in ("page", "page_size", "hardware_id", "type_id"):
        if k in params:
            try: params[k] = int(params[k])
            except (ValueError, TypeError): pass
    return await uc.get_alarm_device_status_control(**params)


@router.get("/devicemqtt")
async def device_mqtt(
    _: Annotated[None, Depends(no_authentication)],
    request: Request,
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    params = dict(request.query_params)
    for k in ("page", "page_size", "pageSize", "type_id", "hardware_id", "deletecache"):
        if k in params:
            try: params[k] = int(params[k])
            except (ValueError, TypeError): pass
    if "pageSize" in params and "page_size" not in params:
        params["page_size"] = params.pop("pageSize")
    return await uc.get_device_mqtt(**params)


@router.get("/monitordevicegroup")
async def get_monitor_device_group(
    _: Annotated[None, Depends(no_authentication)],
    request: Request,
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> Any:
    params = dict(request.query_params)
    for k in ("location_id", "hardware_id", "delcache", "del_cache"):
        if k in params:
            try: params[k] = int(params[k])
            except (ValueError, TypeError): pass
    return await uc.get_monitor_device_group(**params)


# ═══════════════════════════════════════════════════════════════
#  DEVICE STATUS (GET public / PUT protected)
# ═══════════════════════════════════════════════════════════════
@router.get("/devicestatus")
async def get_device_status(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
) -> dict[str, Any]:
    return await uc.get_device_status(deviceId)


@router.put("/devicestatus")
async def update_device_status(
    payload: UpdateDeviceStatusRequest,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
) -> dict[str, str]:
    try:
        _set_tenant_from_auth(authentication)
        await uc.update_device_status(deviceId, payload.model_dump(exclude_none=True))
        return {"status": "updated"}
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.update_device_status.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  DEVICE CONFIG (GET public / PUT protected)
# ═══════════════════════════════════════════════════════════════
@router.get("/deviceconfig")
async def get_device_config(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
) -> dict[str, Any]:
    return await uc.get_device_config(deviceId)


@router.put("/updatedeviceconfig")
async def update_device_config(
    payload: UpdateDeviceConfigRequest,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
) -> dict[str, str]:
    try:
        _set_tenant_from_auth(authentication)
        await uc.update_device_config(deviceId, payload.config)
        return {"status": "updated"}
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.update_device_config.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  IOT DATA  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/deviceiotdata")
async def list_iot_data(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    startDate: str = Query(""),
    endDate: str = Query(""),
) -> dict[str, Any]:
    return await uc.list_iot_data(
        device_id=deviceId, page=page, limit=limit,
        start_date=startDate, end_date=endDate,
    )


@router.get("/devicestats")
async def get_device_stats(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
) -> dict[str, Any]:
    return await uc.get_device_stats(deviceId)


# ═══════════════════════════════════════════════════════════════
#  🔒 CLEANUP  (protected)
# ═══════════════════════════════════════════════════════════════
@router.delete("/devicedatacleanup")
async def cleanup_old_data(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    days: int = Query(30, ge=1),
) -> dict[str, int]:
    try:
        _set_tenant_from_auth(authentication)
        count = await uc.cleanup_old_data(days)
        return {"deleted": count}
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.cleanup.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  EXPORT  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/devicedataexport")
async def export_data(
    _: Annotated[None, Depends(no_authentication)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
    deviceId: str = Query(..., min_length=1),
    startDate: str = Query(..., min_length=1),
    endDate: str = Query(..., min_length=1),
    format: str = Query("json"),
) -> Response:
    try:
        start = _parse_export_date(startDate)
        end = _parse_export_date(endDate)
    except ValueError:
        raise HTTPException(
            400, "invalid date format (RFC3339 or YYYY-MM-DD HH:MM:SS)",
        )

    fmt = "csv" if format.lower() == "csv" else "json"
    data, content_type = await uc.export_data(
        device_id=deviceId, start_date=start, end_date=end, export_format=fmt,
    )
    filename = f"data.{fmt}"
    return Response(
        content=data, media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ═══════════════════════════════════════════════════════════════
#  WS STATS  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/ws/stats")
async def ws_stats(
    _: Annotated[None, Depends(no_authentication)],
) -> dict[str, Any]:
    """TH: สถิติ WS rooms | EN: WS rooms stats"""
    try:
        return {
            "rooms": ws_manager.get_rooms(),
            "topics": ws_manager.get_topics(),
            "total_connections": ws_manager.get_total_connections(),
        }
    except Exception as exc:
        return {"error": str(exc)}


# ═══════════════════════════════════════════════════════════════
#  🔒 BATCH  (protected)
# ═══════════════════════════════════════════════════════════════
@router.post("/batch/process")
async def batch_process(
    payload: BatchProcessRequest,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    """TH: batch process MQTT payloads | EN: batch process MQTT"""
    try:
        _set_tenant_from_auth(authentication)
        items = [it.model_dump() for it in payload.items]
        return await uc.batch_process_mqtt(items)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.batch_process.unexpected")
        raise HTTPException(500, "internal error")


@router.post("/batch/control")
async def batch_control(
    payload: BatchControlRequest,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    """TH: batch send control | EN: batch control"""
    try:
        _set_tenant_from_auth(authentication)
        items = [it.model_dump() for it in payload.items]
        return await uc.batch_control(items)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.batch_control.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  ALERTING  (GET public / POST protected)
# ═══════════════════════════════════════════════════════════════
@router.get("/alerts/channels")
async def get_alert_channels(
    _: Annotated[None, Depends(no_authentication)],
) -> dict[str, Any]:
    try:
        from app.modules.iot.infrastructure.alerting.dispatcher import (
            alert_dispatcher,
        )
        return alert_dispatcher.get_channels_status()
    except Exception as exc:
        return {"error": str(exc)}


@router.post("/alerts/test")
async def test_alert(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    channel: str = Query(..., min_length=1),
) -> dict[str, Any]:
    try:
        from app.modules.iot.infrastructure.alerting.base import AlertMessage
        from app.modules.iot.infrastructure.alerting.dispatcher import (
            alert_dispatcher,
        )
        msg = AlertMessage(
            device_id=0,
            device_name="TEST DEVICE",
            alarm_status=2,
            title="Test Alert",
            subject="Test Alert Subject",
            content="This is a test alert from iot module",
            value_data=99.9,
            unit="°C",
            severity="critical",
        )
        results = await alert_dispatcher.send(msg, channels=[channel])
        return {"channel": channel, "sent": results}
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.test_alert.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  SCHEDULER  (public)
# ═══════════════════════════════════════════════════════════════
@router.get("/admin/scheduler/jobs")
async def get_scheduled_jobs(
    _: Annotated[None, Depends(no_authentication)],
) -> dict[str, Any]:
    try:
        from app.modules.iot.infrastructure.scheduler import get_scheduler
        sched = get_scheduler()
        return {"jobs": sched.get_jobs_info()}
    except Exception as exc:
        return {"jobs": [], "error": str(exc)}


# ═══════════════════════════════════════════════════════════════
#  🔒 MANUAL INGEST  (protected)
# ═══════════════════════════════════════════════════════════════
@router.post("/processmqttdata")
async def process_mqtt_data(
    payload: Annotated[dict[str, Any], Body(...)],
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    uc: Annotated[IotUseCase, Depends(get_iot_use_case)],
) -> dict[str, Any]:
    """TH: process MQTT data ด้วยตนเอง (auth) | EN: manual MQTT ingest (auth)"""
    try:
        _set_tenant_from_auth(authentication)
        device_id = payload.get("device_id") or payload.get("deviceId")
        raw_data = payload.get("raw_data") or payload.get("rawData")
        if not device_id or not raw_data:
            raise HTTPException(400, "device_id and raw_data are required")
        return await uc.process_mqtt_data(str(device_id), str(raw_data))
    except HTTPException:
        raise
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("http.iot.process_mqtt_data.unexpected")
        raise HTTPException(500, "internal error")


# ═══════════════════════════════════════════════════════════════
#  WEBSOCKET  (connect freely — subscribe by room)
# ═══════════════════════════════════════════════════════════════
@router.websocket("/ws/{room}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str = "default",
    authentication: Authentication = Depends(authenticate_websocket),
) -> None:
    # ถ้าอยากคุมสิทธิ์ตาม room ก็ตรวจที่นี่
    # เช่น room ต้องขึ้นต้นด้วย tenant_id ของ user
    if not room.startswith(str(authentication.user.id)):
        await websocket.close(code=4403, reason="forbidden room")
        return

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
    except Exception as exc:
        logger.opt(exception=exc).error("http.iot.ws.unexpected")
        await ws_manager.disconnect(websocket, room)
        with contextlib.suppress(Exception):
            await websocket.close()
