# Database Schema

PostgreSQL schema for the ICMON Auto Repair system. All tables inherit from `BaseModel` which provides `id` (UUID PK), `is_active` (boolean), `created_at` (timestamptz), and `updated_at` (timestamptz) columns.

---

## Shared Base Columns

Every table has these columns (inherited from `BaseModel`):

| Column      | Type             | Default              | Description                     |
|-------------|------------------|----------------------|---------------------------------|
| `id`        | UUID             | `gen_random_uuid()`  | Primary key                     |
| `is_active` | Boolean          | `true`               | Soft-delete flag                |
| `created_at`| DateTime(tz)     | `now()`              | Record creation timestamp       |
| `updated_at`| DateTime(tz)     | `now()` (onupdate)   | Last update timestamp           |

---

## Authentication Module

### `{prefix}_sessions`

Stores active user sessions (one per device/user-agent combo).

| Column           | Type         | Constraints                    | Description                       |
|------------------|--------------|--------------------------------|-----------------------------------|
| `id`             | UUID         | PK, `gen_random_uuid()`       | Session ID                        |
| `user_id`        | UUID         | FK -> `{prefix}_users.id` ON DELETE CASCADE | Owner user          |
| `ip_address`     | VARCHAR(45)  | NOT NULL                       | Client IP address                 |
| `device`         | VARCHAR(255) | NOT NULL                       | Device name                       |
| `user_agent`     | TEXT         | NOT NULL                       | User agent string                 |
| `accept_language`| VARCHAR(255) | NULLABLE                       | Accept-Language header            |
| `accept_encoding`| VARCHAR(255) | NULLABLE                       | Accept-Encoding header            |
| `origin`         | VARCHAR(255) | NULLABLE                       | Origin header                     |
| `referrer`       | VARCHAR(255) | NOT NULL                       | Referrer header                   |
| `location`       | VARCHAR(255) | NULLABLE                       | Approximate geo location          |
| `created_at`     | DateTime(tz) | NOT NULL                       | Session creation time             |
| `last_updated_at`| DateTime(tz) | NOT NULL                       | Last activity time                |
| `blacklisted`    | Boolean      | NOT NULL, default `false`      | Is session revoked                |

**Constraints:** UNIQUE(`user_id`, `user_agent`, `device`)

**Indexes:** `ix_sessions_user_id_user_agent_device`

---

### `{prefix}_refresh_tokens`

Refresh tokens linked to sessions. Supports token rotation.

| Column              | Type         | Constraints                           | Description              |
|---------------------|--------------|---------------------------------------|--------------------------|
| `id`                | UUID         | PK, `gen_random_uuid()`              | Refresh token ID         |
| `session_id`        | UUID         | FK -> `{prefix}_sessions.id` ON DELETE CASCADE, UNIQUE | Session link |
| `hashed_jti`        | TEXT         | NOT NULL, UNIQUE                      | Hashed JWT ID            |
| `previous_hashed_jti`| TEXT        | NULLABLE                              | Previous token's hashed JTI |
| `created_at`        | DateTime(tz) | NOT NULL                              | Creation time            |
| `updated_at`        | DateTime(tz) | NOT NULL                              | Last update time         |
| `expires_at`        | DateTime(tz) | NOT NULL                              | Expiration time          |
| `revoked`           | Boolean      | NOT NULL, default `false`            | Is revoked               |
| `revoked_at`        | DateTime(tz) | NULLABLE                              | Revocation time          |

**Indexes:** `ix_hashed_jti_revoked` (`hashed_jti`, `revoked`)

---

### `{prefix}_access_tokens`

Access tokens linked to refresh tokens. Stores permission level.

| Column              | Type         | Constraints                              | Description           |
|---------------------|--------------|------------------------------------------|-----------------------|
| `id`                | UUID         | PK, `gen_random_uuid()`                 | Access token ID       |
| `refresh_id`        | UUID         | FK -> `{prefix}_refresh_tokens.id` ON DELETE CASCADE, UNIQUE | Parent refresh token |
| `hashed_jti`        | TEXT         | NOT NULL, UNIQUE                         | Hashed JWT ID         |
| `previous_hashed_jti`| TEXT        | NULLABLE, UNIQUE                         | Previous token's JTI  |
| `permission`        | role_enum    | NOT NULL, default `user`                 | Role: admin/manager/user |
| `created_at`        | DateTime(tz) | NOT NULL                                 | Creation time         |
| `expires_at`        | DateTime(tz) | NOT NULL                                 | Expiration time       |
| `revoked`           | Boolean      | NOT NULL, default `false`               | Is revoked            |
| `revoked_at`        | DateTime(tz) | NULLABLE                                 | Revocation time       |

