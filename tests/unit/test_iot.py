"""tests/unit/test_iot.py — Domain + use case unit tests (iot)"""
from __future__ import annotations

import csv
import io
import json
import math
import uuid
from datetime import UTC, datetime

import pytest

from app.modules.iot.application.use_case import iotUseCase
from app.modules.iot.domain.helpers.alarm_logic import (
    evaluate_alarm,
    normalize_sensor_value,
    safe_float,
    safe_int,
    translate,
)
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO

pytestmark = pytest.mark.unit

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")


# ---------------------------------------------------------------------------
# Lightweight async fake repositories (only methods the use case actually calls)
# ---------------------------------------------------------------------------


class FakeDeviceRepo:
    def __init__(self) -> None:
        self.active_devices = [
            {
                "id": 1,
                "device_name": "HW-1",
                "location_id": 10,
                "hardware_type": 1,
                "status": "active",
            },
            {
                "id": 2,
                "device_name": "HW-2",
                "location_id": 20,
                "hardware_type": 2,
                "status": "active",
            },
        ]
        self.paginated_rows = [{"id": 1, "device_name": "HW-1"}]

    async def find_all_paginated(self, page: int, page_size: int) -> list[dict]:
        start = (page - 1) * page_size
        return self.paginated_rows[start : start + page_size]

    async def find_by_location(self, location_id: int) -> list[dict]:
        return [d for d in self.active_devices if d["location_id"] == location_id]

    async def find_all_active(self) -> list[dict]:
        return list(self.active_devices)


class FakeIotDataRepo:
    def __init__(self) -> None:
        self.created: list[dict] = []
        self.cleaned_days: list[int] = []
        self.latest: dict[int, list[dict]] = {
            1: [
                {"device_id": 1, "data": 12.5, "timestamp": datetime.now(UTC)},
                {"device_id": 1, "data": 11.0, "timestamp": datetime.now(UTC)},
            ]
        }
        self.ranged: list[dict] = [
            {"device_id": 1, "data": 10, "timestamp": datetime.now(UTC)},
        ]
        self.paginated_rows: list[dict] = [
            {"device_id": 1, "data": 1, "timestamp": datetime.now(UTC)},
        ]
        self.paginated_total = 120

    async def create(self, data: dict) -> dict:
        self.created.append(data)
        return data

    async def find_latest(self, device_id: int, limit: int) -> list[dict]:
        return self.latest.get(device_id, [])[:limit]

    async def find_by_date_range(
        self, device_id: int | None, start: datetime, end: datetime
    ) -> list[dict]:
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert end > start
        if device_id is None:
            return list(self.ranged)
        return [r for r in self.ranged if r["device_id"] == device_id]

    async def find_paginated(self, page: int, limit: int) -> tuple[list[dict], int]:
        start = (page - 1) * limit
        return self.paginated_rows[start : start + limit], self.paginated_total

    async def cleanup_old(self, days: int) -> None:
        self.cleaned_days.append(days)


class StubRepo:
    """Generic stub — the use case holds these but never calls them directly."""

    def __getattr__(self, name: str):  # pragma: no cover - safety net
        raise AssertionError(f"unexpected repo call: {name}")


def make_use_case() -> tuple[iotUseCase, FakeDeviceRepo, FakeIotDataRepo]:
    device_repo = FakeDeviceRepo()
    iot_data_repo = FakeIotDataRepo()
    uc = iotUseCase(
        device_repo=device_repo,
        device_config_repo=StubRepo(),
        device_status_repo=StubRepo(),
        device_alert_repo=StubRepo(),
        iot_data_repo=iot_data_repo,
        alarm_log_repo=StubRepo(),
        activity_log_repo=StubRepo(),
    )
    return uc, device_repo, iot_data_repo


# ---------------------------------------------------------------------------
# is_connected
# ---------------------------------------------------------------------------


