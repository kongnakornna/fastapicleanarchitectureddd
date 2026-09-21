# Manual Test — money

## Pre-conditions
- [ ] DB migrated (V001–V003)
- [ ] Redis running
- [ ] Kafka running (ถ้ามี)
- [ ] .env set TEST_DATABASE_URL

## Scenarios (8)

| # | Scenario | Method | Endpoint | Expected | OK |
|---|---|---|---|---|---|
| 1 | Create happy | POST | /api/v1/money/ | 201 + body | [ ] |
| 2 | Create duplicate | POST | /api/v1/money/ | 409 | [ ] |
| 3 | Create invalid amount | POST | /api/v1/money/ | 422 | [ ] |
| 4 | Get by id | GET | /api/v1/money/{id} | 200 | [ ] |
| 5 | List + filter | GET | /api/v1/money/?status=ACTIVE | 200 | [ ] |
| 6 | Update | PATCH | /api/v1/money/{id} | 200 + version+1 | [ ] |
| 7 | Delete (soft) | DELETE | /api/v1/money/{id} | 204 | [ ] |
| 8 | Cross-tenant | GET | other tenant token | 404 | [ ] |

## Idempotency
- [ ] POST ซ้ำด้วย Idempotency-Key เดิม -> ได้ response เดิม
- [ ] POST ด้วย key เดิม + payload ต่าง -> 422

## Security
- [ ] ไม่มี token -> 401
- [ ] token ผิด scope -> 403
- [ ] SQL injection ที่ code -> 422