**Indexes:** `ix_hashed_jti_revoked` (`hashed_jti`, `revoked`)

---

## User Module

### `{prefix}_users`

| Column            | Type          | Constraints                    | Description               |
|-------------------|---------------|--------------------------------|---------------------------|
| `id`              | UUID          | PK (inherited)                 | User ID                   |
| `first_name`      | VARCHAR(100)  | NOT NULL                       | First name                |
| `last_name`       | VARCHAR(100)  | NOT NULL                       | Last name                 |
| `preferred_name`  | VARCHAR(100)  | NOT NULL                       | Preferred/display name    |
| `gender`          | gender_enum   | NOT NULL                       | MALE/FEMALE/OTHER         |
| `birthdate`       | DATE          | NOT NULL                       | Date of birth             |
| `email`           | VARCHAR(255)  | NOT NULL                       | Email address             |
| `username`        | VARCHAR(100)  | NOT NULL                       | Unique username           |
| `phone`           | VARCHAR(18)   | NULLABLE                       | Phone number              |
| `hashed_password` | VARCHAR(255)  | NOT NULL                       | Argon2 hashed password    |
| `role`            | role_enum     | NOT NULL, default `user`       | admin/manager/user        |
| `status`          | user_status_enum | NOT NULL, default `active`   | active/inactive/suspended |
| `is_active`       | Boolean       | (inherited)                    | Soft-delete flag          |
| `created_at`      | DateTime(tz)  | (inherited)                    | Creation timestamp        |
| `updated_at`      | DateTime(tz)  | (inherited)                    | Last update timestamp     |

**Constraints:**
- UNIQUE(`email`, `status`)
- UNIQUE(`username`, `status`)

---

### `{prefix}_roles`

| Column        | Type         | Constraints         | Description    |
|---------------|--------------|---------------------|----------------|
| `id`          | UUID         | PK (inherited)      | Role ID        |
| `name`        | VARCHAR(100) | NOT NULL, UNIQUE    | Role name      |
| `description` | TEXT         | NULLABLE            | Role description |

---

### `{prefix}_permissions`

| Column        | Type         | Constraints         | Description                          |
|---------------|--------------|---------------------|--------------------------------------|
| `id`          | UUID         | PK (inherited)      | Permission ID                        |
| `name`        | VARCHAR(100) | NOT NULL, UNIQUE    | Permission name                      |
| `description` | TEXT         | NULLABLE            | Description                          |
| `resource`    | VARCHAR(100) | NOT NULL            | Target resource (e.g. "user")        |
| `action`      | VARCHAR(50)  | NOT NULL            | Action (create/read/update/delete)   |

---

### `{prefix}_user_roles`

| Column    | Type | Constraints                              | Description |
|-----------|------|------------------------------------------|-------------|
| `id`      | UUID | PK (inherited)                           | Record ID   |
| `user_id` | UUID | FK -> `{prefix}_users.id` ON DELETE CASCADE | User       |
| `role_id` | UUID | FK -> `{prefix}_roles.id` ON DELETE CASCADE | Role       |

---

### `{prefix}_role_permissions`

| Column         | Type | Constraints                                 | Description  |
|----------------|------|---------------------------------------------|--------------|
| `id`           | UUID | PK (inherited)                              | Record ID    |
| `role_id`      | UUID | FK -> `{prefix}_roles.id` ON DELETE CASCADE | Role         |
| `permission_id`| UUID | FK -> `{prefix}_permissions.id` ON DELETE CASCADE | Permission |

---

## Customer Module

### `m_customer`