class TestIsConnected:
    async def test_none_client_returns_false(self) -> None:
        uc, _, _ = make_use_case()
        assert uc.is_connected() is False

    async def test_connected_client_returns_true(self) -> None:
        class Client:
            is_connected = True

        uc, _, _ = make_use_case()
        uc._mqtt_client = Client()
        assert uc.is_connected() is True


# ---------------------------------------------------------------------------
# process_mqtt_data
# ---------------------------------------------------------------------------


class TestProcessMqttData:
    async def test_numeric_payload_stored(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        result = await uc.process_mqtt_data(1, {"value": 42})
        assert result["device_id"] == 1
        assert result["data"] == {"value": 42}
        assert "timestamp" in result
        datetime.fromisoformat(result["timestamp"])
        assert len(iot_data_repo.created) == 1

    async def test_string_payload_stored(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        result = await uc.process_mqtt_data(7, {"temp": "23.5"})
        assert result["device_id"] == 7
        assert result["data"] == {"temp": "23.5"}
        assert iot_data_repo.created[0]["device_id"] == 7


# ---------------------------------------------------------------------------
# device / location delegation
# ---------------------------------------------------------------------------


class TestDeviceQueries:
    async def test_get_device_list_pagination_shape(self) -> None:
        uc, device_repo, _ = make_use_case()
        result = await uc.get_device_list(page=1, page_size=10)
        assert result["devices"] == device_repo.paginated_rows
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10

    async def test_get_devices_by_location_filters(self) -> None:
        uc, device_repo, _ = make_use_case()
        rows = await uc.get_devices_by_location(10)
        assert len(rows) == 1
        assert rows[0]["location_id"] == 10

    async def test_get_latest_data_converts_device_id(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        rows = await uc.get_latest_data("1", limit=1)
        assert rows == iot_data_repo.latest[1][:1]

    async def test_get_data_by_date_range_delegates(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        end = datetime.now(UTC)
        start = end.replace(year=end.year - 1)
        rows = await uc.get_data_by_date_range("1", start.isoformat(), end.isoformat())
        assert rows == iot_data_repo.ranged


# ---------------------------------------------------------------------------
# list_iot_data — clamping + pagination math
# ---------------------------------------------------------------------------


class TestListIotData:
    async def test_default_clamping(self) -> None:
        uc, _, _ = make_use_case()
        result = await uc.list_iot_data(page=0, limit=-5)
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 50

    async def test_pagination_math(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        result = await uc.list_iot_data(page=2, limit=50)
        pag = result["pagination"]
        assert pag["total"] == iot_data_repo.paginated_total
        assert pag["pages"] == math.ceil(iot_data_repo.paginated_total / 50)
        assert result["items"] == iot_data_repo.paginated_rows


# ---------------------------------------------------------------------------
# get_device_stats
# ---------------------------------------------------------------------------


class TestDeviceStats:
    async def test_stats_from_latest(self) -> None:
        uc, _, _ = make_use_case()
        stats = await uc.get_device_stats("1")
        assert stats["count"] == 2
        assert stats["last_record"] is not None
        datetime.fromisoformat(stats["last_record"])
        assert stats["first_record"] is not None

    async def test_stats_empty_device(self) -> None:
        uc, _, _ = make_use_case()
        stats = await uc.get_device_stats("999")
        assert stats["count"] == 0
        assert stats["last_record"] is None
        assert stats["first_record"] is None


# ---------------------------------------------------------------------------
# export_data — CSV vs JSON
# ---------------------------------------------------------------------------


class TestExportData:
    async def test_csv_export_default_window(self) -> None:
        uc, _, _ = make_use_case()
        output, mime = await uc.export_data("csv")
        assert mime == "text/csv"
        reader = csv.reader(io.StringIO(output))
        rows = list(reader)
        assert rows[0] == ["timestamp", "device_id", "data"]

    async def test_json_export(self) -> None:
        uc, _, _ = make_use_case()
        output, mime = await uc.export_data("json")
        assert mime == "application/json"
        parsed = json.loads(output)
        assert isinstance(parsed, (list, dict))


# ---------------------------------------------------------------------------
# cleanup_old_data
# ---------------------------------------------------------------------------


class TestCleanupOldData:
    async def test_default_90_days(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        await uc.cleanup_old_data()
        assert iot_data_repo.cleaned_days == [90]

    async def test_custom_days(self) -> None:
        uc, _, iot_data_repo = make_use_case()
        await uc.cleanup_old_data(days=30)
        assert iot_data_repo.cleaned_days == [30]


# ---------------------------------------------------------------------------
# evaluate_alarm — status mapping
# ---------------------------------------------------------------------------


def make_alarm(**overrides) -> AlarmDetailDTO:
    base = {
        "hardware_id": 1,
        "value_data": 0,
        "value_alarm": 0,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    base.update(overrides)
    return AlarmDetailDTO(**base)


class TestAlarmStatus:
    def test_normal_status_5(self) -> None:
        result = evaluate_alarm(make_alarm(status_warning=0, status_alert=0))
        assert result.status == 5

    def test_status_warning_maps_to_1(self) -> None:
        result = evaluate_alarm(make_alarm(status_warning=1))
        assert result.status == 1

    def test_status_alert_maps_to_2(self) -> None:
        result = evaluate_alarm(make_alarm(status_alert=1))
        assert result.status == 2

    def test_recovery_warning_maps_to_3(self) -> None:
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                status_warning=0,
                status_alert=0,
                recovery_warning=50,
                sensor_value_data=40,
            )
        )
        assert result.status == 3

    def test_recovery_critical_maps_to_4(self) -> None:
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                status_warning=0,
                status_alert=0,
                recovery_warning=0,
                recovery_alert=100,
                sensor_value_data=90,
                value_alarm=1,
            )
        )
        assert result.status == 4

    def test_max_value_critical(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=1, status_warning=0, status_alert=0, value_data=200, max_value=100)
        )
        assert result.status == 2

    def test_min_value_warning(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=1, status_warning=0, status_alert=0, value_data=5, min_value=10)
        )
        assert result.status == 1

    def test_value_alarm_zero_normal_hw2(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=2, status_warning=0, status_alert=0, value_alarm=0)
        )
        assert result.status == 5

    def test_value_alarm_set_hw2_recovery(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=2, status_warning=0, status_alert=0, value_alarm=1)
        )
        assert result.status == 4

    def test_hw3_on_is_normal(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=3, status_warning=0, status_alert=0, value_data="ON", value_alarm=0)
        )
        assert result.status == 5

    def test_hw4_abnormal_critical(self) -> None:
        result = evaluate_alarm(
            make_alarm(hardware_id=4, status_warning=0, status_alert=0, value_data=0)
        )
        assert result.status == 2

    def test_unknown_hardware_defaults_999(self) -> None:
        result = evaluate_alarm(make_alarm(hardware_id=99, status_warning=0, status_alert=0))
        assert result.status == 999

    def test_type_id_equals_hardware_id(self) -> None:
        result = evaluate_alarm(make_alarm(hardware_id=3))
        assert result.type_id == 3
        assert result.hardware_id == 3


# ---------------------------------------------------------------------------
# helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_safe_int(self) -> None:
        assert safe_int(None) == 0
        assert safe_int("5") == 5
        assert safe_int("abc") == 0
        assert safe_int(3.7) == 3

    def test_safe_float(self) -> None:
        assert safe_float(None) == 0.0
        assert safe_float("2.5") == 2.5
        assert safe_float("xyz") == 0.0

    def test_normalize_sensor_value(self) -> None:
        assert normalize_sensor_value("on") == "ON"
        assert normalize_sensor_value("off") == "OFF"
        assert normalize_sensor_value("23.5") == 23.5
        assert normalize_sensor_value("abc") == "abc"

    def test_translate_th(self) -> None:
        assert translate("warning", "th") != ""

    def test_translate_en(self) -> None:
        assert translate("warning", "en") != ""
