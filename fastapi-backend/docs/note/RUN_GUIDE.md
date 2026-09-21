# คู่มือการรันโปรเจกต์ (Run Guide)

โปรเจกต์ FastAPI แบบ Clean Architecture + DDD สำหรับระบบ ERP / CRM / IoT โดยใช้ `uv` จัดการ dependencies และ `docker compose` สำหรับรันทั้งระบบในโหมด container (API + ฐานข้อมูล PostgreSQL + Redis + ตัวจัดการ pgAdmin / RedisInsight)

---

## 1. ข้อกำหนดเบื้องต้น (Prerequisites)

- **Python 3.14+** — โปรเจกต์ระบุเวอร์ชัน Python ไว้ที่ `.python-version`
- **uv** — tool สำหรับจัดการ Python project (ติดตั้งได้จาก https://docs.astral.sh/uv/)
- **Docker Desktop + docker compose** — สำหรับรันฐานข้อมูลและเขียนโค้ดแบบ full-stack
- **ระบบปฏิบัติการ** — Windows / macOS / Linux (คำสั่งในคู่มือนี้ใช้ผ่าน `make`

  > **หมายเหตุสำหรับ Windows** ถ้าไม่มี `make` ให้ใช้คำสั่งที่อยู่หลัง target ได้โดยตรง
  > เช่น คู่กันของ `make dev` คือ `uv run uvicorn app.app:app --reload`

---

## 2. ขั้นตอนติดตั้ง (Setup)

### 2.1 ติดตั้ง dependencies

รันจากโฟลเดอร์ `fastapi-backend`:

```bash
uv sync
```

`uv sync` จะอ่าน `pyproject.toml` + `uv.lock` และสร้าง virtual environment ให้อัตโนมัติ
(ไม่จำเป็นต้องสร้าง venv เอง)

### 2.2 สร้างไฟล์ `.env`

**สำคัญ:** ไฟล์ `.env` และ `.env.example` ในโฟลเดอร์นี้เป็นเอกสารอธิบายตัวแปร (รูปแบบ markdown)
**ไม่ใช่ไฟล์ dotenv จริง** — คุณต้องสร้างไฟล์ `.env` จริงขึ้นมาเอง เช่น:

```bash
touch .env
```

จากนั้นเติมค่าที่จำเป็นตามกลุ่มตัวแปรในส่วนถัดไป ค่าที่ต้องกำกับเป็นอย่างน้อย:

| กลุ่ม | ตัวแปรหลัก | ความหมาย |
| --- | --- | --- |
| `APPLICATION_*` | `APPLICATION_ENVIRONMENT` | `dev` / `homolog` / `production` |
| | `APPLICATION_NAME` | ชื่อแอปพลิเคชัน |
| | `APPLICATION_HOST`, `APPLICATION_PORT` | โฮสต์และพอร์ตของ API (พอร์ตที่ใช้ใน Docker) |
| `API_KEY_*` | `API_KEY_ENABLED`, `API_KEY_HEADER_NAME` | เปิด/ปิดการใช้ API Key และชื่อ header |
| `AUTH_*` | `AUTH_BCRYPT_ROUNDS`, `AUTH_ALGORITHM`, `AUTH_SOCIAL_GOOGLE_ENABLED` | ค่าความปลอดภัยของระบบ auth |
| `COOKIES_*` | `COOKIES_ACCESS_TOKEN_NAME`, `COOKIES_ACCESS_TOKEN_SECURE`, `COOKIES_REFRESH_TOKEN_NAME`, `COOKIES_REFRESH_TOKEN_SECURE`, `COOKIES_SAMESITE` | ชื่อและคุณสมบัติของ cookies (ค่า `COOKIES_*.MAX_AGE` คำนวณจากค่า JWT อัตโนมัติ) |
| `JWT_*` | `JWT_ACCESS_TOKEN_EXPIRES_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRES_DAYS` | อายุของ token |
| | `JWT_AUTO_GENERATE_KEYS`, `JWT_KEYS_DIR`, `JWT_SIGNING_KID`, `JWT_ENCRYPTION_KID` | การสร้างคีย์ JWK (ดูหัวข้อ 2.3) |
| `LOGS_*` | `LOGS_LEVEL`, `LOGS_FORMAT` | ระดับและรูปแบบของ log |
| `NGROK_AUTH_TOKEN` | `NGROK_AUTH_TOKEN` | token ของ ngrok (ถ้าใช้) |
| `POSTGRESQL_*` | `POSTGRESQL_HOST`, `POSTGRESQL_PORT`, `POSTGRESQL_DATABASE`, `POSTGRESQL_USERNAME`, `POSTGRESQL_PASSWORD` | ค่าเชื่อมต่อฐานข้อมูล |
| `REDIS_*` | `REDIS_SSL`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DATABASE` | ค่าเชื่อมต่อ Redis (`REDIS_URL`, `REDIS_NAMESPACE` คำนวณอัตโนมัติ) |
| `SECURITY_*` | `SECURITY_ADMIN_EMAIL`, `SECURITY_ADMIN_PASSWORD`, `SECURITY_EMAIL_ALLOWED_DOMAINS` | บัญชี admin เริ่มต้นและโดเมนอีเมลที่อนุญาต |
| `PGADMIN_*` | `PGADMIN_PORT`, `PGADMIN_EMAIL`, `PGADMIN_PASSWORD` | การเข้าสู่ระบบ pgAdmin container |
| `REDISINSIGHT_*` | `REDISINSIGHT_PORT`, `RI_REDIS_HOST`, `RI_REDIS_PORT`, `RI_REDIS_PASSWORD` | การเข้าสู่ระบบ RedisInsight container |

รายการตัวแปรครบทั้งหมดดูได้จาก `app/core/settings.py` และเอกสาร `.env.example`

### 2.3 สร้างคีย์ JWT (JWK)

โปรเจกต์ใช้คีย์ JWK (Ed25519 สำหรับ signing, X25519 สำหรับ encryption) สามารถให้แอปสร้างคีย์ให้อัตโนมัติได้
โดยตั้งค่าใน `.env`:

```env
JWT_AUTO_GENERATE_KEYS=true
JWT_KEYS_DIR=secrets/keys
```

เมื่อแอปเริ่มทำงานครั้งแรก ระบบจะสร้างคีย์ pair ลงใน `secrets/keys/`
(คีย์ส่วนตัวจะถูกเข้ารหัส PKCS8 และรายละเอียดทั้งหมดอธิบายไว้ใน `secrets/keys/README.md`)

---

## 3. การจัดการฐานข้อมูล (Migrate)

รัน migration เพื่อสร้าง schema ของ PostgreSQL:

```bash
make migrate
```

เทียบเท่า `uv run alembic upgrade head` — Alembic ถูก config ให้ใช้ engine จาก `app/core/database.py`
และรู้จักโมเดลทั้งหมดในโปรเจกต์ (User, Token, AccessToken, Knowledge, Notification เป็นต้น)

สร้าง migration ใหม่จากโมเดล (autogenerate):

```bash
make migration m="คำอธิบาย"
```

---

## 4. รันในโหมดพัฒนา (Dev)

```bash
make dev
```

เทียบเท่า `uv run uvicorn app.app:app --reload`

- API เริ่มต้นที่ **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- โหมดนี้ยังไม่ต้องใช้ Docker แต่อย่างไรก็ต้องมี PostgreSQL + Redis รันอยู่
  (ยกเว้นคุณ override ค่าฐานข้อมูลเป็น SQLite/ในหน่วยความจำเอง)

---

## 5. รันด้วย Docker (Full Stack)

### 5.1 รันเฉพาะบริการ dependencies (PostgreSQL + Redis + Admin Panels)

รันเฉพาะ database และ cache (เร็วกว่าการ build ทั้งระบบ):

```bash
make dependencies-up-silent
```

แล้วรัน API ในโหมด dev ด้วย `make dev`

### 5.2 รันทั้งระบบ

```bash
make start
```

เทียบเท่า `docker compose up -d --build --remove-orphans` แล้วตามด้วย `docker compose logs -f`
services ที่มีใน `docker-compose.yaml`:

| Service | Function |
| --- | --- |
| `api` | FastAPI backend (container: `erp-iot-api`, เปิด port `${APPLICATION_PORT}` → 8000) |
| `database` | PostgreSQL 17 Alpine (volume: `postgres_data`) |
| `cache` | Redis 8.6 Alpine (volume: `redis_data`) |
| `database-admin` | pgAdmin 9.2 (port `${PGADMIN_PORT}` → 80) |
| `cache-admin` | RedisInsight 3.4.2 (port `${REDISINSIGHT_PORT}` → 5540) |
| `frontend` | Django BFF (build จาก `./django-frontend`, port `${DJANGO_PORT}` → 8001) |

คำสั่งอื่น ๆ:

```bash
make start-silent      # รันแบบไม่ติดตาม log
make stop              # หยุด container (ไม่ลบข้อมูล)
make delete            # หยุด + ลบ container, network และ volumes ทั้งหมด (ลบข้อมูล!)
make logs              # ติดตาม log ทั้งระบบ
make view-processes    # ดู container ที่รันอยู่ (docker ps -a)
make dependencies-up   # up เฉพาะ dependencies แบบแสดง log
make dependencies-down # ลงเฉพาะ dependencies
```

---

## 6. Lint & Format

```bash
make lint       # uv run ruff check .          — ตรวจหาปัญหาโค้ด
make format     # uv run ruff format .         — จัดรูปแบบโค้ดอัตโนมัติ
```

---

## 7. สคริปต์ช่วยเหลือ (Helper scripts)

ใน `docs/scripts/` มีสคริปต์สำหรับงานที่พบบ่อย:

| Script | ใช้สำหรับ |
| --- | --- |
| `generate_secret.py` | สร้าง secret key แบบสุ่ม |
| `generate_fernet.py` | สร้าง Fernet key สำหรับ encryption |
| `create_module.py` | สร้างโครงสร้างโมดูลใหม่ตาม convention ของโปรเจกต์ |
| `directory_tree.py` | สร้าง tree ของโฟลเดอร์สำหรับเอกสาร |

---

## 8. FAQ / หมายเหตุ

- **ค่า default ของ port**: API dev = `8000`, API Docker = `${APPLICATION_PORT}`, pgAdmin = `${PGADMIN_PORT}`, RedisInsight = `${REDISINSIGHT_PORT}`, Django = `${DJANGO_PORT}`
- **การลบข้อมูลทั้งหมด**: `make delete` ลบ volumes ด้วย (ระวังใช้เมื่อต้องการ reset ฐานข้อมูลจริง ๆ เท่านั้น)
- **ENV_GENERATED ระวังเรื่อง environment**: ตัวแปร `APPLICATION_ENVIRONMENT` ต้องเป็นค่าใดค่าหนึ่งใน `dev` / `homolog` / `production` เท่านั้น ไม่งั้นแอปจะไม่ยอม start
- **ควรตั้งค่า `SECURITY_ADMIN_EMAIL` / `SECURITY_ADMIN_PASSWORD`** ก่อนรันครั้งแรกเพื่อให้มีบัญชีผู้ดูแลระบบ
  
# -------------------------------------------
# -------------------------------------------
# -------------------------------------------
# -------------------------------------------

`make` isn’t recognized because it isn’t installed on Windows by default — you have to add it yourself. Since your earlier `choco install make` attempts all failed with “Access denied” (because you weren’t running as Administrator), here are the reliable ways to fix it, ordered from easiest to most manual.

---

## ✅ Option 1 — Scoop (no admin rights needed)

This is the best path for you. Scoop installs everything into your user folder.

In a **normal** PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
irm get.scoop.sh | iex
scoop install make
```

Then **close and reopen** the terminal and verify:

```powershell
make --version
```

If Scoop complains about `git`, install it first with `scoop install git`, then install `make`.

---

## ✅ Option 2 — Chocolatey (must run as Administrator)

Your log shows every Chocolatey attempt failed because you weren’t elevated. If you want to use Chocolatey, you **must** open PowerShell as Administrator first.

1. Press **Win** → type `PowerShell` → right‑click → **Run as administrator**
2. In that elevated window:

```powershell
choco install make -y
```

3. **Close and reopen** your normal terminal, then test `make --version`.

You can also clean up the stale lock file that kept blocking you:

```powershell
# Still in the admin window
Remove-Item "C:\ProgramData\chocolatey\lib\995c915eb7cf3c8b25f2235e513ef8ca0c75c3e7" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ProgramData\chocolatey\lib-bad" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## ✅ Option 3 — Manual install (no package manager required)

1. Download the **“Complete package, except sources”** from the [GnuWin32 Make for Windows page](https://gnuwin32.sourceforge.net/packages/make.htm).
2. Install it (default location is `C:\Program Files (x86)\GnuWin32\bin`).
3. Add that folder to your **PATH**:
   - Press **Win** → search “Environment Variables” → edit **Path** for your user → add `C:\Program Files (x86)\GnuWin32\bin`
4. **Close and reopen** the terminal, then run `make --version`.

You can also add the path directly in PowerShell:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","User") + ";C:\Program Files (x86)\GnuWin32\bin",
  "User"
)
```

---

## ✅ Option 4 — Use WSL (Windows Subsystem for Linux)

If you have WSL installed, open the Linux terminal (Ubuntu, etc.) and run:

```bash
sudo apt update && sudo apt install make
```

Then **run your project from inside WSL**, not from PowerShell. This gives you the most Linux‑like experience.

---

## ✅ Option 5 — Skip `make` entirely

You don’t actually need `make` to run a FastAPI project. Open the `Makefile` to see what `make dev` does:

```powershell
notepad .\Makefile
```

Find the `dev:` line. It typically looks like:

```makefile
dev:
	pip install -r requirements.txt
	pip install -e .
	uvicorn src.main:app --reload
```

Then run those commands manually:

```powershell
pip install -r requirements.txt
pip install -e .
uvicorn src.main:app --reload
```

---

## Verify the install before running `make dev`

Always test in a **fresh** terminal:

```powershell
Get-Command make        # should print a path
make --version          # should print "GNU Make 4.x"
```

If `Get-Command make` still says “not recognized”, the install didn’t reach your PATH — go back and confirm you used the correct terminal type (admin for Chocolatey, normal for Scoop) and that you reopened the terminal.

---

## Summary

| Method | Admin needed? | Command |
|---|---|---|
| **Scoop** | No | `scoop install make` |
| Chocolatey | **Yes** | `choco install make` |
| Manual (GnuWin32) | No (but need to edit PATH) | Download + add to PATH |
| WSL | No (inside WSL) | `sudo apt install make` |
| No `make` at all | – | Run Makefile commands manually |

**For your situation, Option 1 (Scoop) is the quickest and avoids the admin‑rights problem that broke every previous attempt.**

# 1) ปัก Python เป็น 3.13
```bash
uv python pin 3.13
```

# 2) ลบ venv เก่า
```bash
Remove-Item -Recurse -Force .venv
```

# 3) sync ใหม่
```bash
uv sync
```

# 4) ลอง migrate
```bash
make migrate
make dev
```




```bash

uv python pin 3.13
Remove-Item -Recurse -Force .venv
uv sync
make migrate
make dev

```
#  ---
```bash
Remove-Item -Recurse -Force .venv
make lint       # uv run ruff check .          — ตรวจหาปัญหาโค้ด
make format     # uv run ruff format .         — จัดรูปแบบโค้ดอัตโนมัติ
uv sync
make migrate
make dev
```

#  opencode ---

```bash

    opencode --continue

```
คู่มือการใช้งาน OpenCode ผ่าน Windows Terminal (PowerShell / Command Prompt) เพื่อกู้คืนและทำงานเก่าต่ออย่างละเอียด พร้อมตัวอย่างการใช้งานจริงครับ
------------------------------
## คู่มือการใช้งาน OpenCode AI ผ่าน Windows Terminal
เมื่อคุณใช้งาน OpenCode บน Windows ไฟล์ประวัติการแชท (Chat History) และบริบทของโค้ดจะถูกผูกไว้กับ โฟลเดอร์โปรเจกต์ ที่คุณสั่งรันคำสั่ง ดังนั้นการจะกลับมาทำงานเดิมต่อ สิ่งสำคัญที่สุดคือต้อง เปิด Terminal ให้ถูกโฟลเดอร์ ครับ
## ขั้นตอนที่ 1: การเข้าสู่โฟลเดอร์งานเดิม (สำคัญที่สุด)
ก่อนจะพิมพ์คำสั่ง OpenCode คุณต้องย้าย Terminal ไปยังโฟลเดอร์ที่คุณเคยทำโปรเจกต์นั้นไว้

   1. เปิด PowerShell หรือ Command Prompt (cmd) ขึ้นมา
   2. ใช้คำสั่ง cd ตามด้วยพาธ (Path) ของโฟลเดอร์งานของคุณ
   * ตัวอย่าง: หากโปรเจกต์ของคุณอยู่ที่โฟลเดอร์ D:\my-website ให้พิมพ์ดังนี้:
      
      cd D:\my-website
      
      * เคล็ดลับ Windows: คุณสามารถเข้าไปในโฟลเดอร์งานผ่าน File Explorer จากนั้นคลิกที่แถบที่อยู่ด้านบน พิมพ์ cmd หรือ powershell แล้วกด Enter ระบบจะเปิด Terminal ในโฟลเดอร์นั้นให้ทันที
   
------------------------------
## ขั้นตอนที่ 2: คำสั่งสำหรับกู้คืนและทำต่อจากงานเดิม
เมื่ออยู่ในโฟลเดอร์ที่ถูกต้องแล้ว ให้เลือกใช้คำสั่งตามสถานการณ์ของคุณดังนี้ครับ:
## 1. ทำงานต่อจากเซสชันล่าสุดทันที (--continue)
หากคุณเพิ่งปิด Terminal ไปไม่นาน และอยากจะพิมพ์คุยต่อจากประโยคล่าสุดที่คุยค้างไว้

* คำสั่ง:

opencode --continue

(หรือใช้ตัวย่อ: opencode -c)
* ตัวอย่างการทำงาน: ระบบจะโหลดประวัติการคุยครั้งล่าสุดขึ้นมา และคุณสามารถพิมพ์สั่งงานต่อได้ทันที เช่น:

"ช่วยเขียนฟังก์ชันปุ่มส่งข้อมูล (Submit Button) ต่อจากที่คุยไว้คราวก่อนให้หน่อย"


## 2. ดูประวัติและเลือกเซสชันเก่ามาทำต่อ (--history)
หากคุณเคยคุยไว้หลายเรื่อง หรืออยากย้อนกลับไปทำโปรเจกต์ของเมื่อวันก่อน

* คำสั่ง:

opencode --history

(หรือใช้ตัวย่อ: opencode -h)
* ตัวอย่างการทำงาน: หน้าจอ Terminal จะแสดงรายการเซสชันเก่าทั้งหมด เช่น:

[1] 2026-09-20 10:30 - แก้ไขบั๊กหน้า Login
[2] 2026-09-19 14:15 - ออกแบบฐานข้อมูล User
[3] 2026-09-15 09:00 - เริ่มต้นสร้างโครงสร้างเว็บ

กรุณาเลือกหมายเลขเซสชันที่ต้องการทำต่อ (1-3): _

ให้คุณพิมพ์ตัวเลข (เช่น 1) แล้วกด Enter ระบบจะดึงเอาบริบทของเซสชันนั้นกลับมาทำงานต่อทันที

------------------------------
## ตัวอย่างสถานการณ์จริง (Use Case Example)
สมมติว่าเมื่อวานคุณให้ OpenCode ช่วยเขียนโค้ดหน้าสัมผัส (Contact Page) ค้างไว้ วันนี้คุณต้องการมาทำต่อ:

   1. เปิด Terminal ไปที่โฟลเดอร์งานของคุณ
   2. พิมพ์คำสั่งเพื่อทำต่อ:
   
   opencode -c
   
   3. ระบบจะตอบรับ: โหลดบริบทเดิมสำเร็จ คุณสามารถพิมพ์สั่งการต่อใน Terminal ได้ทันที เช่น:
   
   คุณ: เพิ่มฟิลด์ "เบอร์โทรศัพท์" ลงในฟอร์มติดต่อที่ทำไว้เมื่อวานนี้หน่อย และช่วยตรวจสอบ (Validate) ให้กรอกได้เฉพาะตัวเลข 10 หลักด้วย
   
   OpenCode AI: กำลังดำเนินการแก้ไขไฟล์ contact.html และ contact.js ให้ครับ... (ระบบจะเริ่มเขียนโค้ดต่อให้ทันที)
   
   
------------------------------
## วิธีตรวจสอบและแก้ไขหากเกิดปัญหาบน Windows

* เจอปัญหาคำสั่ง opencode หาย (Command not found): อาจเกิดจากเครื่องมองไม่เห็นตัวแปรสภาพแวดล้อม (Environment Path) ให้ลองรัน Terminal ในโหมดผู้ดูแลระบบ (Run as Administrator)
* หาเซสชันเก่าไม่เจอ: ตรวจสอบให้มั่นใจว่าคุณไม่ได้ย้ายโฟลเดอร์งานไปที่อื่น หรือเปลี่ยนชื่อโฟลเดอร์ เพราะ OpenCode จะจำประวัติแยกตามโฟลเดอร์นั้น ๆ
 