| Column             | Type          | Constraints         | Description               |
|--------------------|---------------|---------------------|---------------------------|
| `id`               | UUID          | PK (inherited)      | Customer ID               |
| `customer_code`    | VARCHAR(20)   | NOT NULL, UNIQUE    | Customer code             |
| `full_name`        | VARCHAR(200)  | NOT NULL            | Full name                 |
| `display_name`     | VARCHAR(200)  | NULLABLE            | Display name              |
| `customer_type`    | VARCHAR(20)   | default `INDIVIDUAL`| INDIVIDUAL/COMPANY        |
| `status`           | VARCHAR(20)   | default `ACTIVE`    | ACTIVE/INACTIVE           |
| `tax_id`           | VARCHAR(20)   | NULLABLE            | Tax ID                    |
| `email`            | VARCHAR(100)  | NULLABLE            | Email                     |
| `phone_number`     | VARCHAR(20)   | NOT NULL            | Primary phone             |
| `secondary_phone`  | VARCHAR(20)   | NULLABLE            | Secondary phone           |
| `address`          | TEXT          | NULLABLE            | Address                   |
| `province`         | VARCHAR(100)  | NULLABLE            | Province                  |
| `city`             | VARCHAR(100)  | NULLABLE            | City                      |
| `district`         | VARCHAR(100)  | NULLABLE            | District                  |
| `postal_code`      | VARCHAR(10)   | NULLABLE            | Postal code               |
| `country`          | VARCHAR(50)   | default `Thailand`  | Country                   |
| `contact_person`   | VARCHAR(100)  | NULLABLE            | Contact person            |
| `contact_phone`    | VARCHAR(20)   | NULLABLE            | Contact phone             |
| `notes`            | TEXT          | NULLABLE            | Notes                     |
| `total_visit_count`| INTEGER       | default `0`         | Total visit count         |
| `total_spent`      | FLOAT         | default `0.0`       | Total amount spent        |
| `user_id`          | UUID          | NOT NULL            | Owner user ID             |
| `whitelabel_id`    | UUID          | NOT NULL            | Whitelabel ID             |

---

### `m_car`

| Column              | Type          | Constraints         | Description               |
|---------------------|---------------|---------------------|---------------------------|
| `id`                | UUID          | PK (inherited)      | Car ID                    |
| `customer_id`       | UUID          | NOT NULL            | Customer UUID             |
| `license_plate`     | VARCHAR(20)   | NOT NULL, UNIQUE    | License plate             |
| `province`          | VARCHAR(50)   | NULLABLE            | License province          |
| `brand`             | VARCHAR(50)   | NOT NULL            | Car brand                 |
| `model`             | VARCHAR(100)  | NOT NULL            | Car model                 |
| `sub_model`         | VARCHAR(100)  | NULLABLE            | Sub model                 |
| `year`              | INTEGER       | NULLABLE            | Model year                |
| `color`             | VARCHAR(30)   | NULLABLE            | Color                     |
| `engine_number`     | VARCHAR(50)   | NULLABLE            | Engine number             |
| `chassis_number`    | VARCHAR(50)   | NULLABLE            | Chassis number            |
| `fuel_type`         | VARCHAR(20)   | NULLABLE            | Gasoline/Diesel/EV/etc    |
| `transmission_type` | VARCHAR(20)   | NULLABLE            | Automatic/Manual          |
| `engine_cc`         | INTEGER       | NULLABLE            | Engine displacement (cc)  |
| `seating_capacity`  | INTEGER       | NULLABLE            | Seating capacity          |
| `mileage`           | INTEGER       | default `0`         | Current mileage (km)      |
| `notes`             | TEXT          | NULLABLE            | Notes                     |
| `user_id`           | UUID          | NOT NULL            | Owner user ID             |
| `whitelabel_id`     | UUID          | NOT NULL            | Whitelabel ID             |

---

## Item Module

### `item`

| Column      | Type          | Constraints    | Description      |
|-------------|---------------|----------------|------------------|
| `id`        | UUID          | PK (inherited) | Item ID          |
| `title`     | VARCHAR(100)  | NOT NULL       | Item title       |
| `description`| VARCHAR(200) | NOT NULL       | Item description |
| `owner_id`  | UUID          | NOT NULL       | Owner user ID    |

---

## IoT Module

### `iot_device`

| Column            | Type          | Constraints    | Description                |
|-------------------|---------------|----------------|----------------------------|
| `id`              | UUID          | PK (inherited) | Device ID                  |
| `hardware_id`     | INTEGER       | NOT NULL       | Hardware identifier        |
| `type_id`         | INTEGER       | default `0`    | Device type ID             |
| `location_id`     | INTEGER       | default `0`    | Location ID                |
| `device_sn`       | VARCHAR(100)  | default `""`   | Serial number              |
| `device_name`     | VARCHAR(255)  | NOT NULL       | Device name                |
| `device_type`     | VARCHAR(100)  | default `""`   | Device type                |
| `location_name`   | VARCHAR(255)  | default `""`   | Location name              |
| `mqtt_id`         | INTEGER       | default `0`    | MQTT config ID             |
| `mqtt_main_id`    | INTEGER       | default `0`    | MQTT main broker ID        |
| `mqtt_topic`      | VARCHAR(500)  | default `""`   | MQTT topic                 |
| `mqtt_name`       | VARCHAR(255)  | default `""`   | MQTT display name          |
| `mqtt_username`   | VARCHAR(255)  | default `""`   | MQTT username              |
| `mqtt_password`   | VARCHAR(255)  | default `""`   | MQTT password              |
| `unit`            | VARCHAR(50)   | default `""`   | Measurement unit           |
| `status`          | VARCHAR(50)   | default `offline` | Device status            |
| `icon`            | VARCHAR(255)  | default `""`   | Icon name                  |
| `icon_color`      | VARCHAR(50)   | default `""`   | Icon color                 |
| `description`     | VARCHAR(500)  | default `""`   | Description                |
| `firmware_version`| VARCHAR(50)   | default `""`   | Firmware version           |

