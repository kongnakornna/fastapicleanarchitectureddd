import pytest

from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Shared test doubles / helpers
# ---------------------------------------------------------------------------

THAI_MESSAGES = {
    "warning": "\u0e04\u0e33\u0e40\u0e15\u0e37\u0e2d\u0e19 \u0e21\u0e35\u0e04\u0e27\u0e32\u0e21\u0e1c\u0e34\u0e14\u0e1b\u0e01\u0e15\u0e34",
    "critical": "\u0e20\u0e32\u0e27\u0e30\u0e27\u0e34\u0e01\u0e24\u0e15\u0e15\u0e49\u0e2d\u0e07\u0e41\u0e01\u0e49\u0e44\u0e02\u0e17\u0e31\u0e19\u0e17\u0e35",
    "recovery_warning": "\u0e04\u0e37\u0e19\u0e2a\u0e39\u0e48\u0e20\u0e32\u0e27\u0e30\u0e1b\u0e01\u0e15\u0e34 (\u0e04\u0e33\u0e40\u0e15\u0e37\u0e2d\u0e19)",
    "recovery_critical": "\u0e04\u0e37\u0e19\u0e2a\u0e39\u0e48\u0e20\u0e32\u0e27\u0e30\u0e1b\u0e01\u0e15\u0e34 (\u0e27\u0e34\u0e01\u0e24\u0e15)",
    "normal": "\u0e1b\u0e01\u0e15\u0e34",
    "critical_max": "\u0e27\u0e34\u0e01\u0e24\u0e15 \u0e21\u0e35\u0e04\u0e48\u0e32\u0e2a\u0e39\u0e07\u0e40\u0e01\u0e34\u0e19\u0e01\u0e33\u0e2b\u0e19\u0e14",
    "critical_min": "\u0e27\u0e34\u0e01\u0e24\u0e15 \u0e21\u0e35\u0e04\u0e48\u0e32\u0e15\u0e48\u0e33\u0e01\u0e27\u0e48\u0e32\u0e01\u0e33\u0e2b\u0e19\u0e14",
}

ENGLISH_MESSAGES = {
    "warning": "Warning",
    "critical": "Critical",
    "recovery_warning": "Recovery Warning",
    "recovery_critical": "Recovery Critical",
    "normal": "Normal",
    "critical_max": "Critical! Maximum limit.",
    "critical_min": "Critical! Minimum limit",
}


def make_alarm(**overrides):
    base = {
        "hardware_id": 1,
        "value_data": 0,
        "value_alarm": 0,
    }
    base.update(overrides)
    return AlarmDetailDTO(**base)


# ---------------------------------------------------------------------------
# Normal state (AlarmStatus.NORMAL = 5)
# ---------------------------------------------------------------------------


class TestAlarmNormal:
    def test_default_dto_is_normal_thai(self):
        result = evaluate_alarm(make_alarm())

        assert result.status == 5
        assert result.alarm_status_set == 999
        assert result.data_alarm == 0
        assert result.data_alarm_raw == 0
        assert result.title == THAI_MESSAGES["normal"]
        assert result.subject == THAI_MESSAGES["normal"]
        assert result.content == f"{THAI_MESSAGES['normal']} "
        assert result.event_control == 0
        assert result.lang == "th"

    def test_default_dto_is_normal_english(self):
        result = evaluate_alarm(make_alarm(), lang="en")

        assert result.status == 5
        assert result.title == ENGLISH_MESSAGES["normal"]
        assert result.content == f"{ENGLISH_MESSAGES['normal']} "
        assert result.lang == "en"

    def test_normal_when_value_below_thresholds(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=5,
                max_value=100,
                min_value=0,
                status_warning=8,
                status_alert=10,
            )
        )

        assert result.status == 5
        assert result.alarm_status_set == 999
        assert result.title == THAI_MESSAGES["normal"]

    def test_recovery_not_fired_without_alarm_history(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=5,
                recovery_warning=50,
                recovery_alert=100,
                count_alarm=0,
            )
        )

        assert result.status == 5
        assert result.alarm_status_set == 999


# ---------------------------------------------------------------------------
# Warning / Critical severity for sensor hardware (hardware_id = 1)
# ---------------------------------------------------------------------------


