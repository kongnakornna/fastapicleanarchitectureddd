from app.modules.iot.domain.helpers.alarm_logic import (
    _normalize_sensor_value,
    _to_float,
    _to_int,
    evaluate_alarm,
)
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO


def _make_dto(**overrides):
    defaults = {
        "hardware_id": 1,
        "value_data": "25.5",
        "value_alarm": 0,
        "value_relay": None,
        "value_control_relay": None,
        "max_value": 50,
        "min_value": 10,
        "status_alert": 45,
        "status_warning": 40,
        "recovery_warning": 35,
        "recovery_alert": 30,
        "device_name": "Test Device",
        "action_name": "relay1",
        "mqtt_name": "mqtt_test",
        "mqtt_control_on": "ON",
        "mqtt_control_off": "OFF",
        "count_alarm": 0,
        "event": 0,
        "unit": "°C",
    }
    defaults.update(overrides)
    return AlarmDetailDTO(**defaults)


# ============================================================
# HELPER FUNCTIONS
# ============================================================


class TestToInt:
    def test_none_returns_zero(self):
        assert _to_int(None) == 0

    def test_string_number(self):
        assert _to_int("42") == 42

    def test_float_string(self):
        assert _to_int("3.14") == 3

    def test_invalid_returns_zero(self):
        assert _to_int("abc") == 0

    def test_integer_passthrough(self):
        assert _to_int(10) == 10


class TestToFloat:
    def test_none_returns_zero(self):
        assert _to_float(None) == 0.0

    def test_string_number(self):
        assert _to_float("3.14") == 3.14

    def test_invalid_returns_zero(self):
        assert _to_float("abc") == 0.0

    def test_integer_passthrough(self):
        assert _to_float(5) == 5.0


class TestNormalizeSensorValue:
    def test_on_uppercase(self):
        assert _normalize_sensor_value("ON") == "ON"

    def test_off_lowercase(self):
        assert _normalize_sensor_value("OFF") == "OFF"

    def test_numeric_string(self):
        assert _normalize_sensor_value("25.5") == 25.5

    def test_non_numeric_string(self):
        assert _normalize_sensor_value("hello") == "hello"

    def test_integer_passthrough(self):
        assert _normalize_sensor_value(42) == 42


# ============================================================
# HARDWARE TYPE 1 - ANALOG SENSOR
# ============================================================


class TestAlarmHardwareType1:
    def test_normal_value(self):
        dto = _make_dto(hardware_id=1, value_data="25", max_value=50, min_value=10)
        result = evaluate_alarm(dto)
        assert result.status == 5
        assert result.alarm_status_set == 999
        assert "ปกติ" in result.title

    def test_exceeds_max(self):
        dto = _make_dto(hardware_id=1, value_data="55", max_value=50, min_value=10)
        result = evaluate_alarm(dto)
        assert result.status == 2
        assert result.alarm_status_set == 2
        assert "วิกฤต" in result.title

    def test_below_min(self):
        dto = _make_dto(hardware_id=1, value_data="5", max_value=50, min_value=10)
        result = evaluate_alarm(dto)
        assert result.status == 1
        assert result.alarm_status_set == 1
        assert "วิกฤต" in result.title

    def test_warning_threshold(self):
        dto = _make_dto(
            hardware_id=1, value_data="42", max_value=50, min_value=10,
            status_warning=40, status_alert=45,
        )
        result = evaluate_alarm(dto)
        assert result.status == 1
        assert "คำเตือน" in result.title

    def test_alert_threshold(self):
        dto = _make_dto(
            hardware_id=1, value_data="46", max_value=50, min_value=10,
            status_warning=40, status_alert=45,
        )
        result = evaluate_alarm(dto)
        assert result.status == 2
        assert "วิกฤตต้องแก้ไขทันที" in result.title

    def test_recovery_warning(self):
        dto = _make_dto(
            hardware_id=1, value_data="34", max_value=50, min_value=10,
            count_alarm=1, recovery_warning=35, recovery_alert=30,
        )
        result = evaluate_alarm(dto)
        assert result.status == 3
        assert result.alarm_status_set == 3
        assert "คืนสู่ภาวะปกติ" in result.title

    def test_recovery_warning_fires_before_critical(self):
        dto = _make_dto(
            hardware_id=1, value_data="29", max_value=50, min_value=10,
            count_alarm=1, recovery_warning=35, recovery_alert=30,
        )
        result = evaluate_alarm(dto)
        assert result.status == 3
        assert result.alarm_status_set == 3

    def test_recovery_critical_when_warning_not_triggered(self):
        dto = _make_dto(
            hardware_id=1, value_data="28", max_value=50, min_value=10,
            count_alarm=1, recovery_warning=25, recovery_alert=30,
        )
        result = evaluate_alarm(dto)
        assert result.status == 4
        assert result.alarm_status_set == 4


