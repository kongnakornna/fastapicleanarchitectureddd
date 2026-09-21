from unittest.mock import AsyncMock, Mock

import pytest

from app.core.influxdb_client import InfluxDBClientWrapper
from app.modules.iot.application.use_case import IoTUseCase
from app.modules.iot.domain.entities.device import Device
from app.modules.iot.domain.entities.iot_data import IoTData


def _make_device(**overrides):
    defaults = {
        "hardware_id": 1,
        "type_id": 1,
        "location_id": 1,
        "device_sn": "SN001",
        "device_name": "Test Device",
        "device_type": "sensor",
        "location_name": "Bangkok",
        "mqtt_id": 1,
        "mqtt_main_id": 1,
        "mqtt_topic": "iot/test",
        "mqtt_name": "mqtt_test",
        "mqtt_username": "user",
        "mqtt_password": "pass",
        "unit": "°C",
        "status": "online",
        "icon": "thermometer",
        "icon_color": "#FF0000",
        "description": "Test",
        "firmware_version": "1.0.0",
    }
    defaults.update(overrides)
    return Device(**defaults)


def _make_iot_data(**overrides):
    defaults = {
        "device_id": 1,
        "data_json": '{"temp": 25.5}',
        "location_id": 1,
        "metadata_json": "{}",
    }
    defaults.update(overrides)
    return IoTData(**defaults)


@pytest.fixture
def device_repo():
    return Mock()


@pytest.fixture
def device_config_repo():
    return Mock()


@pytest.fixture
def device_status_repo():
    return Mock()


@pytest.fixture
def device_alert_repo():
    return Mock()


@pytest.fixture
def iot_data_repo():
    return Mock()


@pytest.fixture
def alarm_log_repo():
    return Mock()


@pytest.fixture
def activity_log_repo():
    return Mock()


@pytest.fixture
def usecase(
    device_repo, device_config_repo, device_status_repo, device_alert_repo,
    iot_data_repo, alarm_log_repo, activity_log_repo,
):
    return IoTUseCase(
        device_repository=device_repo,
        device_config_repository=device_config_repo,
        device_status_repository=device_status_repo,
        device_alert_repository=device_alert_repo,
        iot_data_repository=iot_data_repo,
        alarm_log_repository=alarm_log_repo,
        activity_log_repository=activity_log_repo,
    )


@pytest.fixture
def usecase_with_mqtt(
    device_repo, device_config_repo, device_status_repo, device_alert_repo,
    iot_data_repo, alarm_log_repo, activity_log_repo,
):
    mqtt = Mock()
    mqtt.is_connected.return_value = True
    return IoTUseCase(
        device_repository=device_repo,
        device_config_repository=device_config_repo,
        device_status_repository=device_status_repo,
        device_alert_repository=device_alert_repo,
        iot_data_repository=iot_data_repo,
        alarm_log_repository=alarm_log_repo,
        activity_log_repository=activity_log_repo,
        mqtt_client=mqtt,
    )


@pytest.fixture
def usecase_with_all(
    device_repo, device_config_repo, device_status_repo, device_alert_repo,
    iot_data_repo, alarm_log_repo, activity_log_repo,
):
    mqtt = Mock()
    mqtt.is_connected.return_value = True
    influxdb = Mock(spec=InfluxDBClientWrapper)
    redis = Mock()
    return IoTUseCase(
        device_repository=device_repo,
        device_config_repository=device_config_repo,
        device_status_repository=device_status_repo,
        device_alert_repository=device_alert_repo,
        iot_data_repository=iot_data_repo,
        alarm_log_repository=alarm_log_repo,
        activity_log_repository=activity_log_repo,
        mqtt_client=mqtt,
        influxdb_client=influxdb,
        redis_client=redis,
    )


# ============================================================
# CONNECTION STATUS
# ============================================================


class TestIsConnected:
    def test_not_connected_when_no_mqtt(self, usecase):
        assert usecase.is_connected() is False

    def test_connected_when_mqtt_connected(self, usecase_with_mqtt):
        assert usecase_with_mqtt.is_connected() is True

    def test_not_connected_when_mqtt_disconnected(self, usecase_with_mqtt):
        usecase_with_mqtt._mqtt_client.is_connected.return_value = False
        assert usecase_with_mqtt.is_connected() is False


class TestIsCacheEnabled:
    def test_cache_disabled_when_no_redis(self, usecase):
        assert usecase.is_cache_enabled() is False

    def test_cache_enabled_when_redis_present(self, usecase_with_all):
        assert usecase_with_all.is_cache_enabled() is True


