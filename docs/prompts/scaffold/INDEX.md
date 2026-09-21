# 📚 Scaffold Runner Index

## 🎯 Quick Commands

| Batch | What it does |
|---|---|
| `run-all.bat` | รันทุก layer (65 modules) |
| `run-layer-0.bat` | Core (6 modules) |
| `run-layer-1.bat` | Foundation (8 modules) |
| `run-layer-2.bat` | Money Path (7 modules) |
| `run-layer-3.bat` | Goods Path (13 modules) |
| `run-layer-4.bat` | Operations (13 modules) |
| `run-layer-5.bat` | Intelligence (7 modules) |
| `run-layer-6.bat` | Monitoring (8 modules) |
| `run-layer-7.bat` | Templates (3 modules) |
| `run-single.bat <name>` | รัน module เดียว |
| `modules\<name>.bat` | รัน module นั้น |
| `setup.bat` | venv + pip install |
| `run-server.bat` | uvicorn dev server |
| `clean.bat` | ลบทั้งหมด |
| `list.bat` | ดูรายการ modules |

## 🚀 Workflow แนะนำ

```bat
REM 1. สร้าง base + ทั้งหมด
run-all.bat

REM 2. Setup dependencies
setup.bat

REM 3. รัน server
run-server.bat
REM → http://localhost:8000/docs