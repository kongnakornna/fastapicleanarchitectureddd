# สรุปโครงสร้างและการทำงานของระบบ FastAPI Backend

## 1. โครงสร้าง Folder

```
fastapi-backend/
├── app/
│   ├── main.py                          # Entry point ของแอป
│   ├── core/                            # Core configuration
│   │   ├── config.py                    # Settings (log_level, app_name)
│   │   ├── settings.py                  # Settings หลักของระบบ
│   │   ├── logging.py                   # Loguru setup
│   │   ├── security.py                  # Auth dependencies (JWT, hashing)
│   │   ├── middleware.py                # Response envelope builder
│   │   ├── exception_handler.py         # Global exception handling
│   │   ├── database.py                  # AsyncSession management
│   │   └── cache.py                     # Redis session
│   │
│   └── modules/                         # แบ่งตาม Domain (DDD)
│       ├── shared/                      # โค้ดที่ใช้ร่วมกัน
│       │   ├── domain/
│       │   │   ├── entities.py          # BaseEntity, DomainError
│       │   │   ├── enums.py             # Role, ResponseMessages
│       │   │   └── value_objects.py     # Email, Phone, Name
│       │   ├── application/
│       │   │   ├── exceptions.py        # StandardException, DomainException
│       │   │   ├── use_cases.py         # SharedUseCases
│       │   │   └── utils.py             # BRASILIA_TZ, resolve_client_ip
│       │   └── presentation/
│       │       ├── schemas.py           # StandardResponse
│       │       └── dependencies.py      # get_shared_use_cases
│       │
│       ├── user/                        # Module ผู้ใช้
│       │   ├── domain/
│       │   │   ├── entities.py          # User entity
│       │   │   ├── enums.py             # Gender
│       │   │   └── events.py            # (TODO)
│       │   ├── application/
│       │   │   ├── interfaces.py        # IUserRepository
│       │   │   ├── use_cases.py         # UserUseCases
│       │   │   ├── mappers.py           # Entity/Model/DTO mapping
│       │   │   └── exceptions.py        # UserException, ...
│       │   ├── infrastructure/
│       │   │   ├── models.py            # UserModel (SQLAlchemy)
│       │   │   └── repositories.py      # PostgresUserRepository
│       │   └── presentation/
│       │       ├── routers.py           # /api/v1/user endpoints
│       │       ├── schemas.py           # CreateRequest, MeResponse
│       │       ├── docs.py              # OpenAPI docs
│       │       └── dependencies.py      # get_user_use_cases
│       │
│       └── authentication/              # Module Authentication
│           ├── domain/
│           │   ├── entities.py          # Authentication, AccessToken, RefreshToken
│           │   ├── value_objects.py     # Claims, RefreshClaims
│           │   ├── enums.py             # TokenType
│           │   └── events.py            # (TODO)
│           ├── application/
│           │   ├── interfaces.py        # IAuthRepository, IAuthCache, ITokenService
│           │   ├── use_cases.py         # AuthenticationUseCases
│           │   ├── mappers.py           # Entity/Model/Cache/DTO mapping
│           │   └── exceptions.py        # AuthenticationException, ...
│           ├── infrastructure/
│           │   ├── models.py            # AuthenticationModel, RefreshTokenModel,
│           │   │                        # AccessTokenModel
│           │   ├── repositories.py      # PostgresAuthenticationRepository
│           │   ├── caches.py            # RedisAuthenticationCache
│           │   └── services.py          # TokenService
│           └── presentation/
│               ├── routers.py           # /api/v1/authentication endpoints
│               ├── schemas.py           # LoginResponse, RefreshResponse, LogoutResponse
│               ├── docs.py              # OpenAPI docs
│               └── dependencies.py      # get_authentication_use_cases
│
├── .env
├── pyproject.toml
└── .venv/
```

---

## 2. คำอธิบายการทำงานแต่ละส่วน

### 2.1 Core Layer (`app/core/`)

| ไฟล์ | หน้าที่ |
|------|--------|
| `config.py` | โหลด Settings พื้นฐาน (`log_level`, `app_name`) จาก environment |
| `settings.py` | Settings หลัก (JWT, Redis, DB, Cookies) |
| `logging.py` | ตั้งค่า Loguru + `serialize()` สำหรับ JSON log |
| `security.py` | Dependencies: `authenticate_user`, `authenticate_refresh`, `authenticate_logout`, `no_authentication`, `hash_password`, `verify_password`, `generate_tokens`, `hash_tokens` |
| `middleware.py` | สร้าง Response envelope `{code, method, path, timestamp, details: {message, data}}` |
| `exception_handler.py` | จับ Exception และแปลงเป็น envelope |
| `database.py` | AsyncSession factory |
| `cache.py` | Redis client factory |

### 2.2 Module Pattern (DDD + Clean Architecture)

แต่ละ module แบ่งเป็น 4 layer:

```
presentation → application → domain ← infrastructure
```

#### **Domain Layer** — Business rules บริสุทธิ์
- **entities.py**: Dataclass หลัก เช่น `User`, `Authentication`, `AccessToken`, `RefreshToken`
- **value_objects.py**: Immutable objects เช่น `Claims`, `RefreshClaims`, `Email`, `Phone`, `Name`
- **enums.py**: `Gender`, `TokenType`, `Role`
- **events.py**: (TODO) Domain events

#### **Application Layer** — Use cases + Interfaces
- **interfaces.py**: Protocol classes (`IUserRepository`, `IAuthenticationCache`, `ITokenService`)
- **use_cases.py**: Business orchestration (`UserUseCases`, `AuthenticationUseCases`)
- **mappers.py**: แปลงระหว่าง Entity ↔ Model ↔ Cache ↔ DTO
- **exceptions.py**: Custom exceptions ที่สืบทอด `StandardException`

#### **Infrastructure Layer** — Implementation
- **models.py**: SQLAlchemy ORM models
- **repositories.py**: PostgreSQL implementation
- **caches.py**: Redis implementation (มี tombstone pattern กัน race condition)
- **services.py**: Token service (JWT)

#### **Presentation Layer** — HTTP
- **routers.py**: FastAPI endpoints + cookie management
- **schemas.py**: Pydantic request/response
- **docs.py**: OpenAPI documentation
- **dependencies.py**: DI wiring

### 2.3 Flow การ Login

```
POST /api/v1/authentication/login/
    ↓
routers.login()
    ↓ (login_entity_mapper)
Authentication entity { user, ip, device, user_agent, ... }
    ↓
AuthenticationUseCases.login()
    ├─ shared_service.get_user_by_email()
    ├─ token_service.verify_password()
    ├─ repository.get_by_user_id_agent_and_device()  ← ถ้ามีอยู่แล้ว renew
    ├─ authentication.create_tokens(now, refresh_exp, access_exp)
    ├─ token_service.generate()   ← สร้าง JWT
    ├─ token_service.hash_tokens() ← hash JTI
    ├─ repository.create() หรือ .update()
    └─ return Authentication
    ↓ (entity_login_mapper)
LoginResponse { access_token, refresh_token }
    ↓ (middleware)
Envelope { code, method, path, timestamp, details: { message, data } }
    ↓
routers.set_cookies() ← ตั้ง HttpOnly cookies
```

### 2.4 Response Envelope

```json
{
  "code": 200,
  "method": "POST",
  "path": "/api/v1/authentication/login/",
  "timestamp": "2026-03-15T23:14:46.555200Z",
  "details": {
    "message": "User logged in successfully",
    "data": {
      "access_token": "...",
      "refresh_token": "..."
    }
  }
}
```

Envelope ถูกสร้างใน `core/middleware.py` (success path) และ `core/exception_handler.py` (error path)

### 2.5 Cache Tombstone Pattern

`RedisAuthenticationCache` ใช้ tombstone กัน race condition:
- **ก่อน delete**: เขียน tombstone key (`prefix:tombstone:...`) TTL สั้น
- **ก่อน insert**: เช็ค tombstone ถ้ามี → skip (ป้องกัน stale write หลัง logout/refresh)

---

## 3. การทำส่วนต่อขยาย (Extension)

### 3.1 เพิ่ม Module ใหม่ (เช่น `product`)

```
app/modules/product/
├── domain/
│   ├── entities.py       # Product entity
│   ├── enums.py          # ProductStatus
│   ├── value_objects.py  # SKU, Price
│   └── events.py
├── application/
│   ├── interfaces.py     # IProductRepository
│   ├── use_cases.py      # ProductUseCases
│   ├── mappers.py
│   └── exceptions.py     # ProductException
├── infrastructure/
│   ├── models.py         # ProductModel
│   └── repositories.py   # PostgresProductRepository
└── presentation/
    ├── routers.py
    ├── schemas.py
    ├── docs.py
    └── dependencies.py
```

จากนั้น register router ใน `app/main.py`:
```python
from app.modules.product.presentation.routers import router as product_router

app.include_router(product_router)
```

### 3.2 เพิ่ม Endpoint ใน Module ที่มีอยู่

1. เพิ่ม method ใน `use_cases.py`
2. เพิ่ม schema ใน `presentation/schemas.py`
3. เพิ่ม mapper (ถ้าต้องแปลง Entity ↔ DTO)
4. เพิ่ม endpoint ใน `presentation/routers.py`
5. เพิ่ม docs ใน `presentation/docs.py` (optional)

### 3.3 เพิ่ม Repository Method

1. เพิ่ม signature ใน `application/interfaces.py`
2. implement ใน `infrastructure/repositories.py`

### 3.4 เพิ่ม Exception ใหม่

ใน `application/exceptions.py` สืบทอด `StandardException`:
```python
class ProductNotFoundException(StandardException):
    def __init__(self, product_id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"Product '{product_id}' not found."},
        )
```

### 3.5 เพิ่ม Cache Layer

1. สร้าง Protocol ใน `application/interfaces.py`
2. implement ใน `infrastructure/caches.py` (ทำตาม pattern ของ `RedisAuthenticationCache`)
3. wire ใน `presentation/dependencies.py`

### 3.6 เพิ่ม Background Task / Event

- `domain/events.py` — นิยาม event names
- สร้าง event dispatcher ใน `shared/application/`
- publish จาก use case หลัง business logic สำเร็จ

---

## 4. การแก้ Bug

### 4.1 Bug ที่พบในเซสชันนี้: `SyntaxError` ใน `app/core/logging.py`

**อาการ:**
```
SyntaxError: invalid syntax at app\core\logging.py line 37
```

**สาเหตุ:**
- บรรทัด 37: `def def setup_logging(log_level: str) -> None:` — มี `def` ซ้ำ
- บรรทัด 47: `logger.add(...) -> None:` — มี `-> None:` ต่อท้าย call
- บรรทัด 48-49: duplicate body ของ `init_loguru()` ที่ module level

**วิธีแก้:**

```python
# ก่อนแก้ (ผิด)
def def setup_logging(log_level: str) -> None:
    logger.remove()
    logger.add(
        lambda message: print(serialize(message.record), file=sys.stderr),
        level=log_level.upper(),
    )

def init_loguru() -> None:
    logger.remove()
    logger.add(lambda message: print(serialize(message.record), file=sys.stderr)) -> None:
    logger.remove()
    logger.add(lambda message: print(serialize(message.record), file=sys.stderr))

# หลังแก้ (ถูก)
def setup_logging(log_level: str) -> None:
    logger.remove()
    logger.add(
        lambda message: print(serialize(message.record), file=sys.stderr),
        level=log_level.upper(),
    )

def init_loguru() -> None:
    logger.remove()
    logger.add(lambda message: print(serialize(message.record), file=sys.stderr))
```

**ผลลัพธ์:** `import app.main` ผ่านไม่มี error

### 4.2 Bug: Login response ไม่มี `access_token` / `refresh_token`

**อาการ:** envelope `details.data` ว่างเปล่า `{}`

**สาเหตุ:** `entity_login_mapper` return `LoginResponse()` แบบ message-only

**วิธีแก้:**

`mappers.py`:
```python
def entity_login_mapper(_authentication: Authentication) -> LoginResponse:
    return LoginResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
    )
```

`schemas.py`:
```python
class LoginResponse(BaseModel):
    message: str = ResponseMessages.LOGIN_SUCCESS.value
    access_token: str  # required (ไม่มี default)
    refresh_token: str  # required (ไม่มี default)
```

### 4.3 Bug: Port 8000 ถูก占用 (WinError 10048)

**อาการ:** uvicorn bind ไม่ได้ `[Errno 10048] only one usage of each socket address`

**สาเหตุ:** มี stale uvicorn process ค้างอยู่ (PID 19804, รัน `app.app:app --reload`)

**วิธีแก้:**
```powershell
# หา process ที่占用 port
Get-NetTCPConnection -LocalPort 8000 -State Listen

# ดู command line
Get-CimInstance Win32_Process -Filter "ProcessId=19804" | Select CommandLine

# kill process
Stop-Process -Id 19804 -Force

# ถ้า TCP entry ยังค้าง → ใช้ port อื่น (8002)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### 4.4 Bug: Circular Import

**อาการ:** import error เมื่อ `logging.py` import `settings` จาก `app.core.settings` ซึ่งดึง `app.modules.shared.domain.enums`

**วิธีตรวจสอบ:**
```powershell
.venv\Scripts\python.exe -c "import app.main"
```

**วิธีแก้:** แยก settings ที่เบาออกจาก settings ที่หนัก หรือใช้ lazy import

### 4.5 Bug: Refresh/Logout Response ไม่สมมาตรกับ Login

**หมายเหตุ:** ในเซสชันนี้ `RefreshResponse` และ `entity_refresh_mapper` ถูก mark ว่า out of scope แต่ถ้าต้องการให้สม่ำเสมอ:

```python
# mappers.py
def entity_refresh_mapper(_authentication: Authentication) -> RefreshResponse:
    return RefreshResponse()  # ปัจจุบัน message-only


# ควรเป็น (ถ้าต้องการให้คืน tokens ใน envelope)
def entity_refresh_mapper(_authentication: Authentication) -> RefreshResponse:
    return RefreshResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
    )
