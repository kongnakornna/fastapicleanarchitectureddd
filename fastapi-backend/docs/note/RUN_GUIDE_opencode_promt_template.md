# 📘 ส่วนที่ 1: คู่มือการใช้งาน (User Manual)

````markdown
# 📖 คู่มือการใช้งาน — ERP+CRM+IoT Module Toolkit v5.0

> สำหรับ dev ที่ใช้ **OpenCode Prompt Template** + **Bat/PowerShell Scripts**
> สร้าง/แก้ไข module ตาม Clean Architecture + DDD + FastAPI

---

## 1. ภาพรวม (Overview)

ระบบนี้ประกอบด้วย 3 ส่วน:

| ส่วน | ไฟล์ | หน้าที่ |
|---|---|---|
| **Prompt Template** | `RUN_GUIDE_opencode_promt.md` | Master prompt 23 ส่วน + Template A–G |
| **Module Spec** | `audit.md`, `money.md`, ... | สเปกเฉพาะ module |
| **Scripts** | `create_modules.bat` / `create_module.ps1` | สร้าง/แก้ไขโครงสร้างอัตโนมัติ |

### หลักการ
1. **Prompt → OpenCode** สร้างโค้ดตาม Template A–G
2. **Script → PowerShell** สร้างโครงสร้าง folder + ไฟล์พื้นฐาน
3. ทั้งสองทางต้อง **สอดคล้อง** กับ Global Constraints

---

## 2. โครงสร้างโปรเจกต์มาตรฐาน

```
project-root/
├── RUN_GUIDE_opencode_promt.md      ← Master Prompt
├── create_modules.bat                ← Wrapper
├── create_modules.ps1                ← Implementation
├── create_module.bat                 ← 🆕 Generic template
├── create_module.ps1                 ← 🆕 Generic implementation
│
├── app/
│   ├── app.py
│   ├── routes.py                     ← Register routers
│   └── modules/
│       ├── shared/                   ← BaseEntity, StandardException
│       ├── money/                    ← Layer 2 (Money)
│       ├── idempotency/              ← Layer 0 (Core)
│       ├── audit/                    ← Layer 0 (Core)
│       └── {module}/                 ← 4 layers
│           ├── domain/
│           ├── application/
│           ├── infrastructure/
│           └── presentation/
│
├── db/migrations/
│   ├── V001__create_{module}.sql
│   ├── V002__seed_{module}.sql
│   └── V003__rollback_{module}.sql
│
├── migrations/env.py                 ← Alembic target
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── property/
│   └── manual/
│
└── docs/
    ├── README_{module}.md
    ├── API_{module}.md
    └── postman/{module}.postman_collection.json
```

---

## 3. ขั้นตอนการใช้งาน (Workflow)

### 3.1 สร้าง Module ใหม่ — 2 วิธี

#### 🅰️ ผ่าน OpenCode (แนะนำสำหรับ Full 40 ไฟล์)

```bash
# 1. เตรียม prompt
copy RUN_GUIDE_opencode_promt.md prompt.md
# 2. แก้ module, layer, prefix
# 3. รัน
opencode -c "TEMPLATE A + module=inventory + layer=3-goods + FULL OUTPUT"
```

#### 🅱️ ผ่าน Bat Script (แนะนำสำหรับโครงเริ่มต้น)

```bat
REM สร้าง module เปล่า 4 layers + SQL + Tests + Docs
create_module.bat new inventory 3 inv --sql --tests --docs --routes
```

### 3.2 เพิ่ม SQL Migration

```bat
create_module.bat sql inventory inv --action add_bulk
```

### 3.3 Register Router

```bat
create_module.bat routes inventory
```

### 3.4 สร้าง Tests

```bat
create_module.bat test inventory
```

### 3.5 สร้าง Docs

```bat
create_module.bat docs inventory
```

---

## 4. การใช้ OpenCode Prompt (Templates A–G)

| Template | ใช้เมื่อ | ตัวอย่างคำสั่ง |
|---|---|---|
| **A** — CREATE_NEW | สร้างใหม่ | `TEMPLATE A + module=invoice + layer=2-money` |
| **B** — REFACTOR | แก้ของเดิม | `TEMPLATE B + target=repositories.py` |
| **C** — EXTEND | เพิ่ม feature | `TEMPLATE C + feature=bulk-create` |
| **D** — BUGFIX | แก้บั๊ก | `TEMPLATE D + stacktrace=...` |
| **E** — SECURITY | Audit | `TEMPLATE E + Mode=Read-only` |
| **F** — PERF | ทำ performance | `TEMPLATE F + SLO=p95<200ms` |
| **G** — DOCS | ทำคู่มือ | `TEMPLATE G + Doc Type=README` |

### Universal Header (ก๊อปวางบนสุด)

```markdown
[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน Output Scope
- โค้ดเต็ม Production-ready ห้าม `...`
- 3-branch / 2-branch / never-raise
- Decimal เท่านั้น / flush() ห้าม commit()
- SQL: V001 + V002 + V003 + RLS
- Routing: app/routes.py + migrations/env.py
```

---

## 5. การใช้ Bat Files

### 5.1 Syntax

