/*
 Navicat Premium Dump SQL

 Source Server         : postgres-Docker-5437
 Source Server Type    : PostgreSQL
 Source Server Version : 170011 (170011)
 Source Host           : localhost:5437
 Source Catalog        : ioterp
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170011 (170011)
 File Encoding         : 65001

 Date: 01/10/2026 00:18:22
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
-- Type structure for notification_type_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."notification_type_enum";
CREATE TYPE "public"."notification_type_enum" AS ENUM (
  'KNOWLEDGE_CREATED',
  'KNOWLEDGE_UPDATED',
  'KNOWLEDGE_DELETED',
  'SYSTEM_ALERT'
);

-- ----------------------------
-- Type structure for online_status_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."online_status_enum";
CREATE TYPE "public"."online_status_enum" AS ENUM (
  'OFFLINE',
  'ONLINE',
  'AWAY',
  'BUSY'
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
  'INACTIVE',
  'ACTIVE',
  'SUSPENDED',
  'DELETED'
);

-- ----------------------------
-- Sequence structure for activity_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."activity_log_id_seq";
CREATE SEQUENCE "public"."activity_log_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for command_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."command_log_id_seq";
CREATE SEQUENCE "public"."command_log_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for device_alert_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."device_alert_id_seq";
CREATE SEQUENCE "public"."device_alert_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for device_config_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."device_config_id_seq";
CREATE SEQUENCE "public"."device_config_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for device_status_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."device_status_id_seq";
CREATE SEQUENCE "public"."device_status_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for erp_users_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."erp_users_id_seq";
CREATE SEQUENCE "public"."erp_users_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 10000000000
CACHE 1;

-- ----------------------------
-- Sequence structure for erp_users_id_seq1
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."erp_users_id_seq1";
CREATE SEQUENCE "public"."erp_users_id_seq1"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 10000000000
CACHE 1;

-- ----------------------------
-- Sequence structure for iot_data_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."iot_data_id_seq";
CREATE SEQUENCE "public"."iot_data_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_air_control_air_control_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_air_control_air_control_id_seq";
CREATE SEQUENCE "public"."sd_air_control_air_control_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_air_mod_air_mod_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_air_mod_air_mod_id_seq";
CREATE SEQUENCE "public"."sd_air_mod_air_mod_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_air_period_air_period_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_air_period_air_period_id_seq";
CREATE SEQUENCE "public"."sd_air_period_air_period_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_air_setting_warning_air_setting_warning_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_air_setting_warning_air_setting_warning_id_seq";
CREATE SEQUENCE "public"."sd_air_setting_warning_air_setting_warning_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_air_warning_air_warning_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_air_warning_air_warning_id_seq";
CREATE SEQUENCE "public"."sd_air_warning_air_warning_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_api_key_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_api_key_id_seq";
CREATE SEQUENCE "public"."sd_api_key_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_audit_log_audit_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_audit_log_audit_id_seq";
CREATE SEQUENCE "public"."sd_audit_log_audit_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_channel_template_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_channel_template_id_seq";
CREATE SEQUENCE "public"."sd_channel_template_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_category_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_category_id_seq";
CREATE SEQUENCE "public"."sd_device_category_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_group_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_group_id_seq";
CREATE SEQUENCE "public"."sd_device_group_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_member_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_member_id_seq";
CREATE SEQUENCE "public"."sd_device_member_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_notification_config_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_notification_config_id_seq";
CREATE SEQUENCE "public"."sd_device_notification_config_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_schedule_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_schedule_id_seq";
CREATE SEQUENCE "public"."sd_device_schedule_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_device_status_history_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_device_status_history_id_seq";
CREATE SEQUENCE "public"."sd_device_status_history_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_group_notification_config_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_group_notification_config_id_seq";
CREATE SEQUENCE "public"."sd_group_notification_config_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_device_alarm_action_alarm_action_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_device_alarm_action_alarm_action_id_seq";
CREATE SEQUENCE "public"."sd_iot_device_alarm_action_alarm_action_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_device_device_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_device_device_id_seq";
CREATE SEQUENCE "public"."sd_iot_device_device_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_device_type_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_device_type_type_id_seq";
CREATE SEQUENCE "public"."sd_iot_device_type_type_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_location_location_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_location_location_id_seq";
CREATE SEQUENCE "public"."sd_iot_location_location_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_mqtt_mqtt_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_mqtt_mqtt_id_seq";
CREATE SEQUENCE "public"."sd_iot_mqtt_mqtt_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_iot_schedule_schedule_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_iot_schedule_schedule_id_seq";
CREATE SEQUENCE "public"."sd_iot_schedule_schedule_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_notification_channel_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_notification_channel_id_seq";
CREATE SEQUENCE "public"."sd_notification_channel_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_notification_condition_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_notification_condition_id_seq";
CREATE SEQUENCE "public"."sd_notification_condition_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_notification_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_notification_log_id_seq";
CREATE SEQUENCE "public"."sd_notification_log_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_notification_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_notification_type_id_seq";
CREATE SEQUENCE "public"."sd_notification_type_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_report_data_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_report_data_id_seq";
CREATE SEQUENCE "public"."sd_report_data_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_sensor_data_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_sensor_data_id_seq";
CREATE SEQUENCE "public"."sd_sensor_data_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sd_system_setting_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sd_system_setting_id_seq";
CREATE SEQUENCE "public"."sd_system_setting_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Table structure for activity_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."activity_log";
CREATE TABLE "public"."activity_log" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('activity_log_id_seq'::regclass),
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "device_id" varchar(50) COLLATE "pg_catalog"."default",
  "user_id" varchar(100) COLLATE "pg_catalog"."default",
  "details" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "data" jsonb,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default",
  "user_agent" varchar(500) COLLATE "pg_catalog"."default",
  "session_id" varchar(100) COLLATE "pg_catalog"."default",
  "correlation_id" varchar(100) COLLATE "pg_catalog"."default",
  "timestamp" timestamptz(6) NOT NULL,
  "stack_trace" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of activity_log
-- ----------------------------

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
INSERT INTO "public"."alembic_version" VALUES ('36c2e35e1165');

-- ----------------------------
-- Table structure for bigo_cache_stats
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_cache_stats";
CREATE TABLE "public"."bigo_cache_stats" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "namespace" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'bigo'::character varying,
  "hits" int4 NOT NULL DEFAULT 0,
  "misses" int4 NOT NULL DEFAULT 0,
  "sets" int4 NOT NULL DEFAULT 0,
  "deletes" int4 NOT NULL DEFAULT 0,
  "errors" int4 NOT NULL DEFAULT 0,
  "hit_ratio" numeric(6,4) NOT NULL DEFAULT 0,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_cache_stats
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_kafka_consumers
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_kafka_consumers";
CREATE TABLE "public"."bigo_kafka_consumers" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "group_id" varchar(300) COLLATE "pg_catalog"."default" NOT NULL,
  "topic" varchar(300) COLLATE "pg_catalog"."default" NOT NULL,
  "member_count" int4 NOT NULL DEFAULT 0,
  "total_lag" int4 NOT NULL DEFAULT 0,
  "health" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'HEALTHY'::character varying,
  "last_commit_at" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_kafka_consumers
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_kafka_queues
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_kafka_queues";
CREATE TABLE "public"."bigo_kafka_queues" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "topic" varchar(300) COLLATE "pg_catalog"."default" NOT NULL,
  "partition" int4 NOT NULL DEFAULT 0,
  "current_offset" int4 NOT NULL DEFAULT 0,
  "log_end_offset" int4 NOT NULL DEFAULT 0,
  "lag" int4 NOT NULL DEFAULT 0,
  "health" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'HEALTHY'::character varying,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_kafka_queues
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_kafka_topics
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_kafka_topics";
CREATE TABLE "public"."bigo_kafka_topics" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(300) COLLATE "pg_catalog"."default" NOT NULL,
  "partitions" int4 NOT NULL DEFAULT 3,
  "replication_factor" int4 NOT NULL DEFAULT 1,
  "retention_ms" int4 NOT NULL DEFAULT 604800000,
  "max_message_bytes" int4 NOT NULL DEFAULT 1048576,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_kafka_topics
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_memory_leaks
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_memory_leaks";
CREATE TABLE "public"."bigo_memory_leaks" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "location" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "leak_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'UNKNOWN'::character varying,
  "growth_mb_per_hour" numeric(20,4) NOT NULL DEFAULT 0,
  "current_bytes" int4 NOT NULL DEFAULT 0,
  "samples" int4 NOT NULL DEFAULT 0,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'OPEN'::character varying,
  "detected_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_memory_leaks
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_memory_snapshots
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_memory_snapshots";
CREATE TABLE "public"."bigo_memory_snapshots" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "process_id" int4 NOT NULL DEFAULT 0,
  "rss_mb" numeric(20,4) NOT NULL DEFAULT 0,
  "vms_mb" numeric(20,4) NOT NULL DEFAULT 0,
  "percent" numeric(8,4) NOT NULL DEFAULT 0,
  "pressure" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'NORMAL'::character varying,
  "top_allocations_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_memory_snapshots
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_metrics
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_metrics";
CREATE TABLE "public"."bigo_metrics" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "kind" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "value" numeric(20,8) NOT NULL DEFAULT 0,
  "unit" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "labels_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_metrics
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_profiles
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_profiles";
CREATE TABLE "public"."bigo_profiles" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "function_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "module" varchar(200) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "complexity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'UNKNOWN'::character varying,
  "sample_size" int4 NOT NULL DEFAULT 0,
  "avg_ms" numeric(20,8) NOT NULL DEFAULT 0,
  "p95_ms" numeric(20,8) NOT NULL DEFAULT 0,
  "memory_peak_mb" numeric(20,8) NOT NULL DEFAULT 0,
  "notes" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_profiles
-- ----------------------------

-- ----------------------------
-- Table structure for bigo_ws_sessions
-- ----------------------------
DROP TABLE IF EXISTS "public"."bigo_ws_sessions";
CREATE TABLE "public"."bigo_ws_sessions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "conn_id" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar(64) COLLATE "pg_catalog"."default",
  "rooms_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "connected_at" timestamptz(6) NOT NULL DEFAULT now(),
  "disconnected_at" timestamptz(6),
  "duration_s" int4 NOT NULL DEFAULT 0,
  "messages_sent" int4 NOT NULL DEFAULT 0,
  "messages_recv" int4 NOT NULL DEFAULT 0,
  "close_reason" varchar(100) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of bigo_ws_sessions
-- ----------------------------

-- ----------------------------
-- Table structure for command_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."command_log";
CREATE TABLE "public"."command_log" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('command_log_id_seq'::regclass),
  "device_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "action" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "parameters" jsonb,
  "metadata" jsonb,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "issued_by" varchar(100) COLLATE "pg_catalog"."default",
  "client_ip" varchar(45) COLLATE "pg_catalog"."default",
  "response" jsonb,
  "error" varchar(500) COLLATE "pg_catalog"."default",
  "issued_at" timestamptz(6) NOT NULL,
  "sent_at" timestamptz(6),
  "executed_at" timestamptz(6),
  "failed_at" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of command_log
-- ----------------------------

-- ----------------------------
-- Table structure for device_alert
-- ----------------------------
DROP TABLE IF EXISTS "public"."device_alert";
CREATE TABLE "public"."device_alert" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('device_alert_id_seq'::regclass),
  "device_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "metric" varchar(100) COLLATE "pg_catalog"."default",
  "value" float8,
  "threshold" jsonb,
  "severity" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "message" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "details" jsonb,
  "resolved" bool NOT NULL,
  "resolution_notes" text COLLATE "pg_catalog"."default",
  "resolved_by" varchar(100) COLLATE "pg_catalog"."default",
  "resolved_at" timestamptz(6),
  "acknowledged" bool NOT NULL,
  "acknowledged_by" varchar(100) COLLATE "pg_catalog"."default",
  "acknowledged_at" timestamptz(6),
  "escalation" jsonb,
  "data_id" int4,
  "expires_at" timestamptz(6),
  "notification_count" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of device_alert
-- ----------------------------
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 1, '2', 'offline', 'humidity', 63.89, '{"max": 50}', 'low', 'Alert #1', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 2, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 2, '3', 'battery', 'co2', 32.82, '{"max": 50}', 'medium', 'Alert #2', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 3, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 3, '4', 'sensor_error', 'temperature', 10.62, '{"max": 50}', 'high', 'Alert #3', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 4, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 4, '5', 'threshold', 'humidity', 20.38, '{"max": 50}', 'critical', 'Alert #4', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 5, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 5, '6', 'offline', 'co2', 71.58, '{"max": 50}', 'info', 'Alert #5', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 6, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 6, '7', 'battery', 'temperature', 59.69, '{"max": 50}', 'low', 'Alert #6', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 7, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 7, '8', 'sensor_error', 'humidity', 64.51, '{"max": 50}', 'medium', 'Alert #7', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 8, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 8, '9', 'threshold', 'co2', 28.46, '{"max": 50}', 'high', 'Alert #8', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 9, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 9, '10', 'offline', 'temperature', 14.85, '{"max": 50}', 'critical', 'Alert #9', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 10, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 10, '11', 'battery', 'humidity', 82.89, '{"max": 50}', 'info', 'Alert #10', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 11, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 11, '12', 'sensor_error', 'co2', 33.12, '{"max": 50}', 'low', 'Alert #11', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 12, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 12, '13', 'threshold', 'temperature', 34.24, '{"max": 50}', 'medium', 'Alert #12', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 13, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 13, '14', 'offline', 'humidity', 60.27, '{"max": 50}', 'high', 'Alert #13', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 14, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 14, '15', 'battery', 'co2', 18.51, '{"max": 50}', 'critical', 'Alert #14', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 15, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 15, '16', 'sensor_error', 'temperature', 73.24, '{"max": 50}', 'info', 'Alert #15', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 16, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 16, '17', 'threshold', 'humidity', 41.45, '{"max": 50}', 'low', 'Alert #16', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 17, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 17, '18', 'offline', 'co2', 71.79, '{"max": 50}', 'medium', 'Alert #17', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 18, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 18, '19', 'battery', 'temperature', 29.9, '{"max": 50}', 'high', 'Alert #18', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 19, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 19, '20', 'sensor_error', 'humidity', 91.43, '{"max": 50}', 'critical', 'Alert #19', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 20, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 20, '21', 'threshold', 'co2', 83.33, '{"max": 50}', 'info', 'Alert #20', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 21, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 21, '22', 'offline', 'temperature', 1.53, '{"max": 50}', 'low', 'Alert #21', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 22, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 22, '23', 'battery', 'humidity', 81.57, '{"max": 50}', 'medium', 'Alert #22', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 23, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 23, '24', 'sensor_error', 'co2', 13.39, '{"max": 50}', 'high', 'Alert #23', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 24, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 24, '25', 'threshold', 'temperature', 63.32, '{"max": 50}', 'critical', 'Alert #24', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 25, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 25, '26', 'offline', 'humidity', 46.07, '{"max": 50}', 'info', 'Alert #25', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 26, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 26, '27', 'battery', 'co2', 81.41, '{"max": 50}', 'low', 'Alert #26', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 27, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 27, '28', 'sensor_error', 'temperature', 76.87, '{"max": 50}', 'medium', 'Alert #27', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 28, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 28, '29', 'threshold', 'humidity', 45.25, '{"max": 50}', 'high', 'Alert #28', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 29, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 29, '30', 'offline', 'co2', 19.27, '{"max": 50}', 'critical', 'Alert #29', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 30, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 30, '31', 'battery', 'temperature', 52.57, '{"max": 50}', 'info', 'Alert #30', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 31, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 31, '32', 'sensor_error', 'humidity', 99.01, '{"max": 50}', 'low', 'Alert #31', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 32, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 32, '33', 'threshold', 'co2', 21.74, '{"max": 50}', 'medium', 'Alert #32', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 33, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 33, '34', 'offline', 'temperature', 84.52, '{"max": 50}', 'high', 'Alert #33', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 34, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 34, '35', 'battery', 'humidity', 3.48, '{"max": 50}', 'critical', 'Alert #34', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 35, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 35, '36', 'sensor_error', 'co2', 53.32, '{"max": 50}', 'info', 'Alert #35', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 36, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 36, '37', 'threshold', 'temperature', 48.68, '{"max": 50}', 'low', 'Alert #36', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 37, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 37, '38', 'offline', 'humidity', 44.97, '{"max": 50}', 'medium', 'Alert #37', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 38, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 38, '39', 'battery', 'co2', 34.16, '{"max": 50}', 'high', 'Alert #38', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 39, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 39, '40', 'sensor_error', 'temperature', 82.71, '{"max": 50}', 'critical', 'Alert #39', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 40, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 40, '41', 'threshold', 'humidity', 69.77, '{"max": 50}', 'info', 'Alert #40', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 41, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 41, '42', 'offline', 'co2', 16.22, '{"max": 50}', 'low', 'Alert #41', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 42, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 42, '43', 'battery', 'temperature', 23.6, '{"max": 50}', 'medium', 'Alert #42', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 43, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 43, '44', 'sensor_error', 'humidity', 86.86, '{"max": 50}', 'high', 'Alert #43', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 44, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 44, '45', 'threshold', 'co2', 91.64, '{"max": 50}', 'critical', 'Alert #44', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 45, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 45, '46', 'offline', 'temperature', 40.36, '{"max": 50}', 'info', 'Alert #45', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 46, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 46, '47', 'battery', 'humidity', 89.59, '{"max": 50}', 'low', 'Alert #46', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 47, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 47, '48', 'sensor_error', 'co2', 76.62, '{"max": 50}', 'medium', 'Alert #47', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 48, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 48, '49', 'threshold', 'temperature', 19.08, '{"max": 50}', 'high', 'Alert #48', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 49, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 49, '50', 'offline', 'humidity', 39.55, '{"max": 50}', 'critical', 'Alert #49', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 50, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 50, '51', 'battery', 'co2', 76.87, '{"max": 50}', 'info', 'Alert #50', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 51, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 51, '52', 'sensor_error', 'temperature', 55.19, '{"max": 50}', 'low', 'Alert #51', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 52, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 52, '53', 'threshold', 'humidity', 84.58, '{"max": 50}', 'medium', 'Alert #52', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 53, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 53, '54', 'offline', 'co2', 86.57, '{"max": 50}', 'high', 'Alert #53', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 54, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 54, '55', 'battery', 'temperature', 62.25, '{"max": 50}', 'critical', 'Alert #54', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 55, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 55, '56', 'sensor_error', 'humidity', 46.66, '{"max": 50}', 'info', 'Alert #55', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 56, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 56, '57', 'threshold', 'co2', 63.64, '{"max": 50}', 'low', 'Alert #56', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 57, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 57, '58', 'offline', 'temperature', 61.38, '{"max": 50}', 'medium', 'Alert #57', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 58, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 58, '59', 'battery', 'humidity', 44.87, '{"max": 50}', 'high', 'Alert #58', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 59, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 59, '60', 'sensor_error', 'co2', 47.92, '{"max": 50}', 'critical', 'Alert #59', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 60, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 60, '61', 'threshold', 'temperature', 91.8, '{"max": 50}', 'info', 'Alert #60', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 61, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 61, '62', 'offline', 'humidity', 74.9, '{"max": 50}', 'low', 'Alert #61', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 62, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 62, '63', 'battery', 'co2', 63.26, '{"max": 50}', 'medium', 'Alert #62', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 63, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 63, '64', 'sensor_error', 'temperature', 69.47, '{"max": 50}', 'high', 'Alert #63', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 64, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 64, '65', 'threshold', 'humidity', 70.2, '{"max": 50}', 'critical', 'Alert #64', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 65, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 65, '66', 'offline', 'co2', 96.53, '{"max": 50}', 'info', 'Alert #65', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 66, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 66, '67', 'battery', 'temperature', 74.58, '{"max": 50}', 'low', 'Alert #66', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 67, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 67, '68', 'sensor_error', 'humidity', 68.42, '{"max": 50}', 'medium', 'Alert #67', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 68, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 68, '69', 'threshold', 'co2', 53.57, '{"max": 50}', 'high', 'Alert #68', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 69, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 69, '70', 'offline', 'temperature', 88.34, '{"max": 50}', 'critical', 'Alert #69', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 70, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 70, '71', 'battery', 'humidity', 92.05, '{"max": 50}', 'info', 'Alert #70', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 71, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 71, '72', 'sensor_error', 'co2', 40.62, '{"max": 50}', 'low', 'Alert #71', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 72, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 72, '73', 'threshold', 'temperature', 65.77, '{"max": 50}', 'medium', 'Alert #72', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 73, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 73, '74', 'offline', 'humidity', 30.73, '{"max": 50}', 'high', 'Alert #73', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 74, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 74, '75', 'battery', 'co2', 93.49, '{"max": 50}', 'critical', 'Alert #74', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 75, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 75, '76', 'sensor_error', 'temperature', 30.21, '{"max": 50}', 'info', 'Alert #75', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 76, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 76, '77', 'threshold', 'humidity', 13.67, '{"max": 50}', 'low', 'Alert #76', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 77, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 77, '78', 'offline', 'co2', 82.29, '{"max": 50}', 'medium', 'Alert #77', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 78, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 78, '79', 'battery', 'temperature', 62.54, '{"max": 50}', 'high', 'Alert #78', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 79, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 79, '80', 'sensor_error', 'humidity', 10.72, '{"max": 50}', 'critical', 'Alert #79', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 80, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 80, '81', 'threshold', 'co2', 57.96, '{"max": 50}', 'info', 'Alert #80', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 81, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 81, '82', 'offline', 'temperature', 12.91, '{"max": 50}', 'low', 'Alert #81', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 82, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 82, '83', 'battery', 'humidity', 80.93, '{"max": 50}', 'medium', 'Alert #82', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 83, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 83, '84', 'sensor_error', 'co2', 40.42, '{"max": 50}', 'high', 'Alert #83', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 84, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 84, '85', 'threshold', 'temperature', 83.2, '{"max": 50}', 'critical', 'Alert #84', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 85, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 85, '86', 'offline', 'humidity', 47.95, '{"max": 50}', 'info', 'Alert #85', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 86, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 86, '87', 'battery', 'co2', 25.91, '{"max": 50}', 'low', 'Alert #86', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 87, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 87, '88', 'sensor_error', 'temperature', 43.14, '{"max": 50}', 'medium', 'Alert #87', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 88, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 88, '89', 'threshold', 'humidity', 5.05, '{"max": 50}', 'high', 'Alert #88', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 89, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 89, '90', 'offline', 'co2', 97.48, '{"max": 50}', 'critical', 'Alert #89', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 90, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 90, '91', 'battery', 'temperature', 42.7, '{"max": 50}', 'info', 'Alert #90', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 91, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 91, '92', 'sensor_error', 'humidity', 51.24, '{"max": 50}', 'low', 'Alert #91', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 92, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 92, '93', 'threshold', 'co2', 3.88, '{"max": 50}', 'medium', 'Alert #92', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 93, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 93, '94', 'offline', 'temperature', 99.84, '{"max": 50}', 'high', 'Alert #93', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 94, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 94, '95', 'battery', 'humidity', 83.79, '{"max": 50}', 'critical', 'Alert #94', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 95, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 95, '96', 'sensor_error', 'co2', 70.05, '{"max": 50}', 'info', 'Alert #95', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 96, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 96, '97', 'threshold', 'temperature', 23.04, '{"max": 50}', 'low', 'Alert #96', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 97, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 97, '98', 'offline', 'humidity', 52.54, '{"max": 50}', 'medium', 'Alert #97', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 98, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 98, '99', 'battery', 'co2', 97.22, '{"max": 50}', 'high', 'Alert #98', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 99, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 99, '100', 'sensor_error', 'temperature', 73.57, '{"max": 50}', 'critical', 'Alert #99', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 100, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 100, '101', 'threshold', 'humidity', 42.98, '{"max": 50}', 'info', 'Alert #100', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 101, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 101, '102', 'offline', 'co2', 18.72, '{"max": 50}', 'low', 'Alert #101', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 102, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 102, '103', 'battery', 'temperature', 90, '{"max": 50}', 'medium', 'Alert #102', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 103, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 103, '104', 'sensor_error', 'humidity', 16.42, '{"max": 50}', 'high', 'Alert #103', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 104, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 104, '105', 'threshold', 'co2', 9.71, '{"max": 50}', 'critical', 'Alert #104', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 105, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 105, '106', 'offline', 'temperature', 54.43, '{"max": 50}', 'info', 'Alert #105', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 106, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 106, '107', 'battery', 'humidity', 52.36, '{"max": 50}', 'low', 'Alert #106', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 107, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 107, '108', 'sensor_error', 'co2', 87.99, '{"max": 50}', 'medium', 'Alert #107', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 108, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 108, '109', 'threshold', 'temperature', 31.4, '{"max": 50}', 'high', 'Alert #108', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 109, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 109, '110', 'offline', 'humidity', 55.16, '{"max": 50}', 'critical', 'Alert #109', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 110, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 110, '111', 'battery', 'co2', 85.72, '{"max": 50}', 'info', 'Alert #110', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 111, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 111, '112', 'sensor_error', 'temperature', 41.64, '{"max": 50}', 'low', 'Alert #111', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 112, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 112, '113', 'threshold', 'humidity', 92.94, '{"max": 50}', 'medium', 'Alert #112', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 113, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 113, '114', 'offline', 'co2', 90.05, '{"max": 50}', 'high', 'Alert #113', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 114, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 114, '115', 'battery', 'temperature', 15.32, '{"max": 50}', 'critical', 'Alert #114', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 115, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 115, '116', 'sensor_error', 'humidity', 37.26, '{"max": 50}', 'info', 'Alert #115', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 116, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 116, '117', 'threshold', 'co2', 62.55, '{"max": 50}', 'low', 'Alert #116', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 117, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 117, '118', 'offline', 'temperature', 14.95, '{"max": 50}', 'medium', 'Alert #117', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 118, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 118, '119', 'battery', 'humidity', 38.78, '{"max": 50}', 'high', 'Alert #118', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 119, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 119, '120', 'sensor_error', 'co2', 87.24, '{"max": 50}', 'critical', 'Alert #119', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 120, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 120, '121', 'threshold', 'temperature', 42.77, '{"max": 50}', 'info', 'Alert #120', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 121, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 121, '122', 'offline', 'humidity', 79.95, '{"max": 50}', 'low', 'Alert #121', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 122, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 122, '123', 'battery', 'co2', 80.7, '{"max": 50}', 'medium', 'Alert #122', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 123, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 123, '124', 'sensor_error', 'temperature', 5.23, '{"max": 50}', 'high', 'Alert #123', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 124, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 124, '125', 'threshold', 'humidity', 8.41, '{"max": 50}', 'critical', 'Alert #124', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 125, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 125, '126', 'offline', 'co2', 99.1, '{"max": 50}', 'info', 'Alert #125', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 126, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 126, '127', 'battery', 'temperature', 75.36, '{"max": 50}', 'low', 'Alert #126', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 127, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 127, '128', 'sensor_error', 'humidity', 4.69, '{"max": 50}', 'medium', 'Alert #127', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 128, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 128, '129', 'threshold', 'co2', 73.99, '{"max": 50}', 'high', 'Alert #128', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 129, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 129, '130', 'offline', 'temperature', 73.51, '{"max": 50}', 'critical', 'Alert #129', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 130, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 130, '131', 'battery', 'humidity', 99.37, '{"max": 50}', 'info', 'Alert #130', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 131, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 131, '132', 'sensor_error', 'co2', 35.62, '{"max": 50}', 'low', 'Alert #131', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 132, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 132, '133', 'threshold', 'temperature', 42.1, '{"max": 50}', 'medium', 'Alert #132', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 133, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 133, '134', 'offline', 'humidity', 16.44, '{"max": 50}', 'high', 'Alert #133', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 134, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 134, '135', 'battery', 'co2', 21.32, '{"max": 50}', 'critical', 'Alert #134', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 135, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 135, '136', 'sensor_error', 'temperature', 45.39, '{"max": 50}', 'info', 'Alert #135', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 136, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 136, '137', 'threshold', 'humidity', 97.57, '{"max": 50}', 'low', 'Alert #136', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 137, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 137, '138', 'offline', 'co2', 34.5, '{"max": 50}', 'medium', 'Alert #137', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 138, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 138, '139', 'battery', 'temperature', 78.19, '{"max": 50}', 'high', 'Alert #138', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 139, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 139, '140', 'sensor_error', 'humidity', 39.67, '{"max": 50}', 'critical', 'Alert #139', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 140, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 140, '141', 'threshold', 'co2', 72.1, '{"max": 50}', 'info', 'Alert #140', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 141, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 141, '142', 'offline', 'temperature', 40.04, '{"max": 50}', 'low', 'Alert #141', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 142, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 142, '143', 'battery', 'humidity', 77.13, '{"max": 50}', 'medium', 'Alert #142', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 143, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 143, '144', 'sensor_error', 'co2', 66.86, '{"max": 50}', 'high', 'Alert #143', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 144, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 144, '145', 'threshold', 'temperature', 0.15, '{"max": 50}', 'critical', 'Alert #144', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 145, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 145, '146', 'offline', 'humidity', 52.47, '{"max": 50}', 'info', 'Alert #145', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 146, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 146, '147', 'battery', 'co2', 80.7, '{"max": 50}', 'low', 'Alert #146', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 147, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 147, '148', 'sensor_error', 'temperature', 36.97, '{"max": 50}', 'medium', 'Alert #147', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 148, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 148, '149', 'threshold', 'humidity', 64.45, '{"max": 50}', 'high', 'Alert #148', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 149, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 149, '150', 'offline', 'co2', 16.99, '{"max": 50}', 'critical', 'Alert #149', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 150, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 150, '151', 'battery', 'temperature', 39.19, '{"max": 50}', 'info', 'Alert #150', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 151, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 151, '152', 'sensor_error', 'humidity', 9.34, '{"max": 50}', 'low', 'Alert #151', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 152, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 152, '153', 'threshold', 'co2', 22.19, '{"max": 50}', 'medium', 'Alert #152', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 153, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 153, '154', 'offline', 'temperature', 22.43, '{"max": 50}', 'high', 'Alert #153', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 154, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 154, '155', 'battery', 'humidity', 97.51, '{"max": 50}', 'critical', 'Alert #154', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 155, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 155, '156', 'sensor_error', 'co2', 72.2, '{"max": 50}', 'info', 'Alert #155', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 156, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 156, '157', 'threshold', 'temperature', 62.17, '{"max": 50}', 'low', 'Alert #156', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 157, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 157, '158', 'offline', 'humidity', 86.81, '{"max": 50}', 'medium', 'Alert #157', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 158, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 158, '159', 'battery', 'co2', 84.35, '{"max": 50}', 'high', 'Alert #158', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 159, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 159, '160', 'sensor_error', 'temperature', 20.37, '{"max": 50}', 'critical', 'Alert #159', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 160, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 160, '161', 'threshold', 'humidity', 68.74, '{"max": 50}', 'info', 'Alert #160', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 161, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 161, '162', 'offline', 'co2', 19.45, '{"max": 50}', 'low', 'Alert #161', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 162, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 162, '163', 'battery', 'temperature', 1.57, '{"max": 50}', 'medium', 'Alert #162', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 163, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 163, '164', 'sensor_error', 'humidity', 3.4, '{"max": 50}', 'high', 'Alert #163', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 164, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 164, '165', 'threshold', 'co2', 90.78, '{"max": 50}', 'critical', 'Alert #164', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 165, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 165, '166', 'offline', 'temperature', 18.31, '{"max": 50}', 'info', 'Alert #165', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 166, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 166, '167', 'battery', 'humidity', 23.23, '{"max": 50}', 'low', 'Alert #166', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 167, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 167, '168', 'sensor_error', 'co2', 28.96, '{"max": 50}', 'medium', 'Alert #167', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 168, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 168, '169', 'threshold', 'temperature', 10.62, '{"max": 50}', 'high', 'Alert #168', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 169, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 169, '170', 'offline', 'humidity', 34.12, '{"max": 50}', 'critical', 'Alert #169', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 170, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 170, '171', 'battery', 'co2', 16.47, '{"max": 50}', 'info', 'Alert #170', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 171, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 171, '172', 'sensor_error', 'temperature', 46.81, '{"max": 50}', 'low', 'Alert #171', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 172, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 172, '173', 'threshold', 'humidity', 90.07, '{"max": 50}', 'medium', 'Alert #172', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 173, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 173, '174', 'offline', 'co2', 51.04, '{"max": 50}', 'high', 'Alert #173', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 174, '2026-10-23 07:50:24.751134+00', 10, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 174, '175', 'battery', 'temperature', 52.63, '{"max": 50}', 'critical', 'Alert #174', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 175, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 175, '176', 'sensor_error', 'humidity', 98.74, '{"max": 50}', 'info', 'Alert #175', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 176, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 176, '177', 'threshold', 'co2', 25.92, '{"max": 50}', 'low', 'Alert #176', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 177, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 177, '178', 'offline', 'temperature', 40.13, '{"max": 50}', 'medium', 'Alert #177', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 178, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 178, '179', 'battery', 'humidity', 63.41, '{"max": 50}', 'high', 'Alert #178', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 179, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 179, '180', 'sensor_error', 'co2', 26.7, '{"max": 50}', 'critical', 'Alert #179', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 180, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 180, '181', 'threshold', 'temperature', 48.93, '{"max": 50}', 'info', 'Alert #180', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 181, '2026-10-23 07:50:24.751134+00', 8, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 181, '182', 'offline', 'humidity', 70.05, '{"max": 50}', 'low', 'Alert #181', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 182, '2026-10-23 07:50:24.751134+00', 4, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 182, '183', 'battery', 'co2', 46.44, '{"max": 50}', 'medium', 'Alert #182', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 183, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 183, '184', 'sensor_error', 'temperature', 93.89, '{"max": 50}', 'high', 'Alert #183', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 184, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 184, '185', 'threshold', 'humidity', 25.64, '{"max": 50}', 'critical', 'Alert #184', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 185, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 185, '186', 'offline', 'co2', 68.78, '{"max": 50}', 'info', 'Alert #185', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 186, '2026-10-23 07:50:24.751134+00', 2, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 186, '187', 'battery', 'temperature', 57.28, '{"max": 50}', 'low', 'Alert #186', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 187, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 187, '188', 'sensor_error', 'humidity', 59.94, '{"max": 50}', 'medium', 'Alert #187', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 188, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 188, '189', 'threshold', 'co2', 80.18, '{"max": 50}', 'high', 'Alert #188', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 189, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 189, '190', 'offline', 'temperature', 37.84, '{"max": 50}', 'critical', 'Alert #189', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 190, '2026-10-23 07:50:24.751134+00', 1, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 190, '191', 'battery', 'humidity', 17.9, '{"max": 50}', 'info', 'Alert #190', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 191, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 191, '192', 'sensor_error', 'co2', 75.03, '{"max": 50}', 'low', 'Alert #191', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 192, '2026-10-23 07:50:24.751134+00', 5, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 192, '193', 'threshold', 'temperature', 40.53, '{"max": 50}', 'medium', 'Alert #192', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 193, '2026-10-23 07:50:24.751134+00', 0, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 193, '194', 'offline', 'humidity', 62.58, '{"max": 50}', 'high', 'Alert #193', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 194, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 194, '195', 'battery', 'co2', 58.69, '{"max": 50}', 'critical', 'Alert #194', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 195, '2026-10-23 07:50:24.751134+00', 9, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 195, '196', 'sensor_error', 'temperature', 78.86, '{"max": 50}', 'info', 'Alert #195', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 196, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 196, '197', 'threshold', 'humidity', 91.27, '{"max": 50}', 'low', 'Alert #196', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 197, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 197, '198', 'offline', 'co2', 6.17, '{"max": 50}', 'medium', 'Alert #197', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 198, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 198, '199', 'battery', 'temperature', 95.76, '{"max": 50}', 'high', 'Alert #198', '{"source": "sensor"}', 't', NULL, NULL, NULL, 'f', NULL, NULL, NULL, 199, '2026-10-23 07:50:24.751134+00', 3, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 199, '200', 'sensor_error', 'humidity', 92.33, '{"max": 50}', 'critical', 'Alert #199', '{"source": "sensor"}', 't', NULL, NULL, NULL, 't', NULL, NULL, NULL, 200, '2026-10-23 07:50:24.751134+00', 7, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');
INSERT INTO "public"."device_alert" VALUES ('11111111-1111-1111-1111-111111111111', 200, '1', 'threshold', 'co2', 86.5, '{"max": 50}', 'info', 'Alert #200', '{"source": "sensor"}', 'f', NULL, NULL, NULL, 't', NULL, NULL, NULL, 1, '2026-10-23 07:50:24.751134+00', 6, '2026-09-23 07:50:24.751134+00', '2026-09-23 07:50:24.751134+00');

-- ----------------------------
-- Table structure for device_config
-- ----------------------------
DROP TABLE IF EXISTS "public"."device_config";
CREATE TABLE "public"."device_config" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('device_config_id_seq'::regclass),
  "deviceId" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "config" jsonb,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "notes" text COLLATE "pg_catalog"."default",
  "updatedBy" varchar(100) COLLATE "pg_catalog"."default",
  "lastAppliedAt" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of device_config
-- ----------------------------
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 1, '1', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 1"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 1', 'system', '2026-08-24 17:10:13.257477+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 2, '2', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 2"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 2', 'system', '2026-09-08 17:15:57.823214+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 3, '3', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 3"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 3', 'system', '2026-09-10 00:42:58.497161+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 4, '4', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 4"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 4', 'system', '2026-09-22 08:04:13.022955+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 5, '5', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 5"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 5', 'system', '2026-08-26 18:04:05.318898+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 6, '6', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 6"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 6', 'system', '2026-09-22 09:48:26.751828+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 7, '7', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 7"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 7', 'system', '2026-09-19 08:12:15.720154+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 8, '8', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 8"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 8', 'system', '2026-08-25 08:41:50.649462+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 9, '9', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 9"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 9', 'system', '2026-09-02 23:25:54.637671+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 10, '10', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 10"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 10', 'system', '2026-08-28 22:23:17.195487+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 11, '11', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 11"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 11', 'system', '2026-09-01 06:56:05.520674+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 12, '12', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 12"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 12', 'system', '2026-09-04 11:43:26.722715+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 13, '13', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 13"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 13', 'system', '2026-08-24 16:16:38.28701+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 14, '14', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 14"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 14', 'system', '2026-09-06 02:41:21.132996+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 15, '15', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 15"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 15', 'system', '2026-08-27 21:50:37.649187+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 16, '16', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 16"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 16', 'system', '2026-09-01 10:59:21.848121+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 17, '17', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 17"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 17', 'system', '2026-09-16 03:19:48.334615+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 18, '18', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 18"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 18', 'system', '2026-09-18 15:01:14.30997+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 19, '19', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 19"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 19', 'system', '2026-09-21 18:20:20.260431+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 20, '20', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 20"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 20', 'system', '2026-08-27 00:50:32.985419+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 21, '21', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 21"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 21', 'system', '2026-09-20 16:42:24.83565+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 22, '22', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 22"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 22', 'system', '2026-09-14 22:54:51.859825+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 23, '23', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 23"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 23', 'system', '2026-08-31 19:42:12.24087+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 24, '24', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 24"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 24', 'system', '2026-09-04 17:40:59.795063+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 25, '25', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 25"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 25', 'system', '2026-09-04 21:00:07.604478+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 26, '26', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 26"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 26', 'system', '2026-09-11 09:33:23.40881+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 27, '27', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 27"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 27', 'system', '2026-09-19 00:53:07.408399+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 28, '28', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 28"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 28', 'system', '2026-09-11 16:35:43.018547+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 29, '29', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 29"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 29', 'system', '2026-08-26 09:55:19.90949+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 30, '30', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 30"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 30', 'system', '2026-09-21 08:32:42.564489+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 31, '31', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 31"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 31', 'system', '2026-09-16 17:53:41.711748+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 32, '32', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 32"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 32', 'system', '2026-09-20 19:28:01.788122+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 33, '33', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 33"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 33', 'system', '2026-09-20 06:12:36.715152+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 34, '34', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 34"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 34', 'system', '2026-08-29 08:36:10.570271+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 35, '35', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 35"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 35', 'system', '2026-08-31 03:57:17.917127+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 36, '36', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 36"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 36', 'system', '2026-09-02 12:12:39.894442+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 37, '37', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 37"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 37', 'system', '2026-08-27 19:13:55.288509+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 38, '38', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 38"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 38', 'system', '2026-09-01 07:37:29.936424+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 39, '39', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 39"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 39', 'system', '2026-09-06 02:32:29.064516+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 40, '40', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 40"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 40', 'system', '2026-09-11 20:00:43.646372+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 41, '41', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 41"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 41', 'system', '2026-09-21 05:12:10.597587+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 42, '42', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 42"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 42', 'system', '2026-09-07 04:28:47.403584+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 43, '43', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 43"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 43', 'system', '2026-09-09 09:21:49.81165+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 44, '44', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 44"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 44', 'system', '2026-09-07 20:17:56.263788+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 45, '45', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 45"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 45', 'system', '2026-08-27 23:53:24.075557+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 46, '46', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 46"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 46', 'system', '2026-09-18 09:47:05.767585+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 47, '47', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 47"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 47', 'system', '2026-08-29 17:13:03.133886+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 48, '48', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 48"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 48', 'system', '2026-09-09 14:25:11.384752+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 49, '49', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 49"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 49', 'system', '2026-09-15 10:12:47.427569+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 50, '50', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 50"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 50', 'system', '2026-08-27 04:59:01.133703+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 51, '51', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 51"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 51', 'system', '2026-08-29 16:35:34.6931+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 52, '52', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 52"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 52', 'system', '2026-08-29 03:59:56.434432+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 53, '53', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 53"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 53', 'system', '2026-08-28 12:00:58.516052+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 54, '54', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 54"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 54', 'system', '2026-08-24 14:59:08.965914+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 55, '55', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 55"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 55', 'system', '2026-09-16 11:46:04.13972+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 56, '56', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 56"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 56', 'system', '2026-08-28 11:30:09.12319+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 57, '57', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 57"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 57', 'system', '2026-09-11 08:03:58.093746+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 58, '58', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 58"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 58', 'system', '2026-09-16 10:44:31.711418+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 59, '59', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 59"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 59', 'system', '2026-08-31 20:07:47.764778+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 60, '60', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 60"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 60', 'system', '2026-08-26 09:28:31.214965+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 61, '61', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 61"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 61', 'system', '2026-08-25 14:17:00.633595+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 62, '62', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 62"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 62', 'system', '2026-09-12 22:40:03.662963+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 63, '63', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 63"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 63', 'system', '2026-08-25 06:32:50.730524+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 64, '64', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 64"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 64', 'system', '2026-08-24 08:43:08.040943+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 65, '65', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 65"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 65', 'system', '2026-08-30 17:37:00.733654+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 66, '66', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 66"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 66', 'system', '2026-09-22 09:31:09.911587+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 67, '67', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 67"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 67', 'system', '2026-09-04 11:19:40.070914+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 68, '68', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 68"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 68', 'system', '2026-08-24 10:10:27.610118+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 69, '69', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 69"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 69', 'system', '2026-08-28 16:45:59.732577+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 70, '70', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 70"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 70', 'system', '2026-09-21 06:18:40.70767+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 71, '71', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 71"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 71', 'system', '2026-09-21 17:02:37.909491+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 72, '72', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 72"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 72', 'system', '2026-09-14 19:30:23.858927+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 73, '73', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 73"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 73', 'system', '2026-09-07 02:03:20.813149+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 74, '74', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 74"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 74', 'system', '2026-08-25 20:01:09.516507+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 75, '75', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 75"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 75', 'system', '2026-09-09 02:06:10.224499+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 76, '76', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 76"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 76', 'system', '2026-08-25 08:23:09.592939+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 77, '77', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 77"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 77', 'system', '2026-08-25 04:34:53.589977+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 78, '78', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 78"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 78', 'system', '2026-09-18 18:41:17.694469+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 79, '79', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 79"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 79', 'system', '2026-08-27 13:51:16.310755+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 80, '80', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 80"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 80', 'system', '2026-09-18 11:47:10.914357+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 81, '81', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 81"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 81', 'system', '2026-09-08 08:56:00.332744+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 82, '82', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 82"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 82', 'system', '2026-09-20 10:31:09.468562+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 83, '83', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 83"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 83', 'system', '2026-09-02 23:52:59.680538+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 84, '84', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 84"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 84', 'system', '2026-09-11 13:01:10.371061+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 85, '85', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 85"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 85', 'system', '2026-09-17 17:42:15.325262+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 86, '86', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 86"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 86', 'system', '2026-09-04 20:47:18.835155+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 87, '87', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 87"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 87', 'system', '2026-08-28 22:43:09.581081+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 88, '88', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 88"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 88', 'system', '2026-09-17 07:54:11.838912+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 89, '89', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 89"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 89', 'system', '2026-09-16 04:48:38.289977+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 90, '90', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 90"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 90', 'system', '2026-09-11 13:29:00.521589+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 91, '91', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 91"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 91', 'system', '2026-09-08 23:31:09.362379+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 92, '92', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 92"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 92', 'system', '2026-08-30 23:56:55.480073+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 93, '93', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 93"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 93', 'system', '2026-08-24 15:02:58.921136+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 94, '94', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 94"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 94', 'system', '2026-08-29 03:03:10.40388+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 95, '95', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 95"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 95', 'system', '2026-09-03 19:02:03.764387+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 96, '96', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 96"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 96', 'system', '2026-09-05 09:41:07.083301+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 97, '97', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 97"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 97', 'system', '2026-09-03 22:59:22.876396+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 98, '98', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 98"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 98', 'system', '2026-09-19 14:50:58.965578+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 99, '99', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 99"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 99', 'system', '2026-09-18 04:50:46.493428+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 100, '100', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 100"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 100', 'system', '2026-09-18 05:21:58.472807+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 101, '101', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 101"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 101', 'system', '2026-09-04 00:21:07.490868+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 102, '102', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 102"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 102', 'system', '2026-08-31 05:01:05.160981+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 103, '103', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 103"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 103', 'system', '2026-08-26 19:29:29.402154+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 104, '104', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 104"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 104', 'system', '2026-09-07 05:58:04.704913+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 105, '105', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 105"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 105', 'system', '2026-09-23 03:49:41.684246+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 106, '106', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 106"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 106', 'system', '2026-09-21 03:06:13.398922+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 107, '107', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 107"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 107', 'system', '2026-09-13 03:31:36.56395+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 108, '108', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 108"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 108', 'system', '2026-09-22 18:44:02.795049+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 109, '109', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 109"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 109', 'system', '2026-08-30 05:32:00.532756+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 110, '110', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 110"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 110', 'system', '2026-08-24 09:36:45.581547+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 111, '111', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 111"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 111', 'system', '2026-09-05 11:11:20.902443+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 112, '112', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 112"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 112', 'system', '2026-08-25 12:14:52.60938+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 113, '113', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 113"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 113', 'system', '2026-09-04 16:37:27.074936+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 114, '114', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 114"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 114', 'system', '2026-09-12 02:06:23.80748+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 115, '115', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 115"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 115', 'system', '2026-09-12 03:09:44.80794+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 116, '116', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 116"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 116', 'system', '2026-09-17 10:12:17.317211+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 117, '117', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 117"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 117', 'system', '2026-09-17 07:55:18.588089+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 118, '118', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 118"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 118', 'system', '2026-09-10 09:58:09.551142+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 119, '119', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 119"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 119', 'system', '2026-08-29 11:33:38.625132+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 120, '120', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 120"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 120', 'system', '2026-08-30 10:25:12.488529+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 121, '121', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 121"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 121', 'system', '2026-09-20 07:14:57.469546+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 122, '122', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 122"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 122', 'system', '2026-09-12 22:41:00.360872+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 123, '123', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 123"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 123', 'system', '2026-09-19 05:25:00.626694+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 124, '124', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 124"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 124', 'system', '2026-08-26 05:36:35.818043+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 125, '125', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 125"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 125', 'system', '2026-09-16 23:01:02.400918+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 126, '126', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 126"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 126', 'system', '2026-08-31 05:01:26.070574+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 127, '127', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 127"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 127', 'system', '2026-09-16 05:52:21.531081+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 128, '128', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 128"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 128', 'system', '2026-08-30 07:10:07.356187+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 129, '129', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 129"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 129', 'system', '2026-08-31 08:09:18.231865+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 130, '130', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 130"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 130', 'system', '2026-08-31 04:46:50.62485+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 131, '131', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 131"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 131', 'system', '2026-08-24 19:26:19.583902+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 132, '132', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 132"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 132', 'system', '2026-09-14 03:44:06.596009+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 133, '133', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 133"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 133', 'system', '2026-08-25 05:15:05.055855+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 134, '134', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 134"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 134', 'system', '2026-09-18 09:05:12.770468+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 135, '135', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 135"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 135', 'system', '2026-09-17 11:38:15.695105+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 136, '136', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 136"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 136', 'system', '2026-09-16 04:30:04.44235+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 137, '137', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 137"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 137', 'system', '2026-08-24 09:10:30.302915+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 138, '138', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 138"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 138', 'system', '2026-09-17 20:26:56.71194+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 139, '139', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 139"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 139', 'system', '2026-09-16 01:04:01.624526+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 140, '140', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 140"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 140', 'system', '2026-09-12 22:17:47.229869+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 141, '141', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 141"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 141', 'system', '2026-08-30 03:38:43.82298+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 142, '142', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 142"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 142', 'system', '2026-09-05 15:34:45.606347+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 143, '143', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 143"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 143', 'system', '2026-09-02 06:16:13.88244+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 144, '144', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 144"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 144', 'system', '2026-09-11 06:45:35.380594+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 145, '145', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 145"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 145', 'system', '2026-09-21 20:15:21.351983+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 146, '146', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 146"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 146', 'system', '2026-09-08 11:44:49.510274+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 147, '147', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 147"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 147', 'system', '2026-09-16 16:39:56.937299+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 148, '148', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 148"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 148', 'system', '2026-09-01 07:05:12.233956+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 149, '149', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 149"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 149', 'system', '2026-09-13 03:56:55.971495+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 150, '150', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 150"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 150', 'system', '2026-09-11 07:26:10.979805+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 151, '151', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 151"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 151', 'system', '2026-09-04 15:15:33.887737+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 152, '152', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 152"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 152', 'system', '2026-08-24 20:07:34.019308+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 153, '153', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 153"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 153', 'system', '2026-09-18 23:39:59.37211+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 154, '154', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 154"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 154', 'system', '2026-09-09 19:03:17.985434+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 155, '155', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 155"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 155', 'system', '2026-09-10 08:40:36.193832+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 156, '156', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 156"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 156', 'system', '2026-09-02 10:57:17.804768+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 157, '157', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 157"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 157', 'system', '2026-08-29 23:23:42.522353+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 158, '158', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 158"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 158', 'system', '2026-09-03 05:15:42.308641+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 159, '159', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 159"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 159', 'system', '2026-09-19 02:05:28.262473+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 160, '160', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 160"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 160', 'system', '2026-09-15 14:32:49.664085+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 161, '161', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 161"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 161', 'system', '2026-09-22 06:37:05.199622+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 162, '162', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 162"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 162', 'system', '2026-08-25 10:11:26.164332+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 163, '163', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 163"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 163', 'system', '2026-09-17 23:35:35.879734+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 164, '164', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 164"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 164', 'system', '2026-08-26 21:59:11.922095+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 165, '165', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 165"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 165', 'system', '2026-08-31 14:37:03.539857+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 166, '166', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 166"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 166', 'system', '2026-08-29 06:59:26.281365+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 167, '167', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 167"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 167', 'system', '2026-09-12 22:43:16.481723+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 168, '168', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 168"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 168', 'system', '2026-09-10 20:14:42.644743+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 169, '169', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 169"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 169', 'system', '2026-09-10 05:47:36.118825+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 170, '170', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 170"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 170', 'system', '2026-09-14 19:53:43.917669+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 171, '171', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 171"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 171', 'system', '2026-09-13 01:38:10.405297+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 172, '172', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 172"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 172', 'system', '2026-08-24 19:59:06.766205+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 173, '173', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 173"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 173', 'system', '2026-09-16 03:35:02.281259+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 174, '174', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 174"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 174', 'system', '2026-08-27 02:30:07.307152+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 175, '175', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 175"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 175', 'system', '2026-08-29 13:41:17.066277+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 176, '176', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 176"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 176', 'system', '2026-09-08 04:45:57.943151+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 177, '177', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 177"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 177', 'system', '2026-09-07 02:33:40.910047+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 178, '178', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 178"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 178', 'system', '2026-08-26 08:41:12.960337+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 179, '179', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 179"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 179', 'system', '2026-09-07 17:35:55.630377+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 180, '180', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 180"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 180', 'system', '2026-09-13 20:41:32.771137+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 181, '181', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 181"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 181', 'system', '2026-09-22 10:43:13.227925+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 182, '182', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 182"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 182', 'system', '2026-08-28 05:50:10.369052+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 183, '183', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 183"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 183', 'system', '2026-08-24 21:08:59.289105+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 184, '184', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 184"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 184', 'system', '2026-09-07 05:36:52.687479+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 185, '185', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 185"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 185', 'system', '2026-08-29 07:43:58.925737+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 186, '186', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 186"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 186', 'system', '2026-09-18 04:53:03.065954+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 187, '187', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 187"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 187', 'system', '2026-09-02 08:42:59.998268+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 188, '188', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 188"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 188', 'system', '2026-09-18 16:05:22.734537+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 189, '189', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 189"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 189', 'system', '2026-09-14 00:36:50.130519+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 190, '190', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 190"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 190', 'system', '2026-09-19 16:15:35.890066+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 191, '191', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 191"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 191', 'system', '2026-09-20 09:14:38.362081+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 192, '192', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 192"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 192', 'system', '2026-09-10 14:54:04.4336+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 193, '193', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 193"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 193', 'system', '2026-09-17 09:04:56.187375+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 194, '194', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 194"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 194', 'system', '2026-09-18 03:38:45.069422+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 195, '195', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 195"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 195', 'system', '2026-09-14 06:42:28.694536+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 196, '196', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 196"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 196', 'system', '2026-09-19 04:06:12.253909+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 197, '197', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 197"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 197', 'system', '2026-09-13 13:15:03.722609+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 198, '198', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 198"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 198', 'system', '2026-09-22 02:20:26.281476+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 199, '199', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 199"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 199', 'system', '2026-09-12 14:59:40.223143+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');
INSERT INTO "public"."device_config" VALUES ('11111111-1111-1111-1111-111111111111', 200, '200', '{"general": {"timezone": "Asia/Bangkok", "deviceName": "Device 200"}, "reporting": {"enabled": true, "interval": 300}}', 'active', 'Config 200', 'system', '2026-09-22 00:39:14.348085+00', '2026-09-23 07:50:24.74108+00', '2026-09-23 07:50:24.74108+00');

-- ----------------------------
-- Table structure for device_status
-- ----------------------------
DROP TABLE IF EXISTS "public"."device_status";
CREATE TABLE "public"."device_status" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('device_status_id_seq'::regclass),
  "deviceId" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "isOnline" bool NOT NULL,
  "isActive" bool NOT NULL,
  "lastSeen" timestamptz(6) NOT NULL,
  "lastData" jsonb,
  "batteryLevel" int4,
  "signalStrength" int4,
  "temperature" float8,
  "humidity" float8,
  "firmwareVersion" varchar(20) COLLATE "pg_catalog"."default",
  "uptime" int4,
  "location" jsonb,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of device_status
-- ----------------------------
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 8, '8', 'f', 't', '2026-09-20 15:06:42.652886+00', '{"hum": 60, "temp": 25.5}', 37, -53, 42.02, 75.48, 'v1.0.3', 1733690, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 12, '12', 'f', 't', '2026-09-16 17:49:52.641649+00', '{"hum": 60, "temp": 25.5}', 87, -58, 27.25, 66.78, 'v1.0.2', 2314034, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 19, '19', 'f', 't', '2026-09-20 12:03:29.475629+00', '{"hum": 60, "temp": 25.5}', 65, -72, 19.33, 57.38, 'v1.0.4', 1514914, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 21, '21', 'f', 't', '2026-09-18 23:09:24.557731+00', '{"hum": 60, "temp": 25.5}', 59, -56, 34.73, 43.97, 'v1.0.1', 2144872, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 23, '23', 'f', 't', '2026-09-16 19:37:40.589501+00', '{"hum": 60, "temp": 25.5}', 88, -80, 37.21, 37.84, 'v1.0.3', 2455474, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 24, '24', 'f', 't', '2026-09-22 11:28:14.232294+00', '{"hum": 60, "temp": 25.5}', 42, -57, 34.78, 61.67, 'v1.0.4', 2086297, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 32, '32', 'f', 't', '2026-09-22 14:19:23.03139+00', '{"hum": 60, "temp": 25.5}', 86, -79, 42.03, 61.71, 'v1.0.2', 2107264, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 34, '34', 'f', 't', '2026-09-17 20:17:42.414341+00', '{"hum": 60, "temp": 25.5}', 68, -65, 21.41, 48.53, 'v1.0.4', 637303, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 41, '41', 'f', 't', '2026-09-16 22:18:12.67686+00', '{"hum": 60, "temp": 25.5}', 91, -41, 24.81, 37.3, 'v1.0.1', 70350, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 43, '43', 'f', 't', '2026-09-19 13:12:34.411895+00', '{"hum": 60, "temp": 25.5}', 52, -41, 28.67, 53.22, 'v1.0.3', 1975776, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 45, '45', 'f', 't', '2026-09-19 17:20:35.401328+00', '{"hum": 60, "temp": 25.5}', 91, -62, 29.07, 74.09, 'v1.0.0', 1149046, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 46, '46', 'f', 't', '2026-09-18 13:51:22.488322+00', '{"hum": 60, "temp": 25.5}', 72, -67, 34.51, 81.58, 'v1.0.1', 1330456, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 48, '48', 'f', 't', '2026-09-21 17:35:41.42272+00', '{"hum": 60, "temp": 25.5}', 33, -56, 35.2, 50.52, 'v1.0.3', 599275, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 54, '54', 'f', 't', '2026-09-17 03:45:59.710783+00', '{"hum": 60, "temp": 25.5}', 24, -53, 32.08, 76.18, 'v1.0.4', 2533440, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 56, '56', 'f', 't', '2026-09-20 01:43:05.127825+00', '{"hum": 60, "temp": 25.5}', 70, -64, 30.94, 69.02, 'v1.0.1', 2392625, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 57, '57', 'f', 't', '2026-09-19 13:41:27.188073+00', '{"hum": 60, "temp": 25.5}', 98, -65, 30.31, 85.27, 'v1.0.2', 237259, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 59, '59', 'f', 't', '2026-09-17 10:39:21.039588+00', '{"hum": 60, "temp": 25.5}', 25, -76, 32.24, 40.64, 'v1.0.4', 1220400, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 62, '62', 'f', 't', '2026-09-16 14:03:56.260067+00', '{"hum": 60, "temp": 25.5}', 90, -68, 20.03, 65.82, 'v1.0.2', 1497548, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 63, '63', 'f', 't', '2026-09-16 21:17:21.44012+00', '{"hum": 60, "temp": 25.5}', 47, -73, 32.16, 86.17, 'v1.0.3', 2523070, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 64, '64', 'f', 't', '2026-09-21 10:53:04.512926+00', '{"hum": 60, "temp": 25.5}', 60, -55, 30.25, 85.93, 'v1.0.4', 1023062, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 70, '70', 'f', 't', '2026-09-22 18:48:54.011668+00', '{"hum": 60, "temp": 25.5}', 31, -61, 32.48, 69.7, 'v1.0.0', 472828, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 75, '75', 'f', 't', '2026-09-17 04:45:42.707075+00', '{"hum": 60, "temp": 25.5}', 64, -69, 38.95, 65.35, 'v1.0.0', 2229456, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 76, '76', 'f', 't', '2026-09-19 04:08:00.357946+00', '{"hum": 60, "temp": 25.5}', 79, -59, 19.78, 87.33, 'v1.0.1', 2528572, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 77, '77', 'f', 't', '2026-09-19 15:24:59.57348+00', '{"hum": 60, "temp": 25.5}', 90, -73, 27.44, 78.29, 'v1.0.2', 2342895, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 78, '78', 'f', 't', '2026-09-21 16:54:01.038216+00', '{"hum": 60, "temp": 25.5}', 65, -77, 33.67, 67.9, 'v1.0.3', 508730, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 83, '83', 'f', 't', '2026-09-18 17:00:14.446631+00', '{"hum": 60, "temp": 25.5}', 69, -58, 17.37, 80.39, 'v1.0.3', 1241259, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 84, '84', 'f', 't', '2026-09-16 22:55:56.866178+00', '{"hum": 60, "temp": 25.5}', 37, -78, 34.2, 51.52, 'v1.0.4', 1787845, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 92, '92', 'f', 't', '2026-09-23 06:58:00.832074+00', '{"hum": 60, "temp": 25.5}', 31, -43, 32.81, 48.25, 'v1.0.2', 1626970, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 95, '95', 'f', 't', '2026-09-18 21:55:36.891818+00', '{"hum": 60, "temp": 25.5}', 76, -63, 34.2, 72.94, 'v1.0.0', 1532210, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 96, '96', 'f', 't', '2026-09-16 12:12:57.087756+00', '{"hum": 60, "temp": 25.5}', 67, -57, 34.22, 31.34, 'v1.0.1', 1946195, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 100, '100', 'f', 't', '2026-09-22 15:13:40.955626+00', '{"hum": 60, "temp": 25.5}', 27, -59, 15.61, 81.58, 'v1.0.0', 893248, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 104, '104', 'f', 't', '2026-09-21 20:10:05.868063+00', '{"hum": 60, "temp": 25.5}', 55, -64, 18.62, 69.57, 'v1.0.4', 2235806, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 105, '105', 'f', 't', '2026-09-20 08:06:13.066268+00', '{"hum": 60, "temp": 25.5}', 67, -73, 22.13, 52.81, 'v1.0.0', 408148, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 106, '106', 'f', 't', '2026-09-21 18:01:10.413194+00', '{"hum": 60, "temp": 25.5}', 62, -59, 43.65, 77.67, 'v1.0.1', 610569, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 120, '120', 'f', 't', '2026-09-17 16:11:31.182448+00', '{"hum": 60, "temp": 25.5}', 56, -75, 40.38, 52.29, 'v1.0.0', 1198514, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 127, '127', 'f', 't', '2026-09-23 07:40:57.401262+00', '{"hum": 60, "temp": 25.5}', 36, -66, 37.19, 47.3, 'v1.0.2', 1588030, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 130, '130', 'f', 't', '2026-09-21 06:51:54.95244+00', '{"hum": 60, "temp": 25.5}', 73, -64, 23.17, 47.1, 'v1.0.0', 1639059, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 131, '131', 'f', 't', '2026-09-22 22:24:10.790502+00', '{"hum": 60, "temp": 25.5}', 53, -74, 18.21, 68.57, 'v1.0.1', 2557949, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 137, '137', 'f', 't', '2026-09-22 00:20:59.732708+00', '{"hum": 60, "temp": 25.5}', 33, -67, 20.93, 84.35, 'v1.0.2', 1138286, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 138, '138', 'f', 't', '2026-09-21 12:13:40.665264+00', '{"hum": 60, "temp": 25.5}', 79, -72, 31.32, 62.29, 'v1.0.3', 2215035, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 142, '142', 'f', 't', '2026-09-23 05:17:57.314136+00', '{"hum": 60, "temp": 25.5}', 95, -80, 23.71, 50.95, 'v1.0.2', 1671712, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 144, '144', 'f', 't', '2026-09-17 06:48:47.611429+00', '{"hum": 60, "temp": 25.5}', 25, -70, 16.93, 32.02, 'v1.0.4', 528694, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 147, '147', 'f', 't', '2026-09-17 21:08:10.816417+00', '{"hum": 60, "temp": 25.5}', 33, -67, 21.38, 50.06, 'v1.0.2', 2555685, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 151, '151', 'f', 't', '2026-09-20 19:46:39.104273+00', '{"hum": 60, "temp": 25.5}', 77, -50, 44.09, 32.65, 'v1.0.1', 2167427, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 155, '155', 'f', 't', '2026-09-17 21:33:21.103927+00', '{"hum": 60, "temp": 25.5}', 23, -44, 20.63, 85.78, 'v1.0.0', 918653, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 158, '158', 'f', 't', '2026-09-22 16:59:41.175975+00', '{"hum": 60, "temp": 25.5}', 43, -49, 35.69, 43.5, 'v1.0.3', 1409519, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 159, '159', 'f', 't', '2026-09-19 23:00:39.10431+00', '{"hum": 60, "temp": 25.5}', 83, -63, 17.01, 45.44, 'v1.0.4', 1033211, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 160, '160', 'f', 't', '2026-09-19 03:51:20.912198+00', '{"hum": 60, "temp": 25.5}', 85, -43, 15.79, 64.74, 'v1.0.0', 1825952, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 161, '161', 'f', 't', '2026-09-16 14:08:41.967634+00', '{"hum": 60, "temp": 25.5}', 32, -76, 44.2, 52.33, 'v1.0.1', 49298, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 163, '163', 'f', 't', '2026-09-17 16:53:07.038725+00', '{"hum": 60, "temp": 25.5}', 68, -49, 21.62, 80.58, 'v1.0.3', 443859, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 164, '164', 'f', 't', '2026-09-17 08:32:31.40964+00', '{"hum": 60, "temp": 25.5}', 71, -55, 35.27, 56.04, 'v1.0.4', 351474, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 165, '165', 'f', 't', '2026-09-18 22:06:14.421889+00', '{"hum": 60, "temp": 25.5}', 98, -50, 17.39, 64.69, 'v1.0.0', 625542, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 168, '168', 'f', 't', '2026-09-17 05:08:06.914817+00', '{"hum": 60, "temp": 25.5}', 73, -50, 36.74, 43.66, 'v1.0.3', 1325502, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 173, '173', 'f', 't', '2026-09-21 11:23:07.269964+00', '{"hum": 60, "temp": 25.5}', 53, -72, 19.67, 53.24, 'v1.0.3', 2425789, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 175, '175', 'f', 't', '2026-09-17 20:37:21.338764+00', '{"hum": 60, "temp": 25.5}', 69, -66, 22.57, 76.49, 'v1.0.0', 2157550, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 176, '176', 'f', 't', '2026-09-19 08:21:52.892008+00', '{"hum": 60, "temp": 25.5}', 95, -66, 34.95, 48.61, 'v1.0.1', 1892528, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 181, '181', 'f', 't', '2026-09-17 10:05:07.619723+00', '{"hum": 60, "temp": 25.5}', 35, -58, 43.4, 42.61, 'v1.0.1', 2022659, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 182, '182', 'f', 't', '2026-09-18 06:04:09.056921+00', '{"hum": 60, "temp": 25.5}', 80, -54, 17.76, 45.24, 'v1.0.2', 2420679, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 185, '185', 'f', 't', '2026-09-22 11:03:03.012476+00', '{"hum": 60, "temp": 25.5}', 82, -79, 25.71, 55.35, 'v1.0.0', 1238015, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 189, '189', 'f', 't', '2026-09-19 09:06:05.665025+00', '{"hum": 60, "temp": 25.5}', 30, -41, 33.62, 34.44, 'v1.0.4', 2556419, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 1, '1', 'f', 't', '2026-09-23 08:49:23.708128+00', '{"signal": -55, "battery": 90}', 90, -55, 33.48, 32.5, 'v1.0.1', 39795, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 09:13:58.602955+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 195, '195', 'f', 't', '2026-09-17 06:10:17.163583+00', '{"hum": 60, "temp": 25.5}', 77, -71, 29.91, 40.06, 'v1.0.0', 2246885, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:50:24.72707+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 2, '2', 'f', 't', '2026-09-18 02:40:07.688789+00', '{"hum": 60, "temp": 25.5}', 54, -64, 15.71, 59.18, 'v1.0.2', 2400567, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 3, '3', 'f', 't', '2026-09-22 07:24:07.171989+00', '{"hum": 60, "temp": 25.5}', 100, -71, 25.63, 72.5, 'v1.0.3', 116005, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 4, '4', 'f', 't', '2026-09-19 19:23:10.578105+00', '{"hum": 60, "temp": 25.5}', 56, -50, 31.03, 80.58, 'v1.0.4', 320038, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 5, '5', 'f', 't', '2026-09-22 04:23:18.505376+00', '{"hum": 60, "temp": 25.5}', 53, -67, 34.02, 41.25, 'v1.0.0', 510361, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 6, '6', 'f', 't', '2026-09-21 20:41:27.315949+00', '{"hum": 60, "temp": 25.5}', 20, -60, 26.51, 86.19, 'v1.0.1', 706359, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 7, '7', 'f', 't', '2026-09-22 13:33:36.714897+00', '{"hum": 60, "temp": 25.5}', 48, -77, 30.55, 32.58, 'v1.0.2', 114537, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 9, '9', 'f', 't', '2026-09-17 01:31:48.338832+00', '{"hum": 60, "temp": 25.5}', 54, -66, 34.85, 65.76, 'v1.0.4', 1953283, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 10, '10', 'f', 't', '2026-09-21 04:18:16.756559+00', '{"hum": 60, "temp": 25.5}', 66, -60, 28.01, 77.04, 'v1.0.0', 719877, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 11, '11', 'f', 't', '2026-09-16 10:08:07.001788+00', '{"hum": 60, "temp": 25.5}', 55, -80, 23.32, 65.16, 'v1.0.1', 1041943, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 13, '13', 'f', 't', '2026-09-19 02:11:50.005288+00', '{"hum": 60, "temp": 25.5}', 70, -67, 42.04, 65.98, 'v1.0.3', 251542, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 14, '14', 'f', 't', '2026-09-22 09:24:47.407608+00', '{"hum": 60, "temp": 25.5}', 52, -70, 40.38, 43.45, 'v1.0.4', 1510357, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 15, '15', 'f', 't', '2026-09-23 04:14:55.841239+00', '{"hum": 60, "temp": 25.5}', 29, -69, 32.76, 47.65, 'v1.0.0', 807356, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 16, '16', 'f', 't', '2026-09-18 11:08:17.720526+00', '{"hum": 60, "temp": 25.5}', 81, -63, 25.28, 39.13, 'v1.0.1', 544892, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 17, '17', 'f', 't', '2026-09-16 18:56:25.052558+00', '{"hum": 60, "temp": 25.5}', 43, -79, 44.34, 83.79, 'v1.0.2', 831765, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 18, '18', 'f', 't', '2026-09-18 12:10:34.304714+00', '{"hum": 60, "temp": 25.5}', 77, -53, 20.15, 82.71, 'v1.0.3', 114365, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 20, '20', 'f', 't', '2026-09-21 13:10:07.656551+00', '{"hum": 60, "temp": 25.5}', 76, -63, 34.96, 56.42, 'v1.0.0', 260771, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 22, '22', 'f', 't', '2026-09-19 01:03:13.45246+00', '{"hum": 60, "temp": 25.5}', 60, -46, 27.1, 47.32, 'v1.0.2', 1886875, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 25, '25', 'f', 't', '2026-09-21 02:53:26.657662+00', '{"hum": 60, "temp": 25.5}', 63, -75, 17.94, 37.12, 'v1.0.0', 1746849, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 26, '26', 'f', 't', '2026-09-21 06:12:38.285936+00', '{"hum": 60, "temp": 25.5}', 27, -72, 44.18, 40.53, 'v1.0.1', 791169, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 27, '27', 'f', 't', '2026-09-22 19:52:16.665875+00', '{"hum": 60, "temp": 25.5}', 76, -57, 30.18, 77.99, 'v1.0.2', 1421989, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 28, '28', 'f', 't', '2026-09-20 08:57:55.667095+00', '{"hum": 60, "temp": 25.5}', 26, -58, 37.79, 45.94, 'v1.0.3', 597129, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 29, '29', 'f', 't', '2026-09-18 16:36:53.525588+00', '{"hum": 60, "temp": 25.5}', 88, -72, 25.82, 48.17, 'v1.0.4', 2149888, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 30, '30', 'f', 't', '2026-09-20 20:44:28.428414+00', '{"hum": 60, "temp": 25.5}', 96, -47, 28.72, 81.99, 'v1.0.0', 299761, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 31, '31', 'f', 't', '2026-09-22 13:23:13.905345+00', '{"hum": 60, "temp": 25.5}', 82, -41, 21.14, 88.27, 'v1.0.1', 1877840, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 33, '33', 'f', 't', '2026-09-23 06:38:36.096337+00', '{"hum": 60, "temp": 25.5}', 21, -44, 16.37, 54.09, 'v1.0.3', 546728, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 35, '35', 'f', 't', '2026-09-19 19:01:14.940206+00', '{"hum": 60, "temp": 25.5}', 86, -50, 22.3, 64.71, 'v1.0.0', 1372482, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 36, '36', 'f', 't', '2026-09-17 06:46:10.044154+00', '{"hum": 60, "temp": 25.5}', 88, -48, 39.76, 52.54, 'v1.0.1', 347923, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 37, '37', 'f', 't', '2026-09-18 15:02:24.691819+00', '{"hum": 60, "temp": 25.5}', 64, -55, 36.4, 41.78, 'v1.0.2', 1979477, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 38, '38', 'f', 't', '2026-09-21 23:48:04.212033+00', '{"hum": 60, "temp": 25.5}', 47, -67, 41.13, 41.78, 'v1.0.3', 1129631, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 39, '39', 'f', 't', '2026-09-17 19:04:46.815973+00', '{"hum": 60, "temp": 25.5}', 29, -68, 21.3, 60.61, 'v1.0.4', 661378, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 40, '40', 'f', 't', '2026-09-23 04:52:16.832755+00', '{"hum": 60, "temp": 25.5}', 95, -60, 35.51, 59.85, 'v1.0.0', 2039415, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 42, '42', 'f', 't', '2026-09-21 22:41:56.344684+00', '{"hum": 60, "temp": 25.5}', 37, -67, 36.58, 40.79, 'v1.0.2', 1950460, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 44, '44', 'f', 't', '2026-09-23 04:50:13.606159+00', '{"hum": 60, "temp": 25.5}', 56, -77, 29.93, 39.36, 'v1.0.4', 1171536, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 47, '47', 'f', 't', '2026-09-22 15:37:39.823163+00', '{"hum": 60, "temp": 25.5}', 66, -67, 32.02, 52.73, 'v1.0.2', 393362, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 49, '49', 'f', 't', '2026-09-22 07:55:54.291482+00', '{"hum": 60, "temp": 25.5}', 36, -45, 20.25, 45.74, 'v1.0.4', 595081, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 50, '50', 'f', 't', '2026-09-18 03:16:21.532777+00', '{"hum": 60, "temp": 25.5}', 67, -68, 37.05, 86.09, 'v1.0.0', 356616, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 51, '51', 'f', 't', '2026-09-19 11:15:36.905699+00', '{"hum": 60, "temp": 25.5}', 70, -67, 29.22, 77.32, 'v1.0.1', 1562979, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 52, '52', 'f', 't', '2026-09-19 23:52:12.900753+00', '{"hum": 60, "temp": 25.5}', 35, -63, 40.65, 42.92, 'v1.0.2', 871940, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 53, '53', 'f', 't', '2026-09-19 08:52:41.504903+00', '{"hum": 60, "temp": 25.5}', 99, -63, 44.06, 41.81, 'v1.0.3', 980770, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 55, '55', 'f', 't', '2026-09-19 07:38:06.461067+00', '{"hum": 60, "temp": 25.5}', 25, -47, 39.04, 85.84, 'v1.0.0', 1670145, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 58, '58', 'f', 't', '2026-09-19 15:31:16.977764+00', '{"hum": 60, "temp": 25.5}', 65, -52, 28.99, 58.52, 'v1.0.3', 234524, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 60, '60', 'f', 't', '2026-09-16 17:46:03.892459+00', '{"hum": 60, "temp": 25.5}', 64, -45, 17.81, 68.18, 'v1.0.0', 403323, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 61, '61', 'f', 't', '2026-09-19 00:51:48.679345+00', '{"hum": 60, "temp": 25.5}', 64, -56, 32.07, 49.19, 'v1.0.1', 2177528, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 65, '65', 'f', 't', '2026-09-23 03:56:01.133639+00', '{"hum": 60, "temp": 25.5}', 93, -65, 40.63, 72.23, 'v1.0.0', 1412406, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 66, '66', 'f', 't', '2026-09-16 20:25:12.144609+00', '{"hum": 60, "temp": 25.5}', 74, -45, 28.89, 61.46, 'v1.0.1', 1985781, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 67, '67', 'f', 't', '2026-09-16 10:14:53.628985+00', '{"hum": 60, "temp": 25.5}', 94, -76, 43.26, 52.24, 'v1.0.2', 850647, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 68, '68', 'f', 't', '2026-09-22 09:51:27.434698+00', '{"hum": 60, "temp": 25.5}', 62, -67, 35.89, 37.29, 'v1.0.3', 711406, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 69, '69', 'f', 't', '2026-09-21 07:31:32.043576+00', '{"hum": 60, "temp": 25.5}', 93, -58, 38.88, 68.8, 'v1.0.4', 2382512, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 71, '71', 'f', 't', '2026-09-21 08:07:44.032483+00', '{"hum": 60, "temp": 25.5}', 55, -78, 39.15, 80.88, 'v1.0.1', 1108451, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 72, '72', 'f', 't', '2026-09-22 01:48:50.830554+00', '{"hum": 60, "temp": 25.5}', 29, -45, 23.72, 81.44, 'v1.0.2', 963131, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 73, '73', 'f', 't', '2026-09-18 05:53:48.557922+00', '{"hum": 60, "temp": 25.5}', 74, -68, 31.76, 39.54, 'v1.0.3', 1623598, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 74, '74', 'f', 't', '2026-09-18 22:58:08.946788+00', '{"hum": 60, "temp": 25.5}', 39, -50, 43.46, 69.1, 'v1.0.4', 1780698, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 79, '79', 'f', 't', '2026-09-19 18:12:30.330163+00', '{"hum": 60, "temp": 25.5}', 58, -52, 30.42, 31.62, 'v1.0.4', 2103319, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 80, '80', 'f', 't', '2026-09-17 21:25:39.252145+00', '{"hum": 60, "temp": 25.5}', 38, -60, 33.26, 51.81, 'v1.0.0', 748980, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 81, '81', 'f', 't', '2026-09-22 04:28:46.124098+00', '{"hum": 60, "temp": 25.5}', 56, -62, 43.74, 34.46, 'v1.0.1', 1246222, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 82, '82', 'f', 't', '2026-09-18 23:12:23.83864+00', '{"hum": 60, "temp": 25.5}', 24, -57, 23.63, 74.06, 'v1.0.2', 812100, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 85, '85', 'f', 't', '2026-09-21 17:13:08.499064+00', '{"hum": 60, "temp": 25.5}', 93, -58, 30.54, 62.77, 'v1.0.0', 1969482, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 86, '86', 'f', 't', '2026-09-21 20:32:28.512408+00', '{"hum": 60, "temp": 25.5}', 41, -50, 34.41, 68.97, 'v1.0.1', 1567919, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 87, '87', 'f', 't', '2026-09-23 06:39:49.140382+00', '{"hum": 60, "temp": 25.5}', 25, -43, 37.35, 75.56, 'v1.0.2', 1556964, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 88, '88', 'f', 't', '2026-09-22 01:57:28.769716+00', '{"hum": 60, "temp": 25.5}', 38, -77, 43.81, 72.02, 'v1.0.3', 2166180, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 89, '89', 'f', 't', '2026-09-19 19:39:47.084789+00', '{"hum": 60, "temp": 25.5}', 25, -55, 28.07, 53.57, 'v1.0.4', 404391, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 90, '90', 'f', 't', '2026-09-18 00:19:32.070999+00', '{"hum": 60, "temp": 25.5}', 41, -55, 38.01, 55.68, 'v1.0.0', 1412751, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 91, '91', 'f', 't', '2026-09-22 13:19:14.023881+00', '{"hum": 60, "temp": 25.5}', 77, -59, 17.65, 57.87, 'v1.0.1', 1736044, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 93, '93', 'f', 't', '2026-09-19 10:05:56.790826+00', '{"hum": 60, "temp": 25.5}', 89, -42, 44.6, 71.95, 'v1.0.3', 970440, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 94, '94', 'f', 't', '2026-09-19 22:52:00.712403+00', '{"hum": 60, "temp": 25.5}', 79, -58, 26.61, 59.89, 'v1.0.4', 1109171, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 97, '97', 'f', 't', '2026-09-17 16:07:56.708827+00', '{"hum": 60, "temp": 25.5}', 43, -75, 28.21, 34.29, 'v1.0.2', 1585483, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 98, '98', 'f', 't', '2026-09-20 07:25:30.070314+00', '{"hum": 60, "temp": 25.5}', 45, -71, 22.17, 83.5, 'v1.0.3', 121605, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 99, '99', 'f', 't', '2026-09-22 20:59:11.272786+00', '{"hum": 60, "temp": 25.5}', 60, -48, 23.18, 75.76, 'v1.0.4', 1131350, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 101, '101', 'f', 't', '2026-09-21 13:12:59.394881+00', '{"hum": 60, "temp": 25.5}', 26, -69, 41.23, 52.11, 'v1.0.1', 1635127, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 102, '102', 'f', 't', '2026-09-16 12:02:28.397556+00', '{"hum": 60, "temp": 25.5}', 46, -55, 42.17, 51.57, 'v1.0.2', 2269645, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 103, '103', 'f', 't', '2026-09-21 03:56:32.957988+00', '{"hum": 60, "temp": 25.5}', 76, -49, 31.69, 78.34, 'v1.0.3', 1410198, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 107, '107', 'f', 't', '2026-09-21 15:35:25.926073+00', '{"hum": 60, "temp": 25.5}', 67, -45, 24.84, 51.34, 'v1.0.2', 389708, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 108, '108', 'f', 't', '2026-09-16 14:13:18.246225+00', '{"hum": 60, "temp": 25.5}', 87, -72, 34.37, 35.05, 'v1.0.3', 1945469, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 109, '109', 'f', 't', '2026-09-19 19:32:55.010687+00', '{"hum": 60, "temp": 25.5}', 36, -42, 42.12, 45.64, 'v1.0.4', 686341, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 110, '110', 'f', 't', '2026-09-18 16:04:16.99938+00', '{"hum": 60, "temp": 25.5}', 47, -65, 18.4, 34.79, 'v1.0.0', 1637624, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 111, '111', 'f', 't', '2026-09-22 21:09:26.625087+00', '{"hum": 60, "temp": 25.5}', 99, -45, 42.13, 89.72, 'v1.0.1', 269545, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 112, '112', 'f', 't', '2026-09-22 02:53:26.957893+00', '{"hum": 60, "temp": 25.5}', 92, -76, 25.18, 41.4, 'v1.0.2', 547732, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 113, '113', 'f', 't', '2026-09-20 19:35:30.751474+00', '{"hum": 60, "temp": 25.5}', 82, -54, 15.85, 47.37, 'v1.0.3', 333397, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 114, '114', 'f', 't', '2026-09-18 01:46:14.333724+00', '{"hum": 60, "temp": 25.5}', 55, -75, 33.62, 41.09, 'v1.0.4', 1444510, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 115, '115', 'f', 't', '2026-09-20 19:15:37.811532+00', '{"hum": 60, "temp": 25.5}', 53, -49, 41.16, 48.76, 'v1.0.0', 2466524, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 116, '116', 'f', 't', '2026-09-22 00:17:53.44862+00', '{"hum": 60, "temp": 25.5}', 30, -69, 31.71, 31.51, 'v1.0.1', 2115174, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 117, '117', 'f', 't', '2026-09-20 08:33:06.373069+00', '{"hum": 60, "temp": 25.5}', 56, -40, 32.34, 79.47, 'v1.0.2', 1785926, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 118, '118', 'f', 't', '2026-09-16 10:32:18.71157+00', '{"hum": 60, "temp": 25.5}', 69, -54, 44.26, 79.95, 'v1.0.3', 1695263, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 119, '119', 'f', 't', '2026-09-20 12:46:06.648955+00', '{"hum": 60, "temp": 25.5}', 62, -74, 16.98, 89.57, 'v1.0.4', 2344307, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 121, '121', 'f', 't', '2026-09-18 10:31:18.231662+00', '{"hum": 60, "temp": 25.5}', 95, -42, 44.01, 63.34, 'v1.0.1', 2208240, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 122, '122', 'f', 't', '2026-09-16 08:43:05.907292+00', '{"hum": 60, "temp": 25.5}', 95, -56, 22.8, 55.16, 'v1.0.2', 2128225, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 123, '123', 'f', 't', '2026-09-21 08:35:13.021571+00', '{"hum": 60, "temp": 25.5}', 38, -62, 36.85, 39.04, 'v1.0.3', 2408963, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 124, '124', 'f', 't', '2026-09-19 19:37:37.053171+00', '{"hum": 60, "temp": 25.5}', 79, -41, 30.59, 38.54, 'v1.0.4', 911957, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 125, '125', 'f', 't', '2026-09-17 17:40:19.209607+00', '{"hum": 60, "temp": 25.5}', 56, -41, 16.91, 32.63, 'v1.0.0', 1658635, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 126, '126', 'f', 't', '2026-09-16 15:29:32.706179+00', '{"hum": 60, "temp": 25.5}', 62, -65, 39.98, 57.39, 'v1.0.1', 407678, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 128, '128', 'f', 't', '2026-09-18 02:03:26.044066+00', '{"hum": 60, "temp": 25.5}', 50, -68, 44.45, 84.04, 'v1.0.3', 1525843, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 129, '129', 'f', 't', '2026-09-17 23:58:10.382368+00', '{"hum": 60, "temp": 25.5}', 48, -70, 32.2, 69.96, 'v1.0.4', 761175, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 132, '132', 'f', 't', '2026-09-18 04:16:42.315092+00', '{"hum": 60, "temp": 25.5}', 75, -54, 25.55, 84.78, 'v1.0.2', 1719847, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 133, '133', 'f', 't', '2026-09-18 02:55:53.071758+00', '{"hum": 60, "temp": 25.5}', 45, -56, 24.53, 77.15, 'v1.0.3', 1132231, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 134, '134', 'f', 't', '2026-09-22 15:30:37.932748+00', '{"hum": 60, "temp": 25.5}', 94, -61, 42.99, 54.34, 'v1.0.4', 118533, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 135, '135', 'f', 't', '2026-09-18 00:44:08.048146+00', '{"hum": 60, "temp": 25.5}', 69, -63, 19.16, 37.74, 'v1.0.0', 1478400, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 136, '136', 'f', 't', '2026-09-18 14:32:47.907758+00', '{"hum": 60, "temp": 25.5}', 65, -44, 24.79, 80.3, 'v1.0.1', 1995323, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 139, '139', 'f', 't', '2026-09-22 18:35:22.346331+00', '{"hum": 60, "temp": 25.5}', 69, -70, 38.53, 31.75, 'v1.0.4', 874027, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 140, '140', 'f', 't', '2026-09-19 08:18:39.955255+00', '{"hum": 60, "temp": 25.5}', 65, -76, 25.06, 51.08, 'v1.0.0', 1760709, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 141, '141', 'f', 't', '2026-09-17 18:46:58.891201+00', '{"hum": 60, "temp": 25.5}', 56, -50, 22.19, 37.76, 'v1.0.1', 2194930, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 143, '143', 'f', 't', '2026-09-19 14:19:42.837055+00', '{"hum": 60, "temp": 25.5}', 98, -49, 20.34, 41.71, 'v1.0.3', 2589575, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 145, '145', 'f', 't', '2026-09-20 22:56:58.589048+00', '{"hum": 60, "temp": 25.5}', 76, -50, 28.66, 31.68, 'v1.0.0', 1114494, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 146, '146', 'f', 't', '2026-09-17 00:55:30.424364+00', '{"hum": 60, "temp": 25.5}', 91, -65, 26.61, 63.88, 'v1.0.1', 2084384, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 148, '148', 'f', 't', '2026-09-17 15:18:02.124212+00', '{"hum": 60, "temp": 25.5}', 52, -72, 25.88, 83.99, 'v1.0.3', 537012, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 149, '149', 'f', 't', '2026-09-21 05:14:01.160596+00', '{"hum": 60, "temp": 25.5}', 58, -64, 23.92, 51.73, 'v1.0.4', 1834622, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 150, '150', 'f', 't', '2026-09-20 23:47:12.786338+00', '{"hum": 60, "temp": 25.5}', 31, -53, 23.8, 81.28, 'v1.0.0', 801732, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 152, '152', 'f', 't', '2026-09-22 01:44:15.662775+00', '{"hum": 60, "temp": 25.5}', 39, -53, 29.61, 84.76, 'v1.0.2', 203018, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 153, '153', 'f', 't', '2026-09-19 06:28:52.740565+00', '{"hum": 60, "temp": 25.5}', 28, -80, 23, 80.67, 'v1.0.3', 2591024, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 154, '154', 'f', 't', '2026-09-19 07:21:27.439316+00', '{"hum": 60, "temp": 25.5}', 71, -70, 19.07, 61.44, 'v1.0.4', 1713997, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 156, '156', 'f', 't', '2026-09-22 03:33:30.713012+00', '{"hum": 60, "temp": 25.5}', 54, -69, 44.26, 76.26, 'v1.0.1', 2329320, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 157, '157', 'f', 't', '2026-09-16 21:07:40.692998+00', '{"hum": 60, "temp": 25.5}', 28, -48, 39.63, 64.35, 'v1.0.2', 1202087, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 162, '162', 'f', 't', '2026-09-17 17:20:37.750828+00', '{"hum": 60, "temp": 25.5}', 88, -69, 21.27, 68.8, 'v1.0.2', 162060, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 166, '166', 'f', 't', '2026-09-22 14:09:06.366979+00', '{"hum": 60, "temp": 25.5}', 35, -58, 44.29, 43.61, 'v1.0.1', 2363812, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 167, '167', 'f', 't', '2026-09-16 13:06:22.23411+00', '{"hum": 60, "temp": 25.5}', 52, -67, 22.39, 58.46, 'v1.0.2', 2395386, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 169, '169', 'f', 't', '2026-09-21 23:06:51.515336+00', '{"hum": 60, "temp": 25.5}', 29, -58, 38.02, 34.6, 'v1.0.4', 1176484, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 170, '170', 'f', 't', '2026-09-20 18:38:26.305551+00', '{"hum": 60, "temp": 25.5}', 30, -50, 31.26, 36.13, 'v1.0.0', 1434618, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 171, '171', 'f', 't', '2026-09-17 01:44:03.48134+00', '{"hum": 60, "temp": 25.5}', 92, -47, 18.45, 35, 'v1.0.1', 1500806, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 172, '172', 'f', 't', '2026-09-23 02:19:57.705691+00', '{"hum": 60, "temp": 25.5}', 30, -79, 16.54, 32.25, 'v1.0.2', 1066765, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 174, '174', 'f', 't', '2026-09-21 09:02:25.615445+00', '{"hum": 60, "temp": 25.5}', 89, -61, 41.52, 65.16, 'v1.0.4', 1811843, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 177, '177', 'f', 't', '2026-09-19 16:02:25.96082+00', '{"hum": 60, "temp": 25.5}', 79, -68, 23.74, 53.18, 'v1.0.2', 927841, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 178, '178', 'f', 't', '2026-09-19 09:37:00.497716+00', '{"hum": 60, "temp": 25.5}', 89, -46, 44.9, 60.88, 'v1.0.3', 677874, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 179, '179', 'f', 't', '2026-09-21 13:08:48.820515+00', '{"hum": 60, "temp": 25.5}', 63, -45, 21.13, 48.41, 'v1.0.4', 934110, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 180, '180', 'f', 't', '2026-09-21 11:30:45.927954+00', '{"hum": 60, "temp": 25.5}', 89, -65, 43.34, 73.87, 'v1.0.0', 2189174, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 183, '183', 'f', 't', '2026-09-22 12:03:30.310275+00', '{"hum": 60, "temp": 25.5}', 70, -64, 44.93, 87.89, 'v1.0.3', 353396, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 184, '184', 'f', 't', '2026-09-16 17:51:18.807346+00', '{"hum": 60, "temp": 25.5}', 65, -78, 17.54, 88.78, 'v1.0.4', 550575, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 186, '186', 'f', 't', '2026-09-22 15:46:02.047356+00', '{"hum": 60, "temp": 25.5}', 47, -64, 36.66, 55.77, 'v1.0.1', 1762409, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 187, '187', 'f', 't', '2026-09-23 04:15:15.409511+00', '{"hum": 60, "temp": 25.5}', 55, -50, 35.49, 72.33, 'v1.0.2', 1970917, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 188, '188', 'f', 't', '2026-09-20 17:04:26.163318+00', '{"hum": 60, "temp": 25.5}', 38, -58, 38.63, 41.46, 'v1.0.3', 1063859, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 190, '190', 'f', 't', '2026-09-17 22:11:32.74231+00', '{"hum": 60, "temp": 25.5}', 85, -46, 36.33, 41.99, 'v1.0.0', 1840268, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 191, '191', 'f', 't', '2026-09-22 18:40:17.753541+00', '{"hum": 60, "temp": 25.5}', 63, -72, 20.7, 56.95, 'v1.0.1', 2020859, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 192, '192', 'f', 't', '2026-09-17 14:34:35.645687+00', '{"hum": 60, "temp": 25.5}', 60, -75, 20.04, 83.51, 'v1.0.2', 2006044, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 193, '193', 'f', 't', '2026-09-18 08:39:07.937478+00', '{"hum": 60, "temp": 25.5}', 65, -70, 27.54, 79.43, 'v1.0.3', 306009, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 194, '194', 'f', 't', '2026-09-17 01:22:00.111449+00', '{"hum": 60, "temp": 25.5}', 55, -64, 35.36, 81.05, 'v1.0.4', 2313396, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 196, '196', 'f', 't', '2026-09-22 05:43:28.856479+00', '{"hum": 60, "temp": 25.5}', 28, -51, 21.08, 65.95, 'v1.0.1', 2238513, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 197, '197', 'f', 't', '2026-09-21 08:28:45.290573+00', '{"hum": 60, "temp": 25.5}', 70, -62, 16.08, 87.59, 'v1.0.2', 312877, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 198, '198', 'f', 't', '2026-09-17 06:18:37.661247+00', '{"hum": 60, "temp": 25.5}', 81, -64, 20.6, 67.66, 'v1.0.3', 2107955, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 199, '199', 'f', 't', '2026-09-19 06:05:53.251769+00', '{"hum": 60, "temp": 25.5}', 25, -42, 26.58, 37.01, 'v1.0.4', 1831712, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');
INSERT INTO "public"."device_status" VALUES ('11111111-1111-1111-1111-111111111111', 200, '200', 'f', 't', '2026-09-22 23:20:11.597037+00', '{"hum": 60, "temp": 25.5}', 51, -67, 37.7, 44.45, 'v1.0.0', 1392736, '{"lat": 13.75, "lng": 100.5}', '2026-09-23 07:50:24.72707+00', '2026-09-23 07:53:18.310404+00');

-- ----------------------------
-- Table structure for erp_access_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_access_tokens";
CREATE TABLE "public"."erp_access_tokens" (
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
COMMENT ON COLUMN "public"."erp_access_tokens"."id" IS 'Unique identifier of the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."refresh_id" IS 'Refresh token associated with this access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."erp_access_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."permission" IS 'Permission level associated with the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."created_at" IS 'Timestamp when the access token was created';
COMMENT ON COLUMN "public"."erp_access_tokens"."expires_at" IS 'Expiration timestamp of the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."revoked" IS 'Indicates whether the access token was revoked';
COMMENT ON COLUMN "public"."erp_access_tokens"."revoked_at" IS 'Timestamp when the access token was revoked';

-- ----------------------------
-- Records of erp_access_tokens
-- ----------------------------
INSERT INTO "public"."erp_access_tokens" VALUES ('a1bc9edc-949e-46a4-b7e1-24da3dcd12a7', 'add80c27-79bc-43b1-8b39-86a6567261d2', '8bef7399ee7b4f649b811bc1f310ac9ac0daa2052f2141e42b003449f8806907', '9a0f4b95e83e380cd8356d78e3a76b707f7b9b2e4555363999cf42dea02c4780', 'USER', '2026-09-30 15:13:35.889488+00', '2026-09-30 15:28:35.889488+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('62a65827-70c4-4e7d-914c-917651c18432', 'a2160472-ef20-411d-87e4-568f34ab8d8b', '1657d2e600ea6d231768595d665f0a7147a3c7c5508b9a7912cfa84359a7786b', '22935414960b5706f4ad661d17f0201ce4b72d2fe98ac7f99903e4c5833ca273', 'USER', '2026-09-30 17:17:12.411281+00', '2026-09-30 17:32:12.411281+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('4c5d7e3a-4197-4407-a5c8-28bedc2c26e2', 'cff5f11b-dea7-41d7-8e2a-b5d57b89fb65', '31fc7b98aebbf83f6a3c713814710525c62ce37ab2cbf8479ccb7f761e067206', '3aed3837233abde5e65ef67a05f680bfa7206213d4c602f590585d5a2b3c38fd', 'USER', '2026-09-30 17:17:21.143016+00', '2026-09-30 17:32:21.143016+00', 'f', NULL);

-- ----------------------------
-- Table structure for erp_authentications
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_authentications";
CREATE TABLE "public"."erp_authentications" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" int8 NOT NULL,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default" NOT NULL,
  "device" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "accept_language" varchar(255) COLLATE "pg_catalog"."default",
  "accept_encoding" varchar(255) COLLATE "pg_catalog"."default",
  "origin" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "referrer" varchar(255) COLLATE "pg_catalog"."default",
  "location" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at" timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted" bool NOT NULL
)
;
COMMENT ON COLUMN "public"."erp_authentications"."id" IS 'Unique identifier of the authentication';
COMMENT ON COLUMN "public"."erp_authentications"."user_id" IS 'Identifier of the user who owns the authentication (BIGINT 11+ digits)';
COMMENT ON COLUMN "public"."erp_authentications"."ip_address" IS 'IP address used when the authentication was created';
COMMENT ON COLUMN "public"."erp_authentications"."device" IS 'Human readable device name';
COMMENT ON COLUMN "public"."erp_authentications"."user_agent" IS 'User agent string of the client';
COMMENT ON COLUMN "public"."erp_authentications"."accept_language" IS 'Accept-Language header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."accept_encoding" IS 'accept_encoding header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."origin" IS 'Origin header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."referrer" IS 'Referrer header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."location" IS 'Approximate geographic location of the client';
COMMENT ON COLUMN "public"."erp_authentications"."created_at" IS 'Timestamp when the authentication was created';
COMMENT ON COLUMN "public"."erp_authentications"."last_update_at" IS 'Last time the authentication was updated';
COMMENT ON COLUMN "public"."erp_authentications"."blacklisted" IS 'Indicates whether the authentication is blacklisted';

-- ----------------------------
-- Records of erp_authentications
-- ----------------------------
INSERT INTO "public"."erp_authentications" VALUES ('466503cf-91eb-4771-ad66-2bf3baa5547b', 10000000004, '127.0.0.1', 'b693d4695d474fa3baffd5bb117c11e4', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/154.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://localhost:8000', 'http://localhost:8000/docs', NULL, '2026-09-30 15:13:12.731332+00', '2026-09-30 15:13:35.889488+00', 'f');
INSERT INTO "public"."erp_authentications" VALUES ('76fdde86-f439-48c1-8428-ecf9f3563d9f', 10000000004, '127.0.0.1', '77238c79e91e4ef28859f2e92a7aa6df', 'postmanruntime/2.10.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-30 14:57:24.669509+00', '2026-09-30 17:17:12.411281+00', 'f');
INSERT INTO "public"."erp_authentications" VALUES ('9dbda9ed-d63c-45ca-8cdf-5c812357979a', 10000000002, '127.0.0.1', '77238c79e91e4ef28859f2e92a7aa6df', 'postmanruntime/2.10.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-30 15:16:10.734401+00', '2026-09-30 17:17:18.979309+00', 'f');

-- ----------------------------
-- Table structure for erp_keys
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_keys";
CREATE TABLE "public"."erp_keys" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "prefix" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "last_four" varchar(4) COLLATE "pg_catalog"."default" NOT NULL,
  "hashed_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "expires_at" timestamptz(6),
  "last_used_at" timestamptz(6),
  "created_by" int8 NOT NULL,
  "updated_by" int8 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_keys"."name" IS 'Human-readable name of the API key';
COMMENT ON COLUMN "public"."erp_keys"."description" IS 'Optional description of the API key';
COMMENT ON COLUMN "public"."erp_keys"."prefix" IS 'Public, non-secret identifier fragment of the key';
COMMENT ON COLUMN "public"."erp_keys"."last_four" IS 'Last four characters of the raw key, for masked display';
COMMENT ON COLUMN "public"."erp_keys"."hashed_key" IS 'HMAC-SHA256 hash of the raw key; the raw key is never stored';
COMMENT ON COLUMN "public"."erp_keys"."expires_at" IS 'Expiration timestamp of the key; null means it never expires';
COMMENT ON COLUMN "public"."erp_keys"."last_used_at" IS 'Timestamp of the last time the key was used to authenticate';
COMMENT ON COLUMN "public"."erp_keys"."created_by" IS 'Identifier of the user (BIGINT) who created the key';
COMMENT ON COLUMN "public"."erp_keys"."updated_by" IS 'Identifier of the user (BIGINT) who last updated the key';

-- ----------------------------
-- Records of erp_keys
-- ----------------------------

-- ----------------------------
-- Table structure for erp_knowledges
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_knowledges";
CREATE TABLE "public"."erp_knowledges" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_by" int8 NOT NULL,
  "updated_by" int8 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_knowledges"."name" IS 'Unique name of the knowledge record';
COMMENT ON COLUMN "public"."erp_knowledges"."description" IS 'Detailed description of the knowledge record';
COMMENT ON COLUMN "public"."erp_knowledges"."created_by" IS 'Identifier of the user who created the record';
COMMENT ON COLUMN "public"."erp_knowledges"."updated_by" IS 'Identifier of the user who last updated the record';

-- ----------------------------
-- Records of erp_knowledges
-- ----------------------------

-- ----------------------------
-- Table structure for erp_notifications
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_notifications";
CREATE TABLE "public"."erp_notifications" (
  "user_id" int8 NOT NULL,
  "notification_type" "public"."notification_type_enum" NOT NULL,
  "title" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "body" text COLLATE "pg_catalog"."default" NOT NULL,
  "redirect_url" varchar(2048) COLLATE "pg_catalog"."default",
  "metadata" jsonb,
  "originated_from_broadcast" varchar(20) COLLATE "pg_catalog"."default",
  "is_read" bool NOT NULL DEFAULT false,
  "read_at" timestamptz(6),
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_notifications"."user_id" IS 'Identifier of the user who receives this notification';
COMMENT ON COLUMN "public"."erp_notifications"."notification_type" IS 'Event type that triggered this notification';
COMMENT ON COLUMN "public"."erp_notifications"."title" IS 'Short title of the notification';
COMMENT ON COLUMN "public"."erp_notifications"."body" IS 'Full body text of the notification';
COMMENT ON COLUMN "public"."erp_notifications"."redirect_url" IS 'Optional URL for deep linking from the notification';
COMMENT ON COLUMN "public"."erp_notifications"."metadata" IS 'Optional JSON payload with internal context data (resource_id, etc.)';
COMMENT ON COLUMN "public"."erp_notifications"."originated_from_broadcast" IS 'Role targeted by the fan-out broadcast that created this notification, if any';
COMMENT ON COLUMN "public"."erp_notifications"."is_read" IS 'Whether the user has read this notification';
COMMENT ON COLUMN "public"."erp_notifications"."read_at" IS 'Timestamp when the notification was marked as read';

-- ----------------------------
-- Records of erp_notifications
-- ----------------------------

-- ----------------------------
-- Table structure for erp_refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_refresh_tokens";
CREATE TABLE "public"."erp_refresh_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "authentication_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."erp_refresh_tokens"."id" IS 'Unique identifier of the refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."authentication_id" IS 'Authentication associated with this refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."created_at" IS 'Timestamp when the refresh token was created';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."expires_at" IS 'Expiration timestamp of the refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of erp_refresh_tokens
-- ----------------------------
INSERT INTO "public"."erp_refresh_tokens" VALUES ('add80c27-79bc-43b1-8b39-86a6567261d2', '466503cf-91eb-4771-ad66-2bf3baa5547b', '7255a9d635e92a096a5befc5bfff29ca4529a3201eb1c16aa74f5b214c17534e', 'd345395726186e8efa25578835aae15a762793819597b85bfa37e766a8cc7f2a', '2026-09-30 15:13:12.729831+00', '2026-09-30 15:13:35.889488+00', '2026-10-07 15:13:35.889488+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('a2160472-ef20-411d-87e4-568f34ab8d8b', '76fdde86-f439-48c1-8428-ecf9f3563d9f', '586caaf8149bac46513a4b590dfb03e1cf5e557a8ee5ecccfcfcf867db40cd3f', '588f1c24883482251807fbbc5889f86ae10468c4303d8a70d1b883093281e3e1', '2026-09-30 14:57:24.622387+00', '2026-09-30 17:17:12.411281+00', '2026-10-07 17:17:12.411281+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('cff5f11b-dea7-41d7-8e2a-b5d57b89fb65', '9dbda9ed-d63c-45ca-8cdf-5c812357979a', '0ee3e29d4d3bae763cfa0c3f71b3fce6a3930063b6e8f3f3bb165fa82954a729', '3ba3d587e7217c3954373a2a5dd850cc6918156f3568ee5d682dee2ab37ef0e3', '2026-09-30 15:16:10.733375+00', '2026-09-30 17:17:21.143016+00', '2026-10-07 17:17:18.979309+00', 'f', NULL);

-- ----------------------------
-- Table structure for erp_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_users";
CREATE TABLE "public"."erp_users" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 10000000000
CACHE 1
),
  "first_name" varchar(100) COLLATE "pg_catalog"."default",
  "last_name" varchar(100) COLLATE "pg_catalog"."default",
  "preferred_name" varchar(100) COLLATE "pg_catalog"."default",
  "full_name" varchar(200) COLLATE "pg_catalog"."default",
  "nickname" varchar(100) COLLATE "pg_catalog"."default",
  "username" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "phone" varchar(18) COLLATE "pg_catalog"."default",
  "mobile_number" varchar(18) COLLATE "pg_catalog"."default",
  "line_id" varchar(100) COLLATE "pg_catalog"."default",
  "id_card" varchar(20) COLLATE "pg_catalog"."default",
  "gender" "public"."gender_enum",
  "birthdate" date,
  "avatar" text COLLATE "pg_catalog"."default",
  "avatar_path" text COLLATE "pg_catalog"."default",
  "message" text COLLATE "pg_catalog"."default",
  "remark" text COLLATE "pg_catalog"."default",
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "temporary_password" varchar(255) COLLATE "pg_catalog"."default",
  "role" "public"."role_enum" NOT NULL DEFAULT 'USER'::role_enum,
  "status" "public"."user_status_enum" NOT NULL DEFAULT 'ACTIVE'::user_status_enum,
  "online_status" "public"."online_status_enum" NOT NULL DEFAULT 'OFFLINE'::online_status_enum,
  "active_status" int2,
  "network_id" int8,
  "network_type_id" int8,
  "type_id" int8,
  "system_id" varchar(50) COLLATE "pg_catalog"."default",
  "location_id" varchar(50) COLLATE "pg_catalog"."default",
  "deleted_at" date,
  "is_verified" bool NOT NULL DEFAULT false,
  "is_superuser" bool NOT NULL DEFAULT false,
  "verification_code" varchar(64) COLLATE "pg_catalog"."default",
  "password_reset_token" varchar(64) COLLATE "pg_catalog"."default",
  "password_reset_at" timestamptz(6),
  "login_failed_count" int2 NOT NULL DEFAULT '0'::smallint,
  "last_sign_in_at" timestamptz(6),
  "public_notification" int2 NOT NULL DEFAULT '0'::smallint,
  "sms_notification" int2 NOT NULL DEFAULT '0'::smallint,
  "email_notification" int2 NOT NULL DEFAULT '0'::smallint,
  "line_notification" int2 NOT NULL DEFAULT '0'::smallint,
  "public_status" int2 NOT NULL DEFAULT '0'::smallint,
  "information_agreement_status" int2 NOT NULL DEFAULT '0'::smallint,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_users"."id" IS 'Auto-increment 11+ digit identifier';

-- ----------------------------
-- Records of erp_users
-- ----------------------------
INSERT INTO "public"."erp_users" VALUES (10000000002, 'John', 'Doe', 'John', 'John Doe', NULL, 'johndoe', 'johndoe@example.com', '+555472664275', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '$argon2id$v=19$m=65536,t=3,p=4$HabOnWs+KFFN4ECiIpcOcA$5zjDJzdh3UMfJW6QDRApCN0lNBYVi/JKx0D7fmQdOHY', 'MyP@ssword123', 'USER', 'ACTIVE', 'OFFLINE', 1, 1, 0, 0, '1', '1', NULL, 'f', 'f', NULL, NULL, NULL, 0, '2026-09-29 05:24:53.309663+00', 0, 0, 0, 0, 0, 0, 't', '2026-09-29 05:24:53.309663+00', '2026-09-29 05:24:53.309663+00');
INSERT INTO "public"."erp_users" VALUES (10000000007, 'system', 'admin', 'system', 'admin dev', NULL, 'system', 'system@example.com', '+555472664275', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '$argon2id$v=19$m=65536,t=3,p=4$WeNvqeZ+DKSA6vp7lljgcw$T13FChOj78CNKFMsXEdXUQUXtqRu3HqdnpELw0j+fMo', NULL, 'USER', 'ACTIVE', 'OFFLINE', 1, 1, 0, 0, '1', '1', NULL, 'f', 'f', NULL, NULL, NULL, 0, '2026-09-29 05:30:07.402279+00', 0, 0, 0, 0, 0, 0, 't', '2026-09-29 05:30:07.402279+00', '2026-09-29 05:30:07.402279+00');
INSERT INTO "public"."erp_users" VALUES (10000000004, 'admin', 'admin', 'admin', 'admin dev', NULL, 'admin', 'admin@example.com', '+555472664275', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '$argon2id$v=19$m=65536,t=3,p=4$MFryJna0AH2avV7Q19ABzg$szSHgxP/d78/v7/K9dENmMHZap1d1ChOAn2omHimrn0', 'MyP@ssword123', 'USER', 'ACTIVE', 'OFFLINE', 1, 1, 0, 0, '1', '1', NULL, 't', 't', NULL, NULL, NULL, 0, '2026-09-29 05:25:56.449029+00', 0, 0, 0, 0, 0, 0, 't', '2026-09-29 05:25:56.449029+00', '2026-09-29 05:25:56.449029+00');
INSERT INTO "public"."erp_users" VALUES (10000000000, 'demo', 'demo', 'demo', 'demo demo', 'demo', 'demo', 'demo@example.com', '+66896514753', '+66896514753', 'demo', NULL, 'MALE', '1991-09-30', NULL, NULL, NULL, NULL, '$argon2id$v=19$m=65536,t=3,p=4$JoO/qA/SWu06j2T66O1RPQ$i36wruFD1a2445GAQYkMk6IxWXKXnjgOAG7AhTQbyxY', NULL, 'USER', 'ACTIVE', 'OFFLINE', 1, 0, 0, 0, '1', '1', NULL, 'f', 'f', NULL, NULL, NULL, 0, '2026-09-30 15:20:21.751064+00', 0, 0, 0, 0, 0, 0, 't', '2026-09-30 15:20:21.751064+00', '2026-09-30 15:20:21.751064+00');

-- ----------------------------
-- Table structure for eval_datasets
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_datasets";
CREATE TABLE "public"."eval_datasets" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "task_type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'qa'::character varying,
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '1.0.0'::character varying,
  "case_count" int4 NOT NULL DEFAULT 0,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_datasets
-- ----------------------------

-- ----------------------------
-- Table structure for eval_metrics
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_metrics";
CREATE TABLE "public"."eval_metrics" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "kind" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "higher_is_better" bool NOT NULL DEFAULT true,
  "range_min" float8 NOT NULL DEFAULT 0,
  "range_max" float8 NOT NULL DEFAULT 1,
  "description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_metrics
-- ----------------------------
INSERT INTO "public"."eval_metrics" VALUES ('6b9882d0-1000-4c2d-ab6f-4081cba1fb20', 'exact_match', 'exact_match', 't', 0, 1, 'Exact string match (normalized)', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('4c633e9a-c6d1-4edf-a6be-12288830c8d6', 'f1', 'f1', 't', 0, 1, 'Token-level F1', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('5ad56304-404b-40cf-863a-e0fbfd564300', 'rouge', 'rouge', 't', 0, 1, 'ROUGE-L F1', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('011f0491-c90c-4a40-9d3a-5d8d35eaeab6', 'faithfulness', 'faithfulness', 't', 0, 1, 'Faithfulness (no hallucination)', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('afd63d25-0dcc-4536-b350-6adb205acc28', 'answer_relevance', 'answer_relevance', 't', 0, 1, 'Answer relevance', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('d5f01826-228e-47fb-831c-774f9c052a7e', 'context_precision', 'context_precision', 't', 0, 1, 'Context precision', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('2f94e7ad-676b-4460-8445-2d6e52124925', 'context_recall', 'context_recall', 't', 0, 1, 'Context recall', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('d6261326-0951-4d41-8033-21483675045a', 'mrr', 'mrr', 't', 0, 1, 'Mean Reciprocal Rank', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('106341c3-2d9c-48f3-aa6a-c396204b7755', 'ndcg', 'ndcg', 't', 0, 1, 'NDCG', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('7fca6727-5cd2-41e7-b327-f7adf7314936', 'ragas', 'ragas', 't', 0, 1, 'RAGAS combined', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');
INSERT INTO "public"."eval_metrics" VALUES ('79c8b1c2-f03d-4fb1-a495-fd2faa354c49', 'hallucination', 'hallucination', 'f', 0, 1, 'Hallucination rate', '2026-09-28 13:28:53.941387+00', '2026-09-28 13:28:53.941387+00');

-- ----------------------------
-- Table structure for eval_reports
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_reports";
CREATE TABLE "public"."eval_reports" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "run_id" uuid NOT NULL,
  "summary_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "passed" bool NOT NULL DEFAULT false,
  "generated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_reports
-- ----------------------------

-- ----------------------------
-- Table structure for eval_results
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_results";
CREATE TABLE "public"."eval_results" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "run_id" uuid NOT NULL,
  "case_id" uuid NOT NULL,
  "metric_name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "score" float8 NOT NULL DEFAULT 0,
  "confidence" float8 NOT NULL DEFAULT 1,
  "details_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "answer_text" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "tokens_used" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_results
-- ----------------------------

-- ----------------------------
-- Table structure for eval_runs
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_runs";
CREATE TABLE "public"."eval_runs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "dataset_id" uuid NOT NULL,
  "target_kind" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'model'::character varying,
  "target_model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "target_pipeline" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "config_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'QUEUED'::character varying,
  "case_count" int4 NOT NULL DEFAULT 0,
  "completed_count" int4 NOT NULL DEFAULT 0,
  "failed_count" int4 NOT NULL DEFAULT 0,
  "started_at" timestamptz(6),
  "finished_at" timestamptz(6),
  "duration_ms" int4 NOT NULL DEFAULT 0,
  "total_cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "error_message" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_runs
-- ----------------------------

-- ----------------------------
-- Table structure for eval_test_cases
-- ----------------------------
DROP TABLE IF EXISTS "public"."eval_test_cases";
CREATE TABLE "public"."eval_test_cases" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "dataset_id" uuid NOT NULL,
  "question" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "ground_truth" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "context_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of eval_test_cases
-- ----------------------------

-- ----------------------------
-- Table structure for fs_areas
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_areas";
CREATE TABLE "public"."fs_areas" (
  "id" uuid NOT NULL,
  "zone_id" uuid NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "sort_id" int4 NOT NULL,
  "created_by" uuid,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_by" uuid,
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "version" int8 NOT NULL,
  "deleted_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of fs_areas
-- ----------------------------

-- ----------------------------
-- Table structure for fs_device_area
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_device_area";
CREATE TABLE "public"."fs_device_area" (
  "id" uuid NOT NULL,
  "area_id" uuid NOT NULL,
  "device_id" int4 NOT NULL,
  "device_sn" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "deleted_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of fs_device_area
-- ----------------------------

-- ----------------------------
-- Table structure for fs_groups
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_groups";
CREATE TABLE "public"."fs_groups" (
  "id" uuid NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "sort_id" int4 NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "created_by" uuid,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_by" uuid,
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "version" int8 NOT NULL,
  "deleted_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of fs_groups
-- ----------------------------

-- ----------------------------
-- Table structure for fs_schedule
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_schedule";
CREATE TABLE "public"."fs_schedule" (
  "id" uuid NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mode" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "status" int2 NOT NULL,
  "time_start" varchar(5) COLLATE "pg_catalog"."default" NOT NULL,
  "event_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "event_action" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "event" int2 NOT NULL,
  "sunday" int2 NOT NULL,
  "monday" int2 NOT NULL,
  "tuesday" int2 NOT NULL,
  "wednesday" int2 NOT NULL,
  "thursday" int2 NOT NULL,
  "friday" int2 NOT NULL,
  "saturday" int2 NOT NULL,
  "months" int4[] NOT NULL DEFAULT '{}'::integer[],
  "dates" int4[] NOT NULL DEFAULT '{}'::integer[],
  "cron_expr" varchar(100) COLLATE "pg_catalog"."default",
  "manual_trigger" bool NOT NULL,
  "last_run_at" timestamptz(6),
  "next_run_at" timestamptz(6),
  "run_count" int8 NOT NULL,
  "success_count" int8 NOT NULL,
  "failed_count" int8 NOT NULL,
  "created_by" uuid,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_by" uuid,
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "version" int8 NOT NULL,
  "deleted_at" timestamptz(6),
  "group_id" uuid,
  "zone_id" uuid,
  "area_id" uuid
)
;

-- ----------------------------
-- Records of fs_schedule
-- ----------------------------

-- ----------------------------
-- Table structure for fs_schedule_device
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_schedule_device";
CREATE TABLE "public"."fs_schedule_device" (
  "id" uuid NOT NULL,
  "schedule_id" uuid NOT NULL,
  "device_id" int4 NOT NULL,
  "device_sn" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "deleted_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of fs_schedule_device
-- ----------------------------

-- ----------------------------
-- Table structure for fs_schedule_history
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_schedule_history";
CREATE TABLE "public"."fs_schedule_history" (
  "id" uuid NOT NULL,
  "schedule_id" uuid NOT NULL,
  "device_id" int4,
  "triggered_by" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "trigger_source" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "event_action" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "payload" text COLLATE "pg_catalog"."default",
  "message" text COLLATE "pg_catalog"."default",
  "duration_ms" int8 NOT NULL,
  "retry_count" int4 NOT NULL,
  "executed_at" timestamptz(6),
  "timezone" varchar(50) COLLATE "pg_catalog"."default",
  "date" varchar(20) COLLATE "pg_catalog"."default",
  "time" varchar(20) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of fs_schedule_history
-- ----------------------------

-- ----------------------------
-- Table structure for fs_schedule_settings
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_schedule_settings";
CREATE TABLE "public"."fs_schedule_settings" (
  "id" uuid NOT NULL,
  "schedule_id" uuid NOT NULL,
  "key" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "value" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of fs_schedule_settings
-- ----------------------------

-- ----------------------------
-- Table structure for fs_zones
-- ----------------------------
DROP TABLE IF EXISTS "public"."fs_zones";
CREATE TABLE "public"."fs_zones" (
  "id" uuid NOT NULL,
  "group_id" uuid NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "sort_id" int4 NOT NULL,
  "created_by" uuid,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_by" uuid,
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "version" int8 NOT NULL,
  "deleted_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of fs_zones
-- ----------------------------

-- ----------------------------
-- Table structure for iot_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."iot_data";
CREATE TABLE "public"."iot_data" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('iot_data_id_seq'::regclass),
  "deviceId" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" jsonb NOT NULL,
  "timestamp" timestamptz(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "location" jsonb,
  "metadata" jsonb,
  "dataType" varchar(20) COLLATE "pg_catalog"."default",
  "dataQuality" float8,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of iot_data
-- ----------------------------

-- ----------------------------
-- Table structure for lc_agents
-- ----------------------------
DROP TABLE IF EXISTS "public"."lc_agents";
CREATE TABLE "public"."lc_agents" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "agent_type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'react'::character varying,
  "tools_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'gpt-4o-mini'::character varying,
  "max_iterations" int4 NOT NULL DEFAULT 10,
  "config_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of lc_agents
-- ----------------------------
INSERT INTO "public"."lc_agents" VALUES ('0dd670f2-73b8-48ca-a09e-20f8d272eac7', '00000000-0000-0000-0000-000000000001', 'default_react', 'react', '[]', 'gpt-4o-mini', 10, '{"system_prompt":"You are a helpful agent."}', 't', '2026-09-28 13:30:18.780721+00', '2026-09-28 13:30:18.780721+00');

-- ----------------------------
-- Table structure for lc_chains
-- ----------------------------
DROP TABLE IF EXISTS "public"."lc_chains";
CREATE TABLE "public"."lc_chains" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "chain_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'lcel'::character varying,
  "config_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '1.0.0'::character varying,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of lc_chains
-- ----------------------------
INSERT INTO "public"."lc_chains" VALUES ('cca41c68-b87f-4145-ad46-8d48ea369a48', '00000000-0000-0000-0000-000000000001', 'default_lcel', 'lcel', '{"model":"gpt-4o-mini"}', '1.0.0', 't', '2026-09-28 13:30:18.780721+00', '2026-09-28 13:30:18.780721+00');
INSERT INTO "public"."lc_chains" VALUES ('33d965f8-e134-41ac-ad8a-64c58ec5c5f2', '00000000-0000-0000-0000-000000000001', 'sequential_qa', 'sequential', '{"model":"gpt-4o-mini","steps":["retrieve","generate"]}', '1.0.0', 't', '2026-09-28 13:30:18.780721+00', '2026-09-28 13:30:18.780721+00');

-- ----------------------------
-- Table structure for lc_memories
-- ----------------------------
DROP TABLE IF EXISTS "public"."lc_memories";
CREATE TABLE "public"."lc_memories" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "conversation_id" uuid NOT NULL,
  "memory_type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'buffer'::character varying,
  "snapshot_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "size_bytes" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of lc_memories
-- ----------------------------

-- ----------------------------
-- Table structure for lc_runs
-- ----------------------------
DROP TABLE IF EXISTS "public"."lc_runs";
CREATE TABLE "public"."lc_runs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "kind" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'chain'::character varying,
  "target_id" uuid NOT NULL,
  "input_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "output_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'QUEUED'::character varying,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "tokens_used" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "error_message" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of lc_runs
-- ----------------------------

-- ----------------------------
-- Table structure for lc_traces
-- ----------------------------
DROP TABLE IF EXISTS "public"."lc_traces";
CREATE TABLE "public"."lc_traces" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "run_id" uuid NOT NULL,
  "step" int4 NOT NULL DEFAULT 0,
  "kind" varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'other'::character varying,
  "payload_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of lc_traces
-- ----------------------------

-- ----------------------------
-- Table structure for llm_conversations
-- ----------------------------
DROP TABLE IF EXISTS "public"."llm_conversations";
CREATE TABLE "public"."llm_conversations" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "title" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "model_id" uuid NOT NULL,
  "system_prompt" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'ACTIVE'::character varying,
  "message_count" int4 NOT NULL DEFAULT 0,
  "total_tokens" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of llm_conversations
-- ----------------------------
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000001', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', 'Chat session #001', '22222222-2222-2222-2222-000000000001', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "c4ca4238a0b9"}', 'ACTIVE', 0, 0, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000002', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', 'Chat session #002', '22222222-2222-2222-2222-000000000002', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "c81e728d9d4c"}', 'ACTIVE', 7, 1379, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000003', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', 'Chat session #003', '22222222-2222-2222-2222-000000000003', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "eccbc87e4b5c"}', 'ACTIVE', 14, 2758, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000004', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', 'Chat session #004', '22222222-2222-2222-2222-000000000004', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "a87ff679a2f3"}', 'ACTIVE', 21, 4137, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000005', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', 'Chat session #005', '22222222-2222-2222-2222-000000000005', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "e4da3b7fbbce"}', 'ACTIVE', 28, 5516, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000006', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', 'Chat session #006', '22222222-2222-2222-2222-000000000006', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "1679091c5a88"}', 'ACTIVE', 35, 6895, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000007', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', 'Chat session #007', '22222222-2222-2222-2222-000000000007', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "8f14e45fceea"}', 'ACTIVE', 42, 8274, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000008', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', 'Chat session #008', '22222222-2222-2222-2222-000000000008', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "c9f0f895fb98"}', 'ARCHIVED', 49, 9653, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000009', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', 'Chat session #009', '22222222-2222-2222-2222-000000000009', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "45c48cce2e2d"}', 'ARCHIVED', 5, 11032, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000010', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', 'Chat session #010', '22222222-2222-2222-2222-000000000010', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "d3d9446802a4"}', 'DELETED', 12, 12411, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000011', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', 'Chat session #011', '22222222-2222-2222-2222-000000000011', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "6512bd43d9ca"}', 'ACTIVE', 19, 13790, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000012', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', 'Chat session #012', '22222222-2222-2222-2222-000000000012', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "c20ad4d76fe9"}', 'ACTIVE', 26, 15169, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000013', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', 'Chat session #013', '22222222-2222-2222-2222-000000000013', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "c51ce410c124"}', 'ACTIVE', 33, 16548, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000014', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', 'Chat session #014', '22222222-2222-2222-2222-000000000014', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "aab3238922bc"}', 'ACTIVE', 40, 17927, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000015', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', 'Chat session #015', '22222222-2222-2222-2222-000000000015', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "9bf31c7ff062"}', 'ACTIVE', 47, 19306, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000016', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', 'Chat session #016', '22222222-2222-2222-2222-000000000016', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "c74d97b01eae"}', 'ACTIVE', 3, 20685, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000017', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', 'Chat session #017', '22222222-2222-2222-2222-000000000017', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "70efdf2ec9b0"}', 'ACTIVE', 10, 22064, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000018', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', 'Chat session #018', '22222222-2222-2222-2222-000000000018', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "6f4922f45568"}', 'ARCHIVED', 17, 23443, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000019', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', 'Chat session #019', '22222222-2222-2222-2222-000000000019', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "1f0e3dad9990"}', 'ARCHIVED', 24, 24822, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000020', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', 'Chat session #020', '22222222-2222-2222-2222-000000000020', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "98f137082101"}', 'DELETED', 31, 26201, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000021', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', 'Chat session #021', '22222222-2222-2222-2222-000000000021', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "3c59dc048e88"}', 'ACTIVE', 38, 27580, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000022', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', 'Chat session #022', '22222222-2222-2222-2222-000000000022', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "b6d767d2f8ed"}', 'ACTIVE', 45, 28959, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000023', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', 'Chat session #023', '22222222-2222-2222-2222-000000000023', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "37693cfc7480"}', 'ACTIVE', 1, 30338, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000024', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', 'Chat session #024', '22222222-2222-2222-2222-000000000024', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "1ff1de774005"}', 'ACTIVE', 8, 31717, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000025', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', 'Chat session #025', '22222222-2222-2222-2222-000000000025', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "8e296a067a37"}', 'ACTIVE', 15, 33096, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000026', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', 'Chat session #026', '22222222-2222-2222-2222-000000000026', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "4e732ced3463"}', 'ACTIVE', 22, 34475, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000027', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', 'Chat session #027', '22222222-2222-2222-2222-000000000027', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "02e74f10e032"}', 'ACTIVE', 29, 35854, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000028', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', 'Chat session #028', '22222222-2222-2222-2222-000000000028', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "33e75ff09dd6"}', 'ARCHIVED', 36, 37233, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000029', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', 'Chat session #029', '22222222-2222-2222-2222-000000000029', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "6ea9ab1baa0e"}', 'ARCHIVED', 43, 38612, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000030', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', 'Chat session #030', '22222222-2222-2222-2222-000000000030', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "34173cb38f07"}', 'DELETED', 50, 39991, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000031', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', 'Chat session #031', '22222222-2222-2222-2222-000000000031', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "c16a5320fa47"}', 'ACTIVE', 6, 41370, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000032', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', 'Chat session #032', '22222222-2222-2222-2222-000000000032', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "6364d3f0f495"}', 'ACTIVE', 13, 42749, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000033', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', 'Chat session #033', '22222222-2222-2222-2222-000000000033', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "182be0c5cdcd"}', 'ACTIVE', 20, 44128, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000034', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', 'Chat session #034', '22222222-2222-2222-2222-000000000034', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "e369853df766"}', 'ACTIVE', 27, 45507, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000035', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', 'Chat session #035', '22222222-2222-2222-2222-000000000035', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "1c383cd30b7c"}', 'ACTIVE', 34, 46886, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000036', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', 'Chat session #036', '22222222-2222-2222-2222-000000000036', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "19ca14e7ea63"}', 'ACTIVE', 41, 48265, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000037', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', 'Chat session #037', '22222222-2222-2222-2222-000000000037', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "a5bfc9e07964"}', 'ACTIVE', 48, 49644, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000038', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', 'Chat session #038', '22222222-2222-2222-2222-000000000038', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "a5771bce93e2"}', 'ARCHIVED', 4, 51023, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000039', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', 'Chat session #039', '22222222-2222-2222-2222-000000000039', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "d67d8ab4f4c1"}', 'ARCHIVED', 11, 52402, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000040', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', 'Chat session #040', '22222222-2222-2222-2222-000000000040', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "d645920e395f"}', 'DELETED', 18, 53781, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000041', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', 'Chat session #041', '22222222-2222-2222-2222-000000000041', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "3416a75f4cea"}', 'ACTIVE', 25, 55160, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000042', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', 'Chat session #042', '22222222-2222-2222-2222-000000000042', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "a1d0c6e83f02"}', 'ACTIVE', 32, 56539, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000043', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', 'Chat session #043', '22222222-2222-2222-2222-000000000043', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "17e62166fc85"}', 'ACTIVE', 39, 57918, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000044', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', 'Chat session #044', '22222222-2222-2222-2222-000000000044', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "f7177163c833"}', 'ACTIVE', 46, 59297, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000045', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', 'Chat session #045', '22222222-2222-2222-2222-000000000045', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "6c8349cc7260"}', 'ACTIVE', 2, 60676, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000046', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', 'Chat session #046', '22222222-2222-2222-2222-000000000046', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "d9d4f495e875"}', 'ACTIVE', 9, 62055, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000047', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', 'Chat session #047', '22222222-2222-2222-2222-000000000047', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "67c6a1e7ce56"}', 'ACTIVE', 16, 63434, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000048', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', 'Chat session #048', '22222222-2222-2222-2222-000000000048', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "642e92efb794"}', 'ARCHIVED', 23, 64813, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000049', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', 'Chat session #049', '22222222-2222-2222-2222-000000000049', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "f457c545a9de"}', 'ARCHIVED', 30, 66192, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000050', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', 'Chat session #050', '22222222-2222-2222-2222-000000000050', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "c0c7c76d30bd"}', 'DELETED', 37, 67571, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000051', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', 'Chat session #051', '22222222-2222-2222-2222-000000000051', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "2838023a778d"}', 'ACTIVE', 44, 68950, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000052', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', 'Chat session #052', '22222222-2222-2222-2222-000000000052', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "9a1158154dfa"}', 'ACTIVE', 0, 70329, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000053', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', 'Chat session #053', '22222222-2222-2222-2222-000000000053', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "d82c8d1619ad"}', 'ACTIVE', 7, 71708, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000054', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', 'Chat session #054', '22222222-2222-2222-2222-000000000054', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "a684eceee76f"}', 'ACTIVE', 14, 73087, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000055', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', 'Chat session #055', '22222222-2222-2222-2222-000000000055', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "b53b3a3d6ab9"}', 'ACTIVE', 21, 74466, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000056', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', 'Chat session #056', '22222222-2222-2222-2222-000000000056', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "9f61408e3afb"}', 'ACTIVE', 28, 75845, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000057', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', 'Chat session #057', '22222222-2222-2222-2222-000000000057', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "72b32a1f754b"}', 'ACTIVE', 35, 77224, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000058', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', 'Chat session #058', '22222222-2222-2222-2222-000000000058', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "66f041e16a60"}', 'ARCHIVED', 42, 78603, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000059', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', 'Chat session #059', '22222222-2222-2222-2222-000000000059', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "093f65e080a2"}', 'ARCHIVED', 49, 79982, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000060', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', 'Chat session #060', '22222222-2222-2222-2222-000000000060', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "072b030ba126"}', 'DELETED', 5, 81361, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000061', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', 'Chat session #061', '22222222-2222-2222-2222-000000000061', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "7f39f8317fbd"}', 'ACTIVE', 12, 82740, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000062', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', 'Chat session #062', '22222222-2222-2222-2222-000000000062', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "44f683a84163"}', 'ACTIVE', 19, 84119, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000063', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', 'Chat session #063', '22222222-2222-2222-2222-000000000063', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "03afdbd66e79"}', 'ACTIVE', 26, 85498, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000064', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', 'Chat session #064', '22222222-2222-2222-2222-000000000064', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "ea5d2f1c4608"}', 'ACTIVE', 33, 86877, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000065', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', 'Chat session #065', '22222222-2222-2222-2222-000000000065', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "fc490ca45c00"}', 'ACTIVE', 40, 88256, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000066', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', 'Chat session #066', '22222222-2222-2222-2222-000000000066', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "3295c76acbf4"}', 'ACTIVE', 47, 89635, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000067', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', 'Chat session #067', '22222222-2222-2222-2222-000000000067', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "735b90b45681"}', 'ACTIVE', 3, 91014, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000068', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', 'Chat session #068', '22222222-2222-2222-2222-000000000068', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "a3f390d88e4c"}', 'ARCHIVED', 10, 92393, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000069', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', 'Chat session #069', '22222222-2222-2222-2222-000000000069', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "14bfa6bb1487"}', 'ARCHIVED', 17, 93772, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000070', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', 'Chat session #070', '22222222-2222-2222-2222-000000000070', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "7cbbc409ec99"}', 'DELETED', 24, 95151, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000071', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', 'Chat session #071', '22222222-2222-2222-2222-000000000071', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "e2c420d928d4"}', 'ACTIVE', 31, 96530, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000072', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', 'Chat session #072', '22222222-2222-2222-2222-000000000072', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "32bb90e8976a"}', 'ACTIVE', 38, 97909, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000073', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', 'Chat session #073', '22222222-2222-2222-2222-000000000073', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "d2ddea18f006"}', 'ACTIVE', 45, 99288, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000074', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', 'Chat session #074', '22222222-2222-2222-2222-000000000074', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "ad61ab143223"}', 'ACTIVE', 1, 667, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000075', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', 'Chat session #075', '22222222-2222-2222-2222-000000000075', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "d09bf41544a3"}', 'ACTIVE', 8, 2046, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000076', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', 'Chat session #076', '22222222-2222-2222-2222-000000000076', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "fbd7939d6749"}', 'ACTIVE', 15, 3425, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000077', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', 'Chat session #077', '22222222-2222-2222-2222-000000000077', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "28dd2c7955ce"}', 'ACTIVE', 22, 4804, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000078', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', 'Chat session #078', '22222222-2222-2222-2222-000000000078', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "35f4a8d465e6"}', 'ARCHIVED', 29, 6183, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000079', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', 'Chat session #079', '22222222-2222-2222-2222-000000000079', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "d1fe173d08e9"}', 'ARCHIVED', 36, 7562, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000080', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', 'Chat session #080', '22222222-2222-2222-2222-000000000080', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "f033ab37c302"}', 'DELETED', 43, 8941, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000081', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', 'Chat session #081', '22222222-2222-2222-2222-000000000081', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "43ec517d68b6"}', 'ACTIVE', 50, 10320, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000082', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', 'Chat session #082', '22222222-2222-2222-2222-000000000082', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "9778d5d219c5"}', 'ACTIVE', 6, 11699, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000083', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', 'Chat session #083', '22222222-2222-2222-2222-000000000083', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "fe9fc289c3ff"}', 'ACTIVE', 13, 13078, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000084', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', 'Chat session #084', '22222222-2222-2222-2222-000000000084', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "68d30a959472"}', 'ACTIVE', 20, 14457, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000085', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', 'Chat session #085', '22222222-2222-2222-2222-000000000085', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "3ef815416f77"}', 'ACTIVE', 27, 15836, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000086', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', 'Chat session #086', '22222222-2222-2222-2222-000000000086', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "93db85ed909c"}', 'ACTIVE', 34, 17215, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000087', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', 'Chat session #087', '22222222-2222-2222-2222-000000000087', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "c7e1249ffc03"}', 'ACTIVE', 41, 18594, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000088', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', 'Chat session #088', '22222222-2222-2222-2222-000000000088', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "2a38a4a9316c"}', 'ARCHIVED', 48, 19973, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000089', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', 'Chat session #089', '22222222-2222-2222-2222-000000000089', 'You are a Thai language expert.', '{"channel" : "web", "lang" : "en", "ip_hash" : "7647966b7343"}', 'ARCHIVED', 4, 21352, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000090', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', 'Chat session #090', '22222222-2222-2222-2222-000000000090', '', '{"channel" : "mobile", "lang" : "mixed", "ip_hash" : "8613985ec49e"}', 'DELETED', 11, 22731, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000091', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', 'Chat session #091', '22222222-2222-2222-2222-000000000091', 'You are a helpful assistant.', '{"channel" : "api", "lang" : "th", "ip_hash" : "54229abfcfa5"}', 'ACTIVE', 18, 24110, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000092', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', 'Chat session #092', '22222222-2222-2222-2222-000000000092', 'You are a Thai language expert.', '{"channel" : "slack", "lang" : "en", "ip_hash" : "92cc227532d1"}', 'ACTIVE', 25, 25489, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000093', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', 'Chat session #093', '22222222-2222-2222-2222-000000000093', '', '{"channel" : "web", "lang" : "mixed", "ip_hash" : "98dce83da57b"}', 'ACTIVE', 32, 26868, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000094', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', 'Chat session #094', '22222222-2222-2222-2222-000000000094', 'You are a helpful assistant.', '{"channel" : "mobile", "lang" : "th", "ip_hash" : "f4b9ec30ad9f"}', 'ACTIVE', 39, 28247, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000095', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', 'Chat session #095', '22222222-2222-2222-2222-000000000095', 'You are a Thai language expert.', '{"channel" : "api", "lang" : "en", "ip_hash" : "812b4ba287f5"}', 'ACTIVE', 46, 29626, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000096', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', 'Chat session #096', '22222222-2222-2222-2222-000000000096', '', '{"channel" : "slack", "lang" : "mixed", "ip_hash" : "26657d5ff902"}', 'ACTIVE', 2, 31005, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000097', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', 'Chat session #097', '22222222-2222-2222-2222-000000000097', 'You are a helpful assistant.', '{"channel" : "web", "lang" : "th", "ip_hash" : "e2ef524fbf3d"}', 'ACTIVE', 9, 32384, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000098', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', 'Chat session #098', '22222222-2222-2222-2222-000000000098', 'You are a Thai language expert.', '{"channel" : "mobile", "lang" : "en", "ip_hash" : "ed3d2c21991e"}', 'ARCHIVED', 16, 33763, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000099', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', 'Chat session #099', '22222222-2222-2222-2222-000000000099', '', '{"channel" : "api", "lang" : "mixed", "ip_hash" : "ac627ab1ccbd"}', 'ARCHIVED', 23, 35142, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_conversations" VALUES ('33333333-3333-3333-3333-000000000100', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', 'Chat session #100', '22222222-2222-2222-2222-000000000100', 'You are a helpful assistant.', '{"channel" : "slack", "lang" : "th", "ip_hash" : "f899139df5e1"}', 'DELETED', 30, 36521, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');

-- ----------------------------
-- Table structure for llm_messages
-- ----------------------------
DROP TABLE IF EXISTS "public"."llm_messages";
CREATE TABLE "public"."llm_messages" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "conversation_id" uuid NOT NULL,
  "role" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "tool_calls_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "tool_call_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "tokens_input" int4 NOT NULL DEFAULT 0,
  "tokens_output" int4 NOT NULL DEFAULT 0,
  "finish_reason" varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of llm_messages
-- ----------------------------
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000001', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000001', 'system', 'You are a helpful assistant.', '[]', '', 0, 0, 'stop', 100, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000002', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000002', 'user', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', '', 37, 53, 'stop', 197, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000003', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000003', 'assistant', 'Hello! How can I help you today?', '[]', '', 74, 106, 'stop', 294, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000004', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000004', 'tool', 'Sure! Let me break this down for you.', '[]', 'call_000004', 111, 159, 'stop', 391, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000005', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000005', 'system', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 148, 212, 'stop', 488, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000006', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000006', 'user', 'Here is the summary you requested.', '[]', '', 185, 265, 'stop', 585, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000007', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000007', 'assistant', '{"result": "success", "value": 42}', '[]', '', 222, 318, 'stop', 682, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000008', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000008', 'tool', 'What is the weather like today?', '[]', 'call_000008', 259, 371, 'stop', 779, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000009', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000009', 'system', 'The weather is sunny with a high of 32°C.', '[]', '', 296, 424, 'length', 876, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000010', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000010', 'user', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', '', 333, 477, 'tool_calls', 973, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000011', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000011', 'assistant', 'You are a helpful assistant.', '[]', '', 370, 530, 'stop', 1070, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000012', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000012', 'tool', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', 'call_000012', 407, 583, 'stop', 1167, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000013', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000013', 'system', 'Hello! How can I help you today?', '[]', '', 444, 636, 'stop', 1264, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000014', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000014', 'user', 'Sure! Let me break this down for you.', '[]', '', 481, 689, 'stop', 1361, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000015', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000015', 'assistant', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 518, 742, 'stop', 1458, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000016', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000016', 'tool', 'Here is the summary you requested.', '[]', 'call_000016', 555, 795, 'stop', 1555, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000017', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000017', 'system', '{"result": "success", "value": 42}', '[]', '', 592, 848, 'stop', 1652, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000018', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000018', 'user', 'What is the weather like today?', '[]', '', 629, 901, 'stop', 1749, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000019', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000019', 'assistant', 'The weather is sunny with a high of 32°C.', '[]', '', 666, 954, 'length', 1846, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000020', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000020', 'tool', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', 'call_000020', 703, 1007, 'tool_calls', 1943, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000021', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000021', 'system', 'You are a helpful assistant.', '[]', '', 740, 1060, 'stop', 2040, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000022', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000022', 'user', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', '', 777, 1113, 'stop', 2137, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000023', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000023', 'assistant', 'Hello! How can I help you today?', '[]', '', 814, 1166, 'stop', 2234, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000024', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000024', 'tool', 'Sure! Let me break this down for you.', '[]', 'call_000024', 851, 1219, 'stop', 2331, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000025', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000025', 'system', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 888, 1272, 'stop', 2428, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000026', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000026', 'user', 'Here is the summary you requested.', '[]', '', 925, 1325, 'stop', 2525, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000027', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000027', 'assistant', '{"result": "success", "value": 42}', '[]', '', 962, 1378, 'stop', 2622, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000028', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000028', 'tool', 'What is the weather like today?', '[]', 'call_000028', 999, 1431, 'stop', 2719, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000029', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000029', 'system', 'The weather is sunny with a high of 32°C.', '[]', '', 1036, 1484, 'length', 2816, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000030', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000030', 'user', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', '', 1073, 1537, 'tool_calls', 2913, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000031', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000031', 'assistant', 'You are a helpful assistant.', '[]', '', 1110, 1590, 'stop', 3010, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000032', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000032', 'tool', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', 'call_000032', 1147, 1643, 'stop', 3107, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000033', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000033', 'system', 'Hello! How can I help you today?', '[]', '', 1184, 1696, 'stop', 3204, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000034', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000034', 'user', 'Sure! Let me break this down for you.', '[]', '', 1221, 1749, 'stop', 3301, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000035', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000035', 'assistant', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 1258, 1802, 'stop', 3398, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000036', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000036', 'tool', 'Here is the summary you requested.', '[]', 'call_000036', 1295, 1855, 'stop', 3495, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000037', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000037', 'system', '{"result": "success", "value": 42}', '[]', '', 1332, 1908, 'stop', 3592, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000038', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000038', 'user', 'What is the weather like today?', '[]', '', 1369, 1961, 'stop', 3689, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000039', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000039', 'assistant', 'The weather is sunny with a high of 32°C.', '[]', '', 1406, 2014, 'length', 3786, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000040', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000040', 'tool', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', 'call_000040', 1443, 2067, 'tool_calls', 3883, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000041', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000041', 'system', 'You are a helpful assistant.', '[]', '', 1480, 2120, 'stop', 3980, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000042', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000042', 'user', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', '', 1517, 2173, 'stop', 4077, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000043', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000043', 'assistant', 'Hello! How can I help you today?', '[]', '', 1554, 2226, 'stop', 4174, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000044', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000044', 'tool', 'Sure! Let me break this down for you.', '[]', 'call_000044', 1591, 2279, 'stop', 4271, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000045', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000045', 'system', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 1628, 2332, 'stop', 4368, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000046', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000046', 'user', 'Here is the summary you requested.', '[]', '', 1665, 2385, 'stop', 4465, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000047', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000047', 'assistant', '{"result": "success", "value": 42}', '[]', '', 1702, 2438, 'stop', 4562, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000048', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000048', 'tool', 'What is the weather like today?', '[]', 'call_000048', 1739, 2491, 'stop', 4659, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000049', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000049', 'system', 'The weather is sunny with a high of 32°C.', '[]', '', 1776, 2544, 'length', 4756, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000050', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000050', 'user', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', '', 1813, 2597, 'tool_calls', 4853, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000051', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000051', 'assistant', 'You are a helpful assistant.', '[]', '', 1850, 2650, 'stop', 4950, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000052', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000052', 'tool', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', 'call_000052', 1887, 2703, 'stop', 147, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000053', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000053', 'system', 'Hello! How can I help you today?', '[]', '', 1924, 2756, 'stop', 244, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000054', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000054', 'user', 'Sure! Let me break this down for you.', '[]', '', 1961, 2809, 'stop', 341, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000055', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000055', 'assistant', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 1998, 2862, 'stop', 438, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000056', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000056', 'tool', 'Here is the summary you requested.', '[]', 'call_000056', 2035, 2915, 'stop', 535, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000057', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000057', 'system', '{"result": "success", "value": 42}', '[]', '', 2072, 2968, 'stop', 632, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000058', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000058', 'user', 'What is the weather like today?', '[]', '', 2109, 3021, 'stop', 729, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000059', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000059', 'assistant', 'The weather is sunny with a high of 32°C.', '[]', '', 2146, 3074, 'length', 826, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000060', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000060', 'tool', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', 'call_000060', 2183, 3127, 'tool_calls', 923, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000061', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000061', 'system', 'You are a helpful assistant.', '[]', '', 2220, 3180, 'stop', 1020, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000062', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000062', 'user', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', '', 2257, 3233, 'stop', 1117, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000063', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000063', 'assistant', 'Hello! How can I help you today?', '[]', '', 2294, 3286, 'stop', 1214, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000064', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000064', 'tool', 'Sure! Let me break this down for you.', '[]', 'call_000064', 2331, 3339, 'stop', 1311, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000065', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000065', 'system', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 2368, 3392, 'stop', 1408, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000066', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000066', 'user', 'Here is the summary you requested.', '[]', '', 2405, 3445, 'stop', 1505, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000067', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000067', 'assistant', '{"result": "success", "value": 42}', '[]', '', 2442, 3498, 'stop', 1602, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000068', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000068', 'tool', 'What is the weather like today?', '[]', 'call_000068', 2479, 3551, 'stop', 1699, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000069', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000069', 'system', 'The weather is sunny with a high of 32°C.', '[]', '', 2516, 3604, 'length', 1796, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000070', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000070', 'user', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', '', 2553, 3657, 'tool_calls', 1893, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000071', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000071', 'assistant', 'You are a helpful assistant.', '[]', '', 2590, 3710, 'stop', 1990, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000072', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000072', 'tool', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', 'call_000072', 2627, 3763, 'stop', 2087, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000073', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000073', 'system', 'Hello! How can I help you today?', '[]', '', 2664, 3816, 'stop', 2184, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000074', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000074', 'user', 'Sure! Let me break this down for you.', '[]', '', 2701, 3869, 'stop', 2281, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000075', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000075', 'assistant', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 2738, 3922, 'stop', 2378, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000076', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000076', 'tool', 'Here is the summary you requested.', '[]', 'call_000076', 2775, 3975, 'stop', 2475, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000077', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000077', 'system', '{"result": "success", "value": 42}', '[]', '', 2812, 4028, 'stop', 2572, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000078', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000078', 'user', 'What is the weather like today?', '[]', '', 2849, 4081, 'stop', 2669, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000079', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000079', 'assistant', 'The weather is sunny with a high of 32°C.', '[]', '', 2886, 4134, 'length', 2766, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000080', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000080', 'tool', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', 'call_000080', 2923, 4187, 'tool_calls', 2863, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000081', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000081', 'system', 'You are a helpful assistant.', '[]', '', 2960, 4240, 'stop', 2960, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000082', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000082', 'user', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', '', 2997, 4293, 'stop', 3057, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000083', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000083', 'assistant', 'Hello! How can I help you today?', '[]', '', 3034, 4346, 'stop', 3154, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000084', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000084', 'tool', 'Sure! Let me break this down for you.', '[]', 'call_000084', 3071, 4399, 'stop', 3251, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000085', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000085', 'system', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 3108, 4452, 'stop', 3348, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000086', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000086', 'user', 'Here is the summary you requested.', '[]', '', 3145, 4505, 'stop', 3445, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000087', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000087', 'assistant', '{"result": "success", "value": 42}', '[]', '', 3182, 4558, 'stop', 3542, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000088', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000088', 'tool', 'What is the weather like today?', '[]', 'call_000088', 3219, 4611, 'stop', 3639, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000089', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000089', 'system', 'The weather is sunny with a high of 32°C.', '[]', '', 3256, 4664, 'length', 3736, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000090', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000090', 'user', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', '', 3293, 4717, 'tool_calls', 3833, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000091', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000091', 'assistant', 'You are a helpful assistant.', '[]', '', 3330, 4770, 'stop', 3930, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000092', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000092', 'tool', 'สวัสดีครับ ช่วยอธิบายเรื่อง AI ให้ฟังหน่อย', '[]', 'call_000092', 3367, 4823, 'stop', 4027, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000093', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000093', 'system', 'Hello! How can I help you today?', '[]', '', 3404, 4876, 'stop', 4124, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000094', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000094', 'user', 'Sure! Let me break this down for you.', '[]', '', 3441, 4929, 'stop', 4221, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000095', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000095', 'assistant', 'กรุณาสรุปข้อมูลให้หน่อยครับ', '[]', '', 3478, 4982, 'stop', 4318, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000096', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000096', 'tool', 'Here is the summary you requested.', '[]', 'call_000096', 3515, 5035, 'stop', 4415, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000097', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000097', 'system', '{"result": "success", "value": 42}', '[]', '', 3552, 5088, 'stop', 4512, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000098', '00000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-000000000098', 'user', 'What is the weather like today?', '[]', '', 3589, 5141, 'stop', 4609, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000099', '00000000-0000-0000-0000-000000000003', '33333333-3333-3333-3333-000000000099', 'assistant', 'The weather is sunny with a high of 32°C.', '[]', '', 3626, 5194, 'length', 4706, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_messages" VALUES ('55555555-5555-5555-5555-000000000100', '00000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-000000000100', 'tool', 'ช่วยเขียนโค้ด Python สำหรับอ่าน CSV ให้หน่อย', '[]', 'call_000100', 3663, 5247, 'tool_calls', 4803, '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');

-- ----------------------------
-- Table structure for llm_models
-- ----------------------------
DROP TABLE IF EXISTS "public"."llm_models";
CREATE TABLE "public"."llm_models" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "provider_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "display_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "context_window" int4 NOT NULL DEFAULT 4096,
  "max_output_tokens" int4 NOT NULL DEFAULT 4096,
  "cost_per_1k_input" numeric(12,8) NOT NULL DEFAULT 0,
  "cost_per_1k_output" numeric(12,8) NOT NULL DEFAULT 0,
  "supports_streaming" bool NOT NULL DEFAULT true,
  "supports_tools" bool NOT NULL DEFAULT false,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of llm_models
-- ----------------------------
INSERT INTO "public"."llm_models" VALUES ('36ecfeab-fb47-4b84-8b70-2c5658d3f4eb', '00000000-0000-0000-0000-000000000001', '51a929e6-8f99-47d9-86c2-11da1d90d3b5', 'gpt-4o-mini', 'GPT-4o Mini', 128000, 16384, 0.00015000, 0.00060000, 't', 't', 't', '2026-09-28 13:30:47.439749+00', '2026-09-28 13:30:47.439749+00');
INSERT INTO "public"."llm_models" VALUES ('ab4cacfc-d3e9-4af6-93db-296364237597', '00000000-0000-0000-0000-000000000001', '40a0d742-b61f-45ad-8cd6-f67bca6d42e0', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 200000, 8192, 0.00300000, 0.01500000, 't', 't', 't', '2026-09-28 13:30:47.439749+00', '2026-09-28 13:30:47.439749+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000001', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000001', 'gpt-4o-mini-v001', 'GPT-4o Mini #001', 4096, 1024, 0.00015000, 0.00060000, 'f', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000002', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000002', 'gpt-4o-v002', 'GPT-4o #002', 8192, 2048, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000003', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000003', 'gpt-4-turbo-v003', 'GPT-4 Turbo #003', 16384, 4096, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000004', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000004', 'gpt-3.5-turbo-v004', 'GPT-3.5 Turbo #004', 32768, 8192, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000005', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000005', 'claude-3-5-sonnet-20241022-v005', 'Claude 3.5 Sonnet #005', 128000, 16384, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000006', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000006', 'claude-3-opus-20240229-v006', 'Claude 3 Opus #006', 200000, 1024, 0.01000000, 0.05000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000007', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000007', 'claude-3-haiku-20240307-v007', 'Claude 3 Haiku #007', 4096, 2048, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000008', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000008', 'llama-3.1-8b-v008', 'Llama 3.1 8B #008', 8192, 4096, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000009', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000009', 'llama-3.1-70b-v009', 'Llama 3.1 70B #009', 16384, 8192, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000010', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000010', 'mistral-7b-v010', 'Mistral 7B #010', 32768, 16384, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000011', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000011', 'gemini-1.5-pro-v011', 'Gemini 1.5 Pro #011', 128000, 1024, 0.00500000, 0.03000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000012', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000012', 'gemini-1.5-flash-v012', 'Gemini 1.5 Flash #012', 200000, 2048, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000013', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000013', 'gpt-4o-mini-v013', 'GPT-4o Mini #013', 4096, 4096, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000014', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000014', 'gpt-4o-v014', 'GPT-4o #014', 8192, 8192, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000015', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000015', 'gpt-4-turbo-v015', 'GPT-4 Turbo #015', 16384, 16384, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000016', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000016', 'gpt-3.5-turbo-v016', 'GPT-3.5 Turbo #016', 32768, 1024, 0.00300000, 0.01500000, 'f', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000017', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000017', 'claude-3-5-sonnet-20241022-v017', 'Claude 3.5 Sonnet #017', 128000, 2048, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000018', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000018', 'claude-3-opus-20240229-v018', 'Claude 3 Opus #018', 200000, 4096, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000019', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000019', 'claude-3-haiku-20240307-v019', 'Claude 3 Haiku #019', 4096, 8192, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000020', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000020', 'llama-3.1-8b-v020', 'Llama 3.1 8B #020', 8192, 16384, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000021', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000021', 'llama-3.1-70b-v021', 'Llama 3.1 70B #021', 16384, 1024, 0.00100000, 0.00300000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000022', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000022', 'mistral-7b-v022', 'Mistral 7B #022', 32768, 2048, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000023', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000023', 'gemini-1.5-pro-v023', 'Gemini 1.5 Pro #023', 128000, 4096, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000024', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000024', 'gemini-1.5-flash-v024', 'Gemini 1.5 Flash #024', 200000, 8192, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000025', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000025', 'gpt-4o-mini-v025', 'GPT-4o Mini #025', 4096, 16384, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000026', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000026', 'gpt-4o-v026', 'GPT-4o #026', 8192, 1024, 0.00050000, 0.00150000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000027', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000027', 'gpt-4-turbo-v027', 'GPT-4 Turbo #027', 16384, 2048, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000028', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000028', 'gpt-3.5-turbo-v028', 'GPT-3.5 Turbo #028', 32768, 4096, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000029', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000029', 'claude-3-5-sonnet-20241022-v029', 'Claude 3.5 Sonnet #029', 128000, 8192, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000030', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000030', 'claude-3-opus-20240229-v030', 'Claude 3 Opus #030', 200000, 16384, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000031', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000031', 'claude-3-haiku-20240307-v031', 'Claude 3 Haiku #031', 4096, 1024, 0.00015000, 0.00060000, 'f', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000032', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000032', 'llama-3.1-8b-v032', 'Llama 3.1 8B #032', 8192, 2048, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000033', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000033', 'llama-3.1-70b-v033', 'Llama 3.1 70B #033', 16384, 4096, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000034', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000034', 'mistral-7b-v034', 'Mistral 7B #034', 32768, 8192, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000035', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000035', 'gemini-1.5-pro-v035', 'Gemini 1.5 Pro #035', 128000, 16384, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000036', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000036', 'gemini-1.5-flash-v036', 'Gemini 1.5 Flash #036', 200000, 1024, 0.01000000, 0.05000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000037', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000037', 'gpt-4o-mini-v037', 'GPT-4o Mini #037', 4096, 2048, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000038', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000038', 'gpt-4o-v038', 'GPT-4o #038', 8192, 4096, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000039', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000039', 'gpt-4-turbo-v039', 'GPT-4 Turbo #039', 16384, 8192, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000040', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000040', 'gpt-3.5-turbo-v040', 'GPT-3.5 Turbo #040', 32768, 16384, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000041', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000041', 'claude-3-5-sonnet-20241022-v041', 'Claude 3.5 Sonnet #041', 128000, 1024, 0.00500000, 0.03000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000042', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000042', 'claude-3-opus-20240229-v042', 'Claude 3 Opus #042', 200000, 2048, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000043', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000043', 'claude-3-haiku-20240307-v043', 'Claude 3 Haiku #043', 4096, 4096, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000044', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000044', 'llama-3.1-8b-v044', 'Llama 3.1 8B #044', 8192, 8192, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000045', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000045', 'llama-3.1-70b-v045', 'Llama 3.1 70B #045', 16384, 16384, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000046', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000046', 'mistral-7b-v046', 'Mistral 7B #046', 32768, 1024, 0.00300000, 0.01500000, 'f', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000047', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000047', 'gemini-1.5-pro-v047', 'Gemini 1.5 Pro #047', 128000, 2048, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000048', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000048', 'gemini-1.5-flash-v048', 'Gemini 1.5 Flash #048', 200000, 4096, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000049', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000049', 'gpt-4o-mini-v049', 'GPT-4o Mini #049', 4096, 8192, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000050', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000050', 'gpt-4o-v050', 'GPT-4o #050', 8192, 16384, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000051', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000051', 'gpt-4-turbo-v051', 'GPT-4 Turbo #051', 16384, 1024, 0.00100000, 0.00300000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000052', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000052', 'gpt-3.5-turbo-v052', 'GPT-3.5 Turbo #052', 32768, 2048, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000053', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000053', 'claude-3-5-sonnet-20241022-v053', 'Claude 3.5 Sonnet #053', 128000, 4096, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000054', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000054', 'claude-3-opus-20240229-v054', 'Claude 3 Opus #054', 200000, 8192, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000055', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000055', 'claude-3-haiku-20240307-v055', 'Claude 3 Haiku #055', 4096, 16384, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000056', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000056', 'llama-3.1-8b-v056', 'Llama 3.1 8B #056', 8192, 1024, 0.00050000, 0.00150000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000057', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000057', 'llama-3.1-70b-v057', 'Llama 3.1 70B #057', 16384, 2048, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000058', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000058', 'mistral-7b-v058', 'Mistral 7B #058', 32768, 4096, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000059', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000059', 'gemini-1.5-pro-v059', 'Gemini 1.5 Pro #059', 128000, 8192, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000060', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000060', 'gemini-1.5-flash-v060', 'Gemini 1.5 Flash #060', 200000, 16384, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000061', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000061', 'gpt-4o-mini-v061', 'GPT-4o Mini #061', 4096, 1024, 0.00015000, 0.00060000, 'f', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000062', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000062', 'gpt-4o-v062', 'GPT-4o #062', 8192, 2048, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000063', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000063', 'gpt-4-turbo-v063', 'GPT-4 Turbo #063', 16384, 4096, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000064', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000064', 'gpt-3.5-turbo-v064', 'GPT-3.5 Turbo #064', 32768, 8192, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000065', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000065', 'claude-3-5-sonnet-20241022-v065', 'Claude 3.5 Sonnet #065', 128000, 16384, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000066', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000066', 'claude-3-opus-20240229-v066', 'Claude 3 Opus #066', 200000, 1024, 0.01000000, 0.05000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000067', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000067', 'claude-3-haiku-20240307-v067', 'Claude 3 Haiku #067', 4096, 2048, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000068', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000068', 'llama-3.1-8b-v068', 'Llama 3.1 8B #068', 8192, 4096, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000069', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000069', 'llama-3.1-70b-v069', 'Llama 3.1 70B #069', 16384, 8192, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000070', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000070', 'mistral-7b-v070', 'Mistral 7B #070', 32768, 16384, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000071', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000071', 'gemini-1.5-pro-v071', 'Gemini 1.5 Pro #071', 128000, 1024, 0.00500000, 0.03000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000072', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000072', 'gemini-1.5-flash-v072', 'Gemini 1.5 Flash #072', 200000, 2048, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000073', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000073', 'gpt-4o-mini-v073', 'GPT-4o Mini #073', 4096, 4096, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000074', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000074', 'gpt-4o-v074', 'GPT-4o #074', 8192, 8192, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000075', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000075', 'gpt-4-turbo-v075', 'GPT-4 Turbo #075', 16384, 16384, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000076', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000076', 'gpt-3.5-turbo-v076', 'GPT-3.5 Turbo #076', 32768, 1024, 0.00300000, 0.01500000, 'f', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000077', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000077', 'claude-3-5-sonnet-20241022-v077', 'Claude 3.5 Sonnet #077', 128000, 2048, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000078', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000078', 'claude-3-opus-20240229-v078', 'Claude 3 Opus #078', 200000, 4096, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000079', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000079', 'claude-3-haiku-20240307-v079', 'Claude 3 Haiku #079', 4096, 8192, 0.00015000, 0.00060000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000080', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000080', 'llama-3.1-8b-v080', 'Llama 3.1 8B #080', 8192, 16384, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000081', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000081', 'llama-3.1-70b-v081', 'Llama 3.1 70B #081', 16384, 1024, 0.00100000, 0.00300000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000082', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000082', 'mistral-7b-v082', 'Mistral 7B #082', 32768, 2048, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000083', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000083', 'gemini-1.5-pro-v083', 'Gemini 1.5 Pro #083', 128000, 4096, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000084', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000084', 'gemini-1.5-flash-v084', 'Gemini 1.5 Flash #084', 200000, 8192, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000085', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000085', 'gpt-4o-mini-v085', 'GPT-4o Mini #085', 4096, 16384, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000086', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000086', 'gpt-4o-v086', 'GPT-4o #086', 8192, 1024, 0.00050000, 0.00150000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000087', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000087', 'gpt-4-turbo-v087', 'GPT-4 Turbo #087', 16384, 2048, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000088', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000088', 'gpt-3.5-turbo-v088', 'GPT-3.5 Turbo #088', 32768, 4096, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000089', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000089', 'claude-3-5-sonnet-20241022-v089', 'Claude 3.5 Sonnet #089', 128000, 8192, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000090', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000090', 'claude-3-opus-20240229-v090', 'Claude 3 Opus #090', 200000, 16384, 0.01000000, 0.05000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000091', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000091', 'claude-3-haiku-20240307-v091', 'Claude 3 Haiku #091', 4096, 1024, 0.00015000, 0.00060000, 'f', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000092', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000092', 'llama-3.1-8b-v092', 'Llama 3.1 8B #092', 8192, 2048, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000093', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000093', 'llama-3.1-70b-v093', 'Llama 3.1 70B #093', 16384, 4096, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000094', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000094', 'mistral-7b-v094', 'Mistral 7B #094', 32768, 8192, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000095', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000095', 'gemini-1.5-pro-v095', 'Gemini 1.5 Pro #095', 128000, 16384, 0.00500000, 0.03000000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000096', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000096', 'gemini-1.5-flash-v096', 'Gemini 1.5 Flash #096', 200000, 1024, 0.01000000, 0.05000000, 'f', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000097', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000097', 'gpt-4o-mini-v097', 'GPT-4o Mini #097', 4096, 2048, 0.00015000, 0.00060000, 't', 'f', 'f', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000098', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-000000000098', 'gpt-4o-v098', 'GPT-4o #098', 8192, 4096, 0.00050000, 0.00150000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000099', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-000000000099', 'gpt-4-turbo-v099', 'GPT-4 Turbo #099', 16384, 8192, 0.00100000, 0.00300000, 't', 't', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_models" VALUES ('22222222-2222-2222-2222-000000000100', '00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-000000000100', 'gpt-3.5-turbo-v100', 'GPT-3.5 Turbo #100', 32768, 16384, 0.00300000, 0.01500000, 't', 'f', 't', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');

-- ----------------------------
-- Table structure for llm_providers
-- ----------------------------
DROP TABLE IF EXISTS "public"."llm_providers";
CREATE TABLE "public"."llm_providers" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "provider_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "api_key_encrypted" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "base_url" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "timeout_seconds" int4 NOT NULL DEFAULT 60,
  "priority" int4 NOT NULL DEFAULT 100,
  "is_active" bool NOT NULL DEFAULT true,
  "config_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of llm_providers
-- ----------------------------
INSERT INTO "public"."llm_providers" VALUES ('51a929e6-8f99-47d9-86c2-11da1d90d3b5', '00000000-0000-0000-0000-000000000001', 'openai-default', 'openai', '', 'https://api.openai.com/v1', 60, 10, 't', '{}', '2026-09-28 13:30:47.439749+00', '2026-09-28 13:30:47.439749+00');
INSERT INTO "public"."llm_providers" VALUES ('40a0d742-b61f-45ad-8cd6-f67bca6d42e0', '00000000-0000-0000-0000-000000000001', 'anthropic-default', 'anthropic', '', 'https://api.anthropic.com/v1', 60, 20, 't', '{}', '2026-09-28 13:30:47.439749+00', '2026-09-28 13:30:47.439749+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000001', '00000000-0000-0000-0000-000000000001', 'provider-001', 'openai', 'enc:v1:21af6b8b5e2244835679bbdbe0ab03a6', 'https://api.openai.com/v1', 30, 10, 'f', '{"region" : "us-east-1", "max_rps" : 10}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000002', '00000000-0000-0000-0000-000000000002', 'provider-002', 'anthropic', 'enc:v1:bcca528ca1b0ba9d641cf4b123f2d026', 'https://api.anthropic.com/v1', 60, 19, 't', '{"region" : "eu-west-1", "max_rps" : 11}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000003', '00000000-0000-0000-0000-000000000003', 'provider-003', 'local', 'enc:v1:5ccd563d0f716c309df53229000ad62c', 'http://localhost:11434', 90, 28, 't', '{"region" : "ap-southeast-1", "max_rps" : 12}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000004', '00000000-0000-0000-0000-000000000001', 'provider-004', 'azure', 'enc:v1:9bf3323d0aad0d0cbc1cb0bbb1529c0f', 'https://myorg.openai.azure.com', 120, 37, 't', '{"region" : "us-east-1", "max_rps" : 13}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000005', '00000000-0000-0000-0000-000000000002', 'provider-005', 'openai', 'enc:v1:8764262b17d9c32a8650d17e91b7600b', 'https://api.openai.com/v1', 30, 46, 't', '{"region" : "eu-west-1", "max_rps" : 14}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000006', '00000000-0000-0000-0000-000000000003', 'provider-006', 'anthropic', 'enc:v1:a678585e4b12fdda4131640cf0ded2dc', 'https://api.anthropic.com/v1', 60, 55, 't', '{"region" : "ap-southeast-1", "max_rps" : 15}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000007', '00000000-0000-0000-0000-000000000001', 'provider-007', 'local', 'enc:v1:429e0173addead3f5ed34035f4ac02ab', 'http://localhost:11434', 90, 64, 't', '{"region" : "us-east-1", "max_rps" : 16}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000008', '00000000-0000-0000-0000-000000000002', 'provider-008', 'azure', 'enc:v1:cacd85471987d51ea0be0d0d852f6dfb', 'https://myorg.openai.azure.com', 120, 73, 't', '{"region" : "eu-west-1", "max_rps" : 17}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000009', '00000000-0000-0000-0000-000000000003', 'provider-009', 'openai', 'enc:v1:80705ee2b93c8508068023de12b4c3af', 'https://api.openai.com/v1', 30, 82, 't', '{"region" : "ap-southeast-1", "max_rps" : 18}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000010', '00000000-0000-0000-0000-000000000001', 'provider-010', 'anthropic', 'enc:v1:6f1e278bd055e11813e006224ee7b886', 'https://api.anthropic.com/v1', 60, 91, 't', '{"region" : "us-east-1", "max_rps" : 19}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000011', '00000000-0000-0000-0000-000000000002', 'provider-011', 'local', 'enc:v1:a27c53ddf5b9c7be6a0c1c14675ecaee', 'http://localhost:11434', 90, 100, 'f', '{"region" : "eu-west-1", "max_rps" : 20}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000012', '00000000-0000-0000-0000-000000000003', 'provider-012', 'azure', 'enc:v1:09e7f289375040d64e88cd4ebbcc389c', 'https://myorg.openai.azure.com', 120, 109, 't', '{"region" : "ap-southeast-1", "max_rps" : 21}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000013', '00000000-0000-0000-0000-000000000001', 'provider-013', 'openai', 'enc:v1:edcaa086f984c30e957935263814d232', 'https://api.openai.com/v1', 30, 118, 't', '{"region" : "us-east-1", "max_rps" : 22}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000014', '00000000-0000-0000-0000-000000000002', 'provider-014', 'anthropic', 'enc:v1:f69bbbc4245b6de0fd47ff2f211af78e', 'https://api.anthropic.com/v1', 60, 127, 't', '{"region" : "eu-west-1", "max_rps" : 23}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000015', '00000000-0000-0000-0000-000000000003', 'provider-015', 'local', 'enc:v1:987921da37bb743b5c70000c751e7bbf', 'http://localhost:11434', 90, 136, 't', '{"region" : "ap-southeast-1", "max_rps" : 24}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000016', '00000000-0000-0000-0000-000000000001', 'provider-016', 'azure', 'enc:v1:5e444216c58c4e63a9a9898a3232b5f2', 'https://myorg.openai.azure.com', 120, 145, 't', '{"region" : "us-east-1", "max_rps" : 25}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000017', '00000000-0000-0000-0000-000000000002', 'provider-017', 'openai', 'enc:v1:17c34624ecdaff737ad328e426cc60a4', 'https://api.openai.com/v1', 30, 154, 't', '{"region" : "eu-west-1", "max_rps" : 26}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000018', '00000000-0000-0000-0000-000000000003', 'provider-018', 'anthropic', 'enc:v1:6c1845ce80801329ea9c1318db065099', 'https://api.anthropic.com/v1', 60, 163, 't', '{"region" : "ap-southeast-1", "max_rps" : 27}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000019', '00000000-0000-0000-0000-000000000001', 'provider-019', 'local', 'enc:v1:4f0769177cc53f4db9ee23b1229c77d0', 'http://localhost:11434', 90, 172, 't', '{"region" : "us-east-1", "max_rps" : 28}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000020', '00000000-0000-0000-0000-000000000002', 'provider-020', 'azure', 'enc:v1:8b6710062b9b36494b601d56ad0ebec8', 'https://myorg.openai.azure.com', 120, 181, 't', '{"region" : "eu-west-1", "max_rps" : 29}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000021', '00000000-0000-0000-0000-000000000003', 'provider-021', 'openai', 'enc:v1:3dcfc5a6a76eed8fcf56774904d45058', 'https://api.openai.com/v1', 30, 190, 'f', '{"region" : "ap-southeast-1", "max_rps" : 30}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000022', '00000000-0000-0000-0000-000000000001', 'provider-022', 'anthropic', 'enc:v1:ef17fa62f2443ba60cdc969e82f5adab', 'https://api.anthropic.com/v1', 60, 199, 't', '{"region" : "us-east-1", "max_rps" : 31}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000023', '00000000-0000-0000-0000-000000000002', 'provider-023', 'local', 'enc:v1:95253836b38e864b857d502156161f77', 'http://localhost:11434', 90, 208, 't', '{"region" : "eu-west-1", "max_rps" : 32}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000024', '00000000-0000-0000-0000-000000000003', 'provider-024', 'azure', 'enc:v1:7753851b8c193ea42c192245522d2e2a', 'https://myorg.openai.azure.com', 120, 217, 't', '{"region" : "ap-southeast-1", "max_rps" : 33}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000025', '00000000-0000-0000-0000-000000000001', 'provider-025', 'openai', 'enc:v1:471eff843be514177d91c8a8d8b124ec', 'https://api.openai.com/v1', 30, 226, 't', '{"region" : "us-east-1", "max_rps" : 34}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000026', '00000000-0000-0000-0000-000000000002', 'provider-026', 'anthropic', 'enc:v1:0ee1d58b4d569e3f843ea36c4e36a07c', 'https://api.anthropic.com/v1', 60, 235, 't', '{"region" : "eu-west-1", "max_rps" : 35}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000027', '00000000-0000-0000-0000-000000000003', 'provider-027', 'local', 'enc:v1:6e86cedc19c1b27291655013b424ea0a', 'http://localhost:11434', 90, 244, 't', '{"region" : "ap-southeast-1", "max_rps" : 36}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000028', '00000000-0000-0000-0000-000000000001', 'provider-028', 'azure', 'enc:v1:f53c5537df638ba487f09b9edbc43e02', 'https://myorg.openai.azure.com', 120, 253, 't', '{"region" : "us-east-1", "max_rps" : 37}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000029', '00000000-0000-0000-0000-000000000002', 'provider-029', 'openai', 'enc:v1:1839bf9e1a327d7169dbbba4b3c19290', 'https://api.openai.com/v1', 30, 262, 't', '{"region" : "eu-west-1", "max_rps" : 38}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000030', '00000000-0000-0000-0000-000000000003', 'provider-030', 'anthropic', 'enc:v1:594db5339ac95f8c0eaf3039ecf5d0d6', 'https://api.anthropic.com/v1', 60, 271, 't', '{"region" : "ap-southeast-1", "max_rps" : 39}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000031', '00000000-0000-0000-0000-000000000001', 'provider-031', 'local', 'enc:v1:6a454237d59d79db9cf69986f430efa9', 'http://localhost:11434', 90, 280, 'f', '{"region" : "us-east-1", "max_rps" : 40}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000032', '00000000-0000-0000-0000-000000000002', 'provider-032', 'azure', 'enc:v1:4122fe1472b79dd9a5d75310229c5eb1', 'https://myorg.openai.azure.com', 120, 289, 't', '{"region" : "eu-west-1", "max_rps" : 41}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000033', '00000000-0000-0000-0000-000000000003', 'provider-033', 'openai', 'enc:v1:19821e32d105eb0b8b6ed5c375960c29', 'https://api.openai.com/v1', 30, 298, 't', '{"region" : "ap-southeast-1", "max_rps" : 42}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000034', '00000000-0000-0000-0000-000000000001', 'provider-034', 'anthropic', 'enc:v1:728a60ac4983400b7d09f51320f43ae3', 'https://api.anthropic.com/v1', 60, 307, 't', '{"region" : "us-east-1", "max_rps" : 43}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000035', '00000000-0000-0000-0000-000000000002', 'provider-035', 'local', 'enc:v1:c075fb8bf44272c4f1c38ad76ea36530', 'http://localhost:11434', 90, 316, 't', '{"region" : "eu-west-1", "max_rps" : 44}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000036', '00000000-0000-0000-0000-000000000003', 'provider-036', 'azure', 'enc:v1:757d504c6fc0a1dfbb028f813ba3748c', 'https://myorg.openai.azure.com', 120, 325, 't', '{"region" : "ap-southeast-1", "max_rps" : 45}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000037', '00000000-0000-0000-0000-000000000001', 'provider-037', 'openai', 'enc:v1:d6613d45be4b15035cf922bc14065ce5', 'https://api.openai.com/v1', 30, 334, 't', '{"region" : "us-east-1", "max_rps" : 46}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000038', '00000000-0000-0000-0000-000000000002', 'provider-038', 'anthropic', 'enc:v1:35d1af3227c8fca89b240011e7e4eb92', 'https://api.anthropic.com/v1', 60, 343, 't', '{"region" : "eu-west-1", "max_rps" : 47}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000039', '00000000-0000-0000-0000-000000000003', 'provider-039', 'local', 'enc:v1:e8196e9daa8a1259e7aa3cc90e46d73e', 'http://localhost:11434', 90, 352, 't', '{"region" : "ap-southeast-1", "max_rps" : 48}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000040', '00000000-0000-0000-0000-000000000001', 'provider-040', 'azure', 'enc:v1:9fdebeb8242807f1158b2870478de8d5', 'https://myorg.openai.azure.com', 120, 361, 't', '{"region" : "us-east-1", "max_rps" : 49}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000041', '00000000-0000-0000-0000-000000000002', 'provider-041', 'openai', 'enc:v1:396781efa180f9c8fdff7b29d49bdaeb', 'https://api.openai.com/v1', 30, 370, 'f', '{"region" : "eu-west-1", "max_rps" : 50}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000042', '00000000-0000-0000-0000-000000000003', 'provider-042', 'anthropic', 'enc:v1:c4c607a3017486057abf4e57efb474cb', 'https://api.anthropic.com/v1', 60, 379, 't', '{"region" : "ap-southeast-1", "max_rps" : 51}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000043', '00000000-0000-0000-0000-000000000001', 'provider-043', 'local', 'enc:v1:7fe146b6fdcaa7ff871661a9988a5dcd', 'http://localhost:11434', 90, 388, 't', '{"region" : "us-east-1", "max_rps" : 52}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000044', '00000000-0000-0000-0000-000000000002', 'provider-044', 'azure', 'enc:v1:2dceff7303429cbc7b891d0c696be796', 'https://myorg.openai.azure.com', 120, 397, 't', '{"region" : "eu-west-1", "max_rps" : 53}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000045', '00000000-0000-0000-0000-000000000003', 'provider-045', 'openai', 'enc:v1:3d43a1434dabafcdb29b2a8ffcaaf7e5', 'https://api.openai.com/v1', 30, 406, 't', '{"region" : "ap-southeast-1", "max_rps" : 54}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000046', '00000000-0000-0000-0000-000000000001', 'provider-046', 'anthropic', 'enc:v1:f5ba74e0848c6e3516865dfe954ce341', 'https://api.anthropic.com/v1', 60, 415, 't', '{"region" : "us-east-1", "max_rps" : 55}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000047', '00000000-0000-0000-0000-000000000002', 'provider-047', 'local', 'enc:v1:ada989f640d6abf181a525c30798c5eb', 'http://localhost:11434', 90, 424, 't', '{"region" : "eu-west-1", "max_rps" : 56}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000048', '00000000-0000-0000-0000-000000000003', 'provider-048', 'azure', 'enc:v1:72124ea75565d47435f7b58d5791b298', 'https://myorg.openai.azure.com', 120, 433, 't', '{"region" : "ap-southeast-1", "max_rps" : 57}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000049', '00000000-0000-0000-0000-000000000001', 'provider-049', 'openai', 'enc:v1:2c15749b9f493d29e0ae991cf1705a01', 'https://api.openai.com/v1', 30, 442, 't', '{"region" : "us-east-1", "max_rps" : 58}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000050', '00000000-0000-0000-0000-000000000002', 'provider-050', 'anthropic', 'enc:v1:c55d1efa26e2a8356568127807089ead', 'https://api.anthropic.com/v1', 60, 451, 't', '{"region" : "eu-west-1", "max_rps" : 59}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000051', '00000000-0000-0000-0000-000000000003', 'provider-051', 'local', 'enc:v1:2df12c59709c74bf2cbedb2222ab5d4e', 'http://localhost:11434', 90, 460, 'f', '{"region" : "ap-southeast-1", "max_rps" : 60}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000052', '00000000-0000-0000-0000-000000000001', 'provider-052', 'azure', 'enc:v1:3722ba0ca6e7f0ef1c09524afbd85f89', 'https://myorg.openai.azure.com', 120, 469, 't', '{"region" : "us-east-1", "max_rps" : 61}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000053', '00000000-0000-0000-0000-000000000002', 'provider-053', 'openai', 'enc:v1:f25df5891d514bd978ad3e97984354f9', 'https://api.openai.com/v1', 30, 478, 't', '{"region" : "eu-west-1", "max_rps" : 62}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000054', '00000000-0000-0000-0000-000000000003', 'provider-054', 'anthropic', 'enc:v1:98ec54d45a7b70876a6e1fa585a0b3b5', 'https://api.anthropic.com/v1', 60, 487, 't', '{"region" : "ap-southeast-1", "max_rps" : 63}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000055', '00000000-0000-0000-0000-000000000001', 'provider-055', 'local', 'enc:v1:0b1dac2e1afa386caacab8ce19bea0a9', 'http://localhost:11434', 90, 496, 't', '{"region" : "us-east-1", "max_rps" : 64}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000056', '00000000-0000-0000-0000-000000000002', 'provider-056', 'azure', 'enc:v1:ee3b0ce6cb3f00de36cda6f0836cbb7a', 'https://myorg.openai.azure.com', 120, 505, 't', '{"region" : "eu-west-1", "max_rps" : 65}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000057', '00000000-0000-0000-0000-000000000003', 'provider-057', 'openai', 'enc:v1:236cdd1ee97845e65955b0fafc306262', 'https://api.openai.com/v1', 30, 514, 't', '{"region" : "ap-southeast-1", "max_rps" : 66}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000058', '00000000-0000-0000-0000-000000000001', 'provider-058', 'anthropic', 'enc:v1:357cb80bb66151f42900e99c6d574cd1', 'https://api.anthropic.com/v1', 60, 523, 't', '{"region" : "us-east-1", "max_rps" : 67}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000059', '00000000-0000-0000-0000-000000000002', 'provider-059', 'local', 'enc:v1:47112f95d4ccc797f3516d8cccc550ae', 'http://localhost:11434', 90, 532, 't', '{"region" : "eu-west-1", "max_rps" : 68}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000060', '00000000-0000-0000-0000-000000000003', 'provider-060', 'azure', 'enc:v1:a81e9f70341fc40aaca2b471b71d8cf3', 'https://myorg.openai.azure.com', 120, 541, 't', '{"region" : "ap-southeast-1", "max_rps" : 69}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000061', '00000000-0000-0000-0000-000000000001', 'provider-061', 'openai', 'enc:v1:7b600504a3dd0b649753a725cffe7601', 'https://api.openai.com/v1', 30, 550, 'f', '{"region" : "us-east-1", "max_rps" : 70}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000062', '00000000-0000-0000-0000-000000000002', 'provider-062', 'anthropic', 'enc:v1:b5b2a5bb2d1c1956f4caa2c73ea018fc', 'https://api.anthropic.com/v1', 60, 559, 't', '{"region" : "eu-west-1", "max_rps" : 71}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000063', '00000000-0000-0000-0000-000000000003', 'provider-063', 'local', 'enc:v1:0c641586c82192d577827235fc67cb0b', 'http://localhost:11434', 90, 568, 't', '{"region" : "ap-southeast-1", "max_rps" : 72}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000064', '00000000-0000-0000-0000-000000000001', 'provider-064', 'azure', 'enc:v1:99d51edce9efe30928431e8656d6a111', 'https://myorg.openai.azure.com', 120, 577, 't', '{"region" : "us-east-1", "max_rps" : 73}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000065', '00000000-0000-0000-0000-000000000002', 'provider-065', 'openai', 'enc:v1:9f6476f60252ab85ae6688891b52b93f', 'https://api.openai.com/v1', 30, 586, 't', '{"region" : "eu-west-1", "max_rps" : 74}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000066', '00000000-0000-0000-0000-000000000003', 'provider-066', 'anthropic', 'enc:v1:574a90a26054168eb009b28f3ce1fd0a', 'https://api.anthropic.com/v1', 60, 595, 't', '{"region" : "ap-southeast-1", "max_rps" : 75}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000067', '00000000-0000-0000-0000-000000000001', 'provider-067', 'local', 'enc:v1:aac696d5590ba50ad994b295ea89e401', 'http://localhost:11434', 90, 604, 't', '{"region" : "us-east-1", "max_rps" : 76}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000068', '00000000-0000-0000-0000-000000000002', 'provider-068', 'azure', 'enc:v1:d89fc0dcc1898ac287487eeb149d0683', 'https://myorg.openai.azure.com', 120, 613, 't', '{"region" : "eu-west-1", "max_rps" : 77}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000069', '00000000-0000-0000-0000-000000000003', 'provider-069', 'openai', 'enc:v1:5c62957c8abea37f2a932b1dfc3471ad', 'https://api.openai.com/v1', 30, 622, 't', '{"region" : "ap-southeast-1", "max_rps" : 78}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000070', '00000000-0000-0000-0000-000000000001', 'provider-070', 'anthropic', 'enc:v1:135d3baeca413696a4860e1503d1a847', 'https://api.anthropic.com/v1', 60, 631, 't', '{"region" : "us-east-1", "max_rps" : 79}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000071', '00000000-0000-0000-0000-000000000002', 'provider-071', 'local', 'enc:v1:f9d7433d74187a5cf6cabe1687881f64', 'http://localhost:11434', 90, 640, 'f', '{"region" : "eu-west-1", "max_rps" : 80}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000072', '00000000-0000-0000-0000-000000000003', 'provider-072', 'azure', 'enc:v1:f8b8e459f6d5553c0e1aef71992d4e0d', 'https://myorg.openai.azure.com', 120, 649, 't', '{"region" : "ap-southeast-1", "max_rps" : 81}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000073', '00000000-0000-0000-0000-000000000001', 'provider-073', 'openai', 'enc:v1:6611378121a60da69b97a6de3299dccd', 'https://api.openai.com/v1', 30, 658, 't', '{"region" : "us-east-1", "max_rps" : 82}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000074', '00000000-0000-0000-0000-000000000002', 'provider-074', 'anthropic', 'enc:v1:bb517c5987c57bfd2747e11f750974fb', 'https://api.anthropic.com/v1', 60, 667, 't', '{"region" : "eu-west-1", "max_rps" : 83}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000075', '00000000-0000-0000-0000-000000000003', 'provider-075', 'local', 'enc:v1:c6233cf6532ce1961dd52b589b36511e', 'http://localhost:11434', 90, 676, 't', '{"region" : "ap-southeast-1", "max_rps" : 84}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000076', '00000000-0000-0000-0000-000000000001', 'provider-076', 'azure', 'enc:v1:c7abaefddf941694b93ef0f1a92fb250', 'https://myorg.openai.azure.com', 120, 685, 't', '{"region" : "us-east-1", "max_rps" : 85}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000077', '00000000-0000-0000-0000-000000000002', 'provider-077', 'openai', 'enc:v1:d7083c8658cf0cfaa01a9498d0e11076', 'https://api.openai.com/v1', 30, 694, 't', '{"region" : "eu-west-1", "max_rps" : 86}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000078', '00000000-0000-0000-0000-000000000003', 'provider-078', 'anthropic', 'enc:v1:cfed7b3fcfdc15214f06a73e79570c7f', 'https://api.anthropic.com/v1', 60, 703, 't', '{"region" : "ap-southeast-1", "max_rps" : 87}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000079', '00000000-0000-0000-0000-000000000001', 'provider-079', 'local', 'enc:v1:776e69b3b4d8c75e0f9a622c665c72d5', 'http://localhost:11434', 90, 712, 't', '{"region" : "us-east-1", "max_rps" : 88}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000080', '00000000-0000-0000-0000-000000000002', 'provider-080', 'azure', 'enc:v1:a916742b636a41f313db7176d9176f3e', 'https://myorg.openai.azure.com', 120, 721, 't', '{"region" : "eu-west-1", "max_rps" : 89}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000081', '00000000-0000-0000-0000-000000000003', 'provider-081', 'openai', 'enc:v1:b2c32cf9e76d1b3998d1237afd069d3b', 'https://api.openai.com/v1', 30, 730, 'f', '{"region" : "ap-southeast-1", "max_rps" : 90}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000082', '00000000-0000-0000-0000-000000000001', 'provider-082', 'anthropic', 'enc:v1:a730ee60ee7e5cabfefe2c0b7d358d63', 'https://api.anthropic.com/v1', 60, 739, 't', '{"region" : "us-east-1", "max_rps" : 91}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000083', '00000000-0000-0000-0000-000000000002', 'provider-083', 'local', 'enc:v1:a2bf9f75c9392c602262be7506685ae0', 'http://localhost:11434', 90, 748, 't', '{"region" : "eu-west-1", "max_rps" : 92}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000084', '00000000-0000-0000-0000-000000000003', 'provider-084', 'azure', 'enc:v1:db807784d6b5eaf0f31a7aab4d4694a7', 'https://myorg.openai.azure.com', 120, 757, 't', '{"region" : "ap-southeast-1", "max_rps" : 93}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000085', '00000000-0000-0000-0000-000000000001', 'provider-085', 'openai', 'enc:v1:170a5ac7ac14f5a05e4353392b64f634', 'https://api.openai.com/v1', 30, 766, 't', '{"region" : "us-east-1", "max_rps" : 94}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000086', '00000000-0000-0000-0000-000000000002', 'provider-086', 'anthropic', 'enc:v1:f81756f3f6d119b93257b9e731bae547', 'https://api.anthropic.com/v1', 60, 775, 't', '{"region" : "eu-west-1", "max_rps" : 95}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000087', '00000000-0000-0000-0000-000000000003', 'provider-087', 'local', 'enc:v1:cdf2c68be0b42bd6cb417f1fc4e71dfa', 'http://localhost:11434', 90, 784, 't', '{"region" : "ap-southeast-1", "max_rps" : 96}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000088', '00000000-0000-0000-0000-000000000001', 'provider-088', 'azure', 'enc:v1:c62915034d1a8ea2770b26db8ba9dfe6', 'https://myorg.openai.azure.com', 120, 793, 't', '{"region" : "us-east-1", "max_rps" : 97}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000089', '00000000-0000-0000-0000-000000000002', 'provider-089', 'openai', 'enc:v1:28d5823f1acfc127bcc30cc8e01cbe6e', 'https://api.openai.com/v1', 30, 802, 't', '{"region" : "eu-west-1", "max_rps" : 98}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000090', '00000000-0000-0000-0000-000000000003', 'provider-090', 'anthropic', 'enc:v1:9cb54dbca2980b3f0cc2e01caa202311', 'https://api.anthropic.com/v1', 60, 811, 't', '{"region" : "ap-southeast-1", "max_rps" : 99}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000091', '00000000-0000-0000-0000-000000000001', 'provider-091', 'local', 'enc:v1:c865b47dd0822805f617a7338c5e60d0', 'http://localhost:11434', 90, 820, 'f', '{"region" : "us-east-1", "max_rps" : 10}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000092', '00000000-0000-0000-0000-000000000002', 'provider-092', 'azure', 'enc:v1:38f727c2d17f989472d5e19843d80420', 'https://myorg.openai.azure.com', 120, 829, 't', '{"region" : "eu-west-1", "max_rps" : 11}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000093', '00000000-0000-0000-0000-000000000003', 'provider-093', 'openai', 'enc:v1:c1ff53f9498d46ce02555a044ce1cdf5', 'https://api.openai.com/v1', 30, 838, 't', '{"region" : "ap-southeast-1", "max_rps" : 12}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000094', '00000000-0000-0000-0000-000000000001', 'provider-094', 'anthropic', 'enc:v1:f366c8e1fc6549e540113157fe966ff2', 'https://api.anthropic.com/v1', 60, 847, 't', '{"region" : "us-east-1", "max_rps" : 13}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000095', '00000000-0000-0000-0000-000000000002', 'provider-095', 'local', 'enc:v1:633751bf312bb2501887b7b4ab8dba75', 'http://localhost:11434', 90, 856, 't', '{"region" : "eu-west-1", "max_rps" : 14}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000096', '00000000-0000-0000-0000-000000000003', 'provider-096', 'azure', 'enc:v1:72889932782faed696092a422ded55d3', 'https://myorg.openai.azure.com', 120, 865, 't', '{"region" : "ap-southeast-1", "max_rps" : 15}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000097', '00000000-0000-0000-0000-000000000001', 'provider-097', 'openai', 'enc:v1:7d8a9bc88dfde8b006ad0e6e25365860', 'https://api.openai.com/v1', 30, 874, 't', '{"region" : "us-east-1", "max_rps" : 16}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000098', '00000000-0000-0000-0000-000000000002', 'provider-098', 'anthropic', 'enc:v1:17d35e79e43499357e940e0fdedc021b', 'https://api.anthropic.com/v1', 60, 883, 't', '{"region" : "eu-west-1", "max_rps" : 17}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000099', '00000000-0000-0000-0000-000000000003', 'provider-099', 'local', 'enc:v1:e3db459a61b7272a1fe1636a37349c3e', 'http://localhost:11434', 90, 892, 't', '{"region" : "ap-southeast-1", "max_rps" : 18}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_providers" VALUES ('11111111-1111-1111-1111-000000000100', '00000000-0000-0000-0000-000000000001', 'provider-100', 'azure', 'enc:v1:49d1f4dfc8abfbbaec268be2c311a38c', 'https://myorg.openai.azure.com', 120, 901, 't', '{"region" : "us-east-1", "max_rps" : 19}', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');

-- ----------------------------
-- Table structure for llm_usage_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."llm_usage_logs";
CREATE TABLE "public"."llm_usage_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "model_id" uuid NOT NULL,
  "conversation_id" uuid,
  "tokens_input" int4 NOT NULL DEFAULT 0,
  "tokens_output" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "source" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'chat'::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of llm_usage_logs
-- ----------------------------
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000001', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000001', '33333333-3333-3333-3333-000000000001', 0, 0, 0.00000000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000002', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000002', '33333333-3333-3333-3333-000000000002', 41, 67, 0.00023000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000003', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000003', '33333333-3333-3333-3333-000000000003', 82, 134, 0.00046000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000004', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000004', '33333333-3333-3333-3333-000000000004', 123, 201, 0.00069000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000005', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000005', '33333333-3333-3333-3333-000000000005', 164, 268, 0.00092000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000006', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000006', '33333333-3333-3333-3333-000000000006', 205, 335, 0.00115000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000007', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000007', '33333333-3333-3333-3333-000000000007', 246, 402, 0.00138000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000008', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000008', '33333333-3333-3333-3333-000000000008', 287, 469, 0.00161000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000009', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000009', NULL, 328, 536, 0.00184000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000010', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000010', NULL, 369, 603, 0.00207000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000011', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000011', '33333333-3333-3333-3333-000000000011', 410, 670, 0.00230000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000012', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000012', '33333333-3333-3333-3333-000000000012', 451, 737, 0.00253000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000013', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000013', '33333333-3333-3333-3333-000000000013', 492, 804, 0.00276000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000014', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000014', '33333333-3333-3333-3333-000000000014', 533, 871, 0.00299000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000015', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000015', '33333333-3333-3333-3333-000000000015', 574, 938, 0.00322000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000016', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000016', '33333333-3333-3333-3333-000000000016', 615, 1005, 0.00345000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000017', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000017', '33333333-3333-3333-3333-000000000017', 656, 1072, 0.00368000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000018', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000018', '33333333-3333-3333-3333-000000000018', 697, 1139, 0.00391000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000019', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000019', NULL, 738, 1206, 0.00414000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000020', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000020', NULL, 779, 1273, 0.00437000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000021', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000021', '33333333-3333-3333-3333-000000000021', 820, 1340, 0.00460000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000022', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000022', '33333333-3333-3333-3333-000000000022', 861, 1407, 0.00483000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000023', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000023', '33333333-3333-3333-3333-000000000023', 902, 1474, 0.00506000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000024', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000024', '33333333-3333-3333-3333-000000000024', 943, 1541, 0.00529000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000025', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000025', '33333333-3333-3333-3333-000000000025', 984, 1608, 0.00552000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000026', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000026', '33333333-3333-3333-3333-000000000026', 1025, 1675, 0.00575000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000027', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000027', '33333333-3333-3333-3333-000000000027', 1066, 1742, 0.00598000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000028', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000028', '33333333-3333-3333-3333-000000000028', 1107, 1809, 0.00621000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000029', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000029', NULL, 1148, 1876, 0.00644000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000030', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000030', NULL, 1189, 1943, 0.00667000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000031', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000031', '33333333-3333-3333-3333-000000000031', 1230, 2010, 0.00690000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000032', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000032', '33333333-3333-3333-3333-000000000032', 1271, 2077, 0.00713000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000033', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000033', '33333333-3333-3333-3333-000000000033', 1312, 2144, 0.00736000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000034', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000034', '33333333-3333-3333-3333-000000000034', 1353, 2211, 0.00759000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000035', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000035', '33333333-3333-3333-3333-000000000035', 1394, 2278, 0.00782000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000036', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000036', '33333333-3333-3333-3333-000000000036', 1435, 2345, 0.00805000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000037', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000037', '33333333-3333-3333-3333-000000000037', 1476, 2412, 0.00828000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000038', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000038', '33333333-3333-3333-3333-000000000038', 1517, 2479, 0.00851000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000039', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000039', NULL, 1558, 2546, 0.00874000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000040', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000040', NULL, 1599, 2613, 0.00897000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000041', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000041', '33333333-3333-3333-3333-000000000041', 1640, 2680, 0.00920000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000042', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000042', '33333333-3333-3333-3333-000000000042', 1681, 2747, 0.00943000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000043', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000043', '33333333-3333-3333-3333-000000000043', 1722, 2814, 0.00966000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000044', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000044', '33333333-3333-3333-3333-000000000044', 1763, 2881, 0.00989000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000045', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000045', '33333333-3333-3333-3333-000000000045', 1804, 2948, 0.01012000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000046', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000046', '33333333-3333-3333-3333-000000000046', 1845, 3015, 0.01035000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000047', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000047', '33333333-3333-3333-3333-000000000047', 1886, 3082, 0.01058000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000048', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000048', '33333333-3333-3333-3333-000000000048', 1927, 3149, 0.01081000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000049', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000049', NULL, 1968, 3216, 0.01104000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000050', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000050', NULL, 2009, 3283, 0.01127000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000051', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000051', '33333333-3333-3333-3333-000000000051', 2050, 3350, 0.01150000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000052', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000052', '33333333-3333-3333-3333-000000000052', 2091, 3417, 0.01173000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000053', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000053', '33333333-3333-3333-3333-000000000053', 2132, 3484, 0.01196000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000054', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000054', '33333333-3333-3333-3333-000000000054', 2173, 3551, 0.01219000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000055', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000055', '33333333-3333-3333-3333-000000000055', 2214, 3618, 0.01242000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000056', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000056', '33333333-3333-3333-3333-000000000056', 2255, 3685, 0.01265000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000057', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000057', '33333333-3333-3333-3333-000000000057', 2296, 3752, 0.01288000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000058', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000058', '33333333-3333-3333-3333-000000000058', 2337, 3819, 0.01311000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000059', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000059', NULL, 2378, 3886, 0.01334000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000060', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000060', NULL, 2419, 3953, 0.01357000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000061', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000061', '33333333-3333-3333-3333-000000000061', 2460, 4020, 0.01380000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000062', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000062', '33333333-3333-3333-3333-000000000062', 2501, 4087, 0.01403000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000063', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000063', '33333333-3333-3333-3333-000000000063', 2542, 4154, 0.01426000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000064', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000064', '33333333-3333-3333-3333-000000000064', 2583, 4221, 0.01449000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000065', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000065', '33333333-3333-3333-3333-000000000065', 2624, 4288, 0.01472000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000066', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000066', '33333333-3333-3333-3333-000000000066', 2665, 4355, 0.01495000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000067', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000067', '33333333-3333-3333-3333-000000000067', 2706, 4422, 0.01518000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000068', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000068', '33333333-3333-3333-3333-000000000068', 2747, 4489, 0.01541000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000069', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000069', NULL, 2788, 4556, 0.01564000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000070', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000070', NULL, 2829, 4623, 0.01587000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000071', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000071', '33333333-3333-3333-3333-000000000071', 2870, 4690, 0.01610000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000072', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000072', '33333333-3333-3333-3333-000000000072', 2911, 4757, 0.01633000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000073', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000073', '33333333-3333-3333-3333-000000000073', 2952, 4824, 0.01656000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000074', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000074', '33333333-3333-3333-3333-000000000074', 2993, 4891, 0.01679000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000075', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000075', '33333333-3333-3333-3333-000000000075', 3034, 4958, 0.01702000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000076', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000076', '33333333-3333-3333-3333-000000000076', 3075, 5025, 0.01725000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000077', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000077', '33333333-3333-3333-3333-000000000077', 3116, 5092, 0.01748000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000078', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000078', '33333333-3333-3333-3333-000000000078', 3157, 5159, 0.01771000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000079', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000079', NULL, 3198, 5226, 0.01794000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000080', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000080', NULL, 3239, 5293, 0.01817000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000081', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000081', '33333333-3333-3333-3333-000000000081', 3280, 5360, 0.01840000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000082', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000082', '33333333-3333-3333-3333-000000000082', 3321, 5427, 0.01863000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000083', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000083', '33333333-3333-3333-3333-000000000083', 3362, 5494, 0.01886000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000084', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000084', '33333333-3333-3333-3333-000000000084', 3403, 5561, 0.01909000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000085', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000085', '33333333-3333-3333-3333-000000000085', 3444, 5628, 0.01932000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000086', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000086', '33333333-3333-3333-3333-000000000086', 3485, 5695, 0.01955000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000087', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000087', '33333333-3333-3333-3333-000000000087', 3526, 5762, 0.01978000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000088', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000088', '33333333-3333-3333-3333-000000000088', 3567, 5829, 0.02001000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000089', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000089', NULL, 3608, 5896, 0.02024000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000090', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000090', NULL, 3649, 5963, 0.02047000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000091', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000001', '22222222-2222-2222-2222-000000000091', '33333333-3333-3333-3333-000000000091', 3690, 6030, 0.02070000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000092', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000002', '22222222-2222-2222-2222-000000000092', '33333333-3333-3333-3333-000000000092', 3731, 6097, 0.02093000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000093', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000003', '22222222-2222-2222-2222-000000000093', '33333333-3333-3333-3333-000000000093', 3772, 6164, 0.02116000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000094', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000004', '22222222-2222-2222-2222-000000000094', '33333333-3333-3333-3333-000000000094', 3813, 6231, 0.02139000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000095', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000005', '22222222-2222-2222-2222-000000000095', '33333333-3333-3333-3333-000000000095', 3854, 6298, 0.02162000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000096', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000006', '22222222-2222-2222-2222-000000000096', '33333333-3333-3333-3333-000000000096', 3895, 6365, 0.02185000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000097', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000007', '22222222-2222-2222-2222-000000000097', '33333333-3333-3333-3333-000000000097', 3936, 6432, 0.02208000, 'chat', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000098', '00000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-000000000008', '22222222-2222-2222-2222-000000000098', '33333333-3333-3333-3333-000000000098', 3977, 6499, 0.02231000, 'stream', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000099', '00000000-0000-0000-0000-000000000003', '44444444-4444-4444-4444-000000000009', '22222222-2222-2222-2222-000000000099', NULL, 4018, 6566, 0.02254000, 'completion', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');
INSERT INTO "public"."llm_usage_logs" VALUES ('66666666-6666-6666-6666-000000000100', '00000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-000000000010', '22222222-2222-2222-2222-000000000100', NULL, 4059, 6633, 0.02277000, 'tool', '2026-09-28 13:31:36.870692+00', '2026-09-28 13:31:36.870692+00');

-- ----------------------------
-- Table structure for pdpa_consent_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."pdpa_consent_logs";
CREATE TABLE "public"."pdpa_consent_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "purpose_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'GRANTED'::character varying,
  "granted_at" timestamptz(6) NOT NULL DEFAULT now(),
  "revoked_at" timestamptz(6),
  "expires_at" timestamptz(6),
  "evidence" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "version" int4 NOT NULL DEFAULT 1,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of pdpa_consent_logs
-- ----------------------------
INSERT INTO "public"."pdpa_consent_logs" VALUES ('ad5b147c-6e8e-4275-91ea-8236e07cf367', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'DATA_COLLECTION', 'GRANTED', '2026-09-01 09:00:00+00', NULL, '2027-09-01 09:00:00+00', '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('862923c6-5c1d-4b94-b0d1-d52f4a2c610b', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'DATA_DELETION', 'GRANTED', '2026-09-01 09:05:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('d6a18052-2cdb-4238-bdbd-65b3e6287797', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'USER_ACCOUNT', 'GRANTED', '2026-09-01 09:10:00+00', NULL, NULL, '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('dba3ac8b-7eaf-43af-8a9e-a489ccd8a243', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'USAGE_LOGS', 'GRANTED', '2026-09-01 09:15:00+00', NULL, '2027-03-01 09:15:00+00', '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('4b3b151a-056f-4c2e-96e0-a3b3d7e2115b', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'TRANSACTION_HISTORY', 'GRANTED', '2026-09-01 09:20:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('2af18e19-707e-477b-a120-ba6ad762667e', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'DATA_COLLECTION', 'GRANTED', '2026-09-02 10:00:00+00', NULL, '2027-09-02 10:00:00+00', '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('88489b98-c5b9-4aab-9386-8985f7ab13f8', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'DATA_DELETION', 'GRANTED', '2026-09-02 10:05:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('0d14f286-cb09-4f9f-a3a3-1bfe81a42d5f', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'USER_ACCOUNT', 'GRANTED', '2026-09-02 10:10:00+00', NULL, NULL, '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('b1d97340-386a-4303-9fd8-a20b155bdb97', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'USAGE_LOGS', 'GRANTED', '2026-09-02 10:15:00+00', NULL, '2027-03-02 10:15:00+00', '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('4eda1784-282e-4a81-a680-67a371e44830', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'TRANSACTION_HISTORY', 'GRANTED', '2026-09-02 10:20:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('c043cd03-a1cb-4eca-b27b-515f5f5ccd35', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'DATA_COLLECTION', 'GRANTED', '2026-09-03 11:00:00+00', NULL, '2027-09-03 11:00:00+00', '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('fbeceb45-8c1e-4a0c-a8dd-f3fec2b0ad26', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'DATA_DELETION', 'GRANTED', '2026-09-03 11:05:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('a5c0b42e-6b17-4f7d-8e04-949029b5c3d8', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'USER_ACCOUNT', 'GRANTED', '2026-09-03 11:10:00+00', NULL, NULL, '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('fb54b034-f5a2-43a8-beff-462e7daf779b', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'USAGE_LOGS', 'GRANTED', '2026-09-03 11:15:00+00', NULL, '2027-03-03 11:15:00+00', '{"source": "mobile", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('ce3d1a8f-6f91-42c0-a366-0a830044b788', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'TRANSACTION_HISTORY', 'GRANTED', '2026-09-03 11:20:00+00', NULL, NULL, '{"source": "web", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('486c9370-2566-41fe-8555-5ad2c5f94550', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'DATA_COLLECTION', 'GRANTED', '2026-09-04 12:00:00+00', NULL, '2027-09-04 12:00:00+00', '{"source": "api", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('2f9a7b04-3d06-4058-ae48-497e35ffe6af', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'DATA_DELETION', 'GRANTED', '2026-09-04 12:05:00+00', NULL, NULL, '{"source": "api", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('c29a1dcf-edf6-4db4-b8a2-e05af31e7a57', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'USER_ACCOUNT', 'GRANTED', '2026-09-04 12:10:00+00', NULL, NULL, '{"source": "api", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('82a6e455-1afe-4306-9c28-5d6de15a53ed', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'USAGE_LOGS', 'GRANTED', '2026-09-04 12:15:00+00', NULL, '2027-03-04 12:15:00+00', '{"source": "api", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_consent_logs" VALUES ('e9c4eef5-32ba-4792-bf9b-ce0a9090ba16', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'TRANSACTION_HISTORY', 'GRANTED', '2026-09-04 12:20:00+00', NULL, NULL, '{"source": "api", "policy_version": 1}', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');

-- ----------------------------
-- Table structure for pdpa_cookie_consents
-- ----------------------------
DROP TABLE IF EXISTS "public"."pdpa_cookie_consents";
CREATE TABLE "public"."pdpa_cookie_consents" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid,
  "session_id" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "necessary" bool NOT NULL DEFAULT true,
  "analytics" bool NOT NULL DEFAULT false,
  "marketing" bool NOT NULL DEFAULT false,
  "functional" bool NOT NULL DEFAULT false,
  "ip_address" inet,
  "user_agent" varchar(500) COLLATE "pg_catalog"."default",
  "accepted_at" timestamptz(6) NOT NULL DEFAULT now(),
  "withdrawn_at" timestamptz(6),
  "version" int4 NOT NULL DEFAULT 1,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of pdpa_cookie_consents
-- ----------------------------
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('49e6d4db-1264-48df-852e-86b1b2b53c7c', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'sess-demo-001', 't', 't', 'f', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-01 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('29b3d964-9249-4f12-9283-0066c02cc6d8', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'sess-demo-002', 't', 'f', 'f', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-02 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('280f818f-280b-4807-9fd1-320af6730e44', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'sess-demo-003', 't', 't', 't', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-03 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('d61b071e-9834-40d9-954d-412535eceaf3', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'sess-demo-004', 't', 'f', 'f', 'f', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-04 13:00:00+00', '2026-09-10 13:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('b5a53952-f6ff-4e0e-956c-553a50e8a0b6', '11111111-1111-1111-1111-111111111111', NULL, 'sess-demo-005', 't', 't', 'f', 'f', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-05 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('70bd33fb-27b2-4e87-bdc2-59094c690b1f', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'sess-demo-006', 't', 't', 't', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-06 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('fdc23ee2-c1d4-48e4-b933-473b08625676', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'sess-demo-007', 't', 'f', 'f', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-07 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('8849970f-193b-43fd-aa21-4a9bb12dfbf0', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'sess-demo-008', 't', 't', 'f', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-08 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('c9521d25-2825-4540-ad1b-42ff133f0d73', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', 'sess-demo-009', 't', 'f', 't', 'f', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-09 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('5f40c433-93a8-4233-8301-2a703c08c992', '22222222-2222-2222-2222-222222222222', NULL, 'sess-demo-010', 't', 't', 't', 't', '127.0.0.1', 'Mozilla/5.0 Demo', '2026-09-10 13:00:00+00', '2026-09-12 13:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('2cef3908-15d6-4c9e-a09b-99a9e493389e', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'sess-demo-011', 't', 'f', 'f', 'f', '192.168.1.10', 'Mozilla/5.0 Demo', '2026-09-11 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('18aa56ca-a2ba-4f9a-99a2-d1838c2e0777', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'sess-demo-012', 't', 't', 'f', 't', '192.168.1.11', 'Mozilla/5.0 Demo', '2026-09-12 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('2ba592ed-67da-44d6-8d30-fec7b12860f9', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'sess-demo-013', 't', 't', 't', 'f', '192.168.1.12', 'Mozilla/5.0 Demo', '2026-09-13 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('a799e6a9-4770-445d-8200-6913d5398590', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'sess-demo-014', 't', 'f', 'f', 't', '192.168.1.13', 'Mozilla/5.0 Demo', '2026-09-14 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('b269e74c-32dc-4062-8f58-47e22ebed3fe', '11111111-1111-1111-1111-111111111111', NULL, 'sess-demo-015', 't', 't', 'f', 't', '192.168.1.14', 'Mozilla/5.0 Demo', '2026-09-15 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('e59ad99e-3357-45ab-afe8-c541d5074c1b', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'sess-demo-016', 't', 'f', 't', 't', '192.168.1.15', 'Mozilla/5.0 Demo', '2026-09-16 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('96e4673b-9b7e-4e69-8629-dd88bb045ef4', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'sess-demo-017', 't', 't', 't', 'f', '192.168.1.16', 'Mozilla/5.0 Demo', '2026-09-17 13:00:00+00', '2026-09-18 13:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('55f820e9-a78d-4a80-af8d-537359ca15a7', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'sess-demo-018', 't', 't', 'f', 'f', '192.168.1.17', 'Mozilla/5.0 Demo', '2026-09-18 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('12f6852d-af31-4329-a5b0-68ab4ddc0fb5', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', 'sess-demo-019', 't', 'f', 'f', 't', '192.168.1.18', 'Mozilla/5.0 Demo', '2026-09-19 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_cookie_consents" VALUES ('e5c1ef2e-9755-427c-8013-572682cf237d', '22222222-2222-2222-2222-222222222222', NULL, 'sess-demo-020', 't', 't', 't', 't', '192.168.1.19', 'Mozilla/5.0 Demo', '2026-09-20 13:00:00+00', NULL, 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');

-- ----------------------------
-- Table structure for pdpa_dsar_requests
-- ----------------------------
DROP TABLE IF EXISTS "public"."pdpa_dsar_requests";
CREATE TABLE "public"."pdpa_dsar_requests" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'SUBMITTED'::character varying,
  "reason" varchar(500) COLLATE "pg_catalog"."default",
  "rejection_reason" varchar(500) COLLATE "pg_catalog"."default",
  "response_payload" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "submitted_at" timestamptz(6) NOT NULL DEFAULT now(),
  "verified_at" timestamptz(6),
  "completed_at" timestamptz(6),
  "deadline_at" timestamptz(6) NOT NULL,
  "version" int4 NOT NULL DEFAULT 1,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of pdpa_dsar_requests
-- ----------------------------
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('baaaa43d-e69a-40c6-9ceb-0680239b6625', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'ACCESS', 'SUBMITTED', 'ขอเข้าถึงข้อมูลส่วนบุคคล', NULL, '{}', '2026-09-01 09:00:00+00', NULL, NULL, '2026-10-01 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('a8e4e855-d740-4122-9207-a00c740293fe', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'ERASURE', 'VERIFIED', 'ขอลบข้อมูลส่วนบุคคล', NULL, '{}', '2026-09-02 09:00:00+00', '2026-09-03 09:00:00+00', NULL, '2026-10-02 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('3aabe30a-9f68-432e-ae58-b081cc45c90e', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'WITHDRAW_CONSENT', 'PROCESSING', 'ถอนความยินยอม', NULL, '{}', '2026-09-03 09:00:00+00', '2026-09-04 09:00:00+00', NULL, '2026-10-03 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('a5927caf-1036-4f8f-b9c7-48f963ce5c81', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'ACCESS', 'COMPLETED', 'ขอสำเนาข้อมูล', NULL, '{"format": "json"}', '2026-09-04 09:00:00+00', '2026-09-05 09:00:00+00', '2026-09-10 09:00:00+00', '2026-10-04 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('8d438981-ae7a-400c-839d-4a444f00a523', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'ERASURE', 'REJECTED', 'ขอลบข้อมูล', 'มีภาระผูกพันทางกฎหมาย', '{}', '2026-09-05 09:00:00+00', '2026-09-06 09:00:00+00', NULL, '2026-10-05 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('d60edf61-70eb-4c71-b30c-22239d716c8a', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'WITHDRAW_CONSENT', 'SUBMITTED', 'ถอนความยินยอม', NULL, '{}', '2026-09-06 09:00:00+00', NULL, NULL, '2026-10-06 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('8c6dc724-31eb-40fa-8cea-e6ef3cbe6966', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'ACCESS', 'VERIFIED', 'ขอเข้าถึงข้อมูล', NULL, '{}', '2026-09-07 09:00:00+00', '2026-09-08 09:00:00+00', NULL, '2026-10-07 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('1a956e62-c1ea-4290-b174-9ba905940633', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', 'ERASURE', 'PROCESSING', 'ขอลบข้อมูล', NULL, '{}', '2026-09-08 09:00:00+00', '2026-09-09 09:00:00+00', NULL, '2026-10-08 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('186a56e4-84c8-440e-8462-86625e022b00', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'WITHDRAW_CONSENT', 'COMPLETED', 'ถอนความยินยอม', NULL, '{"status": "done"}', '2026-09-09 09:00:00+00', '2026-09-10 09:00:00+00', '2026-09-12 09:00:00+00', '2026-10-09 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('af205f77-0f07-4db4-8041-666023a3e410', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'ACCESS', 'REJECTED', 'ขอเข้าถึงข้อมูล', 'คำขอไม่ครบถ้วน', '{}', '2026-09-10 09:00:00+00', '2026-09-11 09:00:00+00', NULL, '2026-10-10 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('043affb7-54b3-4c9b-844e-91f55fc86915', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'ACCESS', 'SUBMITTED', 'ขอเข้าถึงข้อมูล', NULL, '{}', '2026-09-11 09:00:00+00', NULL, NULL, '2026-10-11 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('5e10cad8-0a08-485c-9eb4-935c1af266c7', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', 'ERASURE', 'VERIFIED', 'ขอลบข้อมูล', NULL, '{}', '2026-09-12 09:00:00+00', '2026-09-13 09:00:00+00', NULL, '2026-10-12 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('4535cd55-fe5a-49dd-ae4f-b79337855559', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'WITHDRAW_CONSENT', 'PROCESSING', 'ถอนความยินยอม', NULL, '{}', '2026-09-13 09:00:00+00', '2026-09-14 09:00:00+00', NULL, '2026-10-13 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('1fb7a294-6df0-477f-aa13-e83981f2b324', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'ACCESS', 'COMPLETED', 'ขอสำเนาข้อมูล', NULL, '{"format": "csv"}', '2026-09-14 09:00:00+00', '2026-09-15 09:00:00+00', '2026-09-18 09:00:00+00', '2026-10-14 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('3a1d3bfb-6e57-4d84-9ac7-63bb005ccc37', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'ERASURE', 'REJECTED', 'ขอลบข้อมูล', 'ข้อมูลยังอยู่ในระยะเก็บรักษา', '{}', '2026-09-15 09:00:00+00', '2026-09-16 09:00:00+00', NULL, '2026-10-15 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('46448b6f-533e-4496-b625-450bdbfd8e69', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', 'WITHDRAW_CONSENT', 'SUBMITTED', 'ถอนความยินยอม', NULL, '{}', '2026-09-16 09:00:00+00', NULL, NULL, '2026-10-16 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('f1e6f157-bc75-4463-b9d4-11a56baba986', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'ACCESS', 'VERIFIED', 'ขอเข้าถึงข้อมูล', NULL, '{}', '2026-09-17 09:00:00+00', '2026-09-18 09:00:00+00', NULL, '2026-10-17 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('4bf00565-059f-41ed-9cbf-489408aed40d', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 'ERASURE', 'PROCESSING', 'ขอลบข้อมูล', NULL, '{}', '2026-09-18 09:00:00+00', '2026-09-19 09:00:00+00', NULL, '2026-10-18 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('7586d27d-421d-429b-9f18-a0e51c4ba6a7', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', 'WITHDRAW_CONSENT', 'COMPLETED', 'ถอนความยินยอม', NULL, '{"status": "done"}', '2026-09-19 09:00:00+00', '2026-09-20 09:00:00+00', '2026-09-21 09:00:00+00', '2026-10-19 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_dsar_requests" VALUES ('3d3b9db3-807c-4288-b84b-042927a117b3', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', 'ACCESS', 'REJECTED', 'ขอเข้าถึงข้อมูล', 'ยืนยันตัวตนไม่สำเร็จ', '{}', '2026-09-20 09:00:00+00', '2026-09-21 09:00:00+00', NULL, '2026-10-20 09:00:00+00', 1, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');

-- ----------------------------
-- Table structure for pdpa_idempotency_keys
-- ----------------------------
DROP TABLE IF EXISTS "public"."pdpa_idempotency_keys";
CREATE TABLE "public"."pdpa_idempotency_keys" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid,
  "idempotency_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "request_method" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "request_path" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "request_hash" char(64) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'IN_PROGRESS'::character varying,
  "response_status" int4,
  "response_body" jsonb,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of pdpa_idempotency_keys
-- ----------------------------
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('383b9f40-3694-4e35-8f88-f271457e8c08', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '3a4b5c6d-7e8f-4a1b-9c2d-3e4f5a6b7c8d', 'POST', '/api/v1/knowledges', 'demo-request-hash-0001                                          ', 'COMPLETED', 201, '{"id": "100b5c8b-a777-45db-97c4-cae0140ee339"}', '2026-09-01 10:00:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:00:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('4ceafcbe-ca0e-4263-8970-8344fbff4bf1', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', '1f2e3d4c-5b6a-4c7d-8e9f-0a1b2c3d4e5f', 'POST', '/api/v1/knowledges', 'demo-request-hash-0002                                          ', 'COMPLETED', 201, '{"id": "3e1c67cc-94ee-40b5-a725-8dc828106f75"}', '2026-09-01 10:05:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:05:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('b68137fc-625e-4d88-a7c7-1a51ad698ff1', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', '9a8b7c6d-5e4f-4a3b-2c1d-0e9f8a7b6c5d', 'POST', '/api/v1/keys', 'demo-request-hash-0003                                          ', 'COMPLETED', 201, '{"id": "16a113dd-c1e4-4e08-8576-b04a61656ddb"}', '2026-09-01 10:10:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:10:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('110184d6-d2de-406c-bde2-325afa9e06c4', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', '0d1e2f3a-4b5c-4d6e-7f8a-9b0c1d2e3f4a', 'POST', '/api/v1/auth/login', 'demo-request-hash-0004                                          ', 'COMPLETED', 200, '{"access_token": "demo"}', '2026-09-01 10:15:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:15:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('08cd6cc3-4b48-419d-b29c-c1950c62ce5b', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '5e6f7a8b-9c0d-4e1f-2a3b-4c5d6e7f8a9b', 'DELETE', '/api/v1/keys/16a113dd-c1e4-4e08-8576-b04a61656ddb', 'demo-request-hash-0005                                          ', 'COMPLETED', 204, NULL, '2026-09-01 10:20:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:20:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('29a87118-df3f-45f8-9942-5b733fd08efe', '11111111-1111-1111-1111-111111111111', 'e4461d77-2832-47d9-81ca-8c3b401cde56', '7c8d9e0f-1a2b-4c3d-4e5f-6a7b8c9d0e1f', 'POST', '/api/v1/notifications/broadcast', 'demo-request-hash-0006                                          ', 'IN_PROGRESS', NULL, NULL, '2026-09-01 10:25:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:25:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('c12738a5-4986-44bd-9491-fbb8484adc7d', '11111111-1111-1111-1111-111111111111', '0d610b48-e83a-4e81-8a25-d43296bf4521', '2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e', 'POST', '/api/v1/knowledges', 'demo-request-hash-0007                                          ', 'FAILED', 400, '{"error": "validation_error"}', '2026-09-01 10:30:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:30:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('2c7187d7-db6e-4383-8f6a-380c03518b3f', '11111111-1111-1111-1111-111111111111', 'd767edfd-e087-4885-9486-ffdc708d859d', '8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c', 'POST', '/api/v1/keys', 'demo-request-hash-0008                                          ', 'COMPLETED', 201, '{"id": "99237e05-c08e-46ae-8670-7078e8c90f49"}', '2026-09-01 10:35:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:35:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('1e22faa6-88eb-499c-9a55-aed0b9d8e106', '11111111-1111-1111-1111-111111111111', NULL, '4d5e6f7a-8b9c-4d0e-1f2a-3b4c5d6e7f8a', 'POST', '/api/v1/auth/login', 'demo-request-hash-0009                                          ', 'COMPLETED', 200, '{"access_token": "anon-demo"}', '2026-09-01 10:40:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:40:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('a87d0df4-4e8b-484c-b152-e47baeaf8445', '11111111-1111-1111-1111-111111111111', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '6a7b8c9d-0e1f-4a2b-3c4d-5e6f7a8b9c0d', 'POST', '/api/v1/dsar', 'demo-request-hash-0010                                          ', 'COMPLETED', 201, '{"id": "dsar-demo-001"}', '2026-09-01 10:45:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 10:45:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('918507b8-27dd-4cc7-89e8-635e61a18b89', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '1c2d3e4f-5a6b-4c7d-8e9f-0a1b2c3d4e5f', 'POST', '/api/v1/knowledges', 'demo-request-hash-0011                                          ', 'COMPLETED', 201, '{"id": "knowledge-demo-011"}', '2026-09-01 11:00:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:00:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('2b024cc3-03fb-4237-a7c8-f3baeb59da88', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', '9e0f1a2b-3c4d-4e5f-6a7b-8c9d0e1f2a3b', 'POST', '/api/v1/keys', 'demo-request-hash-0012                                          ', 'COMPLETED', 201, '{"id": "key-demo-012"}', '2026-09-01 11:05:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:05:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('68289b2e-dbd9-4fa2-8b50-f373258e4b91', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', '3f4a5b6c-7d8e-4f9a-0b1c-2d3e4f5a6b7c', 'POST', '/api/v1/auth/login', 'demo-request-hash-0013                                          ', 'COMPLETED', 200, '{"access_token": "demo-222"}', '2026-09-01 11:10:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:10:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('dab450d7-228c-4c3f-817f-9fa07d5a363e', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', '5b6c7d8e-9f0a-4b1c-2d3e-4f5a6b7c8d9e', 'DELETE', '/api/v1/keys/99237e05-c08e-46ae-8670-7078e8c90f49', 'demo-request-hash-0014                                          ', 'COMPLETED', 204, NULL, '2026-09-01 11:15:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:15:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('00abb8f8-a659-4763-994b-dde3cc48e306', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '7d8e9f0a-1b2c-4d3e-4f5a-6b7c8d9e0f1a', 'POST', '/api/v1/notifications/broadcast', 'demo-request-hash-0015                                          ', 'IN_PROGRESS', NULL, NULL, '2026-09-01 11:20:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:20:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('dcaf8770-f6cc-44bb-9ae5-3794d15b2417', '22222222-2222-2222-2222-222222222222', 'e4461d77-2832-47d9-81ca-8c3b401cde56', '2f3a4b5c-6d7e-4f8a-9b0c-1d2e3f4a5b6c', 'POST', '/api/v1/knowledges', 'demo-request-hash-0016                                          ', 'FAILED', 400, '{"error": "duplicate_name"}', '2026-09-01 11:25:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:25:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('bf08b5a2-0050-4535-a2dd-a23971e014f0', '22222222-2222-2222-2222-222222222222', '0d610b48-e83a-4e81-8a25-d43296bf4521', '8a9b0c1d-2e3f-4a4b-5c6d-7e8f9a0b1c2d', 'POST', '/api/v1/keys', 'demo-request-hash-0017                                          ', 'COMPLETED', 201, '{"id": "key-demo-017"}', '2026-09-01 11:30:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:30:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('a7b802ea-c81f-437d-99e8-da21d553314a', '22222222-2222-2222-2222-222222222222', 'd767edfd-e087-4885-9486-ffdc708d859d', '4b5c6d7e-8f9a-4b0c-1d2e-3f4a5b6c7d8e', 'POST', '/api/v1/auth/login', 'demo-request-hash-0018                                          ', 'COMPLETED', 200, '{"access_token": "demo-222b"}', '2026-09-01 11:35:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:35:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('1b427433-4885-494e-84ee-32b3ec955e2b', '22222222-2222-2222-2222-222222222222', NULL, '6c7d8e9f-0a1b-4c2d-3e4f-5a6b7c8d9e0f', 'POST', '/api/v1/auth/login', 'demo-request-hash-0019                                          ', 'COMPLETED', 200, '{"access_token": "anon-222"}', '2026-09-01 11:40:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:40:00+00');
INSERT INTO "public"."pdpa_idempotency_keys" VALUES ('8cecad39-fcd4-4c4c-95fe-7599ec221af0', '22222222-2222-2222-2222-222222222222', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '1e2f3a4b-5c6d-4e7f-8a9b-0c1d2e3f4a5b', 'POST', '/api/v1/dsar', 'demo-request-hash-0020                                          ', 'COMPLETED', 201, '{"id": "dsar-demo-020"}', '2026-09-01 11:45:00+00', '2026-09-22 14:17:50.958643+00', '2026-09-02 11:45:00+00');

-- ----------------------------
-- Table structure for pdpa_privacy_policies
-- ----------------------------
DROP TABLE IF EXISTS "public"."pdpa_privacy_policies";
CREATE TABLE "public"."pdpa_privacy_policies" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "version" int4 NOT NULL,
  "content_th" text COLLATE "pg_catalog"."default" NOT NULL,
  "content_en" text COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'DRAFT'::character varying,
  "effective_from" timestamptz(6) NOT NULL DEFAULT now(),
  "published_at" timestamptz(6),
  "superseded_at" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of pdpa_privacy_policies
-- ----------------------------
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('d77c2fc2-efcb-4a6b-b195-3ebbdbad542c', '11111111-1111-1111-1111-111111111111', 1, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 1', 'Privacy policy version 1', 'PUBLISHED', '2026-01-01 00:00:00+00', '2026-01-01 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('941a1406-3e70-4b08-a96f-2d7b19b5333b', '11111111-1111-1111-1111-111111111111', 2, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 2', 'Privacy policy version 2', 'SUPERSEDED', '2026-02-01 00:00:00+00', '2026-02-01 00:00:00+00', '2026-03-01 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('1f347d7b-e1ef-428e-8e94-ed817f4a0df9', '11111111-1111-1111-1111-111111111111', 3, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 3', 'Privacy policy version 3', 'ARCHIVED', '2026-03-01 00:00:00+00', '2026-03-01 00:00:00+00', '2026-04-01 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('1c520458-db91-4771-ba65-9b0fc9eac829', '11111111-1111-1111-1111-111111111111', 4, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 4', 'Privacy policy version 4', 'DRAFT', '2026-04-01 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('41c7a961-eace-4313-b0e2-d5cf09c72b00', '11111111-1111-1111-1111-111111111111', 5, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 5', 'Privacy policy version 5', 'PUBLISHED', '2026-05-01 00:00:00+00', '2026-05-01 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('5aa913a8-574c-4867-ac81-b72bba7bf2ab', '11111111-1111-1111-1111-111111111111', 6, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 6', 'Privacy policy version 6', 'SUPERSEDED', '2026-06-01 00:00:00+00', '2026-06-01 00:00:00+00', '2026-07-01 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('015749d4-e25a-45af-8ecd-5db8ebafe628', '11111111-1111-1111-1111-111111111111', 7, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 7', 'Privacy policy version 7', 'ARCHIVED', '2026-07-01 00:00:00+00', '2026-07-01 00:00:00+00', '2026-08-01 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('ed0b7a3d-db3a-421d-9012-08b55c03765d', '11111111-1111-1111-1111-111111111111', 8, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 8', 'Privacy policy version 8', 'DRAFT', '2026-08-01 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('381b4915-2490-4160-9180-7947d522c84c', '11111111-1111-1111-1111-111111111111', 9, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 9', 'Privacy policy version 9', 'PUBLISHED', '2026-09-01 00:00:00+00', '2026-09-01 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('976442fd-3b8d-4c89-aec3-5a94225f84c5', '11111111-1111-1111-1111-111111111111', 10, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 10', 'Privacy policy version 10', 'DRAFT', '2026-10-01 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('5580f158-5141-4675-9c88-4550459c8684', '22222222-2222-2222-2222-222222222222', 1, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 1', 'Privacy policy version 1', 'PUBLISHED', '2026-01-15 00:00:00+00', '2026-01-15 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('2e5eecc0-f393-4e8c-80b0-5f358e36d11a', '22222222-2222-2222-2222-222222222222', 2, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 2', 'Privacy policy version 2', 'SUPERSEDED', '2026-02-15 00:00:00+00', '2026-02-15 00:00:00+00', '2026-03-15 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('eb0699cf-9bc3-4b7c-ab23-b3f7eafc68b9', '22222222-2222-2222-2222-222222222222', 3, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 3', 'Privacy policy version 3', 'ARCHIVED', '2026-03-15 00:00:00+00', '2026-03-15 00:00:00+00', '2026-04-15 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('32475d60-a0a4-4793-862b-d194f587b0e4', '22222222-2222-2222-2222-222222222222', 4, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 4', 'Privacy policy version 4', 'DRAFT', '2026-04-15 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('86e497fc-951c-44de-81f5-3948ceb01353', '22222222-2222-2222-2222-222222222222', 5, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 5', 'Privacy policy version 5', 'PUBLISHED', '2026-05-15 00:00:00+00', '2026-05-15 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('f3f236ef-46e7-4ba5-912e-f5eefef1e683', '22222222-2222-2222-2222-222222222222', 6, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 6', 'Privacy policy version 6', 'SUPERSEDED', '2026-06-15 00:00:00+00', '2026-06-15 00:00:00+00', '2026-07-15 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('72ba90f5-f209-4855-9651-1dcf6c101903', '22222222-2222-2222-2222-222222222222', 7, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 7', 'Privacy policy version 7', 'ARCHIVED', '2026-07-15 00:00:00+00', '2026-07-15 00:00:00+00', '2026-08-15 00:00:00+00', '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('c4b84424-1252-4f38-b9a2-2ba0b5cbc553', '22222222-2222-2222-2222-222222222222', 8, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 8', 'Privacy policy version 8', 'DRAFT', '2026-08-15 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('8b24d0dc-3af0-4116-b1ce-70d7c1fff289', '22222222-2222-2222-2222-222222222222', 9, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 9', 'Privacy policy version 9', 'PUBLISHED', '2026-09-15 00:00:00+00', '2026-09-15 00:00:00+00', NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');
INSERT INTO "public"."pdpa_privacy_policies" VALUES ('ef877bd3-4a6b-496e-8481-071ce31ceea3', '22222222-2222-2222-2222-222222222222', 10, 'นโยบายความเป็นส่วนตัวเวอร์ชัน 10', 'Privacy policy version 10', 'DRAFT', '2026-10-15 00:00:00+00', NULL, NULL, '2026-09-22 14:14:18.960086+00', '2026-09-22 14:14:18.960086+00');

-- ----------------------------
-- Table structure for rag_chunks
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_chunks";
CREATE TABLE "public"."rag_chunks" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "document_id" uuid NOT NULL,
  "ordinal" int4 NOT NULL DEFAULT 0,
  "content" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "token_count" int4 NOT NULL DEFAULT 0,
  "embedding_id" uuid,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_chunks
-- ----------------------------

-- ----------------------------
-- Table structure for rag_citations
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_citations";
CREATE TABLE "public"."rag_citations" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "run_id" uuid NOT NULL,
  "chunk_id" uuid NOT NULL,
  "document_id" uuid NOT NULL,
  "score" float8 NOT NULL DEFAULT 0,
  "rank" int4 NOT NULL DEFAULT 0,
  "snippet" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_citations
-- ----------------------------

-- ----------------------------
-- Table structure for rag_documents
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_documents";
CREATE TABLE "public"."rag_documents" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "source_uri" varchar(1000) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "mime_type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "title" varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "content" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "hash" varchar(128) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'PENDING'::character varying,
  "size_bytes" int4 NOT NULL DEFAULT 0,
  "chunk_count" int4 NOT NULL DEFAULT 0,
  "metadata_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_documents
-- ----------------------------

-- ----------------------------
-- Table structure for rag_pipelines
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_pipelines";
CREATE TABLE "public"."rag_pipelines" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "chunker_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'recursive'::character varying,
  "chunk_size" int4 NOT NULL DEFAULT 512,
  "chunk_overlap" int4 NOT NULL DEFAULT 50,
  "retriever_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'vector'::character varying,
  "top_k" int4 NOT NULL DEFAULT 5,
  "reranker_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'none'::character varying,
  "embedding_model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'text-embedding-3-small'::character varying,
  "generation_model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'gpt-4o-mini'::character varying,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_pipelines
-- ----------------------------

-- ----------------------------
-- Table structure for rag_retrieval_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_retrieval_logs";
CREATE TABLE "public"."rag_retrieval_logs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "run_id" uuid NOT NULL,
  "stage" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'retrieve'::character varying,
  "top_k" int4 NOT NULL DEFAULT 0,
  "candidates_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_retrieval_logs
-- ----------------------------

-- ----------------------------
-- Table structure for rag_runs
-- ----------------------------
DROP TABLE IF EXISTS "public"."rag_runs";
CREATE TABLE "public"."rag_runs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "pipeline_id" uuid,
  "conversation_id" uuid,
  "query" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "answer" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "model_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "total_tokens" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'QUEUED'::character varying,
  "error_message" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of rag_runs
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_control
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_control";
CREATE TABLE "public"."sd_air_control" (
  "tenant_id" uuid NOT NULL,
  "air_control_id" int4 NOT NULL DEFAULT nextval('sd_air_control_air_control_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "active" int4,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_control
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_control_device_map
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_control_device_map";
CREATE TABLE "public"."sd_air_control_device_map" (
  "tenant_id" uuid NOT NULL,
  "air_control_id" int4,
  "device_id" int4,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_control_device_map
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_control_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_control_log";
CREATE TABLE "public"."sd_air_control_log" (
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4,
  "air_control_id" int4,
  "device_id" int4,
  "type_id" int4,
  "temperature" varchar(255) COLLATE "pg_catalog"."default",
  "warning" varchar(255) COLLATE "pg_catalog"."default",
  "recovery" varchar(150) COLLATE "pg_catalog"."default",
  "period" varchar(150) COLLATE "pg_catalog"."default",
  "percent" varchar(150) COLLATE "pg_catalog"."default",
  "firealarm" varchar(150) COLLATE "pg_catalog"."default",
  "humidityalarm" varchar(150) COLLATE "pg_catalog"."default",
  "air2_alarm" varchar(150) COLLATE "pg_catalog"."default",
  "air1_alarm" varchar(150) COLLATE "pg_catalog"."default",
  "temperaturealarm" varchar(150) COLLATE "pg_catalog"."default",
  "mode" varchar(150) COLLATE "pg_catalog"."default",
  "state_air1" varchar(150) COLLATE "pg_catalog"."default",
  "state_air2" varchar(150) COLLATE "pg_catalog"."default",
  "temperaturealarmoff" varchar(150) COLLATE "pg_catalog"."default",
  "ups_alarm" varchar(150) COLLATE "pg_catalog"."default",
  "ups2_alarm" varchar(150) COLLATE "pg_catalog"."default",
  "hssdalarm" varchar(150) COLLATE "pg_catalog"."default",
  "waterleakalarm" varchar(150) COLLATE "pg_catalog"."default",
  "date" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_control_log
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_mod
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_mod";
CREATE TABLE "public"."sd_air_mod" (
  "tenant_id" uuid NOT NULL,
  "air_mod_id" int4 NOT NULL DEFAULT nextval('sd_air_mod_air_mod_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "active" int4,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_mod
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_mod_device_map
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_mod_device_map";
CREATE TABLE "public"."sd_air_mod_device_map" (
  "tenant_id" uuid NOT NULL,
  "air_mod_id" int4,
  "air_control_id" int4,
  "device_id" int4,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_mod_device_map
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_period
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_period";
CREATE TABLE "public"."sd_air_period" (
  "tenant_id" uuid NOT NULL,
  "air_period_id" int4 NOT NULL DEFAULT nextval('sd_air_period_air_period_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "active" int4,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_period
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_period_device_map
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_period_device_map";
CREATE TABLE "public"."sd_air_period_device_map" (
  "tenant_id" uuid NOT NULL,
  "air_period_id" int4,
  "air_control_id" int4,
  "device_id" int4,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_period_device_map
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_setting_warning
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_setting_warning";
CREATE TABLE "public"."sd_air_setting_warning" (
  "tenant_id" uuid NOT NULL,
  "air_setting_warning_id" int4 NOT NULL DEFAULT nextval('sd_air_setting_warning_air_setting_warning_id_seq'::regclass),
  "type_id" int4,
  "device_id" int4,
  "period_id" int4,
  "event_name" varchar(255) COLLATE "pg_catalog"."default",
  "date" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "active" int4,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_setting_warning
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_setting_warning_device_map
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_setting_warning_device_map";
CREATE TABLE "public"."sd_air_setting_warning_device_map" (
  "tenant_id" uuid NOT NULL,
  "air_setting_warning_id" int4,
  "air_control_id" int4,
  "device_id" int4,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_setting_warning_device_map
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_warning
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_warning";
CREATE TABLE "public"."sd_air_warning" (
  "tenant_id" uuid NOT NULL,
  "air_warning_id" int4 NOT NULL DEFAULT nextval('sd_air_warning_air_warning_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "data" varchar(255) COLLATE "pg_catalog"."default",
  "status" varchar(150) COLLATE "pg_catalog"."default",
  "active" int4,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_warning
-- ----------------------------

-- ----------------------------
-- Table structure for sd_air_warning_device_map
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_air_warning_device_map";
CREATE TABLE "public"."sd_air_warning_device_map" (
  "tenant_id" uuid NOT NULL,
  "air_warning_id" int4,
  "air_control_id" int4,
  "device_id" int4,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_air_warning_device_map
-- ----------------------------

-- ----------------------------
-- Table structure for sd_alarm_process_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_alarm_process_log";
CREATE TABLE "public"."sd_alarm_process_log" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "type_id" int4 NOT NULL,
  "event" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_type" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "status_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email_alarm" int4 NOT NULL,
  "line_alarm" int4 NOT NULL,
  "telegram_alarm" int4 NOT NULL,
  "sms_alarm" int4 NOT NULL,
  "nonc_alarm" int4 NOT NULL,
  "status" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "date" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "data_alarm" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_status" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "subject" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of sd_alarm_process_log
-- ----------------------------

-- ----------------------------
-- Table structure for sd_alarm_process_log_email
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_alarm_process_log_email";
CREATE TABLE "public"."sd_alarm_process_log_email" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "type_id" int4 NOT NULL,
  "event" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_type" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "status_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email_alarm" int4 NOT NULL,
  "line_alarm" int4 NOT NULL,
  "telegram_alarm" int4 NOT NULL,
  "sms_alarm" int4 NOT NULL,
  "nonc_alarm" int4 NOT NULL,
  "status" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "date" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "data_alarm" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_status" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "subject" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of sd_alarm_process_log_email
-- ----------------------------

-- ----------------------------
-- Table structure for sd_alarm_process_log_temp
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_alarm_process_log_temp";
CREATE TABLE "public"."sd_alarm_process_log_temp" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "type_id" int4 NOT NULL,
  "event" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_type" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "status_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email_alarm" int4 NOT NULL,
  "line_alarm" int4 NOT NULL,
  "telegram_alarm" int4 NOT NULL,
  "sms_alarm" int4 NOT NULL,
  "nonc_alarm" int4 NOT NULL,
  "status" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "date" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "data_alarm" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "alarm_status" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "subject" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content" varchar(255) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of sd_alarm_process_log_temp
-- ----------------------------

-- ----------------------------
-- Table structure for sd_api_key
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_api_key";
CREATE TABLE "public"."sd_api_key" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_api_key_id_seq'::regclass),
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "api_key" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "api_secret" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar(255) COLLATE "pg_catalog"."default",
  "permissions" jsonb,
  "expires_at" timestamptz(6),
  "last_used_at" timestamptz(6),
  "usage_count" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "ip_whitelist" jsonb,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_api_key
-- ----------------------------

-- ----------------------------
-- Table structure for sd_audit_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_audit_log";
CREATE TABLE "public"."sd_audit_log" (
  "tenant_id" uuid NOT NULL,
  "audit_id" int4 NOT NULL DEFAULT nextval('sd_audit_log_audit_id_seq'::regclass),
  "user_id" varchar COLLATE "pg_catalog"."default",
  "user_name" varchar(200) COLLATE "pg_catalog"."default",
  "action" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "entity_type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "entity_id" int4 NOT NULL,
  "before" jsonb,
  "after" jsonb,
  "changes" jsonb,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default",
  "user_agent" text COLLATE "pg_catalog"."default",
  "action_time" timestamptz(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_audit_log
-- ----------------------------

-- ----------------------------
-- Table structure for sd_channel_template
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_channel_template";
CREATE TABLE "public"."sd_channel_template" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_channel_template_id_seq'::regclass),
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "channel_id" int4 NOT NULL,
  "notification_type_id" int4 NOT NULL,
  "template" text COLLATE "pg_catalog"."default" NOT NULL,
  "variables" jsonb,
  "is_active" bool NOT NULL,
  "is_default" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_channel_template
-- ----------------------------

-- ----------------------------
-- Table structure for sd_device_category
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_category";
CREATE TABLE "public"."sd_device_category" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_category_id_seq'::regclass),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "icon" varchar(100) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_category
-- ----------------------------
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 1, 'Category 01', 'Device category 1', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 2, 'Category 02', 'Device category 2', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 3, 'Category 03', 'Device category 3', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 4, 'Category 04', 'Device category 4', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 5, 'Category 05', 'Device category 5', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 6, 'Category 06', 'Device category 6', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 7, 'Category 07', 'Device category 7', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 8, 'Category 08', 'Device category 8', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 9, 'Category 09', 'Device category 9', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 10, 'Category 10', 'Device category 10', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 11, 'Category 11', 'Device category 11', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 12, 'Category 12', 'Device category 12', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 13, 'Category 13', 'Device category 13', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 14, 'Category 14', 'Device category 14', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 15, 'Category 15', 'Device category 15', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 16, 'Category 16', 'Device category 16', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 17, 'Category 17', 'Device category 17', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 18, 'Category 18', 'Device category 18', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 19, 'Category 19', 'Device category 19', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');
INSERT INTO "public"."sd_device_category" VALUES ('11111111-1111-1111-1111-111111111111', 20, 'Category 20', 'Device category 20', 'thermometer', '2026-09-23 07:50:24.698421+00', '2026-09-23 07:50:24.698421+00');

-- ----------------------------
-- Table structure for sd_device_group
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_group";
CREATE TABLE "public"."sd_device_group" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_group_id_seq'::regclass),
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "group_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "config" jsonb,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_group
-- ----------------------------

-- ----------------------------
-- Table structure for sd_device_member
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_member";
CREATE TABLE "public"."sd_device_member" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_member_id_seq'::regclass),
  "Device_id" int4 NOT NULL,
  "group_id" int4 NOT NULL,
  "role" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "priority" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_member
-- ----------------------------

-- ----------------------------
-- Table structure for sd_device_notification_config
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_notification_config";
CREATE TABLE "public"."sd_device_notification_config" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_notification_config_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "notification_channel_id" int4 NOT NULL,
  "notification_type_id" int4 NOT NULL,
  "config" jsonb,
  "is_active" bool NOT NULL,
  "retry_count" int4 NOT NULL,
  "retry_delay_minutes" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_notification_config
-- ----------------------------

-- ----------------------------
-- Table structure for sd_device_schedule
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_schedule";
CREATE TABLE "public"."sd_device_schedule" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_schedule_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "schedule_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "schedule_config" jsonb NOT NULL,
  "action" jsonb NOT NULL,
  "is_active" bool NOT NULL,
  "last_run_at" timestamptz(6),
  "next_run_at" timestamptz(6),
  "run_count" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_schedule
-- ----------------------------

-- ----------------------------
-- Table structure for sd_device_status_history
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_device_status_history";
CREATE TABLE "public"."sd_device_status_history" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_device_status_history_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "status" varchar(50) COLLATE "pg_catalog"."default",
  "value" numeric(10,2),
  "notification_type_id" int4,
  "duration_minutes" int4,
  "previous_status" varchar(50) COLLATE "pg_catalog"."default",
  "previous_value" numeric(10,2),
  "change_reason" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_device_status_history
-- ----------------------------

-- ----------------------------
-- Table structure for sd_group_notification_config
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_group_notification_config";
CREATE TABLE "public"."sd_group_notification_config" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_group_notification_config_id_seq'::regclass),
  "group_id" int4 NOT NULL,
  "notification_channel_id" int4 NOT NULL,
  "notification_type_id" int4 NOT NULL,
  "config" jsonb,
  "is_active" bool NOT NULL,
  "escalation_level" int4 NOT NULL,
  "escalation_delay_minutes" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_group_notification_config
-- ----------------------------

-- ----------------------------
-- Table structure for sd_iot_alarm_device
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_alarm_device";
CREATE TABLE "public"."sd_iot_alarm_device" (
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_alarm_device
-- ----------------------------
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 2, 6, '25a81485-96b4-4c20-a74d-9c1208f2eeed', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 3, 11, 'e89d8985-8fc4-4f6e-ad23-9a8edb8ba400', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 4, 16, 'a25c5960-63b6-4f6d-93c8-db286af9c13b', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 5, 21, 'be677b44-39a4-49a0-91ef-93268d981524', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 6, 26, '7700f5ad-3b60-478b-bebf-28fd149271bd', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 7, 31, 'fbd8140c-3fe4-4e42-ba96-9249d6d95976', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 8, 36, '9ab2e205-9aa7-4061-be19-8efcb268698c', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 9, 41, '9d81bde3-c285-4dc5-91a9-853782f35b43', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 10, 46, 'fe356905-1089-4a10-909e-4fa4e3d914ab', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 11, 51, '8134bca6-46be-4263-93f0-ff07d02b1c02', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 12, 56, '193a7a5f-b750-4efa-ae5f-09540851bd31', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 13, 61, '4af67817-c401-4771-aa5f-269e7a22e72a', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 14, 66, 'c58feb49-b786-48e8-b445-f3f4fd4ae34e', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 15, 71, '4d58fdac-ed04-461e-943c-d2d144e27d89', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 16, 76, '45dd0b80-527f-4dc4-9d78-60f75a6210bd', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 17, 81, '553466af-d89d-4763-bd6e-51ea2b408457', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 18, 86, '6990b06f-9d2d-4dbb-99b3-14e7c8a66c14', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 19, 91, 'bbeaa734-068e-486e-a74a-4f2af9b13872', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 20, 96, '6a63b8c0-41db-4dc0-896f-660e54ef5295', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 1, 101, '273a4962-ded7-4411-ac3e-8c7d4147398b', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 2, 106, '6f60a327-ef4c-4c67-8c9f-d0aa86bfc3b7', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 3, 111, '5b859380-56b8-4055-90fe-24d8d2f18c33', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 4, 116, '3fe8e6f0-83be-4719-a42d-729ad28408d9', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 5, 121, 'dc3fc406-201c-43ca-a492-4a8bae35df88', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 6, 126, '5776a666-d3da-4b20-81fb-ab56a227566c', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 7, 131, '16bfea25-6796-4bb4-8c6a-0d7e7c07d724', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 8, 136, '86abd6d0-d3fd-48a5-b569-4dd2ebbd201d', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 9, 141, 'cbe62e43-ef55-448a-ae69-9a05aa59422b', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 10, 146, '0a8db8d5-6cde-4c07-98c1-0ec36aeed6db', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 11, 151, '5a2e8b44-6f7c-4315-9da7-9d1ff976bcf3', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 12, 156, '7df164b7-817a-46c0-8e93-8b193ebd3522', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 13, 161, '442cc83b-bec0-48d3-af43-c47e9196a1d7', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 14, 166, 'aa29033b-b3fc-4699-af49-4649c8d2899b', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 15, 171, '1ab9f261-de7b-42fa-aa57-96ca8c3ab7ab', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 16, 176, 'a36a9f25-be37-455c-856b-ad53e1f6e421', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 17, 181, 'e7b7e451-87e5-42f9-85d9-189d7fd289f8', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 18, 186, '6d1a63ae-83fd-4836-a319-23770b129abb', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 19, 191, 'f9670bb9-93e4-4788-bddc-5c0ff80f8621', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 20, 196, '4fa5df61-be1a-4e2d-bed8-b9e4e49e1733', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 1, 1, 'ce06f555-8df2-4368-8243-394d425529f2', 't', '2026-09-23 07:50:24.718833+00', '2026-09-23 07:50:24.718833+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 2, 6, '98962ae2-e0bb-4ea8-b1da-d3f6fe23be7c', 't', '2026-09-27 02:50:41.701851+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 3, 11, 'aaeb1fdb-41e8-4d24-a117-efe251a91e7a', 't', '2026-08-22 06:17:36.865029+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 4, 16, '7b30423b-0e8d-454a-9a15-75105b6a491f', 't', '2026-08-28 15:44:36.207146+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 5, 21, 'd036bcef-93a9-4c41-b148-5230d83c37c3', 't', '2026-07-17 07:10:45.284203+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 6, 26, '58f97296-22ef-4498-a695-c858e9336a52', 't', '2026-08-17 02:17:55.180648+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 7, 31, '39522262-c334-4fdd-8834-9ab4e9ebe201', 't', '2026-09-12 09:57:43.481723+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 8, 36, 'd0e4eb3f-0f22-442a-a888-2dcfea1ba093', 't', '2026-07-23 23:55:17.294103+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 9, 41, '3b67c42e-47a6-4b8b-bc8e-2b5fba58ecbb', 't', '2026-07-09 08:07:57.608597+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 10, 46, '90183ebd-5451-4a34-894f-3d77b2cbacc2', 't', '2026-09-14 14:08:32.541919+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 11, 51, 'a7dce8af-ecf3-4736-b810-9e2184320230', 't', '2026-09-21 01:15:03.456367+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 12, 56, '776977d1-59f2-40d5-a68d-10f40f8eb46e', 't', '2026-08-21 17:17:17.823451+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 13, 61, 'aa979f7a-f841-46cb-8714-52fd56fdf21f', 't', '2026-07-07 05:31:44.232042+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 14, 66, 'ff32836e-b694-4deb-97b3-07abf83fb224', 't', '2026-07-16 00:10:51.012103+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 15, 71, '236025b5-d240-4b96-b9ea-8ff77b9ad3cf', 't', '2026-07-18 08:28:16.157895+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 16, 76, '7a751e75-88ef-4496-89c4-5dfe146a8aed', 't', '2026-07-09 21:03:13.985872+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 17, 81, '8b8648ed-4e9f-4597-8c7a-cbeb7957f84c', 't', '2026-09-08 03:14:24.297978+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 18, 86, '68be37d3-e315-4bb2-b373-061dcfdce04d', 't', '2026-09-23 09:40:18.94098+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 19, 91, 'b49b9843-0ff5-4a7b-b571-379162485abb', 't', '2026-07-01 14:33:14.594493+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 20, 96, 'f3d2892f-8949-4025-a7f5-60410a1fe734', 't', '2026-07-04 13:26:44.411735+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 1, 101, '52baa1ed-bcb9-4b7e-a231-8f08b2d44340', 't', '2026-08-17 12:35:21.870861+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 2, 106, '5bac98cd-2004-427f-859f-dd995573c478', 't', '2026-09-27 11:19:21.417474+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 3, 111, '07ac7914-a25b-41c0-b758-ff9e1e830988', 't', '2026-09-25 19:39:04.444616+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 4, 116, '99240bd6-7840-4b16-9c4e-c1eb2b979f0c', 't', '2026-08-28 04:41:03.627139+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 5, 121, '3b672a36-e5b8-41fc-ac7b-55ce5aa85d5e', 't', '2026-09-26 05:37:20.618937+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 6, 126, '6feb60f9-901d-4dfd-b896-401072dcb009', 't', '2026-09-15 18:53:13.796404+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 7, 131, 'bc8f45b2-d048-435f-aaf9-257a88f7e63b', 't', '2026-07-14 07:23:51.370432+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 8, 136, '1055724e-e5d6-4aad-9782-c44fda0ba126', 't', '2026-07-23 18:18:10.909968+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 9, 141, 'c64305bd-2266-4467-aa7f-4a1fb209021a', 't', '2026-07-29 19:00:23.760277+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 10, 146, '333d69be-b630-4a30-a798-42c89c86516f', 't', '2026-09-15 14:36:50.110848+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 11, 151, 'be43b8ce-404d-4f5d-90d4-4a9768dc56e1', 't', '2026-07-19 21:19:48.983572+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 12, 156, '6928f1e7-ae70-45a5-a721-def8a21b2e6f', 't', '2026-07-23 03:11:59.235668+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 13, 161, 'aa35034a-4451-4c36-a298-0f6ce27bd08d', 't', '2026-09-02 19:18:21.000778+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 14, 166, 'fcbce6d1-092a-41bb-a710-f1a92b69f37c', 't', '2026-08-28 18:23:47.149117+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 15, 171, '739bf744-f48b-4464-aa24-fc3116d3d376', 't', '2026-08-20 21:33:46.912403+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 16, 176, 'b3ebcef6-65e8-46d1-af25-d608f45b4100', 't', '2026-08-10 04:17:07.963269+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 17, 181, '99a5907a-789f-492f-9b64-7e4a9e73f39f', 't', '2026-08-19 01:09:53.715335+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 18, 186, '28bd2789-3cad-429d-93f5-3f1e8419bff0', 't', '2026-08-26 14:37:41.742045+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('33333333-3333-3333-3333-333333333333', 19, 191, '75c4e9db-64da-44e2-8e85-adadab0ab8b6', 't', '2026-08-21 14:13:01.278319+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('11111111-1111-1111-1111-111111111111', 20, 196, '977aac9d-ce7d-4ddf-bbf6-7db2866fe318', 't', '2026-07-20 03:09:36.897666+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device" VALUES ('22222222-2222-2222-2222-222222222222', 1, 1, 'd842c9de-afe5-4486-a462-48278bfe850a', 't', '2026-09-28 01:56:33.300173+00', '2026-09-28 13:34:28.774661+00');

-- ----------------------------
-- Table structure for sd_iot_alarm_device_event
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_alarm_device_event";
CREATE TABLE "public"."sd_iot_alarm_device_event" (
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_alarm_device_event
-- ----------------------------
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 2, 8, 'ed09faea-11c7-424b-9298-bdf4d40c2c80', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 3, 15, 'c0ee2d44-1e26-484e-a967-e30901739212', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 4, 22, '9534b57a-289b-4860-9c5d-824cb0a4718e', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 5, 29, '2a25e2be-3d33-44b1-9b9a-b5afecc2fe6a', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 6, 36, '6235a325-494a-430c-b670-e8e489a36423', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 7, 43, '578261dc-e1a6-4eea-a2fe-f74ffbcbca80', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 8, 50, 'f749f613-d259-486a-ace2-c9d7ae5e0e86', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 9, 57, '6029e246-f1e3-4dd9-bba1-88d5f441f553', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 10, 64, '7a75fa41-b46a-4ad4-b84e-1dbe32249f70', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 11, 71, 'db4e6115-0460-418c-bdfe-b1a07efa3a77', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 12, 78, 'd3f87394-689a-4c2f-ad30-9246eff27b4d', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 13, 85, 'afb6699b-4bdc-44e3-8eca-94e0f127c53f', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 14, 92, 'b9b1a0a3-fde6-44dd-8c60-fac005a86d92', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 15, 99, '36c222c8-54ba-4632-8879-535552f90b35', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 16, 106, 'a2dfc547-cf00-4834-b095-a6d2afb204c1', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 17, 113, 'edcfacec-b63f-4470-ab7c-e9ef94550fee', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 18, 120, '54f5ee97-9b27-4568-9e86-b83bf11fbaa0', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 19, 127, '6a8b061b-060f-434b-aebb-39d9c400d73e', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 20, 134, '4ab18900-4d30-4d5a-9a1a-b4ca96b9cfe8', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 1, 141, '2079fca0-e22b-4cc1-a29a-4cfd2a91dfa3', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 2, 148, '41e8d5dc-a7ca-4c8c-b132-dcb0e432b97d', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 3, 155, '7458fa0b-3d12-4e22-a93a-3f6029577f23', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 4, 162, 'a94f5af5-758c-45eb-918e-47c60599eb96', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 5, 169, '837d0cc9-f501-401d-bd34-62a661bce1a2', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 6, 176, 'aba26297-97cc-419f-a994-ad07222417a9', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 7, 183, '292b12ff-6a5d-42f8-ae09-28fb0e189ab3', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 8, 190, 'ef141c8c-8b25-457f-a0e1-a9f9fa12c6b6', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 9, 197, '9d898c3a-fc50-423b-afef-b0d5fbb558c3', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 10, 4, '901e27f1-cf2a-4039-85c9-7b553ce2b962', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 11, 11, 'c51b8b52-0115-41ea-81f3-85ab0940d73a', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 12, 18, 'c1b1bcb5-2e71-4d48-aa81-c0b919d7d341', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 13, 25, 'fa443b73-0da4-4471-a908-c8693c04f5e2', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 14, 32, 'd9eca4a3-1bb1-4c9f-9c15-7e53cfb4c745', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 15, 39, '193e02b4-f268-46b4-ad46-c00efcd548a8', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 16, 46, 'eb718c6a-37c7-49be-842c-d3c04e4c6c92', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 17, 53, '45778c62-ac8d-4ab0-9e9a-cc03332e36fe', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 18, 60, 'e227bd33-7787-40d5-93b0-8e1551efa38b', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 19, 67, 'ece5114f-5ce3-450d-965a-89d133fe8d70', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 20, 74, '6adfca2b-3eb6-44e8-9325-6e01f357d935', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 1, 81, '5b7759c7-4f8f-4d35-aef3-8a7434708186', 't', '2026-09-23 07:50:24.722725+00', '2026-09-23 07:50:24.722725+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 2, 8, '06fe6276-a5b6-4bfa-a053-d56b5f26729c', 't', '2026-08-13 02:39:48.510842+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 3, 15, '932ba448-c9c6-4d3b-b957-f9b773aea648', 't', '2026-07-03 12:32:45.00435+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 4, 22, '36cbda96-f827-4955-b608-a8a83fc421e7', 't', '2026-09-08 15:27:55.226041+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 5, 29, '50565f54-82a8-4fe4-8cdc-4234ca7050df', 't', '2026-07-09 23:11:40.511237+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 6, 36, '883c46ad-dad7-467a-84de-e9fc36dda7bf', 't', '2026-08-27 07:04:26.130484+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 7, 43, '3969e699-067f-4e34-bb4b-73a0dcd63130', 't', '2026-07-02 21:28:14.315976+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 8, 50, '7a8cc874-3340-4c85-8f72-a4c3f14fe4e7', 't', '2026-09-05 06:13:52.162764+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 9, 57, '6fddc5cb-245a-47f0-8d6a-1d0bb93668d9', 't', '2026-09-18 05:59:15.071985+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 10, 64, '3a2aea21-d31b-4dff-a948-fc8a5fd0237f', 't', '2026-08-04 12:11:32.703195+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 11, 71, 'b7feab7d-5b1f-4b8c-9aae-ab1eb06ed605', 't', '2026-09-02 12:04:15.207568+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 12, 78, 'e3fd22d3-25cd-4eb0-9c78-274e13aecfcd', 't', '2026-08-08 19:06:20.753964+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 13, 85, '8f7cc91d-2db1-49a2-9439-1d27bacd1d4e', 't', '2026-09-10 03:58:09.110349+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 14, 92, '6baa5308-89c7-4dbb-a027-4959fbc2de59', 't', '2026-08-05 03:25:46.435098+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 15, 99, 'a8535dbc-84e2-458c-b6a5-88c894ce732d', 't', '2026-09-01 08:43:22.124564+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 16, 106, 'e2b0c00e-c357-4fb5-a893-a36dc9540754', 't', '2026-08-26 21:16:27.505685+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 17, 113, 'ab07d183-2320-4da1-b19d-7964f7478791', 't', '2026-07-26 08:55:06.255321+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 18, 120, '1ea212df-7560-4237-aeb1-e4508c96df27', 't', '2026-09-21 15:02:14.516519+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 19, 127, '8d3d18cc-35f9-4784-adac-9544b49a2520', 't', '2026-07-03 01:01:29.569355+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 20, 134, 'e3355c8b-aa51-48a8-957e-4801a01eb6c4', 't', '2026-07-29 09:55:23.680123+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 1, 141, 'b1b8dbbf-f6fb-405b-b88f-52e030ccc757', 't', '2026-08-29 12:14:50.618107+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 2, 148, '578cbc6e-2665-4908-af0a-b967dbdbcf69', 't', '2026-07-26 09:16:52.713771+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 3, 155, '1074d1cc-d579-4aa9-b3cf-2a6534bec8d6', 't', '2026-09-03 03:00:26.818057+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 4, 162, 'b43ab277-f3b5-4e5c-af73-74ef6df4b56d', 't', '2026-07-31 16:59:33.996752+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 5, 169, 'fbc66d22-6ba4-447d-a05f-4ade2fb16822', 't', '2026-07-16 01:34:08.123013+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 6, 176, '8c08f53b-cb6d-4a3a-bbdd-011ae778bcf8', 't', '2026-08-16 00:47:27.474824+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 7, 183, '03df5f5f-d2ae-4f5f-9365-b234d854d368', 't', '2026-08-21 09:55:32.804531+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 8, 190, '5f934340-0103-4ffe-8fe9-3ec6cc0df8e4', 't', '2026-08-13 11:35:29.121767+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 9, 197, '6d8c1730-ffd9-4710-b0dc-32b672bf85b7', 't', '2026-09-06 16:38:29.036013+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 10, 4, '2e08e7a6-b46f-4f52-8933-42adc6d6107b', 't', '2026-08-27 10:28:10.648138+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 11, 11, 'cf3fde2b-9747-4f9e-9a10-68c4fea6bb07', 't', '2026-07-02 23:33:31.072386+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 12, 18, 'e64e2d16-082c-4fdb-80bd-2053f48d8d15', 't', '2026-07-18 17:52:40.586934+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 13, 25, '6568ddee-0967-45b1-a50c-e48693a6e7ca', 't', '2026-09-28 12:51:39.143735+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 14, 32, 'eca89c70-3dc5-4e9c-9089-58d1f4281a34', 't', '2026-07-22 20:42:59.974622+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 15, 39, '3124c4ce-fa44-4720-a931-40acf8683454', 't', '2026-08-30 16:23:09.098513+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 16, 46, '532c1262-aa15-418c-862a-19c97152fcdf', 't', '2026-07-13 04:36:53.962563+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 17, 53, 'b4fcf4b9-bb2d-4675-8e31-47f87c64a408', 't', '2026-07-16 20:29:51.002956+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 18, 60, '2b67a963-c59d-4d25-8f96-c4acf8546a90', 't', '2026-08-07 22:57:09.556104+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('33333333-3333-3333-3333-333333333333', 19, 67, '7c83cb1f-bd84-4520-8d5d-56322009393a', 't', '2026-09-23 11:10:28.29524+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('11111111-1111-1111-1111-111111111111', 20, 74, 'ef64b4c1-c864-4c5f-b7c6-86ede19a629a', 't', '2026-09-16 11:39:13.441781+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_iot_alarm_device_event" VALUES ('22222222-2222-2222-2222-222222222222', 1, 81, '1752dda5-b6ff-44e8-8fff-9dfc1d1b6bf6', 't', '2026-07-25 01:19:32.463606+00', '2026-09-28 13:34:28.774661+00');

-- ----------------------------
-- Table structure for sd_iot_device
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_device";
CREATE TABLE "public"."sd_iot_device" (
  "tenant_id" uuid NOT NULL,
  "device_id" int4 NOT NULL DEFAULT nextval('sd_iot_device_device_id_seq'::regclass),
  "mqtt_id" int4 NOT NULL,
  "setting_id" int4 NOT NULL,
  "type_id" int4 NOT NULL,
  "location_id" int4 NOT NULL,
  "device_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "sn" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "hardware_id" int4 NOT NULL,
  "status_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "status_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "time_life" int4 NOT NULL,
  "period" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "work_status" int4 NOT NULL,
  "max" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "min" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "vendor" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "comparevalue" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "unit" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "host_id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "oid" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "action_id" int4 NOT NULL,
  "status_alert_id" int4 NOT NULL,
  "mqtt_data_value" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_data_control" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "measurement" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_control_on" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_control_off" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "org" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "bucket" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "mqtt_device_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_status_over_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_status_data_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_act_relay_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "mqtt_control_relay_name" text COLLATE "pg_catalog"."default" NOT NULL,
  "layout" int4 NOT NULL,
  "alert_set" int4 NOT NULL,
  "icon_normal" text COLLATE "pg_catalog"."default" NOT NULL,
  "icon_warning" text COLLATE "pg_catalog"."default" NOT NULL,
  "icon_alert" text COLLATE "pg_catalog"."default" NOT NULL,
  "icon" text COLLATE "pg_catalog"."default" NOT NULL,
  "icon_on" text COLLATE "pg_catalog"."default" NOT NULL,
  "icon_off" text COLLATE "pg_catalog"."default" NOT NULL,
  "color_normal" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "color_warning" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "color_alert" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "menu" int4 NOT NULL,
  "calibration_add" varchar(250) COLLATE "pg_catalog"."default" NOT NULL,
  "calibration_subtract" varchar(250) COLLATE "pg_catalog"."default" NOT NULL,
  "calibration_type" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_device
-- ----------------------------
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 1, 2, 0, 2, 2, 'Humidity Device 1', 'SN-2024-00001', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.1', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0001', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 2, 3, 0, 3, 3, 'Pressure Device 2', 'SN-2024-00002', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.2', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0002', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 3, 4, 0, 4, 4, 'CO2 Device 3', 'SN-2024-00003', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.3', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0003', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 4, 5, 0, 5, 5, 'Door Device 4', 'SN-2024-00004', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.4', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0004', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 5, 6, 0, 6, 6, 'Fire Device 5', 'SN-2024-00005', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.5', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0005', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 6, 7, 0, 7, 7, 'Gas Device 6', 'SN-2024-00006', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.6', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0006', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 7, 8, 0, 8, 8, 'Vibration Device 7', 'SN-2024-00007', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.7', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0007', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 8, 9, 0, 9, 9, 'Relay Device 8', 'SN-2024-00008', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.8', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0008', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 9, 10, 0, 10, 10, 'UPS Device 9', 'SN-2024-00009', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.9', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0009', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 10, 11, 0, 11, 11, 'Temperature Device 10', 'SN-2024-00010', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.10', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0010', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 11, 12, 0, 12, 12, 'Humidity Device 11', 'SN-2024-00011', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.11', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0011', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 12, 13, 0, 13, 13, 'Pressure Device 12', 'SN-2024-00012', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.12', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0012', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 13, 14, 0, 14, 14, 'CO2 Device 13', 'SN-2024-00013', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.13', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0013', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 14, 15, 0, 15, 15, 'Door Device 14', 'SN-2024-00014', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.14', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0014', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 15, 16, 0, 16, 16, 'Fire Device 15', 'SN-2024-00015', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.15', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0015', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 16, 17, 0, 17, 17, 'Gas Device 16', 'SN-2024-00016', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.16', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0016', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 17, 18, 0, 18, 18, 'Vibration Device 17', 'SN-2024-00017', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.17', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0017', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 18, 19, 0, 19, 19, 'Relay Device 18', 'SN-2024-00018', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.18', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0018', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 19, 20, 0, 20, 20, 'UPS Device 19', 'SN-2024-00019', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.19', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0019', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 20, 1, 0, 1, 21, 'Temperature Device 20', 'SN-2024-00020', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.20', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0020', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 21, 2, 0, 2, 22, 'Humidity Device 21', 'SN-2024-00021', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.21', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0021', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 22, 3, 0, 3, 23, 'Pressure Device 22', 'SN-2024-00022', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.22', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0022', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 23, 4, 0, 4, 24, 'CO2 Device 23', 'SN-2024-00023', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.23', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0023', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 24, 5, 0, 5, 25, 'Door Device 24', 'SN-2024-00024', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.24', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0024', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 25, 6, 0, 6, 26, 'Fire Device 25', 'SN-2024-00025', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.25', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0025', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 26, 7, 0, 7, 27, 'Gas Device 26', 'SN-2024-00026', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.26', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0026', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 27, 8, 0, 8, 28, 'Vibration Device 27', 'SN-2024-00027', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.27', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0027', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 28, 9, 0, 9, 29, 'Relay Device 28', 'SN-2024-00028', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.28', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0028', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 29, 10, 0, 10, 30, 'UPS Device 29', 'SN-2024-00029', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.29', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0029', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 30, 11, 0, 11, 1, 'Temperature Device 30', 'SN-2024-00030', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.30', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0030', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 31, 12, 0, 12, 2, 'Humidity Device 31', 'SN-2024-00031', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.31', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0031', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 32, 13, 0, 13, 3, 'Pressure Device 32', 'SN-2024-00032', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.32', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0032', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 33, 14, 0, 14, 4, 'CO2 Device 33', 'SN-2024-00033', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.33', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0033', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 34, 15, 0, 15, 5, 'Door Device 34', 'SN-2024-00034', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.34', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0034', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 35, 16, 0, 16, 6, 'Fire Device 35', 'SN-2024-00035', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.35', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0035', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 36, 17, 0, 17, 7, 'Gas Device 36', 'SN-2024-00036', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.36', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0036', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 37, 18, 0, 18, 8, 'Vibration Device 37', 'SN-2024-00037', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.37', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0037', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 38, 19, 0, 19, 9, 'Relay Device 38', 'SN-2024-00038', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.38', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0038', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 39, 20, 0, 20, 10, 'UPS Device 39', 'SN-2024-00039', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.39', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0039', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 40, 1, 0, 1, 11, 'Temperature Device 40', 'SN-2024-00040', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.40', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0040', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 41, 2, 0, 2, 12, 'Humidity Device 41', 'SN-2024-00041', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.41', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0041', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 42, 3, 0, 3, 13, 'Pressure Device 42', 'SN-2024-00042', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.42', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0042', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 43, 4, 0, 4, 14, 'CO2 Device 43', 'SN-2024-00043', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.43', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0043', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 44, 5, 0, 5, 15, 'Door Device 44', 'SN-2024-00044', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.44', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0044', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 45, 6, 0, 6, 16, 'Fire Device 45', 'SN-2024-00045', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.45', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0045', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 46, 7, 0, 7, 17, 'Gas Device 46', 'SN-2024-00046', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.46', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0046', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 47, 8, 0, 8, 18, 'Vibration Device 47', 'SN-2024-00047', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.47', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0047', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 48, 9, 0, 9, 19, 'Relay Device 48', 'SN-2024-00048', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.48', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0048', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 49, 10, 0, 10, 20, 'UPS Device 49', 'SN-2024-00049', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.49', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0049', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 50, 11, 0, 11, 21, 'Temperature Device 50', 'SN-2024-00050', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.50', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0050', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 51, 12, 0, 12, 22, 'Humidity Device 51', 'SN-2024-00051', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.51', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0051', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 52, 13, 0, 13, 23, 'Pressure Device 52', 'SN-2024-00052', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.52', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0052', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 53, 14, 0, 14, 24, 'CO2 Device 53', 'SN-2024-00053', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.53', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0053', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 54, 15, 0, 15, 25, 'Door Device 54', 'SN-2024-00054', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.54', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0054', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 55, 16, 0, 16, 26, 'Fire Device 55', 'SN-2024-00055', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.55', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0055', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 56, 17, 0, 17, 27, 'Gas Device 56', 'SN-2024-00056', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.56', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0056', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 57, 18, 0, 18, 28, 'Vibration Device 57', 'SN-2024-00057', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.57', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0057', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 58, 19, 0, 19, 29, 'Relay Device 58', 'SN-2024-00058', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.58', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0058', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 59, 20, 0, 20, 30, 'UPS Device 59', 'SN-2024-00059', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.59', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0059', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 60, 1, 0, 1, 1, 'Temperature Device 60', 'SN-2024-00060', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.60', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0060', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 61, 2, 0, 2, 2, 'Humidity Device 61', 'SN-2024-00061', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.61', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0061', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 62, 3, 0, 3, 3, 'Pressure Device 62', 'SN-2024-00062', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.62', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0062', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 63, 4, 0, 4, 4, 'CO2 Device 63', 'SN-2024-00063', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.63', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0063', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 64, 5, 0, 5, 5, 'Door Device 64', 'SN-2024-00064', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.64', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0064', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 65, 6, 0, 6, 6, 'Fire Device 65', 'SN-2024-00065', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.65', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0065', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 66, 7, 0, 7, 7, 'Gas Device 66', 'SN-2024-00066', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.66', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0066', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 67, 8, 0, 8, 8, 'Vibration Device 67', 'SN-2024-00067', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.67', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0067', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 68, 9, 0, 9, 9, 'Relay Device 68', 'SN-2024-00068', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.68', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0068', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 69, 10, 0, 10, 10, 'UPS Device 69', 'SN-2024-00069', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.69', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0069', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 70, 11, 0, 11, 11, 'Temperature Device 70', 'SN-2024-00070', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.70', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0070', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 71, 12, 0, 12, 12, 'Humidity Device 71', 'SN-2024-00071', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.71', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0071', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 72, 13, 0, 13, 13, 'Pressure Device 72', 'SN-2024-00072', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.72', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0072', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 73, 14, 0, 14, 14, 'CO2 Device 73', 'SN-2024-00073', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.73', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0073', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 74, 15, 0, 15, 15, 'Door Device 74', 'SN-2024-00074', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.74', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0074', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 75, 16, 0, 16, 16, 'Fire Device 75', 'SN-2024-00075', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.75', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0075', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 76, 17, 0, 17, 17, 'Gas Device 76', 'SN-2024-00076', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.76', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0076', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 77, 18, 0, 18, 18, 'Vibration Device 77', 'SN-2024-00077', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.77', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0077', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 78, 19, 0, 19, 19, 'Relay Device 78', 'SN-2024-00078', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.78', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0078', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 79, 20, 0, 20, 20, 'UPS Device 79', 'SN-2024-00079', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.79', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0079', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 80, 1, 0, 1, 21, 'Temperature Device 80', 'SN-2024-00080', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.80', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0080', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 81, 2, 0, 2, 22, 'Humidity Device 81', 'SN-2024-00081', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.81', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0081', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 82, 3, 0, 3, 23, 'Pressure Device 82', 'SN-2024-00082', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.82', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0082', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 83, 4, 0, 4, 24, 'CO2 Device 83', 'SN-2024-00083', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.83', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0083', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 84, 5, 0, 5, 25, 'Door Device 84', 'SN-2024-00084', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.84', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0084', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 85, 6, 0, 6, 26, 'Fire Device 85', 'SN-2024-00085', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.85', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0085', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 86, 7, 0, 7, 27, 'Gas Device 86', 'SN-2024-00086', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.86', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0086', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 87, 8, 0, 8, 28, 'Vibration Device 87', 'SN-2024-00087', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.87', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0087', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 88, 9, 0, 9, 29, 'Relay Device 88', 'SN-2024-00088', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.88', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0088', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 89, 10, 0, 10, 30, 'UPS Device 89', 'SN-2024-00089', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.89', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0089', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 90, 11, 0, 11, 1, 'Temperature Device 90', 'SN-2024-00090', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.90', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0090', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 91, 12, 0, 12, 2, 'Humidity Device 91', 'SN-2024-00091', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.91', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0091', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 92, 13, 0, 13, 3, 'Pressure Device 92', 'SN-2024-00092', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.92', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0092', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 93, 14, 0, 14, 4, 'CO2 Device 93', 'SN-2024-00093', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.93', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0093', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 94, 15, 0, 15, 5, 'Door Device 94', 'SN-2024-00094', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.94', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0094', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 95, 16, 0, 16, 6, 'Fire Device 95', 'SN-2024-00095', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.95', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0095', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 96, 17, 0, 17, 7, 'Gas Device 96', 'SN-2024-00096', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.96', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0096', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 97, 18, 0, 18, 8, 'Vibration Device 97', 'SN-2024-00097', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.97', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0097', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 98, 19, 0, 19, 9, 'Relay Device 98', 'SN-2024-00098', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.98', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0098', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 99, 20, 0, 20, 10, 'UPS Device 99', 'SN-2024-00099', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.99', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0099', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 100, 1, 0, 1, 11, 'Temperature Device 100', 'SN-2024-00100', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.100', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0100', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 101, 2, 0, 2, 12, 'Humidity Device 101', 'SN-2024-00101', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.101', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0101', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 102, 3, 0, 3, 13, 'Pressure Device 102', 'SN-2024-00102', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.102', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0102', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 103, 4, 0, 4, 14, 'CO2 Device 103', 'SN-2024-00103', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.103', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0103', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 104, 5, 0, 5, 15, 'Door Device 104', 'SN-2024-00104', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.104', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0104', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 105, 6, 0, 6, 16, 'Fire Device 105', 'SN-2024-00105', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.105', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0105', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 106, 7, 0, 7, 17, 'Gas Device 106', 'SN-2024-00106', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.106', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0106', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 107, 8, 0, 8, 18, 'Vibration Device 107', 'SN-2024-00107', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.107', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0107', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 108, 9, 0, 9, 19, 'Relay Device 108', 'SN-2024-00108', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.108', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0108', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 109, 10, 0, 10, 20, 'UPS Device 109', 'SN-2024-00109', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.109', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0109', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 110, 11, 0, 11, 21, 'Temperature Device 110', 'SN-2024-00110', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.110', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0110', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 111, 12, 0, 12, 22, 'Humidity Device 111', 'SN-2024-00111', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.111', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0111', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 112, 13, 0, 13, 23, 'Pressure Device 112', 'SN-2024-00112', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.112', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0112', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 113, 14, 0, 14, 24, 'CO2 Device 113', 'SN-2024-00113', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.113', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0113', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 114, 15, 0, 15, 25, 'Door Device 114', 'SN-2024-00114', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.114', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0114', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 115, 16, 0, 16, 26, 'Fire Device 115', 'SN-2024-00115', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.115', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0115', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 116, 17, 0, 17, 27, 'Gas Device 116', 'SN-2024-00116', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.116', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0116', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 117, 18, 0, 18, 28, 'Vibration Device 117', 'SN-2024-00117', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.117', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0117', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 118, 19, 0, 19, 29, 'Relay Device 118', 'SN-2024-00118', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.118', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0118', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 119, 20, 0, 20, 30, 'UPS Device 119', 'SN-2024-00119', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.119', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0119', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 120, 1, 0, 1, 1, 'Temperature Device 120', 'SN-2024-00120', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.120', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0120', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 121, 2, 0, 2, 2, 'Humidity Device 121', 'SN-2024-00121', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.121', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0121', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 122, 3, 0, 3, 3, 'Pressure Device 122', 'SN-2024-00122', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.122', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0122', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 123, 4, 0, 4, 4, 'CO2 Device 123', 'SN-2024-00123', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.123', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0123', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 124, 5, 0, 5, 5, 'Door Device 124', 'SN-2024-00124', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.124', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0124', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 125, 6, 0, 6, 6, 'Fire Device 125', 'SN-2024-00125', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.125', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0125', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 126, 7, 0, 7, 7, 'Gas Device 126', 'SN-2024-00126', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.126', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0126', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 127, 8, 0, 8, 8, 'Vibration Device 127', 'SN-2024-00127', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.127', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0127', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 128, 9, 0, 9, 9, 'Relay Device 128', 'SN-2024-00128', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.128', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0128', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 129, 10, 0, 10, 10, 'UPS Device 129', 'SN-2024-00129', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.129', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0129', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 130, 11, 0, 11, 11, 'Temperature Device 130', 'SN-2024-00130', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.130', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0130', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 131, 12, 0, 12, 12, 'Humidity Device 131', 'SN-2024-00131', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.131', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0131', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 132, 13, 0, 13, 13, 'Pressure Device 132', 'SN-2024-00132', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.132', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0132', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 133, 14, 0, 14, 14, 'CO2 Device 133', 'SN-2024-00133', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.133', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0133', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 134, 15, 0, 15, 15, 'Door Device 134', 'SN-2024-00134', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.134', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0134', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 135, 16, 0, 16, 16, 'Fire Device 135', 'SN-2024-00135', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.135', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0135', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 136, 17, 0, 17, 17, 'Gas Device 136', 'SN-2024-00136', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.136', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0136', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 137, 18, 0, 18, 18, 'Vibration Device 137', 'SN-2024-00137', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.137', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0137', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 138, 19, 0, 19, 19, 'Relay Device 138', 'SN-2024-00138', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.138', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0138', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 139, 20, 0, 20, 20, 'UPS Device 139', 'SN-2024-00139', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.139', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0139', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 140, 1, 0, 1, 21, 'Temperature Device 140', 'SN-2024-00140', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.140', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0140', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 141, 2, 0, 2, 22, 'Humidity Device 141', 'SN-2024-00141', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.141', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0141', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 142, 3, 0, 3, 23, 'Pressure Device 142', 'SN-2024-00142', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.142', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0142', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 143, 4, 0, 4, 24, 'CO2 Device 143', 'SN-2024-00143', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.143', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0143', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 144, 5, 0, 5, 25, 'Door Device 144', 'SN-2024-00144', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.144', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0144', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 145, 6, 0, 6, 26, 'Fire Device 145', 'SN-2024-00145', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.145', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0145', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 146, 7, 0, 7, 27, 'Gas Device 146', 'SN-2024-00146', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.146', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0146', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 147, 8, 0, 8, 28, 'Vibration Device 147', 'SN-2024-00147', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.147', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0147', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 148, 9, 0, 9, 29, 'Relay Device 148', 'SN-2024-00148', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.148', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0148', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 149, 10, 0, 10, 30, 'UPS Device 149', 'SN-2024-00149', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.149', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0149', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 150, 11, 0, 11, 1, 'Temperature Device 150', 'SN-2024-00150', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.150', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0150', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 151, 12, 0, 12, 2, 'Humidity Device 151', 'SN-2024-00151', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.151', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0151', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 152, 13, 0, 13, 3, 'Pressure Device 152', 'SN-2024-00152', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.152', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0152', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 153, 14, 0, 14, 4, 'CO2 Device 153', 'SN-2024-00153', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.153', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0153', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 154, 15, 0, 15, 5, 'Door Device 154', 'SN-2024-00154', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.154', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0154', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 155, 16, 0, 16, 6, 'Fire Device 155', 'SN-2024-00155', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.155', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0155', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 156, 17, 0, 17, 7, 'Gas Device 156', 'SN-2024-00156', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.156', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0156', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 157, 18, 0, 18, 8, 'Vibration Device 157', 'SN-2024-00157', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.157', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0157', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 158, 19, 0, 19, 9, 'Relay Device 158', 'SN-2024-00158', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.158', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0158', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 159, 20, 0, 20, 10, 'UPS Device 159', 'SN-2024-00159', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.159', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0159', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 160, 1, 0, 1, 11, 'Temperature Device 160', 'SN-2024-00160', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.160', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0160', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 161, 2, 0, 2, 12, 'Humidity Device 161', 'SN-2024-00161', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.161', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0161', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 162, 3, 0, 3, 13, 'Pressure Device 162', 'SN-2024-00162', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.162', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0162', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 163, 4, 0, 4, 14, 'CO2 Device 163', 'SN-2024-00163', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.163', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0163', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 164, 5, 0, 5, 15, 'Door Device 164', 'SN-2024-00164', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.164', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0164', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 165, 6, 0, 6, 16, 'Fire Device 165', 'SN-2024-00165', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.165', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0165', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 166, 7, 0, 7, 17, 'Gas Device 166', 'SN-2024-00166', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.166', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0166', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 167, 8, 0, 8, 18, 'Vibration Device 167', 'SN-2024-00167', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.167', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0167', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 168, 9, 0, 9, 19, 'Relay Device 168', 'SN-2024-00168', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.168', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0168', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 169, 10, 0, 10, 20, 'UPS Device 169', 'SN-2024-00169', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.169', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0169', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 170, 11, 0, 11, 21, 'Temperature Device 170', 'SN-2024-00170', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.170', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0170', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 171, 12, 0, 12, 22, 'Humidity Device 171', 'SN-2024-00171', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.171', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0171', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 172, 13, 0, 13, 23, 'Pressure Device 172', 'SN-2024-00172', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.172', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0172', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 173, 14, 0, 14, 24, 'CO2 Device 173', 'SN-2024-00173', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.173', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0173', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 174, 15, 0, 15, 25, 'Door Device 174', 'SN-2024-00174', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.174', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0174', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 175, 16, 0, 16, 26, 'Fire Device 175', 'SN-2024-00175', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.175', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0175', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 176, 17, 0, 17, 27, 'Gas Device 176', 'SN-2024-00176', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.176', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0176', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 177, 18, 0, 18, 28, 'Vibration Device 177', 'SN-2024-00177', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.177', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0177', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 178, 19, 0, 19, 29, 'Relay Device 178', 'SN-2024-00178', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.178', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0178', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 179, 20, 0, 20, 30, 'UPS Device 179', 'SN-2024-00179', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.179', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0179', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 180, 1, 0, 1, 1, 'Temperature Device 180', 'SN-2024-00180', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.180', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0180', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 181, 2, 0, 2, 2, 'Humidity Device 181', 'SN-2024-00181', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '%', 'host-2', '1.3.6.1.4.1.181', 2, 2, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'humidity', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0181', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 182, 3, 0, 3, 3, 'Pressure Device 182', 'SN-2024-00182', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'kPa', 'host-3', '1.3.6.1.4.1.182', 3, 3, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'pressure', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0182', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 183, 4, 0, 4, 4, 'CO2 Device 183', 'SN-2024-00183', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'ppm', 'host-4', '1.3.6.1.4.1.183', 4, 4, 'CBKK01/DATA', 'CBKK01/CONTROL', 'co2', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0183', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 184, 5, 0, 5, 5, 'Door Device 184', 'SN-2024-00184', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '', 'host-5', '1.3.6.1.4.1.184', 5, 5, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'door', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0184', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 185, 6, 0, 6, 6, 'Fire Device 185', 'SN-2024-00185', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '°C', 'host-6', '1.3.6.1.4.1.185', 6, 6, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'fire', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0185', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 186, 7, 0, 7, 7, 'Gas Device 186', 'SN-2024-00186', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '%', 'host-7', '1.3.6.1.4.1.186', 7, 7, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'gas', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0186', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 187, 8, 0, 8, 8, 'Vibration Device 187', 'SN-2024-00187', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', 'kPa', 'host-8', '1.3.6.1.4.1.187', 8, 8, 'CBKK01/DATA', 'CBKK01/CONTROL', 'vibration', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0187', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 188, 9, 0, 9, 9, 'Relay Device 188', 'SN-2024-00188', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'ppm', 'host-9', '1.3.6.1.4.1.188', 9, 9, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'relay', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0188', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 189, 10, 0, 10, 10, 'UPS Device 189', 'SN-2024-00189', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', '', 'host-10', '1.3.6.1.4.1.189', 10, 10, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'ups', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0189', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 190, 11, 0, 11, 11, 'Temperature Device 190', 'SN-2024-00190', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '°C', 'host-1', '1.3.6.1.4.1.190', 11, 11, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'temperature', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0190', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 191, 12, 0, 12, 12, 'Humidity Device 191', 'SN-2024-00191', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '%', 'host-2', '1.3.6.1.4.1.191', 12, 12, 'CBKK01/DATA', 'CBKK01/CONTROL', 'humidity', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0191', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 192, 13, 0, 13, 13, 'Pressure Device 192', 'SN-2024-00192', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', 'kPa', 'host-3', '1.3.6.1.4.1.192', 13, 13, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'pressure', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0192', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 193, 14, 0, 14, 14, 'CO2 Device 193', 'SN-2024-00193', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'ppm', 'host-4', '1.3.6.1.4.1.193', 14, 14, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'co2', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0193', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 194, 15, 0, 15, 15, 'Door Device 194', 'SN-2024-00194', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', '', 'host-5', '1.3.6.1.4.1.194', 15, 15, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'door', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0194', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 195, 16, 0, 16, 16, 'Fire Device 195', 'SN-2024-00195', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '°C', 'host-6', '1.3.6.1.4.1.195', 16, 16, 'CBKK01/DATA', 'CBKK01/CONTROL', 'fire', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0195', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 196, 17, 0, 17, 17, 'Gas Device 196', 'SN-2024-00196', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '%', 'host-7', '1.3.6.1.4.1.196', 17, 17, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'gas', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0196', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 197, 18, 0, 18, 18, 'Vibration Device 197', 'SN-2024-00197', 2, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'BME280', 'Bosch', '0', 'kPa', 'host-8', '1.3.6.1.4.1.197', 18, 18, 'AIRCOM2/DATA', 'AIRCOM2/CONTROL', 'vibration', '1', '0', 'ORG-A', 'AIRCOM2', 1, 'dev-0197', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 2, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 198, 19, 0, 19, 19, 'Relay Device 198', 'SN-2024-00198', 3, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'SHT31', 'TI', '0', 'ppm', 'host-9', '1.3.6.1.4.1.198', 19, 19, 'BAACTW01/DATA', 'BAACTW01/CONTROL', 'relay', '1', '0', 'ORG-A', 'BAACTW01', 1, 'dev-0198', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 3, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 199, 20, 0, 20, 20, 'UPS Device 199', 'SN-2024-00199', 4, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DS18B20', 'Dallas', '0', '', 'host-10', '1.3.6.1.4.1.199', 20, 20, 'CBKK01/DATA', 'CBKK01/CONTROL', 'ups', '1', '0', 'ORG-A', 'CBKK01', 1, 'dev-0199', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 4, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');
INSERT INTO "public"."sd_iot_device" VALUES ('11111111-1111-1111-1111-111111111111', 200, 1, 0, 1, 21, 'Temperature Device 200', 'SN-2024-00200', 1, '40', '38', '50', '45', 300, '5m', 1, '60', '-10', 'DHT22', 'Sensirion', '0', '°C', 'host-1', '1.3.6.1.4.1.200', 1, 1, 'AIRCOM1/DATA', 'AIRCOM1/CONTROL', 'temperature', '1', '0', 'ORG-A', 'AIRCOM1', 1, 'dev-0200', '{"0":"value"}', '{"0":"temperature"}', '{"0":"relay1"}', '{"0":"relay1"}', 1, 1, 'icon-normal.png', 'icon-warning.png', 'icon-alert.png', 'icon-normal.png', 'icon-on.png', 'icon-off.png', '#22C55E', '#F59E0B', '#EF4444', 'normal', 1, '0', '0', 3, '2026-09-23 07:50:24.705713+00', '2026-09-23 07:50:24.705713+00');

-- ----------------------------
-- Table structure for sd_iot_device_alarm_action
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_device_alarm_action";
CREATE TABLE "public"."sd_iot_device_alarm_action" (
  "tenant_id" uuid NOT NULL,
  "alarm_action_id" int4 NOT NULL DEFAULT nextval('sd_iot_device_alarm_action_alarm_action_id_seq'::regclass),
  "action_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_warning" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "status_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "recovery_alert" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email_alarm" int4 NOT NULL,
  "line_alarm" int4 NOT NULL,
  "telegram_alarm" int4 NOT NULL,
  "sms_alarm" int4 NOT NULL,
  "nonc_alarm" int4 NOT NULL,
  "time_life" int4 NOT NULL,
  "event" int4 NOT NULL,
  "status" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_device_alarm_action
-- ----------------------------
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 1, 'Alarm Action 1', '40', '38', '50', '45', 1, 0, 0, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 2, 'Alarm Action 2', '40', '38', '50', '45', 1, 0, 1, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 3, 'Alarm Action 3', '40', '38', '50', '45', 0, 1, 0, 1, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 4, 'Alarm Action 4', '40', '38', '50', '45', 1, 1, 0, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 5, 'Alarm Action 5', '40', '38', '50', '45', 0, 0, 1, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 6, 'Alarm Action 6', '40', '38', '50', '45', 1, 1, 0, 1, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 7, 'Alarm Action 7', '40', '38', '50', '45', 1, 1, 0, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 8, 'Alarm Action 8', '40', '38', '50', '45', 0, 0, 1, 1, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 9, 'Alarm Action 9', '40', '38', '50', '45', 1, 1, 1, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 10, 'Alarm Action 10', '40', '38', '50', '45', 1, 0, 1, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 11, 'Alarm Action 11', '40', '38', '50', '45', 0, 0, 1, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 12, 'Alarm Action 12', '40', '38', '50', '45', 1, 1, 1, 0, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 13, 'Alarm Action 13', '40', '38', '50', '45', 0, 0, 1, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 14, 'Alarm Action 14', '40', '38', '50', '45', 1, 1, 0, 1, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 15, 'Alarm Action 15', '40', '38', '50', '45', 1, 0, 0, 0, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 16, 'Alarm Action 16', '40', '38', '50', '45', 0, 1, 1, 0, 0, 300, 1, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 17, 'Alarm Action 17', '40', '38', '50', '45', 1, 0, 0, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 18, 'Alarm Action 18', '40', '38', '50', '45', 0, 0, 1, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 19, 'Alarm Action 19', '40', '38', '50', '45', 1, 1, 1, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');
INSERT INTO "public"."sd_iot_device_alarm_action" VALUES ('11111111-1111-1111-1111-111111111111', 20, 'Alarm Action 20', '40', '38', '50', '45', 1, 0, 0, 1, 0, 300, 0, 1, '2026-09-23 07:50:24.701624+00', '2026-09-23 07:50:24.701624+00');

-- ----------------------------
-- Table structure for sd_iot_device_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_device_type";
CREATE TABLE "public"."sd_iot_device_type" (
  "tenant_id" uuid NOT NULL,
  "type_id" int4 NOT NULL DEFAULT nextval('sd_iot_device_type_type_id_seq'::regclass),
  "type_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_device_type
-- ----------------------------
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 1, 'Humidity Type 1', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 2, 'Pressure Type 2', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 3, 'CO2 Type 3', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 4, 'Door Type 4', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 5, 'Fire Type 5', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 6, 'Gas Type 6', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 7, 'Vibration Type 7', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 8, 'Relay Type 8', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 9, 'UPS Type 9', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 10, 'Temperature Type 10', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 11, 'Humidity Type 11', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 12, 'Pressure Type 12', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 13, 'CO2 Type 13', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 14, 'Door Type 14', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 15, 'Fire Type 15', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 16, 'Gas Type 16', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 17, 'Vibration Type 17', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 18, 'Relay Type 18', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 19, 'UPS Type 19', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');
INSERT INTO "public"."sd_iot_device_type" VALUES ('11111111-1111-1111-1111-111111111111', 20, 'Temperature Type 20', 1, '2026-09-23 07:50:24.695133+00', '2026-09-23 07:50:24.695133+00');

-- ----------------------------
-- Table structure for sd_iot_location
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_location";
CREATE TABLE "public"."sd_iot_location" (
  "tenant_id" uuid NOT NULL,
  "location_id" int4 NOT NULL DEFAULT nextval('sd_iot_location_location_id_seq'::regclass),
  "location_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "ipaddress" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "location_detail" text COLLATE "pg_catalog"."default" NOT NULL,
  "configdata" text COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_location
-- ----------------------------
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 1, 'Factory B-22', '192.168.1.1', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 2, 'Factory C-33', '192.168.1.2', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 3, 'Factory D-44', '192.168.1.3', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 4, 'Factory E-55', '192.168.1.4', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 5, 'Factory A-16', '192.168.1.5', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 6, 'Factory B-27', '192.168.1.6', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 7, 'Factory C-38', '192.168.1.7', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 8, 'Factory D-41', '192.168.1.8', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 9, 'Factory E-52', '192.168.1.9', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 10, 'Factory A-13', '192.168.1.10', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 11, 'Factory B-24', '192.168.1.11', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 12, 'Factory C-35', '192.168.1.12', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 13, 'Factory D-46', '192.168.1.13', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 14, 'Factory E-57', '192.168.1.14', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 15, 'Factory A-18', '192.168.1.15', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 16, 'Factory B-21', '192.168.1.16', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 17, 'Factory C-32', '192.168.1.17', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 18, 'Factory D-43', '192.168.1.18', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 19, 'Factory E-54', '192.168.1.19', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 20, 'Factory A-15', '192.168.1.20', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 21, 'Factory B-26', '192.168.1.21', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 22, 'Factory C-37', '192.168.1.22', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 23, 'Factory D-48', '192.168.1.23', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 24, 'Factory E-51', '192.168.1.24', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 25, 'Factory A-12', '192.168.1.25', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 26, 'Factory B-23', '192.168.1.26', 'Building B', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 27, 'Factory C-34', '192.168.1.27', 'Building C', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 28, 'Factory D-45', '192.168.1.28', 'Building D', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 29, 'Factory E-56', '192.168.1.29', 'Building E', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');
INSERT INTO "public"."sd_iot_location" VALUES ('11111111-1111-1111-1111-111111111111', 30, 'Factory A-17', '192.168.1.30', 'Building A', '{"lat":13.75,"lng":100.5}', 1, '2026-09-23 07:50:24.690835+00', '2026-09-23 07:50:24.690835+00');

-- ----------------------------
-- Table structure for sd_iot_mqtt
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_mqtt";
CREATE TABLE "public"."sd_iot_mqtt" (
  "tenant_id" uuid NOT NULL,
  "mqtt_id" int4 NOT NULL DEFAULT nextval('sd_iot_mqtt_mqtt_id_seq'::regclass),
  "mqtt_type_id" int4 NOT NULL,
  "sort" int4 NOT NULL,
  "mqtt_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "host" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "port" int4 NOT NULL,
  "username" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "secret" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "expire_in" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "token_value" text COLLATE "pg_catalog"."default" NOT NULL,
  "org" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "bucket" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "envavorment" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "location_id" int4 NOT NULL,
  "latitude" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "longitude" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "zoom" int4 NOT NULL,
  "mqtt_main_id" int4 NOT NULL,
  "configuration" text COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_mqtt
-- ----------------------------
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 1, 1, 1, 'MQTT-AIRCOM2', '10.0.0.2', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM2', 'production', 2, '13.7563', '100.5018', 12, 2, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 2, 1, 2, 'MQTT-BAACTW01', '10.0.0.3', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'BAACTW01', 'production', 3, '13.7563', '100.5018', 12, 3, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 3, 1, 3, 'MQTT-CBKK01', '10.0.0.4', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'CBKK01', 'production', 4, '13.7563', '100.5018', 12, 4, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 4, 1, 4, 'MQTT-AIRCOM1', '10.0.0.5', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM1', 'production', 5, '13.7563', '100.5018', 12, 5, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 5, 1, 5, 'MQTT-AIRCOM2', '10.0.0.6', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM2', 'production', 6, '13.7563', '100.5018', 12, 6, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 6, 1, 6, 'MQTT-BAACTW01', '10.0.0.7', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'BAACTW01', 'production', 7, '13.7563', '100.5018', 12, 7, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 7, 1, 7, 'MQTT-CBKK01', '10.0.0.8', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'CBKK01', 'production', 8, '13.7563', '100.5018', 12, 8, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 8, 1, 8, 'MQTT-AIRCOM1', '10.0.0.9', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM1', 'production', 9, '13.7563', '100.5018', 12, 9, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 9, 1, 9, 'MQTT-AIRCOM2', '10.0.0.10', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM2', 'production', 10, '13.7563', '100.5018', 12, 10, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 10, 1, 10, 'MQTT-BAACTW01', '10.0.0.1', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'BAACTW01', 'production', 11, '13.7563', '100.5018', 12, 1, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 11, 1, 11, 'MQTT-CBKK01', '10.0.0.2', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'CBKK01', 'production', 12, '13.7563', '100.5018', 12, 2, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 12, 1, 12, 'MQTT-AIRCOM1', '10.0.0.3', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM1', 'production', 13, '13.7563', '100.5018', 12, 3, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 13, 1, 13, 'MQTT-AIRCOM2', '10.0.0.4', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM2', 'production', 14, '13.7563', '100.5018', 12, 4, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 14, 1, 14, 'MQTT-BAACTW01', '10.0.0.5', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'BAACTW01', 'production', 15, '13.7563', '100.5018', 12, 5, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 15, 1, 15, 'MQTT-CBKK01', '10.0.0.6', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'CBKK01', 'production', 16, '13.7563', '100.5018', 12, 6, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 16, 1, 16, 'MQTT-AIRCOM1', '10.0.0.7', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM1', 'production', 17, '13.7563', '100.5018', 12, 7, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 17, 1, 17, 'MQTT-AIRCOM2', '10.0.0.8', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM2', 'production', 18, '13.7563', '100.5018', 12, 8, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 18, 1, 18, 'MQTT-BAACTW01', '10.0.0.9', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'BAACTW01', 'production', 19, '13.7563', '100.5018', 12, 9, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 19, 1, 19, 'MQTT-CBKK01', '10.0.0.10', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'CBKK01', 'production', 20, '13.7563', '100.5018', 12, 10, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');
INSERT INTO "public"."sd_iot_mqtt" VALUES ('11111111-1111-1111-1111-111111111111', 20, 1, 20, 'MQTT-AIRCOM1', '10.0.0.1', 1883, 'user', 'pass', '', '3600', '', 'ORG-A', 'AIRCOM1', 'production', 21, '13.7563', '100.5018', 12, 1, '{"qos":1}', 1, '2026-09-23 07:50:24.687221+00', '2026-09-23 07:50:24.687221+00');

-- ----------------------------
-- Table structure for sd_iot_schedule
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_schedule";
CREATE TABLE "public"."sd_iot_schedule" (
  "tenant_id" uuid NOT NULL,
  "schedule_id" int4 NOT NULL DEFAULT nextval('sd_iot_schedule_schedule_id_seq'::regclass),
  "schedule_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "device_id" int4 NOT NULL,
  "start" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "event" int4 NOT NULL,
  "sunday" int4 NOT NULL,
  "monday" int4 NOT NULL,
  "tuesday" int4 NOT NULL,
  "wednesday" int4 NOT NULL,
  "thursday" int4 NOT NULL,
  "friday" int4 NOT NULL,
  "saturday" int4 NOT NULL,
  "status" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_schedule
-- ----------------------------

-- ----------------------------
-- Table structure for sd_iot_schedule_device
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_iot_schedule_device";
CREATE TABLE "public"."sd_iot_schedule_device" (
  "tenant_id" uuid NOT NULL,
  "schedule_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_iot_schedule_device
-- ----------------------------

-- ----------------------------
-- Table structure for sd_mqtt_host
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_mqtt_host";
CREATE TABLE "public"."sd_mqtt_host" (
  "tenant_id" uuid NOT NULL,
  "hostname" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "host" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "port" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "username" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "idhost" int4 NOT NULL,
  "status" int4 NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_mqtt_host
-- ----------------------------
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-1.iot.local', '10.0.0.1', '1883', 'admin', 'secret', 1, 1, '8a374e32-f549-4ee5-94ec-c5fef956b4aa', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-2.iot.local', '10.0.0.2', '1883', 'admin', 'secret', 2, 1, 'e9bdac17-700d-4634-a6fb-15809d37216c', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-3.iot.local', '10.0.0.3', '1883', 'admin', 'secret', 3, 1, 'd7e964f7-bb63-4024-80c1-5c350054de86', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-4.iot.local', '10.0.0.4', '1883', 'admin', 'secret', 4, 1, '75ac4d38-2654-4c9a-9424-0f9d07acad49', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-5.iot.local', '10.0.0.5', '1883', 'admin', 'secret', 5, 1, 'c6b7235e-6e4e-4bfb-ba05-eb06297c3545', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-6.iot.local', '10.0.0.6', '1883', 'admin', 'secret', 6, 1, '8237612e-7fc2-477f-8dff-0d2e05064096', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-7.iot.local', '10.0.0.7', '1883', 'admin', 'secret', 7, 1, 'e688edfc-a3d5-4d0e-ba4a-9faaced25348', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-8.iot.local', '10.0.0.8', '1883', 'admin', 'secret', 8, 1, '7ba5ef0e-530c-4998-8ea8-5a2f8d72386d', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-9.iot.local', '10.0.0.9', '1883', 'admin', 'secret', 9, 1, '71626353-146d-4e38-bb5d-2369c9b71c0c', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-10.iot.local', '10.0.0.10', '1883', 'admin', 'secret', 10, 1, '2cf01170-2198-4eea-8e41-25b87019ce25', 't', '2026-09-23 07:50:24.682147+00', '2026-09-23 07:50:24.682147+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('22222222-2222-2222-2222-222222222222', 'broker-1.iot.local', '10.0.0.1', '1883', 'admin', 'secret_pass', 1, 1, '652da985-b16b-4bd5-886f-c59ccc7cf3a1', 't', '2026-07-31 04:20:31.243813+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('33333333-3333-3333-3333-333333333333', 'broker-2.iot.local', '10.0.0.2', '1883', 'admin', 'secret_pass', 2, 1, '3c80b179-02cf-4c3f-a1d3-b62822ac1466', 't', '2026-07-28 02:51:05.537907+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-3.iot.local', '10.0.0.3', '1883', 'admin', 'secret_pass', 3, 1, '4c5ce8bc-f5b9-4852-adac-f12ae9237595', 't', '2026-08-01 22:37:14.52766+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('22222222-2222-2222-2222-222222222222', 'broker-4.iot.local', '10.0.0.4', '1883', 'admin', 'secret_pass', 4, 1, '6dd00d39-1995-4f87-957b-044848d86c53', 't', '2026-09-14 17:19:56.937753+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('33333333-3333-3333-3333-333333333333', 'broker-5.iot.local', '10.0.0.5', '1883', 'admin', 'secret_pass', 5, 1, 'b310d171-5c1f-413b-91fa-6ab7661741b2', 't', '2026-08-25 08:35:50.486409+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-6.iot.local', '10.0.0.6', '1883', 'admin', 'secret_pass', 6, 1, '70dd7cc5-00e3-443f-ac17-65f8a3ee110a', 't', '2026-09-27 20:22:14.827432+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('22222222-2222-2222-2222-222222222222', 'broker-7.iot.local', '10.0.0.7', '1883', 'admin', 'secret_pass', 7, 1, 'a224fa6c-b3de-483e-9f1e-97bef595b527', 't', '2026-07-01 21:51:26.61206+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('33333333-3333-3333-3333-333333333333', 'broker-8.iot.local', '10.0.0.8', '1883', 'admin', 'secret_pass', 8, 1, '9241dcc3-0685-4c70-8404-4be982d8bc6f', 't', '2026-08-21 00:59:43.352698+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('11111111-1111-1111-1111-111111111111', 'broker-9.iot.local', '10.0.0.9', '1883', 'admin', 'secret_pass', 9, 1, '2c5420c1-0f2d-40f4-950e-e342db950222', 't', '2026-08-20 01:15:25.82717+00', '2026-09-28 13:34:28.774661+00');
INSERT INTO "public"."sd_mqtt_host" VALUES ('22222222-2222-2222-2222-222222222222', 'broker-10.iot.local', '10.0.0.10', '1883', 'admin', 'secret_pass', 10, 1, '6bc36155-eaf9-498b-9eb9-a25bd555ce0e', 't', '2026-07-29 01:10:43.013026+00', '2026-09-28 13:34:28.774661+00');

-- ----------------------------
-- Table structure for sd_notification_channel
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_notification_channel";
CREATE TABLE "public"."sd_notification_channel" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_notification_channel_id_seq'::regclass),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "icon" varchar(100) COLLATE "pg_catalog"."default",
  "handler_class" varchar(200) COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_notification_channel
-- ----------------------------

-- ----------------------------
-- Table structure for sd_notification_condition
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_notification_condition";
CREATE TABLE "public"."sd_notification_condition" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_notification_condition_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "notification_type_id" int4 NOT NULL,
  "min_value" numeric(10,2),
  "max_value" numeric(10,2),
  "condition_operator" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "priority" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_notification_condition
-- ----------------------------

-- ----------------------------
-- Table structure for sd_notification_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_notification_log";
CREATE TABLE "public"."sd_notification_log" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_notification_log_id_seq'::regclass),
  "device_id" int4,
  "notification_type_id" int4,
  "notification_channel_id" int4,
  "template_id" int4,
  "message" text COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "response_data" jsonb,
  "sent_at" timestamptz(6),
  "delivered_at" timestamptz(6),
  "read_at" timestamptz(6),
  "retry_count" int4 NOT NULL,
  "error_message" text COLLATE "pg_catalog"."default",
  "message_id" varchar(100) COLLATE "pg_catalog"."default",
  "recipient" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_notification_log
-- ----------------------------

-- ----------------------------
-- Table structure for sd_notification_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_notification_type";
CREATE TABLE "public"."sd_notification_type" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_notification_type_id_seq'::regclass),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "cooldown_minutes" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "icon" varchar(100) COLLATE "pg_catalog"."default",
  "color" varchar(20) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_notification_type
-- ----------------------------

-- ----------------------------
-- Table structure for sd_report_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_report_data";
CREATE TABLE "public"."sd_report_data" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_report_data_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "template_id" int4,
  "report_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "data" jsonb NOT NULL,
  "period_start" timestamptz(6) NOT NULL,
  "period_end" timestamptz(6) NOT NULL,
  "generated_at" timestamptz(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "file_path" varchar(500) COLLATE "pg_catalog"."default",
  "file_format" varchar(20) COLLATE "pg_catalog"."default",
  "is_exported" bool NOT NULL,
  "exported_at" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_report_data
-- ----------------------------

-- ----------------------------
-- Table structure for sd_schedule_process_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_schedule_process_log";
CREATE TABLE "public"."sd_schedule_process_log" (
  "tenant_id" uuid NOT NULL,
  "schedule_id" int4 NOT NULL,
  "device_id" int4 NOT NULL,
  "schedule_event_start" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "day" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "doday" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "dotime" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "schedule_event" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "device_status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "date" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "time" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_schedule_process_log
-- ----------------------------

-- ----------------------------
-- Table structure for sd_sensor_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_sensor_data";
CREATE TABLE "public"."sd_sensor_data" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_sensor_data_id_seq'::regclass),
  "device_id" int4 NOT NULL,
  "value" numeric(10,2) NOT NULL,
  "raw_data" jsonb,
  "notification_type_id" int4,
  "battery_level" numeric(5,2),
  "signal_strength" int4,
  "timestamp" timestamptz(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_sensor_data
-- ----------------------------

-- ----------------------------
-- Table structure for sd_system_setting
-- ----------------------------
DROP TABLE IF EXISTS "public"."sd_system_setting";
CREATE TABLE "public"."sd_system_setting" (
  "tenant_id" uuid NOT NULL,
  "id" int4 NOT NULL DEFAULT nextval('sd_system_setting_id_seq'::regclass),
  "key" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "value" jsonb NOT NULL,
  "category" varchar(50) COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default",
  "is_public" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of sd_system_setting
-- ----------------------------

-- ----------------------------
-- Table structure for so_outputs
-- ----------------------------
DROP TABLE IF EXISTS "public"."so_outputs";
CREATE TABLE "public"."so_outputs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "request_id" uuid NOT NULL,
  "raw_text" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "parsed_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "is_valid" bool NOT NULL DEFAULT false,
  "attempts" int4 NOT NULL DEFAULT 0,
  "tokens_used" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of so_outputs
-- ----------------------------

-- ----------------------------
-- Table structure for so_repairs
-- ----------------------------
DROP TABLE IF EXISTS "public"."so_repairs";
CREATE TABLE "public"."so_repairs" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "output_id" uuid NOT NULL,
  "attempt" int4 NOT NULL DEFAULT 1,
  "feedback" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "raw_text" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of so_repairs
-- ----------------------------

-- ----------------------------
-- Table structure for so_requests
-- ----------------------------
DROP TABLE IF EXISTS "public"."so_requests";
CREATE TABLE "public"."so_requests" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "schema_id" uuid NOT NULL,
  "model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "prompt" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "temperature" float8 NOT NULL DEFAULT 0,
  "max_repairs" int4 NOT NULL DEFAULT 2,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of so_requests
-- ----------------------------

-- ----------------------------
-- Table structure for so_schemas
-- ----------------------------
DROP TABLE IF EXISTS "public"."so_schemas";
CREATE TABLE "public"."so_schemas" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "json_schema" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "pydantic_model" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "strict" bool NOT NULL DEFAULT false,
  "strategy" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'json_mode'::character varying,
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '1.0.0'::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of so_schemas
-- ----------------------------

-- ----------------------------
-- Table structure for so_validations
-- ----------------------------
DROP TABLE IF EXISTS "public"."so_validations";
CREATE TABLE "public"."so_validations" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "output_id" uuid NOT NULL,
  "attempt" int4 NOT NULL DEFAULT 1,
  "errors_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "passed" bool NOT NULL DEFAULT false,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of so_validations
-- ----------------------------

-- ----------------------------
-- Table structure for tool_definitions
-- ----------------------------
DROP TABLE IF EXISTS "public"."tool_definitions";
CREATE TABLE "public"."tool_definitions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "parameters_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "returns_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '1.0.0'::character varying,
  "kind" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'http'::character varying,
  "risk_level" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'low'::character varying,
  "visibility" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'tenant'::character varying,
  "timeout_seconds" int4 NOT NULL DEFAULT 30,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of tool_definitions
-- ----------------------------

-- ----------------------------
-- Table structure for tool_invocations
-- ----------------------------
DROP TABLE IF EXISTS "public"."tool_invocations";
CREATE TABLE "public"."tool_invocations" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "tool_id" uuid NOT NULL,
  "tool_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "args_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "result_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'SUCCESS'::character varying,
  "latency_ms" int4 NOT NULL DEFAULT 0,
  "error_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "error_message" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "tokens_used" int4 NOT NULL DEFAULT 0,
  "cost_usd" numeric(12,8) NOT NULL DEFAULT 0,
  "idempotency_key" varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of tool_invocations
-- ----------------------------

-- ----------------------------
-- Table structure for tool_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."tool_permissions";
CREATE TABLE "public"."tool_permissions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "tool_id" uuid NOT NULL,
  "role" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "allowed" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of tool_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for tool_registrations
-- ----------------------------
DROP TABLE IF EXISTS "public"."tool_registrations";
CREATE TABLE "public"."tool_registrations" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "tool_id" uuid NOT NULL,
  "enabled" bool NOT NULL DEFAULT true,
  "rate_limit_per_min" int4 NOT NULL DEFAULT 60,
  "scopes_json" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of tool_registrations
-- ----------------------------

-- ----------------------------
-- Function structure for armor
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."armor"(bytea);
CREATE FUNCTION "public"."armor"(bytea)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pg_armor'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for armor
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."armor"(bytea, _text, _text);
CREATE FUNCTION "public"."armor"(bytea, _text, _text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pg_armor'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for crypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."crypt"(text, text);
CREATE FUNCTION "public"."crypt"(text, text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pg_crypt'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for dearmor
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."dearmor"(text);
CREATE FUNCTION "public"."dearmor"(text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_dearmor'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."decrypt"(bytea, bytea, text);
CREATE FUNCTION "public"."decrypt"(bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_decrypt'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for decrypt_iv
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."decrypt_iv"(bytea, bytea, bytea, text);
CREATE FUNCTION "public"."decrypt_iv"(bytea, bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_decrypt_iv'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for digest
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."digest"(bytea, text);
CREATE FUNCTION "public"."digest"(bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_digest'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for digest
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."digest"(text, text);
CREATE FUNCTION "public"."digest"(text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_digest'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for encrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."encrypt"(bytea, bytea, text);
CREATE FUNCTION "public"."encrypt"(bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_encrypt'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for encrypt_iv
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."encrypt_iv"(bytea, bytea, bytea, text);
CREATE FUNCTION "public"."encrypt_iv"(bytea, bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_encrypt_iv'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gen_random_bytes
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gen_random_bytes"(int4);
CREATE FUNCTION "public"."gen_random_bytes"(int4)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_random_bytes'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gen_random_uuid
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gen_random_uuid"();
CREATE FUNCTION "public"."gen_random_uuid"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/pgcrypto', 'pg_random_uuid'
  LANGUAGE c VOLATILE
  COST 1;

-- ----------------------------
-- Function structure for gen_salt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gen_salt"(text, int4);
CREATE FUNCTION "public"."gen_salt"(text, int4)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pg_gen_salt_rounds'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gen_salt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gen_salt"(text);
CREATE FUNCTION "public"."gen_salt"(text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pg_gen_salt'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for hmac
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."hmac"(text, text, text);
CREATE FUNCTION "public"."hmac"(text, text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_hmac'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for hmac
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."hmac"(bytea, bytea, text);
CREATE FUNCTION "public"."hmac"(bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pg_hmac'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_armor_headers
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_armor_headers"(text, OUT "key" text, OUT "value" text);
CREATE FUNCTION "public"."pgp_armor_headers"(IN text, OUT "key" text, OUT "value" text)
  RETURNS SETOF "pg_catalog"."record" AS '$libdir/pgcrypto', 'pgp_armor_headers'
  LANGUAGE c IMMUTABLE STRICT
  COST 1
  ROWS 1000;

-- ----------------------------
-- Function structure for pgp_key_id
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_key_id"(bytea);
CREATE FUNCTION "public"."pgp_key_id"(bytea)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_key_id_w'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt"(bytea, bytea, text, text);
CREATE FUNCTION "public"."pgp_pub_decrypt"(bytea, bytea, text, text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_text'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt"(bytea, bytea, text);
CREATE FUNCTION "public"."pgp_pub_decrypt"(bytea, bytea, text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_text'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt"(bytea, bytea);
CREATE FUNCTION "public"."pgp_pub_decrypt"(bytea, bytea)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_text'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt_bytea"(bytea, bytea, text);
CREATE FUNCTION "public"."pgp_pub_decrypt_bytea"(bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_bytea'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt_bytea"(bytea, bytea, text, text);
CREATE FUNCTION "public"."pgp_pub_decrypt_bytea"(bytea, bytea, text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_bytea'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_decrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_decrypt_bytea"(bytea, bytea);
CREATE FUNCTION "public"."pgp_pub_decrypt_bytea"(bytea, bytea)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_decrypt_bytea'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_encrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_encrypt"(text, bytea, text);
CREATE FUNCTION "public"."pgp_pub_encrypt"(text, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_encrypt_text'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_encrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_encrypt"(text, bytea);
CREATE FUNCTION "public"."pgp_pub_encrypt"(text, bytea)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_encrypt_text'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_encrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_encrypt_bytea"(bytea, bytea);
CREATE FUNCTION "public"."pgp_pub_encrypt_bytea"(bytea, bytea)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_encrypt_bytea'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_pub_encrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_pub_encrypt_bytea"(bytea, bytea, text);
CREATE FUNCTION "public"."pgp_pub_encrypt_bytea"(bytea, bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_pub_encrypt_bytea'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_decrypt"(bytea, text);
CREATE FUNCTION "public"."pgp_sym_decrypt"(bytea, text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_sym_decrypt_text'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_decrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_decrypt"(bytea, text, text);
CREATE FUNCTION "public"."pgp_sym_decrypt"(bytea, text, text)
  RETURNS "pg_catalog"."text" AS '$libdir/pgcrypto', 'pgp_sym_decrypt_text'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_decrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_decrypt_bytea"(bytea, text);
CREATE FUNCTION "public"."pgp_sym_decrypt_bytea"(bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_decrypt_bytea'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_decrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_decrypt_bytea"(bytea, text, text);
CREATE FUNCTION "public"."pgp_sym_decrypt_bytea"(bytea, text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_decrypt_bytea'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_encrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_encrypt"(text, text, text);
CREATE FUNCTION "public"."pgp_sym_encrypt"(text, text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_encrypt_text'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_encrypt
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_encrypt"(text, text);
CREATE FUNCTION "public"."pgp_sym_encrypt"(text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_encrypt_text'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_encrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_encrypt_bytea"(bytea, text);
CREATE FUNCTION "public"."pgp_sym_encrypt_bytea"(bytea, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_encrypt_bytea'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for pgp_sym_encrypt_bytea
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."pgp_sym_encrypt_bytea"(bytea, text, text);
CREATE FUNCTION "public"."pgp_sym_encrypt_bytea"(bytea, text, text)
  RETURNS "pg_catalog"."bytea" AS '$libdir/pgcrypto', 'pgp_sym_encrypt_bytea'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for set_updated_at
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at"();
CREATE FUNCTION "public"."set_updated_at"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_auth
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_auth"();
CREATE FUNCTION "public"."set_updated_at_auth"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.last_update_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_bigo
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_bigo"();
CREATE FUNCTION "public"."set_updated_at_bigo"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_eval
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_eval"();
CREATE FUNCTION "public"."set_updated_at_eval"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_iot
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_iot"();
CREATE FUNCTION "public"."set_updated_at_iot"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_lc
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_lc"();
CREATE FUNCTION "public"."set_updated_at_lc"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_llm
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_llm"();
CREATE FUNCTION "public"."set_updated_at_llm"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_pdpa
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_pdpa"();
CREATE FUNCTION "public"."set_updated_at_pdpa"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_rag
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_rag"();
CREATE FUNCTION "public"."set_updated_at_rag"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_so
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_so"();
CREATE FUNCTION "public"."set_updated_at_so"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for set_updated_at_tool
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at_tool"();
CREATE FUNCTION "public"."set_updated_at_tool"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."activity_log_id_seq"
OWNED BY "public"."activity_log"."id";
SELECT setval('"public"."activity_log_id_seq"', 2, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."command_log_id_seq"
OWNED BY "public"."command_log"."id";
SELECT setval('"public"."command_log_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."device_alert_id_seq"
OWNED BY "public"."device_alert"."id";
SELECT setval('"public"."device_alert_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."device_config_id_seq"
OWNED BY "public"."device_config"."id";
SELECT setval('"public"."device_config_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."device_status_id_seq"
OWNED BY "public"."device_status"."id";
SELECT setval('"public"."device_status_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."erp_users_id_seq"
OWNED BY "public"."erp_users"."id";
SELECT setval('"public"."erp_users_id_seq"', 10000000007, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."erp_users_id_seq1"
OWNED BY "public"."erp_users"."id";
SELECT setval('"public"."erp_users_id_seq1"', 10000000000, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."iot_data_id_seq"
OWNED BY "public"."iot_data"."id";
SELECT setval('"public"."iot_data_id_seq"', 2, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_air_control_air_control_id_seq"
OWNED BY "public"."sd_air_control"."air_control_id";
SELECT setval('"public"."sd_air_control_air_control_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_air_mod_air_mod_id_seq"
OWNED BY "public"."sd_air_mod"."air_mod_id";
SELECT setval('"public"."sd_air_mod_air_mod_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_air_period_air_period_id_seq"
OWNED BY "public"."sd_air_period"."air_period_id";
SELECT setval('"public"."sd_air_period_air_period_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_air_setting_warning_air_setting_warning_id_seq"
OWNED BY "public"."sd_air_setting_warning"."air_setting_warning_id";
SELECT setval('"public"."sd_air_setting_warning_air_setting_warning_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_air_warning_air_warning_id_seq"
OWNED BY "public"."sd_air_warning"."air_warning_id";
SELECT setval('"public"."sd_air_warning_air_warning_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_api_key_id_seq"
OWNED BY "public"."sd_api_key"."id";
SELECT setval('"public"."sd_api_key_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_audit_log_audit_id_seq"
OWNED BY "public"."sd_audit_log"."audit_id";
SELECT setval('"public"."sd_audit_log_audit_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_channel_template_id_seq"
OWNED BY "public"."sd_channel_template"."id";
SELECT setval('"public"."sd_channel_template_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_category_id_seq"
OWNED BY "public"."sd_device_category"."id";
SELECT setval('"public"."sd_device_category_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_group_id_seq"
OWNED BY "public"."sd_device_group"."id";
SELECT setval('"public"."sd_device_group_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_member_id_seq"
OWNED BY "public"."sd_device_member"."id";
SELECT setval('"public"."sd_device_member_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_notification_config_id_seq"
OWNED BY "public"."sd_device_notification_config"."id";
SELECT setval('"public"."sd_device_notification_config_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_schedule_id_seq"
OWNED BY "public"."sd_device_schedule"."id";
SELECT setval('"public"."sd_device_schedule_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_device_status_history_id_seq"
OWNED BY "public"."sd_device_status_history"."id";
SELECT setval('"public"."sd_device_status_history_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_group_notification_config_id_seq"
OWNED BY "public"."sd_group_notification_config"."id";
SELECT setval('"public"."sd_group_notification_config_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_device_alarm_action_alarm_action_id_seq"
OWNED BY "public"."sd_iot_device_alarm_action"."alarm_action_id";
SELECT setval('"public"."sd_iot_device_alarm_action_alarm_action_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_device_device_id_seq"
OWNED BY "public"."sd_iot_device"."device_id";
SELECT setval('"public"."sd_iot_device_device_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_device_type_type_id_seq"
OWNED BY "public"."sd_iot_device_type"."type_id";
SELECT setval('"public"."sd_iot_device_type_type_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_location_location_id_seq"
OWNED BY "public"."sd_iot_location"."location_id";
SELECT setval('"public"."sd_iot_location_location_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_mqtt_mqtt_id_seq"
OWNED BY "public"."sd_iot_mqtt"."mqtt_id";
SELECT setval('"public"."sd_iot_mqtt_mqtt_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_iot_schedule_schedule_id_seq"
OWNED BY "public"."sd_iot_schedule"."schedule_id";
SELECT setval('"public"."sd_iot_schedule_schedule_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_notification_channel_id_seq"
OWNED BY "public"."sd_notification_channel"."id";
SELECT setval('"public"."sd_notification_channel_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_notification_condition_id_seq"
OWNED BY "public"."sd_notification_condition"."id";
SELECT setval('"public"."sd_notification_condition_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_notification_log_id_seq"
OWNED BY "public"."sd_notification_log"."id";
SELECT setval('"public"."sd_notification_log_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_notification_type_id_seq"
OWNED BY "public"."sd_notification_type"."id";
SELECT setval('"public"."sd_notification_type_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_report_data_id_seq"
OWNED BY "public"."sd_report_data"."id";
SELECT setval('"public"."sd_report_data_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_sensor_data_id_seq"
OWNED BY "public"."sd_sensor_data"."id";
SELECT setval('"public"."sd_sensor_data_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sd_system_setting_id_seq"
OWNED BY "public"."sd_system_setting"."id";
SELECT setval('"public"."sd_system_setting_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table activity_log
-- ----------------------------
CREATE INDEX "ix_activity_log_tenant_id" ON "public"."activity_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table activity_log
-- ----------------------------
ALTER TABLE "public"."activity_log" ADD CONSTRAINT "activity_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table alembic_version
-- ----------------------------
ALTER TABLE "public"."alembic_version" ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");

-- ----------------------------
-- Indexes structure for table bigo_cache_stats
-- ----------------------------
CREATE INDEX "ix_bigo_cache_stats_tenant" ON "public"."bigo_cache_stats" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table bigo_cache_stats
-- ----------------------------
CREATE TRIGGER "trg_bigo_cache_stats_updated" BEFORE UPDATE ON "public"."bigo_cache_stats"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_bigo"();

-- ----------------------------
-- Primary Key structure for table bigo_cache_stats
-- ----------------------------
ALTER TABLE "public"."bigo_cache_stats" ADD CONSTRAINT "bigo_cache_stats_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table bigo_kafka_consumers
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_consumers" ADD CONSTRAINT "uq_bigo_consumer" UNIQUE ("tenant_id", "group_id", "topic");

-- ----------------------------
-- Checks structure for table bigo_kafka_consumers
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_consumers" ADD CONSTRAINT "ck_bigo_consumer_health" CHECK (health::text = ANY (ARRAY['HEALTHY'::character varying::text, 'WARNING'::character varying::text, 'DEGRADED'::character varying::text, 'CRITICAL'::character varying::text, 'OFFLINE'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_kafka_consumers
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_consumers" ADD CONSTRAINT "bigo_kafka_consumers_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_kafka_queues
-- ----------------------------
CREATE INDEX "ix_bigo_queue_topic" ON "public"."bigo_kafka_queues" USING btree (
  "topic" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "partition" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Checks structure for table bigo_kafka_queues
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_queues" ADD CONSTRAINT "ck_bigo_queue_health" CHECK (health::text = ANY (ARRAY['HEALTHY'::character varying::text, 'WARNING'::character varying::text, 'DEGRADED'::character varying::text, 'CRITICAL'::character varying::text, 'OFFLINE'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_kafka_queues
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_queues" ADD CONSTRAINT "bigo_kafka_queues_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table bigo_kafka_topics
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_topics" ADD CONSTRAINT "uq_bigo_topic_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Primary Key structure for table bigo_kafka_topics
-- ----------------------------
ALTER TABLE "public"."bigo_kafka_topics" ADD CONSTRAINT "bigo_kafka_topics_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_memory_leaks
-- ----------------------------
CREATE INDEX "ix_bigo_leak_tenant" ON "public"."bigo_memory_leaks" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "detected_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Checks structure for table bigo_memory_leaks
-- ----------------------------
ALTER TABLE "public"."bigo_memory_leaks" ADD CONSTRAINT "ck_bigo_leak_type" CHECK (leak_type::text = ANY (ARRAY['REFERENCE_CYCLE'::character varying::text, 'UNBOUNDED_CACHE'::character varying::text, 'LISTENER_LEAK'::character varying::text, 'THREAD_LOCAL'::character varying::text, 'NATIVE_BUFFER'::character varying::text, 'UNKNOWN'::character varying::text]));
ALTER TABLE "public"."bigo_memory_leaks" ADD CONSTRAINT "ck_bigo_leak_status" CHECK (status::text = ANY (ARRAY['OPEN'::character varying::text, 'INVESTIGATING'::character varying::text, 'RESOLVED'::character varying::text, 'IGNORED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_memory_leaks
-- ----------------------------
ALTER TABLE "public"."bigo_memory_leaks" ADD CONSTRAINT "bigo_memory_leaks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_memory_snapshots
-- ----------------------------
CREATE INDEX "ix_bigo_mem_tenant" ON "public"."bigo_memory_snapshots" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Checks structure for table bigo_memory_snapshots
-- ----------------------------
ALTER TABLE "public"."bigo_memory_snapshots" ADD CONSTRAINT "ck_bigo_mem_pressure" CHECK (pressure::text = ANY (ARRAY['NORMAL'::character varying::text, 'ELEVATED'::character varying::text, 'HIGH'::character varying::text, 'CRITICAL'::character varying::text, 'OOM'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_memory_snapshots
-- ----------------------------
ALTER TABLE "public"."bigo_memory_snapshots" ADD CONSTRAINT "bigo_memory_snapshots_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_metrics
-- ----------------------------
CREATE INDEX "ix_bigo_metric_kind" ON "public"."bigo_metrics" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "kind" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_bigo_metric_tenant" ON "public"."bigo_metrics" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Checks structure for table bigo_metrics
-- ----------------------------
ALTER TABLE "public"."bigo_metrics" ADD CONSTRAINT "ck_bigo_metric_kind" CHECK (kind::text = ANY (ARRAY['latency'::character varying::text, 'throughput'::character varying::text, 'memory_rss'::character varying::text, 'memory_heap'::character varying::text, 'cpu_percent'::character varying::text, 'gc_pause'::character varying::text, 'queue_depth'::character varying::text, 'kafka_lag'::character varying::text, 'error_rate'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_metrics
-- ----------------------------
ALTER TABLE "public"."bigo_metrics" ADD CONSTRAINT "bigo_metrics_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_profiles
-- ----------------------------
CREATE INDEX "ix_bigo_profile_function" ON "public"."bigo_profiles" USING btree (
  "function_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_bigo_profile_tenant" ON "public"."bigo_profiles" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "captured_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Checks structure for table bigo_profiles
-- ----------------------------
ALTER TABLE "public"."bigo_profiles" ADD CONSTRAINT "ck_bigo_profile_complexity" CHECK (complexity::text = ANY (ARRAY['O(1)'::character varying::text, 'O(log n)'::character varying::text, 'O(n)'::character varying::text, 'O(n log n)'::character varying::text, 'O(n^2)'::character varying::text, 'O(n^3)'::character varying::text, 'O(2^n)'::character varying::text, 'O(n!)'::character varying::text, 'UNKNOWN'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table bigo_profiles
-- ----------------------------
ALTER TABLE "public"."bigo_profiles" ADD CONSTRAINT "bigo_profiles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table bigo_ws_sessions
-- ----------------------------
CREATE INDEX "ix_bigo_ws_tenant" ON "public"."bigo_ws_sessions" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "connected_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_bigo_ws_user" ON "public"."bigo_ws_sessions" USING btree (
  "user_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table bigo_ws_sessions
-- ----------------------------
CREATE TRIGGER "trg_bigo_ws_sessions_updated" BEFORE UPDATE ON "public"."bigo_ws_sessions"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_bigo"();

-- ----------------------------
-- Uniques structure for table bigo_ws_sessions
-- ----------------------------
ALTER TABLE "public"."bigo_ws_sessions" ADD CONSTRAINT "uq_bigo_ws_conn" UNIQUE ("tenant_id", "conn_id");

-- ----------------------------
-- Primary Key structure for table bigo_ws_sessions
-- ----------------------------
ALTER TABLE "public"."bigo_ws_sessions" ADD CONSTRAINT "bigo_ws_sessions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table command_log
-- ----------------------------
CREATE INDEX "ix_command_log_device_id" ON "public"."command_log" USING btree (
  "device_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_command_log_tenant_id" ON "public"."command_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table command_log
-- ----------------------------
ALTER TABLE "public"."command_log" ADD CONSTRAINT "command_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table device_alert
-- ----------------------------
CREATE INDEX "ix_device_alert_device_id" ON "public"."device_alert" USING btree (
  "device_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_device_alert_tenant_id" ON "public"."device_alert" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_device_alert_type" ON "public"."device_alert" USING btree (
  "type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table device_alert
-- ----------------------------
ALTER TABLE "public"."device_alert" ADD CONSTRAINT "device_alert_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table device_config
-- ----------------------------
CREATE INDEX "ix_device_config_tenant_id" ON "public"."device_config" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table device_config
-- ----------------------------
ALTER TABLE "public"."device_config" ADD CONSTRAINT "device_config_deviceId_key" UNIQUE ("deviceId");

-- ----------------------------
-- Primary Key structure for table device_config
-- ----------------------------
ALTER TABLE "public"."device_config" ADD CONSTRAINT "device_config_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table device_status
-- ----------------------------
CREATE INDEX "ix_device_status_isActive" ON "public"."device_status" USING btree (
  "isActive" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_device_status_isOnline" ON "public"."device_status" USING btree (
  "isOnline" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_device_status_lastSeen" ON "public"."device_status" USING btree (
  "lastSeen" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_device_status_tenant_id" ON "public"."device_status" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table device_status
-- ----------------------------
ALTER TABLE "public"."device_status" ADD CONSTRAINT "device_status_deviceId_key" UNIQUE ("deviceId");

-- ----------------------------
-- Primary Key structure for table device_status
-- ----------------------------
ALTER TABLE "public"."device_status" ADD CONSTRAINT "device_status_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_access_tokens
-- ----------------------------
CREATE INDEX "ix_access_tokens_hashed_jti_revoked" ON "public"."erp_access_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "revoked" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_hashed_jti_key" UNIQUE ("hashed_jti");
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_previous_hashed_jti_key" UNIQUE ("previous_hashed_jti");
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "uq_access_tokens_refresh_id" UNIQUE ("refresh_id");

-- ----------------------------
-- Primary Key structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_authentications
-- ----------------------------
CREATE INDEX "ix_authentications_user_id_user_agent_device" ON "public"."erp_authentications" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "user_agent" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "device" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "uq_authentications_user_id_user_agent_device" UNIQUE ("user_id", "user_agent", "device");

-- ----------------------------
-- Primary Key structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "erp_authentications_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_keys
-- ----------------------------
CREATE INDEX "ix_keys_created_by" ON "public"."erp_keys" USING btree (
  "created_by" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "ix_keys_prefix" ON "public"."erp_keys" USING btree (
  "prefix" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_keys_updated_by" ON "public"."erp_keys" USING btree (
  "updated_by" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "uq_keys_hashed_key" UNIQUE ("hashed_key");

-- ----------------------------
-- Primary Key structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_knowledges
-- ----------------------------
CREATE INDEX "ix_knowledges_created_by" ON "public"."erp_knowledges" USING btree (
  "created_by" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "ix_knowledges_name_is_active" ON "public"."erp_knowledges" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_knowledges_updated_by" ON "public"."erp_knowledges" USING btree (
  "updated_by" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_notifications
-- ----------------------------
CREATE INDEX "ix_notifications_user_id_is_active" ON "public"."erp_notifications" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_notifications_user_id_is_read" ON "public"."erp_notifications" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST,
  "is_read" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table erp_notifications
-- ----------------------------
ALTER TABLE "public"."erp_notifications" ADD CONSTRAINT "erp_notifications_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_refresh_tokens
-- ----------------------------
CREATE INDEX "ix_refresh_tokens_hashed_jti_revoked" ON "public"."erp_refresh_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "revoked" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "uq_refresh_tokens_authentication_id" UNIQUE ("authentication_id");
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_hashed_jti_key" UNIQUE ("hashed_jti");

-- ----------------------------
-- Primary Key structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for erp_users
-- ----------------------------
SELECT setval('"public"."erp_users_id_seq1"', 10000000000, true);

-- ----------------------------
-- Indexes structure for table erp_users
-- ----------------------------
CREATE INDEX "ix_users_email_is_active" ON "public"."erp_users" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_users_status" ON "public"."erp_users" USING btree (
  "status" "pg_catalog"."enum_ops" ASC NULLS LAST
);
CREATE INDEX "ix_users_username" ON "public"."erp_users" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_users
-- ----------------------------
ALTER TABLE "public"."erp_users" ADD CONSTRAINT "erp_users_email_key" UNIQUE ("email");
ALTER TABLE "public"."erp_users" ADD CONSTRAINT "erp_users_username_key" UNIQUE ("username");

-- ----------------------------
-- Primary Key structure for table erp_users
-- ----------------------------
ALTER TABLE "public"."erp_users" ADD CONSTRAINT "erp_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table eval_datasets
-- ----------------------------
CREATE INDEX "ix_eval_ds_tenant" ON "public"."eval_datasets" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table eval_datasets
-- ----------------------------
CREATE TRIGGER "trg_eval_ds_updated" BEFORE UPDATE ON "public"."eval_datasets"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Uniques structure for table eval_datasets
-- ----------------------------
ALTER TABLE "public"."eval_datasets" ADD CONSTRAINT "uq_eval_dataset_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table eval_datasets
-- ----------------------------
ALTER TABLE "public"."eval_datasets" ADD CONSTRAINT "ck_eval_dataset_task" CHECK (task_type::text = ANY (ARRAY['qa'::character varying::text, 'summarization'::character varying::text, 'classification'::character varying::text, 'rag'::character varying::text, 'agent'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table eval_datasets
-- ----------------------------
ALTER TABLE "public"."eval_datasets" ADD CONSTRAINT "eval_datasets_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table eval_metrics
-- ----------------------------
CREATE TRIGGER "trg_eval_metric_updated" BEFORE UPDATE ON "public"."eval_metrics"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Uniques structure for table eval_metrics
-- ----------------------------
ALTER TABLE "public"."eval_metrics" ADD CONSTRAINT "uq_eval_metric_name" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table eval_metrics
-- ----------------------------
ALTER TABLE "public"."eval_metrics" ADD CONSTRAINT "eval_metrics_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table eval_reports
-- ----------------------------
CREATE INDEX "ix_eval_rep_tenant" ON "public"."eval_reports" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table eval_reports
-- ----------------------------
CREATE TRIGGER "trg_eval_rep_updated" BEFORE UPDATE ON "public"."eval_reports"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Uniques structure for table eval_reports
-- ----------------------------
ALTER TABLE "public"."eval_reports" ADD CONSTRAINT "uq_eval_report_run" UNIQUE ("run_id");

-- ----------------------------
-- Primary Key structure for table eval_reports
-- ----------------------------
ALTER TABLE "public"."eval_reports" ADD CONSTRAINT "eval_reports_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table eval_results
-- ----------------------------
CREATE INDEX "ix_eval_res_case" ON "public"."eval_results" USING btree (
  "case_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_eval_res_run_metric" ON "public"."eval_results" USING btree (
  "run_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "metric_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_eval_res_tenant" ON "public"."eval_results" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table eval_results
-- ----------------------------
CREATE TRIGGER "trg_eval_res_updated" BEFORE UPDATE ON "public"."eval_results"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Primary Key structure for table eval_results
-- ----------------------------
ALTER TABLE "public"."eval_results" ADD CONSTRAINT "eval_results_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table eval_runs
-- ----------------------------
CREATE INDEX "ix_eval_run_status" ON "public"."eval_runs" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_eval_run_tenant_time" ON "public"."eval_runs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table eval_runs
-- ----------------------------
CREATE TRIGGER "trg_eval_run_updated" BEFORE UPDATE ON "public"."eval_runs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Checks structure for table eval_runs
-- ----------------------------
ALTER TABLE "public"."eval_runs" ADD CONSTRAINT "ck_eval_run_status" CHECK (status::text = ANY (ARRAY['QUEUED'::character varying::text, 'RUNNING'::character varying::text, 'DONE'::character varying::text, 'FAILED'::character varying::text, 'CANCELLED'::character varying::text]));
ALTER TABLE "public"."eval_runs" ADD CONSTRAINT "ck_eval_run_target_kind" CHECK (target_kind::text = ANY (ARRAY['model'::character varying::text, 'pipeline'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table eval_runs
-- ----------------------------
ALTER TABLE "public"."eval_runs" ADD CONSTRAINT "eval_runs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table eval_test_cases
-- ----------------------------
CREATE INDEX "ix_eval_case_dataset" ON "public"."eval_test_cases" USING btree (
  "dataset_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_eval_case_tenant" ON "public"."eval_test_cases" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table eval_test_cases
-- ----------------------------
CREATE TRIGGER "trg_eval_case_updated" BEFORE UPDATE ON "public"."eval_test_cases"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_eval"();

-- ----------------------------
-- Primary Key structure for table eval_test_cases
-- ----------------------------
ALTER TABLE "public"."eval_test_cases" ADD CONSTRAINT "eval_test_cases_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_areas
-- ----------------------------
CREATE INDEX "ix_fs_areas_deleted_at" ON "public"."fs_areas" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_areas_zone_id" ON "public"."fs_areas" USING btree (
  "zone_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_areas
-- ----------------------------
ALTER TABLE "public"."fs_areas" ADD CONSTRAINT "fs_areas_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_device_area
-- ----------------------------
CREATE INDEX "ix_fs_device_area_area_id" ON "public"."fs_device_area" USING btree (
  "area_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_device_area_deleted_at" ON "public"."fs_device_area" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_device_area_device_id" ON "public"."fs_device_area" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_device_area
-- ----------------------------
ALTER TABLE "public"."fs_device_area" ADD CONSTRAINT "fs_device_area_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_groups
-- ----------------------------
CREATE INDEX "ix_fs_groups_deleted_at" ON "public"."fs_groups" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_groups
-- ----------------------------
ALTER TABLE "public"."fs_groups" ADD CONSTRAINT "fs_groups_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_schedule
-- ----------------------------
CREATE INDEX "ix_fs_schedule_area_id" ON "public"."fs_schedule" USING btree (
  "area_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_schedule_deleted_at" ON "public"."fs_schedule" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_schedule_group_id" ON "public"."fs_schedule" USING btree (
  "group_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_schedule_zone_id" ON "public"."fs_schedule" USING btree (
  "zone_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_schedule
-- ----------------------------
ALTER TABLE "public"."fs_schedule" ADD CONSTRAINT "fs_schedule_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_schedule_device
-- ----------------------------
CREATE INDEX "ix_fs_schedule_device_deleted_at" ON "public"."fs_schedule_device" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_schedule_device_schedule_id" ON "public"."fs_schedule_device" USING btree (
  "schedule_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_schedule_device
-- ----------------------------
ALTER TABLE "public"."fs_schedule_device" ADD CONSTRAINT "fs_schedule_device_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_schedule_history
-- ----------------------------
CREATE INDEX "ix_fs_schedule_history_schedule_id" ON "public"."fs_schedule_history" USING btree (
  "schedule_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_schedule_history
-- ----------------------------
ALTER TABLE "public"."fs_schedule_history" ADD CONSTRAINT "fs_schedule_history_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_schedule_settings
-- ----------------------------
CREATE INDEX "ix_fs_schedule_settings_schedule_id" ON "public"."fs_schedule_settings" USING btree (
  "schedule_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_schedule_settings
-- ----------------------------
ALTER TABLE "public"."fs_schedule_settings" ADD CONSTRAINT "fs_schedule_settings_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table fs_zones
-- ----------------------------
CREATE INDEX "ix_fs_zones_deleted_at" ON "public"."fs_zones" USING btree (
  "deleted_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_fs_zones_group_id" ON "public"."fs_zones" USING btree (
  "group_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table fs_zones
-- ----------------------------
ALTER TABLE "public"."fs_zones" ADD CONSTRAINT "fs_zones_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table iot_data
-- ----------------------------
CREATE INDEX "ix_iot_data_deviceId" ON "public"."iot_data" USING btree (
  "deviceId" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_data_tenant_id" ON "public"."iot_data" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_iot_data_timestamp" ON "public"."iot_data" USING btree (
  "timestamp" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table iot_data
-- ----------------------------
ALTER TABLE "public"."iot_data" ADD CONSTRAINT "iot_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table lc_agents
-- ----------------------------
CREATE INDEX "ix_lc_agent_tenant" ON "public"."lc_agents" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table lc_agents
-- ----------------------------
CREATE TRIGGER "trg_lc_agent_updated" BEFORE UPDATE ON "public"."lc_agents"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_lc"();

-- ----------------------------
-- Uniques structure for table lc_agents
-- ----------------------------
ALTER TABLE "public"."lc_agents" ADD CONSTRAINT "uq_lc_agent_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table lc_agents
-- ----------------------------
ALTER TABLE "public"."lc_agents" ADD CONSTRAINT "ck_lc_agent_type" CHECK (agent_type::text = ANY (ARRAY['react'::character varying::text, 'openai_tools'::character varying::text, 'plan_execute'::character varying::text, 'self_ask'::character varying::text, 'reflexion'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table lc_agents
-- ----------------------------
ALTER TABLE "public"."lc_agents" ADD CONSTRAINT "lc_agents_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table lc_chains
-- ----------------------------
CREATE INDEX "ix_lc_chain_tenant" ON "public"."lc_chains" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table lc_chains
-- ----------------------------
CREATE TRIGGER "trg_lc_chain_updated" BEFORE UPDATE ON "public"."lc_chains"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_lc"();

-- ----------------------------
-- Uniques structure for table lc_chains
-- ----------------------------
ALTER TABLE "public"."lc_chains" ADD CONSTRAINT "uq_lc_chain_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table lc_chains
-- ----------------------------
ALTER TABLE "public"."lc_chains" ADD CONSTRAINT "ck_lc_chain_type" CHECK (chain_type::text = ANY (ARRAY['lcel'::character varying::text, 'sequential'::character varying::text, 'router'::character varying::text, 'map_reduce'::character varying::text, 'refine'::character varying::text, 'stuff'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table lc_chains
-- ----------------------------
ALTER TABLE "public"."lc_chains" ADD CONSTRAINT "lc_chains_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table lc_memories
-- ----------------------------
CREATE INDEX "ix_lc_memory_conv" ON "public"."lc_memories" USING btree (
  "conversation_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_lc_memory_tenant" ON "public"."lc_memories" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table lc_memories
-- ----------------------------
CREATE TRIGGER "trg_lc_mem_updated" BEFORE UPDATE ON "public"."lc_memories"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_lc"();

-- ----------------------------
-- Checks structure for table lc_memories
-- ----------------------------
ALTER TABLE "public"."lc_memories" ADD CONSTRAINT "ck_lc_memory_type" CHECK (memory_type::text = ANY (ARRAY['buffer'::character varying::text, 'window'::character varying::text, 'summary'::character varying::text, 'summary_buffer'::character varying::text, 'vector'::character varying::text, 'kg'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table lc_memories
-- ----------------------------
ALTER TABLE "public"."lc_memories" ADD CONSTRAINT "lc_memories_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table lc_runs
-- ----------------------------
CREATE INDEX "ix_lc_run_tenant_time" ON "public"."lc_runs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_lc_run_user_time" ON "public"."lc_runs" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table lc_runs
-- ----------------------------
CREATE TRIGGER "trg_lc_run_updated" BEFORE UPDATE ON "public"."lc_runs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_lc"();

-- ----------------------------
-- Checks structure for table lc_runs
-- ----------------------------
ALTER TABLE "public"."lc_runs" ADD CONSTRAINT "ck_lc_run_kind" CHECK (kind::text = ANY (ARRAY['chain'::character varying::text, 'agent'::character varying::text]));
ALTER TABLE "public"."lc_runs" ADD CONSTRAINT "ck_lc_run_status" CHECK (status::text = ANY (ARRAY['QUEUED'::character varying::text, 'RUNNING'::character varying::text, 'DONE'::character varying::text, 'FAILED'::character varying::text, 'CANCELLED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table lc_runs
-- ----------------------------
ALTER TABLE "public"."lc_runs" ADD CONSTRAINT "lc_runs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table lc_traces
-- ----------------------------
CREATE INDEX "ix_lc_trace_run_step" ON "public"."lc_traces" USING btree (
  "run_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "step" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_lc_trace_tenant" ON "public"."lc_traces" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table lc_traces
-- ----------------------------
CREATE TRIGGER "trg_lc_trace_updated" BEFORE UPDATE ON "public"."lc_traces"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_lc"();

-- ----------------------------
-- Primary Key structure for table lc_traces
-- ----------------------------
ALTER TABLE "public"."lc_traces" ADD CONSTRAINT "lc_traces_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table llm_conversations
-- ----------------------------
CREATE INDEX "ix_llm_conv_tenant" ON "public"."llm_conversations" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_llm_conv_user" ON "public"."llm_conversations" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table llm_conversations
-- ----------------------------
CREATE TRIGGER "trg_llm_conv_updated" BEFORE UPDATE ON "public"."llm_conversations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_llm"();

-- ----------------------------
-- Checks structure for table llm_conversations
-- ----------------------------
ALTER TABLE "public"."llm_conversations" ADD CONSTRAINT "ck_llm_conv_status" CHECK (status::text = ANY (ARRAY['ACTIVE'::character varying::text, 'ARCHIVED'::character varying::text, 'DELETED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table llm_conversations
-- ----------------------------
ALTER TABLE "public"."llm_conversations" ADD CONSTRAINT "llm_conversations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table llm_messages
-- ----------------------------
CREATE INDEX "ix_llm_msg_conv" ON "public"."llm_messages" USING btree (
  "conversation_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table llm_messages
-- ----------------------------
CREATE TRIGGER "trg_llm_msg_updated" BEFORE UPDATE ON "public"."llm_messages"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_llm"();

-- ----------------------------
-- Checks structure for table llm_messages
-- ----------------------------
ALTER TABLE "public"."llm_messages" ADD CONSTRAINT "ck_llm_msg_role" CHECK (role::text = ANY (ARRAY['system'::character varying::text, 'user'::character varying::text, 'assistant'::character varying::text, 'tool'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table llm_messages
-- ----------------------------
ALTER TABLE "public"."llm_messages" ADD CONSTRAINT "llm_messages_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table llm_models
-- ----------------------------
CREATE INDEX "ix_llm_model_provider" ON "public"."llm_models" USING btree (
  "provider_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_llm_model_tenant" ON "public"."llm_models" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table llm_models
-- ----------------------------
CREATE TRIGGER "trg_llm_model_updated" BEFORE UPDATE ON "public"."llm_models"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_llm"();

-- ----------------------------
-- Uniques structure for table llm_models
-- ----------------------------
ALTER TABLE "public"."llm_models" ADD CONSTRAINT "uq_llm_model_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Primary Key structure for table llm_models
-- ----------------------------
ALTER TABLE "public"."llm_models" ADD CONSTRAINT "llm_models_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table llm_providers
-- ----------------------------
CREATE INDEX "ix_llm_provider_tenant" ON "public"."llm_providers" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_llm_provider_type" ON "public"."llm_providers" USING btree (
  "provider_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table llm_providers
-- ----------------------------
CREATE TRIGGER "trg_llm_provider_updated" BEFORE UPDATE ON "public"."llm_providers"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_llm"();

-- ----------------------------
-- Uniques structure for table llm_providers
-- ----------------------------
ALTER TABLE "public"."llm_providers" ADD CONSTRAINT "uq_llm_provider_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table llm_providers
-- ----------------------------
ALTER TABLE "public"."llm_providers" ADD CONSTRAINT "ck_llm_provider_type" CHECK (provider_type::text = ANY (ARRAY['openai'::character varying::text, 'anthropic'::character varying::text, 'local'::character varying::text, 'azure'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table llm_providers
-- ----------------------------
ALTER TABLE "public"."llm_providers" ADD CONSTRAINT "llm_providers_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table llm_usage_logs
-- ----------------------------
CREATE INDEX "ix_llm_usage_tenant" ON "public"."llm_usage_logs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_llm_usage_user" ON "public"."llm_usage_logs" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table llm_usage_logs
-- ----------------------------
CREATE TRIGGER "trg_llm_usage_updated" BEFORE UPDATE ON "public"."llm_usage_logs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_llm"();

-- ----------------------------
-- Primary Key structure for table llm_usage_logs
-- ----------------------------
ALTER TABLE "public"."llm_usage_logs" ADD CONSTRAINT "llm_usage_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table pdpa_consent_logs
-- ----------------------------
CREATE INDEX "ix_consent_expires" ON "public"."pdpa_consent_logs" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
) WHERE status::text = 'GRANTED'::text AND expires_at IS NOT NULL;
CREATE INDEX "ix_consent_tenant" ON "public"."pdpa_consent_logs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_consent_user" ON "public"."pdpa_consent_logs" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "uq_consent_active" ON "public"."pdpa_consent_logs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "purpose_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE status::text = 'GRANTED'::text;

-- ----------------------------
-- Triggers structure for table pdpa_consent_logs
-- ----------------------------
CREATE TRIGGER "trg_consent_logs_updated_at" BEFORE UPDATE ON "public"."pdpa_consent_logs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_pdpa"();

-- ----------------------------
-- Checks structure for table pdpa_consent_logs
-- ----------------------------
ALTER TABLE "public"."pdpa_consent_logs" ADD CONSTRAINT "pdpa_consent_logs_purpose_code_check" CHECK (purpose_code::text = ANY (ARRAY['DATA_COLLECTION'::character varying::text, 'DATA_DELETION'::character varying::text, 'USER_ACCOUNT'::character varying::text, 'USAGE_LOGS'::character varying::text, 'TRANSACTION_HISTORY'::character varying::text]));
ALTER TABLE "public"."pdpa_consent_logs" ADD CONSTRAINT "pdpa_consent_logs_status_check" CHECK (status::text = ANY (ARRAY['GRANTED'::character varying::text, 'REVOKED'::character varying::text, 'EXPIRED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table pdpa_consent_logs
-- ----------------------------
ALTER TABLE "public"."pdpa_consent_logs" ADD CONSTRAINT "pdpa_consent_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table pdpa_cookie_consents
-- ----------------------------
CREATE INDEX "ix_cc_session" ON "public"."pdpa_cookie_consents" USING btree (
  "session_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_cc_user" ON "public"."pdpa_cookie_consents" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table pdpa_cookie_consents
-- ----------------------------
CREATE TRIGGER "trg_cookie_consents_updated_at" BEFORE UPDATE ON "public"."pdpa_cookie_consents"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_pdpa"();

-- ----------------------------
-- Primary Key structure for table pdpa_cookie_consents
-- ----------------------------
ALTER TABLE "public"."pdpa_cookie_consents" ADD CONSTRAINT "pdpa_cookie_consents_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table pdpa_dsar_requests
-- ----------------------------
CREATE INDEX "ix_dsar_tenant" ON "public"."pdpa_dsar_requests" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_dsar_user" ON "public"."pdpa_dsar_requests" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table pdpa_dsar_requests
-- ----------------------------
CREATE TRIGGER "trg_dsar_requests_updated_at" BEFORE UPDATE ON "public"."pdpa_dsar_requests"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_pdpa"();

-- ----------------------------
-- Checks structure for table pdpa_dsar_requests
-- ----------------------------
ALTER TABLE "public"."pdpa_dsar_requests" ADD CONSTRAINT "pdpa_dsar_requests_status_check" CHECK (status::text = ANY (ARRAY['SUBMITTED'::character varying::text, 'VERIFIED'::character varying::text, 'PROCESSING'::character varying::text, 'COMPLETED'::character varying::text, 'REJECTED'::character varying::text]));
ALTER TABLE "public"."pdpa_dsar_requests" ADD CONSTRAINT "pdpa_dsar_requests_type_check" CHECK (type::text = ANY (ARRAY['ACCESS'::character varying::text, 'ERASURE'::character varying::text, 'WITHDRAW_CONSENT'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table pdpa_dsar_requests
-- ----------------------------
ALTER TABLE "public"."pdpa_dsar_requests" ADD CONSTRAINT "pdpa_dsar_requests_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table pdpa_idempotency_keys
-- ----------------------------
CREATE INDEX "ix_idempotency_keys_expires" ON "public"."pdpa_idempotency_keys" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_idempotency_keys_user" ON "public"."pdpa_idempotency_keys" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table pdpa_idempotency_keys
-- ----------------------------
CREATE TRIGGER "trg_idempotency_keys_updated_at" BEFORE UPDATE ON "public"."pdpa_idempotency_keys"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_pdpa"();

-- ----------------------------
-- Uniques structure for table pdpa_idempotency_keys
-- ----------------------------
ALTER TABLE "public"."pdpa_idempotency_keys" ADD CONSTRAINT "pdpa_idempotency_keys_tenant_id_idempotency_key_key" UNIQUE ("tenant_id", "idempotency_key");

-- ----------------------------
-- Primary Key structure for table pdpa_idempotency_keys
-- ----------------------------
ALTER TABLE "public"."pdpa_idempotency_keys" ADD CONSTRAINT "pdpa_idempotency_keys_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table pdpa_privacy_policies
-- ----------------------------
CREATE TRIGGER "trg_privacy_policies_updated_at" BEFORE UPDATE ON "public"."pdpa_privacy_policies"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_pdpa"();

-- ----------------------------
-- Uniques structure for table pdpa_privacy_policies
-- ----------------------------
ALTER TABLE "public"."pdpa_privacy_policies" ADD CONSTRAINT "pdpa_privacy_policies_tenant_id_version_key" UNIQUE ("tenant_id", "version");

-- ----------------------------
-- Checks structure for table pdpa_privacy_policies
-- ----------------------------
ALTER TABLE "public"."pdpa_privacy_policies" ADD CONSTRAINT "pdpa_privacy_policies_status_check" CHECK (status::text = ANY (ARRAY['DRAFT'::character varying::text, 'PUBLISHED'::character varying::text, 'SUPERSEDED'::character varying::text, 'ARCHIVED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table pdpa_privacy_policies
-- ----------------------------
ALTER TABLE "public"."pdpa_privacy_policies" ADD CONSTRAINT "pdpa_privacy_policies_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_chunks
-- ----------------------------
CREATE INDEX "ix_rag_chunk_doc_ordinal" ON "public"."rag_chunks" USING btree (
  "document_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "ordinal" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_rag_chunk_tenant" ON "public"."rag_chunks" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table rag_chunks
-- ----------------------------
CREATE TRIGGER "trg_rag_chunk_updated" BEFORE UPDATE ON "public"."rag_chunks"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Primary Key structure for table rag_chunks
-- ----------------------------
ALTER TABLE "public"."rag_chunks" ADD CONSTRAINT "rag_chunks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_citations
-- ----------------------------
CREATE INDEX "ix_rag_cit_run_rank" ON "public"."rag_citations" USING btree (
  "run_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "rank" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_rag_cit_tenant" ON "public"."rag_citations" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table rag_citations
-- ----------------------------
CREATE TRIGGER "trg_rag_cit_updated" BEFORE UPDATE ON "public"."rag_citations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Primary Key structure for table rag_citations
-- ----------------------------
ALTER TABLE "public"."rag_citations" ADD CONSTRAINT "rag_citations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_documents
-- ----------------------------
CREATE INDEX "ix_rag_doc_tenant_hash" ON "public"."rag_documents" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "hash" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_rag_doc_tenant_status" ON "public"."rag_documents" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table rag_documents
-- ----------------------------
CREATE TRIGGER "trg_rag_doc_updated" BEFORE UPDATE ON "public"."rag_documents"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Checks structure for table rag_documents
-- ----------------------------
ALTER TABLE "public"."rag_documents" ADD CONSTRAINT "ck_rag_doc_status" CHECK (status::text = ANY (ARRAY['PENDING'::character varying::text, 'PROCESSING'::character varying::text, 'READY'::character varying::text, 'FAILED'::character varying::text, 'DELETED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table rag_documents
-- ----------------------------
ALTER TABLE "public"."rag_documents" ADD CONSTRAINT "rag_documents_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_pipelines
-- ----------------------------
CREATE INDEX "ix_rag_pipe_tenant" ON "public"."rag_pipelines" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table rag_pipelines
-- ----------------------------
CREATE TRIGGER "trg_rag_pipe_updated" BEFORE UPDATE ON "public"."rag_pipelines"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Uniques structure for table rag_pipelines
-- ----------------------------
ALTER TABLE "public"."rag_pipelines" ADD CONSTRAINT "uq_rag_pipe_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table rag_pipelines
-- ----------------------------
ALTER TABLE "public"."rag_pipelines" ADD CONSTRAINT "ck_rag_pipe_chunker" CHECK (chunker_type::text = ANY (ARRAY['fixed'::character varying::text, 'recursive'::character varying::text, 'semantic'::character varying::text, 'markdown'::character varying::text, 'code'::character varying::text]));
ALTER TABLE "public"."rag_pipelines" ADD CONSTRAINT "ck_rag_pipe_reranker" CHECK (reranker_type::text = ANY (ARRAY['none'::character varying::text, 'cross_encoder'::character varying::text, 'cohere'::character varying::text, 'bge'::character varying::text]));
ALTER TABLE "public"."rag_pipelines" ADD CONSTRAINT "ck_rag_pipe_retriever" CHECK (retriever_type::text = ANY (ARRAY['vector'::character varying::text, 'bm25'::character varying::text, 'hybrid'::character varying::text, 'mmr'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table rag_pipelines
-- ----------------------------
ALTER TABLE "public"."rag_pipelines" ADD CONSTRAINT "rag_pipelines_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_retrieval_logs
-- ----------------------------
CREATE INDEX "ix_rag_rlog_run_stage" ON "public"."rag_retrieval_logs" USING btree (
  "run_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "stage" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_rag_rlog_tenant" ON "public"."rag_retrieval_logs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table rag_retrieval_logs
-- ----------------------------
CREATE TRIGGER "trg_rag_rlog_updated" BEFORE UPDATE ON "public"."rag_retrieval_logs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Primary Key structure for table rag_retrieval_logs
-- ----------------------------
ALTER TABLE "public"."rag_retrieval_logs" ADD CONSTRAINT "rag_retrieval_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table rag_runs
-- ----------------------------
CREATE INDEX "ix_rag_run_tenant_time" ON "public"."rag_runs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_rag_run_user_time" ON "public"."rag_runs" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table rag_runs
-- ----------------------------
CREATE TRIGGER "trg_rag_run_updated" BEFORE UPDATE ON "public"."rag_runs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_rag"();

-- ----------------------------
-- Checks structure for table rag_runs
-- ----------------------------
ALTER TABLE "public"."rag_runs" ADD CONSTRAINT "ck_rag_run_status" CHECK (status::text = ANY (ARRAY['QUEUED'::character varying::text, 'RETRIEVING'::character varying::text, 'RERANKING'::character varying::text, 'GENERATING'::character varying::text, 'DONE'::character varying::text, 'FAILED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table rag_runs
-- ----------------------------
ALTER TABLE "public"."rag_runs" ADD CONSTRAINT "rag_runs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_control
-- ----------------------------
CREATE INDEX "ix_sd_air_control_tenant_id" ON "public"."sd_air_control" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_control
-- ----------------------------
ALTER TABLE "public"."sd_air_control" ADD CONSTRAINT "sd_air_control_pkey" PRIMARY KEY ("air_control_id");

-- ----------------------------
-- Indexes structure for table sd_air_control_device_map
-- ----------------------------
CREATE INDEX "ix_sd_air_control_device_map_tenant_id" ON "public"."sd_air_control_device_map" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_control_device_map
-- ----------------------------
ALTER TABLE "public"."sd_air_control_device_map" ADD CONSTRAINT "sd_air_control_device_map_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_control_log
-- ----------------------------
CREATE INDEX "ix_sd_air_control_log_tenant_id" ON "public"."sd_air_control_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_control_log
-- ----------------------------
ALTER TABLE "public"."sd_air_control_log" ADD CONSTRAINT "sd_air_control_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_mod
-- ----------------------------
CREATE INDEX "ix_sd_air_mod_tenant_id" ON "public"."sd_air_mod" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_mod
-- ----------------------------
ALTER TABLE "public"."sd_air_mod" ADD CONSTRAINT "sd_air_mod_pkey" PRIMARY KEY ("air_mod_id");

-- ----------------------------
-- Indexes structure for table sd_air_mod_device_map
-- ----------------------------
CREATE INDEX "ix_sd_air_mod_device_map_tenant_id" ON "public"."sd_air_mod_device_map" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_mod_device_map
-- ----------------------------
ALTER TABLE "public"."sd_air_mod_device_map" ADD CONSTRAINT "sd_air_mod_device_map_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_period
-- ----------------------------
CREATE INDEX "ix_sd_air_period_tenant_id" ON "public"."sd_air_period" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_period
-- ----------------------------
ALTER TABLE "public"."sd_air_period" ADD CONSTRAINT "sd_air_period_pkey" PRIMARY KEY ("air_period_id");

-- ----------------------------
-- Indexes structure for table sd_air_period_device_map
-- ----------------------------
CREATE INDEX "ix_sd_air_period_device_map_tenant_id" ON "public"."sd_air_period_device_map" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_period_device_map
-- ----------------------------
ALTER TABLE "public"."sd_air_period_device_map" ADD CONSTRAINT "sd_air_period_device_map_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_setting_warning
-- ----------------------------
CREATE INDEX "ix_sd_air_setting_warning_tenant_id" ON "public"."sd_air_setting_warning" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_setting_warning
-- ----------------------------
ALTER TABLE "public"."sd_air_setting_warning" ADD CONSTRAINT "sd_air_setting_warning_pkey" PRIMARY KEY ("air_setting_warning_id");

-- ----------------------------
-- Indexes structure for table sd_air_setting_warning_device_map
-- ----------------------------
CREATE INDEX "ix_sd_air_setting_warning_device_map_tenant_id" ON "public"."sd_air_setting_warning_device_map" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_setting_warning_device_map
-- ----------------------------
ALTER TABLE "public"."sd_air_setting_warning_device_map" ADD CONSTRAINT "sd_air_setting_warning_device_map_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_air_warning
-- ----------------------------
CREATE INDEX "ix_sd_air_warning_tenant_id" ON "public"."sd_air_warning" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_warning
-- ----------------------------
ALTER TABLE "public"."sd_air_warning" ADD CONSTRAINT "sd_air_warning_pkey" PRIMARY KEY ("air_warning_id");

-- ----------------------------
-- Indexes structure for table sd_air_warning_device_map
-- ----------------------------
CREATE INDEX "ix_sd_air_warning_device_map_tenant_id" ON "public"."sd_air_warning_device_map" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_air_warning_device_map
-- ----------------------------
ALTER TABLE "public"."sd_air_warning_device_map" ADD CONSTRAINT "sd_air_warning_device_map_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_alarm_process_log
-- ----------------------------
CREATE INDEX "ix_sd_alarm_process_log_tenant_id" ON "public"."sd_alarm_process_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_alarm_process_log
-- ----------------------------
ALTER TABLE "public"."sd_alarm_process_log" ADD CONSTRAINT "sd_alarm_process_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_alarm_process_log_email
-- ----------------------------
CREATE INDEX "ix_sd_alarm_process_log_email_tenant_id" ON "public"."sd_alarm_process_log_email" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_alarm_process_log_email
-- ----------------------------
ALTER TABLE "public"."sd_alarm_process_log_email" ADD CONSTRAINT "sd_alarm_process_log_email_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_alarm_process_log_temp
-- ----------------------------
CREATE INDEX "ix_sd_alarm_process_log_temp_tenant_id" ON "public"."sd_alarm_process_log_temp" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_alarm_process_log_temp
-- ----------------------------
ALTER TABLE "public"."sd_alarm_process_log_temp" ADD CONSTRAINT "sd_alarm_process_log_temp_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_api_key
-- ----------------------------
CREATE UNIQUE INDEX "ix_sd_api_key_api_key" ON "public"."sd_api_key" USING btree (
  "api_key" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_api_key_expires_at" ON "public"."sd_api_key" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_api_key_is_active" ON "public"."sd_api_key" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_api_key_tenant_id" ON "public"."sd_api_key" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_api_key_user_id" ON "public"."sd_api_key" USING btree (
  "user_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_api_key
-- ----------------------------
ALTER TABLE "public"."sd_api_key" ADD CONSTRAINT "sd_api_key_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_audit_log
-- ----------------------------
CREATE INDEX "ix_sd_audit_log_action" ON "public"."sd_audit_log" USING btree (
  "action" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_audit_log_action_time" ON "public"."sd_audit_log" USING btree (
  "action_time" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_audit_log_entity_id" ON "public"."sd_audit_log" USING btree (
  "entity_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_audit_log_entity_type" ON "public"."sd_audit_log" USING btree (
  "entity_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_audit_log_tenant_id" ON "public"."sd_audit_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_audit_log_user_id" ON "public"."sd_audit_log" USING btree (
  "user_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_audit_log
-- ----------------------------
ALTER TABLE "public"."sd_audit_log" ADD CONSTRAINT "sd_audit_log_pkey" PRIMARY KEY ("audit_id");

-- ----------------------------
-- Indexes structure for table sd_channel_template
-- ----------------------------
CREATE INDEX "ix_sd_channel_template_channel_id" ON "public"."sd_channel_template" USING btree (
  "channel_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_channel_template_notification_type_id" ON "public"."sd_channel_template" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_channel_template_tenant_id" ON "public"."sd_channel_template" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_channel_template
-- ----------------------------
ALTER TABLE "public"."sd_channel_template" ADD CONSTRAINT "sd_channel_template_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_category
-- ----------------------------
CREATE INDEX "ix_sd_device_category_tenant_id" ON "public"."sd_device_category" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_device_category
-- ----------------------------
ALTER TABLE "public"."sd_device_category" ADD CONSTRAINT "sd_device_category_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_group
-- ----------------------------
CREATE INDEX "ix_sd_device_group_group_type" ON "public"."sd_device_group" USING btree (
  "group_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_group_is_active" ON "public"."sd_device_group" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_group_tenant_id" ON "public"."sd_device_group" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_device_group
-- ----------------------------
ALTER TABLE "public"."sd_device_group" ADD CONSTRAINT "sd_device_group_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_member
-- ----------------------------
CREATE INDEX "ix_sd_device_member_Device_id" ON "public"."sd_device_member" USING btree (
  "Device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_member_group_id" ON "public"."sd_device_member" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_member_is_active" ON "public"."sd_device_member" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_member_tenant_id" ON "public"."sd_device_member" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table sd_device_member
-- ----------------------------
ALTER TABLE "public"."sd_device_member" ADD CONSTRAINT "unique_Device_group" UNIQUE ("Device_id", "group_id");

-- ----------------------------
-- Primary Key structure for table sd_device_member
-- ----------------------------
ALTER TABLE "public"."sd_device_member" ADD CONSTRAINT "sd_device_member_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_notification_config
-- ----------------------------
CREATE INDEX "ix_sd_device_notification_config_device_id" ON "public"."sd_device_notification_config" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_notification_config_is_active" ON "public"."sd_device_notification_config" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_notification_config_notification_channel_id" ON "public"."sd_device_notification_config" USING btree (
  "notification_channel_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_notification_config_notification_type_id" ON "public"."sd_device_notification_config" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_notification_config_tenant_id" ON "public"."sd_device_notification_config" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table sd_device_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_device_notification_config" ADD CONSTRAINT "unique_Device_channel_type" UNIQUE ("device_id", "notification_channel_id", "notification_type_id");

-- ----------------------------
-- Primary Key structure for table sd_device_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_device_notification_config" ADD CONSTRAINT "sd_device_notification_config_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_schedule
-- ----------------------------
CREATE INDEX "ix_sd_device_schedule_device_id" ON "public"."sd_device_schedule" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_schedule_is_active" ON "public"."sd_device_schedule" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_schedule_next_run_at" ON "public"."sd_device_schedule" USING btree (
  "next_run_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_schedule_schedule_type" ON "public"."sd_device_schedule" USING btree (
  "schedule_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_schedule_tenant_id" ON "public"."sd_device_schedule" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_device_schedule
-- ----------------------------
ALTER TABLE "public"."sd_device_schedule" ADD CONSTRAINT "sd_device_schedule_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_device_status_history
-- ----------------------------
CREATE INDEX "ix_sd_device_status_history_device_id" ON "public"."sd_device_status_history" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_status_history_notification_type_id" ON "public"."sd_device_status_history" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_device_status_history_tenant_id" ON "public"."sd_device_status_history" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_device_status_history
-- ----------------------------
ALTER TABLE "public"."sd_device_status_history" ADD CONSTRAINT "sd_device_status_history_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_group_notification_config
-- ----------------------------
CREATE INDEX "ix_sd_group_notification_config_group_id" ON "public"."sd_group_notification_config" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_group_notification_config_notification_channel_id" ON "public"."sd_group_notification_config" USING btree (
  "notification_channel_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_group_notification_config_notification_type_id" ON "public"."sd_group_notification_config" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_group_notification_config_tenant_id" ON "public"."sd_group_notification_config" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table sd_group_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_group_notification_config" ADD CONSTRAINT "unique_group_channel_type" UNIQUE ("group_id", "notification_channel_id", "notification_type_id");

-- ----------------------------
-- Primary Key structure for table sd_group_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_group_notification_config" ADD CONSTRAINT "sd_group_notification_config_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_iot_alarm_device
-- ----------------------------
CREATE INDEX "ix_sd_iot_alarm_device_tenant_id" ON "public"."sd_iot_alarm_device" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_alarm_device
-- ----------------------------
ALTER TABLE "public"."sd_iot_alarm_device" ADD CONSTRAINT "sd_iot_alarm_device_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_iot_alarm_device_event
-- ----------------------------
CREATE INDEX "ix_sd_iot_alarm_device_event_tenant_id" ON "public"."sd_iot_alarm_device_event" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_alarm_device_event
-- ----------------------------
ALTER TABLE "public"."sd_iot_alarm_device_event" ADD CONSTRAINT "sd_iot_alarm_device_event_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_iot_device
-- ----------------------------
CREATE UNIQUE INDEX "ix_sd_iot_device_sn" ON "public"."sd_iot_device" USING btree (
  "sn" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_iot_device_tenant_id" ON "public"."sd_iot_device" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_device
-- ----------------------------
ALTER TABLE "public"."sd_iot_device" ADD CONSTRAINT "sd_iot_device_pkey" PRIMARY KEY ("device_id");

-- ----------------------------
-- Indexes structure for table sd_iot_device_alarm_action
-- ----------------------------
CREATE INDEX "ix_sd_iot_device_alarm_action_tenant_id" ON "public"."sd_iot_device_alarm_action" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_device_alarm_action
-- ----------------------------
ALTER TABLE "public"."sd_iot_device_alarm_action" ADD CONSTRAINT "sd_iot_device_alarm_action_pkey" PRIMARY KEY ("alarm_action_id");

-- ----------------------------
-- Indexes structure for table sd_iot_device_type
-- ----------------------------
CREATE INDEX "ix_sd_iot_device_type_tenant_id" ON "public"."sd_iot_device_type" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_device_type
-- ----------------------------
ALTER TABLE "public"."sd_iot_device_type" ADD CONSTRAINT "sd_iot_device_type_pkey" PRIMARY KEY ("type_id");

-- ----------------------------
-- Indexes structure for table sd_iot_location
-- ----------------------------
CREATE INDEX "ix_sd_iot_location_tenant_id" ON "public"."sd_iot_location" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_location
-- ----------------------------
ALTER TABLE "public"."sd_iot_location" ADD CONSTRAINT "sd_iot_location_pkey" PRIMARY KEY ("location_id");

-- ----------------------------
-- Indexes structure for table sd_iot_mqtt
-- ----------------------------
CREATE INDEX "ix_sd_iot_mqtt_tenant_id" ON "public"."sd_iot_mqtt" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_mqtt
-- ----------------------------
ALTER TABLE "public"."sd_iot_mqtt" ADD CONSTRAINT "sd_iot_mqtt_pkey" PRIMARY KEY ("mqtt_id");

-- ----------------------------
-- Indexes structure for table sd_iot_schedule
-- ----------------------------
CREATE INDEX "ix_sd_iot_schedule_device_id" ON "public"."sd_iot_schedule" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_iot_schedule_tenant_id" ON "public"."sd_iot_schedule" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_schedule
-- ----------------------------
ALTER TABLE "public"."sd_iot_schedule" ADD CONSTRAINT "sd_iot_schedule_pkey" PRIMARY KEY ("schedule_id");

-- ----------------------------
-- Indexes structure for table sd_iot_schedule_device
-- ----------------------------
CREATE INDEX "ix_sd_iot_schedule_device_tenant_id" ON "public"."sd_iot_schedule_device" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_iot_schedule_device
-- ----------------------------
ALTER TABLE "public"."sd_iot_schedule_device" ADD CONSTRAINT "sd_iot_schedule_device_pkey" PRIMARY KEY ("schedule_id", "device_id");

-- ----------------------------
-- Indexes structure for table sd_mqtt_host
-- ----------------------------
CREATE INDEX "ix_sd_mqtt_host_tenant_id" ON "public"."sd_mqtt_host" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_mqtt_host
-- ----------------------------
ALTER TABLE "public"."sd_mqtt_host" ADD CONSTRAINT "sd_mqtt_host_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_notification_channel
-- ----------------------------
CREATE INDEX "ix_sd_notification_channel_tenant_id" ON "public"."sd_notification_channel" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_notification_channel
-- ----------------------------
ALTER TABLE "public"."sd_notification_channel" ADD CONSTRAINT "sd_notification_channel_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_notification_condition
-- ----------------------------
CREATE INDEX "ix_sd_notification_condition_device_id" ON "public"."sd_notification_condition" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_condition_is_active" ON "public"."sd_notification_condition" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_condition_notification_type_id" ON "public"."sd_notification_condition" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_condition_tenant_id" ON "public"."sd_notification_condition" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_notification_condition
-- ----------------------------
ALTER TABLE "public"."sd_notification_condition" ADD CONSTRAINT "sd_notification_condition_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_notification_log
-- ----------------------------
CREATE INDEX "ix_sd_notification_log_device_id" ON "public"."sd_notification_log" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_log_notification_channel_id" ON "public"."sd_notification_log" USING btree (
  "notification_channel_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_log_notification_type_id" ON "public"."sd_notification_log" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_log_status" ON "public"."sd_notification_log" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_notification_log_tenant_id" ON "public"."sd_notification_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_notification_log
-- ----------------------------
ALTER TABLE "public"."sd_notification_log" ADD CONSTRAINT "sd_notification_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_notification_type
-- ----------------------------
CREATE INDEX "ix_sd_notification_type_tenant_id" ON "public"."sd_notification_type" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_notification_type
-- ----------------------------
ALTER TABLE "public"."sd_notification_type" ADD CONSTRAINT "sd_notification_type_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_report_data
-- ----------------------------
CREATE INDEX "ix_sd_report_data_device_id" ON "public"."sd_report_data" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_report_data_generated_at" ON "public"."sd_report_data" USING btree (
  "generated_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_report_data_period_end" ON "public"."sd_report_data" USING btree (
  "period_end" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_report_data_period_start" ON "public"."sd_report_data" USING btree (
  "period_start" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_report_data_report_type" ON "public"."sd_report_data" USING btree (
  "report_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_report_data_tenant_id" ON "public"."sd_report_data" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_report_data
-- ----------------------------
ALTER TABLE "public"."sd_report_data" ADD CONSTRAINT "sd_report_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_schedule_process_log
-- ----------------------------
CREATE INDEX "ix_sd_schedule_process_log_tenant_id" ON "public"."sd_schedule_process_log" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_schedule_process_log
-- ----------------------------
ALTER TABLE "public"."sd_schedule_process_log" ADD CONSTRAINT "sd_schedule_process_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_sensor_data
-- ----------------------------
CREATE INDEX "ix_sd_sensor_data_device_id" ON "public"."sd_sensor_data" USING btree (
  "device_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_sensor_data_notification_type_id" ON "public"."sd_sensor_data" USING btree (
  "notification_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_sensor_data_tenant_id" ON "public"."sd_sensor_data" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_sensor_data_timestamp" ON "public"."sd_sensor_data" USING btree (
  "timestamp" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_sensor_data
-- ----------------------------
ALTER TABLE "public"."sd_sensor_data" ADD CONSTRAINT "sd_sensor_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sd_system_setting
-- ----------------------------
CREATE INDEX "ix_sd_system_setting_category" ON "public"."sd_system_setting" USING btree (
  "category" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_sd_system_setting_key" ON "public"."sd_system_setting" USING btree (
  "key" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sd_system_setting_tenant_id" ON "public"."sd_system_setting" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sd_system_setting
-- ----------------------------
ALTER TABLE "public"."sd_system_setting" ADD CONSTRAINT "sd_system_setting_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table so_outputs
-- ----------------------------
CREATE INDEX "ix_so_out_request" ON "public"."so_outputs" USING btree (
  "request_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_so_out_tenant" ON "public"."so_outputs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table so_outputs
-- ----------------------------
CREATE TRIGGER "trg_so_out_updated" BEFORE UPDATE ON "public"."so_outputs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_so"();

-- ----------------------------
-- Primary Key structure for table so_outputs
-- ----------------------------
ALTER TABLE "public"."so_outputs" ADD CONSTRAINT "so_outputs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table so_repairs
-- ----------------------------
CREATE INDEX "ix_so_rep_output" ON "public"."so_repairs" USING btree (
  "output_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_so_rep_tenant" ON "public"."so_repairs" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table so_repairs
-- ----------------------------
CREATE TRIGGER "trg_so_rep_updated" BEFORE UPDATE ON "public"."so_repairs"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_so"();

-- ----------------------------
-- Primary Key structure for table so_repairs
-- ----------------------------
ALTER TABLE "public"."so_repairs" ADD CONSTRAINT "so_repairs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table so_requests
-- ----------------------------
CREATE INDEX "ix_so_req_schema" ON "public"."so_requests" USING btree (
  "schema_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_so_req_tenant_time" ON "public"."so_requests" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table so_requests
-- ----------------------------
CREATE TRIGGER "trg_so_req_updated" BEFORE UPDATE ON "public"."so_requests"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_so"();

-- ----------------------------
-- Primary Key structure for table so_requests
-- ----------------------------
ALTER TABLE "public"."so_requests" ADD CONSTRAINT "so_requests_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table so_schemas
-- ----------------------------
CREATE INDEX "ix_so_schema_tenant" ON "public"."so_schemas" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table so_schemas
-- ----------------------------
CREATE TRIGGER "trg_so_schema_updated" BEFORE UPDATE ON "public"."so_schemas"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_so"();

-- ----------------------------
-- Uniques structure for table so_schemas
-- ----------------------------
ALTER TABLE "public"."so_schemas" ADD CONSTRAINT "uq_so_schema_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table so_schemas
-- ----------------------------
ALTER TABLE "public"."so_schemas" ADD CONSTRAINT "ck_so_schema_strategy" CHECK (strategy::text = ANY (ARRAY['json_mode'::character varying::text, 'function_call'::character varying::text, 'grammar'::character varying::text, 'regex'::character varying::text, 'prompt_only'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table so_schemas
-- ----------------------------
ALTER TABLE "public"."so_schemas" ADD CONSTRAINT "so_schemas_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table so_validations
-- ----------------------------
CREATE INDEX "ix_so_val_output" ON "public"."so_validations" USING btree (
  "output_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_so_val_tenant" ON "public"."so_validations" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table so_validations
-- ----------------------------
CREATE TRIGGER "trg_so_val_updated" BEFORE UPDATE ON "public"."so_validations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_so"();

-- ----------------------------
-- Primary Key structure for table so_validations
-- ----------------------------
ALTER TABLE "public"."so_validations" ADD CONSTRAINT "so_validations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table tool_definitions
-- ----------------------------
CREATE INDEX "ix_tool_def_kind" ON "public"."tool_definitions" USING btree (
  "kind" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_tool_def_tenant" ON "public"."tool_definitions" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table tool_definitions
-- ----------------------------
CREATE TRIGGER "trg_tool_def_updated" BEFORE UPDATE ON "public"."tool_definitions"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_tool"();

-- ----------------------------
-- Uniques structure for table tool_definitions
-- ----------------------------
ALTER TABLE "public"."tool_definitions" ADD CONSTRAINT "uq_tool_name" UNIQUE ("tenant_id", "name");

-- ----------------------------
-- Checks structure for table tool_definitions
-- ----------------------------
ALTER TABLE "public"."tool_definitions" ADD CONSTRAINT "ck_tool_kind" CHECK (kind::text = ANY (ARRAY['http'::character varying::text, 'python'::character varying::text, 'sql'::character varying::text, 'shell'::character varying::text, 'mcp'::character varying::text, 'openapi'::character varying::text]));
ALTER TABLE "public"."tool_definitions" ADD CONSTRAINT "ck_tool_risk" CHECK (risk_level::text = ANY (ARRAY['low'::character varying::text, 'medium'::character varying::text, 'high'::character varying::text, 'critical'::character varying::text]));
ALTER TABLE "public"."tool_definitions" ADD CONSTRAINT "ck_tool_visibility" CHECK (visibility::text = ANY (ARRAY['private'::character varying::text, 'tenant'::character varying::text, 'public'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table tool_definitions
-- ----------------------------
ALTER TABLE "public"."tool_definitions" ADD CONSTRAINT "tool_definitions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table tool_invocations
-- ----------------------------
CREATE INDEX "ix_tool_inv_tenant" ON "public"."tool_invocations" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);
CREATE INDEX "ix_tool_inv_tool" ON "public"."tool_invocations" USING btree (
  "tool_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "created_at" "pg_catalog"."timestamptz_ops" DESC NULLS FIRST
);

-- ----------------------------
-- Triggers structure for table tool_invocations
-- ----------------------------
CREATE TRIGGER "trg_tool_inv_updated" BEFORE UPDATE ON "public"."tool_invocations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_tool"();

-- ----------------------------
-- Checks structure for table tool_invocations
-- ----------------------------
ALTER TABLE "public"."tool_invocations" ADD CONSTRAINT "ck_tool_inv_status" CHECK (status::text = ANY (ARRAY['SUCCESS'::character varying::text, 'ERROR'::character varying::text, 'TIMEOUT'::character varying::text, 'DENIED'::character varying::text, 'RATE_LIMITED'::character varying::text]));

-- ----------------------------
-- Primary Key structure for table tool_invocations
-- ----------------------------
ALTER TABLE "public"."tool_invocations" ADD CONSTRAINT "tool_invocations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table tool_permissions
-- ----------------------------
CREATE INDEX "ix_tool_perm_tenant" ON "public"."tool_permissions" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table tool_permissions
-- ----------------------------
CREATE TRIGGER "trg_tool_perm_updated" BEFORE UPDATE ON "public"."tool_permissions"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_tool"();

-- ----------------------------
-- Uniques structure for table tool_permissions
-- ----------------------------
ALTER TABLE "public"."tool_permissions" ADD CONSTRAINT "uq_tool_perm_role" UNIQUE ("tool_id", "role");

-- ----------------------------
-- Primary Key structure for table tool_permissions
-- ----------------------------
ALTER TABLE "public"."tool_permissions" ADD CONSTRAINT "tool_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table tool_registrations
-- ----------------------------
CREATE INDEX "ix_tool_reg_tenant" ON "public"."tool_registrations" USING btree (
  "tenant_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table tool_registrations
-- ----------------------------
CREATE TRIGGER "trg_tool_reg_updated" BEFORE UPDATE ON "public"."tool_registrations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."set_updated_at_tool"();

-- ----------------------------
-- Uniques structure for table tool_registrations
-- ----------------------------
ALTER TABLE "public"."tool_registrations" ADD CONSTRAINT "uq_tool_reg_tool" UNIQUE ("tool_id");

-- ----------------------------
-- Primary Key structure for table tool_registrations
-- ----------------------------
ALTER TABLE "public"."tool_registrations" ADD CONSTRAINT "tool_registrations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_refresh_id_fkey" FOREIGN KEY ("refresh_id") REFERENCES "public"."erp_refresh_tokens" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "erp_authentications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_notifications
-- ----------------------------
ALTER TABLE "public"."erp_notifications" ADD CONSTRAINT "erp_notifications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_authentication_id_fkey" FOREIGN KEY ("authentication_id") REFERENCES "public"."erp_authentications" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_areas
-- ----------------------------
ALTER TABLE "public"."fs_areas" ADD CONSTRAINT "fs_areas_zone_id_fkey" FOREIGN KEY ("zone_id") REFERENCES "public"."fs_zones" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_device_area
-- ----------------------------
ALTER TABLE "public"."fs_device_area" ADD CONSTRAINT "fs_device_area_area_id_fkey" FOREIGN KEY ("area_id") REFERENCES "public"."fs_areas" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_schedule_device
-- ----------------------------
ALTER TABLE "public"."fs_schedule_device" ADD CONSTRAINT "fs_schedule_device_schedule_id_fkey" FOREIGN KEY ("schedule_id") REFERENCES "public"."fs_schedule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_schedule_history
-- ----------------------------
ALTER TABLE "public"."fs_schedule_history" ADD CONSTRAINT "fs_schedule_history_schedule_id_fkey" FOREIGN KEY ("schedule_id") REFERENCES "public"."fs_schedule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_schedule_settings
-- ----------------------------
ALTER TABLE "public"."fs_schedule_settings" ADD CONSTRAINT "fs_schedule_settings_schedule_id_fkey" FOREIGN KEY ("schedule_id") REFERENCES "public"."fs_schedule" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table fs_zones
-- ----------------------------
ALTER TABLE "public"."fs_zones" ADD CONSTRAINT "fs_zones_group_id_fkey" FOREIGN KEY ("group_id") REFERENCES "public"."fs_groups" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_device_member
-- ----------------------------
ALTER TABLE "public"."sd_device_member" ADD CONSTRAINT "sd_device_member_Device_id_fkey" FOREIGN KEY ("Device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_device_member" ADD CONSTRAINT "sd_device_member_group_id_fkey" FOREIGN KEY ("group_id") REFERENCES "public"."sd_device_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_device_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_device_notification_config" ADD CONSTRAINT "sd_device_notification_config_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_device_notification_config" ADD CONSTRAINT "sd_device_notification_config_notification_channel_id_fkey" FOREIGN KEY ("notification_channel_id") REFERENCES "public"."sd_notification_channel" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_device_notification_config" ADD CONSTRAINT "sd_device_notification_config_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_device_schedule
-- ----------------------------
ALTER TABLE "public"."sd_device_schedule" ADD CONSTRAINT "sd_device_schedule_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_device_status_history
-- ----------------------------
ALTER TABLE "public"."sd_device_status_history" ADD CONSTRAINT "sd_device_status_history_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_device_status_history" ADD CONSTRAINT "sd_device_status_history_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_group_notification_config
-- ----------------------------
ALTER TABLE "public"."sd_group_notification_config" ADD CONSTRAINT "sd_group_notification_config_group_id_fkey" FOREIGN KEY ("group_id") REFERENCES "public"."sd_device_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_group_notification_config" ADD CONSTRAINT "sd_group_notification_config_notification_channel_id_fkey" FOREIGN KEY ("notification_channel_id") REFERENCES "public"."sd_notification_channel" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_group_notification_config" ADD CONSTRAINT "sd_group_notification_config_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_notification_condition
-- ----------------------------
ALTER TABLE "public"."sd_notification_condition" ADD CONSTRAINT "sd_notification_condition_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_notification_condition" ADD CONSTRAINT "sd_notification_condition_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_notification_log
-- ----------------------------
ALTER TABLE "public"."sd_notification_log" ADD CONSTRAINT "sd_notification_log_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_notification_log" ADD CONSTRAINT "sd_notification_log_notification_channel_id_fkey" FOREIGN KEY ("notification_channel_id") REFERENCES "public"."sd_notification_channel" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_notification_log" ADD CONSTRAINT "sd_notification_log_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_report_data
-- ----------------------------
ALTER TABLE "public"."sd_report_data" ADD CONSTRAINT "sd_report_data_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sd_sensor_data
-- ----------------------------
ALTER TABLE "public"."sd_sensor_data" ADD CONSTRAINT "sd_sensor_data_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "public"."sd_iot_device" ("device_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sd_sensor_data" ADD CONSTRAINT "sd_sensor_data_notification_type_id_fkey" FOREIGN KEY ("notification_type_id") REFERENCES "public"."sd_notification_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