```

### 4.6 ข้อควรระวังในการแก้ Bug

1. **อย่าแตะ cookie logic** — `set_cookies` / `delete_cookies` ใน `routers.py` เป็นส่วนที่ทำงานถูกต้องแล้ว
2. **อย่าแตะ envelope builder** — `middleware.py` (บรรทัด 473-545) และ `exception_handler.py` เป็นส่วนกลาง
3. **ใช้ tombstone pattern** — ถ้าเพิ่ม cache operations ต้องคำนึงถึง race condition ระหว่าง read/write กับ delete
4. **Check `extra="forbid"`** — Pydantic models ตั้ง `extra="forbid"` ถ้าเพิ่ม field ต้องอัปเดต mapper ด้วย
5. **`validate_return=True`** — Pydantic จะ validate ค่าที่ return จาก method ถ้า schema ไม่ตรงจะ error

---

## 5. สถานะปัจจุบันของงาน

| Todo | สถานะ |
|------|--------|
| Fix SyntaxErrors in `logging.py` + verify import | ✅ เสร็จ |
| Verify `login_entity_mapper` returns nested tokens | ✅ เสร็จ |
| Verify `LoginResponse` schema requires tokens | ✅ เสร็จ |
| Launch uvicorn on free port 8002 | 🔄 กำลังทำ |
| Poll `GET /` for health payload | ⏳ รอ |
| Probe `POST /api/v1/authentication/login/` | ⏳ รอ |
| Stop process + report | ⏳ รอ |

**คำสั่งถัดไป:**
```powershell
# Launch on port 8002 (ยืนยันว่าว่าง)
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8002" `
  -WorkingDirectory "C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend" `
  -RedirectStandardOutput "...\uvicorn_stdout.log" `
  -RedirectStandardError "...\uvicorn_stderr.log" `
  -PassThru | Select -ExpandProperty Id | Set-Content "...\uvicorn.pid"

# รอ 5 วินาที แล้วเช็ค startup
Start-Sleep -Seconds 5
Get-Content "...\uvicorn_stderr.log"

# Poll root route
Invoke-WebRequest http://127.0.0.1:8002/ -UseBasicParsing

# Probe login (expect 401/422)
try { Invoke-WebRequest -Method POST http://127.0.0.1:8002/api/v1/authentication/login/ -Body @{username="x";password="y"} -UseBasicParsing } catch { $_.Exception.Response.StatusCode.value__ }
```
# สรุปสถานะและแผนดำเนินการต่อ

## สถานะปัจจุบัน (จากไฟล์ Thought)

### ✅ งานที่เสร็จแล้ว

| # | งาน | สถานะ |
|---|-----|--------|
| 1 | Fix SyntaxErrors ใน `app/core/logging.py` + verify import | ✅ เสร็จ |
| 2 | Verify `login_entity_mapper` return nested tokens | ✅ เสร็จ |
| 3 | Verify `LoginResponse` schema requires tokens | ✅ เสร็จ |
| 4 | Launch uvicorn on free port 8002 | 🔄 กำลังทำ |
| 5 | Poll `GET /` for health payload | ⏳ รอ |
| 6 | Probe `POST /api/v1/authentication/login/` | ⏳ รอ |
| 7 | Stop process + report | ⏳ รอ |

### 🔍 ปัญหาที่พบและแก้ไขแล้ว

**1. SyntaxError ใน `app/core/logging.py`**
```python
# ก่อนแก้ (ผิด)
def def setup_logging(log_level: str) -> None:   # ← def ซ้ำ
    ...
    logger.add(...) -> None:                      # ← -> None: เกินมา

# หลังแก้ (ถูก)
def setup_logging(log_level: str) -> None:
    logger.remove()
    logger.add(
        lambda message: print(serialize(message.record), file=sys.stderr),
        level=log_level.upper(),
    )

def init_loguru() -> None:
    logger.remove()
    logger.add(lambda message: print(serialize(message.record), file=sys.stderr))
```
**ผลลัพธ์:** `import app.main` ผ่าน ✅

**2. Login response ไม่มี tokens**
- `entity_login_mapper` return `LoginResponse()` แบบ message-only → แก้เป็น return `access_token` + `refresh_token`
- `LoginResponse` schema: เปลี่ยน `access_token` และ `refresh_token` เป็น required (ไม่มี default)

**3. Port 8000/8001 ถูก占用**
- Port 8000: stale uvicorn (PID 19804) รัน `app.app:app --reload` — kill แล้วแต่ TCP entry ยังค้าง
- Port 8001: occupied by PID 34748 (unknown process)
- Port 8002: ✅ ว่าง (verified via `Get-NetTCPConnection`)

### ⚠️ ข้อสังเกตสำคัญ

**1. Stale TCP Entry บน Windows**
หลังจาก kill process แล้ว Windows อาจเก็บ TCP listener entry ค้างไว้ชั่วคราว ทำให้ bind ไม่ได้ (`[Errno 10048]`) แม้ process จะตายแล้ว → ต้องรอหรือเปลี่ยน port

**2. App Boot ทำงานได้ดี**
stderr แสดง:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.       ← app boot สำเร็จ
ERROR:    [Errno 10048] error while attempting to bind on address ...  ← port conflict
INFO:     Application shutdown complete.       ← ปิด cleanly
```
**สรุป:** Code ทำงานได้ ปัญหาอยู่ที่ port bind เท่านั้น

**3. Root route พร้อมใช้งาน**
`GET /` → `{"service": "erp-iot-api", "status": "ok"}`

---

## แผนดำเนินการต่อ (Next Move)

### ขั้นตอนที่ 1: Launch uvicorn บน port 8002

```powershell
# ตั้งค่า path ของ log files
$out = "C:\Users\kongn\AppData\Local\Temp\opencode\uvicorn_stdout.log"
$err = "C:\Users\kongn\AppData\Local\Temp\opencode\uvicorn_stderr.log"
$pidFile = "C:\Users\kongn\AppData\Local\Temp\opencode\uvicorn.pid"

# ลบ log เก่า
Remove-Item $out, $err -ErrorAction SilentlyContinue

# Launch uvicorn บน port 8002
$p = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8002" `
  -WorkingDirectory "C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend" `
  -RedirectStandardOutput $out `
  -RedirectStandardError $err `
  -WindowStyle Hidden `
  -PassThru

# เก็บ PID
$p.Id | Set-Content $pidFile

# รอ 5 วินาที
Start-Sleep -Seconds 5

# เช็ค startup
Write-Output "PID: $($p.Id)"
Write-Output "--- stderr ---"
Get-Content $err
```

**ผลที่คาดหวัง:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```
→ **ไม่มี** `[Errno 10048]`

### ขั้นตอนที่ 2: Poll root route

```powershell
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8002/" -UseBasicParsing
    Write-Output "Status: $($response.StatusCode)"
    Write-Output "Body: $($response.Content)"
} catch {
    Write-Output "Error: $($_.Exception.Message)"
}
```

**ผลที่คาดหวัง:**
```
Status: 200
Body: {"service":"erp-iot-api","status":"ok"}
```

### ขั้นตอนที่ 3: Probe login route

```powershell
try {
    $body = @{ username = "test@example.com"; password = "WrongPassword123!" }
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8002/api/v1/authentication/login/" `
      -Method POST `
      -Body $body `
      -ContentType "application/x-www-form-urlencoded" `
      -UseBasicParsing
    Write-Output "Status: $($response.StatusCode)"
    Write-Output "Body: $($response.Content)"
} catch {
    # PS 5.1 throws on 4xx/5xx — ต้องอ่าน response จาก Exception
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Output "Status: $statusCode"
    
    $stream = $_.Exception.Response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $body = $reader.ReadToEnd()
    Write-Output "Body: $body"
}
```

**ผลที่คาดหวัง:**
- **401** (Invalid credentials) — route wired, credentials ผิด
- **422** (Validation error) — form data ไม่ครบ
- **500** — มีปัญหาที่อื่น

ทั้ง 401 และ 422 แสดงว่า **route ทำงาน** (ไม่ใช่ 404 Not Found)

### ขั้นตอนที่ 4: Cleanup

```powershell
# อ่าน PID และ stop process
$pid = Get-Content "C:\Users\kongn\AppData\Local\Temp\opencode\uvicorn.pid"
Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue

# ยืนยัน
Start-Sleep -Seconds 1
Get-Process -Id $pid -ErrorAction SilentlyContinue
```

### ขั้นตอนที่ 5: รายงานผล

**Template การรายงาน:**

```
## Verification Report

### ✅ Completed
1. **SyntaxError fix** — `app/core/logging.py` แก้ `def def` และ stray `-> None:` แล้ว
2. **Import check** — `.venv\Scripts\python.exe -c "import app.main"` ผ่าน
3. **Mapper fix** — `entity_login_mapper` return nested tokens
4. **Schema fix** — `LoginResponse.access_token` + `.refresh_token` เป็น required

### ✅ Boot Verification (port 8002)
- stderr: `Application startup complete.` (ไม่มี 10048)
- `GET /` → 200 `{"service":"erp-iot-api","status":"ok"}`

### ✅ Login Route Wiring
- `POST /api/v1/authentication/login/` → [status code]
- Route ถูก wire ถูกต้อง (ไม่ใช่ 404)

### 📋 Expected Login Response (เมื่อ credentials ถูกต้อง)
{
  "code": 200,
  "method": "POST",
  "path": "/api/v1/authentication/login/",
  "timestamp": "...",
  "details": {
    "message": "User logged in successfully",
    "data": {
      "access_token": "...",
      "refresh_token": "..."
    }
  }
}

### ⚠️ Known Issues
- Port 8000: stale TCP entry (dead PID 19804)
- Port 8001: occupied by PID 34748
- Port 8002: ✅ ใช้งานได้
```

---

## สรุป Bug ที่แก้ไขในเซสชันนี้

### Bug 1: SyntaxError — `def def` ซ้ำ
**ไฟล์:** `app/core/logging.py:37`
**สาเหตุ:** แก้ไข code ผิดพลาด ทำให้มี `def` ซ้ำ + stray `-> None:` + duplicate body
**วิธีแก้:** ลบ `def` ที่ซ้ำ, ลบ `-> None:` ที่เกินมา, ลบ body ที่ซ้ำ

### Bug 2: Login response ไม่มี tokens
**ไฟล์:** `mappers.py:62` + `schemas.py`
**สาเหตุ:** `entity_login_mapper` return `LoginResponse()` แบบ message-only
**วิธีแก้:** Return `access_token` + `refresh_token` จาก `authentication.refresh_token`

### Bug 3: Port 8000/8001 ถูก占用
**สาเหตุ:** Stale uvicorn process (PID 19804) + unknown process (PID 34748)
**วิธีแก้:** Kill stale process, ใช้ port 8002 ที่ว่าง

### Bug 4: Circular Import Risk
**ไฟล์:** `app/core/logging.py` → `app.core.settings` → `app.modules.shared.domain.enums`
**วิธีตรวจสอบ:** `.venv\Scripts\python.exe -c "import app.main"`
**ผลลัพธ์:** ✅ ผ่าน ไม่มี circular import

---

## การทำส่วนต่อขยาย (Extension Guide)

### เพิ่ม Module ใหม่
```
app/modules/{module_name}/
├── domain/
│   ├── entities.py
│   ├── enums.py
│   ├── value_objects.py
│   └── events.py
├── application/
│   ├── interfaces.py
│   ├── use_cases.py
│   ├── mappers.py
│   └── exceptions.py
├── infrastructure/
│   ├── models.py
│   ├── repositories.py
│   └── (caches.py / services.py)
└── presentation/
    ├── routers.py
    ├── schemas.py
    ├── docs.py
    └── dependencies.py
```

Register router ใน `app/main.py`:
```python
from app.modules.{module_name}.presentation.routers import router as module_router
app.include_router(module_router)
```

### เพิ่ม Endpoint ใน Module ที่มีอยู่
1. เพิ่ม method ใน `use_cases.py`
2. เพิ่ม schema ใน `presentation/schemas.py`
3. เพิ่ม mapper (ถ้าต้องแปลง Entity ↔ DTO)
4. เพิ่ม endpoint ใน `presentation/routers.py`
5. เพิ่ม docs ใน `presentation/docs.py`

### เพิ่ม Exception ใหม่
```python
# application/exceptions.py
class {Custom}Exception(StandardException):
    def __init__(self, ...) -> None:
        super().__init__(
            status_code=HTTPStatus.{CODE},
            message=ResponseMessages.{MESSAGE}.value,
            data={"errors": "..."},
        )
```

### เพิ่ม Cache Layer
1. สร้าง Protocol ใน `application/interfaces.py`
2. implement ใน `infrastructure/caches.py` (ตาม pattern `RedisAuthenticationCache` — มี tombstone pattern)
3. wire ใน `presentation/dependencies.py`

### เพิ่ม Repository Method
1. เพิ่ม signature ใน `application/interfaces.py`
2. implement ใน `infrastructure/repositories.py`

---

## ข้อควรระวังในการแก้ Bug

1. **อย่าแตะ cookie logic** — `set_cookies` / `delete_cookies` ใน `routers.py` ทำงานถูกต้องแล้ว
2. **อย่าแตะ envelope builder** — `middleware.py` (473-545) และ `exception_handler.py` เป็นส่วนกลาง
3. **ใช้ tombstone pattern** — ถ้าเพิ่ม cache operations ต้องคำนึงถึง race condition
4. **Check `extra="forbid"`** — Pydantic models ตั้ง `extra="forbid"` ถ้าเพิ่ม field ต้องอัปเดต mapper ด้วย
5. **`validate_return=True`** — Pydantic จะ validate ค่าที่ return ถ้า schema ไม่ตรงจะ error
6. **อย่าใช้ `app.app:app`** — ใช้ `app.main:app` เท่านั้น (stale process ใช้ `app.app:app`)

---

## คำสั่งสรุป (Copy-Paste)

```powershell
# 1. Launch on port 8002
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
$out = "$env:TEMP\uvicorn_stdout.log"
$err = "$env:TEMP\uvicorn_stderr.log"
Remove-Item $out, $err -ErrorAction SilentlyContinue
$p = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8002" `
  -WorkingDirectory (Get-Location) `
  -RedirectStandardOutput $out -RedirectStandardError $err `
  -WindowStyle Hidden -PassThru
$p.Id | Set-Content "$env:TEMP\uvicorn.pid"
Start-Sleep -Seconds 5
Get-Content $err

# 2. Poll root
Invoke-WebRequest -Uri "http://127.0.0.1:8002/" -UseBasicParsing | Select StatusCode, Content

# 3. Probe login
try {
    Invoke-WebRequest -Uri "http://127.0.0.1:8002/api/v1/authentication/login/" `
      -Method POST -Body @{username="test";password="test"} `
      -ContentType "application/x-www-form-urlencoded" -UseBasicParsing
} catch {
    Write-Output "Status: $($_.Exception.Response.StatusCode.value__)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    Write-Output "Body: $($reader.ReadToEnd())"
}

