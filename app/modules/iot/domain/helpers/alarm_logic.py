"""Alarm evaluation logic - translated from Go: pkg/helpers/iot.go

Evaluates alarm thresholds and generates alarm results based on hardware type,
sensor values, and configured thresholds.
"""

from __future__ import annotations

from typing import Any

from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO, AlarmDetailResult

_THAI_MESSAGES: dict[str, str] = {
    "warning": "คำเตือน มีความผิดปกติ",
    "critical": "ภาวะวิกฤตต้องแก้ไขทันที",
    "recovery_warning": "คืนสู่ภาวะปกติ (คำเตือน)",
    "recovery_critical": "คืนสู่ภาวะปกติ (วิกฤต)",
    "normal": "ปกติ",
    "critical_max": "วิกฤต มีค่าสูงเกินกำหนด",
    "critical_min": "วิกฤต มีค่าต่ำกว่ากำหนด",
}

_ENGLISH_MESSAGES: dict[str, str] = {
    "warning": "Warning",
    "critical": "Critical",
    "recovery_warning": "Recovery Warning",
    "recovery_critical": "Recovery Critical",
    "normal": "Normal",
    "critical_max": "Critical! Maximum limit.",
    "critical_min": "Critical! Minimum limit",
}


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return 0


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _normalize_sensor_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.upper() in ("ON", "OFF"):
            return value.upper()
        try:
            return float(value)
        except ValueError:
            return value
    return value


