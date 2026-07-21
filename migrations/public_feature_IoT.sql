/*
 Navicat Premium Dump SQL

 Source Server         : postgres-localhost
 Source Server Type    : PostgreSQL
 Source Server Version : 180003 (180003)
 Source Host           : localhost:5432
 Source Catalog        : fastapi
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 180003 (180003)
 File Encoding         : 65001

 Date: 21/07/2026 15:26:52
*/


-- ----------------------------
-- Type structure for gender_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."gender_enum";
CREATE TYPE "public"."gender_enum" AS ENUM (
  'MALE',
  'FEMALE',
  'NON_BINARY',
  'OTHER'
);

-- ----------------------------
-- Type structure for role_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."role_enum";
CREATE TYPE "public"."role_enum" AS ENUM (
  'ADMIN',
  'MANAGER',
  'USER'
);

-- ----------------------------
-- Type structure for user_status_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."user_status_enum";
CREATE TYPE "public"."user_status_enum" AS ENUM (
  'ACTIVE',
  'INACTIVE',
  'SUSPENDED'
);

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."alembic_version";
CREATE TABLE "public"."alembic_version" (
  "version_num" varchar(32) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO "public"."alembic_version" VALUES ('4586f82a4d7e');

-- ----------------------------
-- Table structure for app_access_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_access_tokens";
CREATE TABLE "public"."app_access_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "refresh_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "permission" "public"."role_enum" NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."app_access_tokens"."id" IS 'Unique identifier of the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."refresh_id" IS 'Refresh token associated with this access token';
COMMENT ON COLUMN "public"."app_access_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."app_access_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous access token';
COMMENT ON COLUMN "public"."app_access_tokens"."permission" IS 'Permission level associated with the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_access_tokens"."expires_at" IS 'Expiration timestamp of the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."app_access_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of app_access_tokens
-- ----------------------------

-- ----------------------------
-- Table structure for app_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_permissions";
CREATE TABLE "public"."app_permissions" (
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "resource" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "action" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_permissions"."name" IS 'Name of the permission';
COMMENT ON COLUMN "public"."app_permissions"."description" IS 'Description of the permission';
COMMENT ON COLUMN "public"."app_permissions"."resource" IS 'Resource that the permission applies to (e.g. ''user'', ''session'')';
COMMENT ON COLUMN "public"."app_permissions"."action" IS 'Action allowed on the resource (e.g. ''create'', ''read'', ''update'', ''delete'')';
COMMENT ON COLUMN "public"."app_permissions"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_permissions"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_permissions"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for app_refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_refresh_tokens";
CREATE TABLE "public"."app_refresh_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "session_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."app_refresh_tokens"."id" IS 'Unique identifier of the refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."session_id" IS 'Session associated with this refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."app_refresh_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."created_at" IS 'Timestamp when the refresh token was created';
COMMENT ON COLUMN "public"."app_refresh_tokens"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."app_refresh_tokens"."expires_at" IS 'Expiration timestamp of the refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."app_refresh_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of app_refresh_tokens
-- ----------------------------

-- ----------------------------
-- Table structure for app_role_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_role_permissions";
CREATE TABLE "public"."app_role_permissions" (
  "role_id" uuid NOT NULL,
  "permission_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_role_permissions"."role_id" IS 'Identifier of the role';
COMMENT ON COLUMN "public"."app_role_permissions"."permission_id" IS 'Identifier of the permission';
COMMENT ON COLUMN "public"."app_role_permissions"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_role_permissions"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_role_permissions"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_role_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for app_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_roles";
CREATE TABLE "public"."app_roles" (
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_roles"."name" IS 'Name of the role';
COMMENT ON COLUMN "public"."app_roles"."description" IS 'Description of the role';
COMMENT ON COLUMN "public"."app_roles"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_roles"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_roles"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_roles
-- ----------------------------
INSERT INTO "public"."app_roles" VALUES ('admin', 'Administrator role with full access', 'd2adb107-0e51-4811-aedf-9e65ed82b875', 't', '2026-07-21 15:24:52.444226+07', '2026-07-21 15:24:52.444226+07');
INSERT INTO "public"."app_roles" VALUES ('manager', 'Manager role with elevated access', 'd59a80dc-408e-4ae0-b6ae-b0d3f44c274e', 't', '2026-07-21 15:24:52.444226+07', '2026-07-21 15:24:52.444226+07');
INSERT INTO "public"."app_roles" VALUES ('user', 'Regular user role with basic access', 'aaa3ae86-20aa-4702-82ff-97be72a328d2', 't', '2026-07-21 15:24:52.444226+07', '2026-07-21 15:24:52.444226+07');

-- ----------------------------
-- Table structure for app_sessions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_sessions";
CREATE TABLE "public"."app_sessions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default" NOT NULL,
  "device" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "accept_language" varchar(255) COLLATE "pg_catalog"."default",
  "accept-encoding" varchar(255) COLLATE "pg_catalog"."default",
  "origin" varchar(255) COLLATE "pg_catalog"."default",
  "referrer" varchar(255) COLLATE "pg_catalog"."default",
  "location" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at" timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted" bool NOT NULL
)
;
COMMENT ON COLUMN "public"."app_sessions"."id" IS 'Unique identifier of the session';
COMMENT ON COLUMN "public"."app_sessions"."user_id" IS 'Identifier of the user who owns the session';
COMMENT ON COLUMN "public"."app_sessions"."ip_address" IS 'IP address used when the session was created';
COMMENT ON COLUMN "public"."app_sessions"."device" IS 'Human readable device name';
COMMENT ON COLUMN "public"."app_sessions"."user_agent" IS 'User agent string of the client';
COMMENT ON COLUMN "public"."app_sessions"."accept_language" IS 'Accept-Language header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."accept-encoding" IS 'Accept-Encoding header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."origin" IS 'Origin header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."referrer" IS 'Referrer header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."location" IS 'Approximate geographic location of the client';
COMMENT ON COLUMN "public"."app_sessions"."created_at" IS 'Timestamp when the session was created';
COMMENT ON COLUMN "public"."app_sessions"."last_update_at" IS 'Last time the session was updated';
COMMENT ON COLUMN "public"."app_sessions"."blacklisted" IS 'Indicates whether the session is blacklisted';

-- ----------------------------
-- Records of app_sessions
-- ----------------------------

-- ----------------------------
-- Table structure for app_user_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_user_roles";
CREATE TABLE "public"."app_user_roles" (
  "user_id" uuid NOT NULL,
  "role_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_user_roles"."user_id" IS 'Identifier of the user';
COMMENT ON COLUMN "public"."app_user_roles"."role_id" IS 'Identifier of the role';
COMMENT ON COLUMN "public"."app_user_roles"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_user_roles"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_user_roles"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_user_roles
-- ----------------------------

-- ----------------------------
-- Table structure for app_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_users";
CREATE TABLE "public"."app_users" (
  "first_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "last_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "preferred_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "gender" "public"."gender_enum" NOT NULL,
  "birthdate" date NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "phone" varchar(18) COLLATE "pg_catalog"."default",
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "role" "public"."role_enum" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "status" "public"."user_status_enum" NOT NULL DEFAULT 'ACTIVE'::user_status_enum,
  "username" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;
COMMENT ON COLUMN "public"."app_users"."first_name" IS 'First name of the user';
COMMENT ON COLUMN "public"."app_users"."last_name" IS 'Last name of the user';
COMMENT ON COLUMN "public"."app_users"."preferred_name" IS 'Preferred name of the user';
COMMENT ON COLUMN "public"."app_users"."gender" IS 'Gender of the user';
COMMENT ON COLUMN "public"."app_users"."birthdate" IS 'Birthdate of the user';
COMMENT ON COLUMN "public"."app_users"."email" IS 'Email address of the user';
COMMENT ON COLUMN "public"."app_users"."phone" IS 'Phone number of the user';
COMMENT ON COLUMN "public"."app_users"."hashed_password" IS 'Hashed password of the user';
COMMENT ON COLUMN "public"."app_users"."role" IS 'Role of the user';
COMMENT ON COLUMN "public"."app_users"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_users"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_users"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."app_users"."status" IS 'Status of the user (active, inactive, suspended)';
COMMENT ON COLUMN "public"."app_users"."username" IS 'Unique username of the user';

-- ----------------------------
-- Records of app_users
-- ----------------------------
INSERT INTO "public"."app_users" VALUES ('System', 'Administrator', 'Admin', 'OTHER', '1999-12-31', 'admin@localhost.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$CTocv/ktVuMKl1mKR99iHw$7sXnBhQGRd2Ltj1rzLdOsC7RoJ7KJ/dk2pwpBRH7I58', 'ADMIN', '773f4ee9-e206-4642-b3f1-11a33f66bc38', 't', '2026-07-21 15:24:52.444226+07', '2026-07-21 15:24:52.444226+07', 'ACTIVE', 'admin');

-- ----------------------------
-- Table structure for iot_activity_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_activity_log";
CREATE TABLE "public"."iot_activity_log" (
  "log_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "device_id" int4 NOT NULL,
  "user_id" int4 NOT NULL,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "data_json" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_activity_log"."log_type" IS 'Log type';
COMMENT ON COLUMN "public"."iot_activity_log"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_activity_log"."user_id" IS 'User ID';
COMMENT ON COLUMN "public"."iot_activity_log"."severity" IS 'Severity level';
COMMENT ON COLUMN "public"."iot_activity_log"."data_json" IS 'Data JSON';
COMMENT ON COLUMN "public"."iot_activity_log"."description" IS 'Description';
COMMENT ON COLUMN "public"."iot_activity_log"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_activity_log"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_activity_log"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_activity_log
-- ----------------------------

-- ----------------------------
-- Table structure for iot_alarm_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_alarm_log";
CREATE TABLE "public"."iot_alarm_log" (
  "device_id" int4 NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "alarm_type" int4 NOT NULL,
  "alarm_status" int4 NOT NULL,
  "value_data" float8 NOT NULL,
  "value_alarm" float8 NOT NULL,
  "title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "subject" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "data_alarm" int4 NOT NULL,
  "data_alarm_raw" int4 NOT NULL,
  "event_control" int4 NOT NULL,
  "message_mqtt_control" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_alarm_log"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_alarm_log"."alarm_action_id" IS 'Alarm action ID';
COMMENT ON COLUMN "public"."iot_alarm_log"."alarm_type" IS 'Alarm type';
COMMENT ON COLUMN "public"."iot_alarm_log"."alarm_status" IS 'Alarm status';
COMMENT ON COLUMN "public"."iot_alarm_log"."value_data" IS 'Sensor value';
COMMENT ON COLUMN "public"."iot_alarm_log"."value_alarm" IS 'Alarm threshold';
COMMENT ON COLUMN "public"."iot_alarm_log"."title" IS 'Alarm title';
COMMENT ON COLUMN "public"."iot_alarm_log"."subject" IS 'Alarm subject';
COMMENT ON COLUMN "public"."iot_alarm_log"."content" IS 'Alarm content';
COMMENT ON COLUMN "public"."iot_alarm_log"."data_alarm" IS 'Alarm data value';
COMMENT ON COLUMN "public"."iot_alarm_log"."data_alarm_raw" IS 'Raw alarm data';
COMMENT ON COLUMN "public"."iot_alarm_log"."event_control" IS 'Event control state';
COMMENT ON COLUMN "public"."iot_alarm_log"."message_mqtt_control" IS 'MQTT control message';
COMMENT ON COLUMN "public"."iot_alarm_log"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_alarm_log"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_alarm_log"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_alarm_log
-- ----------------------------

-- ----------------------------
-- Table structure for iot_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_data";
CREATE TABLE "public"."iot_data" (
  "device_id" int4 NOT NULL,
  "data_json" text COLLATE "pg_catalog"."default" NOT NULL,
  "timestamp" timestamptz(6),
  "location_id" int4 NOT NULL,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_data"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_data"."data_json" IS 'Data payload JSON';
COMMENT ON COLUMN "public"."iot_data"."timestamp" IS 'Data timestamp';
COMMENT ON COLUMN "public"."iot_data"."location_id" IS 'Location ID';
COMMENT ON COLUMN "public"."iot_data"."metadata_json" IS 'Metadata JSON';
COMMENT ON COLUMN "public"."iot_data"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_data"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_data"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_data
-- ----------------------------

-- ----------------------------
-- Table structure for iot_device
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_device";
CREATE TABLE "public"."iot_device" (
  "hardware_id" int4 NOT NULL,
  "type_id" int4 NOT NULL,
  "location_id" int4 NOT NULL,
  "device_sn" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "device_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "device_type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "location_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_id" int4 NOT NULL,
  "mqtt_main_id" int4 NOT NULL,
  "mqtt_topic" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_username" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "unit" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "icon" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "icon_color" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "firmware_version" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_device"."hardware_id" IS 'Hardware identifier';
COMMENT ON COLUMN "public"."iot_device"."type_id" IS 'Device type ID';
COMMENT ON COLUMN "public"."iot_device"."location_id" IS 'Location ID';
COMMENT ON COLUMN "public"."iot_device"."device_sn" IS 'Serial number';
COMMENT ON COLUMN "public"."iot_device"."device_name" IS 'Device name';
COMMENT ON COLUMN "public"."iot_device"."device_type" IS 'Device type';
COMMENT ON COLUMN "public"."iot_device"."location_name" IS 'Location name';
COMMENT ON COLUMN "public"."iot_device"."mqtt_id" IS 'MQTT config ID';
COMMENT ON COLUMN "public"."iot_device"."mqtt_main_id" IS 'MQTT main broker ID';
COMMENT ON COLUMN "public"."iot_device"."mqtt_topic" IS 'MQTT topic';
COMMENT ON COLUMN "public"."iot_device"."mqtt_name" IS 'MQTT display name';
COMMENT ON COLUMN "public"."iot_device"."mqtt_username" IS 'MQTT username';
COMMENT ON COLUMN "public"."iot_device"."mqtt_password" IS 'MQTT password';
COMMENT ON COLUMN "public"."iot_device"."unit" IS 'Measurement unit';
COMMENT ON COLUMN "public"."iot_device"."status" IS 'Device status';
COMMENT ON COLUMN "public"."iot_device"."icon" IS 'Icon name';
COMMENT ON COLUMN "public"."iot_device"."icon_color" IS 'Icon color';
COMMENT ON COLUMN "public"."iot_device"."description" IS 'Description';
COMMENT ON COLUMN "public"."iot_device"."firmware_version" IS 'Firmware version';
COMMENT ON COLUMN "public"."iot_device"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_device"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_device"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_device
-- ----------------------------

-- ----------------------------
-- Table structure for iot_device_alert
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_device_alert";
CREATE TABLE "public"."iot_device_alert" (
  "device_id" int4 NOT NULL,
  "alert_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "message" varchar(1000) COLLATE "pg_catalog"."default" NOT NULL,
  "value_data" float8 NOT NULL,
  "value_alarm" float8 NOT NULL,
  "resolved" bool NOT NULL,
  "acknowledged" bool NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_device_alert"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_device_alert"."alert_type" IS 'Alert type';
COMMENT ON COLUMN "public"."iot_device_alert"."severity" IS 'Severity: low/medium/high/critical';
COMMENT ON COLUMN "public"."iot_device_alert"."title" IS 'Alert title';
COMMENT ON COLUMN "public"."iot_device_alert"."message" IS 'Alert message';
COMMENT ON COLUMN "public"."iot_device_alert"."value_data" IS 'Sensor value at alert';
COMMENT ON COLUMN "public"."iot_device_alert"."value_alarm" IS 'Alarm threshold value';
COMMENT ON COLUMN "public"."iot_device_alert"."resolved" IS 'Is resolved';
COMMENT ON COLUMN "public"."iot_device_alert"."acknowledged" IS 'Is acknowledged';
COMMENT ON COLUMN "public"."iot_device_alert"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_device_alert"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_device_alert"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_device_alert
-- ----------------------------

-- ----------------------------
-- Table structure for iot_device_config
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_device_config";
CREATE TABLE "public"."iot_device_config" (
  "device_id" int4 NOT NULL,
  "max_value" float8 NOT NULL,
  "min_value" float8 NOT NULL,
  "warning_threshold" float8 NOT NULL,
  "alert_threshold" float8 NOT NULL,
  "recovery_warning" float8 NOT NULL,
  "recovery_alert" float8 NOT NULL,
  "calibration_offset" float8 NOT NULL,
  "calibration_multiplier" float8 NOT NULL,
  "mqtt_control_on" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_control_off" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "action_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "config_json" varchar(2000) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_device_config"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_device_config"."max_value" IS 'Maximum threshold';
COMMENT ON COLUMN "public"."iot_device_config"."min_value" IS 'Minimum threshold';
COMMENT ON COLUMN "public"."iot_device_config"."warning_threshold" IS 'Warning threshold';
COMMENT ON COLUMN "public"."iot_device_config"."alert_threshold" IS 'Alert threshold';
COMMENT ON COLUMN "public"."iot_device_config"."recovery_warning" IS 'Recovery warning level';
COMMENT ON COLUMN "public"."iot_device_config"."recovery_alert" IS 'Recovery alert level';
COMMENT ON COLUMN "public"."iot_device_config"."calibration_offset" IS 'Calibration offset';
COMMENT ON COLUMN "public"."iot_device_config"."calibration_multiplier" IS 'Calibration multiplier';
COMMENT ON COLUMN "public"."iot_device_config"."mqtt_control_on" IS 'MQTT control ON payload';
COMMENT ON COLUMN "public"."iot_device_config"."mqtt_control_off" IS 'MQTT control OFF payload';
COMMENT ON COLUMN "public"."iot_device_config"."action_name" IS 'Alarm action name';
COMMENT ON COLUMN "public"."iot_device_config"."config_json" IS 'Additional config JSON';
COMMENT ON COLUMN "public"."iot_device_config"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_device_config"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_device_config"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_device_config
-- ----------------------------

-- ----------------------------
-- Table structure for iot_device_status
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_device_status";
CREATE TABLE "public"."iot_device_status" (
  "device_id" int4 NOT NULL,
  "is_online" bool NOT NULL,
  "last_seen" timestamptz(6),
  "last_value" float8 NOT NULL,
  "last_alarm" int4 NOT NULL,
  "count_alarm" int4 NOT NULL,
  "event" int4 NOT NULL,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "sensor_data" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "sensor_min" float8 NOT NULL,
  "sensor_max" float8 NOT NULL,
  "sensor_avg" float8 NOT NULL,
  "battery" float8 NOT NULL,
  "rssi" int4 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_device_status"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_device_status"."is_online" IS 'Online status';
COMMENT ON COLUMN "public"."iot_device_status"."last_seen" IS 'Last seen timestamp';
COMMENT ON COLUMN "public"."iot_device_status"."last_value" IS 'Last sensor value';
COMMENT ON COLUMN "public"."iot_device_status"."last_alarm" IS 'Last alarm status';
COMMENT ON COLUMN "public"."iot_device_status"."count_alarm" IS 'Alarm count';
COMMENT ON COLUMN "public"."iot_device_status"."event" IS 'Event state';
COMMENT ON COLUMN "public"."iot_device_status"."status" IS 'Status string';
COMMENT ON COLUMN "public"."iot_device_status"."sensor_data" IS 'Sensor data JSON';
COMMENT ON COLUMN "public"."iot_device_status"."sensor_min" IS 'Sensor min value';
COMMENT ON COLUMN "public"."iot_device_status"."sensor_max" IS 'Sensor max value';
COMMENT ON COLUMN "public"."iot_device_status"."sensor_avg" IS 'Sensor avg value';
COMMENT ON COLUMN "public"."iot_device_status"."battery" IS 'Battery level';
COMMENT ON COLUMN "public"."iot_device_status"."rssi" IS 'Signal strength';
COMMENT ON COLUMN "public"."iot_device_status"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_device_status"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_device_status"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_device_status
-- ----------------------------

-- ----------------------------
-- Table structure for iot_schedule
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_schedule";
CREATE TABLE "public"."iot_schedule" (
  "schedule_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "start_time" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "end_time" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "event" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "monday" bool NOT NULL,
  "tuesday" bool NOT NULL,
  "wednesday" bool NOT NULL,
  "thursday" bool NOT NULL,
  "friday" bool NOT NULL,
  "saturday" bool NOT NULL,
  "sunday" bool NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."iot_schedule"."schedule_id" IS 'Schedule ID';
COMMENT ON COLUMN "public"."iot_schedule"."device_id" IS 'Device ID';
COMMENT ON COLUMN "public"."iot_schedule"."start_time" IS 'Start time HH:MM';
COMMENT ON COLUMN "public"."iot_schedule"."end_time" IS 'End time HH:MM';
COMMENT ON COLUMN "public"."iot_schedule"."event" IS 'Event action';
COMMENT ON COLUMN "public"."iot_schedule"."monday" IS 'Monday';
COMMENT ON COLUMN "public"."iot_schedule"."tuesday" IS 'Tuesday';
COMMENT ON COLUMN "public"."iot_schedule"."wednesday" IS 'Wednesday';
COMMENT ON COLUMN "public"."iot_schedule"."thursday" IS 'Thursday';
COMMENT ON COLUMN "public"."iot_schedule"."friday" IS 'Friday';
COMMENT ON COLUMN "public"."iot_schedule"."saturday" IS 'Saturday';
COMMENT ON COLUMN "public"."iot_schedule"."sunday" IS 'Sunday';
COMMENT ON COLUMN "public"."iot_schedule"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."iot_schedule"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."iot_schedule"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of iot_schedule
-- ----------------------------

-- ----------------------------
-- Table structure for item
-- ----------------------------
DROP TABLE IF EXISTS "public"."item";
CREATE TABLE "public"."item" (
  "title" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "owner_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."item"."title" IS 'Item title';
COMMENT ON COLUMN "public"."item"."description" IS 'Item description';
COMMENT ON COLUMN "public"."item"."owner_id" IS 'Owner user ID';
COMMENT ON COLUMN "public"."item"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."item"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."item"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of item
-- ----------------------------

-- ----------------------------
-- Table structure for m_batch_job
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_batch_job";
CREATE TABLE "public"."m_batch_job" (
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "config" json,
  "schedule" varchar(100) COLLATE "pg_catalog"."default",
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'pending'::character varying,
  "total_count" int4 NOT NULL DEFAULT 0,
  "success_count" int4 NOT NULL DEFAULT 0,
  "fail_count" int4 NOT NULL DEFAULT 0,
  "started_at" timestamptz(6),
  "finished_at" timestamptz(6),
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_batch_job"."name" IS 'Batch job name';
COMMENT ON COLUMN "public"."m_batch_job"."type" IS 'Batch job type';
COMMENT ON COLUMN "public"."m_batch_job"."config" IS 'Job configuration JSON';
COMMENT ON COLUMN "public"."m_batch_job"."schedule" IS 'Job schedule expression';
COMMENT ON COLUMN "public"."m_batch_job"."status" IS 'Job status';
COMMENT ON COLUMN "public"."m_batch_job"."total_count" IS 'Total items to process';
COMMENT ON COLUMN "public"."m_batch_job"."success_count" IS 'Successfully processed items';
COMMENT ON COLUMN "public"."m_batch_job"."fail_count" IS 'Failed items';
COMMENT ON COLUMN "public"."m_batch_job"."started_at" IS 'Job start timestamp';
COMMENT ON COLUMN "public"."m_batch_job"."finished_at" IS 'Job finish timestamp';
COMMENT ON COLUMN "public"."m_batch_job"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_batch_job"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_batch_job"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_batch_job
-- ----------------------------

-- ----------------------------
-- Table structure for m_batch_job_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_batch_job_log";
CREATE TABLE "public"."m_batch_job_log" (
  "job_id" uuid NOT NULL,
  "message" text COLLATE "pg_catalog"."default" NOT NULL,
  "level" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_batch_job_log"."job_id" IS 'Reference to batch job';
COMMENT ON COLUMN "public"."m_batch_job_log"."message" IS 'Log message';
COMMENT ON COLUMN "public"."m_batch_job_log"."level" IS 'Log level (info, warning, error)';
COMMENT ON COLUMN "public"."m_batch_job_log"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_batch_job_log"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_batch_job_log"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_batch_job_log
-- ----------------------------

-- ----------------------------
-- Table structure for m_car
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_car";
CREATE TABLE "public"."m_car" (
  "customer_id" uuid NOT NULL,
  "license_plate" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "province" varchar(50) COLLATE "pg_catalog"."default",
  "brand" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "sub_model" varchar(100) COLLATE "pg_catalog"."default",
  "year" int4,
  "color" varchar(30) COLLATE "pg_catalog"."default",
  "engine_number" varchar(50) COLLATE "pg_catalog"."default",
  "chassis_number" varchar(50) COLLATE "pg_catalog"."default",
  "fuel_type" varchar(20) COLLATE "pg_catalog"."default",
  "transmission_type" varchar(20) COLLATE "pg_catalog"."default",
  "engine_cc" int4,
  "seating_capacity" int4,
  "mileage" int4 NOT NULL,
  "notes" text COLLATE "pg_catalog"."default",
  "user_id" uuid NOT NULL,
  "whitelabel_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_car"."customer_id" IS 'Customer ID';
COMMENT ON COLUMN "public"."m_car"."license_plate" IS 'License plate';
COMMENT ON COLUMN "public"."m_car"."province" IS 'Province';
COMMENT ON COLUMN "public"."m_car"."brand" IS 'Brand';
COMMENT ON COLUMN "public"."m_car"."model" IS 'Model';
COMMENT ON COLUMN "public"."m_car"."sub_model" IS 'Sub model';
COMMENT ON COLUMN "public"."m_car"."year" IS 'Year';
COMMENT ON COLUMN "public"."m_car"."color" IS 'Color';
COMMENT ON COLUMN "public"."m_car"."engine_number" IS 'Engine number';
COMMENT ON COLUMN "public"."m_car"."chassis_number" IS 'Chassis number';
COMMENT ON COLUMN "public"."m_car"."fuel_type" IS 'Fuel type';
COMMENT ON COLUMN "public"."m_car"."transmission_type" IS 'Transmission type';
COMMENT ON COLUMN "public"."m_car"."engine_cc" IS 'Engine CC';
COMMENT ON COLUMN "public"."m_car"."seating_capacity" IS 'Seating capacity';
COMMENT ON COLUMN "public"."m_car"."mileage" IS 'Mileage';
COMMENT ON COLUMN "public"."m_car"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_car"."user_id" IS 'Owner user ID';
COMMENT ON COLUMN "public"."m_car"."whitelabel_id" IS 'Whitelabel ID';
COMMENT ON COLUMN "public"."m_car"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_car"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_car"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_car
-- ----------------------------

-- ----------------------------
-- Table structure for m_customer
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_customer";
CREATE TABLE "public"."m_customer" (
  "customer_code" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "full_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "display_name" varchar(200) COLLATE "pg_catalog"."default",
  "customer_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "tax_id" varchar(20) COLLATE "pg_catalog"."default",
  "email" varchar(100) COLLATE "pg_catalog"."default",
  "phone_number" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "secondary_phone" varchar(20) COLLATE "pg_catalog"."default",
  "address" text COLLATE "pg_catalog"."default",
  "province" varchar(100) COLLATE "pg_catalog"."default",
  "city" varchar(100) COLLATE "pg_catalog"."default",
  "district" varchar(100) COLLATE "pg_catalog"."default",
  "postal_code" varchar(10) COLLATE "pg_catalog"."default",
  "country" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "contact_person" varchar(100) COLLATE "pg_catalog"."default",
  "contact_phone" varchar(20) COLLATE "pg_catalog"."default",
  "notes" text COLLATE "pg_catalog"."default",
  "total_visit_count" int4 NOT NULL,
  "total_spent" float8 NOT NULL,
  "user_id" uuid NOT NULL,
  "whitelabel_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_customer"."customer_code" IS 'Customer code';
COMMENT ON COLUMN "public"."m_customer"."full_name" IS 'Full name';
COMMENT ON COLUMN "public"."m_customer"."display_name" IS 'Display name';
COMMENT ON COLUMN "public"."m_customer"."customer_type" IS 'Customer type';
COMMENT ON COLUMN "public"."m_customer"."status" IS 'Status';
COMMENT ON COLUMN "public"."m_customer"."tax_id" IS 'Tax ID';
COMMENT ON COLUMN "public"."m_customer"."email" IS 'Email';
COMMENT ON COLUMN "public"."m_customer"."phone_number" IS 'Phone number';
COMMENT ON COLUMN "public"."m_customer"."secondary_phone" IS 'Secondary phone';
COMMENT ON COLUMN "public"."m_customer"."address" IS 'Address';
COMMENT ON COLUMN "public"."m_customer"."province" IS 'Province';
COMMENT ON COLUMN "public"."m_customer"."city" IS 'City';
COMMENT ON COLUMN "public"."m_customer"."district" IS 'District';
COMMENT ON COLUMN "public"."m_customer"."postal_code" IS 'Postal code';
COMMENT ON COLUMN "public"."m_customer"."country" IS 'Country';
COMMENT ON COLUMN "public"."m_customer"."contact_person" IS 'Contact person';
COMMENT ON COLUMN "public"."m_customer"."contact_phone" IS 'Contact phone';
COMMENT ON COLUMN "public"."m_customer"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_customer"."total_visit_count" IS 'Total visit count';
COMMENT ON COLUMN "public"."m_customer"."total_spent" IS 'Total spent';
COMMENT ON COLUMN "public"."m_customer"."user_id" IS 'Owner user ID';
COMMENT ON COLUMN "public"."m_customer"."whitelabel_id" IS 'Whitelabel ID';
COMMENT ON COLUMN "public"."m_customer"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_customer"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_customer"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_customer
-- ----------------------------

-- ----------------------------
-- Table structure for m_document
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_document";
CREATE TABLE "public"."m_document" (
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "original_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mime_type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "size" int8 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_document"."filename" IS 'Stored filename';
COMMENT ON COLUMN "public"."m_document"."original_name" IS 'Original upload filename';
COMMENT ON COLUMN "public"."m_document"."mime_type" IS 'MIME type';
COMMENT ON COLUMN "public"."m_document"."size" IS 'File size in bytes';
COMMENT ON COLUMN "public"."m_document"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_document"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_document"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_document
-- ----------------------------

-- ----------------------------
-- Table structure for m_email_config
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_email_config";
CREATE TABLE "public"."m_email_config" (
  "smtp_host" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "smtp_port" int4 NOT NULL,
  "smtp_user" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "from_email" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "from_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_email_config"."smtp_host" IS 'SMTP server host';
COMMENT ON COLUMN "public"."m_email_config"."smtp_port" IS 'SMTP server port';
COMMENT ON COLUMN "public"."m_email_config"."smtp_user" IS 'SMTP username';
COMMENT ON COLUMN "public"."m_email_config"."from_email" IS 'Sender email address';
COMMENT ON COLUMN "public"."m_email_config"."from_name" IS 'Sender display name';
COMMENT ON COLUMN "public"."m_email_config"."is_active" IS 'Whether config is active';
COMMENT ON COLUMN "public"."m_email_config"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_email_config"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_email_config"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_email_config
-- ----------------------------

-- ----------------------------
-- Table structure for m_email_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_email_log";
CREATE TABLE "public"."m_email_log" (
  "to_address" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "cc" varchar(500) COLLATE "pg_catalog"."default",
  "bcc" varchar(500) COLLATE "pg_catalog"."default",
  "subject" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "body" text COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "error_message" text COLLATE "pg_catalog"."default",
  "sent_at" timestamptz(6),
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_email_log"."to_address" IS 'Recipient email address';
COMMENT ON COLUMN "public"."m_email_log"."cc" IS 'CC recipients';
COMMENT ON COLUMN "public"."m_email_log"."bcc" IS 'BCC recipients';
COMMENT ON COLUMN "public"."m_email_log"."subject" IS 'Email subject';
COMMENT ON COLUMN "public"."m_email_log"."body" IS 'Email body';
COMMENT ON COLUMN "public"."m_email_log"."status" IS 'Email status';
COMMENT ON COLUMN "public"."m_email_log"."error_message" IS 'Error message if failed';
COMMENT ON COLUMN "public"."m_email_log"."sent_at" IS 'When email was sent';
COMMENT ON COLUMN "public"."m_email_log"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_email_log"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_email_log"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_email_log
-- ----------------------------

-- ----------------------------
-- Table structure for m_payment
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_payment";
CREATE TABLE "public"."m_payment" (
  "payment_no" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "invoice_id" uuid,
  "job_id" uuid,
  "customer_id" uuid,
  "payment_date" timestamptz(6),
  "payment_method_id" uuid,
  "amount" float8 NOT NULL,
  "amount_received" float8 NOT NULL,
  "change_amount" float8 NOT NULL,
  "currency" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "exchange_rate" float8 NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "reference_number" varchar(100) COLLATE "pg_catalog"."default",
  "bank_name" varchar(100) COLLATE "pg_catalog"."default",
  "cheque_number" varchar(50) COLLATE "pg_catalog"."default",
  "cheque_bank" varchar(100) COLLATE "pg_catalog"."default",
  "cheque_date" date,
  "notes" text COLLATE "pg_catalog"."default",
  "received_by" uuid,
  "approved_by" uuid,
  "approved_at" timestamptz(6),
  "refunded_amount" float8 NOT NULL,
  "refunded_at" timestamptz(6),
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_payment"."payment_no" IS 'Payment number';
COMMENT ON COLUMN "public"."m_payment"."invoice_id" IS 'Invoice ID';
COMMENT ON COLUMN "public"."m_payment"."job_id" IS 'Job ID';
COMMENT ON COLUMN "public"."m_payment"."customer_id" IS 'Customer ID';
COMMENT ON COLUMN "public"."m_payment"."payment_date" IS 'Payment date';
COMMENT ON COLUMN "public"."m_payment"."payment_method_id" IS 'Payment method ID';
COMMENT ON COLUMN "public"."m_payment"."amount" IS 'Payment amount';
COMMENT ON COLUMN "public"."m_payment"."amount_received" IS 'Amount received';
COMMENT ON COLUMN "public"."m_payment"."change_amount" IS 'Change amount';
COMMENT ON COLUMN "public"."m_payment"."currency" IS 'Currency';
COMMENT ON COLUMN "public"."m_payment"."exchange_rate" IS 'Exchange rate';
COMMENT ON COLUMN "public"."m_payment"."status" IS 'Payment status';
COMMENT ON COLUMN "public"."m_payment"."reference_number" IS 'Reference number';
COMMENT ON COLUMN "public"."m_payment"."bank_name" IS 'Bank name';
COMMENT ON COLUMN "public"."m_payment"."cheque_number" IS 'Cheque number';
COMMENT ON COLUMN "public"."m_payment"."cheque_bank" IS 'Cheque bank';
COMMENT ON COLUMN "public"."m_payment"."cheque_date" IS 'Cheque date';
COMMENT ON COLUMN "public"."m_payment"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_payment"."received_by" IS 'Received by user ID';
COMMENT ON COLUMN "public"."m_payment"."approved_by" IS 'Approved by user ID';
COMMENT ON COLUMN "public"."m_payment"."approved_at" IS 'Approved at';
COMMENT ON COLUMN "public"."m_payment"."refunded_amount" IS 'Refunded amount';
COMMENT ON COLUMN "public"."m_payment"."refunded_at" IS 'Refunded at';
COMMENT ON COLUMN "public"."m_payment"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_payment"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_payment"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_payment
-- ----------------------------

-- ----------------------------
-- Table structure for m_payment_history
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_payment_history";
CREATE TABLE "public"."m_payment_history" (
  "payment_id" uuid NOT NULL,
  "from_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "to_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "changed_by" uuid,
  "changed_at" timestamptz(6),
  "reason" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_payment_history"."payment_id" IS 'Payment ID';
COMMENT ON COLUMN "public"."m_payment_history"."from_status" IS 'Previous status';
COMMENT ON COLUMN "public"."m_payment_history"."to_status" IS 'New status';
COMMENT ON COLUMN "public"."m_payment_history"."changed_by" IS 'Changed by user ID';
COMMENT ON COLUMN "public"."m_payment_history"."changed_at" IS 'Changed at';
COMMENT ON COLUMN "public"."m_payment_history"."reason" IS 'Reason';
COMMENT ON COLUMN "public"."m_payment_history"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_payment_history"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_payment_history"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_payment_history
-- ----------------------------

-- ----------------------------
-- Table structure for m_purchase_order_detail
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_purchase_order_detail";
CREATE TABLE "public"."m_purchase_order_detail" (
  "po_header_id" uuid NOT NULL,
  "part_id" uuid,
  "quantity_ordered" int4 NOT NULL,
  "quantity_received" int4 NOT NULL,
  "unit_price" float8 NOT NULL,
  "total_price" float8 NOT NULL,
  "discount" float8 NOT NULL,
  "net_price" float8 NOT NULL,
  "note" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_purchase_order_detail"."po_header_id" IS 'Purchase order header ID';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."part_id" IS 'Part ID';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."quantity_ordered" IS 'Quantity ordered';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."quantity_received" IS 'Quantity received';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."unit_price" IS 'Unit price';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."total_price" IS 'Total price';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."discount" IS 'Discount amount';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."net_price" IS 'Net price after discount';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."note" IS 'Note';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_purchase_order_detail"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_purchase_order_detail
-- ----------------------------

-- ----------------------------
-- Table structure for m_purchase_order_header
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_purchase_order_header";
CREATE TABLE "public"."m_purchase_order_header" (
  "po_no" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "quotation_id" uuid,
  "job_id" uuid,
  "supplier_id" uuid,
  "po_date" date,
  "expected_delivery_date" date,
  "actual_delivery_date" date,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "subtotal" float8 NOT NULL,
  "tax_rate" float8 NOT NULL,
  "tax_amount" float8 NOT NULL,
  "discount_type" varchar(20) COLLATE "pg_catalog"."default",
  "discount_value" float8 NOT NULL,
  "total" float8 NOT NULL,
  "currency" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "exchange_rate" float8 NOT NULL,
  "shipping_cost" float8 NOT NULL,
  "payment_terms" text COLLATE "pg_catalog"."default",
  "delivery_address" text COLLATE "pg_catalog"."default",
  "notes" text COLLATE "pg_catalog"."default",
  "terms_and_conditions" text COLLATE "pg_catalog"."default",
  "sent_at" timestamp(6),
  "confirmed_at" timestamp(6),
  "received_by" uuid,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_purchase_order_header"."po_no" IS 'Purchase order number';
COMMENT ON COLUMN "public"."m_purchase_order_header"."quotation_id" IS 'Related quotation ID';
COMMENT ON COLUMN "public"."m_purchase_order_header"."job_id" IS 'Related job ID';
COMMENT ON COLUMN "public"."m_purchase_order_header"."supplier_id" IS 'Supplier ID';
COMMENT ON COLUMN "public"."m_purchase_order_header"."po_date" IS 'Purchase order date';
COMMENT ON COLUMN "public"."m_purchase_order_header"."expected_delivery_date" IS 'Expected delivery date';
COMMENT ON COLUMN "public"."m_purchase_order_header"."actual_delivery_date" IS 'Actual delivery date';
COMMENT ON COLUMN "public"."m_purchase_order_header"."status" IS 'PO status';
COMMENT ON COLUMN "public"."m_purchase_order_header"."subtotal" IS 'Subtotal amount';
COMMENT ON COLUMN "public"."m_purchase_order_header"."tax_rate" IS 'Tax rate percentage';
COMMENT ON COLUMN "public"."m_purchase_order_header"."tax_amount" IS 'Tax amount';
COMMENT ON COLUMN "public"."m_purchase_order_header"."discount_type" IS 'Discount type (percentage/fixed)';
COMMENT ON COLUMN "public"."m_purchase_order_header"."discount_value" IS 'Discount value';
COMMENT ON COLUMN "public"."m_purchase_order_header"."total" IS 'Total amount';
COMMENT ON COLUMN "public"."m_purchase_order_header"."currency" IS 'Currency code';
COMMENT ON COLUMN "public"."m_purchase_order_header"."exchange_rate" IS 'Exchange rate';
COMMENT ON COLUMN "public"."m_purchase_order_header"."shipping_cost" IS 'Shipping cost';
COMMENT ON COLUMN "public"."m_purchase_order_header"."payment_terms" IS 'Payment terms';
COMMENT ON COLUMN "public"."m_purchase_order_header"."delivery_address" IS 'Delivery address';
COMMENT ON COLUMN "public"."m_purchase_order_header"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_purchase_order_header"."terms_and_conditions" IS 'Terms and conditions';
COMMENT ON COLUMN "public"."m_purchase_order_header"."sent_at" IS 'Timestamp when PO was sent';
COMMENT ON COLUMN "public"."m_purchase_order_header"."confirmed_at" IS 'Timestamp when PO was confirmed';
COMMENT ON COLUMN "public"."m_purchase_order_header"."received_by" IS 'User who received the goods';
COMMENT ON COLUMN "public"."m_purchase_order_header"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_purchase_order_header"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_purchase_order_header"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_purchase_order_header
-- ----------------------------

-- ----------------------------
-- Table structure for m_purchase_order_status_history
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_purchase_order_status_history";
CREATE TABLE "public"."m_purchase_order_status_history" (
  "po_header_id" uuid NOT NULL,
  "from_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "to_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "changed_by" uuid,
  "changed_at" timestamp(6),
  "reason" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."po_header_id" IS 'Purchase order header ID';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."from_status" IS 'Previous status';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."to_status" IS 'New status';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."changed_by" IS 'User who changed the status';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."changed_at" IS 'Timestamp of status change';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."reason" IS 'Reason for status change';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_purchase_order_status_history"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_purchase_order_status_history
-- ----------------------------

-- ----------------------------
-- Table structure for m_quotation
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_quotation";
CREATE TABLE "public"."m_quotation" (
  "quotation_no" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "job_id" uuid,
  "customer_id" uuid,
  "quotation_date" date,
  "expiry_date" date,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "subtotal" float8 NOT NULL,
  "tax_rate" float8 NOT NULL,
  "tax_amount" float8 NOT NULL,
  "discount_type" varchar(20) COLLATE "pg_catalog"."default",
  "discount_value" float8 NOT NULL,
  "total" float8 NOT NULL,
  "amount_in_words_th" text COLLATE "pg_catalog"."default",
  "amount_in_words_en" text COLLATE "pg_catalog"."default",
  "currency" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "exchange_rate" float8 NOT NULL,
  "notes" text COLLATE "pg_catalog"."default",
  "terms_and_conditions" text COLLATE "pg_catalog"."default",
  "approved_by" uuid,
  "approved_at" timestamptz(6),
  "rejected_reason" text COLLATE "pg_catalog"."default",
  "converted_to_po" bool NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_quotation"."quotation_no" IS 'Quotation number';
COMMENT ON COLUMN "public"."m_quotation"."job_id" IS 'Job ID';
COMMENT ON COLUMN "public"."m_quotation"."customer_id" IS 'Customer ID';
COMMENT ON COLUMN "public"."m_quotation"."quotation_date" IS 'Quotation date';
COMMENT ON COLUMN "public"."m_quotation"."expiry_date" IS 'Expiry date';
COMMENT ON COLUMN "public"."m_quotation"."status" IS 'Status';
COMMENT ON COLUMN "public"."m_quotation"."subtotal" IS 'Subtotal';
COMMENT ON COLUMN "public"."m_quotation"."tax_rate" IS 'Tax rate';
COMMENT ON COLUMN "public"."m_quotation"."tax_amount" IS 'Tax amount';
COMMENT ON COLUMN "public"."m_quotation"."discount_type" IS 'Discount type';
COMMENT ON COLUMN "public"."m_quotation"."discount_value" IS 'Discount value';
COMMENT ON COLUMN "public"."m_quotation"."total" IS 'Total';
COMMENT ON COLUMN "public"."m_quotation"."amount_in_words_th" IS 'Amount in words (Thai)';
COMMENT ON COLUMN "public"."m_quotation"."amount_in_words_en" IS 'Amount in words (English)';
COMMENT ON COLUMN "public"."m_quotation"."currency" IS 'Currency';
COMMENT ON COLUMN "public"."m_quotation"."exchange_rate" IS 'Exchange rate';
COMMENT ON COLUMN "public"."m_quotation"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_quotation"."terms_and_conditions" IS 'Terms and conditions';
COMMENT ON COLUMN "public"."m_quotation"."approved_by" IS 'Approved by user ID';
COMMENT ON COLUMN "public"."m_quotation"."approved_at" IS 'Approval timestamp';
COMMENT ON COLUMN "public"."m_quotation"."rejected_reason" IS 'Rejection reason';
COMMENT ON COLUMN "public"."m_quotation"."converted_to_po" IS 'Converted to PO';
COMMENT ON COLUMN "public"."m_quotation"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_quotation"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_quotation"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_quotation
-- ----------------------------

-- ----------------------------
-- Table structure for m_receipt
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_receipt";
CREATE TABLE "public"."m_receipt" (
  "receipt_no" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "payment_id" uuid NOT NULL,
  "invoice_id" uuid,
  "customer_id" uuid,
  "receipt_date" timestamptz(6),
  "receipt_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "amount" float8 NOT NULL,
  "amount_in_words_th" text COLLATE "pg_catalog"."default",
  "amount_in_words_en" text COLLATE "pg_catalog"."default",
  "currency" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "notes" text COLLATE "pg_catalog"."default",
  "issued_by" uuid,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_receipt"."receipt_no" IS 'Receipt number';
COMMENT ON COLUMN "public"."m_receipt"."payment_id" IS 'Payment ID';
COMMENT ON COLUMN "public"."m_receipt"."invoice_id" IS 'Invoice ID';
COMMENT ON COLUMN "public"."m_receipt"."customer_id" IS 'Customer ID';
COMMENT ON COLUMN "public"."m_receipt"."receipt_date" IS 'Receipt date';
COMMENT ON COLUMN "public"."m_receipt"."receipt_type" IS 'Receipt type';
COMMENT ON COLUMN "public"."m_receipt"."amount" IS 'Receipt amount';
COMMENT ON COLUMN "public"."m_receipt"."amount_in_words_th" IS 'Amount in words (Thai)';
COMMENT ON COLUMN "public"."m_receipt"."amount_in_words_en" IS 'Amount in words (English)';
COMMENT ON COLUMN "public"."m_receipt"."currency" IS 'Currency';
COMMENT ON COLUMN "public"."m_receipt"."status" IS 'Receipt status';
COMMENT ON COLUMN "public"."m_receipt"."notes" IS 'Notes';
COMMENT ON COLUMN "public"."m_receipt"."issued_by" IS 'Issued by user ID';
COMMENT ON COLUMN "public"."m_receipt"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_receipt"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_receipt"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_receipt
-- ----------------------------

-- ----------------------------
-- Table structure for m_translation
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_translation";
CREATE TABLE "public"."m_translation" (
  "locale" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "value" text COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_translation"."locale" IS 'Locale code (e.g. en, pt-BR)';
COMMENT ON COLUMN "public"."m_translation"."key" IS 'Translation key';
COMMENT ON COLUMN "public"."m_translation"."value" IS 'Translated value';
COMMENT ON COLUMN "public"."m_translation"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_translation"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_translation"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_translation
-- ----------------------------

-- ----------------------------
-- Table structure for m_wos_order
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_wos_order";
CREATE TABLE "public"."m_wos_order" (
  "order_number" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "customer_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "customer_email" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "customer_phone" varchar(50) COLLATE "pg_catalog"."default",
  "items" json,
  "total_amount" float8 NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'pending'::character varying,
  "notes" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."m_wos_order"."order_number" IS 'Unique order number';
COMMENT ON COLUMN "public"."m_wos_order"."customer_name" IS 'Customer full name';
COMMENT ON COLUMN "public"."m_wos_order"."customer_email" IS 'Customer email address';
COMMENT ON COLUMN "public"."m_wos_order"."customer_phone" IS 'Customer phone number';
COMMENT ON COLUMN "public"."m_wos_order"."items" IS 'Order items as JSON';
COMMENT ON COLUMN "public"."m_wos_order"."total_amount" IS 'Total order amount';
COMMENT ON COLUMN "public"."m_wos_order"."status" IS 'Order status';
COMMENT ON COLUMN "public"."m_wos_order"."notes" IS 'Additional notes';
COMMENT ON COLUMN "public"."m_wos_order"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."m_wos_order"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."m_wos_order"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of m_wos_order
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table alembic_version
-- ----------------------------
ALTER TABLE "public"."alembic_version" ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");

-- ----------------------------
-- Indexes structure for table app_access_tokens
-- ----------------------------
CREATE INDEX "ix_hashed_jti" ON "public"."app_access_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_hashed_jti_key" UNIQUE ("hashed_jti");
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_previous_hashed_jti_key" UNIQUE ("previous_hashed_jti");
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "uq_access_tokens_refresh_id" UNIQUE ("refresh_id");

-- ----------------------------
-- Primary Key structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_permissions
-- ----------------------------
ALTER TABLE "public"."app_permissions" ADD CONSTRAINT "app_permissions_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table app_permissions
-- ----------------------------
ALTER TABLE "public"."app_permissions" ADD CONSTRAINT "app_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "uq_refresh_tokens_session_id" UNIQUE ("session_id");

-- ----------------------------
-- Primary Key structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "app_refresh_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "uq_role_permissions" UNIQUE ("role_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_roles
-- ----------------------------
ALTER TABLE "public"."app_roles" ADD CONSTRAINT "app_roles_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table app_roles
-- ----------------------------
ALTER TABLE "public"."app_roles" ADD CONSTRAINT "app_roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table app_sessions
-- ----------------------------
CREATE INDEX "ix_sessions_user_id_user_agent_device" ON "public"."app_sessions" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "user_agent" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "device" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "uq_sessions_user_id_user_agent_device" UNIQUE ("user_id", "user_agent", "device");

-- ----------------------------
-- Primary Key structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "app_sessions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "uq_user_roles" UNIQUE ("user_id", "role_id");

-- ----------------------------
-- Primary Key structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "uq_users_email_status" UNIQUE ("email", "status");
ALTER TABLE "public"."app_users" ADD CONSTRAINT "uq_users_username_status" UNIQUE ("username", "status");

-- ----------------------------
-- Primary Key structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "app_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_activity_log
-- ----------------------------
ALTER TABLE "public"."iot_activity_log" ADD CONSTRAINT "iot_activity_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_alarm_log
-- ----------------------------
ALTER TABLE "public"."iot_alarm_log" ADD CONSTRAINT "iot_alarm_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_data
-- ----------------------------
ALTER TABLE "public"."iot_data" ADD CONSTRAINT "iot_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_device
-- ----------------------------
ALTER TABLE "public"."iot_device" ADD CONSTRAINT "iot_device_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_device_alert
-- ----------------------------
ALTER TABLE "public"."iot_device_alert" ADD CONSTRAINT "iot_device_alert_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table iot_device_config
-- ----------------------------
ALTER TABLE "public"."iot_device_config" ADD CONSTRAINT "uq_device_config_device_id" UNIQUE ("device_id");

-- ----------------------------
-- Primary Key structure for table iot_device_config
-- ----------------------------
ALTER TABLE "public"."iot_device_config" ADD CONSTRAINT "iot_device_config_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table iot_device_status
-- ----------------------------
ALTER TABLE "public"."iot_device_status" ADD CONSTRAINT "uq_device_status_device_id" UNIQUE ("device_id");

-- ----------------------------
-- Primary Key structure for table iot_device_status
-- ----------------------------
ALTER TABLE "public"."iot_device_status" ADD CONSTRAINT "iot_device_status_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table iot_schedule
-- ----------------------------
ALTER TABLE "public"."iot_schedule" ADD CONSTRAINT "iot_schedule_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table item
-- ----------------------------
ALTER TABLE "public"."item" ADD CONSTRAINT "item_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_batch_job
-- ----------------------------
ALTER TABLE "public"."m_batch_job" ADD CONSTRAINT "m_batch_job_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_batch_job_log
-- ----------------------------
ALTER TABLE "public"."m_batch_job_log" ADD CONSTRAINT "m_batch_job_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table m_car
-- ----------------------------
ALTER TABLE "public"."m_car" ADD CONSTRAINT "m_car_license_plate_key" UNIQUE ("license_plate");

-- ----------------------------
-- Primary Key structure for table m_car
-- ----------------------------
ALTER TABLE "public"."m_car" ADD CONSTRAINT "m_car_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table m_customer
-- ----------------------------
ALTER TABLE "public"."m_customer" ADD CONSTRAINT "m_customer_customer_code_key" UNIQUE ("customer_code");

-- ----------------------------
-- Primary Key structure for table m_customer
-- ----------------------------
ALTER TABLE "public"."m_customer" ADD CONSTRAINT "m_customer_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_document
-- ----------------------------
ALTER TABLE "public"."m_document" ADD CONSTRAINT "m_document_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_email_config
-- ----------------------------
ALTER TABLE "public"."m_email_config" ADD CONSTRAINT "m_email_config_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_email_log
-- ----------------------------
ALTER TABLE "public"."m_email_log" ADD CONSTRAINT "m_email_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_payment
-- ----------------------------
ALTER TABLE "public"."m_payment" ADD CONSTRAINT "m_payment_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_payment_history
-- ----------------------------
ALTER TABLE "public"."m_payment_history" ADD CONSTRAINT "m_payment_history_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_purchase_order_detail
-- ----------------------------
ALTER TABLE "public"."m_purchase_order_detail" ADD CONSTRAINT "m_purchase_order_detail_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_purchase_order_header
-- ----------------------------
ALTER TABLE "public"."m_purchase_order_header" ADD CONSTRAINT "m_purchase_order_header_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_purchase_order_status_history
-- ----------------------------
ALTER TABLE "public"."m_purchase_order_status_history" ADD CONSTRAINT "m_purchase_order_status_history_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_quotation
-- ----------------------------
ALTER TABLE "public"."m_quotation" ADD CONSTRAINT "m_quotation_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_receipt
-- ----------------------------
ALTER TABLE "public"."m_receipt" ADD CONSTRAINT "m_receipt_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table m_translation
-- ----------------------------
ALTER TABLE "public"."m_translation" ADD CONSTRAINT "m_translation_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table m_wos_order
-- ----------------------------
ALTER TABLE "public"."m_wos_order" ADD CONSTRAINT "m_wos_order_order_number_key" UNIQUE ("order_number");

-- ----------------------------
-- Primary Key structure for table m_wos_order
-- ----------------------------
ALTER TABLE "public"."m_wos_order" ADD CONSTRAINT "m_wos_order_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_refresh_id_fkey" FOREIGN KEY ("refresh_id") REFERENCES "public"."app_refresh_tokens" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "app_refresh_tokens_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."app_sessions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."app_permissions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."app_roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "app_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."app_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."app_roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."app_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
