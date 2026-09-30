-- V002__seed_bigo.sql
BEGIN;
INSERT INTO "public"."bigo_kafka_topics"
    (tenant_id, name, partitions, replication_factor, is_active)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'llm.events', 3, 1, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'aiml.events', 3, 1, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'iot.telemetry', 6, 1, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'monitoring.logs', 4, 1, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'monitoring.logs.dlq', 1, 1, TRUE)
ON CONFLICT DO NOTHING;
COMMIT;
