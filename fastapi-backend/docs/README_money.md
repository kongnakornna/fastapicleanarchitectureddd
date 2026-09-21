# Module: money

> Schema: `tenant_mon` | Table: `moneys`
> Generated: 2026-09-21

## Purpose

TH: describe the purpose of module `money`
EN: describe the purpose of module `money`

## Database

**Schema:** `tenant_mon`
**Table:**  `moneys`

| Column | Type | Key | Constraints |
|---|---|---|---|


## SQL Migrations

Files under `migrations/versions/db/`:

    migrations/versions/db/V001__create_money.sql
    migrations/versions/db/V002__seed_money.sql
    migrations/versions/db/V003__rollback_money.sql

Generate more:

    module_sql_router.bat update money --desc "add tax rate"

## API Endpoints

| Method | Path | Summary | Status |
|---|---|---|---|
| POST | /api/v1/money/add/ | POST /add/ | 200 |
| POST | /api/v1/money/subtract/ | POST /subtract/ | 200 |
| POST | /api/v1/money/vat/calculate/ | POST /vat/calculate/ | 200 |
| POST | /api/v1/money/vat/extract/ | POST /vat/extract/ | 200 |
| POST | /api/v1/money/convert/ | POST /convert/ | 200 |

## Postman

Import `docs/postman/money.postman_collection.json`

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-09-21 | initial release |