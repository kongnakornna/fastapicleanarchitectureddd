# คู่มือ FastAPI Clean Architecture & DDD

---

## 1. โครงสร้าง Project

```text
fastapi-clean-architecture-ddd-template/
│
├── .env                    # Environment variables (ไม่ commit)
├── .env.example            # ตัวอย่าง .env
├── .python-version         # เวอร์ชัน Python
├── pyproject.toml          # กำหนด dependencies
├── uv.lock                 # Lock file (ห้ามแก้เอง)
├── requirements.txt        # Dependencies สำรอง
├── Makefile                # คำสั่งลัด
├── Dockerfile              # สำหรับ Docker
├── docker-compose.yaml     # กำหนด services
│
├── app/                    # โค้ดหลัก
│   ├── __init__.py
│   ├── app.py              # Entry point (FastAPI instance)
│   │
│   ├── core/               # การตั้งค่าหลัก
│   │   ├── database.py         # DB connection (SQLAlchemy async)
│   │   ├── exception_handler.py # จัดการ errors
│   │   ├── logging.py          # ตั้งค่า log (loguru)
│   │   ├── middleware.py       # Middleware (CORS, etc.)
│   │   ├── resources.py       # Constants/resources
│   │   ├── security.py        # JWT, password hashing
│   │   ├── settings.py        # Config (pydantic-settings)
│   │   └── utils.py           # Functions ช่วยงาน
│   │
│   └── modules/            # Feature modules
│       └── example/        # ตัวอย่าง module
│           ├── domain/         # กฎธุรกิจล้วน
│           │   ├── entities.py
│           │   ├── value_objects.py
│           │   ├── services.py
│           │   └── mappers.py
│           │
│           ├── application/    # Use cases, interfaces
│           │   ├── use_cases.py
│           │   ├── interfaces.py
│           │   └── utils.py
│           │
│           ├── infrastructure/ # Implement DB, external
│           │   ├── models.py
│           │   └── repositories.py
│           │
│           └── presentation/   # API endpoints
│               ├── routers.py
│               ├── schemas.py
│               ├── dependencies.py
│               └── exceptions.py
│
├── test/                   # ทดสอบ
│   ├── core/
│   └── modules/
│       └── example/
│
├── docs/                   # เอกสาร
└── scripts/                # สคริปต์ช่วยงาน
```

### แผนผังชั้น (Layers)

```
┌─────────────────────────────────────┐
│         Presentation Layer          │  ← FastAPI routers, schemas
├─────────────────────────────────────┤
│         Application Layer           │  ← Use cases, interfaces
├─────────────────────────────────────┤
│           Domain Layer              │  ← Entities, business rules
├─────────────────────────────────────┤
│        Infrastructure Layer         │  ← DB, external API, ORM
└─────────────────────────────────────┘
```

**กฎ:** ชั้นในสุด (Domain) ห้าม import จากชั้นนอก

---

## 2. การติดตั้ง

### 2.1 ติดตั้ง uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.1.1 ติดตั้ง Python

```bash
# ติดตั้ง Python ผ่าน uv
uv python install 3.13
```

### 2.2 Clone โปรเจค

```bash
git clone <repo-url>
cd fastapi-clean-architecture-ddd-template
```

### 2.3 ตั้งค่า Environment Variables

```bash
# คัดลอกไฟล์ตัวอย่าง
cp .env.example .env
```

แก้ไข `.env`:
```env
APP_NAME="FastAPI Clean Architecture DDD Template"
DEBUG=true
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"
SECRET_KEY=your-secret-key-here
```

### 2.4 ติดตั้ง Dependencies

```bash
# ติดตั้ง dependencies ทั้งหมด
uv sync

# ติดตั้ง dev dependencies เพิ่ม
uv sync --group dev
```

### 2.5 ตรวจสอบการติดตั้ง

```bash
# ดูเวอร์ชัน Python
uv run python -V

# ทดสอบ import FastAPI
uv run python -c "import fastapi; print(fastapi.__version__)"
```

---

## 3. การ Run

### 3.1 รันแบบ Local

```bash
# ใช้ uvicorn (แนะนำสำหรับ development)
uv run -- uvicorn app.app:app --reload

# หรือใช้ FastAPI CLI
uv run -- python -m fastapi app.app:app --reload
```

เปิด browser: `http://localhost:8000/docs` (Swagger UI)

### 3.2 รันแบบ Docker

```bash
# Build และ run
docker-compose up --build

# รันแบบ background
docker-compose up -d
```

### 3.3 ใช้ Makefile