---

### `iot_device_status`

| Column         | Type           | Constraints                  | Description             |
|----------------|----------------|------------------------------|-------------------------|
| `id`           | UUID           | PK (inherited)               | Record ID               |
| `device_id`    | INTEGER        | NOT NULL, UNIQUE             | Device ID               |
| `is_online`    | Boolean        | default `false`              | Online status           |
| `last_seen`    | DateTime(tz)   | NULLABLE                     | Last seen timestamp     |
| `last_value`   | Float          | default `0.0`                | Last sensor value       |
| `last_alarm`   | INTEGER        | default `0`                  | Last alarm status       |
| `count_alarm`  | INTEGER        | default `0`                  | Total alarm count       |
| `event`        | INTEGER        | default `0`                  | Event state             |
| `status`       | VARCHAR(50)    | default `offline`            | Status string           |
| `sensor_data`  | VARCHAR(500)   | default `""`                 | Sensor data JSON        |
| `sensor_min`   | Float          | default `0.0`                | Sensor min value        |
| `sensor_max`   | Float          | default `0.0`                | Sensor max value        |
| `sensor_avg`   | Float          | default `0.0`                | Sensor avg value        |
| `battery`      | Float          | default `0.0`                | Battery level           |
| `rssi`         | INTEGER        | default `0`                  | Signal strength         |

---

### `iot_device_config`

| Column                 | Type          | Constraints    | Description                |
|------------------------|---------------|----------------|----------------------------|
| `id`                   | UUID          | PK (inherited) | Config ID                  |
| `device_id`            | INTEGER       | NOT NULL, UNIQUE | Device ID                |
| `max_value`            | Float         | default `0.0`  | Maximum threshold          |
| `min_value`            | Float         | default `0.0`  | Minimum threshold          |
| `warning_threshold`    | Float         | default `0.0`  | Warning threshold          |
| `alert_threshold`      | Float         | default `0.0`  | Alert threshold            |
| `recovery_warning`     | Float         | default `0.0`  | Recovery warning level     |
| `recovery_alert`       | Float         | default `0.0`  | Recovery alert level       |
| `calibration_offset`   | Float         | default `0.0`  | Calibration offset         |
| `calibration_multiplier`| Float        | default `1.0`  | Calibration multiplier     |
| `mqtt_control_on`      | VARCHAR(255)  | default `""`   | MQTT control ON payload    |
| `mqtt_control_off`     | VARCHAR(255)  | default `""`   | MQTT control OFF payload   |
| `action_name`          | VARCHAR(255)  | default `""`   | Alarm action name          |
| `config_json`          | VARCHAR(2000) | default `"{}"` | Additional config JSON     |

---

### `iot_device_alert`

| Column         | Type          | Constraints    | Description                |
|----------------|---------------|----------------|----------------------------|
| `id`           | UUID          | PK (inherited) | Alert ID                   |
| `device_id`    | INTEGER       | NOT NULL       | Device ID                  |
| `alert_type`   | VARCHAR(50)   | default `""`   | Alert type                 |
| `severity`     | VARCHAR(20)   | default `low`  | low/medium/high/critical   |
| `title`        | VARCHAR(255)  | default `""`   | Alert title                |
| `message`      | VARCHAR(1000) | default `""`   | Alert message              |
| `value_data`   | Float         | default `0.0`  | Sensor value at alert      |
| `value_alarm`  | Float         | default `0.0`  | Alarm threshold value      |
| `resolved`     | Boolean       | default `false`| Is resolved                |
| `acknowledged` | Boolean       | default `false`| Is acknowledged            |

---

### `iot_alarm_log`

| Column                | Type          | Constraints    | Description                |
|-----------------------|---------------|----------------|----------------------------|
| `id`                  | UUID          | PK (inherited) | Log ID                     |
| `device_id`           | INTEGER       | NOT NULL       | Device ID                  |
| `alarm_action_id`     | INTEGER       | default `0`    | Alarm action ID            |
| `alarm_type`          | INTEGER       | default `0`    | Alarm type                 |
| `alarm_status`        | INTEGER       | default `0`    | Alarm status               |
| `value_data`          | Float         | default `0.0`  | Sensor value               |
| `value_alarm`         | Float         | default `0.0`  | Alarm threshold            |
| `title`               | VARCHAR(255)  | default `""`   | Alarm title                |
| `subject`             | VARCHAR(500)  | default `""`   | Alarm subject              |
| `content`             | TEXT          | default `""`   | Alarm content              |
| `data_alarm`          | INTEGER       | default `0`    | Alarm data value           |
| `data_alarm_raw`      | INTEGER       | default `0`    | Raw alarm data             |
| `event_control`       | INTEGER       | default `0`    | Event control state        |
| `message_mqtt_control`| VARCHAR(500)  | default `""`   | MQTT control message       |

