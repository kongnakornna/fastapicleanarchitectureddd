from app.modules.iot.domain.entities.activity_log import ActivityLog
from app.modules.iot.domain.entities.alarm_log import AlarmLog
from app.modules.iot.domain.entities.device import Device
from app.modules.iot.domain.entities.device_alert import DeviceAlert
from app.modules.iot.domain.entities.device_config import DeviceConfig
from app.modules.iot.domain.entities.device_status import DeviceStatus
from app.modules.iot.domain.entities.iot_data import IoTData
from app.modules.iot.domain.entities.schedule import Schedule


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
        "description": "Test sensor",
        "firmware_version": "1.0.0",
    }
    defaults.update(overrides)
    return Device(**defaults)


def _make_device_config(**overrides):
    defaults = {
        "device_id": 1,
        "max_value": 50.0,
        "min_value": 10.0,
        "warning_threshold": 40.0,
        "alert_threshold": 45.0,
        "recovery_warning": 35.0,
        "recovery_alert": 30.0,
        "calibration_offset": 0.0,
        "calibration_multiplier": 1.0,
        "mqtt_control_on": "ON",
        "mqtt_control_off": "OFF",
        "action_name": "relay1",
        "config_json": "{}",
    }
    defaults.update(overrides)
    return DeviceConfig(**defaults)


def _make_device_status(**overrides):
    defaults = {
        "device_id": 1,
        "is_online": True,
        "last_value": 25.5,
        "last_alarm": 0,
        "count_alarm": 0,
        "event": 0,
        "status": "online",
        "sensor_data": "",
        "sensor_min": 0.0,
        "sensor_max": 0.0,
        "sensor_avg": 0.0,
        "battery": 100.0,
        "rssi": -50,
    }
    defaults.update(overrides)
    return DeviceStatus(**defaults)


def _make_device_alert(**overrides):
    defaults = {
        "device_id": 1,
        "alert_type": "temperature",
        "severity": "high",
        "title": "High Temperature",
        "message": "Temperature exceeded threshold",
        "value_data": 45.0,
        "value_alarm": 40.0,
        "resolved": False,
        "acknowledged": False,
    }
    defaults.update(overrides)
    return DeviceAlert(**defaults)


def _make_iot_data(**overrides):
    defaults = {
        "device_id": 1,
        "data_json": '{"temp": 25.5}',
        "location_id": 1,
        "metadata_json": "{}",
    }
    defaults.update(overrides)
    return IoTData(**defaults)


def _make_alarm_log(**overrides):
    defaults = {
        "device_id": 1,
        "alarm_action_id": 0,
        "alarm_type": 1,
        "alarm_status": 2,
        "value_data": 45.0,
        "value_alarm": 40.0,
        "title": "Critical",
        "subject": "High temp",
        "content": "Temperature critical",
        "data_alarm": 40,
        "data_alarm_raw": 40,
        "event_control": 0,
        "message_mqtt_control": "",
    }
    defaults.update(overrides)
    return AlarmLog(**defaults)


def _make_activity_log(**overrides):
    defaults = {
        "log_type": "device_update",
        "device_id": 1,
        "user_id": 1,
        "severity": "info",
        "data_json": "{}",
        "description": "Device updated",
    }
    defaults.update(overrides)
    return ActivityLog(**defaults)


def _make_schedule(**overrides):
    defaults = {
        "schedule_id": 1,
        "device_id": 1,
        "start_time": "08:00",
        "end_time": "18:00",
        "event": "on",
        "monday": True,
        "tuesday": True,
        "wednesday": True,
        "thursday": True,
        "friday": True,
        "saturday": False,
        "sunday": False,
    }
    defaults.update(overrides)
    return Schedule(**defaults)


# ============================================================
# DEVICE
# ============================================================


class TestDevice:
    def test_create_device(self):
        device = _make_device()
        assert device.hardware_id == 1
        assert device.device_name == "Test Device"
        assert device.status == "online"
        assert device.unit == "°C"

    def test_device_tablename(self):
        assert Device.__tablename__ == "iot_device"

    def test_device_defaults(self):
        device = _make_device(device_sn="", device_type="", status="offline")
        assert device.device_sn == ""
        assert device.status == "offline"

    def test_device_with_overrides(self):
        device = _make_device(hardware_id=4, device_name="Critical Sensor")
        assert device.hardware_id == 4
        assert device.device_name == "Critical Sensor"


# ============================================================
# DEVICE CONFIG
# ============================================================


class TestDeviceConfig:
    def test_create_config(self):
        config = _make_device_config()
        assert config.device_id == 1
        assert config.max_value == 50.0
        assert config.min_value == 10.0

    def test_config_tablename(self):
        assert DeviceConfig.__tablename__ == "iot_device_config"

    def test_config_defaults(self):
        config = _make_device_config(max_value=0.0, min_value=0.0)
        assert config.max_value == 0.0
        assert config.calibration_multiplier == 1.0


# ============================================================
# DEVICE STATUS
# ============================================================


class TestDeviceStatus:
    def test_create_status(self):
        status = _make_device_status()
        assert status.device_id == 1
        assert status.is_online is True
        assert status.battery == 100.0

    def test_status_tablename(self):
        assert DeviceStatus.__tablename__ == "iot_device_status"

    def test_status_defaults(self):
        status = _make_device_status(is_online=False, battery=0.0)
        assert status.is_online is False
        assert status.battery == 0.0


# ============================================================
# DEVICE ALERT
# ============================================================


class TestDeviceAlert:
    def test_create_alert(self):
        alert = _make_device_alert()
        assert alert.device_id == 1
        assert alert.severity == "high"
        assert alert.resolved is False

    def test_alert_tablename(self):
        assert DeviceAlert.__tablename__ == "iot_device_alert"


# ============================================================
# IOT DATA
# ============================================================


class TestIoTData:
    def test_create_data(self):
        data = _make_iot_data()
        assert data.device_id == 1
        assert data.data_json == '{"temp": 25.5}'

    def test_data_tablename(self):
        assert IoTData.__tablename__ == "iot_data"


# ============================================================
# ALARM LOG
# ============================================================


class TestAlarmLog:
    def test_create_log(self):
        log = _make_alarm_log()
        assert log.device_id == 1
        assert log.alarm_status == 2
        assert log.title == "Critical"

    def test_log_tablename(self):
        assert AlarmLog.__tablename__ == "iot_alarm_log"


# ============================================================
# ACTIVITY LOG
# ============================================================


class TestActivityLog:
    def test_create_log(self):
        log = _make_activity_log()
        assert log.log_type == "device_update"
        assert log.severity == "info"

    def test_log_tablename(self):
        assert ActivityLog.__tablename__ == "iot_activity_log"


# ============================================================
# SCHEDULE
# ============================================================


class TestSchedule:
    def test_create_schedule(self):
        schedule = _make_schedule()
        assert schedule.device_id == 1
        assert schedule.start_time == "08:00"
        assert schedule.monday is True
        assert schedule.sunday is False

    def test_schedule_tablename(self):
        assert Schedule.__tablename__ == "iot_schedule"

    def test_schedule_all_days(self):
        schedule = _make_schedule(
            monday=True, tuesday=True, wednesday=True,
            thursday=True, friday=True, saturday=True, sunday=True,
        )
        assert all([schedule.monday, schedule.tuesday, schedule.wednesday,
                     schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday])