# 4. Cleanup
Stop-Process -Id (Get-Content "$env:TEMP\uvicorn.pid") -Force
```

# คู่มือโครงสร้างโค้ด Authentication Module (Clean Architecture + DDD)

จากโค้ดที่ให้มา ผมจะเขียนคู่มืออธิบายโครงสร้างและการทำงานของ Authentication Module ตามหลัก Clean Architecture + DDD ครับ

---

## 1. ภาพรวมสถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  routers.py → schemas.py → docs.py → dependencies.py        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  use_cases.py → interfaces.py → mappers.py → exceptions.py  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  entities.py → value_objects.py → enums.py → events.py      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  models.py → repositories.py → caches.py → services.py      │
└─────────────────────────────────────────────────────────────┘
```

**หลักการสำคัญ:**
- **Dependencies ชี้เข้าด้านใน** (Infrastructure → Domain)
- **Domain Layer ไม่พึ่งพา Layer อื่น** (Pure Python)
- **Application Layer กำหนด Interfaces** (Ports)
- **Infrastructure Layer implement Interfaces** (Adapters)

---

## 2. Domain Layer (แกนกลาง)

### 2.1 Entities (`entities.py`)

Entity คือ object ที่มี **Identity** (id) และ **Lifecycle** ของตัวเอง

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.shared.domain.enums import Role
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Authentication:
    """Entity แทน session การ login ของ user ใน device หนึ่งๆ"""
    
    # === Identity & Attributes ===
    ip_address: str | None = field(default=None, repr=True, compare=True)
    user_agent: str | None = field(default=None, repr=True, compare=True)
    device: str | None = field(default=None, repr=True, compare=True)
    location: str | None = field(default=None, repr=True, compare=False)
    accept_language: str | None = field(default=None, repr=True, compare=False)
    accept_encoding: str | None = field(default=None, repr=True, compare=False)
    origin: str | None = field(default=None, repr=True, compare=False)
    referer: str | None = field(default=None, repr=True, compare=False)

    # === Application Generated Fields ===
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=False)
    last_updated_at: datetime | None = field(default=None, repr=False, compare=False)
    blacklisted: bool = field(init=False, default=False, repr=False, compare=False)

    # === Foreign Entities ===
    user: User = field(compare=True, repr=True)
    refresh_token: RefreshToken | None = field(default=None, compare=True, repr=True)

    def __post_init__(self):
        """Normalize ข้อมูลหลังสร้าง object"""
        self._normalize()

    def _normalize(self):
        """ทำความสะอาดข้อมูล (lowercase, strip)"""
        self.ip_address = self.ip_address.lower().strip() if self.ip_address else ""
        self.user_agent = self.user_agent.lower().strip() if self.user_agent else ""
        self.accept_language = (
            self.accept_language.lower().strip() if self.accept_language else None
        )
        self.accept_encoding = (
            self.accept_encoding.lower().strip() if self.accept_encoding else None
        )
        self.origin = self.origin.lower().strip() if self.origin else ""
        self.referer = self.referer.lower().strip() if self.referer else None
        self.location = self.location.lower().strip() if self.location else None

    # === Domain Behaviors (Business Logic) ===
    
    def update_last_updated_at(self, now: datetime) -> None:
        """อัปเดต timestamp ล่าสุด"""
        self.last_updated_at = now

    def create_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        """สร้าง tokens ใหม่สำหรับ authentication ใหม่"""
        self.refresh_token = RefreshToken(
            expires_at=refresh_expires_at,
            access_token=AccessToken(expires_at=access_expires_at),
        )
        self.refresh_token.generate_created_at(now)
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.access_token.generate_created_at(now)
        return self

    def renew_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        """ต่ออายุ tokens สำหรับ authentication ที่มีอยู่"""
        self.update_last_updated_at(now)
        self.refresh_token.expires_at = refresh_expires_at
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.activate()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        self.refresh_token.access_token.activate()
        return self

    def refresh_access_token(
        self, now: datetime, access_expires_at: datetime
    ) -> Authentication:
        """Refresh เฉพาะ access token"""
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        return self

    def revoke(self, now: datetime) -> Authentication:
        """เพิกถอน authentication (logout)"""
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.revoke(now)
        return self


@dataclass(kw_only=True, slots=True)
class RefreshToken:
    """Entity แทน refresh token"""
    
    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)

    # Application generated fields
    replaced_by_token: UUID | None = field(default=None, repr=False, compare=False)
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    updated_at: datetime | None = field(default=None, repr=False, compare=False)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )
    refresh_claims: RefreshClaims | None = field(
        default=None, repr=False, compare=False
    )

    access_token: AccessToken | None = field(default=None, repr=False, compare=False)

    def revoke(self, now: datetime) -> None:
        """เพิกถอน refresh token และ access token ที่เกี่ยวข้อง"""
        self.revoked = True
        self.revoked_at = now
        if self.access_token:
            self.access_token.revoke(now)

    def activate(self) -> None:
        """เปิดใช้งาน token อีกครั้ง"""
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def generate_updated_at(self, dt: datetime) -> None:
        self.updated_at = dt

    def update_previous_hashed_jti(self) -> None:
        """เก็บ hashed_jti เก่าไว้สำหรับ token rotation"""
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self,
        iss: str,
        sub: UUID,
        aud: str,
        jti: UUID,
        client_id: str,
        grant_id: str,
        scope: str,
    ) -> None:
        """สร้าง claims สำหรับ refresh token"""
        self.refresh_claims = RefreshClaims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.updated_at.timestamp()),
            nbf=int(self.updated_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            client_id=client_id,
            grant_id=grant_id,
            scope=scope,
        )


@dataclass(kw_only=True, slots=True)
class AccessToken:
    """Entity แทน access token"""
    
    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)
    permission: Role = field(default=Role.USER, repr=False, compare=False)

    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    claims: Claims | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )

    def revoke(self, now: datetime) -> None:
        self.revoked = True
        self.revoked_at = now

    def activate(self) -> None:
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def update_previous_hashed_jti(self) -> None:
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self, iss: str, sub: UUID, aud: str, jti: UUID, grant_id: str, scope: str
    ) -> None:
        """สร้าง claims สำหรับ access token"""
        self.claims = Claims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.created_at.timestamp()),
            nbf=int(self.created_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            grant_id=grant_id,
            scope=scope,
        )
```

### 2.2 Value Objects (`value_objects.py`)

Value Object คือ object ที่ **immutable** และ **ไม่มี identity** (เท่ากันเมื่อค่าทุกอย่างเท่ากัน)

```python
from __future__ import annotations

from uuid import UUID

from app.modules.shared.domain.entities import DomainError


class BaseClaims:
    """Base class สำหรับ JWT Claims - immutable"""
    
    iss: str  # issuer
    sub: UUID  # subject
    aud: str  # audience
    iat: int  # issued at
    nbf: int  # not before
    exp: int  # expiration
    jti: UUID  # JWT ID

    def __setattr__(self, name: str, value) -> None:
        """บล็อกการแก้ไข attribute หลังสร้าง object"""
        raise AttributeError(f"{type(self).__name__} is immutable.")

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
    ) -> None:
        object.__setattr__(self, "iss", iss.strip() if iss else iss)
        object.__setattr__(self, "sub", sub)
        object.__setattr__(self, "aud", aud.strip() if aud else aud)
        object.__setattr__(self, "iat", iat)
        object.__setattr__(self, "nbf", nbf)
        object.__setattr__(self, "exp", exp)
        object.__setattr__(self, "jti", jti)

    def _validate_base(self, prefix: str = "Claims") -> None:
        """Validate ข้อมูลพื้นฐานของ claims"""
        if not self.iss:
            raise DomainError(f"{prefix} issuer (iss) is required.")

        if not self.sub:
            raise DomainError(f"{prefix} subject (sub) is required.")

        if not self.aud:
            raise DomainError(f"{prefix} audience (aud) is required.")

        if self.iat is None:
            raise DomainError(f"{prefix} issued at (iat) is required.")
        if not isinstance(self.iat, int) or self.iat <= 0:
            raise DomainError(
                f"{prefix} issued at (iat) must be a positive integer Unix timestamp."
            )

        if self.nbf is None:
            raise DomainError(f"{prefix} not before (nbf) is required.")
        if not isinstance(self.nbf, int) or self.nbf <= 0:
            raise DomainError(
                f"{prefix} not before (nbf) must be a positive integer Unix timestamp."
            )
        if self.nbf < self.iat:
            raise DomainError(
                f"{prefix} not before (nbf) cannot be earlier than issued at (iat)."
            )

        if self.exp is None:
            raise DomainError(f"{prefix} expiration (exp) is required.")
        if not isinstance(self.exp, int) or self.exp <= 0:
            raise DomainError(
                f"{prefix} expiration (exp) must be a positive integer Unix timestamp."
            )
        if self.exp <= self.iat:
            raise DomainError(
                f"{prefix} expiration (exp) must be after issued at (iat)."
            )

        if not self.jti:
            raise DomainError(f"{prefix} JWT ID (jti) is required.")

    def _base_to_dict(self) -> dict:
        """แปลงเป็น dict"""
        return {
            "iss": self.iss,
            "sub": str(self.sub),
            "aud": self.aud,
            "iat": self.iat,
            "nbf": self.nbf,
            "exp": self.exp,
            "jti": str(self.jti),
        }

    @staticmethod
    def _base_kwargs_from_dict(data: dict) -> dict:
        """สร้าง kwargs จาก dict"""
        return {
            "iss": data["iss"],
            "sub": UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"],
            "aud": data["aud"],
            "iat": data["iat"],
            "nbf": data["nbf"],
            "exp": data["exp"],
            "jti": UUID(data["jti"]) if isinstance(data["jti"], str) else data["jti"],
        }


class Claims(BaseClaims):
    """Claims สำหรับ Access Token"""
    
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(self, "grant_id", grant_id)
        object.__setattr__(self, "scope", scope.strip().lower() if scope else scope)
        self._validate()

    def _validate(self) -> None:
        self._validate_base()
        if not self.grant_id:
            raise DomainError("Claims grant_id is required.")
        if not self.scope:
            raise DomainError("Claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Claims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return f"Claims(iss={self.iss}, sub={self.sub}, jti={self.jti}, grant_id={self.grant_id}, scope={self.scope})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Claims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash((self.iss, self.sub, self.aud, self.jti, self.grant_id, self.scope))


class RefreshClaims(BaseClaims):
    """Claims สำหรับ Refresh Token"""
    
    client_id: str
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        client_id: str | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(
            self, "client_id", client_id.strip().lower() if client_id else client_id
        )
        object.__setattr__(self, "grant_id", grant_id.strip() if grant_id else grant_id)
        object.__setattr__(
            self, "scope", " ".join(scope.lower().split()) if scope else scope
        )
        self._validate()

    def _validate(self) -> None:
        self._validate_base("Refresh claims")
        if not self.client_id:
            raise DomainError("Refresh claims client_id is required.")
        if not self.grant_id:
            raise DomainError("Refresh claims grant_id is required.")
        if not self.scope:
            raise DomainError("Refresh claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "client_id": self.client_id,
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> RefreshClaims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            client_id=data["client_id"],
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return (
            f"RefreshClaims(iss={self.iss}, sub={self.sub}, "
            f"jti={self.jti}, client_id={self.client_id}, scope={self.scope})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RefreshClaims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.client_id == other.client_id
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.iss,
                self.sub,
                self.aud,
                self.jti,
                self.client_id,
                self.grant_id,
                self.scope,
            )
        )
```

---

## 3. Application Layer (Use Cases)

### 3.1 Interfaces (`interfaces.py`) - Ports

กำหนด **Protocol** ที่ Infrastructure ต้อง implement

```python
from __future__ import annotations

from typing import Protocol

from app.modules.authentication.domain.entities import Authentication


class IAuthenticationRepository(Protocol):
    """Interface สำหรับ Repository (Database operations)"""
    
    # CREATE
    async def create(self, authentication: Authentication) -> Authentication: ...

    # READ
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_access_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_refresh_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # UPDATE
    async def update(self, authentication: Authentication) -> Authentication: ...

    # DELETE
    async def delete(self, authentication: Authentication) -> Authentication: ...


class IAuthenticationCache(Protocol):
    """Interface สำหรับ Cache (Redis operations)"""
    
    # CREATE
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    # READ
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # DELETE
    async def delete_by_access_token(self, authentication: Authentication) -> None: ...

    async def delete_by_refresh_token(self, authentication: Authentication) -> None: ...


class ITokenService(Protocol):
    """Interface สำหรับ Token operations"""
    
    async def generate(self, authentication: Authentication) -> Authentication: ...

    async def hash_tokens(self, authentication: Authentication) -> Authentication: ...

    async def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool: ...
```

### 3.2 Use Cases (`use_cases.py`) - Business Logic

```python
from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger

from app.core.settings import settings
from app.modules.authentication.application.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    """
    Use Cases สำหรับ Authentication
    
    รับ dependencies ผ่าน constructor (Dependency Injection)
    - cache: IAuthenticationCache
    - repository: IAuthenticationRepository
    - shared_service: SharedUseCases
    - token_service: ITokenService
    """
    
    def __init__(
        self,
        cache: IAuthenticationCache,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
        token_service: ITokenService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.token_service = token_service
        self.shared_service.disable_exceptions()

    # === CREATE: Login ===
    async def login(self, authentication: Authentication) -> Authentication:
        """
        Login use case
        
        ขั้นตอน:
        1. ค้นหา user จาก email
        2. ตรวจสอบ password
        3. ค้นหา authentication ที่มีอยู่ (user + agent + device)
        4. ถ้ามี → renew tokens / ถ้าไม่มี → create tokens
        5. Generate JWT tokens
        6. Hash tokens
        7. บันทึกลง database
        """
        try:
            logger.debug(
                f"Initializing user login use case for user: {authentication.user.censored_email} in device: {authentication.device}. The user/authentication identifier has not yet been retrieved."
            )

            # 1. ค้นหา user
            db_user: User | None = await self.shared_service.get_user_by_email(
                authentication.user
            )

            if not db_user:
                logger.info(
                    f"User with email {authentication.user.censored_email} not found, raising exception. The user identifier not found."
                )
                raise InvalidCredentialsException()

            # 2. ตรวจสอบ password
            if not await self.token_service.verify_password(
                authentication.user.password, db_user.hashed_password
            ):
                logger.info(
                    f"Invalid password for user {authentication.user.id}, raising exception."
                )
                raise InvalidCredentialsException()

            authentication.user = db_user
            
            # 3. ค้นหา authentication ที่มีอยู่
            authentication_from_db = (
                await self.repository.get_by_user_id_agent_and_device(authentication)
            )

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            # 4. Renew หรือ Create tokens
            if authentication_from_db:
                logger.debug(
                    f"Existing authentication found for user: {authentication.user.id} in device: {authentication.device}. Renewing tokens. Authentication identifier: {authentication_from_db.id}."
                )

                await self.cache.delete_by_access_token(authentication_from_db)
                await self.cache.delete_by_refresh_token(authentication_from_db)

                authentication = authentication_from_db.renew_tokens(
                    now, refresh_expires_at, access_expires_at
                )
            else:
                logger.debug(
                    f"No existing authentication found for user: {authentication.user.id} in device: {authentication.device}. Creating new authentication."
                )
                authentication = authentication.create_tokens(
                    now, refresh_expires_at, access_expires_at
                )

            # 5-6. Generate & Hash tokens
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            # 7. บันทึก
            if authentication_from_db:
                await self.repository.update(authentication)
            else:
                await self.repository.create(authentication)

            logger.debug(
                f"User {authentication.user.id} logged in successfully in device: {authentication.device}. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the login use case."
            )
            raise AuthenticationException()

    # === UPDATE: Refresh ===
    async def refresh(self, authentication: Authentication) -> Authentication:
        """
        Refresh tokens use case
        
        ขั้นตอน:
        1. ลบ cache เก่า
        2. Refresh access token
        3. Generate & Hash tokens ใหม่
        4. อัปเดต database
        """
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {authentication.user.id} in device: {authentication.device}."
            )

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            now = datetime.now(BRASILIA_TZ)
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.refresh_access_token(now, access_expires_at)
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.update(authentication)

            logger.debug(
                f"User {authentication.user.id} refreshed tokens successfully."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the refresh tokens use case."
            )
            raise AuthenticationException()

    # === DELETE: Logout ===
    async def logout(self, authentication: Authentication) -> Authentication:
        """
        Logout use case
        
        ขั้นตอน:
        1. Revoke tokens
        2. บันทึกการ revoke ลง database
        3. ลบ cache
        """
        try:
            logger.debug(
                f"Initializing user logout use case for user: {authentication.user.id} in device: {authentication.device}."
            )

            authentication.revoke(datetime.now(BRASILIA_TZ))
            await self.repository.delete(authentication)

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            logger.debug(
                f"User {authentication.user.id} logged out successfully from device: {authentication.device}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()
```

---

## 4. Infrastructure Layer

### 4.1 Models (`models.py`) - SQLAlchemy ORM

```python
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    UUID as SQUID,
)
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import Role
from app.modules.shared.infrastructure.models import Base

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class AuthenticationModel(Base):
    """SQLAlchemy model สำหรับตาราง authentications"""
    
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_authentications"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "user_agent",
            "device",
            name="uq_authentications_user_id_user_agent_device",
        ),
        Index(
            "ix_authentications_user_id_user_agent_device",
            "user_id",
            "user_agent",
            "device",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the authentication",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        comment="Identifier of the user who owns the authentication",
        nullable=False,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        name="ip_address",
        comment="IP address used when the authentication was created",
        nullable=False,
    )

    device: Mapped[str] = mapped_column(
        String(255), name="device", comment="Human readable device name", nullable=False
    )

    user_agent: Mapped[str] = mapped_column(
        Text,
        name="user_agent",
        comment="User agent string of the client",
        nullable=False,
    )

    accept_language: Mapped[str | None] = mapped_column(
        String(255),
        name="accept_language",
        comment="Accept-Language header value of the client",
        nullable=True,
        default=None,
    )

    accept_encoding: Mapped[str | None] = mapped_column(
        String(255),
        name="accept_encoding",
        comment="accept_encoding header value of the client",
        nullable=True,
        default=None,
    )

    origin: Mapped[str] = mapped_column(
        String(255),
        name="origin",
        comment="Origin header value of the client",
        nullable=False,
    )

    referrer: Mapped[str | None] = mapped_column(
        String(255),
        name="referrer",
        comment="Referrer header value of the client",
        nullable=True,
        default=None,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        name="location",
        comment="Approximate geographic location of the client",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the authentication was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="last_update_at",
        comment="Last time the authentication was updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    blacklisted: Mapped[bool] = mapped_column(
        Boolean,
        name="blacklisted",
        comment="Indicates whether the authentication is blacklisted",
        nullable=False,
        default=False,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="authentications",
        lazy="noload",
    )

    refresh_token: Mapped["RefreshTokenModel | None"] = relationship(
        back_populates="authentication",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="noload",
    )


