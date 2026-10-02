-- V003__rollback_yolo.sql
BEGIN;
DROP POLICY IF EXISTS p_yolo_inf ON "public"."yolo_inferences";
DROP POLICY IF EXISTS p_yolo_model ON "public"."yolo_models";
DROP POLICY IF EXISTS p_yolo_tr ON "public"."yolo_trainings";
DROP POLICY IF EXISTS p_yolo_ann ON "public"."yolo_annotations";
DROP POLICY IF EXISTS p_yolo_img ON "public"."yolo_images";
DROP POLICY IF EXISTS p_yolo_cls ON "public"."yolo_classes";
DROP POLICY IF EXISTS p_yolo_ds ON "public"."yolo_datasets";
DROP TABLE IF EXISTS "public"."yolo_inferences" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_models" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_trainings" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_annotations" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_images" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_classes" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_datasets" CASCADE;
COMMIT;