---

### `iot_data`

| Column         | Type           | Constraints    | Description            |
|----------------|----------------|----------------|------------------------|
| `id`           | UUID           | PK (inherited) | Data record ID         |
| `device_id`    | INTEGER        | NOT NULL       | Device ID              |
| `data_json`    | TEXT           | default `"{}"` | Data payload JSON      |
| `timestamp`    | DateTime(tz)   | NULLABLE       | Data timestamp         |
| `location_id`  | INTEGER        | default `0`    | Location ID            |
| `metadata_json`| TEXT           | default `"{}"` | Metadata JSON          |

---

### `iot_activity_log`

| Column        | Type          | Constraints    | Description        |
|---------------|---------------|----------------|--------------------|
| `id`          | UUID          | PK (inherited) | Log ID             |
| `log_type`    | VARCHAR(50)   | default `""`   | Log type           |
| `device_id`   | INTEGER       | default `0`    | Device ID          |
| `user_id`     | INTEGER       | default `0`    | User ID            |
| `severity`    | VARCHAR(20)   | default `info` | Severity level     |
| `data_json`   | TEXT          | default `"{}"` | Data JSON          |
| `description` | TEXT          | default `""`   | Description        |

---

### `iot_schedule`

| Column       | Type          | Constraints    | Description              |
|--------------|---------------|----------------|--------------------------|
| `id`         | UUID          | PK (inherited) | Schedule ID              |
| `schedule_id`| INTEGER       | default `0`    | Schedule ID (legacy)     |
| `device_id`  | INTEGER       | NOT NULL       | Device ID                |
| `start_time` | VARCHAR(10)   | default `""`   | Start time (HH:MM)       |
| `end_time`   | VARCHAR(10)   | default `""`   | End time (HH:MM)         |
| `event`      | VARCHAR(50)   | default `""`   | Event action             |
| `monday`     | Boolean       | default `false`| Active on Monday         |
| `tuesday`    | Boolean       | default `false`| Active on Tuesday        |
| `wednesday`  | Boolean       | default `false`| Active on Wednesday      |
| `thursday`   | Boolean       | default `false`| Active on Thursday       |
| `friday`     | Boolean       | default `false`| Active on Friday         |
| `saturday`   | Boolean       | default `false`| Active on Saturday       |
| `sunday`     | Boolean       | default `false`| Active on Sunday         |

---

## Batch Module

### `m_batch_job`

| Column          | Type           | Constraints    | Description               |
|-----------------|----------------|----------------|---------------------------|
| `id`            | UUID           | PK (inherited) | Job ID                    |
| `name`          | VARCHAR(200)   | NOT NULL       | Job name                  |
| `type`          | VARCHAR(50)    | NOT NULL       | Job type                  |
| `config`        | JSON           | NULLABLE       | Configuration JSON        |
| `schedule`      | VARCHAR(100)   | NULLABLE       | Cron-like schedule        |
| `status`        | VARCHAR(20)    | default `pending` | pending/running/completed/failed |
| `total_count`   | INTEGER        | default `0`    | Total items               |
| `success_count` | INTEGER        | default `0`    | Successful items          |
| `fail_count`    | INTEGER        | default `0`    | Failed items              |
| `started_at`    | DateTime(tz)   | NULLABLE       | Start time                |
| `finished_at`   | DateTime(tz)   | NULLABLE       | Finish time               |

---

### `m_batch_job_log`

| Column     | Type         | Constraints    | Description         |
|------------|--------------|----------------|---------------------|
| `id`       | UUID         | PK (inherited) | Log ID              |
| `job_id`   | UUID         | NOT NULL       | Batch job ID        |
| `message`  | TEXT         | NOT NULL       | Log message         |
| `level`    | VARCHAR(20)  | NOT NULL       | info/warning/error  |

---

## Email Module

### `m_email_config`

