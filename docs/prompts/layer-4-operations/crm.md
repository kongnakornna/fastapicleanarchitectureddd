### 🎯 ตัวอย่างเต็ม: Module `crm`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `crm` |
| **Layer** | `4` (Operations) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **Dependencies** | `customer`, `line_channel`, `notification`, `campaign`, `invoice`, `audit` |
| **Domain Concepts** | `Lead` (entity), `Deal` (entity), `Pipeline` (VO), `Activity` (VO) |
| **Prefix** | `crm` |
| **Tables** | `tenant_crm.leads`, `tenant_crm.deals`, `tenant_crm.activities` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `crm`

## บริบท
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- มิติ: 📞 CRM (Lead → Customer → Loyalty → Satisfaction)
- **Invariants:** `Deal value >= 0`, `Pipeline stage forward-only`
- **Events:** `LeadCreated`, `LeadConverted`, `DealCreated`, `DealWon`, `DealLost`

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Lead**
```python
@dataclass
class Lead(BaseEntity):
    """Lead entity — เอนทิตีลีด"""
    name: str = ""
    contact: str = ""
    source: str = ""
    status: str = "NEW"
    assigned_to: str = ""
    email: str = ""
    phone: str = ""
    notes: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.name:
            raise DomainError("Lead name is required")

    def convert(self, customer_data: dict) -> "Customer":
        """Convert lead to customer — เปลี่ยนลีดเป็นลูกค้า"""
        if self.status == "CONVERTED":
            raise DomainError("Lead already converted")
        if self.status == "LOST":
            raise DomainError("Cannot convert lost lead")
        self.status = "CONVERTED"
        return Customer(**customer_data)

    def mark_lost(self, reason: str) -> None:
        if self.status in ("CONVERTED", "LOST"):
            raise DomainError(f"Cannot mark {self.status} lead as lost")
        self.status = "LOST"

    def assign(self, user_id: str) -> None:
        self.assigned_to = user_id
```

**`domain/entities.py` — Deal**
```python
@dataclass
class Deal(BaseEntity):
    """Deal entity — เอนทิตีดีล"""
    title: str = ""
    customer_id: str = ""
    lead_id: str | None = None
    value: Decimal = Decimal("0.00")
    currency: str = "THB"
    stage: str = "PROSPECTING"
    probability: int = 0
    expected_close: date | None = None
    owner_id: str = ""
    notes: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.title:
            raise DomainError("Deal title required")
        if self.value < 0:
            raise DomainError("Deal value cannot be negative")
        if not 0 <= self.probability <= 100:
            raise DomainError("Probability must be 0-100")

    def advance_stage(self, new_stage: str) -> None:
        """Advance deal stage (forward only) — เลื่อนขั้นดีล"""
        stages = ["PROSPECTING", "QUALIFICATION", "PROPOSAL", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"]
        if new_stage not in stages:
            raise DomainError(f"Invalid stage: {new_stage}")
        if self.stage in ("CLOSED_WON", "CLOSED_LOST"):
            raise DomainError(f"Cannot change closed deal: {self.stage}")
        current_idx = stages.index(self.stage)
        new_idx = stages.index(new_stage)
        if new_idx <= current_idx:
            raise DomainError(f"Cannot move backward: {self.stage} → {new_stage}")
        self.stage = new_stage

    def win(self) -> None:
        self.advance_stage("CLOSED_WON")
        self.probability = 100

    def lose(self, reason: str) -> None:
        self.advance_stage("CLOSED_LOST")
        self.probability = 0

    def is_open(self) -> bool:
        return self.stage not in ("CLOSED_WON", "CLOSED_LOST")

    @property
    def weighted_value(self) -> Decimal:
        return (self.value * Decimal(self.probability) / Decimal("100")).quantize(Decimal("0.01"))
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Pipeline:
    """Pipeline VO — วัตถุไปป์ไลน์"""
    stages: tuple[str, ...] = (
        "PROSPECTING", "QUALIFICATION", "PROPOSAL", "NEGOTIATION",
        "CLOSED_WON", "CLOSED_LOST",
    )

    def is_valid_stage(self, stage: str) -> bool:
        return stage in self.stages

@dataclass(frozen=True)
class Activity:
    """Activity VO — วัตถุกิจกรรม"""
    activity_type: str  # CALL, EMAIL, MEETING, LINE, NOTE
    subject: str
    description: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.activity_type not in ("CALL", "EMAIL", "MEETING", "LINE", "NOTE"):
            raise DomainError(f"Invalid activity type: {self.activity_type}")
```

**`domain/enums.py`**
```python
class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"

class DealStage(str, Enum):
    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"

class ActivityType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    LINE = "LINE"
    NOTE = "NOTE"
```