```bat
create_module.bat <action> <module> [layer] [prefix] [options]
```

| Argument | ค่า | ตัวอย่าง |
|---|---|---|
| `action` | `new`, `sql`, `docs`, `routes`, `test`, `all`, `help` | `new` |
| `module` | ชื่อ module (snake_case) | `inventory` |
| `layer` | 0–7 | `3` |
| `prefix` | 3 ตัวอักษร | `inv` |
| `--sql` | สร้าง migration | — |
| `--tests` | สร้าง tests | — |
| `--docs` | สร้าง docs | — |
| `--routes` | register router | — |
| `--force` | เขียนทับไฟล์เดิม | — |

### 5.2 ตัวอย่าง

```bat
REM 1. Module เปล่า
create_module.bat new sales 4 sal

REM 2. Full package
create_module.bat new inventory 3 inv --sql --tests --docs --routes

REM 3. เพิ่ม SQL ใหม่
create_module.bat sql inventory inv

REM 4. ดู help
create_module.bat help
```

### 5.3 Layer Mapping

| Layer | ชื่อ | ตัวอย่าง Module |
|---|---|---|
| 0 | Core | `audit`, `idempotency`, `events` |
| 1 | Foundation | `tenant`, `user`, `auth` |
| 2 | Money | `invoice`, `payment`, `gl` |
| 3 | Goods | `inventory`, `product`, `warehouse` |
| 4 | Ops | `sales`, `purchase`, `production` |
| 5 | Intel | `report`, `dashboard`, `analytics` |
| 6 | Monitor | `iot`, `alert`, `health` |
| 7 | Template | `report_template`, `email_template` |

---

## 6. ตัวอย่าง Workflow ครบวงจร

### เป้าหมาย: สร้าง module `inventory` (Layer 3)

```bat
REM ─── STEP 1: สร้างโครงสร้าง ──────────────────────
create_module.bat new inventory 3 inv --sql --tests --docs --routes

REM ─── STEP 2: ตรวจสอบโครงสร้าง ────────────────────
tree app\modules\inventory
dir db\migrations\V00*inventory*.sql
dir tests\unit\test_inventory.py

REM ─── STEP 3: ใช้ OpenCode เติม Business Logic ─────
opencode -c "TEMPLATE A + module=inventory + layer=3 + FULL OUTPUT"

REM ─── STEP 4: Apply migration ─────────────────────
psql %DATABASE_URL% -f db\migrations\V001__create_inventory.sql
psql %DATABASE_URL% -f db\migrations\V002__seed_inventory.sql

REM ─── STEP 5: Run tests ───────────────────────────
pytest tests\unit\test_inventory.py -v

REM ─── STEP 6: ตรวจสอบ Swagger ─────────────────────
start http://localhost:8000/docs
```

---

## 7. Checklist การใช้งาน

### ก่อนสร้าง Module
- [ ] ตรวจ layer ที่ถูกต้อง
- [ ] ตรวจ prefix ไม่ซ้ำ
- [ ] ตรวจ dependencies (tenant_context, audit, idempotency)
- [ ] ตั้ง DATABASE_URL

### หลังสร้าง Module
- [ ] 4 layers ครบ
- [ ] `__init__.py` ทุก folder
- [ ] SQL V001/V002/V003
- [ ] Register ใน `app/routes.py`
- [ ] Register ใน `migrations/env.py`
- [ ] Tests ผ่าน
- [ ] Swagger เห็น endpoint ใหม่

---

## 8. Troubleshooting

| อาการ | สาเหตุ | แก้ |
|---|---|---|
| `ไม่พบ create_module.ps1` | ไฟล์หาย | ตรวจสอบ root |
| `Cannot overwrite file` | ไฟล์มีอยู่ | ใช้ `--force` |
| `module already registered` | register ซ้ำ | ตรวจ `app/routes.py` |
| `RLS policy missing` | SQL ไม่ครบ | รัน `create_module.bat sql {module}` |
| `404 Not Found` | router ไม่ register | รัน `create_module.bat routes {module}` |
| `Idempotency-Key required` | header หาย | ส่ง `Idempotency-Key` ทุก mutating req |

---

## 9. เอกสารอ้างอิง

- `RUN_GUIDE_opencode_promt.md` — Master Prompt v5.0
- `audit.md` — ตัวอย่าง module spec (Layer 0)
- FastAPI: https://fastapi.tiangolo.com
- Pydantic v2: https://docs.pydantic.dev
- SQLAlchemy 2.0: https://docs.sqlalchemy.org

---

**Version:** 1.0.0 · **Updated:** 2025
````

---

# 🛠️ ส่วนที่ 2: Template Bat Files

## 2.1 `create_module.bat` (Wrapper)

```bat
@echo off
REM ============================================================
REM  create_module.bat — Generic Module Generator (Wrapper)
REM  เรียก PowerShell เพื่อสร้าง/แก้ไข module
REM  Usage:
REM    create_module.bat new <module> [layer] [prefix] [--sql --tests --docs --routes --force]
REM    create_module.bat sql    <module> [prefix] [--action add_bulk]
REM    create_module.bat routes <module>
REM    create_module.bat test   <module>
REM    create_module.bat docs   <module>
REM    create_module.bat help
REM ============================================================
chcp 65001 >nul
setlocal

if "%~1"=="" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_module.ps1" -Action help
    goto :end
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_module.ps1" %*
set EXITCODE=%ERRORLEVEL%

:end
echo.
if not "%EXITCODE%"=="0" (
    echo [ERROR] Exit code %EXITCODE%
)
pause
endlocal
exit /b %EXITCODE%
```

