### 📄 Module 7.2: `example` (Reference Implementation)

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `example` |
| **Layer** | `7` (Templates) |
| **Priority** | 🟢 |
| **Phase** | 1 |
| **Dependencies** | `audit`, `events` |
| **Domain Concepts** | `ExampleEntity` (entity), `ExampleStatus` (enum) |
| **Prefix** | `ex` |
| **Tables** | `tenant_ex.examples` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `example`

## บริบท
- Module ตัวอย่างสำหรับ developer ใหม่
- แสดง pattern ครบทุก layer: Domain → Application → Infrastructure → Presentation
- ใช้เป็น blueprint สำหรับสร้าง module ใหม่
- CRUD + idempotency + audit + events + tests

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — ExampleEntity**
```python
@dataclass
class ExampleEntity(BaseEntity):
    """Example entity — เอนทิตีตัวอย่าง"""
    code: str = ""
    name: str = ""
    description: str = ""
    status: str = "ACTIVE"
    amount: Decimal = Decimal("0.00")

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.code or not re.match(r"^[A-Z][A-Z0-9-]{2,20}$", self.code):
            raise DomainError(f"Invalid code: {self.code}")
        if not self.name:
            raise DomainError("Name required")
        if self.amount < 0:
            raise DomainError("Amount cannot be negative")

    def activate(self) -> None:
        self.status = "ACTIVE"

    def deactivate(self) -> None:
        self.status = "INACTIVE"
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ExampleCode:
    """Example code VO — วัตถุรหัส"""
    value: str
    PATTERN = r"^[A-Z][A-Z0-9-]{2,20}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid code: {self.value}")
```

**`domain/enums.py`**
```python
class ExampleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
```

### 2-4. Application / Infrastructure / Presentation

> **ดู pattern จาก `tenancy` module** — ทุก layer ใช้ pattern เดียวกัน
> - Application: `interfaces.py`, `use_cases.py`, `mappers.py`, `exceptions.py`, `utils.py`
> - Infrastructure: `models.py`, `repositories.py`, `caches.py`, `services.py`
> - Presentation: `routers.py`, `schemas.py`, `docs.py`, `dependencies.py`

### 5-7. Invariants / Events / Tests

- Invariants: `code` format, `amount >= 0`
- Events: `ExampleCreated`, `ExampleUpdated`, `ExampleDeleted`
- Tests: unit + integration + property + manual

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---
