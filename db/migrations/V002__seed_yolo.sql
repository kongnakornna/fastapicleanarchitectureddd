-- V002__seed_yolo.sql
BEGIN;
INSERT INTO "public"."yolo_datasets" (tenant_id, name, format, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'demo-coco-subset', 'yolo', 'DRAFT')
ON CONFLICT DO NOTHING;
COMMIT;
