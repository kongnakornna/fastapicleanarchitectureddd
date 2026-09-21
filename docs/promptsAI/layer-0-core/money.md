## 📄 Module 0.1: `money`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `money` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `Money` (VO), `Currency` (enum), `VAT` (VO), `ExchangeRate` (VO) |
| **Prefix** | `mny` |
| **Tables** | ไม่มี (pure VO) |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `money`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- Module นี้เป็น **primitive module** — ไม่มี persistence, ไม่มี cache
- ใช้ `Decimal` เท่านั้น (ห้ามใช้ `float`)
- Money is Domain Invariant — ต้องแม่นยำ 100%

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`** — ไม่มี (pure VO module)

**`domain/value_objects.py` — Money**
```python
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""
    amount: Decimal
    currency: str = "THB"

    def __post_init__(self):
        object.__setattr__(self, "amount",
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("Amount must be Decimal")
        if self.currency not in Currency._value2member_map_:
            raise DomainError(f"Unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(f"Cannot operate on {self.currency} vs {other.currency}")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            raise DomainError("Factor must be Decimal")
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")
```

**`domain/value_objects.py` — VAT**
```python
@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุภาษีมูลค่าเพิ่ม"""
    rate: Decimal

    def calculate(self, base: Money) -> Money:
        return Money((base.amount * self.rate).quantize(Decimal("0.01")), base.currency)

    def extract(self, total: Money) -> Money:
        base = (total.amount / (Decimal("1") + self.rate)).quantize(Decimal("0.01"))
        return Money(total.amount - base, total.currency)
```

**`domain/value_objects.py` — ExchangeRate**
```python
@dataclass(frozen=True)
class ExchangeRate:
    """Exchange rate VO — วัตถุอัตราแลกเปลี่ยน"""
    from_currency: str
    to_currency: str
    rate: Decimal
    as_of: datetime

    def __post_init__(self):
        if self.rate <= 0:
            raise DomainError("Exchange rate must be positive")

    def convert(self, amount: Money) -> Money:
        if amount.currency != self.from_currency:
            raise DomainError("Currency mismatch")
        return Money(amount.amount * self.rate, self.to_currency)
```

**`domain/enums.py`**
```python
from enum import Enum

class Currency(str, Enum):
    THB = "THB"
    USD = "USD"
    EUR = "EUR"

class VATRate(str, Enum):
    ZERO = "0.00"
    SEVEN = "0.07"

class RoundingMode(str, Enum):
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    BANKERS = "BANKERS"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`** — Protocol ว่าง (VO module ไม่มี external deps)

**`application/use_cases.py`**
```python
class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""

    def add(self, a: Money, b: Money) -> Money: return a + b
    def subtract(self, a: Money, b: Money) -> Money: return a - b
    def multiply(self, a: Money, factor: Decimal) -> Money: return a * factor
    def calculate_vat(self, base: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).calculate(base)
    def extract_vat(self, total: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).extract(total)
    def convert(self, amount: Money, rate: ExchangeRate) -> Money:
        return rate.convert(amount)
    def sum_all(self, items: list[Money]) -> Money:
        if not items:
            raise DomainError("Cannot sum empty list")
        result = items[0]
        for item in items[1:]:
            result = result + item
        return result
```

**`application/mappers.py`** — `MoneyMapper.to_schema()` / `to_entity()`
**`application/exceptions.py`** — `MoneyException(StandardException)`
**`application/utils.py`** — `round_money()`, `zero_money(currency)`

### 3. Infrastructure Layer (`infrastructure/`)
- **ไม่มี** `models.py` (pure VO)
- **ไม่มี** `repositories.py`
- **ไม่มี** `caches.py`
- **ไม่มี** `services.py`

### 4. Presentation Layer (`presentation/`)

**`presentation/schemas.py`**
```python
class MoneySchema(BaseModel):
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    model_config = ConfigDict(from_attributes=True)

class VATRequest(BaseModel):
    base: MoneySchema
    rate: VATRate = VATRate.SEVEN

class VATResponse(BaseModel):
    vat: MoneySchema
    total: MoneySchema
```

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/money", tags=["Money"])

@router.post("/add/")
async def add(a: MoneySchema, b: MoneySchema): ...

@router.post("/subtract/")
async def subtract(a: MoneySchema, b: MoneySchema): ...

@router.post("/vat/calculate/")
async def vat_calculate(req: VATRequest): ...

@router.post("/vat/extract/")
async def vat_extract(req: VATRequest): ...

@router.post("/convert/")
async def convert(amount: MoneySchema, rate: ExchangeRateSchema): ...
```

**`presentation/docs.py`** — `router_docs` + per-endpoint docs
**`presentation/dependencies.py`** — `get_money_use_cases()`

### 5. Error Handling
- Use cases: **3-branch** (`StandardException` → `DomainError` → `Exception`)
- ไม่มี repository/cache → ไม่มี 2-branch / never-raise

### 6. Invariants
- `Decimal` quantize 2 ตำแหน่ง (ROUND_HALF_UP)
- `a + b == b + a` (commutative)
- `(a + b) + c == a + (b + c)` (associative)
- `a + Money(0) == a` (identity)
- `a - a == Money(0)` (inverse)
- `VAT.calculate(base) + base == VAT.extract(total)` consistency

### 7. Domain Events
- `MoneyAdded`, `MoneySubtracted`, `VATCalculated`, `CurrencyConverted`

### 8. Tests
```python
def test_commutative(): assert a + b == b + a
def test_associative(): assert (a+b)+c == a+(b+c)
def test_identity(): assert a + Money(Decimal("0")) == a
def test_currency_mismatch(): pytest.raises(DomainError)
def test_vat_7_percent(): assert VAT(Decimal("0.07")).calculate(Money(Decimal("100"))) == Money(Decimal("7.00"))
def test_vat_extract_roundtrip(): ...
def test_exchange_rate_convert(): ...
def test_negative_money(): assert Money(Decimal("-10")).is_negative()
def test_zero_money(): assert Money(Decimal("0")).is_zero()
```

## Output
- ไฟล์ ~8 ไฟล์ (module เล็ก)
- Comment 2 ภาษา (ไทย + English)
- พร้อมรันด้วย `uvicorn app.app:app --reload`
```

---
