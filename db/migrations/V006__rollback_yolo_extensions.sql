-- V006__rollback_yolo_extensions.sql
BEGIN;
DROP POLICY IF EXISTS p_yolo_ga ON "public"."yolo_growth_assessments";
DROP POLICY IF EXISTS p_yolo_fields ON "public"."yolo_fields";
DROP POLICY IF EXISTS p_yolo_pd ON "public"."yolo_plant_diagnoses";
DROP POLICY IF EXISTS p_yolo_cr ON "public"."yolo_counting_results";
DROP POLICY IF EXISTS p_yolo_cs ON "public"."yolo_counting_sessions";
DROP POLICY IF EXISTS p_yolo_categories ON "public"."yolo_categories";
DROP POLICY IF EXISTS p_yolo_settings ON "public"."yolo_settings";
DROP TABLE IF EXISTS "public"."yolo_growth_assessments" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_fields" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_plant_diagnoses" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_diseases" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_counting_results" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_counting_sessions" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_categories" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_settings" CASCADE;
COMMIT;