### 2. Application Layer (`application/`)

**`application/use_cases.py`**
```python
class CRMUseCases:
    """CRM use cases — กรณีการใช้งาน CRM"""

    def __init__(self, lead_repo, deal_repo, activity_repo, customer_repo,
                 cache, idempotency, audit, events):
        ...

    async def create_lead(self, payload: dict, idem_key: str) -> Lead:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            lead = Lead(**payload)
            lead = await self.lead_repo.save(lead)

            # Read-back
            verified = await self.lead_repo.get_by_id(lead.id)
            if not verified or verified.name != lead.name:
                raise CRMException("Read-back failed")

            await self.audit.log("lead.created", lead.id)
            await self.idempotency.set(idem_key, lead)
            await self.events.publish("LeadCreated", lead)
            return lead
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_lead")
            raise CRMException()

    async def convert_lead(self, id: str, customer_data: dict) -> "Customer":
        try:
            lead = await self.lead_repo.get_by_id(id)
            if not lead:
                raise LeadNotFoundException()

            customer = lead.convert(customer_data)
            customer = await self.customer_repo.save(customer)
            lead = await self.lead_repo.save(lead)

            await self.audit.log("lead.converted", lead.id)
            await self.events.publish("LeadConverted", {
                "lead_id": lead.id, "customer_id": customer.id,
            })
            return customer
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in convert_lead")
            raise CRMException()

    async def create_deal(self, payload: dict, idem_key: str) -> Deal:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            deal = Deal(**payload)
            deal = await self.deal_repo.save(deal)

            verified = await self.deal_repo.get_by_id(deal.id)
            if not verified or verified.title != deal.title:
                raise CRMException("Read-back failed")

            await self.audit.log("deal.created", deal.id)
            await self.idempotency.set(idem_key, deal)
            await self.events.publish("DealCreated", deal)
            return deal
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_deal")
            raise CRMException()

    async def advance_deal(self, id: str, new_stage: str) -> Deal:
        try:
            deal = await self.deal_repo.get_by_id(id)
            if not deal:
                raise DealNotFoundException()

            old_stage = deal.stage
            deal.advance_stage(new_stage)
            deal = await self.deal_repo.save(deal)
            await self.cache.delete(id)
            await self.audit.log(f"deal.stage_{new_stage.lower()}", id)

            if new_stage == "CLOSED_WON":
                await self.events.publish("DealWon", deal)
            elif new_stage == "CLOSED_LOST":
                await self.events.publish("DealLost", deal)
            else:
                await self.events.publish("DealStageChanged", {
                    "deal_id": id, "from": old_stage, "to": new_stage,
                })
            return deal
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in advance_deal")
            raise CRMException()

    async def get_pipeline(self, owner_id: str | None = None) -> dict:
        """Get pipeline summary — สรุปไปป์ไลน์"""
        try:
            deals = await self.deal_repo.list_open(owner_id)
            summary: dict[str, dict] = {}
            for stage in DealStage:
                stage_deals = [d for d in deals if d.stage == stage.value]
                summary[stage.value] = {
                    "count": len(stage_deals),
                    "total_value": sum(d.value for d in stage_deals),
                    "weighted_value": sum(d.weighted_value for d in stage_deals),
                }
            return summary
        except Exception as e:
            logger.opt(exception=e).error("Error in get_pipeline")
            raise CRMException()
```

**`application/mappers.py`** — `LeadMapper`, `DealMapper`, `ActivityMapper`
**`application/exceptions.py`** — `CRMException`, `LeadNotFoundException`, `DealNotFoundException`
**`application/utils.py`** — `calculate_weighted_pipeline()`

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class LeadModel(BaseModel):
    __tablename__ = "leads"
    name = Column(String(200), nullable=False)
    contact = Column(String(200))
    source = Column(String(50), index=True)
    status = Column(String(20), nullable=False, default="NEW", index=True)
    assigned_to = Column(String(36), index=True)
    email = Column(String(255))
    phone = Column(String(20))
    notes = Column(Text)

class DealModel(BaseModel):
    __tablename__ = "deals"
    title = Column(String(200), nullable=False)
    customer_id = Column(String(36), nullable=False, index=True)
    lead_id = Column(String(36), index=True)
    value = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), default="THB")
    stage = Column(String(20), nullable=False, default="PROSPECTING", index=True)
    probability = Column(Integer, default=0)
    expected_close = Column(Date)
    owner_id = Column(String(36), index=True)
    notes = Column(Text)
    __table_args__ = (
        CheckConstraint("value >= 0", name="ck_deal_value"),
        CheckConstraint("probability >= 0 AND probability <= 100", name="ck_deal_probability"),
    )

