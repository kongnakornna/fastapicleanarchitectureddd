"""iot use cases — port จาก Go usecase.go"""
from __future__ import annotations

import asyncio
import contextlib
import csv
import io
import json
import os
import uuid as _uuid
from datetime import UTC, datetime
from hashlib import md5
from typing import TYPE_CHECKING, Any

from loguru import logger

from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO
from app.modules.iot.infrastructure.caches import IotCache
from app.modules.iot.infrastructure.models import (
    ActivityLog,
    CommandLog,
    DeviceConfig,
    DeviceStatus,
    IotData,
)
from app.modules.iot.infrastructure.repositories.device_repository import (
    DeviceListFilter,
)
from app.modules.iot.infrastructure.ws_broadcaster import ws_broadcaster

if TYPE_CHECKING:
    from redis.asyncio import Redis


# ═══════════════════════════════════════════════════════════════
#  BACKGROUND TASK REGISTRY
#  TH: กัน GC เก็บ task ทิ้งก่อนทำงานเสร็จ | EN: keep strong refs
# ═══════════════════════════════════════════════════════════════
_BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()


def _spawn(coro: Any) -> asyncio.Task[Any]:
    """TH: สร้าง task พร้อมเก็บ reference | EN: create task with strong ref."""
    task = asyncio.create_task(coro)
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)
    return task


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def _f(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _i(v: Any) -> int:
    if v is None:
        return 0
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _extract(data: dict[str, Any], *keys: str) -> tuple[float, bool]:
    for k in keys:
        if not k:
            continue
        if k in data:
            try:
                return float(data[k]), True
            except (TypeError, ValueError):
                continue
    return 0.0, False


def _build_map(raw: str, cfg: dict[str, str] | None) -> dict[str, Any]:
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            obj["raw"] = raw
            return obj
    except (json.JSONDecodeError, TypeError):
        pass
    parts = raw.split(",")
    out: dict[str, Any] = {}
    for i, val in enumerate(parts):
        key = str(i)
        if cfg and key in cfg:
            key = cfg[key]
        t = val.strip()
        try:
            out[key] = float(t)
        except ValueError:
            out[key] = t
    out["raw"] = raw
    return out


def _bucket_from_topic(topic: str) -> str:
    return topic.split("/")[0].strip("/") if topic else ""


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ═══════════════════════════════════════════════════════════════
#  TENANT RESOLVER — Part 12
# ═══════════════════════════════════════════════════════════════
def _resolve_tenant_id(device: Any = None) -> str | None:
    """
    TH: หา tenant_id จากหลายแหล่งตามลำดับ:
        1. context (จาก TenantMiddleware)
        2. device.tenant_id (จาก record)
        3. env TENANT_DEFAULT_ID
    EN: resolve tenant_id from: context → device → env default
    """
    # 1. Context (จาก middleware)
    try:
        from app.modules.iot.infrastructure.tenant_context import (
            get_current_tenant,
        )

        _tid = get_current_tenant()
        if _tid:
            return _tid
    except Exception:
        pass

    # 2. Device record
    if device is not None:
        _tid = getattr(device, "tenant_id", None)
        if _tid:
            return str(_tid)

    # 3. Env default
    return os.getenv(
        "TENANT_DEFAULT_ID",
        "11111111-1111-1111-1111-111111111111",
    )


# ═══════════════════════════════════════════════════════════════
#  USE CASE
# ═══════════════════════════════════════════════════════════════
class IotUseCase:
    def __init__(
        self,
        device_repository: Any,
        device_config_repository: Any,
        device_status_repository: Any,
        device_alert_repository: Any,
        iot_data_repository: Any,
        alarm_log_repository: Any,
        activity_log_repository: Any,
        command_log_repository: Any,
        mqtt_client: Any | None = None,
        influxdb_client: Any | None = None,
        redis_client: Redis | None = None,
        cfg: Any | None = None,
    ) -> None:
        self._device_repo = device_repository
        self._device_config_repo = device_config_repository
        self._device_status_repo = device_status_repository
        self._device_alert_repo = device_alert_repository
        self._iot_data_repo = iot_data_repository
        self._alarm_log_repo = alarm_log_repository
        self._activity_log_repo = activity_log_repository
        self._command_log_repo = command_log_repository
        self._mqtt = mqtt_client
        self._influx = influxdb_client
        self._cache = IotCache(redis_client)
        self._redis_client = redis_client
        self._cfg = cfg

    # ═══════════════════════════════════════════════════════════
    #  PUBLIC ACCESSORS
    # ═══════════════════════════════════════════════════════════
    @property
    def redis_client(self) -> Redis | None:
        """TH: Redis handle สำหรับ infrastructure helpers (idempotency ฯลฯ)
        | EN: public Redis handle — DO NOT mutate."""
        return self._redis_client

    @property
    def cache(self) -> IotCache:
        """TH: cache abstraction (ปลอดภัยแม้ Redis = None)
        | EN: cache abstraction (safe even when Redis is None)."""
        return self._cache

    # ─── Status ────────────────────────────────────────
    def is_connected(self) -> bool:
        return bool(self._mqtt and self._mqtt.is_connected())

    def is_cache_enabled(self) -> bool:
        return self._cache.enabled

    def _base_url(self) -> str:
        if self._cfg is not None:
            return str(getattr(self._cfg, "SERVER_BASE_URL", "")).rstrip("/")
        return ""

    @staticmethod
    def _parse(data: Any) -> Any:
        if isinstance(data, bytes):
            data = data.decode()
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return data

    # ═══════════════════════════════════════════════════
    #  TOPIC DATA
    # ═══════════════════════════════════════════════════
    async def get_topic_data(
        self, topic: str, del_cache: bool = False,
    ) -> dict[str, Any]:
        key = f"mqtt_topic:{topic}"
        if del_cache:
            await self._cache.delete(key)
        elif self._cache.enabled:
            c = await self._cache.get(key)
            if c is not None:
                return {
                    "topic": topic, "payload": c,
                    "from": "cache", "cache": True,
                }

        if not self.is_connected():
            return {
                "topic": topic, "payload": None,
                "from": "mqtt_disconnected", "cache": False,
            }

        try:
            data = self._mqtt.get_data_from_topic(topic, timeout=1)
            if data:
                p = self._parse(data)
                await self._cache.set(key, p, ttl=10)
                return {
                    "topic": topic, "payload": p,
                    "from": "mqtt", "cache": False,
                }
        except Exception as exc:
            logger.warning(f"MQTT fetch {topic}: {exc}")

        c = await self._cache.get(key)
        if c is not None:
            return {
                "topic": topic, "payload": c,
                "from": "cache_fallback", "cache": True,
            }
        return {
            "topic": topic, "payload": None,
            "from": "mqtt_error", "cache": False,
        }

    # ═══════════════════════════════════════════════════
    #  DEVICE CONTROL
    # ═══════════════════════════════════════════════════
    async def device_control(self, topic: str, message: str) -> bool:
        if not self.is_connected():
            return False
        ok = self._mqtt.publish(topic, message, qos=1)
        with contextlib.suppress(Exception):
            await self._command_log_repo.create(
                CommandLog(
                    device_id=topic, action=message,
                    status="sent" if ok else "failed",
                )
            )
        return bool(ok)

    device_controls = device_control

    # ═══════════════════════════════════════════════════
    #  PART 9 — BATCH OPERATIONS
    # ═══════════════════════════════════════════════════
    async def batch_process_mqtt(
        self, items: list[dict[str, str]],
    ) -> dict[str, Any]:
        """TH: process หลาย MQTT payload พร้อมกัน | EN: batch process MQTT"""
        results = await asyncio.gather(
            *(
                self.process_mqtt_data(it["device_id"], it["raw_data"])
                for it in items
            ),
            return_exceptions=True,
        )
        success, failed = 0, 0
        details: list[dict[str, Any]] = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                failed += 1
                details.append({"index": i, "error": str(r)})
            else:
                success += 1
                details.append({"index": i, "ok": True})

        return {
            "total": len(items),
            "success": success,
            "failed": failed,
            "details": details,
        }

    async def batch_control(
        self, items: list[dict[str, str]],
    ) -> dict[str, Any]:
        """TH: send หลาย control พร้อมกัน | EN: batch control"""
        results = await asyncio.gather(
            *(self.device_control(it["topic"], it["message"]) for it in items),
            return_exceptions=True,
        )
        success = sum(1 for r in results if r is True)

        return {
            "total": len(items),
            "success": success,
            "failed": len(items) - success,
            "results": [bool(r) for r in results],
        }

    # ═══════════════════════════════════════════════════
    #  DEVICE LIST
    # ═══════════════════════════════════════════════════
    async def get_device_list(
        self, bucket: str = "", hardware_id: int = 0,
        page: int = 1, page_size: int = 1000, keyword: str = "",
    ) -> dict[str, Any]:
        f = DeviceListFilter(
            bucket=bucket, hardware_id=hardware_id,
            page=page, page_size=page_size, keyword=keyword,
        )
        items, total = await self._device_repo.list_with_alarm(f)

        buckets: dict[str, Any] = {}
        for it in items:
            if it.device_bucket and it.device_bucket not in buckets:
                buckets[it.device_bucket] = it
        mqtt_map: dict[str, dict[str, Any]] = {}
        for b, s in buckets.items():
            mqtt_map[b] = await self._fetch_bucket(b, s)

        return {
            "data": [
                self._detail(it, mqtt_map.get(it.device_bucket, {}))
                for it in items
            ],
            "total": total, "page": page, "pageSize": page_size,
            "totalPage": (total + page_size - 1) // page_size if page_size else 0,
        }

    async def get_device_list_page(self, **kw: Any) -> dict[str, Any]:
        return await self.get_device_list(**kw)

    async def get_device_list_by_location(
        self, location_id: int,
    ) -> list[dict[str, Any]]:
        devices = await self._device_repo.find_by_location(location_id)
        out = []
        for d in devices:
            s = type(
                "S", (), {
                    "device_id": d.device_id, "device_bucket": d.bucket,
                    "mqtt_data_value": d.mqtt_data_value,
                    "mqtt_status_data_name": d.mqtt_status_data_name,
                    "measurement": d.measurement,
                    "mqtt_device_name": d.mqtt_device_name,
                },
            )()
            p = await self._fetch_bucket(d.bucket, s)
            out.append(self._detail(s, p))
        return out

    async def get_device_buckets(self, bucket: str) -> dict[str, Any]:
        devices = await self._device_repo.find_by_bucket(bucket)
        if not devices:
            return {"bucket": bucket, "devices": []}
        d = devices[0]
        s = type(
            "S", (), {
                "device_id": d.device_id, "device_bucket": d.bucket,
                "mqtt_data_value": d.mqtt_data_value,
                "mqtt_status_data_name": d.mqtt_status_data_name,
                "measurement": d.measurement,
                "mqtt_device_name": d.mqtt_device_name,
            },
        )()
        p = await self._fetch_bucket(bucket, s)
        return {
            "bucket": bucket,
            "devices": [self._detail(s, p) for _ in devices],
        }

    async def _fetch_bucket(
        self, bucket: str, sample: Any,
    ) -> dict[str, Any]:
        if not self.is_connected() and not self._cache.enabled:
            return {}
        topic = getattr(sample, "mqtt_data_value", "") or f"{bucket}/DATA"
        key = f"mqtt_payload:{bucket}"
        raw = await self._cache.get_raw(key) or ""
        if not raw and self.is_connected():
            try:
                data = self._mqtt.get_data_from_topic(topic, timeout=1)
                if data:
                    raw = (
                        data.decode()
                        if isinstance(data, bytes)
                        else str(data)
                    )
                    await self._cache.set(key, raw, ttl=30)
            except Exception as exc:
                logger.warning(f"MQTT bucket {bucket}: {exc}")
        if not raw:
            return {}
        parts = raw.split(",")
        cfg = None
        with contextlib.suppress(json.JSONDecodeError, TypeError):
            cfg = json.loads(
                getattr(sample, "mqtt_status_data_name", "") or "{}"
            )
        out: dict[str, Any] = {}
        for i, v in enumerate(parts):
            k = cfg.get(str(i), str(i)) if cfg else str(i)
            out[k] = v.strip()
        return out

    def _detail(self, item: Any, mqtt: dict[str, Any]) -> dict[str, Any]:
        m = getattr(item, "measurement", "") or ""
        mn = getattr(item, "mqtt_device_name", "") or ""
        raw = mqtt.get(m) or mqtt.get(mn) or "0"
        v = _f(raw)
        vs = f"{v:.2f}" if getattr(item, "hardware_id", 0) == 1 else str(raw)
        dto = AlarmDetailDTO(
            hardware_id=getattr(item, "hardware_id", 0),
            value_data=vs, value_alarm=0,
            max_value=getattr(item, "max_", "") or 0,
            min_value=getattr(item, "min_", "") or 0,
            status_alert=getattr(item, "status_alert", "") or 0,
            status_warning=getattr(item, "status_warning", "") or 0,
            recovery_warning=getattr(item, "recovery_warning", "") or 0,
            recovery_alert=getattr(item, "recovery_alert", "") or 0,
            device_name=getattr(item, "device_name", "") or "",
            action_name=getattr(item, "mqtt_name", "") or "",
            mqtt_name=getattr(item, "mqtt_name", "") or "",
            mqtt_control_on=getattr(item, "mqtt_control_on", "") or "",
            mqtt_control_off=getattr(item, "mqtt_control_off", "") or "",
            count_alarm=0, event=1,
            unit=getattr(item, "unit", "") or "",
        )
        a = evaluate_alarm(dto, lang="en")
        return {
            "device_id": getattr(item, "device_id", 0),
            "device_name": getattr(item, "device_name", "") or "",
            "type_name": getattr(item, "type_name", "") or "",
            "value_data": vs, "unit": getattr(item, "unit", "") or "",
            "status": getattr(item, "status", 0),
            "alarm_title": a.title,
            "status_warning": getattr(item, "status_warning", "") or "",
            "status_alert": getattr(item, "status_alert", "") or "",
            "recovery_warning": getattr(item, "recovery_warning", "") or "",
            "recovery_alert": getattr(item, "recovery_alert", "") or "",
            "icon": getattr(item, "icon", "") or "",
        }

    # ═══════════════════════════════════════════════════
    #  CHARTS
    # ═══════════════════════════════════════════════════
    async def get_senser_charts(
        self, bucket: str = "iot_sensors", measurement: str = "temperature",
        field: str = "value", start: str = "-1h", stop: str = "now()",
        limit: int = 1000,
    ) -> dict[str, Any]:
        return await self._influx_query(
            bucket, measurement, field, start, stop, limit,
        )

    get_senser_data_chart = get_senser_charts
    get_senser_data = get_senser_charts
    get_device_senser_charts = get_senser_charts

    async def _influx_query(
        self, bucket: str, measurement: str, field: str,
        start: str, stop: str, limit: int,
    ) -> dict[str, Any]:
        if self._influx is None:
            return {"data": [], "date": [], "cache": "no cache"}
        try:
            from app.core.influxdb_client import QueryParams

            params = QueryParams(
                measurement=measurement, field=field, bucket=bucket,
                start=start, stop=stop, limit=limit,
            )
            results = self._influx.query_filter_data(params)
            dp, tp = [], []
            for r in results:
                if "_value" in r:
                    dp.append(float(r["_value"]))
                if "_time" in r:
                    tp.append(str(r["_time"]))
            return {"data": dp, "date": tp, "cache": "no cache"}
        except Exception as exc:
            logger.error(f"Influx: {exc}")
            return {
                "data": [], "date": [], "cache": "error",
                "error": str(exc),
            }

    async def get_monitor_device_chart(
        self, bucket: str = "iot_sensors", measurement: str = "temperature",
        field: str = "value", start: str = "-10m", stop: str = "now()",
        limit: int = 100, cache_delete: int = 0,
    ) -> dict[str, Any]:
        # FIPS-safe md5: ใช้ usedforsecurity=False
        _raw = f"{bucket}:{measurement}:{field}:{start}:{stop}:{limit}"
        _h = md5(_raw.encode(), usedforsecurity=False).hexdigest()
        key = f"mqtt_chart:{_h}"
        if cache_delete:
            await self._cache.delete(key)
        else:
            c = await self._cache.get(key)
            if c is not None:
                c["cache"] = "cache"
                return c
        resp = await self._influx_query(
            bucket, measurement, field, start, stop, limit,
        )
        await self._cache.set(key, resp, ttl=41)
        return resp

    async def get_topic_data_device_chart(
        self, bucket: str = "iot_sensors", topic: str = "",
        measurement: str = "temperature", field: str = "value",
        start: str = "-10m", stop: str = "now()", limit: int = 100,
        cache_delete: int = 0,
    ) -> dict[str, Any]:
        topic = topic or f"{bucket}/DATA"
        chart = await self.get_monitor_device_chart(
            bucket=bucket, measurement=measurement, field=field,
            start=start, stop=stop, limit=limit, cache_delete=cache_delete,
        )
        payload = None
        src = ""
        if not cache_delete:
            c = await self._cache.get(f"mqtt_topic:{topic}")
            if c is not None:
                payload, src = c, "cache"
        if src == "" and self.is_connected():
            try:
                data = self._mqtt.get_data_from_topic(topic, timeout=1)
                if data:
                    payload = self._parse(data)
                    src = "mqtt"
                    await self._cache.set(
                        f"mqtt_topic:{topic}", payload, ttl=10,
                    )
            except Exception as exc:
                logger.warning(f"MQTT {topic}: {exc}")
        return {
            "topic": topic, "chart": chart, "latest_payload": payload,
            "latest_from": src,
            "cache": "cache" if src == "cache" else "no cache",
        }

    # ═══════════════════════════════════════════════════
    #  ALARM DEVICE STATUS
    # ═══════════════════════════════════════════════════
    async def get_alarm_device_status(
        self, bucket: str = "", page: int = 1, page_size: int = 1000,
        measurement: str = "temperature", lang: str = "en",
        **filters: Any,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, page=page, page_size=page_size,
            hardware_id=_i(filters.get("hardware_id", 0)),
            keyword=filters.get("keyword", ""),
        )
        items, _ = await self._device_repo.list_with_alarm(f)

        mqtt_map: dict[str, Any] = {}
        raw = ""
        if mqtt_connected and items:
            s = items[0]
            raw = await self._cache.get_raw(f"mqtt_payload:{bucket}") or ""
            if not raw and s.device_bucket:
                raw = (
                    await self._cache.get_raw(
                        f"mqtt_payload:{s.device_bucket}"
                    )
                    or ""
                )
            if not raw:
                try:
                    data = self._mqtt.get_data_from_topic(
                        s.mqtt_data_value or f"{bucket}/DATA", timeout=1,
                    )
                    if data:
                        raw = (
                            data.decode()
                            if isinstance(data, bytes)
                            else str(data)
                        )
                        await self._cache.set(
                            f"mqtt_payload:{bucket}", raw, ttl=60,
                        )
                except Exception as exc:
                    logger.warning(f"MQTT alarm: {exc}")
            if raw:
                cfg = None
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    cfg = json.loads(s.mqtt_status_data_name or "{}")
                for i, v in enumerate(raw.split(",")):
                    k = cfg.get(str(i), str(i)) if cfg else str(i)
                    mqtt_map[k] = v.strip()

        grouped: dict[int, list[dict[str, Any]]] = {
            1: [], 2: [], 3: [], 4: [],
        }
        io_info: list[dict[str, Any]] = []
        arr: list[dict[str, Any]] = []
        base_url = self._base_url()
        for it in items:
            hw = it.hardware_id
            grouped.setdefault(hw, []).append(self._detail(it, mqtt_map))
            rv = (
                mqtt_map.get(it.measurement)
                or mqtt_map.get(it.mqtt_device_name)
                or "0"
            )
            da = 1 if _f(rv) >= 1 else 0
            io_info.append({
                "device_id": it.device_id, "type_id": it.type_id,
                "status": it.status, "device_name": it.device_name,
                "timestamp": _now(), "subject": it.status_warning,
                "value_data": rv, "dataAlarm": da, "eventControl": 1,
                "value_data_msg": rv,
            })
            arr.append(self._build_mqtt_item(it, mqtt_map, lang, base_url))

        check = {
            "isConnected": mqtt_connected, "connected": mqtt_connected,
            "status": 1 if mqtt_connected else 0,
            "msg": (
                "MQTT Connection Status: Connected"
                if mqtt_connected
                else "MQTT Connection Status: Disconnected"
            ),
        }
        mqttrs = {
            "case": 1 if raw else 0, "status": 1 if raw else 0,
            "msg": raw or "No data available",
            "fromCache": False, "time": 0,
            "timestamp": _now(), "isConnected": mqtt_connected,
        }
        return {
            "statuscode": 200, "status": "success",
            "Mqttstatus": 1 if mqtt_connected else 0,
            "payload": {
                "checkConnectionMqtt": check, "mqttrs": mqttrs,
                "mqttname": items[0].mqtt_name if items else "",
                "bucket": bucket, "time": _now(),
                "mqttdata": mqtt_map, "deviceioinfo": io_info,
                "devicesensor": grouped.get(1, []),
                "deviceio": grouped.get(2, []),
                "devicecritical": grouped.get(4, []),
                "cache": "cache",
                "chart": {
                    "bucket": bucket, "field": "value",
                    "data": [], "date": [], "name": "value",
                    "cache": "no cache", "info": {},
                },
                "lang": lang, "page": page, "currentPage": page,
                "pageSize": page_size, "total": len(items),
                "device_count": len(arr), "device": arr,
            },
            "message": "check Connection Status Mqtt",
            "message_th": "check Connection Status Mqtt",
        }

    async def get_alarm_device_status_control(
        self, **kw: Any,
    ) -> dict[str, Any]:
        return await self.get_alarm_device_status(**kw)

    # ═══════════════════════════════════════════════════
    #  MONITOR DEVICE GROUP
    # ═══════════════════════════════════════════════════
    async def get_monitor_device_group(
        self, bucket: str = "", location_id: int = 0,
        hardware_id: int = 0, lang: str = "en", del_cache: int = 0,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, hardware_id=hardware_id, location_id=location_id,
            page=1, page_size=1000,
        )
        items, _ = await self._device_repo.list_with_alarm(f)
        if not items:
            return {"bucket": bucket, "device_count": 0, "data": []}

        s = items[0]
        mqtt_map = await self._fetch_bucket(bucket or s.device_bucket, s)
        names = {
            1: "Sensor", 2: "IO Sensor",
            3: "IO Control", 4: "Critical Sensor",
        }
        groups: dict[int, list[dict[str, Any]]] = {}
        base_url = self._base_url()

        for it in items:
            hw = it.hardware_id
            rv = (
                mqtt_map.get(it.measurement)
                or mqtt_map.get(it.mqtt_device_name)
                or "0"
            )
            v = _f(rv)
            vs = f"{v:.2f}" if hw == 1 else str(rv)
            dto = AlarmDetailDTO(
                hardware_id=hw, value_data=vs, value_alarm=0,
                max_value=it.max_, min_value=it.min_,
                status_alert=it.status_alert,
                status_warning=it.status_warning,
                recovery_warning=it.recovery_warning,
                recovery_alert=it.recovery_alert,
                device_name=it.device_name, action_name=it.mqtt_name,
                mqtt_name=it.mqtt_name,
                mqtt_control_on=it.mqtt_control_on,
                mqtt_control_off=it.mqtt_control_off,
                count_alarm=0, event=1, unit=it.unit,
            )
            a = evaluate_alarm(dto, lang=lang)
            ctrl, dd, ic = "", "", it.icon
            if hw > 1:
                if vs == "1" or vs == it.mqtt_control_on:
                    ctrl = (
                        f"{base_url}/iot/controls?"
                        f"topic={it.mqtt_data_control}"
                        f"&message={it.mqtt_control_on}"
                    )
                    dd, ic = "ON", it.icon_on
                else:
                    ctrl = (
                        f"{base_url}/iot/controls?"
                        f"topic={it.mqtt_data_control}"
                        f"&message={it.mqtt_control_off}"
                    )
                    dd, ic = "OFF", it.icon_off
            else:
                dd = f"{vs} {it.unit}"
            groups.setdefault(hw, []).append({
                "device_id": it.device_id, "device_name": it.device_name,
                "hardware_id": hw, "type_id": it.type_id,
                "type_name": it.type_name,
                "location_name": it.location_name,
                "unit": it.unit, "status": it.status, "layout": it.layout,
                "mqtt_data_value": it.mqtt_data_value,
                "mqtt_data_control": it.mqtt_data_control,
                "measurement": it.measurement,
                "mqtt_control_on": it.mqtt_control_on,
                "mqtt_control_off": it.mqtt_control_off,
                "icon": it.icon, "icon_on": it.icon_on,
                "icon_off": it.icon_off,
                "value_data": vs,
                "alarm_title": a.title, "alarm_subject": a.subject,
                "alarm_status": a.status,
                "control": ctrl, "devicedata": dd, "icon_access": ic,
                "graph": (
                    f"{base_url}/iot/monitordevicechart?"
                    f"bucket={bucket}&measurement={it.measurement}"
                    f"&field=value&start=-5m&stop=now()&limit=120&lang={lang}"
                ),
                "timestamp": _now(), "mqtt_connected": mqtt_connected,
                "cache_used": False,
            })

        layout = items[0].layout if items else 2
        response_groups = [
            {
                "group_id": hw,
                "group_name": names.get(hw, "Unknown"),
                "count": len(devs),
                "devices": devs,
            }
            for hw, devs in groups.items()
        ]
        return {
            "bucket": bucket, "timestamp": _now(),
            "device_count": len(items), "layout": layout,
            "layout_name": "Card",
            "group_name": names.get(hardware_id, ""),
            "device_type": names.get(hardware_id, ""),
            "data": response_groups, "mqtt_connected": mqtt_connected,
            "mqtt_raw_payload": "", "cache_used": False,
        }

    # ═══════════════════════════════════════════════════
    #  DEVICE MQTT
    # ═══════════════════════════════════════════════════
    async def get_device_mqtt(
        self, bucket: str = "", page: int = 1, page_size: int = 10_000_000,
        lang: str = "en", keyword: str = "", device_id: str = "",
        mqtt_id: str = "", type_id: int = 0, hardware_id: int = 0,
        deletecache: int = 0, **_: Any,
    ) -> dict[str, Any]:
        mqtt_connected = self.is_connected()
        f = DeviceListFilter(
            bucket=bucket, page=page, page_size=page_size,
            keyword=keyword, device_id=device_id, mqtt_id=mqtt_id,
            type_id=type_id, hardware_id=hardware_id,
        )
        items, total = await self._device_repo.list_with_alarm(f)
        base_url = self._base_url()
        arr = [self._build_mqtt_item(it, {}, lang, base_url) for it in items]
        return {
            "code": 200,
            "payload": {
                "timestamps": _now(), "lang": lang,
                "page": page, "currentPage": page, "pageSize": page_size,
                "totalPages": (
                    (total + page_size - 1) // page_size
                    if page_size
                    else 1
                ),
                "total": total, "cache": "no cache",
                "device_count": len(arr), "device": arr,
                "connectionMqtt": {
                    "isConnected": mqtt_connected,
                    "connected": mqtt_connected,
                    "status": 1 if mqtt_connected else 0,
                    "msg": (
                        "Connected" if mqtt_connected else "Disconnected"
                    ),
                },
            },
            "message": "OK", "message_th": "OK",
        }

    def _build_mqtt_item(
        self, it: Any, mqtt_map: dict[str, Any],
        lang: str, base_url: str,
    ) -> dict[str, Any]:
        rv = (
            mqtt_map.get(it.measurement)
            or mqtt_map.get(it.mqtt_device_name)
            or "0"
        )
        v = _f(rv)
        if it.hardware_id == 1:
            if it.calibration_type == 1:
                v += _f(it.calibration_add)
            elif it.calibration_type == 2:
                v -= _f(it.calibration_subtract)
            vs = f"{v:.2f}"
        else:
            vs = str(rv)
        ctrl: Any = ""
        dd, ic = "", it.icon
        if it.hardware_id > 1:
            if vs == "1" or vs == it.mqtt_control_on:
                dd, ic = "ON", it.icon_on
                ctrl = (
                    f"{base_url}/iot/controls?"
                    f"topic={it.mqtt_data_control}"
                    f"&message={it.mqtt_control_on}"
                )
            else:
                dd, ic = "OFF", it.icon_off
                ctrl = (
                    f"{base_url}/iot/controls?"
                    f"topic={it.mqtt_data_control}"
                    f"&message={it.mqtt_control_off}"
                )
        else:
            dd = f"{vs} {it.unit}"
        dto = AlarmDetailDTO(
            hardware_id=it.hardware_id, value_data=vs, value_alarm=0,
            max_value=it.max_, min_value=it.min_,
            status_alert=it.status_alert,
            status_warning=it.status_warning,
            recovery_warning=it.recovery_warning,
            recovery_alert=it.recovery_alert,
            device_name=it.device_name, action_name=it.mqtt_name,
            mqtt_name=it.mqtt_name,
            mqtt_control_on=it.mqtt_control_on,
            mqtt_control_off=it.mqtt_control_off,
            count_alarm=0, event=1, unit=it.unit,
        )
        a = evaluate_alarm(dto, lang=lang)
        return {
            "device_id": it.device_id, "tiime": _now(),
            "system_name": it.location_name,
            "location_name": it.mqtt_name,
            "zone_name": it.type_name, "device_name": it.device_name,
            "hardware_type": it.hardware_type_name,
            "bucket": it.mqtt_bucket,
            "measurement": it.measurement,
            "sensor_type": it.hardware_type_name,
            "devicedata": dd, "alarm_title": a.title,
            "alarm_detail": a.subject,
            "notification_status": a.alarm_status_set,
            "notification_alarm_status": a.status,
            "mqtt_data": it.mqtt_data_value,
            "mqtt_control": it.mqtt_data_control,
            "control": ctrl,
            "sensercharts": (
                f"{base_url}/iot/sensercharts?"
                f"bucket={it.mqtt_bucket}&measurement={it.measurement}"
            ),
            "from": "mqtt", "ttl": 60, "cachelift": "no cache",
            "hardware_id": it.hardware_id, "type_id": it.type_id,
            "mqtt_id": it.mqtt_id, "type_name": it.type_name,
            "unit": it.unit, "status": it.status, "value_data": vs,
            "icon_access": ic, "alarm_subject": a.subject,
            "alarm_status": a.status,
        }

    # ═══════════════════════════════════════════════════
    #  PART 8 + 10 + 12 — PROCESS MQTT DATA
    # ═══════════════════════════════════════════════════
    async def process_mqtt_data(
        self, device_id: str, raw_data: str,
    ) -> dict[str, Any]:
        """
        TH: รับข้อมูล MQTT → parse → cache → save → alarm → broadcast
        EN: process MQTT: parse → cache → save → alarm → broadcast
        """
        device = await self._device_repo.find_by_id(int(device_id))
        cfg: dict[str, str] | None = None
        if device and device.mqtt_status_data_name:
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                cfg = json.loads(device.mqtt_status_data_name)
        dm = _build_map(raw_data, cfg)

        # ─── Save to iot_data (throttled 1 min/device) ───
        if await self._should_save(device_id):
            # ═══ Part 12: Resolve + validate tenant_id ═══
            _tid_raw = _resolve_tenant_id(device)
            _tid: _uuid.UUID | None = None
            if _tid_raw:
                try:
                    _tid = _uuid.UUID(str(_tid_raw))
                except (ValueError, TypeError, AttributeError):
                    logger.warning(
                        "process_mqtt_data.invalid_tenant_id",
                        raw=str(_tid_raw), device_id=device_id,
                    )

            has_tenant_field = hasattr(IotData, "tenant_id")
            if has_tenant_field and _tid is None:
                logger.error(
                    "process_mqtt_data.missing_tenant_id",
                    device_id=device_id,
                )

            _kwargs: dict[str, Any] = {
                "device_id": str(device_id),
                "data": dm,
                "timestamp": datetime.now(UTC),
            }
            if has_tenant_field:
                _kwargs["tenant_id"] = _tid
            _iot_data = IotData(**_kwargs)
            await self._iot_data_repo.create(_iot_data)

        # ─── Cache ───
        await self._cache.set(f"iot_data:latest:{device_id}", dm, ttl=300)
        await self._cache.lpush_trim("iot_data:recent", dm, 100, 300)

        # ─── Update device status ───
        with contextlib.suppress(Exception):
            await self._device_status_repo.update_last_seen(str(device_id))

        # ─── Activity log ───
        with contextlib.suppress(Exception):
            await self._activity_log_repo.create(
                ActivityLog(
                    type="DATA_RECEIVED", device_id=str(device_id),
                    details=f"Received data from {device_id}",
                    data=dm, severity="info",
                )
            )

        # ─── Influx + Alarm + WS + Alerting ───
        if device is not None:
            # Write to InfluxDB
            await self._write_influx(device, dm)

            # Evaluate alarm
            try:
                measurement = device.measurement or ""
                raw_val = (
                    dm.get(measurement)
                    or dm.get(device.mqtt_device_name or "")
                    or "0"
                )
                v = _f(raw_val)
                vs = (
                    f"{v:.2f}"
                    if device.hardware_id == 1
                    else str(raw_val)
                )

                dto = AlarmDetailDTO(
                    hardware_id=device.hardware_id,
                    value_data=vs, value_alarm=0,
                    max_value=device.max_, min_value=device.min_,
                    status_alert=device.status_alert,
                    status_warning=device.status_warning,
                    recovery_warning=device.recovery_warning,
                    recovery_alert=device.recovery_alert,
                    device_name=device.device_name,
                    action_name=device.mqtt_name,
                    mqtt_name=device.mqtt_name,
                    mqtt_control_on=device.mqtt_control_on,
                    mqtt_control_off=device.mqtt_control_off,
                    count_alarm=0, event=1,
                    unit=device.unit or "",
                )
                alarm_result = evaluate_alarm(dto, lang="en")

                # ═══ Part 8: Broadcast alarm ═══
                if alarm_result.status in (1, 2):
                    await ws_broadcaster.alarm_triggered(
                        device_id=device.device_id,
                        device_name=device.device_name,
                        alarm_status=alarm_result.status,
                        title=alarm_result.title,
                        subject=alarm_result.subject,
                        value=v,
                        unit=device.unit or "",
                    )

                    # ═══ Part 10: Multi-channel alerting (non-blocking) ═══
                    try:
                        from app.modules.iot.infrastructure.alerting.base import (  # noqa: E501
                            AlertMessage,
                        )
                        from app.modules.iot.infrastructure.alerting.dispatcher import (  # noqa: E501
                            alert_dispatcher,
                        )

                        msg = AlertMessage(
                            device_id=device.device_id,
                            device_name=device.device_name,
                            alarm_status=alarm_result.status,
                            title=alarm_result.title,
                            subject=alarm_result.subject,
                            content=alarm_result.content,
                            value_data=v,
                            unit=device.unit or "",
                            severity=(
                                "critical"
                                if alarm_result.status == 2
                                else "medium"
                            ),
                        )
                        # keep strong ref via _spawn
                        _spawn(alert_dispatcher.send(msg))
                    except Exception as exc:
                        logger.warning(
                            f"alerting dispatch failed: {exc}"
                        )

                # ═══ Part 8: Broadcast data ═══
                await ws_broadcaster.data_received(device.device_id, dm)

            except Exception as exc:
                logger.warning(
                    f"process_mqtt_data broadcast failed: {exc}"
                )

        return {"device_id": device_id, "data": dm, "timestamp": _now()}

    async def _should_save(self, device_id: str) -> bool:
        key = f"iot_last_save:{device_id}"
        now = datetime.now(UTC)
        raw = await self._cache.get_raw(key)
        if raw:
            with contextlib.suppress(ValueError):
                last = datetime.fromisoformat(raw)
                if (now - last).total_seconds() < 60:
                    return False
        await self._cache.set(key, now.isoformat(), ttl=60)
        return True

    async def _write_influx(
        self, device: Any, dm: dict[str, Any],
    ) -> None:
        if self._influx is None:
            return
        v, ok = _extract(
            dm, device.measurement or "", device.mqtt_device_name or "",
        )
        if not ok:
            return
        bucket = device.bucket or ""
        meas = (
            device.measurement
            or device.mqtt_device_name
            or device.device_name
        )
        if not bucket or not meas:
            return
        try:
            self._influx.write_point_to_bucket(
                bucket, meas,
                {
                    "device_id": str(device.device_id),
                    "device_name": device.device_name,
                },
                {"value": v}, datetime.now(UTC),
            )
        except Exception as exc:
            logger.warning(f"Influx write: {exc}")

    # ═══════════════════════════════════════════════════
    #  DEVICE STATUS
    # ═══════════════════════════════════════════════════
    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        st = await self._device_status_repo.find_by_device_id(device_id)
        if st is None:
            return {
                "deviceId": device_id, "isOnline": False, "isActive": True,
                "lastSeen": _now(), "uptime": "0s",
            }
        online = False
        if st.last_seen:
            online = (
                datetime.now(UTC) - st.last_seen
            ).total_seconds() < 900
        return {
            "deviceId": st.device_id, "isOnline": online,
            "isActive": st.is_active,
            "lastSeen": st.last_seen.isoformat() if st.last_seen else "",
            "batteryLevel": st.battery_level,
            "signalStrength": st.signal_strength,
            "firmwareVersion": st.firmware_version,
            "location": st.location, "lastData": st.last_data,
            "uptime": "0s",
        }

    async def update_device_status(
        self, device_id: str, data: dict[str, Any],
    ) -> bool:
        st = await self._device_status_repo.find_by_device_id(device_id)
        if st is None:
            st = DeviceStatus(device_id=device_id)
        st.last_seen = datetime.now(UTC)
        st.is_online = True
        st.last_data = data
        with contextlib.suppress(Exception):
            b = data.get("battery")
            if b is not None:
                st.battery_level = int(float(b))
            s = data.get("signal")
            if s is not None:
                st.signal_strength = int(float(s))
            fw = data.get("firmware")
            if fw:
                st.firmware_version = str(fw)
            loc = data.get("location")
            if loc:
                st.location = loc
        await self._device_status_repo.upsert(st)
        return True

    # ═══════════════════════════════════════════════════
    #  DEVICE CONFIG
    # ═══════════════════════════════════════════════════
    async def get_device_config(self, device_id: str) -> dict[str, Any]:
        cfg = await self._device_config_repo.find_by_device_id(device_id)
        if cfg is None:
            return {
                "deviceId": device_id,
                "config": {
                    "general": {
                        "deviceName": "", "timezone": "Asia/Bangkok",
                    },
                    "reporting": {
                        "enabled": True, "interval": 300,
                        "format": "json",
                    },
                    "thresholds": {
                        "temperature": {"min": 15, "max": 40},
                        "humidity": {"min": 30, "max": 80},
                    },
                    "alerts": {"enabled": True, "email": [], "sms": []},
                },
                "status": "active",
            }
        return {
            "deviceId": cfg.device_id,
            "config": cfg.config or {},
            "status": cfg.status,
        }

    async def update_device_config(
        self, device_id: str, config: dict[str, Any],
    ) -> bool:
        cfg = await self._device_config_repo.find_by_device_id(device_id)
        if cfg is None:
            cfg = DeviceConfig(device_id=device_id, config=config)
        else:
            m = dict(cfg.config or {})
            m.update(config)
            cfg.config = m
        await self._device_config_repo.upsert(cfg)
        return True

    # ═══════════════════════════════════════════════════
    #  IOT DATA LIST / STATS / EXPORT
    # ═══════════════════════════════════════════════════
    async def list_iot_data(
        self, device_id: str, page: int = 1, limit: int = 50,
        start_date: str = "", end_date: str = "",
    ) -> dict[str, Any]:
        items, total = await self._iot_data_repo.find_paginated(
            device_id, page, limit,
        )
        pages = (total + limit - 1) // limit if limit else 0
        return {
            "data": [
                {
                    "id": i.id, "device_id": i.device_id, "data": i.data,
                    "timestamp": (
                        i.timestamp.isoformat() if i.timestamp else ""
                    ),
                }
                for i in items
            ],
            "pagination": {
                "page": page, "limit": limit,
                "total": total, "pages": pages,
            },
        }

    async def get_device_stats(self, device_id: str) -> dict[str, Any]:
        items = await self._iot_data_repo.find_latest(device_id, limit=1000)
        s: dict[str, Any] = {"count": len(items)}
        if items:
            s["lastRecord"] = (
                items[0].timestamp.isoformat()
                if items[0].timestamp
                else None
            )
            s["firstRecord"] = (
                items[-1].timestamp.isoformat()
                if items[-1].timestamp
                else None
            )
        return s

    async def export_data(
        self, device_id: str, start_date: datetime,
        end_date: datetime, export_format: str = "json",
    ) -> tuple[bytes, str]:
        items = await self._iot_data_repo.find_by_date_range(
            device_id, start_date, end_date,
        )
        if export_format == "csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["timestamp", "device_id", "data"])
            for i in items:
                w.writerow([
                    i.timestamp.isoformat() if i.timestamp else "",
                    i.device_id,
                    json.dumps(i.data, default=str),
                ])
            return buf.getvalue().encode(), "text/csv"
        payload = [
            {
                "id": i.id, "device_id": i.device_id, "data": i.data,
                "timestamp": i.timestamp.isoformat() if i.timestamp else "",
            }
            for i in items
        ]
        return (
            json.dumps(payload, default=str).encode(),
            "application/json",
        )

    async def cleanup_old_data(self, days: int = 30) -> int:
        return await self._iot_data_repo.cleanup_old(days)

    # ═══════════════════════════════════════════════════
    #  INGESTER
    # ═══════════════════════════════════════════════════
    async def start_ingest(self) -> bool:
        if not self.is_connected():
            return False

        def _handler(client: Any, msg: Any) -> None:
            topic = getattr(msg, "topic", "")
            payload = getattr(msg, "payload", b"")
            if isinstance(payload, bytes):
                payload = payload.decode(errors="replace")
            bucket = _bucket_from_topic(topic)
            if not bucket:
                return
            _spawn(self._handle_ingest(bucket, str(payload)))

        try:
            self._mqtt.subscribe("#", qos=0)
            return True
        except Exception as exc:
            logger.error(f"ingest subscribe: {exc}")
            return False

    async def _handle_ingest(self, bucket: str, payload: str) -> None:
        try:
            for d in await self._device_repo.find_by_bucket(bucket):
                await self.process_mqtt_data(str(d.device_id), payload)
        except Exception as exc:
            logger.error(f"ingest {bucket}: {exc}")


iotUseCase = IotUseCase