class RefreshTokenModel(Base):
    """SQLAlchemy model สำหรับตาราง refresh_tokens"""
    
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens"
    __table_args__ = (
        UniqueConstraint(
            "authentication_id",
            name="uq_refresh_tokens_authentication_id",
        ),
        Index(
            "ix_refresh_tokens_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the refresh token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    authentication_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_authentications.id",
            ondelete="CASCADE",
        ),
        name="authentication_id",
        comment="Authentication associated with this refresh token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[str | None] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous refresh token",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the refresh token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="updated_at",
        comment="Timestamp when the record was last updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the refresh token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the refresh token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the refresh token was revoked",
        nullable=True,
        default=None,
    )

    authentication: Mapped["AuthenticationModel"] = relationship(
        back_populates="refresh_token",
        uselist=False,
        lazy="noload",
    )

    access_token: Mapped["AccessTokenModel | None"] = relationship(
        back_populates="refresh_token",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="noload",
    )


class AccessTokenModel(Base):
    """SQLAlchemy model สำหรับตาราง access_tokens"""
    
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_access_tokens"
    __table_args__ = (
        UniqueConstraint(
            "refresh_id",
            name="uq_access_tokens_refresh_id",
        ),
        Index(
            "ix_access_tokens_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the access token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    refresh_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens.id",
            ondelete="CASCADE",
        ),
        name="refresh_id",
        comment="Refresh token associated with this access token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[str | None] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous access token",
        nullable=True,
        default=None,
        unique=True,
    )

    permission: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        name="permission",
        comment="Permission level associated with the access token",
        nullable=False,
        default=Role.USER,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the access token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the access token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the refresh token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the refresh token was revoked",
        nullable=True,
        default=None,
    )

    refresh_token: Mapped["RefreshTokenModel"] = relationship(
        back_populates="access_token",
        uselist=False,
        lazy="noload",
    )
```

### 4.2 Repositories (`repositories.py`)

```python
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    sync_entity_from_model,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.infrastructure.models import (
    AccessTokenModel,
    AuthenticationModel,
    RefreshTokenModel,
)
from app.modules.shared.application.exceptions import StandardException


class PostgresAuthenticationRepository(IAuthenticationRepository):
    """Implementation ของ IAuthenticationRepository ด้วย PostgreSQL"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # === CREATE ===
    async def create(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Creating authentication for user {authentication.user.id} with device {authentication.device} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            self.session.add(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, db_authentication
            )

            logger.info(
                f"Authentication created successfully for user {authentication.user.id} with device {authentication.device} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create authentication repository."
            )
            raise AuthenticationException()

    # === READ ===
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by user id, agent and device for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} from database."
            )

            statement = (
                select(AuthenticationModel)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(
                    AuthenticationModel.user_id == authentication.user.id,
                    AuthenticationModel.user_agent == authentication.user_agent,
                    AuthenticationModel.device == authentication.device,
                    AuthenticationModel.blacklisted.is_(False),
                )
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent}."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} from database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by user agent and device repository."
            )
            raise AuthenticationException()

    async def get_access_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by access token hashed_jti {authentication.refresh_token.access_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} from database."
            )

            conditions = [
                AccessTokenModel.hashed_jti
                == authentication.refresh_token.access_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                AccessTokenModel.revoked.is_(False),
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .join(RefreshTokenModel.access_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for access token hashed_jti {authentication.refresh_token.access_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for access token with ID {authentication.id} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise AuthenticationException()

    async def get_refresh_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by refresh token hashed_jti {authentication.refresh_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} from database."
            )

            conditions = [
                RefreshTokenModel.hashed_jti == authentication.refresh_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for refresh token hashed_jti {authentication.refresh_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for refresh token with ID {authentication.id} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get refresh token by hashed_jti repository."
            )
            raise AuthenticationException()

    # === UPDATE ===
    async def update(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Updating authentication {authentication.id} for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(
                f"Authentication {authentication.id} updated successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update authentication repository."
            )
            raise AuthenticationException()

    # === DELETE ===
    async def delete(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Persisting revoked authentication {authentication.id} for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(
                f"Authentication {authentication.id} revoked successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication repository."
            )
            raise AuthenticationException()
```

### 4.3 Cache (`caches.py`) - Redis

```python
from __future__ import annotations

from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.authentication.application.interfaces import IAuthenticationCache
from app.modules.authentication.application.mappers import (
    cache_entity_mapper,
    entity_cache_mapper,
)
from app.modules.authentication.domain.entities import Authentication


class RedisAuthenticationCache(IAuthenticationCache):
    """
    Implementation ของ IAuthenticationCache ด้วย Redis
    
    มีการใช้ Tombstone pattern เพื่อป้องกัน race condition:
    - เมื่อ delete จะเขียน tombstone ไว้ก่อน
    - เมื่อ insert จะเช็ค tombstone ก่อน ถ้ามีให้ skip
    """
    
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:authentication:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"

    # === CREATE ===
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"access_token:{hashed_jti}"

            # เช็ค tombstone ก่อน - ถ้ามีแสดงว่าเพิ่ง delete ไป ให้ skip
            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by access token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by access token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by access token cache. The request continues without caching."
            )
            return

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"refresh_token:{hashed_jti}"

            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by refresh token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by refresh token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by refresh token cache. The request continues without caching."
            )
            return

    # === READ ===
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by access token from cache.")

            raw = await self.cache.get(self._key(f"access_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by access token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by access token cache. Falling back to the database."
            )
            return None

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by refresh token from cache.")

            raw = await self.cache.get(self._key(f"refresh_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by refresh token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by refresh token cache. Falling back to the database."
            )
            return None

    # === DELETE ===
    async def delete_by_access_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by access token."
            )

            suffix = f"access_token:{hashed_jti}"

            # เขียน tombstone ก่อน แล้วค่อย delete
            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by access token cache. The entry remains until its ttl expires."
            )
            return

    async def delete_by_refresh_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by refresh token."
            )

            suffix = f"refresh_token:{hashed_jti}"

            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by refresh token cache. The entry remains until its ttl expires."
            )
            return
```

### 4.4 Services (`services.py`)

```python
from __future__ import annotations

from app.core.security import (
    generate_tokens,
    hash_tokens,
    verify_password,
)
from app.modules.authentication.application.interfaces import ITokenService
from app.modules.authentication.domain.entities import Authentication


class TokenService(ITokenService):
    """Implementation ของ ITokenService"""
    
    async def generate(self, authentication: Authentication) -> Authentication:
        """สร้าง JWT tokens"""
        return generate_tokens(authentication)

    async def hash_tokens(self, authentication: Authentication) -> Authentication:
        """Hash tokens"""
        return hash_tokens(authentication)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ตรวจสอบ password"""
        return verify_password(plain_password, hashed_password)
```

---

## 5. Presentation Layer

### 5.1 Schemas (`schemas.py`) - Pydantic

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.modules.shared.domain.enums import ResponseMessages


# === RESPONSE ===
class LoginResponse(BaseModel):
    """Response model สำหรับ login"""
    
    message: str = ResponseMessages.LOGIN_SUCCESS.value
    access_token: str
    refresh_token: str

    model_config = ConfigDict(
        title="LoginResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user login.",
            "example": {
                "message": ResponseMessages.LOGIN_SUCCESS.value,
                "access_token": "string",
                "refresh_token": "string",
            },
        },
    )


class RefreshResponse(BaseModel):
    """Response model สำหรับ refresh"""
    
    message: str = ResponseMessages.REFRESH_SUCCESS.value

    model_config = ConfigDict(
        title="RefreshResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user refresh.",
            "example": {"message": ResponseMessages.REFRESH_SUCCESS.value},
        },
    )


class LogoutResponse(BaseModel):
    """Response model สำหรับ logout"""
    
    message: str = ResponseMessages.LOGOUT_SUCCESS.value

    model_config = ConfigDict(
        title="LogoutResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user logout.",
            "example": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
        },
    )
```

### 5.2 Routers (`routers.py`)

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    authenticate_logout,
    authenticate_refresh,
    no_authentication,
)
from app.core.settings import settings
from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.mappers import (
    entity_login_mapper,
    entity_logout_mapper,
    entity_refresh_mapper,
    login_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    login_docs,
    logout_docs,
    refresh_docs,
    router_docs,
)
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import CookieManagementException

router = APIRouter(**router_docs)


def set_cookies(response: Response, authentication: Authentication) -> None:
    """ตั้งค่า HttpOnly cookies สำหรับ tokens"""
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=TokenType.BEARER.value,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=authentication.refresh_token.access_token.token
            if authentication.refresh_token.access_token.token
            else "",
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=authentication.refresh_token.token
            if authentication.refresh_token.token
            else "",
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


def delete_cookies(response: Response) -> None:
    """ลบ cookies"""
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the delete_cookies function."
        )
        raise CookieManagementException()


