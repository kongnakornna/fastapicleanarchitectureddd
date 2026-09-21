# FastAPI Backend Scaffold

Scaffold generator for FastAPI + Clean Architecture + DDD.

## ไฟล์ในโฟลเดอร์นี้

- `scaffold.bat` — Windows launcher
- `scaffold.ps1` — PowerShell driver (ทำงานจริง)
- `README.md` — ไฟล์นี้

## วิธีใช้

```bat
REM 1. สร้าง base + health + example
scaffold.bat

REM 2. ดู modules ทั้งหมด
scaffold.bat --list

REM 3. สร้างทั้ง 65 modules
scaffold.bat --all

REM 4. สร้างเฉพาะ module
scaffold.bat --module forecast

REM 5. สร้างทั้ง Layer 5
scaffold.bat --layer 5

REM 6. Dry-run (ดูว่าจะสร้างอะไร)
scaffold.bat --all --dry-run

REM 7. Force overwrite
scaffold.bat --all --force

REM 8. Setup venv + pip
scaffold.bat --setup

REM 9. Run dev server
scaffold.bat --run

REM 10. Validate scaffold
scaffold.bat --validate

REM 11. Clean
scaffold.bat --clean