# API Reference - Money

**Base URL:** `http://localhost:8000/api/v1`
**Module:** money
**Generated:** 2026-09-21

## Authentication

All endpoints require:

    Authorization: Bearer <JWT>

POST/PATCH/DELETE also require:

    Idempotency-Key: <uuid-v4>

## Endpoints


### POST /api/v1/money/add/

POST /add/

- Status: `200`
- Handler: `add`


### POST /api/v1/money/subtract/

POST /subtract/

- Status: `200`
- Handler: `subtract`


### POST /api/v1/money/vat/calculate/

POST /vat/calculate/

- Status: `200`
- Handler: `vat_calculate`


### POST /api/v1/money/vat/extract/

POST /vat/extract/

- Status: `200`
- Handler: `vat_extract`


### POST /api/v1/money/convert/

POST /convert/

- Status: `200`
- Handler: `convert`



## Error Responses

| Status | Meaning |
|---|---|
| 400 | Domain error |
| 401 | Missing or invalid token |
| 403 | Insufficient scope |
| 404 | Entity not found |
| 409 | Duplicate code / version conflict |
| 422 | Validation error |

## OpenAPI

- Interactive: http://localhost:8000/docs
- Machine:     http://localhost:8000/openapi.json