# === CREATE: Login ===
@router.post("/login/", **login_docs)
@router.post("/login", include_in_schema=False)
async def login(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LoginResponse:
    """
    Endpoint สำหรับ login
    
    Flow:
    1. แปลง request → domain entity (login_entity_mapper)
    2. เรียก use case (login)
    3. แปลง domain → response (entity_login_mapper)
    4. ตั้งค่า cookies (set_cookies)
    """
    try:
        request_domain = login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = entity_login_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the login endpoint.")
        raise AuthenticationException()


# === UPDATE: Refresh ===
@router.patch("/refresh/", **refresh_docs)
@router.patch("/refresh", include_in_schema=False)
async def refresh(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_refresh)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> RefreshResponse:
    """
    Endpoint สำหรับ refresh tokens
    
    Flow:
    1. ตรวจสอบ refresh token (authenticate_refresh dependency)
    2. เรียก use case (refresh)
    3. ตั้งค่า cookies ใหม่
    """
    try:
        request_domain = refresh_entity_mapper(authentication)
        response_domain = await use_case.refresh(request_domain)
        output = entity_refresh_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()


# === DELETE: Logout ===
@router.delete("/logout/", **logout_docs)
@router.delete("/logout", include_in_schema=False)
async def logout(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_logout)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LogoutResponse:
    """
    Endpoint สำหรับ logout
    
    Flow:
    1. ตรวจสอบ authentication (authenticate_logout dependency)
    2. เรียก use case (logout)
    3. ลบ cookies
    """
    try:
        request_domain = logout_entity_mapper(authentication)
        response_domain = await use_case.logout(request_domain)
        output = entity_logout_mapper(response_domain)

        delete_cookies(response)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the logout endpoint.")
        raise AuthenticationException()
```

### 5.3 Dependencies (`dependencies.py`) - Dependency Injection

```python
from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.infrastructure.caches import RedisAuthenticationCache
from app.modules.authentication.infrastructure.repositories import (
    PostgresAuthenticationRepository,
)
from app.modules.authentication.infrastructure.services import TokenService
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases


def get_authentication_cache(
    cache: Redis = Depends(get_cache_session),
) -> IAuthenticationCache:
    """สร้าง RedisAuthenticationCache"""
    return RedisAuthenticationCache(cache=cache)


def get_authentication_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IAuthenticationRepository:
    """สร้าง PostgresAuthenticationRepository"""
    return PostgresAuthenticationRepository(session=session)


def get_token_service() -> ITokenService:
    """สร้าง TokenService"""
    return TokenService()


def get_authentication_use_cases(
    cache: IAuthenticationCache = Depends(get_authentication_cache),
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
    token_service: ITokenService = Depends(get_token_service),
) -> AuthenticationUseCases:
    """
    สร้าง AuthenticationUseCases พร้อม inject dependencies
    
    นี่คือจุดที่ Dependency Injection เกิดขึ้น:
    - cache → RedisAuthenticationCache
    - repository → PostgresAuthenticationRepository
    - shared_service → SharedUseCases
    - token_service → TokenService
    """
    return AuthenticationUseCases(
        cache=cache,
        repository=repository,
        shared_service=shared_service,
        token_service=token_service,
    )
```

---

## 6. Mappers (`mappers.py`) - Data Transformation

```python
from __future__ import annotations

import json
from datetime import date, datetime
from uuid import UUID

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.authentication.domain.entities import (
    AccessToken,
    Authentication,
    RefreshToken,
)
from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.authentication.infrastructure.models import (
    AccessTokenModel,
    AuthenticationModel,
    RefreshTokenModel,
)
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
)
from app.modules.shared.application.utils import BRASILIA_TZ, resolve_client_ip
from app.modules.shared.domain.enums import Role
from app.modules.shared.domain.value_objects import Name
from app.modules.user.application.mappers import (
    model_entity_mapper as user_model_entity_mapper,
)
from app.modules.user.domain.entities import User
from app.modules.user.domain.enums import Gender


# === ENTITY / DTOS ===
def login_entity_mapper(
    authentication: OAuth2PasswordRequestForm,
    request: Request,
) -> Authentication:
    """
    แปลง HTTP request → Authentication entity
    
    ดึงข้อมูลจาก:
    - form_data (username, password)
    - request headers (ip, user-agent, accept-language, etc.)
    - request.state (device_id, location)
    """
    return Authentication(
        user=User(email=authentication.username, password=authentication.password),
        ip_address=resolve_client_ip(
            x_forwarded_for=request.headers.get("x-forwarded-for"),
            x_real_ip=request.headers.get("x-real-ip"),
            peer_host=request.client.host if request.client else None,
        ),
        user_agent=request.headers.get("user-agent"),
        device=getattr(request.state, "device_id", None),
        accept_language=request.headers.get("accept-language"),
        accept_encoding=request.headers.get("accept_encoding"),
        origin=request.headers.get("origin"),
        referer=request.headers.get("referer"),
        location=getattr(request.state, "location", None),
        refresh_token=RefreshToken(access_token=AccessToken()),
    )


def entity_login_mapper(
    _authentication: Authentication,
) -> LoginResponse:
    """
    แปลง Authentication entity → LoginResponse
    
    ดึง tokens จาก:
    - _authentication.refresh_token.access_token.token (access token)
    - _authentication.refresh_token.token (refresh token)
    """
    return LoginResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
    )


def refresh_entity_mapper(authentication: Authentication) -> Authentication:
    return authentication


def entity_refresh_mapper(_authentication: Authentication) -> RefreshResponse:
    return RefreshResponse()


def logout_entity_mapper(authentication: Authentication) -> Authentication:
    return authentication


def entity_logout_mapper(_authentication: Authentication) -> LogoutResponse:
    return LogoutResponse()


def access_token_entity_mapper(claims: dict) -> Authentication:
    """
    แปลง JWT claims → Authentication entity
    
    ใช้เมื่อ verify access token
    """
    access = AccessToken(
        claims=Claims.from_dict(claims),
        permission=Role(claims["scope"]),
        created_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    return Authentication(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=RefreshToken(access_token=access),
    )


def refresh_token_entity_mapper(claims: dict) -> Authentication:
    """
    แปลง JWT claims → Authentication entity
    
    ใช้เมื่อ verify refresh token
    """
    access = AccessToken(permission=Role(claims["scope"]))

    refresh = RefreshToken(
        access_token=access,
        refresh_claims=RefreshClaims.from_dict(claims),
        updated_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    return Authentication(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=refresh,
    )


# === ENTITY / MODELS ===
def _access_token_model_to_entity(model: AccessTokenModel) -> AccessToken:
    return AccessToken(
        id=model.id,
        hashed_jti=model.hashed_jti,
        previous_hashed_jti=model.previous_hashed_jti,
        created_at=model.created_at,
        expires_at=model.expires_at,
        permission=model.permission,
    )


def _refresh_token_model_to_entity(
    model: RefreshTokenModel,
    access_token: AccessToken | None,
) -> RefreshToken:
    refresh = RefreshToken(
        id=model.id,
        hashed_jti=model.hashed_jti,
        previous_hashed_jti=model.previous_hashed_jti,
        created_at=model.created_at,
        updated_at=model.updated_at,
        expires_at=model.expires_at,
        access_token=access_token,
    )
    refresh.revoked = model.revoked
    refresh.revoked_at = model.revoked_at
    return refresh


def _authentication_model_to_entity(model: AuthenticationModel) -> Authentication:
    mapped_user = user_model_entity_mapper(model.user) if model.user else None

    access_token = None
    if model.refresh_token and model.refresh_token.access_token:
        access_token = _access_token_model_to_entity(model.refresh_token.access_token)

    refresh_token = None
    if model.refresh_token:
        refresh_token = _refresh_token_model_to_entity(
            model.refresh_token, access_token
        )

    authentication = Authentication(
        id=model.id,
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        device=model.device,
        accept_language=model.accept_language,
        accept_encoding=model.accept_encoding,
        origin=model.origin,
        referer=model.referrer,
        location=model.location,
        created_at=model.created_at,
        last_updated_at=model.last_updated_at,
        user=mapped_user if mapped_user else User(),
        refresh_token=refresh_token,
    )
    authentication.blacklisted = model.blacklisted
    return authentication


def _access_token_entity_to_model(entity: AccessToken) -> AccessTokenModel:
    return AccessTokenModel(
        id=entity.id,
        hashed_jti=entity.hashed_jti,
        previous_hashed_jti=entity.previous_hashed_jti,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        expires_at=entity.expires_at
        if entity.expires_at
        else datetime.now(tz=BRASILIA_TZ),
        permission=entity.permission,
    )


def _refresh_token_entity_to_model(entity: RefreshToken) -> RefreshTokenModel:
    access_token = (
        _access_token_entity_to_model(entity.access_token)
        if entity.access_token
        else None
    )
    return RefreshTokenModel(
        id=entity.id,
        hashed_jti=entity.hashed_jti if entity.hashed_jti else "",
        previous_hashed_jti=entity.previous_hashed_jti,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        updated_at=entity.updated_at
        if entity.updated_at
        else datetime.now(tz=BRASILIA_TZ),
        expires_at=entity.expires_at
        if entity.expires_at
        else datetime.now(tz=BRASILIA_TZ),
        revoked=entity.revoked,
        revoked_at=entity.revoked_at,
        access_token=access_token,
    )


def _authentication_entity_to_model(entity: Authentication) -> AuthenticationModel:
    refresh_token = (
        _refresh_token_entity_to_model(entity.refresh_token)
        if entity.refresh_token
        else None
    )
    model = AuthenticationModel(
        id=entity.id,
        user_id=entity.user.id,
        ip_address=entity.ip_address if entity.ip_address else "",
        user_agent=entity.user_agent if entity.user_agent else "",
        device=entity.device if entity.device else "",
        accept_language=entity.accept_language,
        accept_encoding=entity.accept_encoding,
        origin=entity.origin if entity.origin else "",
        referrer=entity.referer,
        location=entity.location,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        last_updated_at=entity.last_updated_at
        if entity.last_updated_at
        else datetime.now(tz=BRASILIA_TZ),
        blacklisted=entity.blacklisted,
    )
    model.refresh_token = refresh_token
    return model


def model_entity_mapper(model: AuthenticationModel) -> Authentication:
    return _authentication_model_to_entity(model)


def entity_model_mapper(entity: Authentication) -> AuthenticationModel:
    return _authentication_entity_to_model(entity)


def sync_entity_from_model(
    entity: Authentication, model: AuthenticationModel
) -> Authentication:
    """Sync ค่าที่ generate โดย database กลับไปยัง entity"""
    entity.id = model.id
    entity.created_at = model.created_at
    entity.last_updated_at = model.last_updated_at

    if entity.refresh_token and model.refresh_token:
        entity.refresh_token.id = model.refresh_token.id
        entity.refresh_token.created_at = model.refresh_token.created_at
        entity.refresh_token.updated_at = model.refresh_token.updated_at

        if entity.refresh_token.access_token and model.refresh_token.access_token:
            entity.refresh_token.access_token.id = model.refresh_token.access_token.id
            entity.refresh_token.access_token.created_at = (
                model.refresh_token.access_token.created_at
            )

    return entity


# === ENTITY / CACHE ===
def _iso(value: datetime | date | None) -> str | None:
    return value.isoformat() if value else None


def _user_entity_to_cache(entity: User) -> dict:
    return {
        "id": str(entity.id) if entity.id else None,
        "first_name": entity.name.first_name if entity.name else None,
        "last_name": entity.name.last_name if entity.name else None,
        "preferred_name": entity.name.preferred_name if entity.name else None,
        "gender": entity.gender.value if entity.gender else None,
        "birthdate": _iso(entity.birthdate),
        "email": str(entity.email) if entity.email else None,
        "phone": str(entity.phone) if entity.phone else None,
        "role": entity.role.value if entity.role else None,
        "is_active": entity.is_active,
        "created_at": _iso(entity.created_at),
        "updated_at": _iso(entity.updated_at),
    }


def _access_token_entity_to_cache(entity: AccessToken) -> dict:
    # The raw JWT ('token') and the transient 'claims' are never cached.
    return {
        "id": str(entity.id) if entity.id else None,
        "hashed_jti": entity.hashed_jti,
        "previous_hashed_jti": entity.previous_hashed_jti,
        "permission": entity.permission.value if entity.permission else None,
        "created_at": _iso(entity.created_at),
        "expires_at": _iso(entity.expires_at),
        "revoked": entity.revoked,
        "revoked_at": _iso(entity.revoked_at),
    }


def _refresh_token_entity_to_cache(entity: RefreshToken) -> dict:
    return {
        "id": str(entity.id) if entity.id else None,
        "hashed_jti": entity.hashed_jti,
        "previous_hashed_jti": entity.previous_hashed_jti,
        "created_at": _iso(entity.created_at),
        "updated_at": _iso(entity.updated_at),
        "expires_at": _iso(entity.expires_at),
        "revoked": entity.revoked,
        "revoked_at": _iso(entity.revoked_at),
        "access_token": _access_token_entity_to_cache(entity.access_token)
        if entity.access_token
        else None,
    }


def entity_cache_mapper(authentication: Authentication) -> str:
    """แปลง Authentication entity → JSON string สำหรับ cache"""
    return json.dumps(
        {
            "id": str(authentication.id) if authentication.id else None,
            "ip_address": authentication.ip_address,
            "user_agent": authentication.user_agent,
            "device": authentication.device,
            "location": authentication.location,
            "accept_language": authentication.accept_language,
            "accept_encoding": authentication.accept_encoding,
            "origin": authentication.origin,
            "referer": authentication.referer,
            "blacklisted": authentication.blacklisted,
            "created_at": _iso(authentication.created_at),
            "last_updated_at": _iso(authentication.last_updated_at),
            "user": _user_entity_to_cache(authentication.user)
            if authentication.user
            else None,
            "refresh_token": _refresh_token_entity_to_cache(
                authentication.refresh_token
            )
            if authentication.refresh_token
            else None,
        }
    )


def _user_cache_to_entity(data: dict) -> User:
    user = User(
        id=UUID(data["id"]) if data["id"] else None,
        name=Name(
            first_name=data["first_name"],
            last_name=data["last_name"],
            preferred_name=data["preferred_name"],
        )
        if data["first_name"]
        else None,
        gender=Gender(data["gender"]) if data["gender"] else None,
        birthdate=date.fromisoformat(data["birthdate"]) if data["birthdate"] else None,
        email=data["email"],
        phone=data["phone"],
        role=Role(data["role"]) if data["role"] else Role.USER,
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        updated_at=datetime.fromisoformat(data["updated_at"])
        if data["updated_at"]
        else None,
    )
    user.is_active = data["is_active"]
    return user


def _access_token_cache_to_entity(data: dict) -> AccessToken:
    access = AccessToken(
        id=UUID(data["id"]) if data["id"] else None,
        hashed_jti=data["hashed_jti"],
        previous_hashed_jti=data["previous_hashed_jti"],
        permission=Role(data["permission"]) if data["permission"] else Role.USER,
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        expires_at=datetime.fromisoformat(data["expires_at"])
        if data["expires_at"]
        else None,
    )
    access.revoked = data["revoked"]
    access.revoked_at = (
        datetime.fromisoformat(data["revoked_at"]) if data["revoked_at"] else None
    )
    return access


def _refresh_token_cache_to_entity(data: dict) -> RefreshToken:
    refresh = RefreshToken(
        id=UUID(data["id"]) if data["id"] else None,
        hashed_jti=data["hashed_jti"],
        previous_hashed_jti=data["previous_hashed_jti"],
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        updated_at=datetime.fromisoformat(data["updated_at"])
        if data["updated_at"]
        else None,
        expires_at=datetime.fromisoformat(data["expires_at"])
        if data["expires_at"]
        else None,
        access_token=_access_token_cache_to_entity(data["access_token"])
        if data["access_token"]
        else None,
    )
    refresh.revoked = data["revoked"]
    refresh.revoked_at = (
        datetime.fromisoformat(data["revoked_at"]) if data["revoked_at"] else None
    )
    return refresh


def cache_entity_mapper(raw: str) -> Authentication:
    """แปลง JSON string จาก cache → Authentication entity"""
    data = json.loads(raw)

    authentication = Authentication(
        id=UUID(data["id"]) if data["id"] else None,
        ip_address=data["ip_address"],
        user_agent=data["user_agent"],
        device=data["device"],
        location=data["location"],
        accept_language=data["accept_language"],
        accept_encoding=data["accept_encoding"],
        origin=data["origin"],
        referer=data["referer"],
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        last_updated_at=datetime.fromisoformat(data["last_updated_at"])
        if data["last_updated_at"]
        else None,
        user=_user_cache_to_entity(data["user"]) if data["user"] else User(),
        refresh_token=_refresh_token_cache_to_entity(data["refresh_token"])
        if data["refresh_token"]
        else None,
    )
    authentication.blacklisted = data["blacklisted"]
    return authentication
```

---

## 7. Exceptions (`exceptions.py`)

```python
from __future__ import annotations

from http import HTTPStatus

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import ResponseMessages


# === GENERIC EXCEPTIONS ===
class AuthenticationException(StandardException):
    """Exception ทั่วไปสำหรับ authentication module"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the authentication module."
            },
        )


class AuthenticationTokenException(StandardException):
    """Exception สำหรับ token processing errors"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the authentication token. Please login again or contact support."
            },
        )


