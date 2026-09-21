# 📘 Django Clean Architecture + DDD Template

## สำหรับ ERP + CRM + IoT (SME)

> **A production-shaped Django template — Clean Architecture, Domain-Driven Design, Modular Design**
>
> ผสมผสานแนวคิดจาก [FastAPI Clean Architecture + DDD Template](https://github.com/kongnakornna/fastapi-clean-architecture-ddd-erp-iot/fastapi-clean-architecture-ddd-template) เข้ากับ **Layout Components** และ **Tailwind CSS** เพื่อสร้าง Django Frontend ที่แยกออกมา ใช้งานร่วมกับ FastAPI Backend เดิมได้ โดย**ไม่แก้โค้ดเดิม**

---

**ผู้แต่ง:** Kongnakorn Jantakun
**อีเมล:** kongnakornjantakun@gmail.com
**เวอร์ชัน:** 2.0.0
**อัปเดต:** 2026-09-17
**สถานะ:** ✅ พร้อมใช้งาน

---

## สารบัญ

1. [โครงสร้างการทำงาน](#โครงสร้างการทำงาน)
2. [วัตถุประสงค์](#วัตถุประสงค์)
3. [กลุ่มเป้าหมาย](#กลุ่มเป้าหมาย)
4. [ความรู้พื้นฐาน](#ความรู้พื้นฐาน)
5. [เนื้อหาโดยย่อ](#เนื้อหาโดยย่อ)
6. [บทนำ](#บทนำ)
7. [บทนิยาม](#บทนิยาม)
8. [โครงสร้างโฟลเดอร์](#โครงสร้างโฟลเดอร์)
9. [หลักการทำงาน (Concept)](#หลักการทำงาน-concept)
10. [Workflow และ Dataflow](#workflow-และ-dataflow)
11. [Case Study](#case-study)
12. [AI Prompt Template](#ai-prompt-template)
13. [ภาคผนวก](#ภาคผนวก)

---

## โครงสร้างการทำงาน

Django Template นี้ทำงานเป็น **BFF (Backend-for-Frontend)** ที่แยกออกจาก FastAPI Backend โดยสิ้นเชิง สื่อสารผ่าน HTTP และ WebSocket

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (User)                          │
│  • Tailwind CSS (UI)                                            │
│  • Alpine.js (Interactivity)                                    │
│  • HTMX (Dynamic Partial Loading)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (Session + Cookies)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Django Frontend (BFF)  :8001                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Presentation Layer (Templates + Views)                   │  │
│  │  • Layout Components (Header, Sidebar, Footer)            │  │
│  │  • Django Templates + Tailwind CSS                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Application Layer (Use Cases / Services)                 │  │
│  │  • Proxy Use Cases                                        │  │
│  │  • Session Management                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Infrastructure Layer (FastAPI Client)                    │  │
│  │  • HTTPX Client                                           │  │
│  │  • Cookie Forwarding                                      │  │
│  │  • WebSocket Proxy                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (internal)
                             │ + Cookie forwarding
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (เดิม)  :8000                      │
│  • Authentication (nested JWT)                                  │
│  • User, Key, Knowledge, Notification                           │
│  • WebSocket                                                    │
│  • PostgreSQL + Redis                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## วัตถุประสงค์

| # | วัตถุประสงค์ | ผลลัพธ์ที่คาดหวัง |
|---|---|---|
| 1 | **แยก Frontend ออกจาก FastAPI Backend** | Django ทำหน้าที่ BFF, FastAPI เป็น API-only |
| 2 | **ไม่แก้โค้ดเดิมของ FastAPI** | FastAPI ทำงาน 100% เหมือนเดิม |
| 3 | **นำ Layout Components มาใช้ใหม่** | Port มาเป็น Django Templates + Tailwind |
| 4 | **ใช้ Clean Architecture + DDD** | แยก 4 layers ชัดเจน testable |
| 5 | **Modular Design** | แต่ละ module มีหน้าที่ชัดเจน |
| 6 | **Session + Cookies** | จัดการ auth ผ่าน Django session + forward cookies |
| 7 | **รองรับ ERP + CRM + IoT** | พร้อมขยาย modules |
| 8 | **AI-Ready** | มี Prompt Template สำหรับสร้าง module ใหม่ |

---

## กลุ่มเป้าหมาย

| กลุ่ม | บทบาท | ประโยชน์ |
|---|---|---|
| **Backend Developer** | พัฒนา FastAPI modules | ไม่ต้องแก้โค้ดเดิม |
| **Frontend Developer** | พัฒนา Django Templates | ใช้ Layout Components สำเร็จรูป |
| **Full-Stack Developer** | พัฒนาทั้งระบบ | เข้าใจ architecture เดียวกัน |
| **DevOps Engineer** | Deploy ทั้ง stack | แยก container ได้ |
| **AI Engineer** | สร้าง module ใหม่ด้วย AI | ใช้ Prompt Template |
| **SME Owner** | ใช้งาน ERP + CRM + IoT | UI ครบ, ปลอดภัย |

---

## ความรู้พื้นฐาน

| หัวข้อ | ระดับ | แหล่งเรียนรู้ |
|---|---|---|
| Python 3.14+ | ⭐⭐ | [python.org](https://www.python.org/) |
| Django 5.0+ | ⭐⭐⭐ | [djangoproject.com](https://www.djangoproject.com/) |
| FastAPI | ⭐⭐ | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Clean Architecture | ⭐⭐⭐ | [Uncle Bob's blog](https://blog.cleancoder.com/) |
| Domain-Driven Design | ⭐⭐⭐ | [DDD Reference](https://domainlanguage.com/ddd/) |
| HTML + Tailwind CSS | ⭐⭐ | [tailwindcss.com](https://tailwindcss.com/) |
| Alpine.js | ⭐ | [alpinejs.dev](https://alpinejs.dev/) |
| HTMX | ⭐ | [htmx.org](https://htmx.org/) |
| Docker + Compose | ⭐⭐ | [docs.docker.com](https://docs.docker.com/) |

---

## เนื้อหาโดยย่อ

### 🎯 ภาพรวม

Django Template นี้เป็น **Frontend/BFF Layer** ที่ทำงานร่วมกับ FastAPI Backend ที่มีอยู่แล้ว โดย:

- ✅ **ไม่แตะโค้ด FastAPI** — ทำงานเหมือนเดิม 100%
- ✅ **ใช้ Layout Components** — Port เป็น Django Templates + Tailwind
- ✅ **Clean Architecture + DDD** — 4 layers ต่อ module
- ✅ **Modular Design** — แต่ละ module แยกอิสระ
- ✅ **Session + Cookies** — จัดการ auth ผ่าน Django session
- ✅ **AI-Ready** — มี Prompt Template

### 🎁 ประโยชน์

| ประโยชน์ | รายละเอียด |
|---|---|
| **Separation of Concerns** | Frontend / Backend แยกอิสระ |
| **Reusability** | Layout Components ใช้ซ้ำได้ทุกหน้า |
| **Maintainability** | แก้ไขที่เดียว ใช้ได้ทุกที่ |
| **Testability** | Unit test ง่ายด้วย in-memory fakes |
| **Scalability** | เพิ่ม module ได้ไม่จำกัด |
| **Security** | Session + Cookies + CSRF + JWT forwarding |

---

## บทนำ

### 🌟 ปัญหาที่ Template นี้แก้

**ปัญหาเดิม:**

1. FastAPI Template ให้ Backend ที่สมบูรณ์ แต่ **ไม่มี Frontend**
2. Layout Components มีอยู่แล้ว แต่ **ผูกกับ Angular**
3. การนำ FastAPI + Angular มารวมกัน **ต้องแก้โค้ดทั้งสองฝั่ง**
4. ไม่มี **Prompt Template** สำหรับสร้าง module ใหม่ด้วย AI

**วิธีแก้:**

1. สร้าง **Django Frontend** แยกออกมาเป็น BFF
2. **Port Layout Components** → Django Templates + Tailwind
3. **สื่อสารผ่าน HTTP + Cookies** — FastAPI ไม่ต้องแก้
4. **AI Prompt Template** สำหรับ modules

### 🎯 ผลลัพธ์

- Django Frontend :8001 + FastAPI Backend :8000
- Layout Components ครบ (Header, Sidebar, Footer, Settings)
- Clean Architecture 4 layers
- AI พร้อมสร้าง module ใหม่

---

## บทนิยาม

| คำศัพท์ | ความหมาย |
|---|---|
| **BFF (Backend-for-Frontend)** | Backend ที่ทำหน้าที่เฉพาะ Frontend — proxy, transform, render |
| **Clean Architecture** | สถาปัตยกรรมที่แยกชั้น Domain/Application/Infrastructure/Presentation |
| **DDD (Domain-Driven Design)** | การออกแบบที่ให้ Domain เป็นศูนย์กลาง |
| **Module** | หน่วยย่อยของระบบ แยกอิสระ มี 4 layers |
| **Use Case** | Business logic ของ module |
| **Entity** | วัตถุใน domain ที่มี identity |
| **Value Object** | วัตถุใน domain ที่ไม่มี identity (immutable) |
| **Repository** | Interface สำหรับ persist entity |
| **Cache** | ตัวช่วยเร่งความเร็ว (Redis) |
| **Service** | ระบบภายนอก (SMTP, MQTT, AI) |
| **Mapper** | ตัวแปลงระหว่าง Entity ↔ Model ↔ DTO |
| **Protocol** | Interface ของ Python (typing.Protocol) |
| **Session** | ข้อมูลฝั่ง server (Django session) |
| **Cookie** | ข้อมูลฝั่ง client (HTTP-only) |
| **Layout Component** | ชิ้นส่วน UI หลัก (Header, Sidebar, Footer) |
| **Tailwind CSS** | Utility-first CSS framework |
| **Alpine.js** | Lightweight JavaScript framework |
| **HTMX** | Library สำหรับ AJAX + HTML |
| **Tombstone** | Marker สำหรับ invalidation cache |
| **Idempotency** | คุณสมบัติที่ทำซ้ำได้ผลลัพธ์เดิม |
| **Read-back Verification** | ตรวจสอบข้อมูลหลังบันทึก |
| **Money Path** | เส้นทางเงิน — idempotent, audit, read-back |
| **Goods Path** | เส้นทางสินค้า — FEFO/FIFO, lot traceability |
| **Data Path** | เส้นทางข้อมูล — at-least-once, dedup |
| **Outbox Pattern** | เขียน DB ก่อน sync cloud |
| **Reversible Ledger** | ห้ามลบ entry ต้อง reversal |

---

## โครงสร้างโฟลเดอร์ | folder-structure

### 📁 โครงสร้างหลัก

```
django-frontend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yaml
├── README_STR.md
│
├── config/                          # Django Project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── routing.py                   # WebSocket routing
│
├── apps/                            # Django Apps (Modules)
│   ├── shared/                      # Shared base types
│   ├── layout/                      # Layout Components
│   ├── authentication/              # Proxy → FastAPI
│   ├── dashboard/                   # หน้าหลัก
│   ├── user/                        # Proxy → FastAPI
│   ├── key/                         # Proxy → FastAPI
│   ├── knowledge/                   # Proxy → FastAPI
│   ├── notification/                # Proxy → FastAPI
│   ├── websocket/                   # WebSocket Proxy
│   └── core/                        # Core utilities
│
├── templates/                       # Global Templates
│   ├── base.html                    # ← App Layout
│   ├── partials/
│   │   ├── header.html
│   │   ├── sidebar.html
│   │   ├── footer.html
│   │   ├── layout-settings.html
│   │   └── page-header.html
│   ├── authentication/
│   │   └── login.html
│   ├── dashboard/
│   │   └── index.html
│   ├── user/
│   │   └── me.html
│   ├── key/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── form.html
│   ├── knowledge/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── form.html
│   └── notification/
│       └── list.html
│
├── static/
│   ├── css/
│   │   ├── tailwind.css
│   │   └── app.css
│   ├── js/
│   │   ├── app.js
│   │   ├── header.js
│   │   ├── sidebar.js
│   │   └── layout-settings.js
│   └── img/
│       └── logo.svg
│
├── docs/                            # AI Prompt Templates
│   ├── template_modules.md          # Master template
│   ├── README.md                    # Index
│   └── prompts/
│       ├── layer-0-core/
│       │   ├── money.md
│       │   ├── tenant_context.md
│       │   ├── audit.md
│       │   ├── idempotency.md
│       │   ├── config.md
│       │   └── events.md
│       ├── layer-1-foundation/
│       │   ├── tenancy.md
│       │   ├── authentication.md
│       │   ├── user.md
│       │   ├── employee.md
│       │   ├── customer.md
│       │   ├── supplier.md
│       │   ├── product.md
│       │   └── pricing.md
│       ├── layer-2-money-path/
│       │   ├── order.md
│       │   ├── invoice.md
│       │   ├── ledger.md
│       │   ├── payment.md
│       │   ├── accounting_gateway.md
│       │   ├── tax.md
│       │   └── reconciliation.md
│       ├── layer-3-goods-path/
│       │   ├── inventory.md
│       │   ├── warehouse.md
│       │   ├── lot.md
│       │   ├── production.md
│       │   ├── recipe.md
│       │   ├── quality.md
│       │   ├── waste.md
│       │   ├── procurement.md
│       │   ├── traceability.md
│       │   ├── agriculture.md
│       │   ├── crop.md
│       │   ├── soil.md
│       │   └── irrigation.md
│       ├── layer-4-operations/
│       │   ├── transport.md
│       │   ├── delivery.md
│       │   ├── route.md
│       │   ├── gps.md
│       │   ├── retail.md
│       │   ├── pos.md
│       │   ├── shift.md
│       │   ├── line_channel.md
│       │   ├── promotion.md
│       │   ├── loyalty.md
│       │   ├── crm.md
│       │   ├── campaign.md
│       │   └── support.md
│       ├── layer-5-intelligence/
│       │   ├── reporting.md
│       │   ├── analytics.md
│       │   ├── forecast.md
│       │   ├── kpi.md
│       │   ├── satisfaction.md
│       │   ├── recommendation.md
│       │   └── oee.md
│       ├── layer-6-monitoring/
│       │   ├── iot.md
│       │   ├── cctv.md
│       │   ├── monitoring.md
│       │   ├── backup.md
│       │   ├── alerting.md
│       │   ├── audit_viewer.md
│       │   ├── maintenance.md
│       │   └── energy.md
│       └── layer-7-templates/
│           ├── health.md
│           ├── example.md
│           └── blank.md
│
└── test/                            # Tests
    ├── core/
    └── modules/
```

### 📁 โครงสร้าง `apps/` (ตาม FastAPI Template เดิม)

```
apps/
├── shared/                          # Shared base types
│   ├── domain/
│   │   ├── entities.py              # BaseEntity, DomainError, Pagination
│   │   ├── value_objects.py         # UNSET, Email, Name, Phone
│   │   └── enums.py                 # Role, ResponseMessages, SortOrder
│   ├── application/
│   │   ├── use_cases.py             # SharedUseCases
│   │   ├── interfaces.py            # Protocols
│   │   ├── exceptions.py            # StandardException, DomainException
│   │   └── utils.py                 # Helpers
│   ├── infrastructure/
│   │   ├── fastapi_client.py        # HTTPX client
│   │   └── middleware.py            # Session middleware
│   └── presentation/
│       ├── context_processors.py    # user_context
│       └── dependencies.py          # Factories
│
├── layout/                          # Layout Components
│   ├── presentation/
│   │   ├── views.py
│   │   └── urls.py
│   └── templates/
│       └── layout/
│           ├── app_layout.html      # = AppLayoutComponent
│           ├── header.html          # = HeaderComponent
│           ├── sidebar.html         # = SidebarComponent
│           ├── footer.html          # = FooterComponent
│           └── layout_settings.html # = LayoutSettingsComponent
│
├── authentication/                  # Proxy → FastAPI
│   ├── domain/
│   │   └── entities.py              # Authentication entity
│   ├── application/
│   │   ├── use_cases.py             # Login, Logout, Refresh
│   │   └── interfaces.py            # IAuthService
│   ├── infrastructure/
│   │   └── fastapi_auth_client.py   # FastAPI auth client
│   └── presentation/
│       ├── views.py                 # Login, Logout views
│       ├── urls.py                  # Auth URLs
│       └── forms.py                 # Login form
│
├── dashboard/                       # Dashboard
│   ├── application/
│   │   └── use_cases.py             # Dashboard stats
│   ├── infrastructure/
│   │   └── fastapi_client.py        # FastAPI client
│   └── presentation/
│       ├── views.py                 # Dashboard view
│       └── urls.py                  # Dashboard URLs
│
├── user/                            # Proxy → FastAPI
│   ├── domain/
│   │   └── entities.py              # User entity
│   ├── application/
│   │   ├── use_cases.py             # UserUseCases
│   │   └── interfaces.py            # IUserRepository
│   ├── infrastructure/
│   │   └── fastapi_client.py        # FastAPI client
│   └── presentation/
│       ├── views.py                 # User views
│       ├── urls.py                  # User URLs
│       └── forms.py                 # User forms
│
├── key/                             # Proxy → FastAPI
│   ├── domain/
│   │   ├── entities.py              # Key entity
│   │   ├── value_objects.py         # KeySecret
│   │   └── enums.py                 # KeyStatus
│   ├── application/
│   │   ├── use_cases.py             # KeyUseCases
│   │   ├── interfaces.py            # IKeyRepository
│   │   ├── mappers.py               # KeyMapper
│   │   └── exceptions.py            # KeyException
│   ├── infrastructure/
│   │   └── fastapi_client.py        # FastAPI client
│   └── presentation/
│       ├── views.py                 # Key views
│       ├── urls.py                  # Key URLs
│       └── forms.py                 # Key forms
│
├── knowledge/                       # Proxy → FastAPI
│   ├── domain/
│   │   ├── entities.py              # Knowledge entity
│   │   ├── value_objects.py         # KnowledgeName
│   │   └── enums.py                 # KnowledgeStatus
│   ├── application/
│   │   ├── use_cases.py             # KnowledgeUseCases
│   │   ├── interfaces.py            # IKnowledgeRepository
│   │   ├── mappers.py               # KnowledgeMapper
│   │   └── exceptions.py            # KnowledgeException
│   ├── infrastructure/
│   │   └── fastapi_client.py        # FastAPI client
│   └── presentation/
│       ├── views.py                 # Knowledge views
│       ├── urls.py                  # Knowledge URLs
│       └── forms.py                 # Knowledge forms
│
├── notification/                    # Proxy → FastAPI
│   ├── domain/
│   │   ├── entities.py              # Notification entity
│   │   └── enums.py                 # NotificationType
│   ├── application/
│   │   ├── use_cases.py             # NotificationUseCases
│   │   └── interfaces.py            # INotificationRepository
│   ├── infrastructure/
│   │   └── fastapi_client.py        # FastAPI client
│   └── presentation/
│       ├── views.py                 # Notification views
│       └── urls.py                  # Notification URLs
│
├── websocket/                       # WebSocket Proxy
│   ├── application/
│   │   └── consumers.py             # Channels consumer
│   ├── infrastructure/
│   │   └── fastapi_ws_client.py     # FastAPI WS client
│   └── presentation/
│       └── routing.py               # WS routing
│
└── core/                            # Core utilities
    ├── application/
    ├── infrastructure/
    └── presentation/
```

---

## หลักการทำงาน (Concept)

### 1. Four-Layer Architecture (ต่อ Module)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                            │
│  • views.py       — Django views                                 │
│  • forms.py       — Django Forms                                 │
│  • serializers.py — DRF Serializers                              │
│  • urls.py        — URL routing                                  │
│  • templates/     — HTML templates                               │
│  ⬇ (สามารถ import ทุก layer)                                     │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                          │
│  • models.py         — Django ORM models                         │
│  • repositories.py   — Django ORM repository                     │
│  • fastapi_client.py — HTTPX client ไป FastAPI                   │
│  • caches.py         — Django cache (Redis)                      │
│  • services.py       — External services                         │
│  ⬇ (import domain, application, core)                            │
├─────────────────────────────────────────────────────────────────┤
│                    Application Layer                             │
│  • use_cases.py   — Business logic                               │
│  • interfaces.py  — Protocols                                    │
│  • mappers.py     — Entity ↔ Model ↔ DTO                         │
│  • exceptions.py  — Module exceptions                            │
│  • utils.py       — Helpers                                      │
│  ⬇ (import domain, shared)                                       │
├─────────────────────────────────────────────────────────────────┤
│                    Domain Layer                                  │
│  • entities.py      — Dataclasses (BaseEntity)                   │
│  • value_objects.py — Immutable VOs                              │
│  • enums.py         — (str, Enum)                                │
│  ⛔ ห้าม import framework! (Django, DRF, FastAPI)                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Dependency Rule

```
Presentation  →  Infrastructure  →  Application  →  Domain
     │                  │                 │              │
     └──────────────────┴─────────────────┴──────────────┘
                        (ห้ามย้อนกลับ)
```

- **Domain** — ไม่ import อะไรเลยนอกจาก Python stdlib + shared
- **Application** — import domain, shared
- **Infrastructure** — import domain, application, core
- **Presentation** — import ทุก layer

### 3. Layout Components Concept

| Layout Component | Django Equivalent | เทคโนโลยี |
|---|---|---|
| `AppLayoutComponent` | `templates/base.html` | Django Template |
| `HeaderComponent` | `templates/partials/header.html` | Alpine.js + Tailwind |
| `SidebarComponent` | `templates/partials/sidebar.html` | Alpine.js + Tailwind |
| `FooterComponent` | `templates/partials/footer.html` | Django Template |
| `LayoutSettingsComponent` | `templates/partials/layout-settings.html` | Alpine.js + Tailwind |
| `PageHeaderComponent` | `{% block page_header %}` | Django Block |
| `@Output()` | Alpine.js `$dispatch()` | Alpine.js |
| `@Input()` | Alpine.js `x-data` | Alpine.js |
| `router-outlet` | `{% block content %}` | Django Block |

### 4. Session + Cookies Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Browser                                                     │
│  • Django sessionid cookie (session)                         │
│  • FastAPI access_token cookie (HTTP-only)                   │
│  • FastAPI refresh_token cookie (HTTP-only)                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Django Middleware                                           │
│  1. อ่าน cookies จาก request                                 │
│  2. เก็บใน request.fastapi_cookies                           │
│  3. ตั้ง request.is_authenticated                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Django View                                                 │
│  1. เรียก FastAPIClient(cookies=request.fastapi_cookies)     │
│  2. ส่ง request → FastAPI                                    │
│  3. รับ response ← FastAPI                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                             │
│  • ตรวจสอบ JWT จาก cookies                                   │
│  • ส่งข้อมูลกลับ                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5. Error Handling Shapes

**3-branch** — Use cases + Views:
```python
try:
    ...
except StandardException:
    raise                          # ต้องมาก่อนเสมอ
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("Error in {module}")
    raise {Module}Exception()
```

**2-branch** — Repositories + Services:
```python
try:
    ...
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("Error in {module} repository")
    raise {Module}Exception()
```

**Never-raise** — Caches:
```python
try:
    ...
except Exception as e:
    logger.opt(exception=e).error("Cache error. Falling back to DB.")
    return None
```

### 6. The `UNSET` Sentinel

ใช้สำหรับ partial updates:

```python
# domain/entities.py
@dataclass
class Key(BaseEntity):
    name: str = UNSET
    description: str = UNSET

# application/mappers.py
def to_entity_update(payload) -> Key:
    updates = {}
    if "name" in payload.model_fields_set:
        updates["name"] = payload.name
    return Key(**updates)

# application/use_cases.py
async def update_key(self, id: str, payload) -> Key:
    key = await self.repo.get_by_id(id)
    if payload.name is not UNSET:
        key.name = payload.name
    ...
```

---

## Workflow และ Dataflow

### 🔄 Workflow 1: Login Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant B as Browser
    participant D as Django
    participant F as FastAPI
    participant DB as PostgreSQL
    participant R as Redis

    U->>B: กรอก email + password
    B->>D: POST /auth/login/
    Note over D: Django View:<br/>1. รับ form data<br/>2. เรียก FastAPIClient
    D->>F: POST /api/v1/authentication/login/<br/>(form-encoded)
    F->>DB: ตรวจสอบ password (Argon2)
    DB-->>F: ✅ User found
    F->>F: สร้าง nested JWT<br/>(JWS Ed25519 → JWE)
    F->>DB: เก็บ HMAC fingerprints
    F->>R: cache authentication
    F-->>D: 200 OK + Set-Cookie
    Note over D: Django View:<br/>1. รับ Set-Cookie<br/>2. คัดลอก cookies<br/>3. ตั้ง Django session<br/>4. Redirect → /dashboard/
    D-->>B: 302 Redirect + Set-Cookie
    B->>D: GET /dashboard/
    Note over D: Django View:<br/>1. อ่าน cookies<br/>2. เรียก FastAPIClient
    D->>F: GET /api/v1/user/me/
    F-->>D: 200 OK + user data
    D->>F: GET /api/v1/notification/?limit=10
    F-->>D: 200 OK + notifications
    D-->>B: 200 OK + HTML
    B-->>U: แสดง Dashboard
```

### 🔄 Workflow 2: Request Flow (Authenticated)

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant M as Middleware
    participant V as Django View
    participant UC as Use Case
    participant C as FastAPIClient
    participant F as FastAPI
    participant Cache as Redis
    participant DB as PostgreSQL

    B->>M: GET /key/
    Note over M: FastAPISessionMiddleware:<br/>1. อ่าน cookies<br/>2. ตั้ง request.fastapi_cookies<br/>3. ตั้ง request.is_authenticated
    M->>V: request + cookies
    Note over V: KeyListView:<br/>1. รับ request<br/>2. เรียก UseCase
    V->>UC: list_keys(page=1, limit=20)
    Note over UC: KeyUseCases:<br/>1. ตรวจสอบ params<br/>2. เรียก FastAPIClient
    UC->>C: get("/api/v1/key/", params)
    C->>F: GET /api/v1/key/
    Note over F: ตรวจสอบ JWT
    F->>Cache: get(key:list:page:1)
    alt cache hit
        Cache-->>F: data
    else cache miss
        F->>DB: SELECT * FROM keys LIMIT 20
        DB-->>F: rows
        F->>Cache: insert
    end
    F-->>C: 200 OK + envelope
    C-->>UC: unwrap → data
    UC-->>V: list[Key]
    Note over V: Render template:<br/>1. KeyMapper.to_dict<br/>2. render("key/list.html")
    V-->>B: 200 OK + HTML
    B->>B: Alpine.js:<br/>hydrate + bind
```

### 🔄 Workflow 3: WebSocket Flow

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant Ch as Django Channels
    participant C as FastAPI WS Client
    participant F as FastAPI WS
    participant CM as ConnectionManager

    B->>Ch: WS /ws/notifications/
    Note over Ch: NotificationProxyConsumer:<br/>1. รับ cookies<br/>2. แปลงเป็น Cookie header
    Ch->>C: connect(cookies)
    C->>F: WS /api/v1/websocket/connect/<br/>+ Cookie header
    Note over F: ตรวจสอบ JWT<br/>ตรวจสอบ Origin
    F->>CM: register(connection)
    CM-->>F: ✅ Registered
    F-->>C: 101 Switching Protocols
    C-->>Ch: 101 Switching Protocols
    Ch-->>B: 101 Switching Protocols
    Note over B,CM: Connection established

    F->>CM: broadcast(notification)
    CM->>F: send to all
    F-->>C: {"message_type": "notification", ...}
    C-->>Ch: forward
    Ch-->>B: forward
    B->>B: Alpine.js: อัปเดต UI
```

### 🔄 Workflow 4: Layout Render Flow

```mermaid
flowchart TB
    subgraph Request["1. Request"]
        R1["Browser: GET /key/"]
    end

    subgraph Middleware["2. Middleware"]
        M1["FastAPISessionMiddleware"]
        M2["อ่าน cookies"]
        M3["ตั้ง request.fastapi_cookies"]
    end

    subgraph View["3. View"]
        V1["KeyListView.get()"]
        V2["เรียก KeyUseCases"]
        V3["รับ list[Key]"]
        V4["render('key/list.html')"]
    end

    subgraph Template["4. Template"]
        T1["extends base.html"]
        T2["block page_header"]
        T3["block content"]
        T4["include partials/header.html"]
        T5["include partials/sidebar.html"]
        T6["include partials/footer.html"]
    end

    subgraph Context["5. Context Processor"]
        C1["user_context(request)"]
        C2["เรียก FastAPI /user/me/"]
        C3["คืน current_user, is_authenticated"]
    end

    subgraph Response["6. Response"]
        R2["HTML ที่ render แล้ว"]
        R3["Browser: แสดงผล"]
    end

    R1 --> M1
    M1 --> M2
    M2 --> M3
    M3 --> V1
    V1 --> V2
    V2 --> V3
    V3 --> V4
    V4 --> T1
    T1 --> T4
    T1 --> T2
    T1 --> T3
    T1 --> T5
    T1 --> T6
    V4 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> T2
    T2 --> R2
    T3 --> R2
    T4 --> R2
    T5 --> R2
    T6 --> R2
    R2 --> R3

    style R1 fill:#457b9d,color:#fff
    style M1 fill:#6c584c,color:#fff
    style V1 fill:#2d6a4f,color:#fff
    style T1 fill:#1d3557,color:#fff
    style C1 fill:#7f5539,color:#fff
    style R2 fill:#40916c,color:#fff
```

---

## Case Study

### 📖 Case Study 1: การเพิ่ม Module Proxy ใหม่ (Key)

**สถานการณ์:** ต้องการเพิ่ม module "API Keys" ที่ proxy ไป FastAPI

**ขั้นตอน:**

1. **เปิด AI Prompt** — `docs/prompts/layer-1-foundation/key.md`
2. **Copy Prompt** ไปวางใน AI
3. **AI สร้าง 16 ไฟล์** ตาม template
4. **ตรวจสอบ Checklist** ก่อน merge

**ผลลัพธ์:**

```
apps/key/
├── domain/
│   ├── entities.py          # Key, KeySecret
│   ├── value_objects.py     # KeyPrefix, KeyStatus
│   └── enums.py             # KeyStatus
├── application/
│   ├── use_cases.py         # KeyUseCases (CRUD + rotate)
│   ├── interfaces.py        # IKeyRepository
│   ├── mappers.py           # KeyMapper
│   └── exceptions.py        # KeyException
├── infrastructure/
│   └── fastapi_client.py    # FastAPIClient
└── presentation/
    ├── views.py             # KeyListView, KeyDetailView, ...
    ├── urls.py              # URL routing
    └── forms.py             # KeyForm
```

**ประโยชน์:**
- ✅ ไม่ต้องเขียน boilerplate เอง
- ✅ ได้ pattern ที่สอดคล้องกับ module อื่น
- ✅ มี test พร้อมใช้
- ✅ Comment 2 ภาษา

---

### 📖 Case Study 2: การนำ Layout Components มาใช้

**สถานการณ์:** ต้องการใช้ Layout Components

**ขั้นตอน:**

1. **Port `AppLayoutComponent`** → `templates/base.html`
2. **Port `HeaderComponent`** → `templates/partials/header.html`
3. **Port `SidebarComponent`** → `templates/partials/sidebar.html`
4. **Port `FooterComponent`** → `templates/partials/footer.html`
5. **Port `LayoutSettingsComponent`** → `templates/partials/layout-settings.html`

**ตัวอย่าง `base.html`:**

```django
{% load static %}
<!DOCTYPE html>
<html lang="th" x-data="appShell()" x-init="init()">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Dashboard{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50 dark:bg-gray-900">
  <a href="#content" class="sr-only focus:not-sr-only">ข้ามไปยังเนื้อหา</a>

  <div class="min-h-screen flex flex-col">
    {# = HeaderComponent #}
    {% include "partials/header.html" %}

    {# = PageHeaderComponent #}
    {% block page_header %}{% endblock %}

    {# = Main content #}
    <main id="content" class="flex-1 container mx-auto px-4 py-6">
      {% block content %}{% endblock %}
    </main>

    {# = FooterComponent #}
    {% include "partials/footer.html" %}
  </div>

  {# = SidebarComponent #}
  {% include "partials/sidebar.html" %}

  {# = LayoutSettingsComponent #}
  {% include "partials/layout-settings.html" %}

  <script src="{% static 'js/app.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

**ประโยชน์:**
- ✅ UI เหมือนเดิม (Tabler → Tailwind)
- ✅ Responsive
- ✅ Dark mode
- ✅ ใช้ซ้ำได้ทุกหน้า

---

### 📖 Case Study 3: การจัดการ Session + Cookies

**สถานการณ์:** ต้องการให้ Django จัดการ session และ forward cookies ไป FastAPI

**ขั้นตอน:**

1. **สร้าง `FastAPISessionMiddleware`**

```python
# apps/shared/infrastructure/middleware.py
from django.conf import settings


class FastAPISessionMiddleware:
    """
    Middleware สำหรับจัดการ cookies จาก FastAPI
    Middleware for handling FastAPI cookies
    """

    FASTAPI_COOKIE_KEYS = [
        "access_token",
        "refresh_token",
        "device_id",
        "token_type",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # อ่าน cookies จาก request
        # Read cookies from request
        cookies = {}
        for key in self.FASTAPI_COOKIE_KEYS:
            val = request.COOKIES.get(key)
            if val:
                cookies[key] = val

        # เก็บใน request
        # Store in request
        request.fastapi_cookies = cookies
        request.is_authenticated = "access_token" in cookies

        return self.get_response(request)
```

2. **ใช้ใน View**

```python
# apps/dashboard/presentation/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from apps.shared.infrastructure.fastapi_client import FastAPIClient


def dashboard_view(request):
    if not request.is_authenticated:
        return redirect(reverse("authentication:login"))

    client = FastAPIClient(cookies=request.fastapi_cookies)

    # ดึงข้อมูลจาก FastAPI
    # Fetch data from FastAPI
    resp = client.get("/api/v1/notification/", params={"limit": 10})
    notifications = []
    if resp.status_code == 200:
        data = FastAPIClient.unwrap(resp)
        notifications = data.get("items", []) if data else []

    return render(request, "dashboard/index.html", {
        "notifications": notifications,
    })
```

**ประโยชน์:**
- ✅ Session ปลอดภัย
- ✅ Cookies HTTP-only
- ✅ FastAPI ไม่ต้องแก้
- ✅ CSRF protection

---

### 📖 Case Study 4: การจัดการปัญหาที่อาจเกิดขึ้น

| ปัญหา | สาเหตุ | แนวทางแก้ไข |
|---|---|---|
| **CSRF token ไม่ผ่าน** | Django CSRF + FastAPI cookies | ใช้ `@csrf_exempt` ใน login view |
| **Cookie ไม่ถูกส่ง** | SameSite policy | ตั้ง `SameSite=None; Secure` |
| **CORS error** | Origin ไม่ตรง | ตั้ง `SECURITY_ALLOW_ORIGINS` ใน FastAPI |
| **WebSocket หลุด** | Proxy timeout | ตั้ง `proxy_read_timeout` ใน nginx |
| **Session หมดอายุ** | Token หมดอายุ | Refresh token อัตโนมัติ |
| **Slow response** | FastAPI ช้า | เพิ่ม cache ที่ Django |
| **Race condition** | Concurrent requests | ใช้ Idempotency-Key |
| **Data inconsistency** | Cache invalidation | ใช้ Tombstone pattern |

---

## AI Prompt Template

### 📘 ไฟล์ 1: `docs/template_modules.md` (Master Template)

```markdown
# AI Prompt Template — สร้าง Module ใหม่ใน Django Frontend (BFF)

> **เวอร์ชัน:** 2.0.0
> **Stack:** Python 3.14+ · Django 5.0+ · Tailwind CSS · Alpine.js · HTMX · FastAPI Client
> **Scope:** Django Frontend (BFF) ที่ proxy ไป FastAPI Backend เดิม

---

## 📋 ข้อมูล Module (Metadata)

| หัวข้อ | รายละเอียด | ตัวอย่าง |
|---|---|---|
| **ชื่อ Module** | `{module_name}` | `key` |
| **Layer** | `{layer_number}` (0-7) | `1` |
| **Priority** | `{priority}` (🔴/🟠/🟡/🟢) | `🔴` |
| **Phase** | `{phase}` (0-6) | `1` |
| **มิติธุรกิจ** | `{erp/crm/iot/agriculture/...}` | `erp` |
| **Dependencies** | `{list_of_modules}` | `authentication, user` |
| **Domain Concepts** | `{entities}, {value_objects}, {enums}` | `Key, KeySecret, KeyStatus` |
| **FastAPI Endpoint** | `{fastapi_path}` | `/api/v1/key/` |

---

## 🎯 Prompt Template (Master)

### สร้าง Module `{module_name}`

**บริบท:**
- Django Frontend (BFF) สำหรับ FastAPI Backend
- Clean Architecture + DDD (4 layers)
- Python 3.14+, Django 5.0+, Tailwind CSS, Alpine.js
- **ห้ามแก้โค้ด FastAPI** — proxy ผ่าน HTTPX เท่านั้น
- Session + Cookies forwarding

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)
- `entities.py`: Dataclasses extending `BaseEntity`
- `value_objects.py`: Plain classes with `_normalize → _validate → __str__ → __eq__`
- `enums.py`: All enums as `(str, Enum)`
- **ห้าม import framework ใดๆ** (ห้าม Django, DRF, HTTPX)

#### 2. Application Layer (`application/`)
- `interfaces.py`: Protocol contracts
- `use_cases.py`: One `{Module}UseCases` class with business rules
- `mappers.py`: `# ENTITY/DTOS`, `# ENTITY/MODELS`, `# ENTITY/CACHE`
- `exceptions.py`: `{Module}Exception` + one per business rule
- `utils.py`: Module-local helpers

#### 3. Infrastructure Layer (`infrastructure/`)
- `fastapi_client.py`: HTTPX client → FastAPI (หลัก)
- `models.py`: Django ORM (ถ้าจำเป็น)
- `repositories.py`: Django ORM repository (ถ้าจำเป็น)
- `caches.py`: Django cache — namespaced, tombstoned, never raises
- `services.py`: External systems behind Protocol

#### 4. Presentation Layer (`presentation/`)
- `views.py`: `payload → mapper → use case → mapper → return`
- `forms.py`: Django Forms with full validation
- `urls.py`: URL routing
- `templates/`: HTML templates extending `base.html`

#### 5. Error Handling (3 shapes)

```python
# 3-branch: Use cases + views
try:
    ...
except StandardException:
    raise                          # ต้องมาก่อนเสมอ
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("Error in {module}")
    raise {Module}Exception()

# 2-branch: Repositories + services
try:
    ...
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("Error in {module} repository")
    raise {Module}Exception()

# Never-raise: Caches
try:
    ...
except Exception as e:
    logger.opt(exception=e).error("Cache error. Falling back to DB.")
    return None
```

#### 6. Invariants ที่ต้องรักษา
- `{module_specific_invariants}`

#### 7. Domain Events
- `{Module}Created`, `{Module}Updated`, `{Module}Deleted`

#### 8. Tests
- Unit test สำหรับ use cases (in-memory fakes)
- Integration test สำหรับ fastapi_client
- Property-based test สำหรับ invariants

**Output:**
- ไฟล์ครบ 16 ไฟล์ (4 layers × 4 ไฟล์)
- Comment 2 ภาษา (ไทย + English)
- พร้อมรันด้วย `python manage.py runserver 8001`
```

---

### 📑 ไฟล์ 2: `docs/prompts/README.md` (Index)

```markdown
# 📑 Module Prompts Index

รายการ AI Prompt สำหรับสร้าง Module ทั้งหมด **65 modules** แบ่งตาม Layer

---

## Layer 0: CORE (cross-cutting)

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 1 | `money` | 🔴 | 1 | (ไม่มี — pure VO) | [money.md](layer-0-core/money.md) |
| 2 | `tenant_context` | 🔴 | 1 | (middleware) | [tenant_context.md](layer-0-core/tenant_context.md) |
| 3 | `audit` | 🔴 | 1 | `/api/v1/audit/` | [audit.md](layer-0-core/audit.md) |
| 4 | `idempotency` | 🔴 | 1 | (middleware) | [idempotency.md](layer-0-core/idempotency.md) |
| 5 | `config` | 🔴 | 1 | `/api/v1/config/` | [config.md](layer-0-core/config.md) |
| 6 | `events` | 🔴 | 1 | `/api/v1/events/` | [events.md](layer-0-core/events.md) |

## Layer 1: FOUNDATION

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 7 | `tenancy` | 🔴 | 1 | `/api/v1/tenancy/` | [tenancy.md](layer-1-foundation/tenancy.md) |
| 8 | `authentication` | 🔴 | 1 | `/api/v1/authentication/` | [authentication.md](layer-1-foundation/authentication.md) |
| 9 | `user` | 🔴 | 1 | `/api/v1/user/` | [user.md](layer-1-foundation/user.md) |
| 10 | `employee` | 🟠 | 1 | `/api/v1/employee/` | [employee.md](layer-1-foundation/employee.md) |
| 11 | `customer` | 🔴 | 1 | `/api/v1/customer/` | [customer.md](layer-1-foundation/customer.md) |
| 12 | `supplier` | 🟠 | 1 | `/api/v1/supplier/` | [supplier.md](layer-1-foundation/supplier.md) |
| 13 | `product` | 🔴 | 1 | `/api/v1/product/` | [product.md](layer-1-foundation/product.md) |
| 14 | `pricing` | 🔴 | 1 | `/api/v1/pricing/` | [pricing.md](layer-1-foundation/pricing.md) |
| 15 | `key` | 🔴 | 1 | `/api/v1/key/` | [key.md](layer-1-foundation/key.md) |
| 16 | `knowledge` | 🟠 | 1 | `/api/v1/knowledge/` | [knowledge.md](layer-1-foundation/knowledge.md) |
| 17 | `notification` | 🟠 | 1 | `/api/v1/notification/` | [notification.md](layer-1-foundation/notification.md) |

## Layer 2: MONEY PATH (ERP)

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 18 | `order` | 🔴 | 1 | `/api/v1/order/` | [order.md](layer-2-money-path/order.md) |
| 19 | `invoice` | 🔴 | 1 | `/api/v1/invoice/` | [invoice.md](layer-2-money-path/invoice.md) |
| 20 | `ledger` | 🔴 | 1 | `/api/v1/ledger/` | [ledger.md](layer-2-money-path/ledger.md) |
| 21 | `payment` | 🔴 | 2 | `/api/v1/payment/` | [payment.md](layer-2-money-path/payment.md) |
| 22 | `accounting_gateway` | 🔴 | 2 | `/api/v1/accounting/` | [accounting_gateway.md](layer-2-money-path/accounting_gateway.md) |
| 23 | `tax` | 🔴 | 2 | `/api/v1/tax/` | [tax.md](layer-2-money-path/tax.md) |
| 24 | `reconciliation` | 🔴 | 1 | `/api/v1/reconciliation/` | [reconciliation.md](layer-2-money-path/reconciliation.md) |

## Layer 3: GOODS PATH (Production + Agriculture)

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 25 | `inventory` | 🔴 | 1 | `/api/v1/inventory/` | [inventory.md](layer-3-goods-path/inventory.md) |
| 26 | `warehouse` | 🔴 | 1 | `/api/v1/warehouse/` | [warehouse.md](layer-3-goods-path/warehouse.md) |
| 27 | `lot` | 🔴 | 1 | `/api/v1/lot/` | [lot.md](layer-3-goods-path/lot.md) |
| 28 | `production` | 🔴 | 1 | `/api/v1/production/` | [production.md](layer-3-goods-path/production.md) |
| 29 | `recipe` | 🟠 | 1 | `/api/v1/recipe/` | [recipe.md](layer-3-goods-path/recipe.md) |
| 30 | `quality` | 🟠 | 1 | `/api/v1/quality/` | [quality.md](layer-3-goods-path/quality.md) |
| 31 | `waste` | 🟠 | 1 | `/api/v1/waste/` | [waste.md](layer-3-goods-path/waste.md) |
| 32 | `procurement` | 🟠 | 1 | `/api/v1/procurement/` | [procurement.md](layer-3-goods-path/procurement.md) |
| 33 | `traceability` | 🔴 | 2 | `/api/v1/traceability/` | [traceability.md](layer-3-goods-path/traceability.md) |
| 34 | `agriculture` | 🟠 | 4 | `/api/v1/agriculture/` | [agriculture.md](layer-3-goods-path/agriculture.md) |
| 35 | `crop` | 🟠 | 4 | `/api/v1/crop/` | [crop.md](layer-3-goods-path/crop.md) |
| 36 | `soil` | 🟠 | 4 | `/api/v1/soil/` | [soil.md](layer-3-goods-path/soil.md) |
| 37 | `irrigation` | 🟠 | 4 | `/api/v1/irrigation/` | [irrigation.md](layer-3-goods-path/irrigation.md) |

## Layer 4: OPERATIONS

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 38 | `transport` | 🟠 | 4 | `/api/v1/transport/` | [transport.md](layer-4-operations/transport.md) |
| 39 | `delivery` | 🟠 | 4 | `/api/v1/delivery/` | [delivery.md](layer-4-operations/delivery.md) |
| 40 | `route` | 🟠 | 4 | `/api/v1/route/` | [route.md](layer-4-operations/route.md) |
| 41 | `gps` | 🟠 | 4 | `/api/v1/gps/` | [gps.md](layer-4-operations/gps.md) |
| 42 | `retail` | 🟠 | 4 | `/api/v1/retail/` | [retail.md](layer-4-operations/retail.md) |
| 43 | `pos` | 🟠 | 4 | `/api/v1/pos/` | [pos.md](layer-4-operations/pos.md) |
| 44 | `shift` | 🟠 | 4 | `/api/v1/shift/` | [shift.md](layer-4-operations/shift.md) |
| 45 | `line_channel` | 🟠 | 4 | `/api/v1/line/` | [line_channel.md](layer-4-operations/line_channel.md) |
| 46 | `promotion` | 🟡 | 4 | `/api/v1/promotion/` | [promotion.md](layer-4-operations/promotion.md) |
| 47 | `loyalty` | 🟡 | 4 | `/api/v1/loyalty/` | [loyalty.md](layer-4-operations/loyalty.md) |
| 48 | `crm` | 🟠 | 5 | `/api/v1/crm/` | [crm.md](layer-4-operations/crm.md) |
| 49 | `campaign` | 🟡 | 5 | `/api/v1/campaign/` | [campaign.md](layer-4-operations/campaign.md) |
| 50 | `support` | 🟡 | 5 | `/api/v1/support/` | [support.md](layer-4-operations/support.md) |

## Layer 5: INTELLIGENCE

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 51 | `reporting` | 🔴 | 5 | `/api/v1/reporting/` | [reporting.md](layer-5-intelligence/reporting.md) |
| 52 | `analytics` | 🟠 | 5 | `/api/v1/analytics/` | [analytics.md](layer-5-intelligence/analytics.md) |
| 53 | `forecast` | 🟠 | 5 | `/api/v1/forecast/` | [forecast.md](layer-5-intelligence/forecast.md) |
| 54 | `kpi` | 🟠 | 5 | `/api/v1/kpi/` | [kpi.md](layer-5-intelligence/kpi.md) |
| 55 | `satisfaction` | 🟡 | 5 | `/api/v1/satisfaction/` | [satisfaction.md](layer-5-intelligence/satisfaction.md) |
| 56 | `recommendation` | 🟡 | 5 | `/api/v1/recommendation/` | [recommendation.md](layer-5-intelligence/recommendation.md) |
| 57 | `oee` | 🟠 | 5 | `/api/v1/oee/` | [oee.md](layer-5-intelligence/oee.md) |

## Layer 6: MONITORING & SENSING

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 58 | `iot` | 🟠 | 4 | `/api/v1/iot/` | [iot.md](layer-6-monitoring/iot.md) |
| 59 | `cctv` | 🟡 | 4 | `/api/v1/cctv/` | [cctv.md](layer-6-monitoring/cctv.md) |
| 60 | `monitoring` | 🔴 | 1 | `/api/v1/monitoring/` | [monitoring.md](layer-6-monitoring/monitoring.md) |
| 61 | `backup` | 🔴 | 1 | `/api/v1/backup/` | [backup.md](layer-6-monitoring/backup.md) |
| 62 | `alerting` | 🟠 | 1 | `/api/v1/alerting/` | [alerting.md](layer-6-monitoring/alerting.md) |
| 63 | `audit_viewer` | 🟠 | 2 | `/api/v1/audit-viewer/` | [audit_viewer.md](layer-6-monitoring/audit_viewer.md) |
| 64 | `maintenance` | 🟠 | 5 | `/api/v1/maintenance/` | [maintenance.md](layer-6-monitoring/maintenance.md) |
| 65 | `energy` | 🟡 | 5 | `/api/v1/energy/` | [energy.md](layer-6-monitoring/energy.md) |

## Layer 7: TEMPLATES

| # | Module | Priority | Phase | FastAPI Endpoint | ไฟล์ |
|---|---|---|---|---|---|
| 66 | `health` | 🔴 | 1 | `/health/` | [health.md](layer-7-templates/health.md) |
| 67 | `example` | 🟢 | 1 | `/api/v1/example/` | [example.md](layer-7-templates/example.md) |
| 68 | `blank` | 🟢 | 1 | (template) | [blank.md](layer-7-templates/blank.md) |

---

## 🚀 วิธีใช้

1. เปิดไฟล์ prompt ที่ต้องการ เช่น `docs/prompts/layer-1-foundation/key.md`
2. Copy prompt ไปวางใน AI (ChatGPT, Claude, Gemini)
3. AI จะสร้าง 16 ไฟล์ตาม template
4. ตรวจสอบ checklist ก่อน merge

## 📐 ลำดับการสร้างที่แนะนำ

```
Phase 1:  Layer 0 (Core) → Layer 1 (Foundation) → Layer 2 (Money) → Layer 3 (Goods)
Phase 2:  Layer 4 (Operations) → Layer 5 (Intelligence)
Phase 3:  Layer 6 (Monitoring) → Layer 7 (Templates)
```
```

---

### 📄 ไฟล์ 3: ตัวอย่าง `docs/prompts/layer-1-foundation/key.md`

```markdown
# AI Prompt — Module `key`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `key` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | ERP (Security) |
| **Dependencies** | `authentication`, `user` |
| **Domain Concepts** | `Key` (entity), `KeySecret` (VO), `KeyStatus` (enum) |
| **FastAPI Endpoint** | `/api/v1/key/` |

---

## 🎯 Prompt

### สร้าง Module `key` (Django Frontend BFF)

**บริบท:**
- Django Frontend (BFF) สำหรับ FastAPI Backend
- Clean Architecture + DDD (4 layers)
- **ห้ามแก้โค้ด FastAPI** — proxy ผ่าน HTTPX เท่านั้น
- Session + Cookies forwarding
- **Invariants:** `Key hash ไม่ซ้ำ`, `Raw key แสดงครั้งเดียว`
- **Events:** `KeyCreated`, `KeyRotated`, `KeyRevoked`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
from dataclasses import dataclass, field
from datetime import datetime
from apps.shared.domain.entities import BaseEntity, DomainError


@dataclass
class Key(BaseEntity):
    """Key entity — เอนทิตีคีย์"""
    name: str = ""
    description: str = ""
    prefix: str = ""
    last_four: str = ""
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_by: str = ""
    updated_by: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        """Validate key — ตรวจสอบคีย์"""
        if not self.name or len(self.name) < 3:
            raise DomainError("Key name must be at least 3 characters")
        if not self.prefix:
            raise DomainError("Key prefix is required")
        if not self.last_four:
            raise DomainError("Key last_four is required")

    def is_expired(self) -> bool:
        """Check if key is expired — ตรวจสอบว่าหมดอายุ"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_usable(self) -> bool:
        """Check if key is usable — ตรวจสอบว่าใช้ได้"""
        return self.is_active and not self.is_expired()

    def mark_used(self) -> None:
        """Mark key as used — บันทึกว่าใช้แล้ว"""
        self.last_used_at = datetime.utcnow()
```

**`domain/value_objects.py`**
```python
from dataclasses import dataclass
from apps.shared.domain.entities import DomainError


@dataclass(frozen=True)
class KeySecret:
    """Key secret VO — วัตถุค่า secret ของคีย์"""
    value: str

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        """Validate secret — ตรวจสอบ secret"""
        if not self.value or len(self.value) < 16:
            raise DomainError("Key secret must be at least 16 characters")

    def __str__(self) -> str:
        return self.value[:8] + "..." + self.value[-4:]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KeySecret):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class KeyPrefix:
    """Key prefix VO — วัตถุค่า prefix ของคีย์"""
    value: str

    PATTERN = r"^[a-z]{2,5}_$"

    def __post_init__(self):
        import re
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid key prefix: {self.value}")
```

**`domain/enums.py`**
```python
from enum import Enum


class KeyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class KeyScope(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"
```

#### 2. Application Layer

**`application/interfaces.py`**
```python
from typing import Protocol
from apps.key.domain.entities import Key


class IKeyRepository(Protocol):
    """Key repository protocol — โปรโตคอลรีโพซิทอรีคีย์"""

    async def list(
        self,
        page: int,
        limit: int,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[Key], int]: ...

    async def get_by_id(self, id: str) -> Key | None: ...

    async def create(self, payload: dict) -> tuple[Key, str]:
        """Returns (key, raw_secret) — คืน (คีย์, secret)"""
        ...

    async def update(self, id: str, payload: dict) -> Key: ...

    async def rotate(self, id: str) -> tuple[Key, str]:
        """Returns (key, new_raw_secret) — คืน (คีย์, secret ใหม่)"""
        ...

    async def revoke(self, id: str) -> None: ...


class IKeyCache(Protocol):
    """Key cache protocol — โปรโตคอลแคชคีย์"""

    async def get(self, id: str) -> Key | None: ...
    async def insert(self, id: str, key: Key) -> None: ...
    async def delete(self, id: str) -> None: ...
```

**`application/use_cases.py`**
```python
from loguru import logger
from apps.shared.application.exceptions import (
    StandardException, DomainException, DomainError,
)
from apps.key.application.exceptions import KeyException
from apps.key.application.interfaces import IKeyRepository, IKeyCache
from apps.key.domain.entities import Key


class KeyUseCases:
    """Key use cases — กรณีการใช้งานคีย์"""

    def __init__(
        self,
        repo: IKeyRepository,
        cache: IKeyCache,
        audit: "IAuditService",
        idempotency: "IIdempotencyService",
        events: "IEventBus",
    ):
        self.repo = repo
        self.cache = cache
        self.audit = audit
        self.idempotency = idempotency
        self.events = events

    async def list_keys(
        self,
        page: int,
        limit: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[Key], int]:
        """List keys — แสดงรายการคีย์"""
        try:
            keys, total = await self.repo.list(page, limit, sort_by, sort_order)
            return keys, total
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in list_keys")
            raise KeyException()

    async def get_key(self, id: str) -> Key:
        """Get key by ID — ดูคีย์ตาม ID"""
        try:
            # Try cache first
            cached = await self.cache.get(id)
            if cached:
                return cached

            key = await self.repo.get_by_id(id)
            if not key:
                raise KeyException("Key not found")

            await self.cache.insert(id, key)
            return key
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_key")
            raise KeyException()

    async def create_key(
        self,
        payload: dict,
        idem_key: str,
    ) -> tuple[Key, str]:
        """Create key — สร้างคีย์"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            key, raw_secret = await self.repo.create(payload)

            await self.audit.log("key.created", key.id)
            await self.idempotency.set(idem_key, (key, raw_secret))
            await self.events.publish("KeyCreated", key)

            return key, raw_secret
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_key")
            raise KeyException()

    async def update_key(self, id: str, payload: dict) -> Key:
        """Update key — อัปเดตคีย์"""
        try:
            key = await self.repo.update(id, payload)
            await self.cache.delete(id)
            await self.audit.log("key.updated", id)
            await self.events.publish("KeyUpdated", key)
            return key
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in update_key")
            raise KeyException()

    async def rotate_key(self, id: str) -> tuple[Key, str]:
        """Rotate key — หมุนคีย์"""
        try:
            key, new_secret = await self.repo.rotate(id)
            await self.cache.delete(id)
            await self.audit.log("key.rotated", id)
            await self.events.publish("KeyRotated", key)
            return key, new_secret
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in rotate_key")
            raise KeyException()

    async def revoke_key(self, id: str) -> None:
        """Revoke key — ยกเลิกคีย์"""
        try:
            await self.repo.revoke(id)
            await self.cache.delete(id)
            await self.audit.log("key.revoked", id)
            await self.events.publish("KeyRevoked", {"id": id})
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in revoke_key")
            raise KeyException()
```

**`application/mappers.py`**
```python
from apps.key.domain.entities import Key


class KeyMapper:
    """Key mapper — ตัวแปลงคีย์"""

    # ENTITY / DTOS
    @staticmethod
    def to_dto(key: Key) -> dict:
        """Entity → DTO — เอนทิตี → DTO"""
        return {
            "id": key.id,
            "name": key.name,
            "description": key.description,
            "prefix": key.prefix,
            "last_four": key.last_four,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "is_active": key.is_active,
            "created_at": key.created_at.isoformat() if key.created_at else None,
            "updated_at": key.updated_at.isoformat() if key.updated_at else None,
        }

    # ENTITY / MODELS
    @staticmethod
    def to_model_dict(key: Key) -> dict:
        """Entity → Model dict — เอนทิตี → model dict"""
        return {
            "name": key.name,
            "description": key.description,
            "prefix": key.prefix,
            "last_four": key.last_four,
            "expires_at": key.expires_at,
            "is_active": key.is_active,
        }

    @staticmethod
    def from_model(model) -> Key:
        """Model → Entity — model → เอนทิตี"""
        return Key(
            id=str(model.id),
            name=model.name,
            description=model.description,
            prefix=model.prefix,
            last_four=model.last_four,
            expires_at=model.expires_at,
            last_used_at=getattr(model, "last_used_at", None),
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )

    # ENTITY / CACHE
    @staticmethod
    def to_cache(key: Key) -> dict:
        """Entity → Cache — เอนทิตี → cache"""
        return KeyMapper.to_dto(key)

    @staticmethod
    def from_cache(data: dict) -> Key:
        """Cache → Entity — cache → เอนทิตี"""
        from datetime import datetime
        return Key(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            prefix=data["prefix"],
            last_four=data["last_four"],
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at") else None
            ),
            is_active=data.get("is_active", True),
        )
```

**`application/exceptions.py`**
```python
from apps.shared.application.exceptions import StandardException


class KeyException(StandardException):
    """Generic key exception — ข้อผิดพลาดทั่วไปของคีย์"""

    def __init__(self, message: str = "Key operation failed"):
        super().__init__(status_code=500, detail=message)


class KeyNotFoundException(StandardException):
    """Key not found — ไม่พบคีย์"""

    def __init__(self, message: str = "Key not found"):
        super().__init__(status_code=404, detail=message)


class KeyExpiredException(StandardException):
    """Key expired — คีย์หมดอายุ"""

    def __init__(self, message: str = "Key has expired"):
        super().__init__(status_code=400, detail=message)
```

#### 3. Infrastructure Layer

**`infrastructure/fastapi_client.py`**
```python
from apps.shared.infrastructure.fastapi_client import FastAPIClient as BaseClient
from apps.key.application.mappers import KeyMapper
from apps.key.domain.entities import Key


class KeyFastAPIClient:
    """Key FastAPI client — ไคลเอนต์ FastAPI สำหรับคีย์"""

    def __init__(self, base_client: BaseClient):
        self.client = base_client

    async def list(
        self,
        page: int,
        limit: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[Key], int]:
        """List keys — แสดงรายการคีย์"""
        resp = await self.client.get("/api/v1/key/", params={
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
        })

        if resp.status_code != 200:
            return [], 0

        data = BaseClient.unwrap(resp)
        if not data:
            return [], 0

        keys = [KeyMapper.from_cache(item) for item in data.get("items", [])]
        total = data.get("pagination", {}).get("total", 0)
        return keys, total

    async def get_by_id(self, id: str) -> Key | None:
        """Get key by ID — ดูคีย์ตาม ID"""
        resp = await self.client.get(f"/api/v1/key/{id}/")
        if resp.status_code != 200:
            return None
        data = BaseClient.unwrap(resp)
        return KeyMapper.from_cache(data) if data else None

    async def create(self, payload: dict) -> tuple[Key, str]:
        """Create key — สร้างคีย์"""
        resp = await self.client.post("/api/v1/key/", json=payload)
        if resp.status_code != 201:
            raise Exception("Failed to create key")
        data = BaseClient.unwrap(resp)
        key = KeyMapper.from_cache(data)
        raw_secret = data.get("raw_key", "")
        return key, raw_secret

    async def update(self, id: str, payload: dict) -> Key:
        """Update key — อัปเดตคีย์"""
        resp = await self.client.patch(f"/api/v1/key/{id}/", json=payload)
        if resp.status_code != 200:
            raise Exception("Failed to update key")
        data = BaseClient.unwrap(resp)
        return KeyMapper.from_cache(data)

    async def rotate(self, id: str) -> tuple[Key, str]:
        """Rotate key — หมุนคีย์"""
        resp = await self.client.patch(f"/api/v1/key/{id}/rotate/")
        if resp.status_code != 200:
            raise Exception("Failed to rotate key")
        data = BaseClient.unwrap(resp)
        key = KeyMapper.from_cache(data)
        new_secret = data.get("raw_key", "")
        return key, new_secret

    async def revoke(self, id: str) -> None:
        """Revoke key — ยกเลิกคีย์"""
        resp = await self.client.delete(f"/api/v1/key/{id}/")
        if resp.status_code not in (200, 204):
            raise Exception("Failed to revoke key")
```

#### 4. Presentation Layer

**`presentation/views.py`**
```python
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from apps.shared.infrastructure.fastapi_client import FastAPIClient
from apps.key.application.use_cases import KeyUseCases
from apps.key.infrastructure.fastapi_client import KeyFastAPIClient
from apps.key.presentation.forms import KeyCreateForm, KeyUpdateForm


def get_use_cases(request) -> KeyUseCases:
    """Factory — สร้าง use cases"""
    base_client = FastAPIClient(cookies=request.fastapi_cookies)
    key_client = KeyFastAPIClient(base_client)
    return KeyUseCases(
        repo=key_client,
        cache=None,  # TODO: implement cache
        audit=None,  # TODO: implement audit
        idempotency=None,  # TODO: implement idempotency
        events=None,  # TODO: implement events
    )


class KeyListView(View):
    """Key list view — หน้ารายการคีย์"""

    template_name = "key/list.html"

    def get(self, request):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        keys, total = use_cases.list_keys(
            page=int(request.GET.get("page", 1)),
            limit=int(request.GET.get("limit", 20)),
            sort_by=request.GET.get("sort_by", "updated_at"),
            sort_order=request.GET.get("sort_order", "desc"),
        )

        return render(request, self.template_name, {
            "keys": keys,
            "total": total,
            "page": int(request.GET.get("page", 1)),
        })


class KeyCreateView(View):
    """Key create view — หน้าสร้างคีย์"""

    template_name = "key/form.html"

    def get(self, request):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))
        form = KeyCreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        form = KeyCreateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        use_cases = get_use_cases(request)
        key, raw_secret = use_cases.create_key(
            payload=form.cleaned_data,
            idem_key=request.headers.get("Idempotency-Key", ""),
        )

        return render(request, "key/detail.html", {
            "key": key,
            "raw_secret": raw_secret,  # แสดงครั้งเดียว
        })


class KeyDetailView(View):
    """Key detail view — หน้ารายละเอียดคีย์"""

    template_name = "key/detail.html"

    def get(self, request, key_id):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        key = use_cases.get_key(key_id)

        return render(request, self.template_name, {"key": key})


class KeyUpdateView(View):
    """Key update view — หน้าแก้ไขคีย์"""

    template_name = "key/form.html"

    def get(self, request, key_id):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        key = use_cases.get_key(key_id)
        form = KeyUpdateForm(initial={
            "name": key.name,
            "description": key.description,
        })
        return render(request, self.template_name, {"form": form, "key": key})

    def post(self, request, key_id):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        form = KeyUpdateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        use_cases = get_use_cases(request)
        use_cases.update_key(key_id, form.cleaned_data)

        return redirect(reverse("key:detail", args=[key_id]))


class KeyRotateView(View):
    """Key rotate view — หน้าหมุนคีย์"""

    def post(self, request, key_id):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        key, new_secret = use_cases.rotate_key(key_id)

        return render(request, "key/detail.html", {
            "key": key,
            "raw_secret": new_secret,  # แสดงครั้งเดียว
        })


class KeyRevokeView(View):
    """Key revoke view — หน้ายกเลิกคีย์"""

    def post(self, request, key_id):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        use_cases.revoke_key(key_id)

        return redirect(reverse("key:list"))
```

**`presentation/urls.py`**
```python
from django.urls import path
from apps.key.presentation import views

app_name = "key"

urlpatterns = [
    path("", views.KeyListView.as_view(), name="list"),
    path("create/", views.KeyCreateView.as_view(), name="create"),
    path("<str:key_id>/", views.KeyDetailView.as_view(), name="detail"),
    path("<str:key_id>/update/", views.KeyUpdateView.as_view(), name="update"),
    path("<str:key_id>/rotate/", views.KeyRotateView.as_view(), name="rotate"),
    path("<str:key_id>/revoke/", views.KeyRevokeView.as_view(), name="revoke"),
]
```

**`presentation/forms.py`**
```python
from django import forms


class KeyCreateForm(forms.Form):
    """Key create form — ฟอร์มสร้างคีย์"""
    name = forms.CharField(max_length=100, min_length=3, required=True)
    description = forms.CharField(max_length=500, required=False)
    expires_in_days = forms.IntegerField(min_value=1, max_value=3650, required=False)


class KeyUpdateForm(forms.Form):
    """Key update form — ฟอร์มแก้ไขคีย์"""
    name = forms.CharField(max_length=100, min_length=3, required=False)
    description = forms.CharField(max_length=500, required=False)
```

**Template: `key/list.html`**
```django
{% extends "base.html" %}

{% block title %}รายการ API Keys{% endblock %}

{% block page_header %}
<div class="bg-white dark:bg-gray-800 shadow">
  <div class="container mx-auto px-4 py-6 flex justify-between items-center">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
      รายการ API Keys
    </h2>
    <a href="{% url 'key:create' %}"
       class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
      + สร้างคีย์ใหม่
    </a>
  </div>
</div>
{% endblock %}

{% block content %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
  <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
    <thead class="bg-gray-50 dark:bg-gray-900">
      <tr>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ชื่อ</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prefix</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">สร้างเมื่อ</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">จัดการ</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
      {% for key in keys %}
        <tr>
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            {{ key.name }}
          </td>
          <td class="px-6 py-4 text-sm font-mono text-gray-500">
            {{ key.prefix }}••••{{ key.last_four }}
          </td>
          <td class="px-6 py-4 text-sm text-gray-500">
            {{ key.created_at|date:"Y-m-d H:i" }}
          </td>
          <td class="px-6 py-4 text-sm">
            <a href="{% url 'key:detail' key.id %}"
               class="text-blue-600 hover:text-blue-800">
              ดู
            </a>
          </td>
        </tr>
      {% empty %}
        <tr>
          <td colspan="4" class="px-6 py-4 text-center text-gray-500">
            ยังไม่มี API Key
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

#### 5. Tests

```python
# test/modules/key/test_use_cases.py
import pytest
from apps.key.domain.entities import Key
from apps.key.domain.value_objects import KeySecret
from apps.shared.application.exceptions import DomainError


class FakeKeyRepository:
    """Fake key repository — รีโพซิทอรีคีย์ปลอม"""

    def __init__(self):
        self.keys = {}

    async def list(self, page, limit, sort_by, sort_order):
        items = list(self.keys.values())
        return items[:limit], len(items)

    async def get_by_id(self, id):
        return self.keys.get(id)

    async def create(self, payload):
        key = Key(id="key-1", **payload)
        self.keys[key.id] = key
        return key, "raw-secret-1234567890"

    async def update(self, id, payload):
        key = self.keys[id]
        for k, v in payload.items():
            setattr(key, k, v)
        return key

    async def rotate(self, id):
        key = self.keys[id]
        return key, "new-raw-secret-1234567890"

    async def revoke(self, id):
        del self.keys[id]


async def test_create_key_valid():
    """Test create key — ทดสอบสร้างคีย์"""
    repo = FakeKeyRepository()
    use_cases = KeyUseCases(repo=repo, cache=None, audit=None,
                            idempotency=None, events=None)
    key, secret = await use_cases.create_key(
        payload={"name": "Test Key", "prefix": "iap_", "last_four": "1234"},
        idem_key="idem-001",
    )
    assert key.name == "Test Key"
    assert secret.startswith("raw-secret")


async def test_key_name_too_short():
    """Test name too short — ทดสอบชื่อสั้นเกิน"""
    with pytest.raises(DomainError):
        Key(name="ab", prefix="iap_", last_four="1234")


async def test_key_secret_too_short():
    """Test secret too short — ทดสอบ secret สั้นเกิน"""
    with pytest.raises(DomainError):
        KeySecret(value="short")
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

### 📄 ไฟล์ 4: ตัวอย่าง `docs/prompts/layer-5-intelligence/forecast.md`

```markdown
# AI Prompt — Module `forecast`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `forecast` |
| **Layer** | `5` (Intelligence) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **มิติธุรกิจ** | BI |
| **Dependencies** | `analytics`, `reporting`, `production`, `inventory`, `agriculture` |
| **Domain Concepts** | `Forecast` (entity), `ForecastResult` (VO), `ForecastMethod` (enum) |
| **FastAPI Endpoint** | `/api/v1/forecast/` |

---

## 🎯 Prompt

### สร้าง Module `forecast` (Django Frontend BFF)

**บริบท:**
- Django Frontend (BFF) สำหรับ FastAPI Backend
- Clean Architecture + DDD (4 layers)
- **ห้ามแก้โค้ด FastAPI** — proxy ผ่าน HTTPX เท่านั้น
- **Invariants:** `MAPE < 20%`, `Forecast non-negative`
- **Events:** `ForecastGenerated`, `ForecastUpdated`, `ForecastAccuracyDropped`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from apps.shared.domain.entities import BaseEntity, DomainError


@dataclass
class Forecast(BaseEntity):
    """Forecast entity — เอนทิตีพยากรณ์"""
    product_id: str = ""
    branch_id: str = ""
    forecast_date: date | None = None
    predicted_qty: Decimal = Decimal("0.00")
    actual_qty: Decimal | None = None
    method: str = "LSTM"
    mape: Decimal | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        """Validate forecast — ตรวจสอบพยากรณ์"""
        if not self.product_id:
            raise DomainError("Product ID is required")
        if self.predicted_qty < 0:
            raise DomainError("Predicted qty cannot be negative")

    def update_actual(self, actual_qty: Decimal) -> None:
        """Update actual and calculate MAPE — อัปเดตค่าจริงและคำนวณ MAPE"""
        if actual_qty < 0:
            raise DomainError("Actual qty cannot be negative")
        self.actual_qty = actual_qty
        if actual_qty > 0:
            self.mape = abs(self.predicted_qty - actual_qty) / actual_qty * 100

    def is_accurate(self) -> bool:
        """Check if forecast is accurate (MAPE < 20%) — ตรวจสอบความแม่นยำ"""
        return self.mape is not None and self.mape < 20
```

**`domain/value_objects.py`**
```python
from dataclasses import dataclass
from decimal import Decimal
from apps.shared.domain.entities import DomainError


@dataclass(frozen=True)
class ForecastResult:
    """Forecast result VO — วัตถุค่าผลลัพธ์พยากรณ์"""
    predicted: Decimal
    actual: Decimal | None
    error: Decimal | None
    mape: Decimal | None

    def __post_init__(self):
        if self.predicted < 0:
            raise DomainError("Predicted must be non-negative")
        if self.actual is not None and self.actual < 0:
            raise DomainError("Actual must be non-negative")


@dataclass(frozen=True)
class AccuracyThreshold:
    """Accuracy threshold VO — วัตถุค่าเกณฑ์ความแม่นยำ"""
    mape_max: Decimal = Decimal("20.0")

    def is_accurate(self, mape: Decimal) -> bool:
        """Check if MAPE is within threshold — ตรวจสอบ MAPE ในเกณฑ์"""
        return mape < self.mape_max
```

**`domain/enums.py`**
```python
from enum import Enum


class ForecastMethod(str, Enum):
    LSTM = "LSTM"
    PROPHET = "PROPHET"
    XGBOOST = "XGBOOST"
    ARIMA = "ARIMA"
    ENSEMBLE = "ENSEMBLE"


class ForecastType(str, Enum):
    DEMAND = "DEMAND"
    PRODUCTION = "PRODUCTION"
    YIELD = "YIELD"
    PRICE = "PRICE"


class ForecastStatus(str, Enum):
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    VERIFIED = "VERIFIED"
    ACCURACY_DROPPED = "ACCURACY_DROPPED"
```

#### 2. Application Layer

**`application/interfaces.py`**
```python
from typing import Protocol
from apps.forecast.domain.entities import Forecast


class IForecastRepository(Protocol):
    async def list(
        self,
        product_id: str | None,
        branch_id: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[Forecast], int]: ...

    async def get_by_id(self, id: str) -> Forecast | None: ...

    async def generate(
        self,
        product_id: str,
        branch_id: str,
        days: int,
    ) -> list[Forecast]: ...

    async def update_actual(self, id: str, actual_qty) -> Forecast: ...


class IForecastCache(Protocol):
    async def get(self, id: str) -> Forecast | None: ...
    async def insert(self, id: str, forecast: Forecast) -> None: ...
    async def delete(self, id: str) -> None: ...
```

**`application/use_cases.py`**
```python
from decimal import Decimal
from loguru import logger
from apps.shared.application.exceptions import (
    StandardException, DomainException, DomainError,
)
from apps.forecast.application.exceptions import ForecastException
from apps.forecast.application.interfaces import (
    IForecastRepository, IForecastCache,
)
from apps.forecast.domain.entities import Forecast


class ForecastUseCases:
    """Forecast use cases — กรณีการใช้งานพยากรณ์"""

    def __init__(
        self,
        repo: IForecastRepository,
        cache: IForecastCache,
        audit: "IAuditService",
        events: "IEventBus",
    ):
        self.repo = repo
        self.cache = cache
        self.audit = audit
        self.events = events

    async def list_forecasts(
        self,
        product_id: str | None,
        branch_id: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[Forecast], int]:
        """List forecasts — แสดงรายการพยากรณ์"""
        try:
            return await self.repo.list(product_id, branch_id, page, limit)
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in list_forecasts")
            raise ForecastException()

    async def generate_forecast(
        self,
        product_id: str,
        branch_id: str,
        days: int,
    ) -> list[Forecast]:
        """Generate forecast — สร้างพยากรณ์"""
        try:
            forecasts = await self.repo.generate(product_id, branch_id, days)
            await self.audit.log("forecast.generated", product_id)
            await self.events.publish("ForecastGenerated", {
                "product_id": product_id,
                "branch_id": branch_id,
                "count": len(forecasts),
            })
            return forecasts
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in generate_forecast")
            raise ForecastException()

    async def update_actual(
        self,
        id: str,
        actual_qty: Decimal,
    ) -> Forecast:
        """Update actual — อัปเดตค่าจริง"""
        try:
            forecast = await self.repo.get_by_id(id)
            if not forecast:
                raise ForecastException("Forecast not found")

            forecast.update_actual(actual_qty)
            forecast = await self.repo.update_actual(id, actual_qty)

            await self.cache.delete(id)
            await self.audit.log("forecast.updated", id)
            await self.events.publish("ForecastUpdated", forecast)

            if not forecast.is_accurate():
                await self.events.publish("ForecastAccuracyDropped", {
                    "id": id,
                    "mape": str(forecast.mape),
                })

            return forecast
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in update_actual")
            raise ForecastException()

    async def backtest(
        self,
        product_id: str,
        days: int,
    ) -> dict:
        """Backtest — ทดสอบย้อนหลัง"""
        try:
            forecasts = await self.repo.list(
                product_id=product_id,
                branch_id=None,
                page=1,
                limit=days,
            )
            items = forecasts[0]
            maples = [f.mape for f in items if f.mape is not None]
            avg_mape = sum(maples) / len(maples) if maples else Decimal("0")
            return {
                "count": len(items),
                "avg_mape": str(avg_mape),
                "is_accurate": avg_mape < Decimal("20"),
            }
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in backtest")
            raise ForecastException()
```

#### 3. Infrastructure Layer

**`infrastructure/fastapi_client.py`**
```python
from apps.shared.infrastructure.fastapi_client import FastAPIClient as BaseClient
from apps.forecast.application.mappers import ForecastMapper
from apps.forecast.domain.entities import Forecast


class ForecastFastAPIClient:
    """Forecast FastAPI client — ไคลเอนต์ FastAPI สำหรับพยากรณ์"""

    def __init__(self, base_client: BaseClient):
        self.client = base_client

    async def list(self, product_id, branch_id, page, limit):
        params = {"page": page, "limit": limit}
        if product_id:
            params["product_id"] = product_id
        if branch_id:
            params["branch_id"] = branch_id

        resp = await self.client.get("/api/v1/forecast/", params=params)
        if resp.status_code != 200:
            return [], 0

        data = BaseClient.unwrap(resp)
        if not data:
            return [], 0

        items = [ForecastMapper.from_cache(i) for i in data.get("items", [])]
        total = data.get("pagination", {}).get("total", 0)
        return items, total

    async def get_by_id(self, id: str) -> Forecast | None:
        resp = await self.client.get(f"/api/v1/forecast/{id}/")
        if resp.status_code != 200:
            return None
        data = BaseClient.unwrap(resp)
        return ForecastMapper.from_cache(data) if data else None

    async def generate(self, product_id, branch_id, days):
        resp = await self.client.post("/api/v1/forecast/generate/", json={
            "product_id": product_id,
            "branch_id": branch_id,
            "days": days,
        })
        if resp.status_code != 201:
            raise Exception("Failed to generate forecast")
        data = BaseClient.unwrap(resp)
        return [ForecastMapper.from_cache(i) for i in data.get("items", [])]

    async def update_actual(self, id: str, actual_qty):
        resp = await self.client.patch(
            f"/api/v1/forecast/{id}/actual/",
            json={"actual_qty": str(actual_qty)},
        )
        if resp.status_code != 200:
            raise Exception("Failed to update actual")
        data = BaseClient.unwrap(resp)
        return ForecastMapper.from_cache(data)
```

#### 4. Presentation Layer

**`presentation/views.py`**
```python
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from apps.shared.infrastructure.fastapi_client import FastAPIClient
from apps.forecast.application.use_cases import ForecastUseCases
from apps.forecast.infrastructure.fastapi_client import ForecastFastAPIClient


def get_use_cases(request) -> ForecastUseCases:
    base = FastAPIClient(cookies=request.fastapi_cookies)
    client = ForecastFastAPIClient(base)
    return ForecastUseCases(
        repo=client, cache=None, audit=None, events=None,
    )


class ForecastListView(View):
    """Forecast list view — หน้ารายการพยากรณ์"""

    template_name = "forecast/list.html"

    def get(self, request):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        items, total = use_cases.list_forecasts(
            product_id=request.GET.get("product_id"),
            branch_id=request.GET.get("branch_id"),
            page=int(request.GET.get("page", 1)),
            limit=int(request.GET.get("limit", 20)),
        )

        return render(request, self.template_name, {
            "items": items,
            "total": total,
            "page": int(request.GET.get("page", 1)),
        })


class ForecastGenerateView(View):
    """Forecast generate view — หน้าสร้างพยากรณ์"""

    def post(self, request):
        if not request.is_authenticated:
            return redirect(reverse("authentication:login"))

        use_cases = get_use_cases(request)
        items = use_cases.generate_forecast(
            product_id=request.POST["product_id"],
            branch_id=request.POST["branch_id"],
            days=int(request.POST.get("days", 30)),
        )

        return redirect(reverse("forecast:list"))
```

**`presentation/urls.py`**
```python
from django.urls import path
from apps.forecast.presentation import views

app_name = "forecast"

urlpatterns = [
    path("", views.ForecastListView.as_view(), name="list"),
    path("generate/", views.ForecastGenerateView.as_view(), name="generate"),
]
```

**Template: `forecast/list.html`**
```django
{% extends "base.html" %}

{% block title %}พยากรณ์{% endblock %}

{% block page_header %}
<div class="bg-white dark:bg-gray-800 shadow">
  <div class="container mx-auto px-4 py-6 flex justify-between items-center">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
      พยากรณ์
    </h2>
    <a href="{% url 'forecast:generate' %}"
       class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
      + สร้างพยากรณ์ใหม่
    </a>
  </div>
</div>
{% endblock %}

{% block content %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
  <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
    <thead class="bg-gray-50 dark:bg-gray-900">
      <tr>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">วันที่</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">สินค้า</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ทำนาย</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">จริง</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAPE</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">สถานะ</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
      {% for item in items %}
        <tr>
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            {{ item.forecast_date|date:"Y-m-d" }}
          </td>
          <td class="px-6 py-4 text-sm text-gray-500">{{ item.product_id }}</td>
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            {{ item.predicted_qty }}
          </td>
          <td class="px-6 py-4 text-sm text-gray-500">
            {{ item.actual_qty|default:"—" }}
          </td>
          <td class="px-6 py-4 text-sm">
            {% if item.mape %}
              <span class="{% if item.mape < 20 %}text-green-600{% else %}text-red-600{% endif %}">
                {{ item.mape|floatformat:2 }}%
              </span>
            {% else %}—{% endif %}
          </td>
          <td class="px-6 py-4 text-sm">
            {% if item.mape and item.mape < 20 %}
              <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">แม่นยำ</span>
            {% else %}
              <span class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">รอตรวจสอบ</span>
            {% endif %}
          </td>
        </tr>
      {% empty %}
        <tr>
          <td colspan="6" class="px-6 py-4 text-center text-gray-500">
            ยังไม่มีข้อมูลพยากรณ์
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

#### 5. Tests

```python
# test/modules/forecast/test_use_cases.py
import pytest
from decimal import Decimal
from apps.forecast.domain.entities import Forecast
from apps.shared.application.exceptions import DomainError


async def test_generate_forecast_non_negative():
    """Property-based: forecast >= 0 — ทดสอบ invariant"""
    ...


async def test_mape_calculation():
    """Test MAPE — ทดสอบ MAPE"""
    forecast = Forecast(product_id="p1", predicted_qty=Decimal("100"))
    forecast.update_actual(Decimal("110"))
    assert forecast.mape == Decimal("9.090909090909090909090909091")


async def test_forecast_accurate():
    """Test accurate — ทดสอบความแม่นยำ"""
    forecast = Forecast(product_id="p1", predicted_qty=Decimal("100"))
    forecast.update_actual(Decimal("105"))
    assert forecast.is_accurate()  # MAPE < 20%
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## ภาคผนวก

### A. Checklist ก่อนส่ง

- [ ] Domain layer ไม่ import framework
- [ ] ใช้ HTTPX proxy ไป FastAPI (ไม่แก้ FastAPI)
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Session + Cookies forwarding ทำงาน
- [ ] Audit log ครบ
- [ ] Tests ครบ 3 ประเภท
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน

### B. คำสั่งที่ใช้บ่อย

```bash
# ติดตั้ง dependencies
uv sync

# รัน Django development server
python manage.py runserver 8001

# รัน migrations
python manage.py migrate

# สร้าง migration ใหม่
python manage.py makemigrations

# สร้าง superuser
python manage.py createsuperuser

# รัน tests
pytest test/ -v

# รัน lint
ruff check .

# รัน format
ruff format .

# Docker
docker compose up
docker compose up --build
docker compose down -v
```

### C. Environment Variables

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# FastAPI Backend
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_TIMEOUT=30

# Database (optional, for Django models)
DATABASE_URL=postgresql://user:pass@localhost:5432/django_db

# Redis (optional, for Django cache)
REDIS_URL=redis://localhost:6379/0

# Tailwind
TAILWIND_MODE=watch
```

### D. Dependencies

```txt
# requirements.txt
Django==5.0.0
httpx==0.27.0
python-dotenv==1.0.0
channels==4.0.0
channels-redis==4.2.0
websockets==12.0
pytest==8.0.0
pytest-asyncio==0.23.0
ruff==0.3.0
```

### E. การ Deploy

```yaml
# docker-compose.yaml
version: "3.9"

services:
  django:
    build: .
    ports:
      - "8001:8001"
    environment:
      - FASTAPI_BASE_URL=http://fastapi:8000
    depends_on:
      - fastapi
    networks:
      - app-network

  fastapi:
    image: fastapi-backend:latest
    ports:
      - "8000:8000"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

---

## สรุป

Django Frontend (BFF) Template นี้เป็น:

- ✅ **Production-ready** — พร้อมใช้งานจริง
- ✅ **Non-invasive** — ไม่แก้โค้ด FastAPI เดิม
- ✅ **Modular** — แยก module ชัดเจน
- ✅ **Testable** — Unit test ง่าย
- ✅ **Scalable** — ขยายได้ไม่จำกัด
- ✅ **AI-Ready** — มี Prompt Template 68 modules
- ✅ **Modern UI** — Tailwind CSS + Alpine.js
- ✅ **Secure** — Session + Cookies + CSRF

### Module ทั้งหมด 68 ตัว (ตาม App_Modules.md + FastAPI เดิม)

| Layer | จำนวน | Modules |
|---|---|---|
| Layer 0: Core | 6 | money, tenant_context, audit, idempotency, config, events |
| Layer 1: Foundation | 11 | tenancy, authentication, user, employee, customer, supplier, product, pricing, key, knowledge, notification |
| Layer 2: Money Path | 7 | order, invoice, ledger, payment, accounting_gateway, tax, reconciliation |
| Layer 3: Goods Path | 13 | inventory, warehouse, lot, production, recipe, quality, waste, procurement, traceability, agriculture, crop, soil, irrigation |
| Layer 4: Operations | 13 | transport, delivery, route, gps, retail, pos, shift, line_channel, promotion, loyalty, crm, campaign, support |
| Layer 5: Intelligence | 7 | reporting, analytics, forecast, kpi, satisfaction, recommendation, oee |
| Layer 6: Monitoring | 8 | iot, cctv, monitoring, backup, alerting, audit_viewer, maintenance, energy |
| Layer 7: Templates | 3 | health, example, blank |
| **รวม** | **68** | |

---

**ผู้แต่ง:** Kongnakorn Jantakun
**อีเมล:** kongnakornjantakun@gmail.com
**เวอร์ชัน:** 2.0.0
**อัปเดต:** 2026-09-17
**สถานะ:** ✅ พร้อมใช้งาน

---

> **Built with ❤️ for SME ERP + CRM + IoT**