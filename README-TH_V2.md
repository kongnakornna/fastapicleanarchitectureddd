# FastAPI Clean Architecture + Domain-Driven Design Template

FastAPI backend template สำหรับสร้าง application ขนาดใหญ่ที่มีความเป็นโมดูลาร์และ scale ได้ ใช้หลักการ **Clean Architecture** และ **Domain-Driven Design (DDD)** แยกชั้น domain, application, infrastructure, presentation ออกจากกันอย่างชัดเจน

---
U: kongnakorn
P: Na@1234@#
T: password


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
├── .env                      # Environment variables (ไม่ commit)
├── .env.example              # ตัวอย่าง environment variables
├── .gitignore
├── .python-version           # เวอร์ชัน Python (>=3.13)
├── alembic.ini               # ตั้งค่า Alembic
├── Dockerfile
├── docker-compose.yaml
├── Makefile
├── README.md
├── README-TH.md
├── pyproject.toml
├── uv.lock
├── app/
│   ├── __init__.py
│   ├── app.py                # Entry point ของ FastAPI
│   ├── core/
│   │   ├── database.py       # DB connection (SQLAlchemy async + sync)
│   │   ├── exception_handler.py  # Centralized exception handling
│   │   ├── key_management.py # RSA key auto-generation
│   │   ├── logging.py        # Loguru config (daily log files)
│   │   ├── middleware.py      # CORS, Rate Limit, Request Logging, Response Formatting
│   │   ├── migrations.py     # Auto-run Alembic on startup
│   │   ├── redis.py          # Redis client + token blacklist
│   │   ├── resources.py      # Lifespan context manager
│   │   ├── security.py       # JWT (JWS+JWE), password hashing, auth dependencies
│   │   ├── settings.py       # pydantic-settings config schema
│   │   └── utils.py
│   └── modules/
│       ├── shared/           # Shared module (response schemas, base models)
│       ├── authentication/   # ระบบ login/logout/refresh
│       ├── user/             # จัดการ user + RBAC permissions
│       ├── health/           # Health check
│       └── example/          # ตัวอย่าง module
├── migrations/               # Alembic migrations
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
├── secrets/keys/             # RSA keys (auto-generated)
├── logs/                     # Daily log files
├── scripts/                  # Helper scripts
├── test/                     # Unit tests (pytest)
│   ├── modules/
│   │   ├── authentication/
│   │   ├── user/
│   │   ├── health/
│   │   ├── example/
│   │   └── shared/
│   └── core/
└── docs/
```

### รายละเอียดแต่ละส่วน

#### รูทโปรเจค

| ไฟล์ | คำอธิบาย |
|------|----------|
| `.env` | เก็บค่า environment variables ที่เป็นความลับ (ไม่ commit) |
| `.env.example` | ตัวอย่างไฟล์ `.env` สำหรับ reference |
| `.python-version` | กำหนดเวอร์ชัน Python (`>=3.13`) |
| `alembic.ini` | ตั้งค่า Alembic migration tool |
| `Dockerfile` | กำหนดวิธี build Docker image (Python 3.14-slim) |
| `docker-compose.yaml` | กำหนด services: API, PostgreSQL, pgAdmin |
| `Makefile` | คำสั่งลัดสำหรับ Docker commands |
| `pyproject.toml` | กำหนด metadata, dependencies, Python version |
| `uv.lock` | Lock file สำหรับ uv (ห้ามแก้ไขเอง) |

#### `app/core/` - การตั้งค่าหลัก

| ไฟล์ | คำอธิบาย |
|------|----------|
| `database.py` | DB connection: async (asyncpg) สำหรับ app, sync (psycopg2) สำหรับ migration |
| `exception_handler.py` | จัดการ exceptions แบบ centralized (422 validation, 401/403/404/429, 500 catch-all) |
| `key_management.py` | Auto-generate RSA 4096-bit key pairs สำหรับ JWT signing + encryption |
| `logging.py` | Loguru config: JSON log, daily rotating files (`logs/app_YYYY-MM-DD.log`), 30-day retention, zip compression |
| `middleware.py` | 4 middleware classes: RateLimit, DeviceId, RequestLogging, ResponseFormatting + CORS |
| `migrations.py` | Auto-run `alembic upgrade head` ตอน startup |
| `redis.py` | Redis async client, token blacklist functions (`add_to_blacklist`, `is_blacklisted`) |
| `resources.py` | Lifespan context manager: startup (init loguru, DB, keys, migrations, Redis) + shutdown |
| `security.py` | Password hashing (Argon2), JWT (JWS RS256 + JWE RSA-OAEP-256/A256GCM), auth dependencies |
| `settings.py` | Config schema ด้วย pydantic-settings อ่านจาก `.env` |

#### `app/modules/` - Feature Modules

แต่ละ module มีโครงสร้างย่อย 4 ชั้น:

- **domain/**: `entities.py`, `value_objects.py`, `services.py`, `mappers.py` - กฎธุรกิจล้วน
- **application/**: `use_cases.py`, `interfaces.py`, `enums.py`, `utils.py` - การจัดการ workflow
- **infrastructure/**: `repositories.py`, `models.py` - Implement DB access (SQLAlchemy)
- **presentation/**: `routers.py`, `schemas.py`, `exceptions.py`, `dependencies.py`, `docs.py` - API endpoints

---

## Modules ของโปรเจค

### Shared Module

พื้นฐานร่วมของทุก module

| ส่วน | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `DomainError` exception class |
| **Application** | `enums.py` | `ResponseMessages`, `Role` (ADMIN/MANAGER/USER), `ApplicationEnvironment` |
| **Application** | `use_cases.py` | `SharedUseCases` - get_user_by_id/username/email |
| **Application** | `utils.py` | `current_timestamp()`, `BRASILIA_TZ` |
| **Infrastructure** | `models.py` | `BaseModel` abstract class (id UUID, is_active, created_at, updated_at) |
| **Presentation** | `schemas.py` | `StandardResponse`, `StandardDetailsResponse` (generic response envelope) |
| **Presentation** | `dependencies.py` | DI functions: `get_shared_use_cases`, `get_user_repository`, `get_authentication_repository` |

### Authentication Module

ระบบ login, logout, refresh token พร้อม JWT แบบ nested (JWS + JWE)

| ส่วน | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `Session`, `RefreshToken`, `AccessToken` dataclasses |
| **Domain** | `value_objects.py` | `Claims`, `RefreshClaims` - JWT claims schema |
| **Domain** | `mappers.py` | Bidirectional mapping ระหว่าง entities กับ DB models |
| **Application** | `use_cases.py` | `AuthenticationUseCases` - login, refresh, logout |
| **Application** | `interfaces.py` | `IAuthenticationRepository` protocol |
| **Infrastructure** | `models.py` | `SessionModel`, `RefreshTokenModel`, `AccessTokenModel` |
| **Infrastructure** | `repositories.py` | `PostgresSessionRepository` - full CRUD with eager loading |
| **Presentation** | `routers.py` | Endpoints: POST login, POST register, GET me, PATCH refresh, DELETE logout |
| **Presentation** | `schemas.py` | `LoginResponse`, `RefreshResponse`, `LogoutResponse`, `RegisterResponse` |
| **Presentation** | `exceptions.py` | 15+ exception classes (token expired, malformed, invalid, blacklisted, etc.) |

### User Module

จัดการข้อมูลผู้ใช้และ RBAC

| ส่วน | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `User` dataclass, `Name`, `Email`, `Phone`, `Gender` value objects |
| **Domain** | `permission_entities.py` | `Permission`, `Role_`, `UserRole`, `RolePermission` |
| **Application** | `use_cases.py` | `UserUseCases` - create, me |
| **Application** | `enums.py` | `Gender`, `UserStatus` enums |
| **Infrastructure** | `models.py` | `UserModel` |
| **Infrastructure** | `permission_models.py` | `RoleModel`, `PermissionModel`, `UserRoleModel`, `RolePermissionModel` |
| **Presentation** | `routers.py` | Endpoints: POST create user (ต้อง auth), GET me (API key หรือ JWT) |

### Health Module

| ส่วน | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `Health` dataclass (alembic_version, user, status) |
| **Infrastructure** | `models.py` | `AlembicModel` - อ่าน `alembic_version` table |
| **Presentation** | `routers.py` | GET /health/ (public), GET /api/v1/alembic-version/ (admin only) |

### Example Module

ตัวอย่าง module สำหรับ reference

| ส่วน | ไฟล์ | คำอธิบาย |
|------|------|----------|
| **Domain** | `entities.py` | `Example` dataclass, `FullName` value object |
| **Presentation** | `routers.py` | POST / (public, ไม่ต้อง auth) |

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