def evaluate_alarm(dto: AlarmDetailDTO, lang: str = "th") -> AlarmDetailResult:
    """Main alarm evaluation function.

    Translated from Go: pkg/helpers/iot.go processAlarmDetail()

    Args:
        dto: Alarm detail input data
        lang: Language for messages ('th' for Thai, 'en' for English)

    Returns:
        AlarmDetailResult with evaluation results
    """
    messages = _THAI_MESSAGES if lang == "th" else _ENGLISH_MESSAGES

    hardware_id = _to_int(dto.hardware_id)
    type_id = hardware_id

    sensor_value = _normalize_sensor_value(dto.value_data)
    max_val = _to_float(dto.max_value)
    min_val = _to_float(dto.min_value)
    status_alert = _to_int(dto.status_alert)
    status_warning = _to_int(dto.status_warning)
    recovery_warning = _to_int(dto.recovery_warning)
    recovery_alert = _to_int(dto.recovery_alert)
    count_alarm = _to_int(dto.count_alarm)
    event = _to_int(dto.event)

    unit = dto.unit
    mqtt_name = dto.mqtt_name
    device_name = dto.device_name
    alarm_action_name = dto.action_name
    mqtt_control_on = dto.mqtt_control_on
    mqtt_control_off = dto.mqtt_control_off
    value_alarm = dto.value_alarm
    value_relay = dto.value_relay
    value_control_relay = dto.value_control_relay

    sensor_data: Any = None
    value_data: Any = None

    # Determine sensor data based on hardware type
    if hardware_id == 1:
        sensor_data = dto.value_data
        value_data = dto.value_data
    elif hardware_id == 2:
        if _to_int(dto.value_alarm) == 1:
            sensor_data = 1
            value_data = 1
            sensor_value = 1
        else:
            sensor_data = _to_int(dto.value_alarm)
            value_data = _to_int(dto.value_alarm)
            sensor_value = _to_int(dto.value_alarm)
    elif hardware_id == 3:
        sensor_data = _to_int(dto.value_alarm)
        value_data = dto.value_data
        sensor_value = dto.value_data
    elif hardware_id == 4:
        sensor_data = dto.value_data
        value_data = dto.value_data
    else:
        sensor_data = _to_int(dto.value_alarm)
        value_data = dto.value_data

    alarm_status_set = 999
    data_alarm = 0
    data_alarm_raw = 0
    event_control = event
    message_mqtt_control = mqtt_control_off
    if event == 1:
        message_mqtt_control = mqtt_control_on

    status = 5
    title = messages["normal"]
    subject = messages["normal"]
    content = messages["normal"] + " "

    # --- Evaluation rules (matching Go logic exactly) ---

    if hardware_id == 3 and sensor_value in (1, 0, "ON", "OFF", "on", "off"):
        # Relay: ON/OFF is normal
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = f"{messages['normal']} {sensor_value} {unit}"
        status = 5

    elif hardware_id == 4 and sensor_value != 1:
        # Alarm sensor: non-1 value is critical
        alarm_status_set = 2
        title = messages["critical"]
        subject = (
            f"{mqtt_name} {messages['critical']} {device_name}"
            f" : {sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['critical']}"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 2

    elif hardware_id == 4 and sensor_value == 1:
        # Alarm sensor: value 1 is normal
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = f"{messages['normal']} {sensor_value} {unit}"
        status = 5

    elif (
        max_val != 0
        and _to_float(sensor_value) >= max_val
        and hardware_id in (1, 2)
    ):
        # Exceeds maximum threshold
        alarm_status_set = 2
        title = messages["critical_max"]
        subject = (
            f"{mqtt_name} {messages['critical_max']} {device_name}"
            f" : {sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['critical_max']}"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 2

    elif (
        min_val != 0
        and _to_float(sensor_value) <= min_val
        and hardware_id in (1, 2)
    ):
        # Below minimum threshold
        alarm_status_set = 1
        title = messages["critical_min"]
        subject = (
            f"{mqtt_name} {messages['critical_min']} {device_name}"
            f" : {sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['critical_min']}"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 1

    elif (
        hardware_id == 1
        and status_warning > 0
        and _to_float(sensor_value) >= float(status_warning)
        and _to_float(sensor_value) < float(status_alert)
    ):
        # Warning threshold range
        alarm_status_set = 1
        title = messages["warning"]
        subject = (
            f"{mqtt_name} {messages['warning']} : {device_name}"
            f" : {sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['warning']}:"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 1

    elif (
        hardware_id == 1
        and status_alert > 0
        and _to_float(sensor_value) >= float(status_alert)
    ):
        # Alert threshold exceeded
        alarm_status_set = 2
        title = messages["critical"]
        subject = (
            f"{mqtt_name} {messages['critical']} : {device_name}"
            f" :{sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['critical']}:"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = status_alert
        data_alarm_raw = status_alert
        status = 2

    elif _to_int(value_alarm) == 0 and hardware_id in (2, 3, 4):
        # Digital sensor alarm triggered
        is_critical = hardware_id == 4
        if is_critical:
            alarm_status_set = 2
            title = messages["critical"]
        else:
            alarm_status_set = 1
            title = messages["warning"]
        subject = (
            f"{mqtt_name} {title} : {device_name}"
            f" : {sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {title}:"
            f" {device_name} :{sensor_value} {unit}"
        )
        if is_critical:
            data_alarm = status_alert
            data_alarm_raw = status_alert
        else:
            data_alarm = status_warning
            data_alarm_raw = status_warning
        status = 2 if is_critical else 1

    elif (
        count_alarm >= 1
        and recovery_warning > 0
        and _to_float(sensor_value) <= float(recovery_warning)
        and hardware_id in (1, 2)
    ):
        # Recovery from warning
        alarm_status_set = 3
        title = messages["recovery_warning"]
        subject = (
            f"{mqtt_name} {messages['recovery_warning']} : {device_name}"
            f" :{sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['recovery_warning']}:"
            f" {device_name} :{sensor_value} {unit}"
        )
        data_alarm = recovery_warning
        data_alarm_raw = recovery_warning
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 3

    elif (
        count_alarm >= 1
        and recovery_alert > 0
        and _to_float(sensor_value) <= float(recovery_alert)
        and hardware_id in (1, 2)
    ):
        # Recovery from critical
        alarm_status_set = 4
        title = f"{mqtt_name} {messages['recovery_critical']}"
        subject = (
            f"{mqtt_name} {messages['recovery_critical']} :{device_name}"
            f" :{sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']}"
            f" :{device_name} :{sensor_value} {unit}"
        )
        data_alarm = recovery_alert
        data_alarm_raw = recovery_alert
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 4

    elif (
        count_alarm >= 1
        and _to_int(value_alarm) >= 1
        and hardware_id in (2, 3, 4)
    ):
        # Digital sensor recovery
        alarm_status_set = 4
        title = f"{mqtt_name} {messages['recovery_critical']}"
        subject = (
            f"{mqtt_name} {messages['recovery_critical']} :{device_name}"
            f" :{sensor_value} {unit}"
        )
        content = (
            f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']}"
            f" :{device_name} :{sensor_value} {unit}"
        )
        data_alarm = recovery_alert
        data_alarm_raw = recovery_alert
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 4

    else:
        # Normal state
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = messages["normal"] + " "
        data_alarm = 0
        data_alarm_raw = 0
        status = 5

    return AlarmDetailResult(
        status=status,
        status_control=status,
        alarm_type_id=hardware_id,
        type_id=type_id,
        hardware_id=hardware_id,
        alarm_status_set=alarm_status_set,
        title=title,
        subject=subject,
        content=content,
        value_data=value_data,
        value_alarm=value_alarm,
        value_relay=value_relay,
        value_control_relay=value_control_relay,
        data_alarm=data_alarm,
        data_alarm_raw=data_alarm_raw,
        max_value=max_val,
        min_value=min_val,
        event_control=event_control,
        message_mqtt_control=message_mqtt_control,
        sensor_data=sensor_data,
        count_alarm=count_alarm,
        mqtt_name=mqtt_name,
        mqtt_name_str=mqtt_name,
        device_name_str=device_name,
        mqtt_control_on_str=mqtt_control_on,
        unit=unit,
        sensor_value=sensor_value,
        status_alert_val=status_alert,
        status_warning_val=status_warning,
        recovery_warning_val=recovery_warning,
        recovery_alert_val=recovery_alert,
        device_name_val=device_name,
        alarm_action_name=alarm_action_name,
        mqtt_control_on_val=mqtt_control_on,
        mqtt_control_off_val=mqtt_control_off,
        event_val=event,
        timestamp="",
        lang=lang,
    )
