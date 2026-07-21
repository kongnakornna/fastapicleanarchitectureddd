# Database Setup Guide
## IoT Module - PostgreSQL + InfluxDB

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├──────────────┬──────────────┬──────────────┬────────────┤
│  PostgreSQL  │   InfluxDB   │    Redis     │    MQTT    │
│  (Relational)│ (Time-Series)│   (Cache)    │ (Messages) │
├──────────────┼──────────────┼──────────────┼────────────┤
│  IoT tables  │  Sensor data │  MQTT cache  │  IoT data  │
│  User/Auth   │  Time series │  Session     │  Device    │
│  RBAC        │  Statistics  │  Blacklist   │  Control   │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### Database Responsibilities

| Database | Purpose | Data |
|----------|---------|------|
| PostgreSQL | Transactional data | Devices, configs, alerts, logs, users |
| InfluxDB | Time-series sensor data | Temperature, humidity, sensor readings |
| Redis | Cache + session | MQTT topic cache, token blacklist |

---

## 2. PostgreSQL Setup

### 2.1 Existing Tables (from fastapiddd)

```sql
-- Already exist via Alembic migrations
users
sessions
access_tokens
refresh_tokens
roles
permissions
user_roles
role_permissions
alembic_version
```

### 2.2 New Tables (IoT Module)

```sql
-- IoT Module Tables

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    hardware_id INTEGER NOT NULL,
    device_name VARCHAR(255) NOT NULL,
    device_type VARCHAR(100),
    location_id INTEGER,
    location_name VARCHAR(255),
    mqtt_topic VARCHAR(500),
    mqtt_name VARCHAR(255),
    unit VARCHAR(50),
    status VARCHAR(50) DEFAULT 'offline',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_configs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    max_value NUMERIC,
    min_value NUMERIC,
    warning_threshold NUMERIC,
    alert_threshold NUMERIC,
    recovery_warning NUMERIC,
    recovery_alert NUMERIC,
    calibration_offset NUMERIC DEFAULT 0,
    calibration_multiplier NUMERIC DEFAULT 1,
    mqtt_control_on VARCHAR(255),
    mqtt_control_off VARCHAR(255),
    action_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_statuses (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    status VARCHAR(50),
    last_value NUMERIC,
    last_seen TIMESTAMP,
    event INTEGER DEFAULT 0,
    count_alarm INTEGER DEFAULT 0,
    is_online BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alarm_status INTEGER DEFAULT 0,
    alarm_type INTEGER DEFAULT 0,
    value_data NUMERIC,
    value_alarm NUMERIC,
    title VARCHAR(255),
    subject TEXT,
    content TEXT,
    data_alarm INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS iot_data (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    hardware_id INTEGER,
    value_data NUMERIC,
    value_alarm NUMERIC,
    value_relay NUMERIC,
    unit VARCHAR(50),
    mqtt_topic VARCHAR(500),
    recorded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alarm_logs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alarm_status INTEGER,
    alarm_type INTEGER,
    value_data NUMERIC,
    value_alarm NUMERIC,
    title VARCHAR(255),
    subject TEXT,
    content TEXT,
    data_alarm INTEGER,
    data_alarm_raw INTEGER,
    event_control INTEGER DEFAULT 0,
    message_mqtt_control TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER,
    user_id INTEGER,
    action VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS command_logs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    command VARCHAR(255),
    payload TEXT,
    status VARCHAR(50),
    response TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_status_histories (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    status VARCHAR(50),
    previous_status VARCHAR(50),
    value_data NUMERIC,
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    schedule_name VARCHAR(255),
    cron_expression VARCHAR(100),
    action_type VARCHAR(50),
    action_payload TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.3 Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_devices_hardware_id ON devices(hardware_id);
CREATE INDEX IF NOT EXISTS idx_devices_location ON devices(location_id);
CREATE INDEX IF NOT EXISTS idx_devices_mqtt_topic ON devices(mqtt_topic);
CREATE INDEX IF NOT EXISTS idx_device_configs_device_id ON device_configs(device_id);
CREATE INDEX IF NOT EXISTS idx_device_statuses_device_id ON device_statuses(device_id);
CREATE INDEX IF NOT EXISTS idx_device_alerts_device_id ON device_alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_iot_data_device_id ON iot_data(device_id);
CREATE INDEX IF NOT EXISTS idx_iot_data_recorded_at ON iot_data(recorded_at);
CREATE INDEX IF NOT EXISTS idx_alarm_logs_device_id ON alarm_logs(device_id);
CREATE INDEX IF NOT EXISTS idx_alarm_logs_created_at ON alarm_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_device_id ON activity_logs(device_id);
CREATE INDEX IF NOT EXISTS idx_command_logs_device_id ON command_logs(device_id);
```

