from __future__ import annotations

import contextlib
import csv
import io
import json
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from app.core.influxdb_client import InfluxDBClientWrapper, QueryParams
from app.modules.iot.domain.entities.device import Device
from app.modules.iot.domain.entities.iot_data import IoTData
from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO
from app.modules.iot.infrastructure.activity_log_repository import ActivityLogRepository
from app.modules.iot.infrastructure.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.device_repository import DeviceRepository
from app.modules.iot.infrastructure.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.iot_data_repository import IoTDataRepository

MQTTClient = Any
RedisClient = Any


class IoTUseCase:
    """IoT use cases - translated from Go: internal/modules/iot/usecase/usecase.go"""

    def __init__(
        self,
        device_repository: DeviceRepository,
        device_config_repository: DeviceConfigRepository,
        device_status_repository: DeviceStatusRepository,
        device_alert_repository: DeviceAlertRepository,
        iot_data_repository: IoTDataRepository,
        alarm_log_repository: AlarmLogRepository,
        activity_log_repository: ActivityLogRepository,
        mqtt_client: MQTTClient | None = None,
        influxdb_client: InfluxDBClientWrapper | None = None,
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
        self, topic: str, del_cache: bool = False
    ) -> dict[str, Any]:
        cache_key = f"mqtt_topic:{topic}"
        cache_enabled = self.is_cache_enabled()

        if cache_enabled and del_cache:
            try:
                self._redis_client.delete(cache_key)
                logger.info(f"GetTopicData: cache deleted for topic {topic}")
            except Exception as exc:
                logger.warning(
                    f"GetTopicData: failed to delete cache for topic {topic}: {exc}"
                )

        if cache_enabled and not del_cache:
            try:
                cached = self._redis_client.get(cache_key)
                if cached:
                    logger.debug(f"GetTopicData: cache HIT for topic {topic}")
                    payload = json.loads(cached) if isinstance(cached, (str, bytes)) else cached
                    return {
                        "topic": topic,
                        "payload": payload,
                        "from": "cache",
                        "cache": True,
                    }
            except Exception:
                pass
            logger.debug(f"GetTopicData: cache MISS for topic {topic}")

        if self._mqtt_client is None or not self._mqtt_client.is_connected():
            return {"topic": topic, "payload": None, "from": "mqtt_disconnected", "cache": False}

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
                return {"topic": topic, "payload": payload, "from": "mqtt", "cache": False}
        except Exception as exc:
            logger.warning(f"GetTopicData: MQTT fetch failed for topic {topic}: {exc}")

        if cache_enabled:
            try:
                cached = self._redis_client.get(cache_key)
                if cached:
                    payload = json.loads(cached) if isinstance(cached, (str, bytes)) else cached
                    return {
                        "topic": topic,
                        "payload": payload,
                        "from": "cache_fallback",
                        "cache": True,
                    }
            except Exception:
                pass

        return {"topic": topic, "payload": None, "from": "mqtt_error", "cache": False}

    async def device_control(self, topic: str, message: str) -> bool:
        if self._mqtt_client is None or not self._mqtt_client.is_connected():
            return False
        return self._mqtt_client.publish(topic, message, qos=1)

    async def device_controls(self, topic: str, message: str) -> bool:
        return await self.device_control(topic, message)

    async def get_device_list(
        self, bucket: str = "", hardware_id: int = 0, page: int = 1, page_size: int = 20
    ) -> tuple[list[Device], int]:
        return await self._device_repo.find_all_paginated(page, page_size)

    async def get_device_list_page(
        self, bucket: str = "", hardware_id: int = 0, page: int = 1, page_size: int = 20
    ) -> tuple[list[Device], int]:
        return await self.get_device_list(bucket, hardware_id, page, page_size)

    async def get_device_list_by_location(self, location_id: int) -> list[Device]:
        return await self._device_repo.find_by_location(location_id)

    async def get_senser_charts(
        self,
        measurement: str = "temperature",
        field: str = "value",
        bucket: str = "iot_sensors",
        start: str = "-1h",
        stop: str = "now()",
        limit: int = 1000,
    ) -> dict[str, Any]:
        if self._influxdb_client is None:
            return {"data": [], "date": [], "cache": "no cache"}

        params = QueryParams(
            measurement=measurement,
            field=field,
            bucket=bucket,
            start=start,
            stop=stop,
            limit=limit,
        )
        try:
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
            logger.error(f"GetSenserCharts: InfluxDB query failed: {exc}")
            return {"data": [], "date": [], "cache": "error", "error": str(exc)}

    async def get_senser_data_chart(self, **kwargs: Any) -> dict[str, Any]:
        return await self.get_senser_charts(**kwargs)

    async def get_senser_data(self, **kwargs: Any) -> dict[str, Any]:
        return await self.get_senser_charts(**kwargs)

    async def get_device_senser_charts(self, **kwargs: Any) -> dict[str, Any]:
        return await self.get_senser_charts(**kwargs)

    async def get_alarm_device_status(
        self,
        bucket: str = "iot_sensors",
        page: int = 1,
        page_size: int = 1000,
        measurement: str = "temperature",
        **filters: Any,
    ) -> dict[str, Any]:
        from datetime import timedelta

        mqtt_connected = self.is_connected()
        check_connection_mqtt = {
            "isConnected": mqtt_connected,
            "connected": mqtt_connected,
            "status": 1 if mqtt_connected else 0,
            "msg": (
                "MQTT Connection Status: Connected"
                if mqtt_connected
                else "MQTT Connection Status: Disconnected"
            ),
        }

        devices = await self._device_repo.find_all_active()
        device_sensors = [d for d in devices if d.hardware_id == 1]
        device_io = [d for d in devices if d.hardware_id == 2]

        device_io_info = []
        for dev in devices:
            device_io_info.append({
                "device_id": str(dev.id),
                "type_id": dev.type_id,
                "status": dev.status,
                "device_name": dev.device_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "subject": "",
                "value_data": 0,
                "data_alarm": 0,
                "event_control": 1,
                "value_data_msg": "",
            })

        mqtt_data: dict[str, Any] = {}
        mqttrs: dict[str, Any] = {
            "case": 0,
            "status": 0,
            "msg": "No data available",
            "fromCache": False,
            "time": 0,
            "timestamp": datetime.now(UTC).isoformat(),
            "isConnected": mqtt_connected,
        }

        if mqtt_connected and devices:
            first_dev = devices[0]
            topic = first_dev.mqtt_topic or f"{bucket}/DATA"
            try:
                payload = self._mqtt_client.get_data_from_topic(topic, timeout=5)
                if payload:
                    parts = str(payload).split(",")
                    for i, val in enumerate(parts):
                        key = str(i)
                        trimmed = val.strip()
                        try:
                            mqtt_data[key] = float(trimmed)
                        except ValueError:
                            mqtt_data[key] = trimmed
                    mqttrs = {
                        "case": 1,
                        "status": 1,
                        "msg": str(payload),
                        "fromCache": False,
                        "time": 0,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "isConnected": mqtt_connected,
                    }
            except Exception as exc:
                logger.warning(f"GetAlarmDeviceStatus: MQTT fetch failed: {exc}")

        chart_data: dict[str, Any] = {
            "bucket": bucket,
            "field": "value",
            "info": {},
            "data": [],
            "date": [],
            "name": "value",
            "cache": "no cache",
        }

        if self._influxdb_client:
            now = datetime.now(UTC)
            start = (now - timedelta(minutes=15)).isoformat()
            stop = now.isoformat()
            params = QueryParams(
                measurement=measurement,
                field="value",
                bucket=bucket,
                start=start,
                stop=stop,
                limit=150,
            )
            try:
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
                    "bucket": bucket,
                    "measurement": measurement,
                    "result": "last",
                    "table": 0,
                    "field": "value",
                    "start": start,
                    "stop": stop,
                    "time": datetime.now(UTC).isoformat(),
                    "value": data_points[-1] if data_points else None,
                }
            except Exception as exc:
                logger.warning(f"GetAlarmDeviceStatus: InfluxDB query failed: {exc}")

        def _to_dict_list(devs: list[Device]) -> list[dict[str, Any]]:
            return [
                {
                    "device_id": str(d.id),
                    "device_name": d.device_name,
                    "hardware_id": d.hardware_id,
                    "type_id": d.type_id,
                    "unit": d.unit,
                    "status": d.status,
                }
                for d in devs
            ]

        return {
            "statuscode": 200,
            "status": "success",
            "Mqttstatus": 1 if mqtt_connected else 0,
            "payload": {
                "checkConnectionMqtt": check_connection_mqtt,
                "mqttrs": mqttrs,
                "mqttname": "",
                "bucket": bucket,
                "time": datetime.now(UTC).isoformat(),
                "mqttdata": mqtt_data,
                "deviceioinfo": device_io_info,
                "devicesensor": _to_dict_list(device_sensors),
                "deviceio": _to_dict_list(device_io),
                "cache": "cache",
                "chart": chart_data,
            },
            "message": "check Connection Status Mqtt",
            "message_th": "check Connection Status Mqtt",
        }

    async def get_alarm_device_status_control(
        self, bucket: str = "iot_sensors", **filters: Any
    ) -> dict[str, Any]:
        return await self.get_alarm_device_status(bucket=bucket, **filters)

    async def get_monitor_device_group(
        self,
        bucket: str = "iot_sensors",
        location_id: int = 0,
        hardware_id: int = 0,
        lang: str = "en",
        del_cache: int = 0,
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
                    logger.warning(f"GetMonitorDeviceGroup: MQTT fetch failed: {exc}")

            if mqtt_raw_payload:
                parts = mqtt_raw_payload.split(",")
                for i, val in enumerate(parts):
                    key = str(i)
                    mqtt_data_map[key] = val.strip()

        enriched_devices = []
        group_names = {1: "Sensor", 2: "IO Sensor", 3: "IO Control", 4: "Critical Sensor"}

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
                hardware_id=dev.hardware_id,
                value_data=value_data_str,
                value_alarm=0,
                max_value=0,
                min_value=0,
                status_alert=0,
                status_warning=0,
                recovery_warning=0,
                recovery_alert=0,
                device_name=dev.device_name,
                action_name=dev.mqtt_name,
                mqtt_name=dev.mqtt_name,
                mqtt_control_on="",
                mqtt_control_off="",
                count_alarm=0,
                event=1,
                unit=dev.unit,
            )
            alarm_result = evaluate_alarm(alarm_dto, lang=lang)

            control_url = ""
            device_data = ""
            icon_access = dev.icon

            if dev.hardware_id > 1:
                if value_data_float >= 1:
                    device_data = "OFF"
                    icon_access = ""
                else:
                    device_data = "ON"
                    icon_access = ""
            else:
                device_data = f"{value_data_str} {dev.unit}"

            enriched_devices.append({
                "device_id": str(dev.id),
                "device_name": dev.device_name,
                "hardware_id": dev.hardware_id,
                "type_id": dev.type_id,
                "type_name": "",
                "location_name": dev.location_name,
                "unit": dev.unit,
                "status": dev.status,
                "value_data": value_data_str,
                "alarm_title": alarm_result.title,
                "alarm_subject": alarm_result.subject,
                "alarm_status": alarm_result.status,
                "control": control_url,
                "devicedata": device_data,
                "icon_access": icon_access,
                "timestamp": datetime.now(UTC).isoformat(),
                "mqtt_connected": mqtt_connected,
            })

        groups: dict[int, list[dict[str, Any]]] = {}
        for ed in enriched_devices:
            hw_id = ed["hardware_id"]
            groups.setdefault(hw_id, []).append(ed)

        response_groups = []
        for hw_id, devs in groups.items():
            response_groups.append({
                "group_id": hw_id,
                "group_name": group_names.get(hw_id, "Unknown"),
                "count": len(devs),
                "devices": devs,
            })

        layout = enriched_devices[0].get("layout", 2) if enriched_devices else 2

        return {
            "bucket": bucket,
            "timestamp": datetime.now(UTC).isoformat(),
            "device_count": len(enriched_devices),
            "layout": layout,
            "layout_name": "Card",
            "group_name": group_names.get(hardware_id, ""),
            "device_type": group_names.get(hardware_id, ""),
            "data": response_groups,
            "mqtt_connected": mqtt_connected,
            "mqtt_raw_payload": mqtt_raw_payload,
            "cache_used": False,
        }

    async def get_monitor_device_chart(
        self,
        bucket: str = "iot_sensors",
        measurement: str = "temperature",
        field: str = "value",
        start: str = "-10m",
        stop: str = "now()",
        limit: int = 100,
    ) -> dict[str, Any]:
        if self._influxdb_client is None:
            return {"data": [], "date": [], "cache": "no cache"}

        params = QueryParams(
            measurement=measurement,
            field=field,
            bucket=bucket,
            start=start,
            stop=stop,
            limit=limit,
        )
        try:
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
            logger.error(f"GetMonitorDeviceChart: InfluxDB query failed: {exc}")
            return {"data": [], "date": [], "cache": "error", "error": str(exc)}

    async def get_topic_data_device_chart(
        self,
        bucket: str = "iot_sensors",
        topic: str = "",
        measurement: str = "temperature",
        field: str = "value",
        start: str = "-10m",
        stop: str = "now()",
        limit: int = 100,
    ) -> dict[str, Any]:
        topic = topic or f"{bucket}/DATA"

        chart_response = await self.get_monitor_device_chart(
            bucket=bucket,
            measurement=measurement,
            field=field,
            start=start,
            stop=stop,
            limit=limit,
        )

        mqtt_payload = None
        mqtt_from = ""

        if self._redis_client:
            try:
                cached = self._redis_client.get(f"mqtt_topic:{topic}")
                if cached:
                    mqtt_payload = (
                        json.loads(cached) if isinstance(cached, (str, bytes)) else cached
                    )
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
                logger.warning(f"GetTopicDataDeviceChart: MQTT fetch failed: {exc}")

        return {
            "topic": topic,
            "chart": chart_response,
            "latest_payload": mqtt_payload,
            "latest_from": mqtt_from,
            "cache": "cache" if mqtt_from == "cache" else "no cache",
        }

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        return {
            "device_id": device_id,
            "is_online": False,
            "is_active": True,
            "last_seen": datetime.now(UTC).isoformat(),
            "battery_level": None,
            "signal_strength": None,
            "firmware_version": None,
            "location": None,
            "last_data": None,
            "uptime": "0s",
        }

    async def update_device_status(self, device_id: str, data: dict[str, Any]) -> bool:
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
        self, device_id: str, config: dict[str, Any]
    ) -> bool:
        logger.info(f"UpdateDeviceConfig: device_id={device_id}")
        return True

    async def process_mqtt_data(
        self, device_id: str, raw_data: str
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

        iot_data = IoTData(device_id=int(device_id), data_json=json.dumps(data_map))
        await self._iot_data_repo.create(iot_data)

        return {
            "device_id": device_id,
            "data": data_map,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_latest_data(
        self, device_id: str, limit: int = 10
    ) -> list[IoTData]:
        return await self._iot_data_repo.find_latest(int(device_id), limit)

    async def get_data_by_date_range(
        self, device_id: str, start: str, end: str
    ) -> list[IoTData]:
        return await self._iot_data_repo.find_by_date_range(
            int(device_id), start, end
        )

    async def list_iot_data(
        self,
        device_id: str = "",
        page: int = 1,
        limit: int = 50,
    ) -> dict[str, Any]:
        if limit <= 0:
            limit = 50
        if page <= 0:
            page = 1

        items, total = await self._iot_data_repo.find_paginated(page, limit)
        pages = (total + limit - 1) // limit

        return {
            "data": [
                {
                    "id": str(item.id),
                    "device_id": item.device_id,
                    "data": item.data_json,
                    "timestamp": item.created_at.isoformat() if item.created_at else "",
                }
                for item in items
            ],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": pages,
            },
        }

    async def get_device_stats(self, device_id: str) -> dict[str, Any]:
        data = await self._iot_data_repo.find_latest(int(device_id), 1000)
        stats: dict[str, Any] = {"count": len(data)}
        if data:
            stats["last_record"] = data[0].created_at.isoformat() if data[0].created_at else None
            stats["first_record"] = (
                data[-1].created_at.isoformat() if data[-1].created_at else None
            )
        return stats

    async def export_data(
        self,
        device_id: str = "",
        start_date: str = "",
        end_date: str = "",
        export_format: str = "json",
    ) -> tuple[str, str]:
        import datetime as dt

        if not start_date or not end_date:
            now = datetime.now(UTC)
            end_date = now.isoformat()
            start_date = (now - dt.timedelta(days=7)).isoformat()

        data = await self._iot_data_repo.find_by_date_range(
            int(device_id) if device_id else 0, start_date, end_date
        )

        if export_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp", "device_id", "data"])
            for d in data:
                writer.writerow([
                    d.created_at.isoformat() if d.created_at else "",
                    d.device_id,
                    d.data_json,
                ])
            return output.getvalue(), "text/csv"

        json_data = json.dumps(
            [
                {
                    "id": str(d.id),
                    "device_id": d.device_id,
                    "data": d.data_json,
                    "timestamp": d.created_at.isoformat() if d.created_at else "",
                }
                for d in data
            ],
            default=str,
        )
        return json_data, "application/json"

    async def cleanup_old_data(self, days: int = 90) -> int:
        return await self._iot_data_repo.cleanup_old(days)