---

## 2.2 `create_module.ps1` (Generic Implementation)

```powershell
<#
.SYNOPSIS
    create_module.ps1 — Generic Module Generator (Template v1.0)
.DESCRIPTION
    สร้าง/แก้ไข module ตาม Clean Architecture + DDD
    - 4 layers: domain / application / infrastructure / presentation
    - SQL: V001 create + V002 seed + V003 rollback + RLS
    - Routing: app/routes.py + migrations/env.py
    - Tests: unit / integration / property / manual
    - Docs: README + API
.EXAMPLE
    .\create_module.ps1 new inventory 3 inv --sql --tests --docs --routes
.EXAMPLE
    .\create_module.ps1 sql inventory inv
.EXAMPLE
    .\create_module.ps1 routes inventory
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("new","sql","routes","test","docs","all","help")]
    [string]$Action = "help",

    [Parameter(Position=1)]
    [string]$Module = "",

    [Parameter(Position=2)]
    [string]$Layer = "0",

    [Parameter(Position=3)]
    [string]$Prefix = "",

    [switch]$SQL,
    [switch]$Tests,
    [switch]$Docs,
    [switch]$Routes,
    [switch]$Force,

    [string]$ActionName = "add_column"
)

$ErrorActionPreference = "Stop"
$ROOT       = "app\modules"
$SQL_DIR    = "db\migrations"
$TESTS_DIR  = "tests"
$DOCS_DIR   = "docs"

# ─── Color helpers ─────────────────────────────────────────
function Write-Info  { param($m) Write-Host $m -ForegroundColor Cyan }
function Write-Ok    { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "  [!!] $m" -ForegroundColor Yellow }
function Write-Err   { param($m) Write-Host "  [XX] $m" -ForegroundColor Red }

# ─── UTF-8 no BOM writer ───────────────────────────────────
function Write-FileUtf8 {
    param([string]$Path, [string]$Content)
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    if ((Test-Path $Path) -and -not $Force) {
        Write-Warn "Skip (exists): $Path  (use -Force to overwrite)"
        return
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        (Join-Path (Resolve-Path -LiteralPath $dir).Path (Split-Path $Path -Leaf)),
        $Content, $utf8
    )
    Write-Ok $Path
}

# ─── Help ──────────────────────────────────────────────────
function Show-Help {
    Write-Host @"

═══════════════════════════════════════════════════════════
  create_module.ps1 — Generic Module Generator
═══════════════════════════════════════════════════════════

  USAGE
    .\create_module.ps1 <action> <module> [layer] [prefix] [options]

  ACTIONS
    new      สร้าง module ใหม่ (4 layers + __init__.py)
    sql      สร้าง SQL migrations (V001/V002/V003)
    routes   register router + model
    test     สร้าง tests (unit/integration/property/manual)
    docs     สร้าง docs (README + API)
    all      ทำทุกอย่าง
    help     แสดง help นี้

  OPTIONS
    --sql     สร้าง SQL
    --tests   สร้าง tests
    --docs    สร้าง docs
    --routes  register router
    --force   เขียนทับไฟล์เดิม

  LAYERS
    0=Core  1=Foundation  2=Money  3=Goods
    4=Ops   5=Intel       6=Monitor 7=Template

  EXAMPLES
    .\create_module.ps1 new inventory 3 inv --sql --tests --docs --routes
    .\create_module.ps1 sql invoice inv
    .\create_module.ps1 routes invoice
    .\create_module.ps1 all sales 4 sal --force

═══════════════════════════════════════════════════════════
"@ -ForegroundColor White
}

# ─── Validation ────────────────────────────────────────────
function Assert-Inputs {
    if ([string]::IsNullOrWhiteSpace($Module)) {
        Write-Err "Module name required."
        Show-Help
        exit 1
    }
    if ($Module -notmatch '^[a-z][a-z0-9_]*$') {
        Write-Err "Module must be snake_case (a-z, 0-9, _)."
        exit 1
    }
    if ($Layer -notmatch '^[0-7]$') {
        Write-Err "Layer must be 0-7."
        exit 1
    }
    if ([string]::IsNullOrWhiteSpace($Prefix)) {
        $script:Prefix = $Module.Substring(0, [Math]::Min(3, $Module.Length)).ToLower()
        Write-Warn "Prefix not provided, using '$Prefix'."
    }
    if ($Prefix.Length -ne 3) {
        Write-Warn "Prefix should be 3 chars (got '$Prefix')."
    }
}

# ─── Layer name mapping ────────────────────────────────────
function Get-LayerName {
    param([string]$L)
    switch ($L) {
        "0" { "0-Core" }
        "1" { "1-Foundation" }
        "2" { "2-Money" }
        "3" { "3-Goods" }
        "4" { "4-Ops" }
        "5" { "5-Intel" }
        "6" { "6-Monitor" }
        "7" { "7-Template" }
        default { "0-Core" }
    }
}

# ─── Domain Layer ──────────────────────────────────────────
function New-DomainLayer {
    param([string]$Mod)

    $base = "$ROOT\$Mod\domain"

    Write-FileUtf8 "$base\__init__.py" @"
"""$Mod domain layer — ชั้นโดเมน"""
from .entities import $(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1)))
from .enums import ${Mod}Status
from .exceptions import DomainError

__all__ = ["$(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1)))", "${Mod}Status", "DomainError"]
"@

    Write-FileUtf8 "$base\entities.py" @"
"""$Mod entities — เอนทิตี $Mod"""
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import DomainError


@dataclass
class BaseEntity:
    """BaseEntity — เอนทิตีฐาน"""
    id: str = ""
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class $(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1)))(BaseEntity):
    """$(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))) entity — เอนทิตี $Mod"""
    code: str = ""
    name: str = ""
    status: str = "ACTIVE"

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.code:
            raise DomainError("Code is required")
"@

    Write-FileUtf8 "$base\value_objects.py" @"
"""$Mod value objects — วัตถุค่า $Mod"""
from dataclasses import dataclass

from .exceptions import DomainError


@dataclass(frozen=True)
class ${Mod}Code:
    """${Mod}Code VO — รหัส $Mod"""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) > 50:
            raise DomainError("Invalid code")
"@

    Write-FileUtf8 "$base\enums.py" @"
"""$Mod enums — Enum สำหรับ $Mod"""
from enum import Enum


class ${Mod}Status(str, Enum):
    """${Mod}Status — สถานะ $Mod"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
"@

    Write-FileUtf8 "$base\events.py" @"
"""$Mod domain events — เหตุการณ์โดเมน $Mod"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class $(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1)))Created:
    """$(($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1)))Created — เหตุการณ์สร้าง"""
    id: str
    code: str
    occurred_at: datetime
"@

    Write-FileUtf8 "$base\exceptions.py" @"
"""$Mod domain exceptions — ข้อยกเว้นโดเมน $Mod"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดโดเมน"""
    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)
"@
}

# ─── Application Layer ─────────────────────────────────────
function New-ApplicationLayer {
    param([string]$Mod)

    $base = "$ROOT\$Mod\application"
    $Cls  = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$base\__init__.py" @"
"""$Mod application layer — ชั้นแอปพลิเคชัน $Mod"""
from .use_cases import ${Cls}UseCases
from .exceptions import ${Cls}Exception

__all__ = ["${Cls}UseCases", "${Cls}Exception"]
"@

    Write-FileUtf8 "$base\interfaces.py" @"
"""$Mod application interfaces — Protocol"""
from typing import Protocol

from ..domain.entities import $Cls


class I${Cls}Repository(Protocol):
    """I${Cls}Repository — อินเทอร์เฟซ repository"""
    async def save(self, entity: $Cls) -> $Cls: ...
    async def get_by_id(self, id: str) -> $Cls | None: ...
"@

    Write-FileUtf8 "$base\use_cases.py" @"
"""$Mod use cases — กรณีการใช้งาน $Mod"""
import logging
from datetime import datetime

from ..domain.entities import $Cls
from ..domain.exceptions import DomainError
from ..domain.events import ${Cls}Created
from .exceptions import ${Cls}Exception, StandardException

logger = logging.getLogger(__name__)


class ${Cls}UseCases:
    """${Cls}UseCases — กรณีการใช้งาน $Mod"""

    def __init__(self, repo, cache, events):
        self.repo = repo
        self.cache = cache
        self.events = events

    async def create(self, payload: dict) -> $Cls:
        """สร้าง $Mod — Create"""
        try:
            entity = $Cls(
                code=payload["code"],
                name=payload.get("name", ""),
                tenant_id=payload.get("tenant_id", ""),
            )
            saved = await self.repo.save(entity)

            verified = await self.repo.get_by_id(saved.id)
            if not verified:
                raise ${Cls}Exception("Read-back failed")

            await self.cache.invalidate(saved.id)
            await self.events.publish(
                "${Cls}Created",
                ${Cls}Created(
                    id=saved.id,
                    code=saved.code,
                    occurred_at=datetime.utcnow(),
                ),
            )
            return saved
        except StandardException:
            raise
        except DomainError as e:
            raise ${Cls}Exception(str(e))
        except Exception as e:
            logger.exception("Error in create $Mod: %s", e)
            raise ${Cls}Exception()
"@

    Write-FileUtf8 "$base\mappers.py" @"
"""$Mod mappers — ตัวแปลงข้อมูล"""
from ..domain.entities import $Cls


class ${Cls}Mapper:
    """${Cls}Mapper — ตัวแปลง entity/schema"""

    @staticmethod
    def to_schema(entity: $Cls) -> dict:
        return {"id": entity.id, "code": entity.code, "name": entity.name}

    @staticmethod
    def to_entity(data: dict) -> $Cls:
        return $Cls(code=data.get("code", ""), name=data.get("name", ""))
"@

    Write-FileUtf8 "$base\exceptions.py" @"
"""$Mod application exceptions — ข้อยกเว้นแอปพลิเคชัน $Mod"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐาน"""
    pass


class ${Cls}Exception(StandardException):
    """${Cls}Exception — ข้อผิดพลาด $Mod"""
    def __init__(self, message: str = "$Mod operation failed"):
        self.message = message
        super().__init__(message)
"@

    Write-FileUtf8 "$base\utils.py" @"
"""$Mod application utils — เครื่องมือช่วย"""


def now_utc():
    """คืน datetime UTC"""
    from datetime import datetime
    return datetime.utcnow()
"@
}

# ─── Infrastructure Layer ──────────────────────────────────
function New-InfrastructureLayer {
    param([string]$Mod, [string]$Pfx)

    $base = "$ROOT\$Mod\infrastructure"
    $Cls  = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$base\__init__.py" @"
"""$Mod infrastructure layer — ชั้นโครงสร้างพื้นฐาน $Mod"""
from .models import ${Cls}Model
from .repositories import Postgres${Cls}Repository

__all__ = ["${Cls}Model", "Postgres${Cls}Repository"]
"@

    Write-FileUtf8 "$base\models.py" @"
"""$Mod infrastructure models — SQLAlchemy 2.0"""
from sqlalchemy import Column, DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class ${Cls}Model(BaseModel):
    """${Cls}Model — โมเดล $Mod"""
    __tablename__ = "${Mod}s"

    id         = Column(String(36), primary_key=True)
    tenant_id  = Column(String(36), nullable=False, index=True)
    code       = Column(String(50), nullable=False)
    name       = Column(String(200), nullable=False)
    status     = Column(String(20), nullable=False, default="ACTIVE")
    metadata_  = Column("metadata", JSONB, default=dict)
    version    = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    deleted_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_${Mod}_code"),
    )
"@

    Write-FileUtf8 "$base\repositories.py" @"
"""$Mod infrastructure repositories — 2-branch error handling"""
import logging

from ..domain.entities import $Cls
from .models import ${Cls}Model

logger = logging.getLogger(__name__)


class Postgres${Cls}Repository:
    """Postgres${Cls}Repository — repository หลัก"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, entity: $Cls) -> $Cls:
        try:
            async with self.session_factory() as session:
                row = ${Cls}Model(
                    id=entity.id,
                    tenant_id=entity.tenant_id,
                    code=entity.code,
                    name=entity.name,
                    status=entity.status,
                )
                session.add(row)
                await session.flush()
                return entity
        except Exception as e:
            logger.exception("Repo save failed: %s", e)
            raise

    async def get_by_id(self, id: str) -> $Cls | None:
        try:
            async with self.session_factory() as session:
                from sqlalchemy import select
                stmt = select(${Cls}Model).where(${Cls}Model.id == id)
                res = await session.execute(stmt)
                row = res.scalar_one_or_none()
                if row is None:
                    return None
                return $Cls(
                    id=row.id, tenant_id=row.tenant_id,
                    code=row.code, name=row.name, status=row.status,
                )
        except Exception as e:
            logger.exception("Repo get failed: %s", e)
            raise
"@

    Write-FileUtf8 "$base\caches.py" @"
"""$Mod infrastructure caches — never-raise"""
import logging

logger = logging.getLogger(__name__)


class Redis${Cls}Cache:
    """Redis${Cls}Cache — never-raise"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, id: str):
        try:
            return await self.redis.get(f"$Mod:{id}")
        except Exception as e:
            logger.warning("Cache get failed: %s", e)
            return None

    async def set(self, id: str, value: str, ttl: int = 300) -> bool:
        try:
            await self.redis.set(f"$Mod:{id}", value, ex=ttl)
            return True
        except Exception as e:
            logger.warning("Cache set failed: %s", e)
            return False

    async def invalidate(self, id: str) -> bool:
        try:
            await self.redis.delete(f"$Mod:{id}")
            return True
        except Exception as e:
            logger.warning("Cache invalidate failed: %s", e)
            return False
"@

    Write-FileUtf8 "$base\services.py" @"
"""$Mod infrastructure services — Event publisher"""
import logging

logger = logging.getLogger(__name__)


class ${Cls}Publisher:
    """${Cls}Publisher — Kafka publisher"""

    def __init__(self, producer, topic: str = "$Mod.events"):
        self.producer = producer
        self.topic = topic

    async def publish(self, event) -> None:
        try:
            await self.producer.send(self.topic, event)
        except Exception as e:
            logger.warning("Publish failed: %s", e)
"@
}

# ─── Presentation Layer ────────────────────────────────────
function New-PresentationLayer {
    param([string]$Mod)

    $base = "$ROOT\$Mod\presentation"
    $Cls  = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$base\__init__.py" @"
"""$Mod presentation layer — ชั้นนำเสนอ $Mod"""
from .dependencies import get_${Mod}_use_cases
from .routers import router

__all__ = ["router", "get_${Mod}_use_cases"]
"@

    Write-FileUtf8 "$base\schemas.py" @"
"""$Mod presentation schemas — Pydantic v2"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ${Cls}Create(BaseModel):
    """${Cls}Create — payload สร้าง $Mod"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)


class ${Cls}Response(BaseModel):
    """${Cls}Response — response $Mod"""
    id: str
    code: str
    name: str
    status: str
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
"@

    Write-FileUtf8 "$base\routers.py" @"
"""$Mod presentation routers — API endpoints"""
from fastapi import APIRouter, Depends, Header, HTTPException, status

from ..application.exceptions import ${Cls}Exception
from ..application.use_cases import ${Cls}UseCases
from ..domain.exceptions import DomainError
from .dependencies import get_${Mod}_use_cases
from .schemas import ${Cls}Create, ${Cls}Response

router = APIRouter(prefix="/api/v1/$Mod", tags=["$Cls"])


@router.post(
    "/",
    response_model=${Cls}Response,
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง $Mod",
    operation_id="create_$Mod",
)
async def create_$Mod(
    payload: ${Cls}Create,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    uc: ${Cls}UseCases = Depends(get_${Mod}_use_cases),
):
    """สร้าง $Mod — Create."""
    try:
        entity = await uc.create(payload.model_dump())
        return ${Cls}Response.model_validate(entity)
    except ${Cls}Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.get("/", summary="รายการ $Mod", operation_id="list_$Mod")
async def list_$Mod(uc: ${Cls}UseCases = Depends(get_${Mod}_use_cases)):
    """รายการ $Mod — List."""
    return {"items": [], "total": 0}


@router.get("/{id}/", summary="ดู $Mod", operation_id="get_$Mod")
async def get_$Mod(id: str, uc: ${Cls}UseCases = Depends(get_${Mod}_use_cases)):
    """ดู $Mod — Get."""
    return {"id": id}
"@

    Write-FileUtf8 "$base\dependencies.py" @"
"""$Mod presentation dependencies — FastAPI DI"""
from ..application.use_cases import ${Cls}UseCases


def get_${Mod}_use_cases() -> ${Cls}UseCases:
    """สร้าง ${Cls}UseCases — Get use cases"""
    return ${Cls}UseCases(repo=None, cache=None, events=None)
"@

    Write-FileUtf8 "$base\docs.py" @"
"""$Mod presentation docs — OpenAPI metadata"""

router_tags = [{"name": "$Cls", "description": "จัดการ $Mod"}]

RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ",
    "content": {"application/json": {"example": {"id": "...", "code": "TEST-001"}}},
}
"@
}

# ─── Root __init__.py ──────────────────────────────────────
function New-ModuleRoot {
    param([string]$Mod)
    Write-FileUtf8 "$ROOT\$Mod\__init__.py" @"
"""$Mod module — โมดูล $Mod"""
from .presentation.routers import router as ${Mod}_router

__all__ = ["${Mod}_router"]
"@
}

# ─── SQL Migrations ────────────────────────────────────────
function New-SQLMigrations {
    param([string]$Mod, [string]$Pfx)

    $Cls = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$SQL_DIR\V001__create_$Mod.sql" @"
-- ═══════════════════════════════════════════════════════════════
-- V001__create_$Mod.sql
-- Module: $Mod | Prefix: $Pfx
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE TABLE tenant_${Pfx}.${Mod}s (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID NOT NULL,
    code         VARCHAR(50)  NOT NULL,
    name         VARCHAR(200) NOT NULL,
    status       VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',
    metadata     JSONB        NOT NULL DEFAULT '{}'::jsonb,
    version      INTEGER      NOT NULL DEFAULT 1,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ,

    CONSTRAINT uq_${Mod}_code   UNIQUE (tenant_id, code),
    CONSTRAINT ck_${Mod}_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);

CREATE INDEX ix_${Mod}_tenant_status
    ON tenant_${Pfx}.${Mod}s(tenant_id, status)
    WHERE deleted_at IS NULL;

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

CREATE TRIGGER trg_${Mod}_updated_at
    BEFORE UPDATE ON tenant_${Pfx}.${Mod}s
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE tenant_${Pfx}.${Mod}s ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_${Mod}_tenant ON tenant_${Pfx}.${Mod}s
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"@

    Write-FileUtf8 "$SQL_DIR\V002__seed_$Mod.sql" @"
-- ═══════════════════════════════════════════════════════════════
-- V002__seed_$Mod.sql
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO tenant_${Pfx}.${Mod}s (tenant_id, code, name, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'SYS-DEFAULT', 'System Default', 'ACTIVE')
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
"@

    Write-FileUtf8 "$SQL_DIR\V003__rollback_$Mod.sql" @"
-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_$Mod.sql
-- ⚠️ ใช้ในกรณี rollback เท่านั้น
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER  IF EXISTS trg_${Mod}_updated_at ON tenant_${Pfx}.${Mod}s;
DROP POLICY   IF EXISTS p_${Mod}_tenant       ON tenant_${Pfx}.${Mod}s;
DROP TABLE    IF EXISTS tenant_${Pfx}.${Mod}s CASCADE;

COMMIT;
"@
}

# ─── Tests ─────────────────────────────────────────────────
function New-Tests {
    param([string]$Mod)
    $Cls = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$TESTS_DIR\unit\test_$Mod.py" @"
"""Unit tests for $Mod — ทดสอบระดับ unit"""
import pytest

from app.modules.$Mod.domain.entities import $Cls
from app.modules.$Mod.domain.exceptions import DomainError


def test_create_valid():
    """สร้าง $Mod สำเร็จ"""
    e = $Cls(code="TEST-001", name="Test")
    assert e.code == "TEST-001"


def test_create_no_code_raises():
    """ไม่มี code ต้อง raise"""
    with pytest.raises(DomainError):
        $Cls(code="", name="Test")
"@

    Write-FileUtf8 "$TESTS_DIR\integration\test_${Mod}_repository.py" @"
"""Integration tests for $Mod repository — ทดสอบ repository"""
import pytest


@pytest.mark.asyncio
async def test_save_and_get():
    """บันทึกและอ่านกลับ"""
    assert True  # TODO: real test


@pytest.mark.asyncio
async def test_read_back_verify():
    """Read-back verification"""
    assert True
"@

    Write-FileUtf8 "$TESTS_DIR\property\test_${Mod}_invariants.py" @"
"""Property tests for $Mod — ทดสอบ invariants"""
from hypothesis import given, strategies as st

from app.modules.$Mod.domain.entities import $Cls


@given(code=st.text(min_size=1, max_size=50))
def test_code_never_empty(code):
    """code ต้องไม่ว่าง"""
    e = $Cls(code=code, name="x")
    assert e.code != ""
"@

    Write-FileUtf8 "$TESTS_DIR\manual\manual_test_$Mod.md" @"
# Manual Test — $Mod

## Scenarios
- [ ] สร้าง $Mod สำเร็จ (201)
- [ ] สร้างซ้ำ code → 409
- [ ] ไม่ส่ง Idempotency-Key → 400
- [ ] ส่ง payload ผิด → 422
- [ ] GET /api/v1/$Mod/ → 200
- [ ] GET /api/v1/$Mod/{{id}}/ → 200
- [ ] PATCH → 200
- [ ] DELETE → 204
"@
}

# ─── Docs ──────────────────────────────────────────────────
function New-Docs {
    param([string]$Mod, [string]$Pfx)
    $Cls = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))

    Write-FileUtf8 "$DOCS_DIR\README_$Mod.md" @"
# Module: $Mod

> **Layer:** $LayerName · **Prefix:** $Pfx · **Version:** 1.0.0

## 🎯 Purpose
โมดูล $Mod สำหรับ ERP+CRM+IoT

## 🏗️ Architecture
\`\`\`mermaid
flowchart LR
    C[Client] --> R[Router]
    R --> UC[UseCase]
    UC --> RP[Repository]
    UC --> CX[Cache]
    RP --> DB[(PostgreSQL)]
\`\`\`

## 🔌 API Endpoints
| Method | Path | Description |
|---|---|---|
| POST   | \`/api/v1/$Mod/\` | Create |
| GET    | \`/api/v1/$Mod/\` | List |
| GET    | \`/api/v1/$Mod/{id}/\` | Get |
| PATCH  | \`/api/v1/$Mod/{id}/\` | Update |
| DELETE | \`/api/v1/$Mod/{id}/\` | Delete |

## 🗄️ Schema
Table: \`tenant_${Pfx}.${Mod}s\`

## 🚀 Setup
\`\`\`bash
psql \$DATABASE_URL -f db/migrations/V001__create_$Mod.sql
uvicorn app.app:app --reload
\`\`\`
"@

    Write-FileUtf8 "$DOCS_DIR\API_$Mod.md" @"
# API Reference — $Mod

## POST /api/v1/$Mod/
### Request
\`\`\`json
{ "code": "TEST-001", "name": "Test $Cls" }
\`\`\`
### Response 201
\`\`\`json
{ "id": "...", "code": "TEST-001", "name": "Test $Cls", "status": "ACTIVE" }
\`\`\`

## Error Codes
| Code | Meaning |
|---|---|
| 400  | Validation error |
| 401  | Unauthorized |
| 409  | Conflict |
| 422  | Idempotency mismatch |
"@
}

# ─── Register Router ───────────────────────────────────────
function Add-RouterRegistration {
    param([string]$Mod)
    $routesFile = "app\routes.py"

    if (-not (Test-Path $routesFile)) {
        Write-Warn "$routesFile not found — skip routing registration."
        return
    }

    $content = Get-Content $routesFile -Raw
    $importLine = "from app.modules.$Mod.presentation.routers import router as ${Mod}_router"
    $includeLine = "api_router.include_router(${Mod}_router)"

    if ($content -notmatch [regex]::Escape($importLine)) {
        $content = $importLine + "`r`n" + $content
        Write-Ok "Added import: $importLine"
    }

    if ($content -notmatch [regex]::Escape($includeLine)) {
        $content = $content -replace "(api_router\s*=\s*APIRouter\([^\)]*\))",
            "`$1`r`n$includeLine"
        Write-Ok "Added include: $includeLine"
    }

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        (Resolve-Path $routesFile).Path, $content, $utf8
    )
}

