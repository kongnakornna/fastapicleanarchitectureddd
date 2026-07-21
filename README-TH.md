# FastAPI Clean Architecture + Domain-Driven Design Template

FastAPI backend template สำหรับสร้าง application ขนาดใหญ่ที่มีความเป็นโมดูลาร์และ scale ได้ ใช้หลักการ **Clean Architecture** และ **Domain-Driven Design (DDD)** แยกชั้น domain, application, infrastructure, presentation ออกจากกันอย่างชัดเจน

---

## เนื้อหา

- [ภาพรวมสถาปัตยกรรม](#ภาพรวมสถาปัตยกรรม)
- [โครงสร้างไฟล์และโฟลเดอร์](#โครงสร้างไฟล์และโฟลเดอร์)
- [Modules ของโปรเจค](#modules-ของโปรเจค)
- [ระบบ Authentication](#ระบบ-authentication)
- [Middleware](#middleware)
- [คู่มือการ Implement และ Best Practices](#คู่มือการ-implement-และ-best-practices)
- [Dependencies ของโปรเจค](#dependencies-ของโปรเจค)
- [การตั้งค่า Environment และการรันแอปพลิเคชัน](#การตั้งค่า-environment-และการรันแอปพลิเคชัน)
- [Database Migrations](#database-migrations)
- [สรุป](#สรุป)

---

## ภาพรวมสถาปัตยกรรม

สถาปัตยกรรมของโปรเจคนี้ออกแบบมาเพื่อแยกความรับผิดชอบของแต่ละส่วนออกจากกันอย่างชัดเจน โดยใช้หลักการ **Clean Architecture** ซึ่งหมายความว่า **กฎธุรกิจและ Domain Logic** จะถูกแยกออกจาก infrastructure หรือ interface ภายนอก

### ชั้นหลัก (Layers)

| ชั้น | คำอธิบาย |
|------|----------|
| **Domain** | มี entity, กฎธุรกิจล้วน, value object, domain service. ชั้นนี้เป็นแกนกลางของแอปพลิเคชัน ไม่ขึ้นกับ framework ภายนอก |
| **Application** | Implement **use cases** จัดการ workflow ของ Domain, กำหนด interface (ports) ที่ Domain/Application ต้องการ |
| **Infrastructure** | Implement concrete สำหรับ interface ที่กำหนดไว้ เช่น DB access, external API, ORM models |
| **Presentation** | FastAPI routers, schemas (Pydantic), dependencies. รับ request HTTP, validate, เรียก use case, และ return response |

### ข้อดีของการแยกชั้น

- **Maintainability:** แก้กฎธุรกิจไม่กระทบ infrastructure และกลับกัน
- **Testability:** ทดสอบ business logic ได้โดยแยกจาก infrastructure
- **Flexibility:** เปลี่ยน DB หรือ AI provider ได้โดยไม่ต้อง refactor business logic
- **Feature-Based Organization:** `app/modules` จัดกลุ่มโค้ดตาม business context

---

## โครงสร้างไฟล์และโฟลเดอร์

```text
fastapiddd/
├── .env                          # Environment variables ที่เป็นความลับ (ไม่ commit)
├── .env.example                  # ตัวอย่างไฟล์ .env สำหรับ reference
├── .gitignore                    # ไฟล์ที่ไม่ต้อง commit
├── .python-version               # กำหนดเวอร์ชัน Python (>=3.13)
├── alembic.ini                   # ตั้งค่า Alembic migration
├── Dockerfile                    # Build Docker image (Python 3.14-slim)
├── docker-compose.yaml           # Services: API, PostgreSQL, pgAdmin
├── Makefile                      # คำสั่งลัดสำหรับ Docker commands
├── pyproject.toml                # Metadata, dependencies, Python version
├── uv.lock                       # Lock file สำหรับ uv (ห้ามแก้ไขเอง)
├── reset_db.py                   # Script สำหรับ reset database
├── seed_admin.py                 # Script สำหรับ seed admin user
├── setup.bat                     # Setup script สำหรับ Windows
├── setup.ps1                     # Setup script สำหรับ PowerShell
├── openapi.json                  # OpenAPI schema snapshot
├── app/
│   ├── __init__.py
│   ├── app.py                    # FastAPI entry point
│   ├── core/                     # การตั้งค่าหลักของแอปพลิเคชัน
│   └── modules/                  # Feature modules ตาม Clean Architecture
├── migrations/                   # Alembic database migrations
├── secrets/keys/                 # RSA keys (auto-generated, ไม่ commit)
├── logs/                         # Daily log files
├── scripts/                      # Helper scripts
├── test/                         # Unit tests (pytest)
└── docs/                         # เอกสารประกอบ
```

---

## Modules ของโปรเจค

---

### 1. Core - การตั้งค่าหลัก (`app/core/`)

```text
app/core/
├── __init__.py                   # (empty - package marker)
├── database.py                   # DB connection (SQLAlchemy async + sync)
├── exception_handler.py          # Centralized exception handling
├── key_management.py             # RSA key auto-generation
├── logging.py                    # Loguru config (daily log files)
├── middleware.py                  # CORS, Rate Limit, Request Logging, Response Formatting
├── migrations.py                 # Auto-run Alembic on startup
├── redis.py                      # Redis client + token blacklist
├── resources.py                  # Lifespan context manager
├── security.py                   # JWT (JWS+JWE), password hashing, auth dependencies
└── settings.py                   # pydantic-settings config schema
```

| ไฟล์ | คำอธิบาย |
|------|----------|
| `database.py` | สร้าง SQLAlchemy engines ทั้ง async (`asyncpg` สำหรับ app) และ sync (`psycopg2` สำหรับ migration) พร้อม session factories และ lifecycle functions (`init_database_client`, `close_database_client`) |
| `exception_handler.py` | ลงทะเบียน global exception handlers สำหรับ FastAPI: `RequestValidationError` (422), `HTTPException` (400/401/403/404/429/500), `Exception` (500 catch-all) ทั้งหมด return ในรูปแบบ `StandardResponse` |
| `key_management.py` | Auto-generate RSA 4096-bit key pairs ใน `secrets/keys/` ตอน startup สำหรับ JWT signing (`signing_key.pem`) และ encryption (`encryption_key.pem`) ถ้ายังไม่มี |
| `logging.py` | ตั้งค่า Loguru: custom JSON serializer, colored console output ใน debug mode, daily rotating files ที่ `logs/app_YYYY-MM-DD.log` (retention 30 วัน, zip compression) |
| `middleware.py` | 4 middleware classes: `RateLimitMiddleware` (in-memory sliding window), `DeviceIdMiddleware` (สร้าง device_id cookie), `log_request_middleware` (log ทุก request พร้อม request ID), `ResponseFormattingMiddleware` (ครอบ response ใน `StandardResponse` envelope) |
| `migrations.py` | ตรวจสอบ `alembic_version` table ตอน startup; ถ้ายังไม่มีจะ init ทั้งหมด ถ้ามีแล้วจะ upgrade ถ้ามี pending migrations |
| `redis.py` | Async Redis client singleton + functions: `add_to_blacklist()`, `is_blacklisted()`, `remove_from_blacklist()` สำหรับ JWT token blacklisting. Gracefully degrade ถ้า Redis ไม่available |
| `resources.py` | Lifespan context manager: startup (init loguru, DB, RSA keys, migrations, Redis) + shutdown (close DB, close Redis) |
| `security.py` | **ไฟล์หลักของระบบ auth (~1061 บรรทัด)**: สร้าง/validate JWT (JWS RS256 + JWE RSA-OAEP-256/A256GCM), hash password ด้วย Argon2 (via pwdlib), HMAC token fingerprinting, ตรวจสอบ Redis blacklist. กำหนด FastAPI dependencies: `authenticate_admin`, `authenticate_user`, `authenticate_user_or_api_key`, `authenticate_refresh`, `authenticate_logout`, `no_authentication`, `api_key_authentication` |
| `settings.py` | Pydantic `BaseSettings` class อ่านจาก `.env`: application metadata, auth config, cookie settings, PostgreSQL URLs, Redis config, JWT key paths, security parameters, CORS, rate limiting, logging |

---

### 2. Shared Module (`app/modules/shared/`)

พื้นฐานร่วมของทุก module - ไม่มี database ของตัวเอง

```text
app/modules/shared/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # DomainError base exception class
│   ├── mappers.py                # (empty - ไม่ใช้)
│   ├── services.py               # (empty - ไม่ใช้)
│   └── value_objects.py          # (empty - ไม่ใช้)
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # ApplicationEnvironment, ResponseMessages, Role
│   ├── interfaces.py             # (empty - ไม่ใช้)
│   ├── use_cases.py              # SharedUseCases (cross-module user lookups)
│   └── utils.py                  # current_timestamp(), BRASILIA_TZ
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # SQLAlchemy Base + BaseModel (abstract)
│   └── repositories.py           # (empty - ไม่ใช้)
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # DI: get_shared_use_cases, get_user_repository, get_authentication_repository
    ├── docs.py                   # (empty - ไม่ใช้)
    ├── exceptions.py             # StandardException, DomainException, CoreException
    ├── routers.py                # (empty - ไม่มี endpoint ของตัวเอง)
    └── schemas.py                # StandardResponse, StandardDetailsResponse
```

| ชั้น | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `DomainError` exception class ฐานสำหรับ domain errors ทั้งหมด |
| **Application** | `enums.py` | `ApplicationEnvironment` (dev/homolog/production), `ResponseMessages` (ข้อความ response 标准ทั้งหมด เช่น Success, Created, Bad Request), `Role` (ADMIN/MANAGER/USER) |
| **Application** | `use_cases.py` | `SharedUseCases` - lookup user ข้าม module: `get_user_by_id`, `get_user_by_email`, `get_user_by_username` (ใช้โดย authentication และ user modules) |
| **Application** | `utils.py` | `current_timestamp()` return UTC ISO string, `BRASILIA_TZ` timezone constant (`America/Sao_Paulo`) |
| **Infrastructure** | `models.py` | `BaseModel` abstract class ที่ทุก table model ต้อง inherit: มี `id` (UUID PK), `is_active` (bool), `created_at` (datetime), `updated_at` (datetime) |
| **Presentation** | `schemas.py` | `StandardResponse` และ `StandardDetailsResponse` - generic Pydantic response envelope ที่ทุก endpoint ใช้ return |
| **Presentation** | `exceptions.py` | Base exception hierarchy: `StandardException` (HTTP errors), `DomainException` (validation errors), `CoreException` (internal errors) |
| **Presentation** | `dependencies.py` | DI provider functions: `get_shared_use_cases`, `get_user_repository`, `get_authentication_repository` สำหรับ inject ผ่าน FastAPI `Depends` |

---

### 3. Authentication Module (`app/modules/authentication/`)

ระบบ login, logout, refresh token พร้อม JWT แบบ nested (JWS + JWE)

```text
app/modules/authentication/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # Session, AccessToken, RefreshToken dataclasses
│   ├── mappers.py                # Bidirectional mapping ระหว่าง entities กับ DB models/responses
│   ├── services.py               # (empty - logic อยู่ใน use_cases)
│   └── value_objects.py          # Claims, RefreshClaims - JWT claims schema
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # TokenType enum (Bearer)
│   ├── interfaces.py             # IAuthenticationRepository protocol
│   ├── use_cases.py              # AuthenticationUseCases: login, refresh, logout
│   └── utils.py                  # (empty)
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # SessionModel, AccessTokenModel, RefreshTokenModel ORM
│   └── repositories.py           # PostgresSessionRepository: full CRUD with eager loading
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # DI: get_authentication_use_cases, get_user_use_cases_for_auth
    ├── docs.py                   # Swagger/OpenAPI docs สำหรับ auth endpoints (~469 บรรทัด)
    ├── exceptions.py             # 15+ exception classes (token expired, malformed, etc.)
    ├── routers.py                # POST login, refresh, logout, register; GET me
    └── schemas.py                # LoginResponse, RefreshResponse, LogoutResponse, RegisterResponse
```

| ชั้น | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | Dataclasses สำหรับ session management: `Session` (track IP, user agent, device, location, tokens), `AccessToken` (expiry, hash, blacklisted flag), `RefreshToken` (expiry, hash, grant_id) |
| **Domain** | `value_objects.py` | JWT claims: `Claims` (iss, sub, aud, iat, nbf, exp, jti, grant_id, scope) และ `RefreshClaims` พร้อม validation logic ทั้งหมด |
| **Domain** | `mappers.py` | Bidirectional mapping ~304 บรรทัด: `login_entity_mapper`, `logout_entity_mapper`, `refresh_entity_mapper`, `access_token_entity_mapper`, `refresh_token_entity_mapper`, `model_entity_mapper` |
| **Application** | `enums.py` | `TokenType` enum: Bearer |
| **Application** | `interfaces.py` | `IAuthenticationRepository` protocol: `create`, `get_by_user_id_agent_and_device`, `get_access/refresh_token_by_session`, `update`, `delete` |
| **Application** | `use_cases.py` | `AuthenticationUseCases` (~188 บรรทัด): `login()` ตรวจสอบ password + สร้าง session/tokens, `refresh()` validate refresh token + สร้างคู่ใหม่, `logout()` blacklist tokens + ลบ session |
| **Infrastructure** | `models.py` | ORM models (~355 บรรทัด): `SessionModel` (app_sessions), `AccessTokenModel` (app_access_tokens), `RefreshTokenModel` (app_refresh_tokens) พร้อม columns, relationships, constraints, indexes |
| **Infrastructure** | `repositories.py` | `PostgresSessionRepository` (~276 บรรทัด): full CRUD implementation พร้อม eager loading ของ nested relationships |
| **Presentation** | `routers.py` | Endpoints (~243 บรรทัด): `POST /api/v1/authentication/login/`, `POST /api/v1/authentication/register/`, `GET /api/v1/authentication/me/`, `PATCH /api/v1/authentication/refresh/`, `DELETE /api/v1/authentication/logout/` |
| **Presentation** | `schemas.py` | Response DTOs: `LoginResponse` (access + refresh tokens), `RefreshResponse`, `LogoutResponse`, `RegisterResponse` |
| **Presentation** | `exceptions.py` | 15+ exception classes (~318 บรรทัด): `TokenExpiredException`, `TokenNotYetValidException`, `TokenMalformedException`, `TokenModifiedException`, `TokenBlacklistedException`, `CookiesNotProvidedException`, `InvalidCredentialsException`, ฯลฯ |
| **Presentation** | `docs.py` | OpenAPI documentation (~469 บรรทัด): error responses, examples, descriptions สำหรับทุก auth endpoint |
| **Presentation** | `dependencies.py` | DI providers: `get_authentication_use_cases`, `get_user_use_cases_for_auth` |

---

### 4. User Module (`app/modules/user/`)

จัดการข้อมูลผู้ใช้และ RBAC permissions

```text
app/modules/user/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # User dataclass
│   ├── mappers.py                # Bidirectional mapping ระหว่าง entities กับ DB models/responses
│   ├── permission_entities.py    # Permission, Role_, UserRole, RolePermission dataclasses
│   ├── permission_mappers.py     # Model <-> entity mappers สำหรับ permission entities
│   ├── services.py               # (empty - logic อยู่ใน use_cases)
│   └── value_objects.py          # Name, Email, Phone value objects (validation)
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # Gender, UserStatus enums
│   ├── interfaces.py             # IUserRepository protocol
│   ├── use_cases.py              # UserUseCases: create user
│   └── utils.py                  # (empty)
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # UserModel ORM (app_users table)
│   ├── permission_models.py      # RoleModel, PermissionModel, UserRoleModel, RolePermissionModel ORM
│   └── repositories.py           # PostgresUserRepository: full CRUD implementation
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # DI: get_user_repository, get_user_use_cases
    ├── docs.py                   # Swagger/OpenAPI docs สำหรับ user endpoints (~299 บรรทัด)
    ├── exceptions.py             # UserException, email/username already exists/not found, cookie errors
    ├── routers.py                # POST / (create user), GET /me
    └── schemas.py                # CreateRequest, CreateResponse, MeResponse (~397 บรรทัด)
```

| ชั้น | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `User` dataclass (~51 บรรทัด): name, username, gender, birthdate, email, phone, password, role, status. Auto-normalize strings เป็น value objects, validate age >= 18 |
| **Domain** | `value_objects.py` | `Name` (validate first/last name length, characters, strip/capitalize), `Email` (validate format + domain whitelist), `Phone` (validate international format) |
| **Domain** | `mappers.py` | `create_entity_mapper`, `register_entity_mapper`, `me_entity_mapper`, `model_entity_mapper` (~111 บรรทัด) |
| **Domain** | `permission_entities.py` | RBAC entities: `Permission` (resource:action เช่น user:create), `Role_` (name + description), `UserRole` (user_id + role_id), `RolePermission` (role_id + permission_id) |
| **Domain** | `permission_mappers.py` | Bidirectional model <-> entity mappers สำหรับ permission entities |
| **Application** | `enums.py` | `Gender` (male/female/non_binary/other), `UserStatus` (active/inactive/suspended) |
| **Application** | `interfaces.py` | `IUserRepository` protocol: `create`, `exists_by_email`, `exists_by_username`, `get_by_id`, `get_by_username` |
| **Application** | `use_cases.py` | `UserUseCases` (~84 บรรทัด): `create()` พร้อม email/username uniqueness checks + hash password |
| **Infrastructure** | `models.py` | `UserModel` ORM (~109 บรรทัด): map กับ `app_users` table, columns ครบ + constraints |
| **Infrastructure** | `permission_models.py` | ORM models (~101 บรรทัด): `RoleModel`, `PermissionModel`, `UserRoleModel`, `RolePermissionModel` |
| **Infrastructure** | `repositories.py` | `PostgresUserRepository` (~186 บรรทัด): full CRUD พร้อม existence checks |
| **Presentation** | `routers.py` | Endpoints: `POST /api/v1/user/` (create, ต้อง auth), `GET /api/v1/user/me/` (API key หรือ JWT) |
| **Presentation** | `schemas.py` | Request/Response DTOs (~397 บรรทัด): `CreateRequest` ( validations ครบ), `CreateResponse`, `MeResponse` |
| **Presentation** | `exceptions.py` | `UserException`, `UserEmailAlreadyExistsException`, `UserEmailNotFoundException`, `UsernameAlreadyExistsException`, `CookieManagementException` |
| **Presentation** | `docs.py` | OpenAPI docs (~299 บรรทัด) สำหรับ user endpoints |
| **Presentation** | `dependencies.py` | DI providers: `get_user_repository`, `get_user_use_cases` |

---

### 5. Health Module (`app/modules/health/`)

ตรวจสอบสถานะแอปพลิเคชัน

```text
app/modules/health/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # Health dataclass (alembic_version, user, status)
│   ├── mappers.py                # health_mapper, alembic_entity_mapper, model_entity_mapper
│   ├── services.py               # (empty)
│   └── value_objects.py          # (empty)
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # HealthType enum (OK, ERROR)
│   ├── interfaces.py             # IHealthRepository protocol
│   ├── use_cases.py              # HealthUseCases: health check + alembic version
│   └── utils.py                  # (empty)
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # AlembicModel (อ่าน alembic_version table)
│   └── repositories.py           # PostgresHealthRepository: get_alembic_version
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # DI: get_health_repository, get_health_use_cases
    ├── docs.py                   # Swagger/OpenAPI docs สำหรับ health endpoints
    ├── exceptions.py             # HealthException, MigrationNotInitiatedException
    ├── routers.py                # GET /health, GET /health/redirect, GET /health/alembic-version
    └── schemas.py                # HealthResponse, AlembicVersionResponse, AlembicHealthResponse
```

| ชั้น | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `Health` dataclass: `alembic_version`, `user`, `status` property (return OK เสมอ) |
| **Domain** | `mappers.py` | Maps ระหว่าง Health entity <-> AlembicModel, HealthResponse, AlembicVersionResponse |
| **Application** | `enums.py` | `HealthType` enum: OK, ERROR |
| **Application** | `interfaces.py` | `IHealthRepository` protocol: `get_alembic_version()` |
| **Application** | `use_cases.py` | `HealthUseCases`: `health()` static method return OK, `alembic_version()` query migration version จาก repository |
| **Infrastructure** | `models.py` | `AlembicModel`: SQLAlchemy model map กับ `alembic_version` table |
| **Infrastructure** | `repositories.py` | `PostgresHealthRepository`: query `alembic_version` table |
| **Presentation** | `routers.py` | `GET /health` (public), `GET /health/redirect` (redirect), `GET /api/v1/alembic-version/` (admin only) |
| **Presentation** | `schemas.py` | `HealthResponse`, `AlembicVersionResponse`, `AlembicHealthResponse` |
| **Presentation** | `exceptions.py` | `HealthException`, `MigrationNotInitiatedException` |
| **Presentation** | `docs.py` | OpenAPI docs สำหรับ health endpoints (error responses, examples) |
| **Presentation** | `dependencies.py` | DI providers: `get_health_repository`, `get_health_use_cases` |

---

### 6. Example Module (`app/modules/example/`)

ตัวอย่าง module สำหรับ reference - ไม่มี database

```text
app/modules/example/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # Example dataclass (full_name, message property)
│   ├── mappers.py                # example_entity_mapper: request <-> entity <-> response
│   ├── services.py               # (empty)
│   └── value_objects.py          # FullName value object (validate non-empty first/last name)
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # (empty)
│   ├── interfaces.py             # (empty)
│   ├── use_cases.py              # ExampleUseCases.hello: passthrough use case
│   └── utils.py                  # (empty)
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # (empty - ไม่ใช้ DB)
│   └── repositories.py           # (empty - ไม่ใช้ DB)
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # DI: get_example_use_cases
    ├── docs.py                   # Swagger/OpenAPI docs สำหรับ example endpoints
    ├── exceptions.py             # ExampleException
    ├── routers.py                # POST /api/v1/example/ (public, ไม่ต้อง auth)
    └── schemas.py                # ExampleRequest, ExampleResponse
```

| ชั้น | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `Example` dataclass: `full_name` (FullName VO), `message` property return "Hello, {name}!". Reject "John Doe" |
| **Domain** | `value_objects.py` | `FullName` value object: validate non-empty first/last name, capitalize, strip whitespace |
| **Domain** | `mappers.py` | `example_entity_mapper`: map ระหว่าง ExampleRequest <-> Example entity <-> ExampleResponse |
| **Application** | `use_cases.py` | `ExampleUseCases.hello()`: simple passthrough use case |
| **Infrastructure** | - | ทั้ง directory ว่าง (ไม่ต้องใช้ DB สำหรับ example) |
| **Presentation** | `routers.py` | `POST /api/v1/example/`: hello endpoint, ไม่ต้อง auth |
| **Presentation** | `schemas.py` | `ExampleRequest` (first_name, last_name พร้อม validators), `ExampleResponse` (message) |
| **Presentation** | `exceptions.py` | `ExampleException` |
| **Presentation** | `docs.py` | OpenAPI docs สำหรับ example endpoints |
| **Presentation** | `dependencies.py` | DI provider: `get_example_use_cases` |

---

### 7. Blank Module (`app/modules/blank/`)

Template/boilerplate สำหรับสร้าง module ใหม่ - ทั้งหมดว่าง

```text
app/modules/blank/
├── __init__.py                   # (empty)
├── domain/
│   ├── __init__.py               # (empty)
│   ├── entities.py               # (empty - template stub)
│   ├── mappers.py                # (empty - template stub)
│   ├── services.py               # (empty - template stub)
│   └── value_objects.py          # (empty - template stub)
├── application/
│   ├── __init__.py               # (empty)
│   ├── enums.py                  # (empty - template stub)
│   ├── interfaces.py             # (empty - template stub)
│   ├── use_cases.py              # (empty - template stub)
│   └── utils.py                  # (empty - template stub)
├── infrastructure/
│   ├── __init__.py               # (empty)
│   ├── models.py                 # (empty - template stub)
│   └── repositories.py           # (empty - template stub)
└── presentation/
    ├── __init__.py               # (empty)
    ├── dependencies.py           # (empty - template stub)
    ├── docs.py                   # (empty - template stub)
    ├── exceptions.py             # (empty - template stub)
    ├── routers.py                # (empty - template stub)
    └── schemas.py                # (empty - template stub)
```

> **วิธีใช้:** copy ทั้งโฟลเดอร์ `blank/` แล้ว rename เป็นชื่อ module ใหม่ จากนั้นเริ่มเขียนโค้ดในแต่ละไฟล์ตาม pattern ของ module อื่นๆ

---

## Migrations (`migrations/`)

```text
migrations/
├── README.md                                     # Alembic command reference
├── env.py                                        # Alembic environment config
├── script.py.mako                                # Template สำหรับ migration files
├── public.sql                                    # DB schema dump (base)
├── public_feature_user.sql                       # DB schema dump (with RBAC)
└── versions/
    ├── 2026_03_16_0048_f7ea2294d326.py           # initial_schemas
    ├── 2026_03_16_0049_0a4bcd898bd2.py           # insert_admin_user
    ├── 2026_07_20_1424_e8990ecbe9c7.py           # add_username_and_status
    ├── 2026_07_20_1457_25845428d7a7.py           # add_permission_tables
    └── 2026_07_20_2256_a9a05a7f432d.py           # make origin and referrer nullable
```

| ไฟล์ | คำอธิบาย |
|------|----------|
| `env.py` | ตั้งค่า Alembic: import all SQLAlchemy models, config online/offline migration runners |
| `script.py.mako` | Mako template สำหรับ auto-generate migration files ใหม่ |
| `public.sql` | Full PostgreSQL schema dump ของ base schema (enums, tables, indexes, constraints) |
| `public_feature_user.sql` | Full schema dump พร้อม RBAC tables และ seed data |
| `versions/...initial_schemas` | สร้าง tables แรกเริ่ม: `app_users`, `app_sessions`, `app_access_tokens`, `app_refresh_tokens`, enums |
| `versions/...insert_admin_user` | Seed admin user จาก `.env` settings |
| `versions/...add_username_and_status` | เพิ่ม `username` และ `status` columns ใน `app_users` |
| `versions/...add_permission_tables` | สร้าง RBAC tables: `app_permissions`, `app_roles`, `app_role_permissions`, `app_user_roles` พร้อม seed data |
| `versions/...make_origin_referrer_nullable` | ทำให้ `origin` และ `referrer` columns nullable ใน `app_sessions` |

---

## Test Structure (`test/`)

```text
test/
├── __init__.py                                   # (empty)
├── core/
│   └── __init__.py                               # (empty - ยังไม่มี core tests)
└── modules/
    ├── __init__.py                               # (empty)
    ├── shared/
    │   ├── domain/
    │   │   └── test_entities.py                  # Tests DomainError
    │   └── application/
    │       ├── test_enums.py                     # Tests enums (ApplicationEnvironment, Role, ResponseMessages)
    │       ├── test_utils.py                     # Tests current_timestamp(), BRASILIA_TZ
    │       └── test_use_cases.py                 # Tests SharedUseCases (mock user lookups)
    ├── authentication/
    │   ├── domain/
    │   │   ├── test_entities.py                  # Tests Session, AccessToken, RefreshToken
    │   │   ├── test_value_objects.py             # Tests Claims, RefreshClaims validation
    │   │   └── test_mappers.py                   # Tests auth mappers (bidirectional)
    │   └── application/
    │       └── test_use_cases.py                 # Tests AuthenticationUseCases (login, refresh, logout)
    ├── user/
    │   ├── domain/
    │   │   ├── test_entities.py                  # Tests User construction/validation
    │   │   ├── test_value_objects.py             # Tests Name, Email, Phone validation
    │   │   └── test_permission_entities.py       # Tests Permission, Role_, UserRole, RolePermission
    │   └── application/
    │       └── test_use_cases.py                 # Tests UserUseCases (create, duplicates)
    ├── health/
    │   ├── domain/
    │   │   ├── test_entities.py                  # Tests Health entity
    │   │   └── test_mappers.py                   # Tests health/alembic mappers
    │   └── application/
    │       └── test_use_cases.py                 # Tests HealthUseCases
    ├── example/
    │   ├── domain/
    │   │   ├── test_entities.py                  # Tests Example entity
    │   │   ├── test_value_objects.py             # Tests FullName value object
    │   │   └── test_mappers.py                   # Tests example mappers
    │   └── application/
    │       └── test_use_cases.py                 # Tests ExampleUseCases
    └── blank/
        └── __init__.py                           # (empty - template)
```

> **หมายเหตุ:** โครงสร้าง test จำลองโครงสร้าง `app/modules/` เป๊ะ - domain tests ทดสอบ entities, value objects, mappers; application tests ทดสอบ use cases ด้วย mocks

---

## Scripts (`scripts/`)

```text
scripts/
├── __init__.py                                   # (empty)
├── directory_tree.py                             # สร้างไฟล์ directory tree text
├── generate_fernet.py                            # สร้าง Fernet encryption key
└── generate_secret.py                            # สร้าง secret hex token
```

| ไฟล์ | คำอธิบาย |
|------|----------|
| `directory_tree.py` | Walk project directory (skip .venv, .git, .idea, .ruff_cache) แล้วเขียน tree structure ลง `directory_tree.txt` |
| `generate_fernet.py` | Generate และ print Fernet key (ใช้สำหรับ JWT encryption หรืออื่นๆ) |
| `generate_secret.py` | Generate hex token 64 ตัวอักษรผ่าน `secrets.token_hex(32)` (ใช้สำหรับ SECURITY_SECRET_KEY) |

---

## ระบบ Authentication

### JWT (JSON Web Token) - Nested Security

ใช้ระบบ JWT แบบ nested สองชั้นเพื่อความปลอดภัยสูงสุด:

1. **Signing (JWS):** RS256 ด้วย RSA 4096-bit private key
2. **Encryption (JWE):** RSA-OAEP-256 + A256GCM ด้วย key pair แยกต่างหาก

```
JWT Token = Encrypt(Sign(claims))
```

### Flow การทำงาน

**Login (`POST /api/v1/authentication/login/`)**
1. รับ OAuth2 form data (username + password)
2. ค้นหา user จาก username
3. ตรวจสอบ password ด้วย Argon2
4. ตรวจสอบ session ที่มีอยู่ (user + agent + device)
5. สร้าง/หมุนเวียน tokens (access + refresh)
6. Set HttpOnly cookies + ส่ง tokens ใน response body
7. Hash JTIs ด้วย HMAC-SHA256 ก่อนเก็บใน DB

**Refresh (`PATCH /api/v1/authentication/refresh/`)**
1. อ่าน refresh token จาก cookie
2. Decode nested refresh token (decrypt + verify)
3. ตรวจสอบ Redis blacklist
4. หมุนเวียน tokens ใหม่

**Logout (`DELETE /api/v1/authentication/logout/`)**
1. อ่าน access token จาก cookie
2. Blacklist JTIs ใน Redis
3. Revoke tokens ใน DB

### API Key Authentication

ใช้ header `X-API-Key` สำหรับ authentication แบบ API key:

```
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/user/me/
```

- API key auth จะใช้ default admin user (`AUTH_API_KEY_DEFAULT_ADMIN_EMAIL`)
- สามารถใช้ร่วมกับ JWT auth ได้ (fallback)

### Role-Based Access Control (RBAC)

ระบบ RBAC แบบ path-based:

| Level | Description |
|-------|-------------|
| **NO_AUTH** | ไม่ต้อง auth (health, login, register, example) |
| **USER** | ต้อง login (user/me, user/create) |
| **MANAGER** | ต้องเป็น manager ขึ้นไป |
| **ADMIN** | ต้องเป็น admin (alembic-version) |

### Response Format

ทุก endpoint return ในรูปแบบ `StandardResponse`:

```json
{
  "code": 200,
  "method": "GET",
  "path": "/api/v1/user/me/",
  "timestamp": "2026-07-20T16:00:00.000000Z",
  "details": {
    "message": "Success",
    "data": { ... }
  }
}
```

---

## Middleware

### 1. RateLimitMiddleware

Rate limiting แบบ in-memory sliding window แยกตาม endpoint:

| Path | Limit | Window |
|------|-------|--------|
| `/api/v1/authentication/login/` | 5 requests | 60 วินาที |
| `/api/v1/authentication/register/` | 5 requests | 60 วินาที |
| `/health` | ไม่ limit | - |
| Endpoint อื่นๆ | 60 requests | 60 วินาที |

ตั้งค่าใน `.env`:
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT_REQUESTS=60
RATE_LIMIT_DEFAULT_WINDOW_SECONDS=60
RATE_LIMIT_AUTH_REQUESTS=5
RATE_LIMIT_AUTH_WINDOW_SECONDS=60
```

เมื่อเกิน limit จะ return `429 Too Many Requests`:
```json
{
  "code": 429,
  "method": "POST",
  "path": "/api/v1/authentication/login/",
  "timestamp": "2026-07-20T16:00:00.000000Z",
  "details": {
    "message": "Too many requests",
    "data": {
      "retry_after_seconds": 60,
      "limit": 5
    }
  }
}
```

### 2. DeviceIdMiddleware

สร้าง `device_id` cookie อัตโนมัติจาก user-agent + IP hash ใช้สำหรับ session tracking

### 3. Request Logging Middleware

บันทึก request/response ทุกครั้งด้วย loguru:
- Request ID (สั้น 8 ตัวอักษร)
- Method, path, status code
- เวลาที่ใช้ (elapsed time)
- Skip `/health` endpoint

### 4. ResponseFormattingMiddleware

ครอบทุก response ใน `StandardResponse` envelope อัตโนมัติ

### 5. CORSMiddleware

ตั้งค่า CORS จาก settings:
```env
SECURITY_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:5173"]
SECURITY_ALLOW_HEADERS=["*"]
SECURITY_ALLOW_METHODS=["*"]
```

---

## คู่มือการ Implement และ Best Practices

### การแยกความรับผิดชอบ

- **ห้าม mix ชั้น:** กฎธุรกิจ → domain/application, data access → infrastructure, request/response → presentation
- **Domain ต้องบริสุทธิ์:** ห้าม import SQLAlchemy, FastAPI, requests/httpx
- **Application เป็นตัวประสาน:** เรียก domain service, repository ตาม interface
- **Presentation ต้องบาง:** โค้ดใน `routers.py` ต้องน้อย กระจายงานให้ use case

### ตั้งชื่อไฟล์และโค้ด

| ประเภท | Convention | ตัวอย่าง |
|--------|------------|----------|
| โฟลเดอร์/ไฟล์ | snake_case ตัวเล็ก | `value_objects.py`, `my_module/` |
| Class/Interface | PascalCase | `User`, `OrderRepository` |
| Function/Method | snake_case | `calculate_total()`, `get_by_id()` |
| Variable | snake_case | `item_count` |
| Pydantic Schema | PascalCase + suffix | `UserCreate`, `UserOut` |
| Use Case | PascalCase + `UseCase` | `FooUseCase` |
| Test file | prefix `test_` | `test_entities.py` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES = 5` |

### Dependency Inversion และ Injection

- กำหนด interface ใน domain/application layer
- Implement ใน infrastructure layer
- ใช้ FastAPI `Depends` สำหรับ injection
- Domain ห้าม import จาก infrastructure

### คุณภาพโค้ด

- ทำตาม **PEP8**
- ใช้ **Ruff** สำหรับ linting
- เขียน **type hints** ทุกที่
- เขียน **docstring** สำหรับ public class/function
- ทำตาม **DRY** principle
- มี **error handling** ที่ชัดเจน
- เขียน **log** ที่จุดสำคัญ

### การทดสอบ

- ใช้ **pytest** สำหรับทดสอบ
- มีทั้ง **unit test** และ **integration test**
- ใช้ **fixtures** สำหรับ setup
- รัน tests สม่ำเสมอ: `uv run -- pytest`

---

## Dependencies ของโปรเจค

### Runtime Dependencies

| แพ็กเกจ | คำอธิบาย |
|---------|----------|
| FastAPI | Web framework สำหรับสร้าง API |
| Alembic | Database migration tool |
| SQLAlchemy | ORM สำหรับ database |
| AsyncPG | PostgreSQL driver สำหรับ async |
| Psycopg | PostgreSQL adapter (sync + binary) |
| Pydantic | Data validation |
| Pydantic Settings | จัดการ environment variables |
| Email Validator | ตรวจสอบ email format |
| Cryptography | สำหรับเข้ารหัส RSA keys |
| JWCrypto | JWT implementation (JWS + JWE) |
| Argon2-CFFI | Password hashing |
| PWDLib | Password hashing wrapper (Argon2) |
| Redis | Redis async client + token blacklist |
| Loguru | จัดการ logging |
| Stackprinter | Stack trace formatting |
| Orjson | JSON library ที่เร็ว |
| Hypercorn | ASGI server |
| Py-Automapper | Object mapping |
| HTTPX | HTTP client สำหรับ testing |
| Sentry SDK | Error monitoring |
| Python-Multipart | Form data parsing |
| Watchfiles | File watching สำหรับ reload |

### Dev Dependencies

| แพ็กเกจ | คำอธิบาย |
|---------|----------|
| Ruff | Linter และ code formatter |

---

## การตั้งค่า Environment และการรันแอปพลิเคชัน

### 1. ติดตั้ง uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

ดูรายละเอียดที่ https://docs.astral.sh/uv/getting-started/installation/

### 2. ตั้งค่า Environment Variables

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env` ตามต้องการ ดูรายละเอียดที่ `.env.example`

### 3. ติดตั้ง Dependencies

```bash
uv sync
```

### 4. รันแอปพลิเคชัน

```bash
# รันด้วย uvicorn
uv run -- uvicorn app.app:app --reload

# หรือใช้ FastAPI CLI
uv run -- python -m fastapi app.app:app --reload
```

เปิด browser ไปที่ `http://localhost:8000/docs` เพื่อดู Swagger UI

### 5. ใช้ Docker (ถ้าต้องการ)

```bash
docker-compose up --build
```

### 6. ใช้ Makefile

```bash
make start              # เริ่มแอปพลิเคชันด้วย Docker
make start-silent       # เริ่มแบบ background
make delete             # หยุดและลบ containers
make dependencies-up    # เริ่มแค่ database services
make dependencies-down  # หยุด database services
```

---

## Database Migrations

ใช้ **Alembic** สำหรับจัดการ database schema:

```bash
# สร้าง migration ใหม่
alembic revision --autogenerate -m "คำอธิบายการเปลี่ยนแปลง"

# อัปเดต database
alembic upgrade head

# ย้อนกลับ 1 เวอร์ชัน
alembic downgrade -1
```

> **หมายเหตุ:** App จะ auto-run `alembic upgrade head` ทุกครั้งที่ startup อัตโนมัติ

---

## Logging

ใช้ **Loguru** สำหรับ logging ทั้งหมด:

- **Console output:** JSON format พร้อม colored output
- **File output:** Daily rotating log files ที่ `logs/app_YYYY-MM-DD.log`
  - Rotation: เที่ยงคืน (midnight)
  - Retention: 30 วัน
  - Compression: zip
- **Skip:** `/health` endpoint ไม่ถูก log

---

## สรุป

- สถาปัตยกรรมใช้หลักการ **Clean Architecture** แยกชั้น domain, application, infrastructure, presentation
- แต่ละ feature module มีโครงสร้างย่อยที่สม่ำเสมอ
- ระบบ **JWT Nested Security** (JWS + JWE) พร้อม Redis blacklist
- **API Key Authentication** สำหรับ machine-to-machine
- **Rate Limiting** แยกตาม endpoint (auth: 5 req/min, default: 60 req/min)
- **RBAC** แบบ path-based สำหรับ USER/MANAGER/ADMIN
- **Auto-migration** Alembic ตอน startup
- **Daily log files** พร้อม rotation และ compression
- จัดการ config ผ่าน `core/` อย่างเป็นระบบ
- ใช้ **uv** สำหรับจัดการ dependencies
- มี integration กับ Docker, .env, และโครงสร้าง test พร้อมใช้
- เขียนโค้ดตาม **PEP8**, มี documentation, type hints, และแยกความรับผิดชอบชัดเจน
