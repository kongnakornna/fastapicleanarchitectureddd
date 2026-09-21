app/modules/
├── money/                          (25 ไฟล์)
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py             # ว่าง (pure VO)
│   │   ├── enums.py                # Currency, VATRate, RoundingMode
│   │   ├── events.py               # 4 events
│   │   ├── exceptions.py           # DomainError
│   │   └── value_objects.py        # Money, VAT, ExchangeRate ✅
│   ├── application/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── interfaces.py
│   │   ├── mappers.py              # MoneyMapper
│   │   ├── use_cases.py            # MoneyUseCases ✅
│   │   └── utils.py                # round_money, zero_money
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── models.py               # ว่าง
│   │   ├── repositories.py         # ว่าง
│   │   ├── caches.py               # ว่าง
│   │   └── services.py             # ว่าง
│   └── presentation/
│       ├── __init__.py
│       ├── dependencies.py         # get_money_use_cases
│       ├── docs.py
│       ├── routers.py              # 5 endpoints ✅
│       └── schemas.py              # MoneySchema + to_money()
│
└── idempotency/                    (25 ไฟล์)
    ├── __init__.py
    ├── domain/
    │   ├── __init__.py
    │   ├── entities.py             # IdempotencyRecord ✅
    │   ├── enums.py                # IdempotencyStatus, IdempotencyConflict
    │   ├── events.py
    │   ├── exceptions.py
    │   └── value_objects.py        # IdempotencyKey ✅
    ├── application/
    │   ├── __init__.py
    │   ├── exceptions.py           # 3 exception classes
    │   ├── interfaces.py           # IIdempotencyStore ✅
    │   ├── mappers.py
    │   ├── use_cases.py            # IdempotencyUseCases ✅
    │   └── utils.py                # hash_payload, idempotent
    ├── infrastructure/
    │   ├── __init__.py
    │   ├── models.py               # IdempotencyRecordModel ✅
    │   ├── repositories.py         # PostgresIdempotencyRepository
    │   ├── caches.py               # RedisIdempotencyStore ✅
    │   └── services.py
    └── presentation/
        ├── __init__.py
        ├── dependencies.py         # require_idempotency_key ✅
        ├── docs.py
        ├── routers.py              # ว่าง (ใช้ middleware)
        └── schemas.py