```bash
# เริ่มแอปพลิเคชัน
make start

# เริ่มแบบ background
make start-silent

# ดู containers ที่รันอยู่
make view-processes

# หยุดและลบ containers
make delete

# เริ่มแค่ database
make dependencies-up

# หยุด database
make dependencies-down
```

### 3.4 คำสั่ง uv ที่ใช้บ่อย

```bash
# รัน Python script
uv run python script.py

# รัน pytest
uv run -- pytest

# เพิ่ม dependency
uv add <package>

# ลบ dependency
uv remove <package>

# อัปเดต dependencies
uv sync
```

---

## 4. การพัฒนา

### 4.1 สร้าง Module ใหม่

สร้างโฟลเดอร์ตามโครงสร้าง:

```bash
mkdir -p app/modules/{module_name}/{domain,application,infrastructure,presentation}
touch app/modules/{module_name}/{domain,application,infrastructure,presentation}/__init__.py
```

### 4.2 Domain Layer

```python
# app/modules/product/domain/entities.py

from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    price: float
    description: str = ""

    def is_valid(self) -> bool:
        return self.price > 0
```

```python
# app/modules/product/domain/value_objects.py

from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "THB"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
```

### 4.3 Application Layer

```python
# app/modules/product/application/interfaces.py

from abc import ABC, abstractmethod
from ..domain.entities import Product

class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: str) -> Product | None:
        pass

    @abstractmethod
    async def save(self, product: Product) -> Product:
        pass
```

```python
# app/modules/product/application/use_cases.py

from ..domain.entities import Product
from .interfaces import ProductRepositoryInterface

class CreateProductUseCase:
    def __init__(self, repository: ProductRepositoryInterface):
        self.repository = repository

    async def execute(self, name: str, price: float, description: str = "") -> Product:
        product = Product(
            id=str(uuid4()),
            name=name,
            price=price,
            description=description
        )
        return await self.repository.save(product)
```

### 4.4 Infrastructure Layer

```python
# app/modules/product/infrastructure/repositories.py

from sqlalchemy.ext.asyncio import AsyncSession
from ..application.interfaces import ProductRepositoryInterface
from ..domain.entities import Product
from .models import ProductModel

class ProductRepository(ProductRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: str) -> Product | None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalars().first()
        return model.to_entity() if model else None

    async def save(self, product: Product) -> Product:
        model = ProductModel.from_entity(product)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()
```

### 4.5 Presentation Layer

```python
# app/modules/product/presentation/routers.py

from fastapi import APIRouter, Depends
from .schemas import ProductCreate, ProductResponse
from ..application.use_cases import CreateProductUseCase
from ..application.interfaces import ProductRepositoryInterface

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    use_case: CreateProductUseCase = Depends()
):
    return await use_case.execute(
        name=data.name,
        price=data.price,
        description=data.description
    )
```

```python
# app/modules/product/presentation/schemas.py

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str = ""

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    description: str
```

### 4.6 ลงทะเบียน Router ใน app.py

```python
# app/app.py

from fastapi import FastAPI
from app.modules.product.presentation.routers import router as product_router

app = FastAPI(title="My API", version="1.0.0")

app.include_router(product_router, prefix="/api/v1")
```

### 4.7 Database Migrations

```bash
# สร้าง migration ใหม่
alembic revision --autogenerate -m "add product table"

# อัปเดต database
alembic upgrade head

# ย้อนกลับ 1 เวอร์ชัน
alembic downgrade -1

# ดูสถานะ migration
alembic current
```

### 4.8 การทดสอบ

```bash
# รัน tests ทั้งหมด
uv run -- pytest

# รัน tests ในโฟลเดอร์ specific
uv run -- pytest test/modules/product/

# รัน tests ที่มี keyword
uv run -- pytest -k "test_create_product"

# ดู coverage
uv run -- pytest --cov=app
```

### 4.9 Code Quality

```bash
# ตรวจ lint
uv run -- ruff check .

# แก้ไข auto-fix
uv run -- ruff check --fix .

# ตรวจ formatting
uv run -- ruff format .

# ตรวจ type hints (ถ้ามี mypy)
uv run -- mypy app/
```

---

## สรุปคำสั่งที่ใช้บ่อย

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `uv sync` | ติดตั้ง dependencies |
| `uv run -- uvicorn app.app:app --reload` | รันแอป |
| `uv run -- pytest` | รัน tests |
| `uv add <package>` | เพิ่ม package |
| `uv remove <package>` | ลบ package |
| `alembic revision --autogenerate -m "msg"` | สร้าง migration |
| `alembic upgrade head` | อัปเดต DB |
| `uv run -- ruff check .` | ตรวจ lint |

---
 
