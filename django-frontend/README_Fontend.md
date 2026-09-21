# 🐍 ปัญหา: PowerShell ใช้ syntax Linux + venv ซ้อนกัน

## 🔍 วิเคราะห์จาก log

ปัญหามี 3 จุดพร้อมกัน:

| # | สาเหตุ | หลักฐาน |
|---|---|---|
| 1 | **`source .venv/bin/activate` เป็น syntax Linux/Mac** | `source: The term 'source' is not recognized` |
| 2 | **ยังอยู่ใน venv ของ `fastapi-backend`** | prompt: `(fastapi-clean-architecture-ddd-template)` |
| 3 | **มี venv ซ้อน 2 ตัว** — `venv/` (จาก scaffold) + `.venv/` (สร้างใหม่) | `python -m venv .venv` สำเร็จ |

**ผลลัพธ์:** `pip install` ไม่ได้ลงใน venv ของ django-frontend → ลง user site-packages ของ Python 3.14 → แต่ `python` ที่รันยังชี้ไปที่ venv ของ fastapi-backend → หา Django ไม่เจอ

---

## ⚡ Quick Fix — คำสั่งเดียว

**ปิด terminal นี้ทิ้ง** → เปิด PowerShell **ใหม่** → รัน:

```powershell
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\django-frontend

# ถ้าไม่มี venv → สร้าง
# (ข้ามถ้ามีแล้ว)
if (-not (Test-Path .venv)) { python -m venv .venv }

# ใช้ python ตรงจาก venv — ไม่ต้องพึ่ง activate
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8001
```

**ข้อดี:** ไม่ต้อง activate → ไม่มีปัญหา PowerShell policy / ภาษา syntax

---

## 🧹 ล้างของเก่าก่อน (ถ้าสับสน)

```powershell
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\django-frontend

# ดูว่ามี venv กี่ตัว
Get-ChildItem -Directory -Force | Where-Object { $_.Name -match '^\.?venv$' }
# ผลลัพธ์อาจเป็น: venv  และ  .venv  (เลือกใช้ตัวเดียว)

# แนะนำ: ลบทั้ง 2 แล้วสร้างใหม่
Remove-Item -Recurse -Force .\venv, .\.venv -ErrorAction SilentlyContinue

# ลบ user site-packages ที่ pip หลงติดตั้ง (สะอาดกว่า)
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\Django*"     -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\httpx*"      -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\dotenv*"     -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\asgiref*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\sqlparse*"   -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\httpcore*"   -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\h11*"        -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\anyio*"      -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\idna*"       -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\certifi*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\sniffio*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\typing_ext*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\tzdata*"     -ErrorAction SilentlyContinue
```

---

## ✅ วิธี Activate venv ที่ถูกต้อง

| Shell | คำสั่ง |
|---|---|
| **PowerShell** (Windows) | `.\.venv\Scripts\Activate.ps1` |
| **CMD** (Windows) | `.venv\Scripts\activate.bat` |
| **Git Bash / WSL** | `source .venv/Scripts/activate` |
| **Linux / macOS** | `source .venv/bin/activate` |

**ถ้าเจอ error policy:**

```
.\.venv\Scripts\Activate.ps1 : cannot be loaded because running scripts is disabled
```

แก้ชั่วคราว (เฉพาะ session):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

หรือแก้ถาวร (แนะนำ):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

---

## 🚨 อาการที่คุณเจอ — อธิบายให้ชัด

ตอนที่คุณรัน:

```powershell
(fastapi-clean-architecture-ddd-template) PS> pip install -r requirements.txt
Defaulting to user installation because normal site-packages is not writeable
```

**`pip` ตัวนี้คือ pip ของ `fastapi-backend\.venv`** (active อยู่) → พยายามลงใน venv นั้น → venv นั้น **read-only / permission denied** → pip เลย fallback ไปลง **user site-packages**

แล้วพอ:

```powershell
(fastapi-clean-architecture-ddd-template) PS> python manage.py runserver 8001
ModuleNotFoundError: No module named 'django'
```

**`python` ที่รันคือ python ของ `fastapi-backend\.venv`** → มันไม่เห็น user site-packages (เพราะ venv isolate) → หา Django ไม่เจอ

**รากปัญหา:** คุณสร้าง `.venv` ของ django-frontend แต่ **activate ไม่สำเร็จ** (เพราะใช้ syntax Linux) → เลยยังใช้ fastapi venv อยู่

---

## 🎯 วิธีที่แนะนำที่สุด — ใช้ Python ตรงจาก venv

**ไม่ต้อง activate, ไม่ต้องกังวล policy, ไม่ต้องพึ่ง PATH:**

