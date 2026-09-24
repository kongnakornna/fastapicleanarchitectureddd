"""iot DI container"""
from __future__ import annotations
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.iot.application.use_case import IotUseCase
from app.modules.iot.infrastructure.repositories import (
    ActivityLogRepository, AlarmLogRepository, CommandLogRepository,
    DeviceAlertRepository, DeviceConfigRepository, DeviceRepository,
    DeviceStatusRepository, IotDataRepository,
)

_mqtt: Any | None = None
_influx: Any | None = None
_redis: Any | None = None


def _get_mqtt() -> Any | None:
    global _mqtt
    if _mqtt is None:
        try:
            from app.core.mqtt_client import MQTTClient
            from app.core.settings import settings
            _mqtt = MQTTClient(
                broker=settings.MQTT_BROKER,
                client_id=getattr(settings, "MQTT_CLIENT_ID", ""),
                username=getattr(settings, "MQTT_USERNAME", ""),
                password=getattr(settings, "MQTT_PASSWORD", ""),
                keepalive=getattr(settings, "MQTT_KEEPALIVE", 30),
            )
            _mqtt.connect()
        except Exception:
            return None
    return _mqtt


def _get_influx() -> Any | None:
    global _influx
    if _influx is None:
        try:
            from app.core.influxdb_client import InfluxDBClientWrapper
            from app.core.settings import settings
            _influx = InfluxDBClientWrapper(
                url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG, bucket=settings.INFLUXDB_BUCKET,
                timeout=getattr(settings, "INFLUXDB_TIMEOUT", 30),
            )
        except Exception:
            return None
    return _influx


def _get_redis() -> Any | None:
    global _redis
    if _redis is None:
        try:
            import redis
            from app.core.settings import settings
            _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            return None
    return _redis


async def get_iot_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> IotUseCase:
    return IotUseCase(
        device_repository=DeviceRepository(session),
        device_config_repository=DeviceConfigRepository(session),
        device_status_repository=DeviceStatusRepository(session),
        device_alert_repository=DeviceAlertRepository(session),
        iot_data_repository=IotDataRepository(session),
        alarm_log_repository=AlarmLogRepository(session),
        activity_log_repository=ActivityLogRepository(session),
        command_log_repository=CommandLogRepository(session),
        mqtt_client=_get_mqtt(),
        influxdb_client=_get_influx(),
        redis_client=_get_redis(),
    )
