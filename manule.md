# คู่มือการรัน FastAPI Clean Architecture DDD Template (ภาษาไทย)

## 1. ติดตั้ง uv (Package Manager)
```bash
pip install uv
```

## 2. ตั้งค่า Environment Variables
```bash
cp .env.example .env
# แก้ไขไฟล์ .env ใส่ค่า configuration ที่ต้องการ
```

## 3. ติดตั้ง Dependencies
```bash
uv sync
```

## 4. รันแอปพลิเคชัน

### วิธีที่ 1: ใช้ uvicorn โดยตรง
```bash
uv run -- uvicorn app.app:app --reload
```

### วิธีที่ 2: ใช้ FastAPI CLI
```bash
uv run -- python -m fastapi app.app:app --reload
```

### วิธีที่ 3: ใช้ Docker Compose
```bash
docker-compose up --build
```

### วิธีที่ 4: รัน DB ด้วย Docker Compose โดยตรง
```bash
# รัน app + DB
docker-compose up --build

# รันแบบ background
docker-compose up -d

# หยุดและลบ containers
docker-compose down -v

# รันเฉพาะ DB
docker-compose up -d postgres adminer
```

## 5. เข้าถึง API
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 6. Database Migrations (Alembic)
```bash
# สร้าง migration ใหม่
alembic revision --autogenerate -m "คำอธิบายการเปลี่ยนแปลง"

# อัปเดต DB
alembic upgrade head

# ย้อนกลับ 1 เวอร์ชัน
alembic downgrade -1
```

## 7. รัน Tests
```bash
uv run -- pytest -q
```

## 8. Lint โค้ด (Ruff)
```bash
uv run -- ruff .
```

---

**หมายเหตุ:** ต้องมี Python 3.13+ ติดตั้งอยู่ในระบบ (ดูในไฟล์ `.python-version`)