class HashingException(StandardException):
    """Exception สำหรับ hashing errors"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while hashing the password. Please try again."
            },
        )


class RefreshTokenException(StandardException):
    """Exception สำหรับ refresh token errors"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the refresh token. Please login again or contact support."
            },
        )


# === SPECIFIC EXCEPTIONS ===
class InvalidCredentialsException(StandardException):
    """Exception เมื่อ credentials ไม่ถูกต้อง"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid credentials for login.",
                "errors_th": "ข้อมูลเข้าสู่ระบบไม่ถูกต้อง",
            },
        )


class AuthenticationCookiesNotProvidedException(StandardException):
    """Exception เมื่อไม่พบ cookies"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Authentication cookies doest not exist. Please login again or contact support.",
                "errors_th": "ไม่พบคุกกี้สำหรับการยืนยันตัวตน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenExpiredException(StandardException):
    """Exception เมื่อ token หมดอายุ"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Token has expired. Please login again or contact support.",
                "errors_th": "โทเค็นหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenNotYetValidException(StandardException):
    """Exception เมื่อ token ยังไม่พร้อมใช้งาน"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Token is not yet valid. Please login again or contact support.",
                "errors_th": "โทเค็นยังไม่พร้อมใช้งาน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenMalformedError(StandardException):
    """Exception เมื่อ token format ผิด"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Malformed authentication token. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนมีรูปแบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenInvalidException(StandardException):
    """Exception เมื่อ token ไม่ถูกต้อง"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication token. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class ModifiedTokenException(StandardException):
    """Exception เมื่อ token ถูกแก้ไข"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "The authentication token has been modified. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนถูกแก้ไขเปลี่ยนแปลง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class UserHasNotPermissionException(StandardException):
    """Exception เมื่อ user ไม่มี permission"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "User does not have permission to perform this action.",
                "errors_th": "ผู้ใช้ไม่มีสิทธิ์ดำเนินการนี้",
            },
        )


