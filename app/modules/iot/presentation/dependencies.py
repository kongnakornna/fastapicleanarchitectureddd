from __future__ import annotations

from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.influxdb_client import InfluxDBClientWrapper
from app.core.mqtt_client import MQTTClient
from app.core.settings import settings
from app.modules.iot.application.use_case import IoTUseCase
from app.modules.iot.infrastructure.activity_log_repository import ActivityLogRepository
from app.modules.iot.infrastructure.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.device_repository import DeviceRepository
from app.modules.iot.infrastructure.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.iot_data_repository import IoTDataRepository

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
) -> IoTUseCase:
    mqtt_client = _get_mqtt_client()
    influxdb_client = _get_influxdb_client()
    redis_client = _get_redis_client()

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
