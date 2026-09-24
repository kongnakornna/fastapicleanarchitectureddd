# Changelog

## [1.0.0] - 2026-09-23

### Added
- Domain layer (enums, exceptions, events, value objects, alarm_logic)
- Application layer (IotUseCase with 25+ methods)
- Infrastructure layer (43 SQLAlchemy models, 9 repositories)
- Presentation layer (30+ HTTP + 1 WebSocket endpoints)
- Fullschedule module (8 tables)
- Demo data (200 rows/table × 56 tables)
- WebSocket real-time broadcast
- Multi-channel alerting (Email/LINE/Telegram/Webhook)
- Batch operations
- Scheduler (cron jobs)
- Idempotency support
- Cross-tenant RLS
- Docker + docker-compose
- CI/CD (GitHub Actions)
- 11 manuals + Postman collection
- Property-based tests

### Features
- Real-time MQTT ingest
- Multi-language alarms (TH/EN)
- Cache layers (Redis + in-process)
- Time-series (InfluxDB)
- Multi-tenant