# ============================================================
# GET TOPIC DATA
# ============================================================


class TestGetTopicData:
    @pytest.mark.asyncio
    async def test_returns_disconnected_when_no_mqtt(self, usecase):
        result = await usecase.get_topic_data("iot/test")
        assert result["from"] == "mqtt_disconnected"
        assert result["payload"] is None

    @pytest.mark.asyncio
    async def test_returns_data_from_mqtt(self, usecase_with_mqtt):
        usecase_with_mqtt._mqtt_client.get_data_from_topic.return_value = '{"temp": 25}'
        result = await usecase_with_mqtt.get_topic_data("iot/test")
        assert result["from"] == "mqtt"
        assert result["payload"] == {"temp": 25}

    @pytest.mark.asyncio
    async def test_returns_cache_hit(self, usecase_with_all):
        usecase_with_all._redis_client.get.return_value = '{"temp": 20}'
        result = await usecase_with_all.get_topic_data("iot/test")
        assert result["from"] == "cache"
        assert result["cache"] is True

    @pytest.mark.asyncio
    async def test_deletes_cache_when_del_cache(self, usecase_with_all):
        await usecase_with_all.get_topic_data("iot/test", del_cache=True)
        usecase_with_all._redis_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_error_on_mqtt_failure(self, usecase_with_mqtt):
        usecase_with_mqtt._mqtt_client.get_data_from_topic.side_effect = RuntimeError("boom")
        result = await usecase_with_mqtt.get_topic_data("iot/test")
        assert result["from"] == "mqtt_error"


# ============================================================
# DEVICE CONTROL
# ============================================================


class TestDeviceControl:
    @pytest.mark.asyncio
    async def test_returns_false_when_no_mqtt(self, usecase):
        result = await usecase.device_control("iot/test", "ON")
        assert result is False

    @pytest.mark.asyncio
    async def test_publishes_message(self, usecase_with_mqtt):
        usecase_with_mqtt._mqtt_client.publish.return_value = True
        result = await usecase_with_mqtt.device_control("iot/test", "ON")
        assert result is True
        usecase_with_mqtt._mqtt_client.publish.assert_called_once_with("iot/test", "ON", qos=1)

    @pytest.mark.asyncio
    async def test_device_controls_delegates(self, usecase_with_mqtt):
        usecase_with_mqtt._mqtt_client.publish.return_value = True
        result = await usecase_with_mqtt.device_controls("iot/test", "OFF")
        assert result is True


# ============================================================
# GET DEVICE LIST
# ============================================================


class TestGetDeviceList:
    @pytest.mark.asyncio
    async def test_returns_paginated_devices(self, usecase, device_repo):
        devices = [_make_device(), _make_device(device_name="Device 2")]
        device_repo.find_all_paginated = AsyncMock(return_value=(devices, 2))
        result = await usecase.get_device_list()
        assert len(result[0]) == 2
        assert result[1] == 2

    @pytest.mark.asyncio
    async def test_get_device_list_page(self, usecase, device_repo):
        device_repo.find_all_paginated = AsyncMock(return_value=([], 0))
        result = await usecase.get_device_list_page()
        assert result == ([], 0)


class TestGetDeviceListByLocation:
    @pytest.mark.asyncio
    async def test_returns_devices_by_location(self, usecase, device_repo):
        devices = [_make_device()]
        device_repo.find_by_location = AsyncMock(return_value=devices)
        result = await usecase.get_device_list_by_location(1)
        assert len(result) == 1
        device_repo.find_by_location.assert_called_once_with(1)


# ============================================================
# INFLUXDB CHARTS
# ============================================================


class TestGetSenserCharts:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_influxdb(self, usecase):
        result = await usecase.get_senser_charts()
        assert result["data"] == []
        assert result["cache"] == "no cache"

    @pytest.mark.asyncio
    async def test_returns_chart_data(self, usecase_with_all):
        usecase_with_all._influxdb_client.query_filter_data.return_value = [
            {"_value": 25.5, "_time": "2024-01-01T00:00:00Z"},
            {"_value": 26.0, "_time": "2024-01-01T00:01:00Z"},
        ]
        result = await usecase_with_all.get_senser_charts()
        assert result["data"] == [25.5, 26.0]
        assert len(result["date"]) == 2

    @pytest.mark.asyncio
    async def test_returns_error_on_influxdb_failure(self, usecase_with_all):
        usecase_with_all._influxdb_client.query_filter_data.side_effect = RuntimeError("boom")
        result = await usecase_with_all.get_senser_charts()
        assert result["cache"] == "error"
        assert "error" in result