# ============================================================
# HARDWARE TYPE 2 - DIGITAL SENSOR
# ============================================================


class TestAlarmHardwareType2:
    def test_alarm_triggered(self):
        dto = _make_dto(hardware_id=2, value_data="0", value_alarm="0")
        result = evaluate_alarm(dto)
        assert result.status == 1
        assert result.alarm_status_set == 1

    def test_alarm_value_one(self):
        dto = _make_dto(hardware_id=2, value_data="1", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 1
        assert result.sensor_value == 1

    def test_recovery(self):
        dto = _make_dto(
            hardware_id=2, value_data="1", value_alarm="1",
            count_alarm=1, recovery_warning=0, recovery_alert=0,
            max_value=0, min_value=0,
        )
        result = evaluate_alarm(dto)
        assert result.status == 4
        assert result.alarm_status_set == 4


# ============================================================
# HARDWARE TYPE 3 - RELAY
# ============================================================


class TestAlarmHardwareType3:
    def test_relay_on(self):
        dto = _make_dto(hardware_id=3, value_data="ON", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 5
        assert result.alarm_status_set == 999

    def test_relay_off(self):
        dto = _make_dto(hardware_id=3, value_data="OFF", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 5

    def test_relay_zero(self):
        dto = _make_dto(hardware_id=3, value_data="0", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 5

    def test_relay_one(self):
        dto = _make_dto(hardware_id=3, value_data="1", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 5


# ============================================================
# HARDWARE TYPE 4 - CRITICAL ALARM SENSOR
# ============================================================


class TestAlarmHardwareType4:
    def test_critical_normal(self):
        dto = _make_dto(hardware_id=4, value_data="1", value_alarm="1")
        result = evaluate_alarm(dto)
        assert result.status == 5
        assert result.alarm_status_set == 999

    def test_critical_alarm(self):
        dto = _make_dto(hardware_id=4, value_data="0", value_alarm="0")
        result = evaluate_alarm(dto)
        assert result.status == 2
        assert result.alarm_status_set == 2
        assert "วิกฤต" in result.title


# ============================================================
# ENGLISH MESSAGES
# ============================================================


class TestAlarmEnglish:
    def test_normal_english(self):
        dto = _make_dto(hardware_id=1, value_data="25", max_value=50, min_value=10)
        result = evaluate_alarm(dto, lang="en")
        assert result.title == "Normal"

    def test_critical_english(self):
        dto = _make_dto(hardware_id=1, value_data="55", max_value=50, min_value=10)
        result = evaluate_alarm(dto, lang="en")
        assert "Critical" in result.title

    def test_warning_english(self):
        dto = _make_dto(
            hardware_id=1, value_data="42", max_value=50, min_value=10,
            status_warning=40, status_alert=45,
        )
        result = evaluate_alarm(dto, lang="en")
        assert result.title == "Warning"


# ============================================================
# MQTT CONTROL
# ============================================================


class TestAlarmMQTTControl:
    def test_event_on_triggers_control_on(self):
        dto = _make_dto(
            hardware_id=1, value_data="55", max_value=50, min_value=10,
            event=1, mqtt_control_on="RELAY_ON", mqtt_control_off="RELAY_OFF",
        )
        result = evaluate_alarm(dto)
        assert result.event_control == 1
        assert result.message_mqtt_control == "RELAY_ON"

    def test_recovery_with_event_on(self):
        dto = _make_dto(
            hardware_id=1, value_data="34", max_value=50, min_value=10,
            count_alarm=1, recovery_warning=35, recovery_alert=30,
            event=1, mqtt_control_on="RELAY_ON", mqtt_control_off="RELAY_OFF",
        )
        result = evaluate_alarm(dto)
        assert result.event_control == 1
        assert result.message_mqtt_control == "RELAY_OFF"

    def test_recovery_with_event_off(self):
        dto = _make_dto(
            hardware_id=1, value_data="34", max_value=50, min_value=10,
            count_alarm=1, recovery_warning=35, recovery_alert=30,
            event=0, mqtt_control_on="RELAY_ON", mqtt_control_off="RELAY_OFF",
        )
        result = evaluate_alarm(dto)
        assert result.event_control == 0
        assert result.message_mqtt_control == "RELAY_ON"
