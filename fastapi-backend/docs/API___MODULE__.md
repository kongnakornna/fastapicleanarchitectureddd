# API Reference — Money

Base URL: {BASE_URL}/api/v1/money

## Authentication

ทุก request ต้องมี:

    Authorization: Bearer <JWT>
    Idempotency-Key: <uuid>   # เฉพาะ POST/PATCH/DELETE

## Endpoints

### POST / — สร้างใหม่

Request:

    {
      "code": "X-001",
      "name": "Sample",
      "amount": "100.00",
      "currency": "THB",
      "metadata": {}
    }

Response 201:

    {
      "id": "00000000-0000-0000-0000-000000000000",
      "code": "X-001",
      "name": "Sample",
      "amount": "100.00",
      "status": "ACTIVE",
      "version": 1
    }

Errors:

| Status | Code | Description |
|---|---|---|
| 400 | DOMAIN_ERROR | amount < 0 |
| 409 | DUPLICATE_CODE | code ซ้ำ |
| 422 | VALIDATION_ERROR | schema ไม่ถูก |

### GET / — List

Query params: status, q, limit, offset

### GET /{id} — Get by ID

Response 404 ถ้าไม่พบ

### PATCH /{id} — Update

Request: partial {"name": "New"}

### DELETE /{id} — Soft Delete

Response 204