| Column       | Type          | Constraints    | Description           |
|--------------|---------------|----------------|-----------------------|
| `id`         | UUID          | PK (inherited) | Config ID             |
| `smtp_host`  | VARCHAR(200)  | NOT NULL       | SMTP server host      |
| `smtp_port`  | INTEGER       | NOT NULL       | SMTP server port      |
| `smtp_user`  | VARCHAR(200)  | NOT NULL       | SMTP username         |
| `from_email` | VARCHAR(200)  | NOT NULL       | Sender email          |
| `from_name`  | VARCHAR(200)  | NOT NULL       | Sender display name   |
| `is_active`  | Boolean       | default `true` | Is config active      |

---

### `m_email_log`

| Column         | Type           | Constraints    | Description           |
|----------------|----------------|----------------|-----------------------|
| `id`           | UUID           | PK (inherited) | Log ID                |
| `to_address`   | VARCHAR(500)   | NOT NULL       | Recipient email       |
| `cc`           | VARCHAR(500)   | NULLABLE       | CC recipients         |
| `bcc`          | VARCHAR(500)   | NULLABLE       | BCC recipients        |
| `subject`      | VARCHAR(500)   | NOT NULL       | Email subject         |
| `body`         | TEXT           | NOT NULL       | Email body            |
| `status`       | VARCHAR(20)    | default `pending` | pending/sent/failed |
| `error_message`| TEXT           | NULLABLE       | Error if failed       |
| `sent_at`      | DateTime(tz)   | NULLABLE       | Send timestamp        |

---

## I18n Module

### `m_translation`

| Column      | Type          | Constraints    | Description                |
|-------------|---------------|----------------|----------------------------|
| `id`        | UUID          | PK (inherited) | Translation ID             |
| `locale`    | VARCHAR(10)   | NOT NULL       | Locale code (en, th)       |
| `key`       | VARCHAR(255)  | NOT NULL       | Translation key            |
| `value`     | TEXT          | NOT NULL       | Translated value           |

---

## Payment Module

### `m_payment`

| Column              | Type           | Constraints    | Description               |
|---------------------|----------------|----------------|---------------------------|
| `id`                | UUID           | PK (inherited) | Payment ID                |
| `payment_no`        | VARCHAR(50)    | NOT NULL       | Payment number            |
| `invoice_id`        | UUID           | NULLABLE       | Invoice ID                |
| `job_id`            | UUID           | NULLABLE       | Job/work order ID         |
| `customer_id`       | UUID           | NULLABLE       | Customer ID               |
| `payment_date`      | DateTime(tz)   | NULLABLE       | Payment date              |
| `payment_method_id` | UUID           | NULLABLE       | Payment method ID         |
| `amount`            | Float          | default `0`    | Payment amount            |
| `amount_received`   | Float          | default `0`    | Amount received           |
| `change_amount`     | Float          | default `0`    | Change amount             |
| `currency`          | VARCHAR(10)    | default `THB`  | Currency code             |
| `exchange_rate`     | Float          | default `1`    | Exchange rate             |
| `status`            | VARCHAR(20)    | default `pending` | pending/completed/refunded/cancelled |
| `reference_number`  | VARCHAR(100)   | NULLABLE       | Reference number          |
| `bank_name`         | VARCHAR(100)   | NULLABLE       | Bank name                 |
| `cheque_number`     | VARCHAR(50)    | NULLABLE       | Cheque number             |
| `cheque_bank`       | VARCHAR(100)   | NULLABLE       | Cheque bank               |
| `cheque_date`       | DATE           | NULLABLE       | Cheque date               |
| `notes`             | TEXT           | NULLABLE       | Notes                     |
| `received_by`       | UUID           | NULLABLE       | Received by user ID       |
| `approved_by`       | UUID           | NULLABLE       | Approved by user ID       |
| `approved_at`       | DateTime(tz)   | NULLABLE       | Approval timestamp        |
| `refunded_amount`   | Float          | default `0`    | Refunded amount           |
| `refunded_at`       | DateTime(tz)   | NULLABLE       | Refund timestamp          |

---

### `m_receipt`

| Column             | Type           | Constraints    | Description               |
|--------------------|----------------|----------------|---------------------------|
| `id`               | UUID           | PK (inherited) | Receipt ID                |
| `receipt_no`       | VARCHAR(50)    | NOT NULL       | Receipt number            |
| `payment_id`       | UUID           | NOT NULL       | Payment ID                |
| `invoice_id`       | UUID           | NULLABLE       | Invoice ID                |
| `customer_id`      | UUID           | NULLABLE       | Customer ID               |
| `receipt_date`     | DateTime(tz)   | NULLABLE       | Receipt date              |
| `receipt_type`     | VARCHAR(20)    | NOT NULL       | Receipt type              |
| `amount`           | Float          | default `0`    | Receipt amount            |
| `amount_in_words_th`| TEXT          | NULLABLE       | Amount in Thai words      |
| `amount_in_words_en`| TEXT          | NULLABLE       | Amount in English words   |
| `currency`         | VARCHAR(10)    | default `THB`  | Currency code             |
| `status`           | VARCHAR(20)    | default `active` | active/cancelled         |
| `notes`            | TEXT           | NULLABLE       | Notes                     |
| `issued_by`        | UUID           | NULLABLE       | Issued by user ID         |

