# ICMON Auto Repair - Project Overview

FastAPI backend for **ICMON Auto Repair Shop Management System**, migrated from Go to Python with Domain-Driven Design + Onion Architecture.

---

## Architecture

### DDD + Onion Architecture

```
app/
  core/              # Framework-agnostic infrastructure (DB, cache, MQTT, settings)
  modules/
    {module}/
      domain/        # Entities, Value Objects, Domain Services, Mappers
        entities/    # SQLAlchemy ORM models (also domain entities)
        value_objects/
        services.py
        mappers.py
      application/   # Use Cases, Interfaces (Repository ports), Enums, Utils
        use_cases.py
        interfaces.py
      infrastructure/# Repository implementations, external adapters
        models.py    # (in some modules; others use domain entities directly)
        *_repository.py
      presentation/  # FastAPI routers, Pydantic schemas, dependencies, exceptions
        router.py    # or routers.py
        schemas.py
        dependencies.py
        exceptions.py
        docs.py
    shared/          # Cross-cutting: Base models, shared enums, shared utils
```

### Data Flow

```
HTTP Request
  -> Presentation (Router + Pydantic Schema)
    -> Application (Use Case)
      -> Domain (Entities / Value Objects / Domain Services)
      -> Infrastructure (Repository -> PostgreSQL / InfluxDB / Redis)
    -> Presentation (Response Schema)
  -> HTTP Response
```

---

## Tech Stack

| Layer            | Technology                                                  |
|------------------|-------------------------------------------------------------|
| Framework        | FastAPI 0.135+                                              |
| ORM              | SQLAlchemy 2.0 (async via asyncpg)                          |
| Validation       | Pydantic v2 + pydantic-settings                             |
| Database         | PostgreSQL 15+ (asyncpg driver)                             |
| Time-Series DB   | InfluxDB 2.x (influxdb-client)                              |
| Cache / Queue    | Redis 7+ (redis-py)                                         |
| MQTT Broker      | Eclipse Mosquitto (paho-mqtt 2.x)                           |
| Password Hash    | Argon2 (pwdlib + argon2-cffi)                               |
| JWT              | jwcrypto (signed + encrypted JWT with rotation)             |
| Migrations       | Alembic                                                     |
| Logging          | Loguru                                                      |
| Error Tracking   | Sentry SDK                                                  |
| Linting          | Ruff (line-length 100, Python 3.13 target)                  |
| Testing          | pytest (asyncio_mode=auto)                                  |
| ASGI Server      | Hypercorn / Uvicorn                                         |
| Containerization | Docker + docker-compose                                     |

---

## Module List

| Module            | Prefix                | Description                                              |
|-------------------|-----------------------|----------------------------------------------------------|
| **Authentication**| `/api/v1/authentication` | Login, register, logout, refresh JWT, session management |
| **User**          | `/api/v1/user`        | User CRUD, profile (me), roles/permissions               |
| **Customer**      | `/customer`           | Customer CRUD + Car CRUD (vehicles linked to customers)  |
| **Item**          | `/item`               | Generic item/part management                             |
| **IoT (MQTT3)**   | `/mqtt3`              | 30+ endpoints: devices, sensor data, alerts, WebSocket, MQTT control |
| **Batch**         | `/batch`              | Batch job scheduling, execution, and logs                |
| **Dashboard**     | `/dashboard`          | Stats, revenue charts, top parts, job status summary     |
| **Document**      | `/document`           | Document/file upload and management                      |
| **Email**         | `/email`              | Send email, view logs, SMTP config management            |
| **I18n**          | `/i18n`               | Translation key-value management (multi-locale)          |
| **Payment**       | `/payment`            | Payment recording, receipts, refunds, outstanding balance|
| **Purchase Order**| `/purchase-order`     | PO lifecycle: draft -> sent -> confirmed -> received     |
| **Quotation**     | `/quotation`          | Quotation creation, approval, PO conversion              |
| **Report**        | `/report`             | PDF report generation (daily sales, inventory, invoices) |
| **WOS**           | `/wos`                | Web Order System (online orders from customers)          |
| **Health**        | `/health`             | Health check, Alembic version, root redirect             |
| **Example**       | `/api/v1/example`     | Reference module demonstrating the DDD pattern           |