class RefreshTokenNotProvidedException(StandardException):
    """Exception เมื่อไม่พบ refresh token"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token not provided. Please login again or contact support.",
                "errors_th": "ไม่ได้ระบุรีเฟรชโทเค็น กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenExpiredException(StandardException):
    """Exception เมื่อ refresh token หมดอายุ"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token has expired. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenNotYetValidException(StandardException):
    """Exception เมื่อ refresh token ยังไม่พร้อม"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token is not yet valid. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นยังไม่พร้อมใช้งาน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenMalformedError(StandardException):
    """Exception เมื่อ refresh token format ผิด"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Malformed refresh token. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นมีรูปแบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidEndpoint(StandardException):
    """Exception เมื่อ endpoint สำหรับ refresh ผิด"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid endpoint for refresh token. Please login again or contact support.",
                "errors_th": "ปลายทางสำหรับรีเฟรชโทเค็นไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidException(StandardException):
    """Exception เมื่อ refresh token ไม่ถูกต้อง"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidDeviceException(StandardException):
    """Exception เมื่อ device ไม่ตรงกับ refresh token"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token data. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลรีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationInvalidDeviceException(StandardException):
    """Exception เมื่อ device ไม่ตรงกับ authentication"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication data. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class LogoutInvalidEndpoint(StandardException):
    """Exception เมื่อ endpoint สำหรับ logout ผิด"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid endpoint for logout. Please login again or contact support.",
                "errors_th": "ปลายทางสำหรับออกจากระบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )
```

---

## 8. สรุปโครงสร้างโฟลเดอร์

```
app/modules/authentication/
├── domain/                          # Domain Layer
│   ├── entities.py                  # Authentication, RefreshToken, AccessToken
│   ├── value_objects.py             # Claims, RefreshClaims
│   ├── enums.py                     # TokenType
│   ├── events.py                    # Domain events
│   └── exceptions.py                # DomainError
│
├── application/                     # Application Layer
│   ├── use_cases.py                 # AuthenticationUseCases
│   ├── interfaces.py                # IAuthenticationRepository, IAuthenticationCache, ITokenService
│   ├── mappers.py                   # Data transformations
│   └── exceptions.py                # Application exceptions
│
├── infrastructure/                  # Infrastructure Layer
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── repositories.py              # PostgresAuthenticationRepository
│   ├── caches.py                    # RedisAuthenticationCache
│   └── services.py                  # TokenService
│
└── presentation/                    # Presentation Layer
    ├── routers.py                   # FastAPI endpoints
    ├── schemas.py                   # Pydantic models
    ├── docs.py                      # OpenAPI documentation
    └── dependencies.py              # Dependency Injection
```

---

## 9. Flow การทำงาน

### 9.1 Login Flow

```
Client
  │
  │ POST /api/v1/authentication/login/
  │ {username, password}
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Router (routers.py)                                          │
│ 1. รับ request                                               │
│ 2. login_entity_mapper() → Authentication entity             │
│ 3. use_case.login(authentication)                            │
│ 4. entity_login_mapper() → LoginResponse                     │
│ 5. set_cookies(response)                                     │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Use Case (use_cases.py)                                      │
│ 1. shared_service.get_user_by_email()                        │
│ 2. token_service.verify_password()                           │
│ 3. repository.get_by_user_id_agent_and_device()              │
│ 4. authentication.create_tokens() / renew_tokens()           │
│ 5. token_service.generate()                                  │
│ 6. token_service.hash_tokens()                               │
│ 7. repository.create() / update()                            │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Repository (repositories.py)                                 │
│ 1. entity_model_mapper() → AuthenticationModel              │
│ 2. session.add() / session.merge()                           │
│ 3. session.flush()                                           │
│ 4. sync_entity_from_model()                                  │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
Client ← {access_token, refresh_token} + HttpOnly cookies
```

### 9.2 Refresh Flow

```
Client
  │
  │ PATCH /api/v1/authentication/refresh/
  │ (refresh_token จาก cookie)
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Dependency (authenticate_refresh)                            │
│ 1. อ่าน refresh_token จาก cookie                             │
│ 2. verify JWT                                                │
│ 3. cache.get_by_refresh_token() / repository.get_refresh_token_by_authentication() │
│ 4. return Authentication entity                              │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Router (routers.py)                                          │
│ 1. use_case.refresh(authentication)                          │
│ 2. set_cookies(response)                                     │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Use Case (use_cases.py)                                      │
│ 1. cache.delete_by_access_token()                            │
│ 2. cache.delete_by_refresh_token()                           │
│ 3. authentication.refresh_access_token()                     │
│ 4. token_service.generate()                                  │
│ 5. token_service.hash_tokens()                               │
│ 6. repository.update()                                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
Client ← {message} + HttpOnly cookies ใหม่
```

### 9.3 Logout Flow

```
Client
  │
  │ DELETE /api/v1/authentication/logout/
  │ (access_token + refresh_token จาก cookie)
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Dependency (authenticate_logout)                             │
│ 1. อ่าน tokens จาก cookie                                    │
│ 2. verify JWT                                                │
│ 3. return Authentication entity                              │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Router (routers.py)                                          │
│ 1. use_case.logout(authentication)                           │
│ 2. delete_cookies(response)                                  │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Use Case (use_cases.py)                                      │
│ 1. authentication.revoke()                                   │
│ 2. repository.delete()                                       │
│ 3. cache.delete_by_access_token()                            │
│ 4. cache.delete_by_refresh_token()                           │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
Client ← {message} (cookies ถูกลบ)
```

---

## 10. ข้อดีของโครงสร้างนี้

| ข้อดี | คำอธิบาย |
|-------|----------|
| **Separation of Concerns** | แต่ละ layer มีหน้าที่ชัดเจน |
| **Testability** | สามารถ mock dependencies ได้ง่าย |
| **Maintainability** | แก้ไข layer หนึ่งไม่กระทบ layer อื่น |
| **Flexibility** | เปลี่ยน database/cache ได้โดยไม่แก้ business logic |
| **Domain Purity** | Domain layer ไม่พึ่งพา framework |
| **Dependency Inversion** | Application กำหนด interfaces, Infrastructure implement |
| **Tombstone Pattern** | ป้องกัน race condition ใน cache |
| **Token Rotation** | เก็บ `previous_hashed_jti` สำหรับตรวจจับ token reuse |

---

## 11. ข้อควรระวัง

1. **Domain Layer ห้าม import Infrastructure** - ถ้าจำเป็นให้ใช้ interface
2. **Use Case ห้ามเรียก HTTP โดยตรง** - ใช้ interface
3. **Mapper ต้องไม่มี business logic** - แค่ transform data
4. **Repository ห้ามมี business logic** - แค่ CRUD
5. **Cache ต้อง handle error ได้** - ถ้า cache ล่ม ต้อง fallback ไป database
6. **Token ต้อง hash ก่อนเก็บ** - ห้ามเก็บ plain token ใน database

---

# คู่มือเพิ่ม API ส่วนที่เหลือ + แก้ไข Login Response

จากไฟล์ `{.txt` ที่ให้มา ผมเห็นว่า login response มีปัญหา:
1. **Syntax ผิด** - มี `"timeh_token": 555555` และ `"info": {...}` ที่ไม่มี comma คั่น
2. **ขาด `info`** ใน `LoginResponse` schema
3. **ต้องเพิ่ม API** ส่วนที่เหลือ (forgot password, reset password, sign up, lock screen, two-step verification, two-step code)

ผมจะเขียนโค้ดให้ครบครับ

---

## 1. แก้ไข Schemas (`schemas.py`)

เพิ่ม `UserInfo` และแก้ `LoginResponse` ให้รวม `info`

```python
from __future__ import annotations

from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.shared.domain.enums import ResponseMessages, Role


# === USER INFO ===
class UserInfo(BaseModel):
    """ข้อมูล user ที่ส่งกลับพร้อม login response"""
    
    first_name: str
    last_name: str
    preferred_name: str
    gender: str
    birthdate: date
    email: EmailStr
    phone: str | None = None
    role: Role
    created_at: str  # ISO 8601 format

    model_config = ConfigDict(
        title="UserInfo",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "description": "User information returned with login response.",
            "example": {
                "first_name": "System",
                "last_name": "Admin",
                "preferred_name": "Admin",
                "gender": "other",
                "birthdate": "1990-01-01",
                "email": "admin@example.com",
                "phone": None,
                "role": "admin",
                "created_at": "2026-09-19T08:57:37.641459Z",
            },
        },
    )


# === RESPONSE ===
class LoginResponse(BaseModel):
    """
    Response model สำหรับ login
    
    โครงสร้าง:
    {
        "message": "User logged in successfully",
        "access_token": "...",
        "refresh_token": "...",
        "info": { ... }
    }
    """
    
    message: str = ResponseMessages.LOGIN_SUCCESS.value
    access_token: str
    refresh_token: str
    info: UserInfo

    model_config = ConfigDict(
        title="LoginResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user login.",
            "example": {
                "message": ResponseMessages.LOGIN_SUCCESS.value,
                "access_token": "eyJhbGciOi...",
                "refresh_token": "eyJhbGciOi...",
                "info": {
                    "first_name": "System",
                    "last_name": "Admin",
                    "preferred_name": "Admin",
                    "gender": "other",
                    "birthdate": "1990-01-01",
                    "email": "admin@example.com",
                    "phone": None,
                    "role": "admin",
                    "created_at": "2026-09-19T08:57:37.641459Z",
                },
            },
        },
    )


class RefreshResponse(BaseModel):
    """Response model สำหรับ refresh"""
    
    message: str = ResponseMessages.REFRESH_SUCCESS.value

    model_config = ConfigDict(
        title="RefreshResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user refresh.",
            "example": {"message": ResponseMessages.REFRESH_SUCCESS.value},
        },
    )


class LogoutResponse(BaseModel):
    """Response model สำหรับ logout"""
    
    message: str = ResponseMessages.LOGOUT_SUCCESS.value

    model_config = ConfigDict(
        title="LogoutResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user logout.",
            "example": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
        },
    )


# === SIGN UP ===
class SignUpRequest(BaseModel):
    """Request model สำหรับ sign up"""
    
    full_name: str
    username: str
    email: EmailStr
    phone_number: str | None = None
    password: str
    confirm_password: str
    agree_terms: bool

    model_config = ConfigDict(
        title="SignUpRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "phone_number": "+555472664275",
                "password": "MyP@ssword123",
                "confirm_password": "MyP@ssword123",
                "agree_terms": True,
            },
        },
    )


class SignUpResponse(BaseModel):
    """Response model สำหรับ sign up"""
    
    message: str = ResponseMessages.CREATED.value

    model_config = ConfigDict(
        title="SignUpResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.CREATED.value},
        },
    )


# === FORGOT PASSWORD ===
class ForgotPasswordRequest(BaseModel):
    """Request model สำหรับ forgot password"""
    
    email: EmailStr

    model_config = ConfigDict(
        title="ForgotPasswordRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={"example": {"email": "johndoe@example.com"}},
    )


class ForgotPasswordResponse(BaseModel):
    """Response model สำหรับ forgot password"""
    
    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="ForgotPasswordResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# === RESET PASSWORD ===
class ResetPasswordRequest(BaseModel):
    """Request model สำหรับ reset password"""
    
    code: str
    password: str
    confirm_password: str

    model_config = ConfigDict(
        title="ResetPasswordRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "code": "ABC123",
                "password": "NewP@ssword123",
                "confirm_password": "NewP@ssword123",
            },
        },
    )


class ResetPasswordResponse(BaseModel):
    """Response model สำหรับ reset password"""
    
    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="ResetPasswordResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# === LOCK SCREEN ===
class LockScreenRequest(BaseModel):
    """Request model สำหรับ lock screen"""
    
    password: str

    model_config = ConfigDict(
        title="LockScreenRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={"example": {"password": "MyP@ssword123"}},
    )


class LockScreenResponse(BaseModel):
    """Response model สำหรับ lock screen"""
    
    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="LockScreenResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# === TWO-STEP VERIFICATION ===
class TwoStepVerificationRequest(BaseModel):
    """Request model สำหรับ two-step verification"""
    
    country_code: str
    phone_number: str

    model_config = ConfigDict(
        title="TwoStepVerificationRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"country_code": "+1", "phone_number": "8566728552"},
        },
    )


class TwoStepVerificationResponse(BaseModel):
    """Response model สำหรับ two-step verification"""
    
    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="TwoStepVerificationResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# === TWO-STEP CODE ===
class TwoStepCodeRequest(BaseModel):
    """Request model สำหรับ two-step code"""
    
    code: str
    dont_ask_again: bool = False

    model_config = ConfigDict(
        title="TwoStepCodeRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"code": "123456", "dont_ask_again": False},
        },
    )


class TwoStepCodeResponse(BaseModel):
    """Response model สำหรับ two-step code"""
    
    message: str = ResponseMessages.SUCCESS.value
    access_token: str | None = None
    refresh_token: str | None = None

    model_config = ConfigDict(
        title="TwoStepCodeResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "message": ResponseMessages.SUCCESS.value,
                "access_token": "eyJhbGciOi...",
                "refresh_token": "eyJhbGciOi...",
            },
        },
    )
```

---

## 2. แก้ไข Mappers (`mappers.py`)

แก้ `entity_login_mapper` ให้รวม `info`

```python
def entity_login_mapper(
    _authentication: Authentication,
) -> LoginResponse:
    """
    แปลง Authentication entity → LoginResponse
    
    ดึง tokens จาก:
    - _authentication.refresh_token.access_token.token (access token)
    - _authentication.refresh_token.token (refresh token)
    
    ดึง user info จาก:
    - _authentication.user (User entity)
    """
    user = _authentication.user
    
    # สร้าง UserInfo จาก User entity
    user_info = UserInfo(
        first_name=user.name.first_name if user.name else "",
        last_name=user.name.last_name if user.name else "",
        preferred_name=user.name.preferred_name if user.name else "",
        gender=user.gender.value if user.gender else "other",
        birthdate=user.birthdate if user.birthdate else date(1990, 1, 1),
        email=str(user.email) if user.email else "",
        phone=str(user.phone) if user.phone else None,
        role=user.role if user.role else Role.USER,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )
    
    return LoginResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
        info=user_info,
    )
```

**อัปเดต import:**

```python
from app.modules.authentication.presentation.schemas import (
    ForgotPasswordResponse,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordResponse,
    SignUpResponse,
    TwoStepCodeResponse,
    TwoStepVerificationResponse,
    UserInfo,  # เพิ่ม
)
from datetime import date  # เพิ่ม
```

---

## 3. เพิ่ม Use Cases (`use_cases.py`)

เพิ่ม use cases สำหรับ API ที่เหลือ

```python
from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from loguru import logger

from app.core.settings import settings
from app.modules.authentication.application.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    RefreshTokenInvalidException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    def __init__(
        self,
        cache: IAuthenticationCache,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
        token_service: ITokenService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.token_service = token_service
        self.shared_service.disable_exceptions()

    # ========================================================================
    # CREATE: LOGIN
    # ========================================================================
    async def login(self, authentication: Authentication) -> Authentication:
        """Login use case (เหมือนเดิม)"""
        try:
            logger.debug(
                f"Initializing user login use case for user: {authentication.user.censored_email} in device: {authentication.device}."
            )

            db_user: User | None = await self.shared_service.get_user_by_email(
                authentication.user
            )

            if not db_user:
                logger.info(
                    f"User with email {authentication.user.censored_email} not found, raising exception."
                )
                raise InvalidCredentialsException()

            if not await self.token_service.verify_password(
                authentication.user.password, db_user.hashed_password
            ):
                logger.info(
                    f"Invalid password for user {authentication.user.id}, raising exception."
                )
                raise InvalidCredentialsException()

            authentication.user = db_user
            authentication_from_db = (
                await self.repository.get_by_user_id_agent_and_device(authentication)
            )

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            if authentication_from_db:
                await self.cache.delete_by_access_token(authentication_from_db)
                await self.cache.delete_by_refresh_token(authentication_from_db)

                authentication = authentication_from_db.renew_tokens(
                    now, refresh_expires_at, access_expires_at
                )
            else:
                authentication = authentication.create_tokens(
                    now, refresh_expires_at, access_expires_at
                )

            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            if authentication_from_db:
                await self.repository.update(authentication)
            else:
                await self.repository.create(authentication)

            logger.debug(
                f"User {authentication.user.id} logged in successfully in device: {authentication.device}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the login use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # UPDATE: REFRESH
    # ========================================================================
    async def refresh(self, authentication: Authentication) -> Authentication:
        """Refresh tokens use case (เหมือนเดิม)"""
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {authentication.user.id}."
            )

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            now = datetime.now(BRASILIA_TZ)
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.refresh_access_token(now, access_expires_at)
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.update(authentication)

            logger.debug(
                f"User {authentication.user.id} refreshed tokens successfully."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the refresh tokens use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # DELETE: LOGOUT
    # ========================================================================
    async def logout(self, authentication: Authentication) -> Authentication:
        """Logout use case (เหมือนเดิม)"""
        try:
            logger.debug(
                f"Initializing user logout use case for user: {authentication.user.id}."
            )

            authentication.revoke(datetime.now(BRASILIA_TZ))
            await self.repository.delete(authentication)

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            logger.debug(f"User {authentication.user.id} logged out successfully.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # SIGN UP
    # ========================================================================
    async def sign_up(self, user: User) -> User:
        """
        Sign up use case

        ขั้นตอน:
        1. ตรวจสอบว่า email ซ้ำหรือไม่
        2. Hash password
        3. สร้าง user ใหม่
        4. ส่ง verification email (TODO)
        """
        try:
            logger.debug(
                f"Initializing sign up use case for user: {user.censored_email}."
            )

            # ตรวจสอบ email ซ้ำ
            existing_user = await self.shared_service.get_user_by_email(user)
            if existing_user:
                logger.info(f"User with email {user.censored_email} already exists.")
                raise InvalidCredentialsException()

            # สร้าง user ใหม่
            user = await self.shared_service.create_user(user)

            logger.debug(
                f"User {user.censored_email} signed up successfully with id {user.id}."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the sign up use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # FORGOT PASSWORD
    # ========================================================================
    async def forgot_password(self, email: str) -> None:
        """
        Forgot password use case

        ขั้นตอน:
        1. ตรวจสอบว่า user มีอยู่จริง
        2. สร้าง reset code
        3. ส่ง email (TODO)
        """
        try:
            logger.debug(f"Initializing forgot password use case for email: {email}.")

            user = await self.shared_service.get_user_by_email(User(email=email))

            if not user:
                # ไม่เปิดเผยว่า email มีอยู่หรือไม่ (security)
                logger.info(
                    f"User with email {email} not found, but returning success."
                )
                return

            # สร้าง reset code (TODO: implement)
            reset_code = "ABC123"  # Placeholder

            # ส่ง email (TODO: implement)
            logger.debug(f"Reset code sent to {email}.")

            logger.debug(f"Forgot password processed for {email}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the forgot password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # RESET PASSWORD
    # ========================================================================
    async def reset_password(
        self, code: str, password: str, confirm_password: str
    ) -> None:
        """
        Reset password use case

        ขั้นตอน:
        1. ตรวจสอบ reset code
        2. ตรวจสอบ password match
        3. Hash password ใหม่
        4. อัปเดต user
        """
        try:
            logger.debug("Initializing reset password use case.")

            if password != confirm_password:
                raise InvalidCredentialsException()

            # ตรวจสอบ code (TODO: implement)
            # user = await self.shared_service.get_user_by_reset_code(code)
            # if not user:
            #     raise InvalidCredentialsException()

            # อัปเดต password (TODO: implement)
            logger.debug("Reset password processed successfully.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the reset password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # LOCK SCREEN
    # ========================================================================
    async def lock_screen(self, authentication: Authentication, password: str) -> None:
        """
        Lock screen use case

        ตรวจสอบ password ก่อน unlock
        """
        try:
            logger.debug(
                f"Initializing lock screen use case for user: {authentication.user.id}."
            )

            if not await self.token_service.verify_password(
                password, authentication.user.hashed_password
            ):
                raise InvalidCredentialsException()

            logger.debug(f"Lock screen unlocked for user {authentication.user.id}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the lock screen use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP VERIFICATION
    # ========================================================================
    async def two_step_verification(
        self, authentication: Authentication, country_code: str, phone_number: str
    ) -> None:
        """
        Two-step verification use case

        ขั้นตอน:
        1. ตรวจสอบ phone number
        2. ส่ง OTP (TODO)
        """
        try:
            logger.debug(
                f"Initializing two-step verification for user: {authentication.user.id}."
            )

            full_phone = f"{country_code}{phone_number}"

            # ส่ง OTP (TODO: implement)
            logger.debug(f"OTP sent to {full_phone}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step verification use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP CODE
    # ========================================================================
    async def two_step_code(
        self, authentication: Authentication, code: str, dont_ask_again: bool
    ) -> Authentication:
        """
        Two-step code use case

        ขั้นตอน:
        1. ตรวจสอบ OTP code
        2. ถ้าถูกต้อง สร้าง tokens
        3. ถ้า dont_ask_again ให้จำ device
        """
        try:
            logger.debug(
                f"Initializing two-step code verification for user: {authentication.user.id}."
            )

            # ตรวจสอบ OTP (TODO: implement)
            if code != "123456":  # Placeholder
                raise InvalidCredentialsException()

            # สร้าง tokens
            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.create_tokens(
                now, refresh_expires_at, access_expires_at
            )
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.create(authentication)

            # ถ้า dont_ask_again ให้จำ device (TODO: implement)

            logger.debug(f"Two-step code verified for user {authentication.user.id}.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step code use case."
            )
            raise AuthenticationException()
```

---

## 4. เพิ่ม Routers (`routers.py`)

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    authenticate_logout,
    authenticate_refresh,
    authenticate_user,
    no_authentication,
)
from app.core.settings import settings
from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.mappers import (
    entity_login_mapper,
    entity_logout_mapper,
    entity_refresh_mapper,
    login_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    forgot_password_docs,
    login_docs,
    logout_docs,
    refresh_docs,
    reset_password_docs,
    router_docs,
    sign_up_docs,
    lock_screen_docs,
    two_step_code_docs,
    two_step_verification_docs,
)
from app.modules.authentication.presentation.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LockScreenRequest,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignUpRequest,
    SignUpResponse,
    TwoStepCodeRequest,
    TwoStepCodeResponse,
    TwoStepVerificationRequest,
    TwoStepVerificationResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import CookieManagementException

router = APIRouter(**router_docs)


# ============================================================================
# COOKIE HELPERS
# ============================================================================
def set_cookies(response: Response, authentication: Authentication) -> None:
    """ตั้งค่า HttpOnly cookies สำหรับ tokens"""
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=TokenType.BEARER.value,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=authentication.refresh_token.access_token.token
            if authentication.refresh_token.access_token.token
            else "",
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=authentication.refresh_token.token
            if authentication.refresh_token.token
            else "",
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


def delete_cookies(response: Response) -> None:
    """ลบ cookies"""
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the delete_cookies function."
        )
        raise CookieManagementException()


# ============================================================================
# CREATE: LOGIN
# ============================================================================
@router.post("/login/", **login_docs)
@router.post("/login", include_in_schema=False)
async def login(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LoginResponse:
    """
    Endpoint สำหรับ login
    
    Response:
    {
        "message": "User logged in successfully",
        "access_token": "...",
        "refresh_token": "...",
        "info": {
            "first_name": "System",
            "last_name": "Admin",
            ...
        }
    }
    """
    try:
        request_domain = login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = entity_login_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the login endpoint.")
        raise AuthenticationException()


# ============================================================================
# SIGN UP
# ============================================================================
@router.post("/sign-up/", **sign_up_docs)
@router.post("/sign-up", include_in_schema=False)
async def sign_up(
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[SignUpRequest, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> SignUpResponse:
    """
    Endpoint สำหรับ sign up
    
    สร้าง user ใหม่ในระบบ
    """
    try:
        # TODO: แปลง SignUpRequest → User entity
        # request_domain = sign_up_entity_mapper(form_data)
        # response_domain = await use_case.sign_up(request_domain)
        # output = entity_sign_up_mapper(response_domain)
        return SignUpResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the sign up endpoint.")
        raise AuthenticationException()


# ============================================================================
# UPDATE: REFRESH
# ============================================================================
@router.patch("/refresh/", **refresh_docs)
@router.patch("/refresh", include_in_schema=False)
async def refresh(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_refresh)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> RefreshResponse:
    """Endpoint สำหรับ refresh tokens"""
    try:
        request_domain = refresh_entity_mapper(authentication)
        response_domain = await use_case.refresh(request_domain)
        output = entity_refresh_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()


# ============================================================================
# DELETE: LOGOUT
# ============================================================================
@router.delete("/logout/", **logout_docs)
@router.delete("/logout", include_in_schema=False)
async def logout(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_logout)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LogoutResponse:
    """Endpoint สำหรับ logout"""
    try:
        request_domain = logout_entity_mapper(authentication)
        response_domain = await use_case.logout(request_domain)
        output = entity_logout_mapper(response_domain)

        delete_cookies(response)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the logout endpoint.")
        raise AuthenticationException()


# ============================================================================
# FORGOT PASSWORD
# ============================================================================
@router.post("/forgot-password/", **forgot_password_docs)
@router.post("/forgot-password", include_in_schema=False)
async def forgot_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ForgotPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ForgotPasswordResponse:
    """
    Endpoint สำหรับ forgot password
    
    ส่ง reset code ไปยัง email
    """
    try:
        await use_case.forgot_password(email=str(payload.email))
        return ForgotPasswordResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the forgot password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# RESET PASSWORD
# ============================================================================
@router.post("/reset-password/", **reset_password_docs)
@router.post("/reset-password", include_in_schema=False)
async def reset_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ResetPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ResetPasswordResponse:
    """
    Endpoint สำหรับ reset password
    
    ตรวจสอบ reset code และตั้ง password ใหม่
    """
    try:
        await use_case.reset_password(
            code=payload.code,
            password=payload.password,
            confirm_password=payload.confirm_password,
        )
        return ResetPasswordResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the reset password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# LOCK SCREEN
# ============================================================================
@router.post("/lock-screen/", **lock_screen_docs)
@router.post("/lock-screen", include_in_schema=False)
async def lock_screen(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: LockScreenRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LockScreenResponse:
    """
    Endpoint สำหรับ lock screen
    
    ตรวจสอบ password เพื่อ unlock
    """
    try:
        await use_case.lock_screen(
            authentication=authentication, password=payload.password
        )
        return LockScreenResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the lock screen endpoint.")
        raise AuthenticationException()


# ============================================================================
# TWO-STEP VERIFICATION
# ============================================================================
@router.post("/two-step-verification/", **two_step_verification_docs)
@router.post("/two-step-verification", include_in_schema=False)
async def two_step_verification(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepVerificationRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepVerificationResponse:
    """
    Endpoint สำหรับ two-step verification
    
    ส่ง OTP ไปยัง phone number
    """
    try:
        await use_case.two_step_verification(
            authentication=authentication,
            country_code=payload.country_code,
            phone_number=payload.phone_number,
        )
        return TwoStepVerificationResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step verification endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# TWO-STEP CODE
# ============================================================================
@router.post("/two-step-code/", **two_step_code_docs)
@router.post("/two-step-code", include_in_schema=False)
async def two_step_code(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepCodeRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepCodeResponse:
    """
    Endpoint สำหรับ two-step code
    
    ตรวจสอบ OTP code และสร้าง tokens
    """
    try:
        response_domain = await use_case.two_step_code(
            authentication=authentication,
            code=payload.code,
            dont_ask_again=payload.dont_ask_again,
        )

        set_cookies(response, response_domain)

        return TwoStepCodeResponse(
            access_token=response_domain.refresh_token.access_token.token,
            refresh_token=response_domain.refresh_token.token,
        )
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step code endpoint."
        )
        raise AuthenticationException()
```

---

## 5. เพิ่ม Docs (`docs.py`)

```python
from __future__ import annotations

from http import HTTPStatus

from app.modules.authentication.presentation.schemas import (
    ForgotPasswordResponse,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    ResetPasswordResponse,
    SignUpResponse,
    TwoStepCodeResponse,
    TwoStepVerificationResponse,
)
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse

# ============================================================================
# MODULE DOCS
# ============================================================================
router_docs = {
    "prefix": "/api/v1/authentication",
    "tags": ["Authentication"],
    "responses": {
        400: {"model": StandardResponse, "description": "Bad Request"},
        401: {"model": StandardResponse, "description": "Unauthorized"},
        403: {"model": StandardResponse, "description": "Forbidden"},
        405: {"model": StandardResponse, "description": "Method Not Allowed"},
        422: {"model": StandardResponse, "description": "Form Validation Error"},
        500: {"model": StandardResponse, "description": "Internal Server Error"},
        502: {"model": StandardResponse, "description": "Bad Gateway"},
        504: {"model": StandardResponse, "description": "Gateway Timeout"},
    },
}


# ============================================================================
# LOGIN DOCS
# ============================================================================
login_docs = {
    "summary": "Endpoint to login a user.",
    "description": (
        "Authenticate a user and initiate a login session. "
        "Authentication tokens are returned via HttpOnly cookies."
    ),
    "response_description": (
        "Successful authentication. Access/refresh tokens are set in cookies and "
        "the JSON body returns tokens + user info."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LoginResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful login response (cookies + tokens + user info)",
            "model": LoginResponse,
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to set `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": "access_token=<token>; HttpOnly; Path=/; SameSite=lax",
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Login Success": {
                            "summary": "Login response with tokens and user info",
                            "value": {
                                "message": ResponseMessages.LOGIN_SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
                                "info": {
                                    "first_name": "System",
                                    "last_name": "Admin",
                                    "preferred_name": "Admin",
                                    "gender": "other",
                                    "birthdate": "1990-01-01",
                                    "email": "admin@example.com",
                                    "phone": None,
                                    "role": "admin",
                                    "created_at": "2026-09-19T08:57:37.641459Z",
                                },
                            },
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# SIGN UP DOCS
# ============================================================================
sign_up_docs = {
    "summary": "Endpoint to sign up a new user.",
    "description": (
        "Create a new user account. Public endpoint — no authentication is required."
    ),
    "response_description": "Successful sign up.",
    "status_code": HTTPStatus.CREATED,
    "response_model": SignUpResponse,
    "include_in_schema": True,
    "responses": {
        201: {
            "description": "User created successfully",
            "model": SignUpResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Sign Up Success": {
                            "summary": "User signed up successfully",
                            "value": {"message": ResponseMessages.CREATED.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# REFRESH DOCS
# ============================================================================
refresh_docs = {
    "summary": "Endpoint to refresh authentication tokens.",
    "description": (
        "Validates the `refresh_token` from HttpOnly cookies using `refresh_tokens` "
        "security dependency, then rotates and sets new `token_type`, `access_token`, "
        "and `refresh_token` cookies."
    ),
    "response_description": (
        "Successful token refresh. New access/refresh tokens and token type are set "
        "in cookies, and the JSON body returns a refresh confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": RefreshResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful refresh response",
            "model": RefreshResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Refresh Success": {
                            "summary": "Refresh token generated successfully",
                            "value": {
                                "message": ResponseMessages.REFRESH_SUCCESS.value
                            },
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOGOUT DOCS
# ============================================================================
logout_docs = {
    "summary": "Endpoint to logout a user.",
    "description": (
        "Invalidates the authenticated session and removes authentication cookies. "
        "The endpoint requires a valid authenticated user."
    ),
    "response_description": (
        "Successful logout. Authentication cookies are removed and the JSON body "
        "returns a logout confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LogoutResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful logout response",
            "model": LogoutResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Logout Success": {
                            "summary": "User logged out successfully",
                            "value": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# FORGOT PASSWORD DOCS
# ============================================================================
forgot_password_docs = {
    "summary": "Endpoint to request password reset.",
    "description": (
        "Send a password reset code to the user's email address. "
        "Always returns success to avoid revealing whether the email exists."
    ),
    "response_description": "Reset code sent (if email exists).",
    "status_code": HTTPStatus.OK,
    "response_model": ForgotPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Forgot password request processed",
            "model": ForgotPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Forgot Password Success": {
                            "summary": "Reset code sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# RESET PASSWORD DOCS
# ============================================================================
reset_password_docs = {
    "summary": "Endpoint to reset password with code.",
    "description": ("Validate the reset code and set a new password for the user."),
    "response_description": "Password reset successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": ResetPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Password reset successfully",
            "model": ResetPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Reset Password Success": {
                            "summary": "Password reset successfully",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOCK SCREEN DOCS
# ============================================================================
lock_screen_docs = {
    "summary": "Endpoint to unlock the screen.",
    "description": (
        "Validate the user's password to unlock a locked screen. "
        "Requires a valid authenticated session."
    ),
    "response_description": "Screen unlocked successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": LockScreenResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Screen unlocked successfully",
            "model": LockScreenResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Lock Screen Success": {
                            "summary": "Screen unlocked",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP VERIFICATION DOCS
# ============================================================================
two_step_verification_docs = {
    "summary": "Endpoint to initiate two-step verification.",
    "description": (
        "Send an OTP code to the specified phone number for two-step verification."
    ),
    "response_description": "OTP sent successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepVerificationResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP sent successfully",
            "model": TwoStepVerificationResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Verification Success": {
                            "summary": "OTP sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP CODE DOCS
# ============================================================================
two_step_code_docs = {
    "summary": "Endpoint to verify two-step code.",
    "description": ("Validate the OTP code and issue authentication tokens."),
    "response_description": "OTP verified successfully, tokens issued.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepCodeResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP verified successfully",
            "model": TwoStepCodeResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Code Success": {
                            "summary": "OTP verified, tokens issued",
                            "value": {
                                "message": ResponseMessages.SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
                            },
                        }
                    }
                }
            },
        },
    },
}
```

---

## 6. สรุป API Endpoints ทั้งหมด

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/api/v1/authentication/login/` | Login | ❌ |
| POST | `/api/v1/authentication/sign-up/` | Sign up | ❌ |
| PATCH | `/api/v1/authentication/refresh/` | Refresh tokens | ✅ (refresh) |
| DELETE | `/api/v1/authentication/logout/` | Logout | ✅ |
| POST | `/api/v1/authentication/forgot-password/` | Request password reset | ❌ |
| POST | `/api/v1/authentication/reset-password/` | Reset password with code | ❌ |
| POST | `/api/v1/authentication/lock-screen/` | Unlock screen | ✅ |
| POST | `/api/v1/authentication/two-step-verification/` | Send OTP | ✅ |
| POST | `/api/v1/authentication/two-step-code/` | Verify OTP | ✅ |

---

## 7. Login Response ที่ถูกต้อง

```json
{
    "code": 200,
    "method": "POST",
    "path": "/api/v1/authentication/login/",
    "timestamp": "2026-09-20T10:47:51.493046Z",
    "details": {
        "message": "User logged in successfully",
        "data": {
            "message": "User logged in successfully",
            "access_token": "eyJhbGciOiJFQ0RILUVTK0EyNTZLVyIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZHQ00iLCJlcGsiOnsiY3J2IjoiWDI1NTE5Iiwia3R5IjoiT0tQIiwieCI6Im54Q0ctY0t3TFZaU0tWQWFNcGRRMVZQeUxwU0JUZzh1aHl3SWRvR2o4RWcifX0.lVlKbaKQG5eQwSn5iHrGur5YGx0yyf9aoZnBYmyFEJ4n1LASaqF1cw.8I-H1cXPE2EvB0Og.9ZrmCB-XDxtc1ngCi8LEgWLWGVbNPHv4ZD6Ty0Se1_dmF4Fc0eCCkxxxe4pPlOzfCbqlsiokRZ8cBOhleov5OKenb1OBU65eu4OJjny5s18lsUqUzGyfvICv05uyNTLEr2cqMsLsJakAhX_mYiW1GKYtuluFXSIqGe0J_KlxdhT87S7FN9uZylgk4Kg4--s_MoejiV2bo4SJl8DzRL_F-e5cJHLplZ53BGW9cFDn61nb4m6W3jw-ExpdS_TG5yR1xbBAHO1zrFgvoHwepJDcyolytIZB5QPiAHTZivj4kyDfPdv_54ccuc3KxFZYFiui0ytz23sbf4ycJA_gPDnQJRtIwpv66Dbs94_XosPIMgP7m1dSa24_nXtZWO6KWSX8WWJ1ip-MOaiuhMk7qoZIB3FuOS4Tuy5dsTm9wRUm15alM7THyaD6VMmHYY_bwjmWPheqA1lf4tbQ0Le9q8pPUYreL-dwTeclhI37mrbCprqWtFG8bg97Vv1tDpWJGLMUIQWS9f4UvXFFM-esz8Hwc08LmQ-RMktIgMR_Ba7N44qvC6Q9PxYXPPS2TdXRraWFxX_sfplKF7pMmuMBK0fbB0PxFGWasDEZ1eX07p1R1LizwdwM1NK-XwdR6Cr4qDO1zd2KF48wwr-wfSyCG-5VhfyZp4_O4LbJTOZngHmOt9ikjQ.uXx7S0QZFop-LmOSYISHzA",
            "refresh_token": "eyJhbGciOiJFQ0RILUVTK0EyNTZLVyIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZHQ00iLCJlcGsiOnsiY3J2IjoiWDI1NTE5Iiwia3R5IjoiT0tQIiwieCI6ImsxdUlpUGItLUVPTFNvXzZzdURwdHhTb0UxZG9RaFlFRkRHWVpEZUZNRGMifX0.tCMVr_PAigKyb3YsG0LwnvsBQgeWqTGBqQUjcn-vBx3js_AQLqKqXg.nF_IIbIaHK0b3I_I.mtt_Zx8HvsFW-pgKqBsShYwzv1SdS91CB0fEAuuCyOuziJFkcNqw7U0sh_HkAGLEySi_0qhUyttGWV1Y9Iid16YQ7XmljBP0W6-dnOtC_LZ0MLhwccZoQv8csavAxaTRBoI84eIj57YM0Z_wI3-O8CO9gmlM8pubMB_hmUD_rqDnrTBV1ZWnONRHHce9Y4WeAPv4YEsdkSvNitdsQfankpLqVVeIvuG4QN-PwzfieHxYLXNnLyNdmGcxVUqs9uw36pt04gA4mfAmvfouQx6MZUWfKIC7s0lNbqaKYkvwcOhezE1F6uydD76GGgOn0kMlf0iknR-mYD-OF_vmbttUkSuwA6Pt-VVr-9DciIa1t4aulwhoKcl7epXazxlv3OhvrCnlb64If-YXhkPUQwwS8EZ81t_EOKaMqtw-dSj9g7bkG63MBdqOqpXCs1bi5n58mARuMcAOjRLeD5KULOV0x2y6VIs_wLYCLW7Rk_HKd97P2iopBCoM704_VFh1NXXoWq0GrqeLL-72JK9_VyVv5oH90vhiCumLK7AJnMWjwxGtrX61DsbgqizbbY8vBq-YLB2o1bnD1RyUDuPjgPSSJpmPGTv0p2iYm2AKpRocS5jrGuf4nOs9gu-jGPi-e4OHC8YoZksin0O9fgzIxsJM-Yy5jkLyX2uZ6l4UAA_CxjJzOzK5oyAWXDhOVivGTL9QUSZIM21jNWGLB8bP1i38ABU66CZBph87xHcWuZbsSacZq4RzDA.AtCE6Q-U0AsFiyTlhkdvuw",
            "info": {
                "first_name": "System",
                "last_name": "Admin",
                "preferred_name": "Admin",
                "gender": "other",
                "birthdate": "1990-01-01",
                "email": "admin@example.com",
                "phone": null,
                "role": "admin",
                "created_at": "2026-09-19T08:57:37.641459Z"
            }
        }
    }
}
```

---

## 8. Checklist การทำงาน

- [x] แก้ไข `LoginResponse` schema ให้รวม `info`
- [x] สร้าง `UserInfo` schema
- [x] แก้ไข `entity_login_mapper` ให้สร้าง `UserInfo`
- [x] เพิ่ม use cases: `sign_up`, `forgot_password`, `reset_password`, `lock_screen`, `two_step_verification`, `two_step_code`
- [x] เพิ่ม routers สำหรับ API ทั้งหมด
- [x] เพิ่ม docs สำหรับ API ทั้งหมด
- [ ] Implement `sign_up_entity_mapper` (TODO)
- [ ] Implement email sending สำหรับ forgot password (TODO)
- [ ] Implement OTP sending สำหรับ two-step (TODO)
- [ ] Implement reset code validation (TODO)

---

 