```powershell
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\django-frontend

# 1. สร้าง venv (ครั้งเดียว)
python -m venv .venv

# 2. ติดตั้ง packages
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Verify
.\.venv\Scripts\python.exe -c "import django; print(django.get_version())"
# ควรได้: 5.0.6

# 4. Migrate + run
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8001
```

---

## 📜 สร้าง Helper Script — รันครั้งเดียวจบ

เซฟเป็น **`run-django.ps1`** ที่ `django-frontend\`:

```powershell
# run-django.ps1 — รัน Django โดยใช้ venv ตรง (ไม่ต้อง activate)
[CmdletBinding()]
param(
    [int]$Port = 8001,
    [switch]$Install,
    [switch]$Migrate,
    [switch]$Shell
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$Py   = Join-Path $Venv "Scripts\python.exe"

# ─── Create venv ถ้ายังไม่มี ─────────────────────
if (-not (Test-Path $Py)) {
    Write-Host "[--] Creating venv..." -ForegroundColor Cyan
    python -m venv $Venv
    $Install = $true
}

# ─── Install ถ้าขอ หรือ venv ใหม่ ────────────────
if ($Install) {
    Write-Host "[--] Installing requirements..." -ForegroundColor Cyan
    & $Py -m pip install --upgrade pip
    & $Py -m pip install -r (Join-Path $Root "requirements.txt")
}

# ─── Migrate ─────────────────────────────────────
if ($Migrate) {
    Write-Host "[--] Migrating..." -ForegroundColor Cyan
    & $Py (Join-Path $Root "manage.py") migrate --noinput
}

# ─── Shell mode ──────────────────────────────────
if ($Shell) {
    & $Py (Join-Path $Root "manage.py") shell
    exit
}

# ─── Runserver ───────────────────────────────────
Write-Host "[OK] Starting Django on port $Port..." -ForegroundColor Green
Write-Host "     http://localhost:$Port/" -ForegroundColor Cyan
& $Py (Join-Path $Root "manage.py") runserver $Port
```

**ใช้งาน:**

```powershell
# ครั้งแรก (สร้าง venv + ติดตั้ง + migrate + run)
.\run-django.ps1 -Install -Migrate

# ครั้งต่อไป (แค่ run)
.\run-django.ps1

# เปลี่ยนพอร์ต
.\run-django.ps1 -Port 9000

# Django shell
.\run-django.ps1 -Shell
```

---

## ⚠️ ข้อควรระวังเรื่อง venv ซ้อน

ตอนนี้คุณมี **2 venv** ที่ต่างคนต่างใช้:

```
fastapi-backend\
└── .venv\                     ← active อยู่ (prompt แสดง)

django-frontend\
├── venv\                      ← scaffold --setup สร้างไว้
└── .venv\                     ← คุณสร้างใหม่ด้วยมือ
```

**แนะนำ:** เก็บไว้แค่ **1 ตัว** — ผมแนะนำให้เก็บ `.venv` แล้วลบ `venv`

```powershell
Remove-Item -Recurse -Force .\venv -ErrorAction SilentlyContinue
```

หรือแก้ที่ `scaffold.ps1` ให้ใช้ `.venv` เป็นค่าเริ่มต้น (เพื่อความ consistent):

```powershell
# ใน scaffold.ps1 หา "venv" แล้วเปลี่ยนเป็น ".venv"
$venvPath = Join-Path $Root ".venv"
# ...
$pipExe    = Join-Path $Root ".venv\Scripts\pip.exe"
$pythonExe = Join-Path $Root ".venv\Scripts\python.exe"
```

---

## 🎯 TL;DR — คำสั่งที่ต้องรันตอนนี้

**ปิด terminal → เปิดใหม่ → คัดลอกวาง:**

```powershell
# ออกจาก venv ของ fastapi ก่อน (ถ้าเปิด prompt ใหม่จะสะอาดกว่า)
cd C:\github\fastapi-clean-architecture-ddd-erp-iot\django-frontend

# ลบของเก่า
Remove-Item -Recurse -Force .\venv, .\.venv -ErrorAction SilentlyContinue

# สร้างใหม่ + ติดตั้ง + รัน
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8001
```

เปิด browser: `http://127.0.0.1:8001/auth/login/`

---

**หมายเหตุ:** หลัง activate venv ถูกต้องแล้ว prompt จะขึ้น `(.venv) PS C:\...\.\.venv\Scripts\python.exe manage.py runserver 8001-frontend>` — ถ้ายังขึ้น `(fastapi-clean-architecture-ddd-template)` แสดงว่ายังใช้ venv ของ fastapi อยู่ ต้อง `deactivate` ก่อน


.\.venv\Scripts\python.exe manage.py runserver 8001

http://127.0.0.1:8001/auth/login/?next=/

python manage.py runserver 8001