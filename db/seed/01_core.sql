-- ═══════════════════════════════════════════════════════════════
-- iot DEMO DATA — CORE (lookup + device)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- Tenant pool
CREATE TEMP TABLE _tenants(id uuid) ON COMMIT DROP;
INSERT INTO _tenants VALUES
    ('11111111-1111-1111-1111-111111111111'),
    ('22222222-2222-2222-2222-222222222222'),
    ('33333333-3333-3333-3333-333333333333');

-- ═══ sd_mqtt_host (10 rows) ══════════════════════════════════
INSERT INTO sd_mqtt_host
    (id, tenant_id, hostname, host, port, username, password,
     idhost, status, created_at, updated_at)
SELECT
    gen_random_uuid(),
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    'broker-' || i || '.iot.local',
    '10.0.0.' || i,
    '1883',
    'admin',
    'secret_pass',
    i,
    1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 10) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_mqtt (20 rows) ═══════════════════════════════════
INSERT INTO sd_iot_mqtt
    (tenant_id, mqtt_id, mqtt_type_id, sort, mqtt_name, host, port,
     username, password, secret, expire_in, token_value, org, bucket,
     envavorment, location_id, latitude, longitude, zoom, mqtt_main_id,
     configuration, status, created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    1,
    i,
    'MQTT-' || (ARRAY['AIRCOM1','AIRCOM2','BAACTW01','BAACTW02','CBKK01','CMONBUGKET01'])[1 + (i % 6)],
    '10.0.0.' || (i % 10 + 1),
    1883,
    'user',
    'pass',
    '',
    '3600',
    '',
    (ARRAY['ORG-A','ORG-B','ORG-C'])[1 + (i % 3)],
    (ARRAY['AIRCOM1','AIRCOM2','BAACTW01','BAACTW02','CBKK01','CMONBUGKET01'])[1 + (i % 6)],
    'production',
    (i % 30) + 1,
    '13.7563',
    '100.5018',
    12,
    (i % 10) + 1,
    '{"qos":1,"retain":false}',
    1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 20) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_location (30 rows) ═══════════════════════════════
INSERT INTO sd_iot_location
    (tenant_id, location_id, location_name, ipaddress,
     location_detail, configdata, status, created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    (ARRAY['Factory','Warehouse','Cold Room','Lab','Server Room'])[1 + (i % 5)]
        || ' ' || (ARRAY['A','B','C','D','E'])[1 + (i % 5)]
        || '-' || (i % 5 + 1) || (i % 8 + 1),
    '192.168.' || (i / 250 + 1) || '.' || (i % 250 + 1),
    'Building ' || (ARRAY['A','B','C','D','E'])[1 + (i % 5)],
    '{"lat":13.75,"lng":100.5}',
    1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 30) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_device_type (20 rows) ════════════════════════════
INSERT INTO sd_iot_device_type
    (tenant_id, type_id, type_name, status, created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    (ARRAY['Temperature','Humidity','Pressure','CO2','Door','Fire',
           'Gas','Vibration','Relay','UPS'])[1 + (i % 10)]
        || ' Sensor ' || i,
    1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 20) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_device_category (20 rows) ════════════════════════════
INSERT INTO sd_device_category
    (tenant_id, id, name, description, icon, created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    'Category ' || LPAD(i::text, 2, '0'),
    'Device category ' || i,
    'thermometer',
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 20) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_device_alarm_action (20 rows) ════════════════════
INSERT INTO sd_iot_device_alarm_action
    (tenant_id, alarm_action_id, action_name, status_warning, recovery_warning,
     status_alert, recovery_alert, email_alarm, line_alarm, telegram_alarm,
     sms_alarm, nonc_alarm, time_life, event, status, created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    'Alarm Action ' || i,
    '40', '38', '50', '45',
    (random() < 0.5)::int, (random() < 0.5)::int,
    (random() < 0.5)::int, (random() < 0.5)::int,
    0, 300, (random() < 0.5)::int, 1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 20) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_device (200 rows) ════════════════════════════════