# ============================================================
# PROCESS MQTT DATA
# ============================================================


class TestProcessMqttData:
    @pytest.mark.asyncio
    async def test_parses_csv_data(self, usecase, iot_data_repo):
        iot_data_repo.create = AsyncMock()
        result = await usecase.process_mqtt_data("1", "25.5,60,1013")
        assert result["device_id"] == "1"
        assert result["data"]["0"] == 25.5
        assert result["data"]["1"] == 60.0
        assert result["data"]["2"] == 1013.0
        assert result["data"]["raw"] == "25.5,60,1013"
        iot_data_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_non_numeric_values(self, usecase, iot_data_repo):
        iot_data_repo.create = AsyncMock()
        result = await usecase.process_mqtt_data("1", "25.5,hello")
        assert result["data"]["0"] == 25.5
        assert result["data"]["1"] == "hello"


# ============================================================
# GET LATEST DATA
# ============================================================


class TestGetLatestData:
    @pytest.mark.asyncio
    async def test_returns_latest_data(self, usecase, iot_data_repo):
        data = [_make_iot_data(), _make_iot_data()]
        iot_data_repo.find_latest = AsyncMock(return_value=data)
        result = await usecase.get_latest_data("1", limit=5)
        assert len(result) == 2
        iot_data_repo.find_latest.assert_called_once_with(1, 5)


# ============================================================
# LIST IOT DATA
# ============================================================


class TestListIoTData:
    @pytest.mark.asyncio
    async def test_returns_paginated_data(self, usecase, iot_data_repo):
        items = [_make_iot_data(), _make_iot_data()]
        iot_data_repo.find_paginated = AsyncMock(return_value=(items, 10))
        result = await usecase.list_iot_data(page=1, limit=5)
        assert result["pagination"]["total"] == 10
        assert result["pagination"]["page"] == 1
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_invalid_page_and_limit(self, usecase, iot_data_repo):
        iot_data_repo.find_paginated = AsyncMock(return_value=([], 0))
        result = await usecase.list_iot_data(page=0, limit=-1)
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 50


# ============================================================
# EXPORT DATA
# ============================================================


class TestExportData:
    @pytest.mark.asyncio
    async def test_export_json(self, usecase, iot_data_repo):
        items = [_make_iot_data()]
        iot_data_repo.find_by_date_range = AsyncMock(return_value=items)
        content, content_type = await usecase.export_data(
            device_id="1", start_date="2024-01-01", end_date="2024-01-02",
        )
        assert content_type == "application/json"
        assert "device_id" in content

    @pytest.mark.asyncio
    async def test_export_csv(self, usecase, iot_data_repo):
        items = [_make_iot_data()]
        iot_data_repo.find_by_date_range = AsyncMock(return_value=items)
        content, content_type = await usecase.export_data(
            device_id="1", start_date="2024-01-01", end_date="2024-01-02",
            export_format="csv",
        )
        assert content_type == "text/csv"
        assert "timestamp" in content


# ============================================================
# CLEANUP OLD DATA
# ============================================================


class TestCleanupOldData:
    @pytest.mark.asyncio
    async def test_calls_cleanup(self, usecase, iot_data_repo):
        iot_data_repo.cleanup_old = AsyncMock(return_value=5)
        result = await usecase.cleanup_old_data(days=90)
        assert result == 5
        iot_data_repo.cleanup_old.assert_called_once_with(90)


# ============================================================
# DEVICE STATUS / CONFIG
# ============================================================


class TestGetDeviceStatus:
    @pytest.mark.asyncio
    async def test_returns_status(self, usecase):
        result = await usecase.get_device_status("1")
        assert result["device_id"] == "1"
        assert "is_online" in result


class TestUpdateDeviceStatus:
    @pytest.mark.asyncio
    async def test_returns_true(self, usecase):
        result = await usecase.update_device_status("1", {"battery": 80})
        assert result is True


class TestGetDeviceConfig:
    @pytest.mark.asyncio
    async def test_returns_config(self, usecase):
        result = await usecase.get_device_config("1")
        assert result["device_id"] == "1"
        assert "config" in result


class TestUpdateDeviceConfig:
    @pytest.mark.asyncio
    async def test_returns_true(self, usecase):
        result = await usecase.update_device_config("1", {"key": "value"})
        assert result is True


class TestGetDeviceStats:
    @pytest.mark.asyncio
    async def test_returns_stats(self, usecase, iot_data_repo):
        iot_data_repo.find_latest = AsyncMock(return_value=[_make_iot_data()])
        result = await usecase.get_device_stats("1")
        assert result["count"] == 1