---

## 3. InfluxDB Setup

### 3.1 Bucket Configuration

```
Bucket: iot_sensors
Retention: 90 days (or as needed)
Org: your-org
```

### 3.2 Measurement Schema

```
Measurement: sensor_data
Tags:
  - device_id: string
  - hardware_id: string
  - location: string
Fields:
  - value: float
  - unit: string
  - status: string
Timestamp: nanosecond precision
```

### 3.3 Flux Query Examples

```flux
// Get latest sensor data for a device
from(bucket: "iot_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["device_id"] == "123")
  |> filter(fn: (r) => r["_field"] == "value")
  |> last()

// Get sensor data for chart (aggregated)
from(bucket: "iot_sensors")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["device_id"] == "123")
  |> filter(fn: (r) => r["_field"] == "value")
  |> aggregateWindow(every: 15m, fn: mean, createEmpty: false)
  |> yield(name: "chart_data")

// Count data points
from(bucket: "iot_sensors")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["device_id"] == "123")
  |> filter(fn: (r) => r["_field"] == "value")
  |> count()
```

---

## 4. Redis Setup

### 4.1 Cache Strategy

```
Key Pattern: mqtt:topic:{topic}
TTL: 5 seconds (for real-time MQTT data)
Value: JSON serialized sensor data

Key Pattern: mqtt:device:{device_id}:status
TTL: 30 seconds
Value: JSON serialized device status
```

### 4.2 Redis Config

```env
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=5
```

---

## 5. Environment Setup

### 5.1 docker-compose.yaml (additions)

```yaml
services:
  # Existing services...

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: admin12345678
      DOCKER_INFLUXDB_INIT_ORG: my-org
      DOCKER_INFLUXDB_INIT_BUCKET: iot_sensors
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: my-super-secret-token
    volumes:
      - influxdb_data:/var/lib/influxdb2

  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log

volumes:
  influxdb_data:
```

### 5.2 .env Additions

```env
# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-super-secret-token
INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=iot_sensors
INFLUXDB_TIMEOUT=30

# MQTT
MQTT_BROKER=tcp://localhost:1883
MQTT_CLIENT_ID=fastapi-iot-client
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=30
MQTT_CLEAN_SESSION=true
```

---

## 6. Alembic Migration

### 6.1 Create Migration

```bash
cd C:\github\fastapiddd
alembic revision --autogenerate -m "add_iot_module_tables"
alembic upgrade head
```

### 6.2 Migration File Structure

```python
# migrations/versions/xxxx_add_iot_module_tables.py

def upgrade() -> None:
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hardware_id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(255), nullable=False),
        # ... all columns
    )
    # Create other tables...
    # Create indexes...

def downgrade() -> None:
    op.drop_table('schedules')
    op.drop_table('command_logs')
    op.drop_table('device_status_histories')
    op.drop_table('alarm_logs')
    op.drop_table('activity_logs')
    op.drop_table('iot_data')
    op.drop_table('device_alerts')
    op.drop_table('device_statuses')
    op.drop_table('device_configs')
    op.drop_table('devices')
```

---

## 7. Data Flow

```
MQTT Broker
    │
    ▼
MQTT Client (subscribe)
    │
    ├──→ Redis Cache (5s TTL)
    │
    ├──→ InfluxDB (sensor time-series)
    │
    └──→ PostgreSQL (device state, alerts, logs)
              │
              ▼
         FastAPI REST API
              │
              ▼
         Client Application
```

---

## 8. Seed Data

### 8.1 Sample Devices

```sql
INSERT INTO devices (hardware_id, device_name, device_type, mqtt_topic, unit)
VALUES
    (1, 'Temperature Sensor', 'sensor', 'iot/device/temp001', '°C'),
    (2, 'Humidity Sensor', 'sensor', 'iot/device/hum001', '%'),
    (3, 'Relay Control', 'actuator', 'iot/device/relay001', 'ON/OFF'),
    (4, 'Alarm Sensor', 'sensor', 'iot/device/alarm001', '');
```

---

## 9. Verification

```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d fastapi_db -c "\dt device*"

# Test InfluxDB
curl -H "Authorization: Token my-super-secret-token" \
  http://localhost:8086/api/v2/query?org=my-org \
  --data-urlencode 'query=from(bucket:"iot_sensors") |> range(start: -1h) |> limit(n:5)'

# Test Redis
redis-cli -n 0 keys "mqtt:*"

# Test MQTT
mosquitto_sub -h localhost -t "iot/device/#" -v
```