class TestAlarmSeverity:
    def test_warning_fires_thai(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=15,
                status_warning=10,
                status_alert=20,
                device_name="sensor-1",
                mqtt_name="mqtt-topic-1",
                mqtt_control_on="topic/on",
                mqtt_control_off="topic/off",
                action_name="notify",
            )
        )

        assert result.status == 1
        assert result.alarm_status_set == 1
        assert result.data_alarm == 15
        assert result.title == THAI_MESSAGES["warning"]
        assert result.subject == THAI_MESSAGES["warning"]
        assert result.alarm_type_id == result.type_id == result.hardware_id == 1
        assert result.mqtt_name_str == "mqtt-topic-1"
        assert result.device_name_str == "sensor-1"
        assert result.device_name_val == "sensor-1"
        assert result.mqtt_control_on_str == "topic/on"
        assert result.alarm_action_name == "notify"
        assert result.event_control == 0
        assert result.message_mqtt_control == "topic/off"

    def test_warning_fires_english(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=15,
                status_warning=10,
                status_alert=20,
            ),
            lang="en",
        )

        assert result.status == 1
        assert result.title == ENGLISH_MESSAGES["warning"]
        assert result.subject == ENGLISH_MESSAGES["warning"]

    def test_warning_boundary_equal_threshold(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=10, status_warning=10, status_alert=20)
        )

        assert result.status == 1
        assert result.alarm_status_set == 1

    def test_critical_fires_thai(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=15, status_alert=10)
        )

        assert result.status == 2
        assert result.alarm_status_set == 2
        assert result.data_alarm == 15
        assert result.title == THAI_MESSAGES["critical"]
        assert result.subject == THAI_MESSAGES["critical"]

    def test_critical_boundary_equal_threshold(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=10, status_alert=10)
        )

        assert result.status == 2
        assert result.alarm_status_set == 2

    def test_event_control_on_when_event_one(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=15,
                status_alert=10,
                event=1,
                mqtt_control_on="topic/on",
                mqtt_control_off="topic/off",
            )
        )

        assert result.event_control == 1
        assert result.message_mqtt_control == "topic/on"

    def test_warning_not_fired_when_status_alert_zero(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=15, status_warning=10, status_alert=0)
        )

        assert result.status == 5
        assert result.alarm_status_set == 999


# ---------------------------------------------------------------------------
# Max / Min critical bounds (hardware_id 1 or 2, non-zero limits)
# ---------------------------------------------------------------------------


class TestAlarmMaxMin:
    def test_max_fires(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=200, max_value=100)
        )

        assert result.status == 2
        assert result.alarm_status_set == 2
        assert result.title == THAI_MESSAGES["critical_max"]
        assert result.subject == THAI_MESSAGES["critical_max"]

    def test_max_boundary_equal(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=100, max_value=100)
        )

        assert result.status == 2
        assert result.alarm_status_set == 2

    def test_max_not_fired_when_max_value_zero(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=200, max_value=0)
        )

        assert result.status == 5
        assert result.alarm_status_set == 999

    def test_min_fires(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=5, min_value=10)
        )

        assert result.status == 1
        assert result.alarm_status_set == 1
        assert result.title == THAI_MESSAGES["critical_min"]
        assert result.subject == THAI_MESSAGES["critical_min"]

    def test_min_boundary_equal(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=10, min_value=10)
        )

        assert result.status == 1
        assert result.alarm_status_set == 1

    def test_min_not_fired_when_min_value_zero(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=1, value_data=5, min_value=0)
        )

        assert result.status == 5
        assert result.alarm_status_set == 999


# ---------------------------------------------------------------------------
# Digital / IO hardware types 3 and 4 and unknown hardware
# ---------------------------------------------------------------------------


class TestAlarmHardwareDigital:
    def test_io_control_on_normal(self):
        result = evaluate_alarm(make_alarm(hardware_id=3, value_data="ON"))

        assert result.status == 5
        assert result.alarm_status_set == 999
        assert result.title == THAI_MESSAGES["normal"]

    def test_io_control_off_not_normal(self):
        result = evaluate_alarm(make_alarm(hardware_id=3, value_data="OFF"))

        assert result.status != 5

    def test_critical_sensor_on_normal(self):
        result = evaluate_alarm(make_alarm(hardware_id=4, value_data=1))

        assert result.status == 5
        assert result.alarm_status_set == 999

    def test_critical_sensor_off_fires_critical(self):
        result = evaluate_alarm(make_alarm(hardware_id=4, value_data=0))

        assert result.status == 2
        assert result.alarm_status_set == 2
        assert result.title == THAI_MESSAGES["critical"]

    def test_unknown_hardware_normal(self):
        result = evaluate_alarm(make_alarm(hardware_id=99, value_data=55))

        assert result.status == 5
        assert result.alarm_status_set == 999
        assert result.title == THAI_MESSAGES["normal"]


