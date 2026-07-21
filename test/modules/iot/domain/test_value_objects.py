import contextlib

from app.modules.iot.domain.value_objects.alarm import (
    AlarmDetailDTO,
    AlarmDetailResult,
    InfluxDBConfig,
    Location,
    MQTTConfig,
)
from app.modules.iot.domain.value_objects.location import LocationConfig
from app.modules.iot.domain.value_objects.mqtt import MQTTDeviceInfo, MQTTTopicData


class TestAlarmDetailDTO:
    def test_create_with_defaults(self):
        dto = AlarmDetailDTO(hardware_id=1, value_data="25.5", value_alarm=0)
        assert dto.hardware_id == 1
        assert dto.value_data == "25.5"
        assert dto.value_alarm == 0
        assert dto.max_value is None
        assert dto.min_value is None
        assert dto.device_name == ""
        assert dto.unit == ""

    def test_create_with_all_fields(self):
        dto = AlarmDetailDTO(
            hardware_id=2,
            value_data="100",
            value_alarm="1",
            value_relay="ON",
            value_control_relay="OFF",
            max_value=50,
            min_value=10,
            status_alert=80,
            status_warning=60,
            recovery_warning=40,
            recovery_alert=30,
            device_name="Temp Sensor",
            action_name="relay1",
            mqtt_name="mqtt_temp",
            mqtt_control_on="ON",
            mqtt_control_off="OFF",
            count_alarm=3,
            event=1,
            unit="°C",
        )
        assert dto.hardware_id == 2
        assert dto.max_value == 50
        assert dto.device_name == "Temp Sensor"
        assert dto.count_alarm == 3

    def test_is_frozen(self):
        dto = AlarmDetailDTO(hardware_id=1, value_data="1", value_alarm=0)
        with contextlib.suppress(Exception):
            dto.hardware_id = 2
        assert dto.hardware_id == 1


class TestAlarmDetailResult:
    def test_create_with_required_fields(self):
        result = AlarmDetailResult(
            status=5,
            status_control=5,
            alarm_type_id=1,
            type_id=1,
            hardware_id=1,
            alarm_status_set=999,
            title="Normal",
            subject="Normal",
            content="Normal ",
            value_data="25.5",
            value_alarm=0,
            value_relay=None,
            value_control_relay=None,
            data_alarm=0,
            data_alarm_raw=0,
            max_value=0,
            min_value=0,
            event_control=0,
            message_mqtt_control="",
            sensor_data="25.5",
            count_alarm=0,
            mqtt_name="mqtt1",
            mqtt_name_str="mqtt1",
            device_name_str="Device1",
            mqtt_control_on_str="ON",
            unit="°C",
            sensor_value="25.5",
        )
        assert result.status == 5
        assert result.title == "Normal"
        assert result.hardware_id == 1


class TestMQTTConfig:
    def test_create(self):
        config = MQTTConfig(broker="localhost", client_id="test")
        assert config.broker == "localhost"
        assert config.keepalive == 30
        assert config.clean_session is True

    def test_is_frozen(self):
        config = MQTTConfig(broker="localhost")
        with contextlib.suppress(Exception):
            config.broker = "other"
        assert config.broker == "localhost"


class TestInfluxDBConfig:
    def test_create(self):
        config = InfluxDBConfig(url="http://localhost:8086", token="t", org="o", bucket="b")
        assert config.url == "http://localhost:8086"
        assert config.timeout == 30


class TestMQTTTopicData:
    def test_create(self):
        data = MQTTTopicData(topic="iot/data", payload={"temp": 25})
        assert data.topic == "iot/data"
        assert data.payload == {"temp": 25}
        assert data.timestamp == 0.0


class TestMQTTDeviceInfo:
    def test_create(self):
        info = MQTTDeviceInfo(device_id=1, topic="iot/1")
        assert info.device_id == 1
        assert info.name == ""


class TestLocationConfig:
    def test_create(self):
        loc = LocationConfig(location_id=1, location_name="Bangkok", latitude=13.7, longitude=100.5)
        assert loc.location_id == 1
        assert loc.latitude == 13.7


class TestLocation:
    def test_create(self):
        loc = Location(location_id=5, location_name="Office")
        assert loc.location_id == 5