class ActivityModel(BaseModel):
    __tablename__ = "activities"
    entity_type = Column(String(20), nullable=False, index=True)  # LEAD, DEAL, CUSTOMER
    entity_id = Column(String(36), nullable=False, index=True)
    activity_type = Column(String(20), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    actor_id = Column(String(36))
```

**`infrastructure/repositories.py`** — `PostgresLeadRepository`, `PostgresDealRepository`, `PostgresActivityRepository`
**`infrastructure/caches.py`** — `RedisCRMCache`
**`infrastructure/services.py`** — `NotificationService` (LINE/Email)

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])

@router.post("/leads/", status_code=201)
async def create_lead(payload: LeadCreate, idem_key: str = Header(...), ...): ...

@router.get("/leads/{id}/")
async def get_lead(id: str, ...): ...

@router.get("/leads/")
async def list_leads(filters: LeadQuery, ...): ...

@router.post("/leads/{id}/convert/")
async def convert_lead(id: str, payload: ConvertRequest, ...): ...

@router.post("/deals/", status_code=201)
async def create_deal(payload: DealCreate, idem_key: str = Header(...), ...): ...

@router.patch("/deals/{id}/stage/")
async def advance_deal(id: str, payload: StageRequest, ...): ...

@router.patch("/deals/{id}/win/")
async def win_deal(id: str, ...): ...

@router.patch("/deals/{id}/lose/")
async def lose_deal(id: str, payload: LoseRequest, ...): ...

@router.get("/pipeline/")
async def get_pipeline(owner_id: str | None = None, ...): ...

@router.post("/activities/")
async def log_activity(payload: ActivityCreate, ...): ...
```

**`presentation/schemas.py`** — `LeadCreate`, `DealCreate`, `ConvertRequest`, `StageRequest`, `ActivityCreate`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_crm_use_cases()`

### 5. Invariants
- `Deal.value >= 0`
- `Deal.probability` 0-100
- Deal stage forward-only
- Closed deal ห้ามเปลี่ยน stage
- `weighted_value == value * probability / 100`

### 6. Domain Events
- `LeadCreated`, `LeadConverted`, `LeadLost`
- `DealCreated`, `DealStageChanged`, `DealWon`, `DealLost`
- `ActivityLogged`

### 7. Tests
```python
async def test_create_lead(): ...
async def test_convert_lead(): ...
async def test_deal_stage_forward_only():
    """Property: deal stage forward only"""
    deal = Deal(title="D1", customer_id="c1", value=Decimal("1000"), stage="PROPOSAL")
    with pytest.raises(Exception):
        deal.advance_stage("PROSPECTING")

async def test_deal_value_non_negative():
    with pytest.raises(Exception):
        Deal(title="D1", customer_id="c1", value=Decimal("-100"))

async def test_weighted_value():
    deal = Deal(title="D1", customer_id="c1", value=Decimal("10000"), probability=50)
    assert deal.weighted_value == Decimal("5000.00")

async def test_closed_deal_immutable(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `crm`

**`db/migrations/V001__create_crm.sql`**
```sql
BEGIN;

CREATE TABLE tenant_crm.leads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    name            VARCHAR(200) NOT NULL,
    contact         VARCHAR(200),
    source          VARCHAR(50),
    status          VARCHAR(20) NOT NULL DEFAULT 'NEW',
    assigned_to     UUID,
    email           VARCHAR(255),
    phone           VARCHAR(20),
    notes           TEXT,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX ix_leads_status ON tenant_crm.leads(status) WHERE deleted_at IS NULL;
CREATE INDEX ix_leads_assigned ON tenant_crm.leads(assigned_to) WHERE deleted_at IS NULL;

CREATE TABLE tenant_crm.deals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    title           VARCHAR(200) NOT NULL,
    customer_id     UUID NOT NULL,
    lead_id         UUID,
    value           NUMERIC(15,2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'THB',
    stage           VARCHAR(20) NOT NULL DEFAULT 'PROSPECTING',
    probability     INTEGER NOT NULL DEFAULT 0 CHECK (probability BETWEEN 0 AND 100),
    expected_close  DATE,
    owner_id        UUID,
    notes           TEXT,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX ix_deals_customer ON tenant_crm.deals(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX ix_deals_stage ON tenant_crm.deals(stage) WHERE deleted_at IS NULL;
CREATE INDEX ix_deals_owner ON tenant_crm.deals(owner_id) WHERE deleted_at IS NULL;

CREATE TABLE tenant_crm.activities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    entity_type     VARCHAR(20) NOT NULL,
    entity_id       UUID NOT NULL,
    activity_type   VARCHAR(20) NOT NULL,
    subject         VARCHAR(200) NOT NULL,
    description     TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_id        UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_activities_entity ON tenant_crm.activities(entity_type, entity_id, occurred_at DESC);

-- RLS
ALTER TABLE tenant_crm.leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_leads_tenant ON tenant_crm.leads
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_crm.deals ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_deals_tenant ON tenant_crm.deals
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_crm.activities ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_activities_tenant ON tenant_crm.activities
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_crm.sql`**
```sql
BEGIN;
-- Seed CRM sample data
COMMIT;
```

**`db/migrations/V003__rollback_crm.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_crm.activities CASCADE;
DROP TABLE IF EXISTS tenant_crm.deals CASCADE;
DROP TABLE IF EXISTS tenant_crm.leads CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `crm`

**`tests/unit/test_crm.py`**
```python
import pytest
from decimal import Decimal
from app.modules.crm.domain.entities import Lead, Deal

class TestLeadDomain:
    def test_create_valid(self):
        l = Lead(name="John Doe", contact="john@example.com,mycompany.com,gmail.com")
        assert l.status == "NEW"

    def test_convert(self):
        l = Lead(name="John", contact="j@example.com,mycompany.com,gmail.com")
        customer = l.convert({"name": "John", "email": "j@example.com,mycompany.com,gmail.com"})
        assert l.status == "CONVERTED"

    def test_cannot_convert_twice(self):
        l = Lead(name="John")
        l.convert({})
        with pytest.raises(Exception):
            l.convert({})

class TestDealDomain:
    def test_create_valid(self):
        d = Deal(title="Deal 1", customer_id="c1", value=Decimal("10000"))
        assert d.stage == "PROSPECTING"

    def test_negative_value_raises(self):
        with pytest.raises(Exception):
            Deal(title="D1", customer_id="c1", value=Decimal("-100"))

    def test_advance_stage_forward_only(self):
        d = Deal(title="D1", customer_id="c1", value=Decimal("1000"), stage="PROPOSAL")
        with pytest.raises(Exception):
            d.advance_stage("PROSPECTING")

    def test_win_sets_probability_100(self):
        d = Deal(title="D1", customer_id="c1", value=Decimal("1000"), stage="NEGOTIATION")
        d.win()
        assert d.stage == "CLOSED_WON"
        assert d.probability == 100

    def test_weighted_value(self):
        d = Deal(title="D1", customer_id="c1", value=Decimal("10000"), probability=50)
        assert d.weighted_value == Decimal("5000.00")

    def test_property_stage_forward(self):
        """Property: deal stage ห้ามถอยกลับ"""
        for _ in range(100):
            d = Deal(title="D1", customer_id="c1", value=Decimal("1000"))
            # advance multiple times — never backward
```

**`tests/integration/test_crm_repository.py`** — testcontainers
**`tests/property/test_crm_invariants.py`** — hypothesis
**`tests/manual/manual_test_crm.md`** — manual test cases

---

## ✅ สรุป Layer 4 (Operations) — 13/65 ไฟล์

| # | Module | Prefix | Entities | Tables |
|---|---|---|---|---|
| 4.1 | `transport` | `trn` | Vehicle, Driver, Trip | `vehicles`, `drivers`, `trips` |
| 4.2 | `delivery` | `dlv` | Delivery, POD | `deliveries`, `delivery_lines` |
| 4.3 | `route` | `rte` | Route, Stop | `routes`, `route_stops` |
| 4.4 | `gps` | `gps` | Location, Geofence | `locations`, `geofences` |
| 4.5 | `retail` | `rtl` | Store | `stores` |
| 4.6 | `pos` | `pos` | POSTerminal, Transaction | `pos_terminals`, `pos_transactions` |
| 4.7 | `shift` | `shf` | Shift, Assignment | `shifts`, `shift_assignments` |
| 4.8 | `line_channel` | `line` | LINEMessage | `line_messages` |
| 4.9 | `promotion` | `promo` | Promotion, Rule | `promotions`, `promotion_rules` |
| 4.10 | `loyalty` | `loy` | LoyaltyAccount, Tier | `loyalty_accounts` |
| 4.11 | `crm` | `crm` | Lead, Deal, Activity | `leads`, `deals`, `activities` |
| 4.12 | `campaign` | `cmp` | Campaign | `campaigns` |
| 4.13 | `support` | `sup2` | Ticket | `tickets` |

**Layer 4 เสร็จสมบูรณ์ — ต่อไปคือ Layer 5 (Intelligence)**

---
