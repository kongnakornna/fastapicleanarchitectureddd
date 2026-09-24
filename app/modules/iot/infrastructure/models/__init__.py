"""iot entities — SQLAlchemy models (moved from infrastructure/models)

TH: entities ที่ใช้ SQLAlchemy — จัดกลุ่มตามโดเมน
EN: SQLAlchemy-based entities grouped by domain
"""
from app.modules.iot.infrastructure.models.common import BaseModel, StatusModel

from app.modules.iot.infrastructure.models.device import Device
from app.modules.iot.infrastructure.models.device_type import DeviceType
from app.modules.iot.infrastructure.models.device_status import DeviceStatus
from app.modules.iot.infrastructure.models.device_status_history import DeviceStatusHistory
from app.modules.iot.infrastructure.models.device_config import DeviceConfig
from app.modules.iot.infrastructure.models.device_alert import DeviceAlert
from app.modules.iot.infrastructure.models.device_category import DeviceCategory
from app.modules.iot.infrastructure.models.device_group import DeviceGroup
from app.modules.iot.infrastructure.models.device_group_member import DeviceGroupMember
from app.modules.iot.infrastructure.models.device_notification_config import DeviceNotificationConfig
from app.modules.iot.infrastructure.models.device_schedule import DeviceSchedule
from app.modules.iot.infrastructure.models.iot_data import IotData
from app.modules.iot.infrastructure.models.sensor_data import SensorData
from app.modules.iot.infrastructure.models.alarm import (
    DeviceAlarmAction, AlarmDevice, AlarmDeviceEvent,
)
from app.modules.iot.infrastructure.models.alarm_log import (
    AlarmProcessLog, AlarmProcessLogEmail, AlarmProcessLogTemp,
)
from app.modules.iot.infrastructure.models.activity_log import ActivityLog
from app.modules.iot.infrastructure.models.schedule import (
    IotScheduleDevice, Schedule, ScheduleProcessLog,
)
from app.modules.iot.infrastructure.models.location import Location
from app.modules.iot.infrastructure.models.mqtt import Mqtt
from app.modules.iot.infrastructure.models.mqtt_host import MqttHost

from app.modules.iot.infrastructure.models.air_control import AirControl
from app.modules.iot.infrastructure.models.air_control_device_map import AirControlDeviceMap
from app.modules.iot.infrastructure.models.air_control_log import AirControlLog
from app.modules.iot.infrastructure.models.air_mod import AirMod
from app.modules.iot.infrastructure.models.air_mod_device_map import AirModDeviceMap
from app.modules.iot.infrastructure.models.air_period import AirPeriod
from app.modules.iot.infrastructure.models.air_period_device_map import AirPeriodDeviceMap
from app.modules.iot.infrastructure.models.air_setting_warning import AirSettingWarning
from app.modules.iot.infrastructure.models.air_setting_warning_device_map import AirSettingWarningDeviceMap
from app.modules.iot.infrastructure.models.air_warning import AirWarning
from app.modules.iot.infrastructure.models.air_warning_device_map import AirWarningDeviceMap

from app.modules.iot.infrastructure.models.notification_channel import NotificationChannel
from app.modules.iot.infrastructure.models.notification_type import NotificationType
from app.modules.iot.infrastructure.models.notification_condition import NotificationCondition
from app.modules.iot.infrastructure.models.notification_log import NotificationLog
from app.modules.iot.infrastructure.models.group_notification_config import GroupNotificationConfig
from app.modules.iot.infrastructure.models.channel_template import ChannelTemplate

from app.modules.iot.infrastructure.models.report_data import ReportData
from app.modules.iot.infrastructure.models.system_setting import SystemSetting
from app.modules.iot.infrastructure.models.api_key import ApiKey
from app.modules.iot.infrastructure.models.audit_log import AuditLog
from app.modules.iot.infrastructure.models.command_log import CommandLog

__all__ = [
    "BaseModel", "StatusModel",
    "Device", "DeviceType", "DeviceStatus", "DeviceStatusHistory",
    "DeviceConfig", "DeviceAlert", "DeviceCategory",
    "DeviceGroup", "DeviceGroupMember",
    "DeviceNotificationConfig", "DeviceSchedule",
    "IotData", "SensorData",
    "DeviceAlarmAction", "AlarmDevice", "AlarmDeviceEvent",
    "AlarmProcessLog", "AlarmProcessLogEmail", "AlarmProcessLogTemp",
    "ActivityLog", "Schedule", "IotScheduleDevice", "ScheduleProcessLog",
    "Location", "Mqtt", "MqttHost",
    "AirControl", "AirControlDeviceMap", "AirControlLog",
    "AirMod", "AirModDeviceMap", "AirPeriod", "AirPeriodDeviceMap",
    "AirSettingWarning", "AirSettingWarningDeviceMap",
    "AirWarning", "AirWarningDeviceMap",
    "NotificationChannel", "NotificationType", "NotificationCondition",
    "NotificationLog", "GroupNotificationConfig", "ChannelTemplate",
    "ReportData", "SystemSetting", "ApiKey", "AuditLog", "CommandLog",
]
