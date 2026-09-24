"""
TH: Alembic environment — โหลด models ทั้งหมด + run migration
EN: Alembic environment — load all models + run migration
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# ═════════════════════════════════════════════════════════════════
# PATH SETUP
# ═════════════════════════════════════════════════════════════════
# TH: เพิ่ม project root เข้า sys.path เพื่อ import app.* ได้
# EN: add project root to sys.path so app.* imports work
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import pg_engine  # noqa: E402

# ═════════════════════════════════════════════════════════════════
# IMPORT BASE METADATA
# ═════════════════════════════════════════════════════════════════
# TH: BaseModel คือ declarative base — metadata ที่ Alembic จะ autogenerate
# EN: BaseModel is the declarative base — metadata for autogenerate
from app.modules.shared.infrastructure.models import BaseModel  # noqa: E402

# ═════════════════════════════════════════════════════════════════
# AUTO-REGISTERED MODELS
# ═════════════════════════════════════════════════════════════════
# TH: import ทุก model เพื่อให้ Alembic เห็น metadata
#     ใช้ try/except กัน module ที่ไม่มี models (pure VO / ไม่มีไฟล์)
# EN: import every model so Alembic sees the metadata
#     try/except for modules without models (pure VO / no file)

# --- module user ---
try:
    from app.modules.user.infrastructure.models import UserModel  # noqa: F401
except ImportError:
    pass

# --- module authentication ---
try:
    from app.modules.authentication.infrastructure.models import (  # noqa: F401
        AccessTokenModel,
        AuthenticationModel,
        RefreshTokenModel,
    )
except ImportError:
    pass

# --- module notification ---
try:
    from app.modules.notification.infrastructure.models import (  # noqa: F401
        NotificationModel,
    )
except ImportError:
    pass

# --- module money ---
# TH: money เป็น pure VO — ไม่มี DB models
# EN: money is a pure VO module — no DB models
try:
    from app.modules.money.infrastructure.models import MoneyModel  # noqa: F401
except ImportError:
    pass

# --- module audit ---
try:
    from app.modules.audit.infrastructure.models import AuditLogModel  # noqa: F401
except ImportError:
    pass

# --- module websocket (no DB models) ---
# TH: websocket ไม่มี DB models
# EN: websocket has no DB models

# --- module pdpa (Consent / DSAR / Privacy Policy / Cookie Consent) ---
# TH: PDPA module — 4 models ตามสเปค PDPA
# EN: PDPA module — 4 models per PDPA spec
try:
    from app.modules.pdpa.infrastructure.models import (  # noqa: F401
        ConsentLogModel,
        CookieConsentModel,
        DSARRequestModel,
        PrivacyPolicyModel,
    )
except ImportError:
    pass




# --- module llm (Provider / Model / Conversation / Message / UsageLog) ---
# TH: llm module — 5 models (Layer 5-Intel, schema=public, prefix=llm_)
# EN: llm module — 5 models (Layer 5-Intel, schema=public, prefix=llm_)
try:
    from app.modules.llm.infrastructure.models import (  # noqa: F401
        ConversationModel,
        MessageModel,
        ModelModel,
        ProviderModel,
        UsageLogModel,
    )
except ImportError:
    pass


# --- module iot (Device / Config / Status / Alert / Data / Alarm / Activity / Schedule) ---
# TH: iot module — 8 models (Layer 6-Monitor)
# EN: iot module — 8 models (Layer 6-Monitor)
try:
    from app.modules.iot.infrastructure.models import (  # noqa: F401
        ActivityLogModel,
        AlarmLogModel,
        DeviceAlertModel,
        DeviceConfigModel,
        DeviceModel,
        DeviceStatusModel,
        ScheduleModel,
        iotDataModel,
    )
except ImportError:
    pass


# ═════════════════════════════════════════════════════════════════
# ALEMBIC CONFIG
# ═════════════════════════════════════════════════════════════════

# --- iot module (48 models) ---
try:
    from app.modules.iot.infrastructure.models import (  # noqa: F401
        Device, DeviceType, DeviceStatus, DeviceStatusHistory,
        DeviceConfig, DeviceAlert, DeviceCategory,
        DeviceGroup, DeviceGroupMember, DeviceNotificationConfig,
        DeviceSchedule, IotData, SensorData,
        DeviceAlarmAction, AlarmDevice, AlarmDeviceEvent,
        AlarmProcessLog, AlarmProcessLogEmail, AlarmProcessLogTemp,
        ActivityLog, Schedule, IotScheduleDevice, ScheduleProcessLog,
        Location, Mqtt, MqttHost,
        AirControl, AirControlDeviceMap, AirControlLog,
        AirMod, AirModDeviceMap, AirPeriod, AirPeriodDeviceMap,
        AirSettingWarning, AirSettingWarningDeviceMap,
        AirWarning, AirWarningDeviceMap,
        NotificationChannel, NotificationType, NotificationCondition,
        NotificationLog, GroupNotificationConfig, ChannelTemplate,
        ReportData, SystemSetting, ApiKey, AuditLog, CommandLog,
    )
except ImportError:
    pass

# --- fullschedule module (8 models) ---
try:
    from app.modules.fullschedule.models import (  # noqa: F401
        Schedule as FsSchedule,
        ScheduleDevice as FsScheduleDevice,
        ScheduleHistory as FsScheduleHistory,
        ScheduleSetting as FsScheduleSetting,
        Group as FsGroup,
        Zone as FsZone,
        Area as FsArea,
        AreaDevice as FsAreaDevice,
    )
except ImportError:
    pass



# ─── module: fullschedule ───
try:
    from app.modules.fullschedule.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.fullschedule.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.fullschedule.models  # noqa: F401
        except ImportError:
            pass

# ─── module: health ───
try:
    from app.modules.health.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.health.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.health.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# ─── module: iot ───
try:
    from app.modules.iot.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.iot.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.iot.infrastructure.models  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.activity_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.api_key  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.audit_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.channel_template  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.command_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_alert  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_category  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group_member  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status_history  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.group_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.iot_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.location  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt_host  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_channel  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_condition  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.report_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.sensor_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.system_setting  # noqa: F401
        except ImportError:
            pass

# ─── module: pdpa ───
try:
    from app.modules.pdpa.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.pdpa.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.pdpa.infrastructure.models  # noqa: F401
        except ImportError:
            pass



# ─── module: fullschedule ───
try:
    from app.modules.fullschedule.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.fullschedule.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.fullschedule.models  # noqa: F401
        except ImportError:
            pass

# ─── module: health ───
try:
    from app.modules.health.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.health.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.health.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# ─── module: iot ───
try:
    from app.modules.iot.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.iot.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.iot.infrastructure.models  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.activity_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.api_key  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.audit_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.channel_template  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.command_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_alert  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_category  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group_member  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status_history  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.group_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.iot_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.location  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt_host  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_channel  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_condition  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.report_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.sensor_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.system_setting  # noqa: F401
        except ImportError:
            pass

# ─── module: pdpa ───
try:
    from app.modules.pdpa.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.pdpa.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.pdpa.infrastructure.models  # noqa: F401
        except ImportError:
            pass



# ─── module: fullschedule ───
try:
    from app.modules.fullschedule.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.fullschedule.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.fullschedule.models  # noqa: F401
        except ImportError:
            pass

# ─── module: health ───
try:
    from app.modules.health.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.health.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.health.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# ─── module: iot ───
try:
    from app.modules.iot.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.iot.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.iot.infrastructure.models  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.activity_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.api_key  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.audit_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.channel_template  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.command_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_alert  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_category  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group_member  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status_history  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.group_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.iot_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.location  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt_host  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_channel  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_condition  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.report_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.sensor_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.system_setting  # noqa: F401
        except ImportError:
            pass

# ─── module: pdpa ───
try:
    from app.modules.pdpa.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.pdpa.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.pdpa.infrastructure.models  # noqa: F401
        except ImportError:
            pass



# ─── module: fullschedule ───
try:
    from app.modules.fullschedule.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.fullschedule.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.fullschedule.models  # noqa: F401
        except ImportError:
            pass

# ─── module: health ───
try:
    from app.modules.health.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.health.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.health.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# ─── module: iot ───
try:
    from app.modules.iot.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.iot.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.iot.infrastructure.models  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.activity_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.api_key  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.audit_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.channel_template  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.command_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_alert  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_category  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group_member  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status_history  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.group_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.iot_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.location  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt_host  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_channel  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_condition  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.report_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.sensor_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.system_setting  # noqa: F401
        except ImportError:
            pass

# ─── module: pdpa ───
try:
    from app.modules.pdpa.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.pdpa.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.pdpa.infrastructure.models  # noqa: F401
        except ImportError:
            pass


# ==========================================================
# AUTO-GENERATED — import all models for Alembic
# ==========================================================

# ─── module: fullschedule ───
try:
    from app.modules.fullschedule.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.fullschedule.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.fullschedule.models  # noqa: F401
        except ImportError:
            pass

# ─── module: health ───
try:
    from app.modules.health.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.health.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.health.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# ─── module: iot ───
try:
    from app.modules.iot.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.iot.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.iot.infrastructure.models  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.activity_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_control_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_mod_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_period_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_setting_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.air_warning_device_map  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.alarm_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.api_key  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.audit_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.channel_template  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.command_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_alert  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_category  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_group_member  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_status_history  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.device_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.group_notification_config  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.iot_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.location  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.mqtt_host  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_channel  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_condition  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_log  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.notification_type  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.report_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.schedule  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.sensor_data  # noqa: F401
        except ImportError:
            pass
        try:
            import app.modules.iot.infrastructure.models.system_setting  # noqa: F401
        except ImportError:
            pass

# ─── module: pdpa ───
try:
    from app.modules.pdpa.infrastructure.models import *  # noqa: F401,F403
except ImportError:
    try:
        from app.modules.pdpa.domain.entities import *  # noqa: F401,F403
    except ImportError:
        try:
            import app.modules.pdpa.infrastructure.models  # noqa: F401
        except ImportError:
            pass

# --- module vector_db ---
try:
    from app.modules.vector_db.infrastructure.models import (  # noqa: F401
        VDBCollectionModel,
        VDBIndexModel,
        VDBNamespaceModel,
        VDBStatsModel,
        VDBVectorModel,
    )
except ImportError:
    pass

# --- module tool_calling (ToolDefinition / ToolRegistration / ToolInvocation / ToolPermission) ---
# TH: tool_calling — 4 models (Layer 5-Intel, schema=public, prefix=tool_)
# EN: tool_calling — 4 models
try:
    from app.modules.tool_calling.infrastructure.models import (  # noqa: F401
        ToolDefinitionModel,
        ToolInvocationModel,
        ToolPermissionModel,
        ToolRegistrationModel,
    )
except ImportError:
    pass


# --- module structured_outputs ---
try:
    from app.modules.structured_outputs.infrastructure.models import (  # noqa: F401
        SOOutputModel,
        SORepairModel,
        SORequestModel,
        SOSchemaModel,
        SOValidationModel,
    )
except ImportError:
    pass

# --- module hybrid_search ---
try:
    from app.modules.hybrid_search.infrastructure.models import (  # noqa: F401
        HSConfigModel,
        HSQueryModel,
        HSRankingModel,
        HSRerankLogModel,
        HSResultModel,
    )
except ImportError:
    pass

# --- module langchain ---
try:
    from app.modules.langchain.infrastructure.models import (  # noqa: F401
        LCAgentModel,
        LCChainModel,
        LCMemoryModel,
        LCRunModel,
        LCTraceModel,
    )
except ImportError:
    pass

# --- module llamaindex ---
try:
    from app.modules.llamaindex.infrastructure.models import (  # noqa: F401
        LIDocumentModel,
        LIIndexModel,
        LINodeModel,
        LIQueryEngineModel,
        LIRunModel,
    )
except ImportError:
    pass

# --- module rag ---
try:
    from app.modules.rag.infrastructure.models import (  # noqa: F401
        RAGChunkModel,
        RAGCitationModel,
        RAGDocumentModel,
        RAGPipelineModel,
        RAGRetrievalLogModel,
        RAGRunModel,
    )
except ImportError:
    pass

# --- module ai_evaluation ---
try:
    from app.modules.ai_evaluation.infrastructure.models import (  # noqa: F401
        EvalDatasetModel,
        EvalMetricModel,
        EvalReportModel,
        EvalResultModel,
        EvalRunModel,
        EvalTestCaseModel,
    )
except ImportError:
    pass

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TH: metadata ที่ Alembic ใช้ autogenerate
# EN: metadata used by Alembic for autogenerate
target_metadata = BaseModel.metadata


# ═════════════════════════════════════════════════════════════════
# RUN MIGRATIONS
# ═════════════════════════════════════════════════════════════════
def run_migrations_offline() -> None:
    """TH: run migration แบบ offline (generate SQL) | EN: offline mode"""
    url = pg_engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """TH: run migration แบบ online (ต่อ DB จริง) | EN: online mode"""
    with pg_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
