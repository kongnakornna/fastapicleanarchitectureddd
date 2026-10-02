# Full Path ของไฟล์ทั้งหมด

จากโครงสร้าง module ที่ปรากฏใน code ทั้งหมด นี่คือ full path ของแต่ละไฟล์ (relative จาก project root):

## 📁 Key Module

```
app/modules/key/
├── application/
│   ├── __init__.py
│   ├── exceptions.py          ← KeyException, KeyNotFoundException, ...
│   ├── interfaces.py          ← IKeyRepository, IKeyCache, IKeyService
│   ├── mappers.py             ← ⚠️ แก้ไข (cache_entity_mapper)
│   ├── use_cases.py           ← KeyUseCases
│   └── utils.py               ← resolve_expires_at
│
├── domain/
│   ├── __init__.py
│   ├── entities.py            ← Key, KeyList, KeyPagination
│   ├── enums.py               ← KeyExpiration, KeySortField
│   └── value_objects.py       ← (ว่าง)
│
├── infrastructure/
│   ├── __init__.py
│   ├── caches.py              ← RedisKeyCache
│   ├── models.py              ← KeyModel (⚠️ FK เป็น BIGINT)
│   ├── repositories.py        ← PostgresKeyRepository
│   └── services.py            ← KeyService
│
└── presentation/
    ├── __init__.py
    ├── dependencies.py        ← get_key_cache, get_key_repository, ...
    ├── docs.py                ← ⚠️ แก้ไข (get_docs example)
    ├── routers.py             ← APIRouter + endpoints
    └── schemas.py             ← CreateRequest, GetResponse, ...
```

---

## 📁 Shared Module (ที่ถูก import)

```
app/modules/shared/
├── application/
│   ├── exceptions.py          ← StandardException, DomainException
│   └── utils.py               ← BRASILIA_TZ
│
├── domain/
│   ├── entities.py            ← BaseEntity, DomainError, PaginatedList, ...
│   ├── enums.py               ← ResponseMessages, SortOrder
│   └── value_objects.py       ← RESOURCE_NAME_PATTERN, UNSET, Name
│
└── presentation/
    └── schemas.py             ← DeleteResponse, UpdateResponse, ...
```

---

## 📁 Related Modules (ที่ถูก import)

```
app/modules/
├── authentication/
│   └── domain/
│       └── entities.py        ← Authentication
│
└── user/
    ├── domain/
    │   └── entities.py        ← User
    └── infrastructure/
        └── models.py          ← UserModel
```

---

## 📁 Core (ที่ถูก import)

```
app/core/
├── cache.py                   ← get_cache_session
├── database.py                ← get_async_session
├── security.py                ← ⚠️ authenticate_admin (ต้นเหตุ 403 — ยังไม่แนบ)
│                                 generate_api_key
└── settings.py                ← settings (REDIS_NAMESPACE, ...)
```

---

## 🎯 สรุปไฟล์ที่ต้องแก้ไข

| # | Full Path | การแก้ไข |
|---|-----------|---------|
| 1 | `app/modules/key/application/mappers.py` | `cache_entity_mapper`: `UUID(...)` → `int(...)` สำหรับ `created_by` / `updated_by` |
| 2 | `app/modules/key/presentation/docs.py` | `get_docs` example: `created_by`/`updated_by` เป็น object, ลบ `is_active` |

## 🔍 ไฟล์ที่ต้องตรวจเพิ่ม (ยังไม่แนบมา)

| # | Full Path | เหตุผล |
|---|-----------|--------|
| 3 | `app/core/security.py` | ต้นเหตุ 403 — `authenticate_admin` โยน exception ก่อนเข้า use case |
| 4 | `app/modules/user/infrastructure/models.py` | ตรวจว่า `UserModel.id` เป็น `BigInteger` แล้วจริง (สอดคล้องกับ FK) |

---

## 💡 โครงสร้าง dependency (สรุป)

```
routers.py
   │
   ├── Depends(authenticate_admin)  ← app/core/security.py  (403 เกิดที่นี่)
   ├── Depends(get_key_use_cases)   ← presentation/dependencies.py
   │        │
   │        ├── IKeyCache  → infrastructure/caches.py
   │        ├── IKeyRepository → infrastructure/repositories.py
   │        └── IKeyService → infrastructure/services.py
   │
   └── mappers.py (request/response mapping)
```

**หมายเหตุ:** ถ้าต้องการ pinpoint 403 แน่ ๆ กรุณาแนบ `app/core/security.py` และ `app/modules/user/infrastructure/models.py` มาด้วยครับ