---

### `m_payment_history`

| Column       | Type           | Constraints    | Description               |
|--------------|----------------|----------------|---------------------------|
| `id`         | UUID           | PK (inherited) | History ID                |
| `payment_id` | UUID           | NOT NULL       | Payment ID                |
| `from_status`| VARCHAR(20)    | NOT NULL       | Previous status           |
| `to_status`  | VARCHAR(20)    | NOT NULL       | New status                |
| `changed_by` | UUID           | NULLABLE       | Changed by user ID        |
| `changed_at` | DateTime(tz)   | NULLABLE       | Change timestamp          |
| `reason`     | TEXT           | NULLABLE       | Reason for change         |

---

## Purchase Order Module

### `m_purchase_order_header`

| Column                   | Type           | Constraints    | Description               |
|--------------------------|----------------|----------------|---------------------------|
| `id`                     | UUID           | PK (inherited) | PO header ID              |
| `po_no`                  | VARCHAR(50)    | NOT NULL       | PO number                 |
| `quotation_id`           | UUID           | NULLABLE       | Related quotation ID      |
| `job_id`                 | UUID           | NULLABLE       | Related job ID            |
| `supplier_id`            | UUID           | NULLABLE       | Supplier ID               |
| `po_date`                | DATE           | NULLABLE       | PO date                   |
| `expected_delivery_date` | DATE           | NULLABLE       | Expected delivery date    |
| `actual_delivery_date`   | DATE           | NULLABLE       | Actual delivery date      |
| `status`                 | VARCHAR(20)    | default `draft`| draft/sent/confirmed/received/cancelled |
| `subtotal`               | Float          | default `0`    | Subtotal                  |
| `tax_rate`               | Float          | default `0`    | Tax rate (%)              |
| `tax_amount`             | Float          | default `0`    | Tax amount                |
| `discount_type`          | VARCHAR(20)    | NULLABLE       | percentage/fixed          |
| `discount_value`         | Float          | default `0`    | Discount value            |
| `total`                  | Float          | default `0`    | Total amount              |
| `currency`               | VARCHAR(10)    | default `THB`  | Currency code             |
| `exchange_rate`          | Float          | default `1`    | Exchange rate             |
| `shipping_cost`          | Float          | default `0`    | Shipping cost             |
| `payment_terms`          | TEXT           | NULLABLE       | Payment terms             |
| `delivery_address`       | TEXT           | NULLABLE       | Delivery address          |
| `notes`                  | TEXT           | NULLABLE       | Notes                     |
| `terms_and_conditions`   | TEXT           | NULLABLE       | Terms and conditions      |
| `sent_at`                | DateTime       | NULLABLE       | Sent timestamp            |
| `confirmed_at`           | DateTime       | NULLABLE       | Confirmed timestamp       |
| `received_by`            | UUID           | NULLABLE       | Received by user ID       |

---

### `m_purchase_order_detail`

| Column              | Type         | Constraints    | Description               |
|---------------------|--------------|----------------|---------------------------|
| `id`                | UUID         | PK (inherited) | Detail line ID            |
| `po_header_id`      | UUID         | NOT NULL       | PO header ID              |
| `part_id`           | UUID         | NULLABLE       | Part ID                   |
| `quantity_ordered`  | INTEGER      | default `0`    | Quantity ordered          |
| `quantity_received` | INTEGER      | default `0`    | Quantity received         |
| `unit_price`        | Float        | default `0`    | Unit price                |
| `total_price`       | Float        | default `0`    | Total price               |
| `discount`          | Float        | default `0`    | Discount                  |
| `net_price`         | Float        | default `0`    | Net price                 |
| `note`              | TEXT         | NULLABLE       | Line note                 |

---

### `m_purchase_order_status_history`

| Column         | Type           | Constraints    | Description               |
|----------------|----------------|----------------|---------------------------|
| `id`           | UUID           | PK (inherited) | History ID                |
| `po_header_id` | UUID           | NOT NULL       | PO header ID              |
| `from_status`  | VARCHAR(20)    | NOT NULL       | Previous status           |
| `to_status`    | VARCHAR(20)    | NOT NULL       | New status                |
| `changed_by`   | UUID           | NULLABLE       | Changed by user ID        |
| `changed_at`   | DateTime       | NULLABLE       | Change timestamp          |
| `reason`       | TEXT           | NULLABLE       | Reason for change         |