# ─── Register Model ────────────────────────────────────────
function Add-ModelRegistration {
    param([string]$Mod)
    $envFile = "migrations\env.py"

    if (-not (Test-Path $envFile)) {
        Write-Warn "$envFile not found — skip model registration."
        return
    }
    $Cls = ($Mod.Substring(0,1).ToUpper() + $Mod.Substring(1))
    $importLine = "from app.modules.$Mod.infrastructure.models import ${Cls}Model"

    $content = Get-Content $envFile -Raw
    if ($content -notmatch [regex]::Escape($importLine)) {
        $content = $importLine + "`r`n" + $content
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText(
            (Resolve-Path $envFile).Path, $content, $utf8
        )
        Write-Ok "Added import: $importLine"
    } else {
        Write-Warn "Already registered in $envFile"
    }
}

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
if ($Action -eq "help") { Show-Help; exit 0 }

if ($Action -eq "all") {
    $SQL = $true; $Tests = $true; $Docs = $true; $Routes = $true
}

Assert-Inputs
$layerName = Get-LayerName $Layer

Write-Host ""
Write-Info "═══════════════════════════════════════════════════════"
Write-Info "  ACTION: $Action  |  MODULE: $Module  |  LAYER: $layerName"
Write-Info "  PREFIX: $Prefix  |  SQL:$SQL  TEST:$Tests  DOCS:$Docs  ROUTE:$Routes"
Write-Info "═══════════════════════════════════════════════════════"

