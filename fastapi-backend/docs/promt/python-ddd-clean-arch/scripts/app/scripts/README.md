# Scripts

> Scaffolder สำหรับ module DDD + Clean Arch

## Platform

| Script | Platform |
|---|---|
| `create_modules.bat` | Windows (cmd.exe) |
| `create_module.ps1` | Windows (PowerShell) |
| `new_module.sh` | Linux / macOS / WSL / Git Bash |

## Commands

| Command | คำอธิบาย |
|---|---|
| `new` | สร้าง module ใหม่ (เลือก flag ได้) |
| `all` | สร้างทุกส่วนพร้อมกัน |
| `sql` | สร้างเฉพาะ migration 3 ไฟล์ |
| `routes` | พิมพ์ hint สำหรับ register router |
| `test` | สร้างเฉพาะ test files |
| `docs` | สร้างเฉพาะ docs |
| `help` | ดูวิธีใช้ |

## Flags

| Flag | ผล |
|---|---|
| `--sql` | สร้าง `V001/V002/V003` |
| `--tests` | สร้าง 5 test files |
| `--docs` | สร้าง `README_{m}.md` + `API_{m}.md` |
| `--routes` | พิมพ์ hint (ไม่แก้ไฟล์จริง) |
| `--force` | เขียนทับของเดิม |

## ตัวอย่าง

```bash
# Linux / macOS
./scripts/new_module.sh new inventory 3 inv --sql --tests --docs --routes
./scripts/new_module.sh all sales 4 sal
./scripts/new_module.sh sql invoice inv

# Windows (cmd)
scripts\create_modules.bat new inventory 3 inv --sql --tests --docs --routes