---

## Quotation Module

### `m_quotation`

| Column               | Type           | Constraints    | Description               |
|----------------------|----------------|----------------|---------------------------|
| `id`                 | UUID           | PK (inherited) | Quotation ID              |
| `quotation_no`       | VARCHAR(50)    | NOT NULL       | Quotation number          |
| `job_id`             | UUID           | NULLABLE       | Job ID                    |
| `customer_id`        | UUID           | NULLABLE       | Customer ID               |
| `quotation_date`     | DATE           | NULLABLE       | Quotation date            |
| `expiry_date`        | DATE           | NULLABLE       | Expiry date               |
| `status`             | VARCHAR(20)    | default `draft`| draft/approved/rejected   |
| `subtotal`           | Float          | default `0`    | Subtotal                  |
| `tax_rate`           | Float          | default `0`    | Tax rate (%)              |
| `tax_amount`         | Float          | default `0`    | Tax amount                |
| `discount_type`      | VARCHAR(20)    | NULLABLE       | percentage/fixed          |
| `discount_value`     | Float          | default `0`    | Discount value            |
| `total`              | Float          | default `0`    | Total                     |
| `amount_in_words_th` | TEXT           | NULLABLE       | Amount in Thai words      |
| `amount_in_words_en` | TEXT           | NULLABLE       | Amount in English words   |
| `currency`           | VARCHAR(10)    | default `THB`  | Currency                  |
| `exchange_rate`      | Float          | default `1`    | Exchange rate             |
| `notes`              | TEXT           | NULLABLE       | Notes                     |
| `terms_and_conditions`| TEXT          | NULLABLE       | Terms and conditions      |
| `approved_by`        | UUID           | NULLABLE       | Approved by user ID       |
| `approved_at`        | DateTime(tz)   | NULLABLE       | Approval timestamp        |
| `rejected_reason`    | TEXT           | NULLABLE       | Rejection reason          |
| `converted_to_po`    | Boolean        | default `false`| Converted to PO flag      |

---

## WOS Module

### `m_wos_order`

| Column           | Type          | Constraints         | Description               |
|------------------|---------------|---------------------|---------------------------|
| `id`             | UUID          | PK (inherited)      | Order ID                  |
| `order_number`   | VARCHAR(50)   | NOT NULL, UNIQUE    | Unique order number       |
| `customer_name`  | VARCHAR(200)  | NOT NULL            | Customer full name        |
| `customer_email` | VARCHAR(200)  | NOT NULL            | Customer email            |
| `customer_phone` | VARCHAR(50)   | NULLABLE            | Customer phone            |
| `items`          | JSON          | NULLABLE            | Order items               |
| `total_amount`   | Float         | NOT NULL            | Total amount              |
| `status`         | VARCHAR(20)   | default `pending`   | pending/processing/completed/cancelled |
| `notes`          | TEXT          | NULLABLE            | Notes                     |

---

## Document Module

### `m_document`

| Column          | Type          | Constraints    | Description               |
|-----------------|---------------|----------------|---------------------------|
| `id`            | UUID          | PK (inherited) | Document ID               |
| `filename`      | VARCHAR(255)  | NOT NULL       | Stored filename           |
| `original_name` | VARCHAR(255)  | NOT NULL       | Original upload filename  |
| `mime_type`     | VARCHAR(100)  | NOT NULL       | MIME type                 |
| `size`          | BIGINT        | NOT NULL       | File size in bytes        |

---

## Entity Relationship Summary

```
{prefix}_users 1---* {prefix}_sessions 1---1 {prefix}_refresh_tokens 1---1 {prefix}_access_tokens
{prefix}_users *---* {prefix}_roles (via {prefix}_user_roles)
{prefix}_roles *---* {prefix}_permissions (via {prefix}_role_permissions)

m_customer 1---* m_car
m_customer 1---* m_payment (via customer_id)
m_payment 1---1 m_receipt
m_payment 1---* m_payment_history

m_purchase_order_header 1---* m_purchase_order_detail
m_purchase_order_header 1---* m_purchase_order_status_history

m_batch_job 1---* m_batch_job_log

iot_device 1---1 iot_device_status
iot_device 1---1 iot_device_config
iot_device 1---* iot_device_alert
iot_device 1---* iot_alarm_log
iot_device 1---* iot_data
iot_device 1---* iot_activity_log
iot_device 1---* iot_schedule
```
