# 🏗️ ระบบ Monorepo: FastAPI Backend + Django Frontend BFF

## 📖 สารบัญ

1. [ภาพรวมสถาปัตยกรรม](#1-ภาพรวมสถาปัตยกรรม)
2. [API Reference](#2-api-reference)
3. [FastAPI Backend (9 Modules)](#3-fastapi-backend)
4. [Django Frontend BFF (10 Apps)](#4-django-frontend-bff)
5. [การทำงานร่วมกัน](#5-การทำงานร่วมกัน)
6. [จุดต่อขยาย](#6-จุดต่อขยาย)
7. [Bug Patterns และวิธีแก้](#7-bug-patterns-และวิธีแก้)
8. [สรุปและข้อเสนอแนะ](#8-สรุปและข้อเสนอแนะ)

---

## 1. ภาพรวมสถาปัตยกรรม

### 1.1 โครงสร้าง Monorepo

ระบบเป็น **Monorepo** ที่รวม 2 services หลักที่ทำงานร่วมกันผ่าน HTTP และ WebSocket:

```
project-root/
│
├── fastapi-backend/          🐍 Backend API (Clean Arch + DDD)
├── django-frontend/          🎨 BFF (Backend for Frontend)
├── docker-compose.yaml       🐳 Stack รวม (optional)
└── README.md                 📘 เอกสารรวม
```

### 1.2 แผนภาพการทำงาน

```
┌────────────────────────────────────────────────────────────────────┐
│                         Browser                                    │
│                  (Cookies: access_token, refresh_token)            │
└────────────────┬──────────────────────────────┬────────────────────┘
                 │ HTTP                          │ WS
                 ▼                               ▼
┌────────────────────────────────┐   ┌──────────────────────────────┐
│   Django BFF (Port 8001)       │   │   Django Channels            │
│   ─ Server-side rendering      │   │   (WS Proxy Consumer)        │
│   ─ Alpine.js + Tailwind       │   │                              │
│   ─ Thin proxy → FastAPI       │   │                              │
└────────────────┬───────────────┘   └──────────────┬───────────────┘
                 │ HTTP (forward cookies)           │ WS (forward cookies + Origin)
                 ▼                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                           │
│   ─ 9 modules (Clean Arch + DDD)                                   │
│   ─ Nested JWT (JWS + JWE)                                         │
│   ─ ResponseFormattingMiddleware                                   │
└────────────────┬──────────────────────────────┬────────────────────┘
                 │                              │
                 ▼                              ▼
         ┌───────────────┐              ┌───────────────┐
         │  PostgreSQL   │              │     Redis     │
         │  (persistence)│              │    (cache)    │
         └───────────────┘              └───────────────┘
```

### 1.3 หลักการสำคัญ

| หลักการ | รายละเอียด |
|---------|-----------|
| **Backend API** | FastAPI ทำหน้าที่จัดการ business logic ทั้งหมด |
| **BFF Pattern** | Django ไม่มี database เอง — proxy ไป FastAPI เท่านั้น |
| **Cookie Passthrough** | FastAPI set cookies → Django forward → Browser |
| **Separate Concerns** | Django = presentation layer, FastAPI = business layer |

---

## 2. API Reference

### 2.1 สรุป Routes ทั้งหมด

**22 HTTP routes + 1 WebSocket channel** — ทุก route ลงทะเบียน **2 รูปแบบ** (มี/ไม่มี trailing slash) แต่ OpenAPI แสดงเฉพาะแบบมี slash

#### Authentication

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `POST` | `/api/v1/authentication/login/` | 🌐 Public | ออก cookie pair — **form-encoded** ไม่ใช่ JSON |
| `PATCH` | `/api/v1/authentication/refresh/` | 👤 User | หมุน refresh token + mint access token ใหม่ |
| `DELETE` | `/api/v1/authentication/logout/` | 🌐 Public¹ | revoke session + clear cookies |

> ¹ `logout` อยู่ใน public allowlist แต่ยังรัน `authenticate_logout` ซึ่งทนต่อ partial expiry — stale session ยัง cleanup ได้

#### User

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `POST` | `/api/v1/user/` | 🌐 Public | ลงทะเบียน — email ต้องตรง `SECURITY_EMAIL_ALLOWED_DOMAINS` |
| `GET` | `/api/v1/user/me/` | 👤 User | โปรไฟล์ของ user ที่ authenticate |

#### API Keys

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `POST` | `/api/v1/key/` | 🔴 Admin | สร้าง key — **คืน raw secret ครั้งเดียว** |
| `GET` | `/api/v1/key/` | 🔴 Admin | list (paginated) |
| `GET` | `/api/v1/key/{id}/` | 🔴 Admin | หนึ่ง key พร้อม creator/updater |
| `PATCH` | `/api/v1/key/{id}/` | 🔴 Admin | rename หรือ re-describe (partial) |
| `PATCH` | `/api/v1/key/{id}/rotate/` | 🔴 Admin | secret ใหม่, record เดิม — **คืน raw secret ครั้งเดียว** |
| `DELETE` | `/api/v1/key/{id}/` | 🔴 Admin | revoke (soft delete) + invalidate cache |

#### Knowledge

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `POST` | `/api/v1/knowledge/` | 🟡 Manager | สร้าง + broadcast notification |
| `GET` | `/api/v1/knowledge/` | 🟡 Manager | list (paginated) |
| `PATCH` | `/api/v1/knowledge/{id}/` | 🟡 Manager | partial update |
| `DELETE` | `/api/v1/knowledge/{id}/` | 🟡 Manager | soft delete |

#### Notification

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `GET` | `/api/v1/notification/` | 👤 User | notifications ของ caller (paginated) |
| `PATCH` | `/api/v1/notification/{id}/` | 👤 User | mark as read |

#### Health / WebSocket / Example

| Method | Path | Access | คำอธิบาย |
|--------|------|--------|----------|
| `GET` | `/health/` | 🌐 Public | Liveness probe |
| `GET` | `/` | ⚠️ | redirect ไป `/docs` (ดู Known Limitations) |
| `GET` | `/api/v1/alembic-version/` | 🔴 Admin | migration revision ที่ apply |
| `GET` | `/api/v1/websocket/connect/` | 🌐 Public | decoy — raise ทันที |
| `WS` | `/api/v1/websocket/connect/` | 👤 User | channel จริง — origin-validated |
| `POST` | `/api/v1/example/` | 🌐 Public | minimal reference endpoint |

### 2.2 Response Envelope

**ทุก JSON response** ถูก wrap โดย `ResponseFormattingMiddleware` — handler return plain schema เท่านั้น

```json
{
  "code": 200,
  "method": "GET",
  "path": "/api/v1/key/",
  "timestamp": "2026-07-31T12:34:56Z",
  "details": {
    "message": "Resource retrieved successfully",
    "data": { }
  }
}
```

| Field | ความหมาย |
|-------|----------|
| `code` | HTTP status code |
| `method` | HTTP method |
| `path` | Request path |
| `timestamp` | ISO 8601, UTC |
| `details.message` | `ResponseMessages` constant — **ห้ามใช้ ad-hoc string** |
| `details.data` | payload หรือ `{"errors": ...}` เมื่อ error |

**Exception:** Swagger, ReDoc, `text/event-stream` **ข้าม** wrapper

### 2.3 Pagination

| Parameter | Type | Default | Constraint |
|-----------|------|---------|------------|
| `page` | int | `1` | ≥ 1 |
| `limit` | int | `20` | 1–100 |
| `sort_order` | enum | `desc` | `asc` \| `desc` |
| `sort_by` | enum | per module | ต้องเป็น column จริง |

**ทุก list response** มี pagination block:

```json
{
  "total": 87,
  "page": 2,
  "limit": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": true
}
```

> **เทคนิคสำคัญ:** total คำนวณใน **query เดียวกัน** กับ page โดยใช้ window function `func.count(...).over()` — ไม่มี `COUNT(*)` round trip ที่สอง

> **Naming:** HTTP layer ใช้ `limit` แต่ domain layer ใช้ `per_page` — mapper แปลงที่ boundary

### 2.4 Error Catalogue

| Status | `ResponseMessages` | เมื่อไหร่ |
|--------|-------------------|-----------|
| `400` | `VALIDATION_ERROR` | domain rule fail → `DomainException` |
| `400` | `BAD_REQUEST` | update ไม่มี effective change |
| `401` | `UNAUTHORIZED_ERROR` | credential missing/invalid/revoked/expired |
| `403` | `AUTHORIZATION_ERROR` | authenticated แต่ไม่ได้รับอนุญาต |
| `404` | `RESOURCE_NOT_FOUND` | record ไม่มี หรือ soft-deleted |
| `405` | `METHOD_NOT_ALLOWED` | method ไม่รองรับ |
| `409` | `CONFLICT` | natural-key collision |
| `422` | `VALIDATION_ERROR` | Pydantic reject ก่อน handler รัน |
| `500` | `INTERNAL_ERROR` | unexpected failure |
| `502` | `BAD_GATEWAY` | upstream failed |
| `504` | `GATEWAY_TIMEOUT` | upstream timeout |

**ความต่าง 400 vs 422:**
- **422** = FastAPI reject request shape **ก่อน** code รัน
- **400** = business rule fail **ภายใน** code

**Error body:** `details.data.errors` เป็น **string** (error เดียว) หรือ **list** (หลาย error) — entity report **ทั้งหมด** ในครั้งเดียว ไม่ใช่แค่ตัวแรก

### 2.5 WebSocket Channel

- **Endpoint:** `ws://localhost:8000/api/v1/websocket/connect/`
- **Auth:** HTTP-only cookies (browser ส่งอัตโนมัติตอน upgrade)
- **Origin validation:** ตรวจ `SECURITY_ALLOW_ORIGINS` เพราะ `CORSMiddleware` **ไม่ครอบ** WS handshake
- **ทิศทาง:** Server → Client เท่านั้น (client frames ถูก discard → ใช้เป็น keepalive ได้)

**Message shape:**
```json
{
  "message_type": "notification",
  "body": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-15T10:30:00Z",
    "notification_type": "knowledge_created",
    "title": "Knowledge base created",
    "body": "The knowledge base 'ML Fundamentals' was created successfully.",
    "redirect_url": "https://app.example.com/knowledge/550e8400"
  }
}
```

**Role cascade:**
- `ADMIN` → admins เท่านั้น
- `MANAGER` → managers + admins
- `USER` → ทุกคน

**Dev tools:** browser test client + AsyncAPI 2.6 spec ที่ `/devtools/`

---

## 3. FastAPI Backend

### 3.1 โครงสร้าง Module มาตรฐาน

ทุก module ใช้ pattern เดียวกัน — `key` module เป็น **canonical reference**:

```
app/modules/{module}/
│
├── domain/                              # ไม่ depend on อะไร
│   ├── entities.py                      # Dataclasses ขยาย BaseEntity; validation ใน __post_init__
│   ├── value_objects.py                 # Plain classes: _normalize → _validate → __str__ → __eq__
│   └── enums.py                         # (str, Enum) เสมอ
│
├── application/                         # use cases + interfaces
│   ├── interfaces.py                    # Protocol: I{Entity}Repository / Cache / Service
│   ├── use_cases.py                     # {Module}UseCases class เดียว
│   ├── mappers.py                       # # ENTITY/DTOS · # ENTITY/MODELS · # ENTITY/CACHE
│   ├── exceptions.py                    # {Module}Exception + one per business rule
│   └── utils.py                         # Module-local helpers
│
├── infrastructure/                      # implementations
│   ├── models.py                        # SQLAlchemy models ขยาย BaseModel
│   ├── repositories.py                  # Postgres{Entity}Repository — flush(), never commit()
│   ├── caches.py                        # Redis{Entity}Cache — namespaced, tombstoned, never raises
│   └── services.py                      # external/stateful systems behind Protocol
│
└── presentation/                        # HTTP
    ├── routers.py                       # payload → mapper → use case → mapper → return
    ├── schemas.py                       # Pydantic v2 + full Field + ConfigDict
    ├── docs.py                          # router_docs + {action}_docs per endpoint
    └── dependencies.py                  # Depends factories returning Protocol type
```

### 3.2 ตารางเปรียบเทียบ 9 Modules

| Module | Routes | Persistence | Cache | Service | บทบาท |
|--------|--------|-------------|-------|---------|-------|
| `shared` | — | base types | — | — | `BaseEntity`, `BaseModel`, `SharedUseCases` |
| `authentication` | 3 | ✅ | ✅ | `ITokenService` | Session lifecycle, token rotation |
| `user` | 2 | ✅ | — | — | Accounts, roles, `/me` |
| `key` | 6 | ✅ | ✅ | `IKeyService` | **Canonical reference** |
| `knowledge` | 4 | ✅ | partial | — | CRUD + broadcast notifications |
| `notification` | 2 | ✅ | — | — | Per-user + role-cascaded fan-out |
| `websocket` | 1 + WS | — | — | `IConnectionManagerService` | In-memory, single-process |
| `health` | 3 | `alembic_version` | — | — | Liveness, migration state |
| `example` | 1 | — | — | — | Minimal demo; no repository/model |

### 3.3 Core Layer

```
app/core/
├── __init__.py
├── settings.py           # Pydantic-settings: JWT, Redis, Cookies, DB, Security
├── security.py           # Nested JWT (JWS + JWE)
├── database.py           # SQLAlchemy async engine + get_async_session
├── cache.py              # Redis async client + get_cache_session
├── logging.py            # Loguru + orjson
├── middleware.py         # ResponseFormatting, LogRequest, DeviceId
└── exceptions.py         # CoreException
```

### 3.4 Entry Point & Middleware Stack

```
Request
  │
  ├─► DeviceIdMiddleware              # inject request.state.device_id
  ├─► LogRequestMiddleware            # structured logging
  ├─► ResponseFormattingMiddleware    # wrap JSON เป็น envelope
  └─► CORSMiddleware                  # REST เท่านั้น (ไม่ครอบ WS)
       │
       ▼
    Router → Handler
```

**Entry Point:**
- `app/app.py` — สร้าง `FastAPI()` instance
- `app/routes.py` — register ทุก router
- `app/middleware.py` — register ทุก middleware

### 3.5 โครงสร้าง Root

```
fastapi-backend/
├── app/
│   ├── app.py                    # Entry point
│   ├── core/                     # Cross-cutting concerns
│   ├── modules/                  # 9 modules (ดูด้านบน)
│   ├── routes.py                 # Router registration
│   └── middleware.py             # Middleware registration
│
├── migrations/                   # Alembic
│   ├── env.py                    # ⚠️ ต้อง import ทุก model
│   ├── script.py.mako
│   └── versions/                 # ships empty
│
├── scripts/
│   ├── create_module.py          # สร้าง module skeleton
│   ├── generate_secret.py        # 32-byte hex secret
│   ├── generate_fernet.py        # Fernet key
│   ├── directory_tree.py         # เขียน tree
│   ├── websocket_test.html       # Browser WS client
│   └── asyncapi.yaml             # AsyncAPI 2.6 spec
│
├── secrets/keys/                 # JWT keys (gitignored)
│   ├── signing-private.pem
│   ├── signing-public.pem
│   ├── encryption-private.pem
│   └── encryption-public.pem
│
├── test/
│   ├── core/
│   └── modules/{module}/
│
├── docs/postman_collection.json
├── .env.example
├── alembic.ini
├── docker-compose.yaml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

---

## 4. Django Frontend BFF

### 4.1 หลักการ BFF

Django **ไม่มี database เอง** — ทำหน้าที่เป็น **Proxy + Renderer**:

```
Browser ──HTTP──► Django View
                     │
                     ▼
                  UseCase
                     │
                     ▼
              FastAPIClient (httpx)
                     │
                     ▼
              FastAPI Backend
                     │
                     ▼
            Response envelope
                     │
                     ▼
            Map to Django context
                     │
                     ▼
              Render template
                     │
Browser ◄────HTML────┘
```

### 4.2 โครงสร้าง 10 Apps

```
django-frontend/apps/
│
├── shared/              🔗 Base types + FastAPI client
│   ├── domain/          BaseEntity, UNSET, Email, Name, Phone
│   ├── application/     SharedUseCases, Protocols, exceptions
│   ├── infrastructure/  fastapi_client.py (httpx), FastAPISessionMiddleware
│   └── presentation/    context_processors, dependencies
│
├── layout/              🎨 Layout Components (ไม่ routed)
│   ├── presentation/    views.py, urls.py
│   └── templates/layout/
│       ├── app_layout.html        = AppLayoutComponent
│       ├── header.html            = HeaderComponent
│       ├── sidebar.html           = SidebarComponent
│       ├── footer.html            = FooterComponent
│       └── layout_settings.html   = LayoutSettingsComponent
│
├── authentication/      🔐 Auth Proxy
│   ├── domain/          Authentication entity
│   ├── application/     Login, Logout, Refresh use cases
│   ├── infrastructure/  fastapi_auth_client.py
│   └── presentation/    LoginView, LogoutView, LoginForm
│
├── dashboard/           🏠 Dashboard
│   └── presentation/    DashboardView
│
├── user/                👤 User Proxy
│   └── presentation/    ProfileView, UserForm
│
├── key/                 🔑 API Keys Proxy
│   ├── domain/          Key entity, KeySecret, KeyPrefix, KeyStatus
│   ├── application/     KeyUseCases, IKeyRepository, KeyMapper
│   ├── infrastructure/  KeyFastAPIClient
│   └── presentation/    Key CRUD views, KeyCreateForm, KeyUpdateForm
│
├── knowledge/           📚 Knowledge Proxy
│   └── presentation/    Knowledge CRUD views, KnowledgeForm
│
├── notification/        🔔 Notification Proxy
│   └── presentation/    NotificationListView
│
├── websocket/           🔌 WS Proxy
│   ├── application/     NotificationProxyConsumer
│   ├── infrastructure/  fastapi_ws_client.py
│   └── presentation/    routing.py
│
└── core/                🛠️ Core utilities
    └── presentation/    HealthView, ErrorViews
```

### 4.3 Config & Infrastructure

```
django-frontend/config/
├── __init__.py
├── settings.py           # Settings + INSTALLED_APPS + MIDDLEWARE
├── urls.py               # Root URLconf
├── asgi.py               # ASGI (Channels) — สำหรับ WebSocket
├── wsgi.py               # WSGI fallback
└── routing.py            # WebSocket routing
```

### 4.4 Middleware Flow

```
Request
  │
  ├─► FastAPISessionMiddleware    # extract cookies → attach to request
  ├─► Django AuthMiddleware       # session (Django side)
  ├─► CsrfViewMiddleware
  └─► CommonMiddleware
       │
       ▼
    View → UseCase → FastAPIClient → FastAPI Backend
```

### 4.5 Templates Structure

```
templates/
├── base.html                     # ← App Layout (extends)
│
├── partials/                     # Layout partials (= Components)
│   ├── header.html
│   ├── sidebar.html
│   ├── footer.html
│   ├── layout-settings.html
│   ├── page-header.html
│   ├── pagination.html
│   ├── messages.html
│   └── confirm-modal.html
│
├── authentication/               # login.html, logout.html
├── dashboard/                    # index.html
├── user/                         # me.html, list.html
├── key/                          # list.html, detail.html, form.html
├── knowledge/                    # list.html, detail.html, form.html
├── notification/                 # list.html
└── errors/                       # 400, 403, 404, 500
```

### 4.6 Static Files

```
static/
├── css/
│   ├── tailwind.css              # Tailwind source
│   ├── tailwind.output.css       # Build output
│   └── app.css                   # Custom overrides
│
├── js/
│   ├── app.js                    # Alpine.js root
│   ├── header.js                 # Header logic
│   ├── sidebar.js                # Sidebar logic
│   ├── layout-settings.js        # Settings logic
│   ├── websocket.js              # WS client
│   └── api.js                    # Fetch helpers
│
└── img/
    ├── logo.svg
    ├── logo-dark.svg
    └── favicon.ico
```

### 4.7 Docs — AI Prompt Templates

```
docs/
├── template_modules.md           # 📘 Master template
├── README.md                     # 📑 Index 68 modules
│
└── prompts/                      # 1 module = 1 file
    ├── layer-0-core/             (6 modules)   money, tenant_context, audit, idempotency, config, events
    ├── layer-1-foundation/       (11 modules)  tenancy, authentication, user, employee, ...
    ├── layer-2-money-path/       (7 modules)   order, invoice, ledger, payment, ...
    ├── layer-3-goods-path/       (13 modules)  inventory, warehouse, lot, production, ...
    ├── layer-4-operations/       (13 modules)  transport, delivery, route, gps, retail, ...
    ├── layer-5-intelligence/     (7 modules)   reporting, analytics, forecast, kpi, ...
    ├── layer-6-monitoring/       (8 modules)   iot, cctv, monitoring, backup, alerting, ...
    └── layer-7-templates/        (3 modules)   health, example, blank
```

**นัยสำคัญ:** มี **68 modules planned** แบ่งเป็น 8 layers (0–7) — ปัจจุบัน implement 9 modules แรก

### 4.8 โครงสร้าง Root

```
django-frontend/
├── config/                       # Django Project
├── apps/                         # 10 Django Apps
├── templates/                    # Global Templates
├── static/                       # Static files
├── docs/                         # AI Prompt Templates
├── test/
│   ├── conftest.py               # pytest fixtures
│   ├── core/                     # test_middleware.py, test_fastapi_client.py
│   └── modules/{app}/
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yaml
├── manage.py
├── requirements.txt
├── pyproject.toml                # ruff, pytest config
├── tailwind.config.js
├── postcss.config.js
└── README_STR.md
```

---

## 5. การทำงานร่วมกัน

### 5.1 Flow 1: Login

```
1. Browser ──POST /login/──► Django LoginView
2. Django ──POST /api/v1/authentication/login/──► FastAPI (form-encoded)
3. FastAPI ──Set-Cookie: access_token, refresh_token (HttpOnly)──► Django
4. Django ──forward Set-Cookie──► Browser
5. Browser เก็บ cookies ไว้ใช้ต่อ
```

**จุดสำคัญ:** Cookies ถูก set โดย FastAPI แต่ Django ทำหน้าที่ **forward** ให้ browser

### 5.2 Flow 2: API Call ผ่าน Django BFF

```
1. Browser ──GET /keys/──► Django KeyListView
2. Django ──GET /api/v1/key/?page=1──► FastAPI (forward cookies)
3. FastAPI ──envelope JSON──► Django
4. Django ──map data → context──► Template
5. Browser ◄──HTML (rendered)──┘
```

### 5.3 Flow 3: WebSocket

```
1. Browser ──WS /ws/notifications/──► Django Channels (NotificationProxyConsumer)
2. Django ──WS ws://fastapi:8000/api/v1/websocket/connect/──► FastAPI
                                       (forward cookies + Origin)
3. FastAPI ──broadcast notification──► Django
4. Django ──forward frame──► Browser
```

**เหตุผลที่ต้อง proxy:** FastAPI WS ตรวจ `Origin` ตาม `SECURITY_ALLOW_ORIGINS` — ต้องตั้งค่าให้ตรงกับ Django's origin

### 5.4 Cookie Strategy

| Cookie | HttpOnly | Path | ใช้โดย |
|--------|----------|------|--------|
| `access_token` | ✅ | `/` | FastAPI (validate), Django (forward) |
| `refresh_token` | ✅ | `/api/v1/authentication/` | FastAPI (rotate) |
| `token_type` | ✅ | `/` | Metadata (Bearer) |

---

## 6. จุดต่อขยาย

### 6.1 เพิ่ม Module ใหม่ใน FastAPI

**ใช้ script:**
```bash
python scripts/create_module.py product
```

จะได้ skeleton ตาม pattern มาตรฐาน แล้วเพิ่มใน `app/routes.py`:

```python
from app.modules.product.presentation.routers import router as product_router

app.include_router(product_router)
```

> **Tip:** copy `key` module เพราะเป็น **canonical reference** ที่สมบูรณ์ที่สุด

### 6.2 เพิ่ม Module ใหม่ใน Django BFF

สร้าง app ใหม่ตาม pattern:

```
apps/product/
├── domain/entities.py
├── application/use_cases.py
├── infrastructure/fastapi_client.py    # ← proxy ไป FastAPI
└── presentation/views.py, urls.py, forms.py
```

เพิ่มใน `INSTALLED_APPS` และ `config/urls.py`

### 6.3 เพิ่ม Layer ใหม่ใน Docs

สร้าง folder `docs/prompts/layer-8-xxx/` แล้วเพิ่ม `*.md` ต่อ module

### 6.4 เปลี่ยน Cache Backend

Implement `I{Entity}Cache` Protocol ใหม่ แล้ว swap ใน `dependencies.py`:

```python
def get_key_cache(...) -> IKeyCache:
    return MemcachedKeyCache(...)  # swap implementation
```

### 6.5 เปลี่ยน Token Algorithm

สร้าง `TokenService` ใหม่ที่ implement `ITokenService`:

```python
class RS256TokenService(ITokenService):
    async def generate(self, authentication): ...
    async def hash_tokens(self, authentication): ...
    async def verify_password(self, plain, hashed): ...
```

### 6.6 เพิ่ม Middleware ใหม่

- **FastAPI:** แก้ `app/middleware.py`
- **Django:** แก้ `MIDDLEWARE` ใน `config/settings.py`

---

## 7. Bug Patterns และวิธีแก้

### Bug 1: Port Occupied (`[Errno 10048]`)

**อาการ:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```

**สาเหตุ:**
- Process เก่าค้าง (stale uvicorn)
- TCP listener entry ค้างหลัง kill
- Process อื่นใช้ port อยู่

**วิธีแก้:**
```powershell
# 1. ตรวจหา process
Get-NetTCPConnection -LocalPort 8000 -State Listen

# 2. Kill
Stop-Process -Id <PID> -Force

# 3. ถ้า TCP entry ยังค้าง → ใช้ port อื่น
Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue
```

### Bug 2: Login Response ไม่มี tokens

**สาเหตุ:** `entity_login_mapper` ไม่ map tokens

**วิธีแก้:**
```python
def entity_login_mapper(_authentication: Authentication) -> LoginResponse:
    return LoginResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
    )
```

และ `LoginResponse` ต้องมี field เป็น **required** (ไม่ใช่ default)

### Bug 3: Cache Stampede / Revoked Token Resurrection

**ปัญหา:** Concurrent logout ระหว่าง read → write กลับ cache ด้วย pre-revocation snapshot ทำให้ token ที่ revoke แล้วยังใช้ได้จนหมด TTL

**วิธีแก้ — Tombstone Pattern:**
```python
async def delete_by_access_token(self, authentication):
    suffix = f"access_token:{hashed_jti}"
    # 1. เขียน tombstone ก่อน
    await self.cache.set(self._tombstone(suffix), 1, ex=TOMBSTONE_TTL)
    # 2. ลบ key
    await self.cache.delete(self._key(suffix))


async def insert_by_access_token(self, authentication, ttl=None):
    suffix = f"access_token:{hashed_jti}"
    # 3. ตรวจ tombstone ก่อน insert
    if await self.cache.exists(self._tombstone(suffix)):
        return  # skip — ป้องกัน resurrection
    await self.cache.set(self._key(suffix), ...)
```

### Bug 4: Circular Import

**ปัญหา:** `logging.py` import `settings` ซึ่ง pull `modules.shared.domain.enums`

**วิธีตรวจ:**
```powershell
.venv\Scripts\python.exe -c "import app.app"
```

**วิธีแก้:**
- ใช้ lazy import ภายใน function
- หรือ import จาก `core.config` (เบากว่า)

### Bug 5: JWT Key Mismatch

**อาการ:** Token ถูก generate แต่ verify ไม่ผ่าน

**สาเหตุ:**
- Signing key ≠ verification key
- Encryption key ผิด
- Key files ไม่ได้ generate

**วิธีแก้:**
```bash
python scripts/generate_secret.py       # 32-byte hex
python scripts/generate_fernet.py       # Fernet key
# หรือ generate RSA keypair สำหรับ signing/encryption
```

### Bug 6: WebSocket Origin Rejected

**อาการ:** WS connect fail ทั้งที่ cookies ถูกต้อง

**สาเหตุ:** `CORSMiddleware` **ไม่ครอบ** WebSocket handshake — ต้องตรวจ `Origin` เอง

**วิธีแก้:** เพิ่ม Django origin ใน `SECURITY_ALLOW_ORIGINS`:
```env
SECURITY_ALLOW_ORIGINS=http://localhost:8000,http://localhost:8001
```

### Bug 7: Alembic Migration ไม่เห็น Model ใหม่

**สาเหตุ:** `migrations/env.py` ไม่ได้ import model

**วิธีแก้:**
```python
# migrations/env.py
from app.modules.product.infrastructure.models import ProductModel  # noqa
```

หรือใช้ auto-discovery:
```python
from app.modules import __all__ as all_modules

for module in all_modules:
    __import__(f"app.modules.{module}.infrastructure.models")
```

### Bug 8: Django BFF Cookie Passthrough ล้มเหลว

**อาการ:** Login สำเร็จที่ FastAPI แต่ browser ไม่ได้ cookies

**สาเหตุ:**
- Django ไม่ได้ forward `Set-Cookie` header
- Domain/Path ไม่ตรง
- `Secure` flag set แต่ใช้ HTTP

**วิธีแก้:**
```python
# Django view
response = HttpResponseRedirect("/dashboard/")
for cookie in fastapi_response.cookies:
    response.set_cookie(
        cookie.name,
        cookie.value,
        httponly=True,
        secure=not settings.DEBUG,  # ← ต้องตรงกับ environment
        samesite="lax",
    )
```

### Bug 9: Envelope ไม่ครอบ Response

**อาการ:** Response ไม่มี `code`, `method`, `path`, `timestamp`

**สาเหตุ:**
- Response เป็น `text/event-stream` (bypass โดยตั้งใจ)
- Response เป็น Swagger/ReDoc (bypass)
- Middleware ไม่ได้ register

**วิธีแก้:** ตรวจ `app/middleware.py` ว่า `ResponseFormattingMiddleware` ถูกเพิ่มหรือยัง

### Bug 10: Pagination `sort_by` Invalid Column

**อาการ:** 500 error เมื่อใช้ `sort_by=nonexistent`

**สาเหตุ:** `sort_by` enum ไม่ได้ validate กับ column จริง

**วิธีแก้:**
```python
class KeySortBy(str, Enum):
    id = "id"
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


# ใน repository
sort_column = getattr(KeyModel, sort_by.value, KeyModel.created_at)
```

---

## 8. สรุปและข้อเสนอแนะ

### 8.1 จุดแข็งของระบบ

| ด้าน | รายละเอียด |
|------|-----------|
| **Separation of Concerns** | 4 layers ต่อ module: domain/application/infrastructure/presentation |
| **Dependency Inversion** | ทุก dependency ผ่าน Protocol; swap implementation ได้ |
| **Consistent Envelope** | ทุก response มี shape เดียวกัน — client parse ง่าย |
| **Efficient Pagination** | Window function → 1 query เท่านั้น |
| **Cache Safety** | Tombstone pattern ป้องกัน revoked token resurrection |
| **BFF Pattern** | Django เป็น thin proxy — ไม่ duplicate business logic |
| **Component Pattern** | Templates ใช้ partials เหมือน React components |
| **AI-Ready Docs** | 68 modules พร้อม prompt templates ต่อ layer |
| **Nested JWT** | JWS (sign) + JWE (encrypt) — defense in depth |
| **Canonical Reference** | `key` module เป็นแม่แบบที่สมบูรณ์ |

### 8.2 จุดที่ต้องระวัง

| ด้าน | ความเสี่ยง |
|------|-----------|
| **Port Management** | dev environment มี stale process บ่อย |
| **Cookie Path/Scope** | ต้อง sync ระหว่าง FastAPI และ Django |
| **WS Origin** | CORSMiddleware ไม่ครอบ → ต้อง config แยก |
| **Naming** | HTTP `limit` vs domain `per_page` — ต้อง map ทุกครั้ง |
| **Circular Import** | `settings` import chain ยาว |
| **Alembic Auto-discovery** | ต้อง import model เองทุกครั้ง |
| **Single-process WS** | ConnectionManager in-memory → scale ไม่ได้ |

### 8.3 แนวทางพัฒนาในอนาคต

1. **Scale WebSocket:** ย้าย ConnectionManager ไป Redis Pub/Sub หรือ NATS
2. **Distributed Tracing:** เพิ่ม OpenTelemetry ตั้งแต่ Django → FastAPI → DB
3. **Contract Testing:** ใช้ AsyncAPI spec สำหรับ WS + OpenAPI สำหรับ REST
4. **Module Generator:** ขยาย `create_module.py` ให้สร้างทั้ง FastAPI + Django + tests
5. **Feature Flags:** เพิ่ม layer สำหรับ toggle 68 modules ที่ planned

### 8.4 สรุปสุดท้าย

ระบบนี้เป็น **Monorepo ระดับ production** ที่ใช้:

- **FastAPI** เป็น backend API ที่ทำตาม Clean Architecture + DDD อย่างเคร่งครัด
- **Django** เป็น BFF ที่ render HTML + proxy ไป FastAPI
- **PostgreSQL + Redis** เป็น persistence + cache layer
- **Nested JWT (JWS + JWE)** เป็น auth mechanism
- **22 HTTP routes + 1 WebSocket** ครอบคลุม 9 modules
- **68 modules planned** ใน 8 layers (ปัจจุบัน implement 9)

**จุดเด่นที่สุด:** `key` module เป็น **canonical reference** — module อื่นๆ copy pattern มาจากตัวนี้ ทำให้การเพิ่ม module ใหม่เป็นเรื่อง predictable และ testable

**จุดที่ต้องระวังที่สุด:** Cookie passthrough ระหว่าง Django ↔ FastAPI ↔ Browser และ WebSocket Origin validation ที่ไม่ครอบโดย CORSMiddleware

---

**📌 เอกสารนี้รวบรวม:**
- API Reference (22 HTTP routes + 1 WS)
- โครงสร้าง FastAPI Backend (9 modules)
- โครงสร้าง Django BFF (10 apps)
- การทำงานร่วมกันระหว่าง 2 services
- จุดต่อขยายในอนาคต
- Bug patterns 10 รายการพร้อมวิธีแก้