INSERT INTO sd_iot_device
    (tenant_id, device_id, mqtt_id, setting_id, type_id, location_id,
     device_name, sn, hardware_id, status_warning, recovery_warning,
     status_alert, recovery_alert, time_life, period, work_status,
     "max", "min", model, vendor, comparevalue, unit, host_id, oid,
     action_id, status_alert_id, mqtt_data_value, mqtt_data_control,
     measurement, mqtt_control_on, mqtt_control_off, org, bucket, status,
     mqtt_device_name, mqtt_status_over_name, mqtt_status_data_name,
     mqtt_act_relay_name, mqtt_control_relay_name, layout, alert_set,
     icon_normal, icon_warning, icon_alert, icon, icon_on, icon_off,
     color_normal, color_warning, color_alert, code, menu,
     calibration_add, calibration_subtract, calibration_type,
     created_at, updated_at)
SELECT
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    i,
    (i % 20) + 1,
    0,
    (i % 20) + 1,
    (i % 30) + 1,
    (ARRAY['Temperature','Humidity','Pressure','CO2','Door','Fire',
           'Gas','Vibration','Relay','UPS'])[1 + (i % 10)]
        || ' Device ' || i,
    'SN-2024-' || LPAD(i::text, 5, '0'),
    (i % 4) + 1,
    '40', '38', '50', '45',
    300, '5m', 1,
    '60', '-10',
    (ARRAY['DHT22','BME280','SHT31','DS18B20','MQ-135','HC-SR501'])[1 + (i % 6)],
    (ARRAY['Sensirion','Bosch','Texas Instruments','Dallas','Winsen'])[1 + (i % 5)],
    '0',
    (ARRAY['°C','%','kPa','ppm','V','A','kW',''])[1 + (i % 8)],
    'host-' || ((i % 10) + 1),
    '1.3.6.1.4.1.' || i,
    (i % 20) + 1,
    (i % 20) + 1,
    (ARRAY['AIRCOM1','AIRCOM2','BAACTW01','BAACTW02','CBKK01','CMONBUGKET01'])[1 + (i % 6)] || '/DATA',
    (ARRAY['AIRCOM1','AIRCOM2','BAACTW01','BAACTW02','CBKK01','CMONBUGKET01'])[1 + (i % 6)] || '/CONTROL',
    (ARRAY['temperature','humidity','pressure','co2','door','fire',
           'gas','vibration','relay','ups'])[1 + (i % 10)],
    '1', '0',
    (ARRAY['ORG-A','ORG-B','ORG-C'])[1 + (i % 3)],
    (ARRAY['AIRCOM1','AIRCOM2','BAACTW01','BAACTW02','CBKK01','CMONBUGKET01'])[1 + (i % 6)],
    1,
    'dev-' || LPAD(i::text, 4, '0'),
    '{"0":"value"}',
    '{"0":"temperature"}',
    '{"0":"relay1"}',
    '{"0":"relay1"}',
    (i % 4) + 1,
    1,
    'icon-normal.png', 'icon-warning.png', 'icon-alert.png',
    'icon-normal.png', 'icon-on.png', 'icon-off.png',
    '#22C55E', '#F59E0B', '#EF4444',
    'normal', 1,
    '0', '0', 3,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 200) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_alarm_device (40 rows) ═══════════════════════════
INSERT INTO sd_iot_alarm_device
    (id, tenant_id, alarm_action_id, device_id, created_at, updated_at)
SELECT
    gen_random_uuid(),
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    (i % 20) + 1,
    ((i * 5) % 200) + 1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 40) AS i
ON CONFLICT DO NOTHING;

-- ═══ sd_iot_alarm_device_event (40 rows) ═════════════════════
INSERT INTO sd_iot_alarm_device_event
    (id, tenant_id, alarm_action_id, device_id, created_at, updated_at)
SELECT
    gen_random_uuid(),
    (SELECT id FROM _tenants ORDER BY id LIMIT 1 OFFSET (i % 3)),
    (i % 20) + 1,
    ((i * 7) % 200) + 1,
    NOW() - (random() * INTERVAL '90 days'),
    NOW()
FROM generate_series(1, 40) AS i
ON CONFLICT DO NOTHING;

COMMIT;