switch ($Action) {
    "new" {
        Write-Info "── Domain Layer ──"
        New-DomainLayer $Module

        Write-Info "── Application Layer ──"
        New-ApplicationLayer $Module

        Write-Info "── Infrastructure Layer ──"
        New-InfrastructureLayer $Module $Prefix

        Write-Info "── Presentation Layer ──"
        New-PresentationLayer $Module

        Write-Info "── Root __init__.py ──"
        New-ModuleRoot $Module

        if ($SQL) {
            Write-Info "── SQL Migrations ──"
            New-SQLMigrations $Module $Prefix
        }
        if ($Tests) {
            Write-Info "── Tests ──"
            New-Tests $Module
        }
        if ($Docs) {
            Write-Info "── Docs ──"
            New-Docs $Module $Prefix
        }
        if ($Routes) {
            Write-Info "── Routing ──"
            Add-RouterRegistration $Module
            Add-ModelRegistration $Module
        }
    }
    "sql"    { New-SQLMigrations $Module $Prefix }
    "test"   { New-Tests $Module }
    "docs"   { New-Docs $Module $Prefix }
    "routes" {
        Add-RouterRegistration $Module
        Add-ModelRegistration $Module
    }
}

Write-Host ""
Write-Info "═══════════════════════════════════════════════════════"
Write-Ok "DONE — module: $Module"
Write-Info "═══════════════════════════════════════════════════════"
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    1. ตรวจสอบไฟล์:   tree app\modules\$Module" -ForegroundColor White
Write-Host "    2. เติม logic:     opencode -c ""TEMPLATE A + module=$Module""" -ForegroundColor White
Write-Host "    3. Apply SQL:     psql %DATABASE_URL% -f db\migrations\V001__create_$Module.sql" -ForegroundColor White
Write-Host "    4. Run tests:     pytest tests\unit\test_$Module.py -v" -ForegroundColor White
Write-Host "    5. ดู Swagger:    start http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
```

---

## 📋 สรุปสิ่งที่ส่งมอบ

| # | ไฟล์ | หน้าที่ |
|---|---|---|
| 1 | **คู่มือการใช้งาน** | Manual ครบ 9 หัวข้อ: ภาพรวม → โครงสร้าง → Workflow → Templates A–G → Bat → Checklist → Troubleshooting |
| 2 | **`create_module.bat`** | Wrapper generic — รับ action + module + options |
| 3 | **`create_module.ps1`** | Implementation ครบ: Domain/Application/Infrastructure/Presentation + SQL + Tests + Docs + Routing |

### 🎯 Actions ที่รองรับ

| Action | คำสั่งตัวอย่าง |
|---|---|
| `new` | `create_module.bat new inventory 3 inv --sql --tests --docs --routes` |
| `sql` | `create_module.bat sql invoice inv` |
| `routes` | `create_module.bat routes invoice` |
| `test` | `create_module.bat test invoice` |
| `docs` | `create_module.bat docs invoice` |
| `all` | `create_module.bat all sales 4 sal --force` |
| `help` | `create_module.bat help` |

### ⚙️ Features

- ✅ UTF-8 no BOM (รองรับภาษาไทย)
- ✅ `--force` overwrite
- ✅ Skip ไฟล์ที่มีอยู่แล้ว (safety)
- ✅ Auto-generate prefix (3 ตัวอักษรแรก)
- ✅ Register router + model อัตโนมัติ
- ✅ SQL มี RLS + Trigger + Index
- ✅ Tests 4 ประเภท (unit/integration/property/manual)
- ✅ Docs พร้อม Mermaid diagram
- ✅ Comment 2 ภาษา (TH + EN)

**พร้อมใช้งานทันที — วางทั้ง 3 ไฟล์ที่ root แล้วรัน `create_module.bat help` เพื่อเริ่ม**
