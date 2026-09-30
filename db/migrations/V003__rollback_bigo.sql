-- V003__rollback_bigo.sql
BEGIN;
DROP TABLE IF EXISTS "public"."bigo_ws_sessions"  CASCADE;
DROP TABLE IF EXISTS "public"."bigo_cache_stats" CASCADE;
DROP TABLE IF EXISTS "public"."bigo_pipeline_reports" CASCADE;
DROP TABLE IF EXISTS "public"."bigo_kafka_consumers"  CASCADE;
DROP TABLE IF EXISTS "public"."bigo_kafka_queues"     CASCADE;
DROP TABLE IF EXISTS "public"."bigo_kafka_topics"     CASCADE;
DROP TABLE IF EXISTS "public"."bigo_memory_leaks"     CASCADE;
DROP TABLE IF EXISTS "public"."bigo_memory_snapshots" CASCADE;
DROP TABLE IF EXISTS "public"."bigo_profiles"         CASCADE;
DROP TABLE IF EXISTS "public"."bigo_metrics"          CASCADE;
DROP FUNCTION IF EXISTS public.set_updated_at_bigo();
COMMIT;