---

## Directory Structure

```
fastapiddd/
├── app/
│   ├── app.py                          # FastAPI application factory
│   ├── core/
│   │   ├── database.py                 # SQLAlchemy sync + async engines
│   │   ├── settings.py                 # Pydantic Settings (all env vars)
│   │   ├── security.py                 # JWT auth, password hashing
│   │   ├── middleware.py               # CORS, rate limit, request logging
│   │   ├── exception_handler.py        # Global exception handlers
│   │   ├── redis.py                    # Redis client
│   │   ├── influxdb_client.py          # InfluxDB client
│   │   ├── mqtt_client.py              # MQTT client (paho-mqtt)
│   │   ├── websocket_hub.py            # WebSocket connection manager
│   │   ├── key_management.py           # JWT key management
│   │   ├── logging.py                  # Loguru setup
│   │   ├── resources.py                # Lifespan (startup/shutdown)
│   │   ├── migrations.py               # Alembic integration
│   │   └── queue/                      # Queue abstraction (Redis / noop)
│   └── modules/
│       ├── shared/
│       │   ├── application/            # Enums (Role, Environment), utils
│       │   ├── domain/                 # DomainError, shared entities
│       │   ├── infrastructure/         # BaseModel (id, is_active, created_at, updated_at)
│       │   └── presentation/           # StandardException, shared response formatting
│       ├── authentication/             # JWT session management
│       ├── user/                       # User + RBAC (roles, permissions)
│       ├── customer/                   # Customer + Car (vehicle)
│       ├── items/                      # Item/part management
│       ├── iot/                        # IoT device monitoring (PostgreSQL + InfluxDB)
│       ├── batch/                      # Batch job execution
│       ├── dashboard/                  # Dashboard statistics
│       ├── document/                   # File/document management
│       ├── email/                      # Email sending + SMTP config
│       ├── i18n/                       # Translations
│       ├── payment/                    # Payments + receipts
│       ├── purchaseorder/              # Purchase orders
│       ├── quotation/                  # Quotations
│       ├── report/                     # PDF reports
│       ├── wos/                        # Web Order System
│       ├── health/                     # Health checks
│       └── example/                    # Reference/example module
├── migrations/
│   ├── env.py
│   └── versions/                       # Alembic migration files
├── test/
│   ├── core/
│   └── modules/
│       ├── authentication/             # domain, application tests
│       ├── user/                       # domain, application tests
│       ├── iot/                        # domain, application tests
│       ├── health/                     # domain tests
│       └── shared/                     # domain, application tests
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── Makefile
├── requirements.txt
├── seed_admin.py
└── reset_db.py
```

---

## Base Model

All PostgreSQL tables inherit from `BaseModel` (`app/modules/shared/infrastructure/models.py`), which provides:

| Column      | Type             | Default                |
|-------------|------------------|------------------------|
| `id`        | UUID (PK)        | `gen_random_uuid()`    |
| `is_active` | Boolean          | `true`                 |
| `created_at`| DateTime(tz)     | `now()`                |
| `updated_at`| DateTime(tz)     | `now()` + `onupdate`   |

IoT tables (`iot_*`) also inherit from `BaseModel` with the same base columns.

---

## Authentication

Two authentication schemes are supported:

1. **JWT Bearer Token** - Standard OAuth2 password flow returns access + refresh tokens. Tokens are also set as HttpOnly cookies.
2. **API Key** - `X-API-Key` header for service-to-service calls. Maps to the default admin user.

Roles: `admin` | `manager` | `user`

Path-based access control is defined in `Settings.SECURITY_*_ALLOWED_PATHS`.

---

## Quick Start

```bash
# Start dependencies (PostgreSQL + Redis + InfluxDB + Mosquitto)
make dependencies-up-silent

# Run migrations
alembic upgrade head

# Seed admin user
python seed_admin.py

# Start the API
uvicorn app.app:app --reload --port 8000

# Or use Docker
make start
```