# ---------------------------------------------------------------------------
# Recovery state (requires alarm history count_alarm >= 1)
# ---------------------------------------------------------------------------


class TestAlarmRecovery:
    def test_recovery_warning_fires_thai(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=40,
                recovery_warning=50,
                recovery_alert=100,
                count_alarm=1,
            )
        )

        assert result.status == 3
        assert result.alarm_status_set == 3
        assert result.title == THAI_MESSAGES["recovery_warning"]
        assert result.subject == THAI_MESSAGES["recovery_warning"]

    def test_recovery_warning_boundary_equal(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=50,
                recovery_warning=50,
                recovery_alert=100,
                count_alarm=1,
            )
        )

        assert result.status == 3

    def test_recovery_critical_fires_english(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=90,
                recovery_warning=100,
                recovery_alert=100,
                count_alarm=1,
            ),
            lang="en",
        )

        assert result.status == 4
        assert result.alarm_status_set == 4
        assert result.title == ENGLISH_MESSAGES["recovery_critical"]
        assert result.subject == ENGLISH_MESSAGES["recovery_critical"]

    def test_recovery_swaps_mqtt_control_when_event_on(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=40,
                recovery_warning=50,
                recovery_alert=100,
                count_alarm=1,
                event=1,
                mqtt_control_on="topic/on",
                mqtt_control_off="topic/off",
            )
        )

        assert result.event_control == 1
        assert result.message_mqtt_control == "topic/off"

    def test_digital_recovery_io_sensor(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=2, value_alarm=1, count_alarm=1)
        )

        assert result.status == 4
        assert result.alarm_status_set == 4
        assert result.title == THAI_MESSAGES["recovery_critical"]

    def test_digital_recovery_critical_sensor(self):
        result = evaluate_alarm(
            make_alarm(hardware_id=4, value_alarm=1, count_alarm=1)
        )

        assert result.status == 4
        assert result.alarm_status_set == 4

    def test_no_recovery_when_count_alarm_zero(self):
        result = evaluate_alarm(
            make_alarm(
                hardware_id=1,
                value_data=20,
                recovery_warning=50,
                recovery_alert=100,
                count_alarm=0,
            )
        )

        assert result.status == 5
        assert result.alarm_status_set == 999


# ---------------------------------------------------------------------------
# Public helper functions exported by the module
# ---------------------------------------------------------------------------


class TestAlarmHelpers:
    def test_translate_thai(self):
        assert translate("warning") == THAI_MESSAGES["warning"]
        assert translate("critical") == THAI_MESSAGES["critical"]
        assert translate("recovery_warning") == THAI_MESSAGES["recovery_warning"]
        assert translate("recovery_critical") == THAI_MESSAGES["recovery_critical"]
        assert translate("normal") == THAI_MESSAGES["normal"]
        assert translate("critical_max") == THAI_MESSAGES["critical_max"]
        assert translate("critical_min") == THAI_MESSAGES["critical_min"]

    def test_translate_english(self):
        assert translate("warning", lang="en") == ENGLISH_MESSAGES["warning"]
        assert translate("critical", lang="en") == ENGLISH_MESSAGES["critical"]
        assert translate("normal", lang="en") == ENGLISH_MESSAGES["normal"]
        assert translate("critical_max", lang="en") == ENGLISH_MESSAGES["critical_max"]
        assert translate("critical_min", lang="en") == ENGLISH_MESSAGES["critical_min"]

    def test_normalize_sensor_value_digital(self):
        assert normalize_sensor_value("on") == "ON"
        assert normalize_sensor_value("ON") == "ON"
        assert normalize_sensor_value("off") == "OFF"
        assert normalize_sensor_value("OfF") == "OFF"

    def test_normalize_sensor_value_numeric(self):
        assert normalize_sensor_value("12.5") == 12.5
        assert normalize_sensor_value("7") == 7.0
        assert normalize_sensor_value(7) == 7.0

    def test_normalize_sensor_value_unchanged(self):
        assert normalize_sensor_value("abc") == "abc"

    def test_safe_int(self):
        assert safe_int("42") == 42
        assert safe_int(42) == 42
        assert safe_int("3.9") == 3
        assert safe_int("abc") == 0
        assert safe_int(None) == 0

    def test_safe_float(self):
        assert safe_float("3.14") == 3.14
        assert safe_float(3) == 3.0
        assert safe_float("abc") == 0.0
        assert safe_float(None) == 0.0