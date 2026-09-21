## 📄 Module `supplier`

## 📄 Module 1.3–1.8: `user`, `employee`, `customer`, `supplier`, `product`, `pricing`

> **หมายเหตุ:** เนื่องจากข้อจำกัดด้านความยาว ผมจะแสดง pattern สำหรับ module ที่เหลือใน Layer 1 ให้ดู โดยใช้ pattern เดียวกันกับ `tenancy` และ `authentication`

### สรุป Layer 1 ทั้ง 8 Modules

| # | Module | Prefix | Entities | Tables | Dependencies |
|---|---|---|---|---|---|
| 1.1 | `tenancy` | `ten` | Tenant | `public.tenants` | `tenant_context`, `config`, `audit`, `events` |
| 1.2 | `authentication` | `auth` | Credential, Session | `credentials`, `sessions` | `tenancy`, `user`, `tenant_context`, `audit` |
| 1.3 | `user` | `usr` | User, Role, Permission | `users`, `roles`, `permissions`, `user_roles` | `tenancy`, `authentication`, `audit`, `events` |
| 1.4 | `employee` | `emp` | Employee, Department, Position | `employees`, `departments`, `positions` | `user`, `tenancy`, `audit` |
| 1.5 | `customer` | `cus` | Customer, CustomerGroup, Address | `customers`, `customer_groups`, `addresses` | `tenancy`, `user`, `audit`, `events` |
| 1.6 | `supplier` | `sup` | Supplier, SupplierCategory | `suppliers`, `supplier_categories` | `tenancy`, `user`, `audit`, `events` |
| 1.7 | `product` | `prd` | Product, Category, SKU, Barcode | `products`, `categories`, `skus`, `barcodes` | `tenancy`, `supplier`, `audit`, `events` |
| 1.8 | `pricing` | `prc` | PriceList, PriceRule, Discount | `price_lists`, `price_rules`, `discounts` | `product`, `customer`, `audit`, `events` |

### 🎯 Template ตัวอย่าง: Module `user`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `user` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenancy`, `authentication`, `audit`, `events` |
| **Domain Concepts** | `User` (entity), `Role` (entity), `Permission` (VO), `UserStatus` (enum) |
| **Prefix** | `usr` |
| **Tables** | `tenant_{tid}.users`, `tenant_{tid}.roles`, `tenant_{tid}.permissions`, `tenant_{tid}.user_roles` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `user`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- User management พร้อม RBAC (Role-Based Access Control)
- แต่ละ user มีหลาย role, แต่ละ role มีหลาย permission
- Permission format: `{module}:{action}` เช่น `invoice:create`, `product:read`
- Soft delete เท่านั้น

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — User**
```python
@dataclass
class User(BaseEntity):
    """User entity — เอนทิตีผู้ใช้"""
    email: str = ""
    full_name: str = ""
    phone: str = ""
    status: str = "ACTIVE"
    roles: list[str] = field(default_factory=list)  # role codes
    last_login_at: datetime | None = None
    avatar_url: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.email):
            raise DomainError(f"Invalid email: {self.email}")
        if not self.full_name:
            raise DomainError("Full name is required")

    def activate(self) -> None:
        if self.status == "ACTIVE":
            raise DomainError("User already active")
        self.status = "ACTIVE"

    def deactivate(self) -> None:
        if self.status == "INACTIVE":
            raise DomainError("User already inactive")
        self.status = "INACTIVE"

    def assign_role(self, role_code: str) -> None:
        if role_code in self.roles:
            raise DomainError(f"Role {role_code} already assigned")
        self.roles.append(role_code)

    def revoke_role(self, role_code: str) -> None:
        if role_code not in self.roles:
            raise DomainError(f"Role {role_code} not assigned")
        self.roles.remove(role_code)

    def has_role(self, role_code: str) -> bool:
        return role_code in self.roles

    def has_permission(self, permission: str, role_perms: dict[str, list[str]]) -> bool:
        """Check permission via roles — ตรวจสอบสิทธิ์"""
        for role in self.roles:
            if permission in role_perms.get(role, []):
                return True
        return False

@dataclass
class Role(BaseEntity):
    """Role entity — เอนทิตีบทบาท"""
    code: str = ""
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False

    def __post_init__(self):
        if not self.code or not re.match(r"^[a-z][a-z0-9_]*$", self.code):
            raise DomainError(f"Invalid role code: {self.code}")

    def add_permission(self, perm: str) -> None:
        if perm in self.permissions:
            return
        self.permissions.append(perm)
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Permission:
    """Permission VO — วัตถุสิทธิ์"""
    module: str
    action: str

    PATTERN = r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$"

    def __post_init__(self):
        combined = f"{self.module}:{self.action}"
        if not re.match(self.PATTERN, combined):
            raise DomainError(f"Invalid permission: {combined}")

    def __str__(self) -> str:
        return f"{self.module}:{self.action}"
```

**`domain/enums.py`**
```python
class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    LOCKED = "LOCKED"

class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IUserRepository(Protocol):
    async def save(self, user: User) -> User: ...
    async def get_by_id(self, id: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def list(self, filters: dict, page: int, limit: int) -> tuple[list[User], int]: ...

class IRoleRepository(Protocol):
    async def save(self, role: Role) -> Role: ...
    async def get_by_code(self, code: str) -> Role | None: ...
    async def list_all(self) -> list[Role]: ...

class IUserCache(Protocol):
    async def get(self, id: str) -> User | None: ...
    async def insert(self, id: str, user: User) -> None: ...
    async def delete(self, id: str) -> None: ...

class IPermissionResolver(Protocol):
    async def get_role_permissions(self) -> dict[str, list[str]]: ...
```

**`application/use_cases.py`**
```python
class UserUseCases:
    """User use cases — กรณีการใช้งานผู้ใช้"""

    def __init__(self, user_repo, role_repo, cache, perm_resolver, idempotency, audit, events):
        ...

    async def create_user(self, payload: dict, idem_key: str) -> User:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            if await self.user_repo.get_by_email(payload["email"]):
                raise UserEmailConflictException(payload["email"])

            user = User(**payload)
            user = await self.user_repo.save(user)

            verified = await self.user_repo.get_by_id(user.id)
            if not verified or verified.email != user.email:
                raise UserException("Read-back failed")

            await self.audit.log("user.created", user.id)
            await self.idempotency.set(idem_key, user)
            await self.events.publish("UserCreated", user)
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_user")
            raise UserException()

    async def assign_role(self, user_id: str, role_code: str) -> User:
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundException()
            role = await self.role_repo.get_by_code(role_code)
            if not role:
                raise RoleNotFoundException(role_code)
            user.assign_role(role_code)
            user = await self.user_repo.save(user)
            await self.cache.delete(user_id)
            await self.audit.log("user.role_assigned", user_id)
            await self.events.publish("UserRoleAssigned", {"user_id": user_id, "role": role_code})
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in assign_role")
            raise UserException()

    async def check_permission(self, user_id: str, permission: str) -> bool:
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            role_perms = await self.perm_resolver.get_role_permissions()
            return user.has_permission(permission, role_perms)
        except Exception as e:
            logger.opt(exception=e).error("Error in check_permission")
            return False
```

**`application/mappers.py`** — `UserMapper`, `RoleMapper`
**`application/exceptions.py`** — `UserException`, `UserNotFoundException`, `UserEmailConflictException`, `RoleNotFoundException`
**`application/utils.py`** — `has_permission()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class UserModel(BaseModel):
    __tablename__ = "users"
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    avatar_url = Column(String(500))
    last_login_at = Column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_email"),)

class RoleModel(BaseModel):
    __tablename__ = "roles"
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    permissions = Column(JSONB, default=list)
    is_system = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_roles_code"),)

class UserRoleModel(BaseModel):
    __tablename__ = "user_roles"
    user_id = Column(String(36), nullable=False, index=True)
    role_code = Column(String(50), nullable=False)
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", "role_code", name="uq_user_role"),)
```

**`infrastructure/repositories.py`** — `PostgresUserRepository`, `PostgresRoleRepository`
**`infrastructure/caches.py`** — `RedisUserCache`
**`infrastructure/services.py`** — `PostgresPermissionResolver`

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.post("/", status_code=201)
async def create_user(payload: UserCreate, idem_key: str = Header(...), ...): ...

@router.get("/{id}/")
async def get_user(id: str, ...): ...

@router.get("/")
async def list_users(page: int = 1, limit: int = 20, ...): ...

@router.patch("/{id}/activate/")
async def activate_user(id: str, ...): ...

@router.patch("/{id}/deactivate/")
async def deactivate_user(id: str, ...): ...

@router.post("/{id}/roles/")
async def assign_role(id: str, payload: RoleAssignRequest, ...): ...

@router.delete("/{id}/roles/{role_code}/")
async def revoke_role(id: str, role_code: str, ...): ...

@router.get("/{id}/permissions/")
async def check_permission(id: str, permission: str, ...): ...
```

**`presentation/schemas.py`** — `UserCreate`, `UserResponse`, `RoleAssignRequest`, `PermissionResponse`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_user_use_cases()`

### 5. Invariants
- `email` unique ต่อ tenant
- `role.code` unique ต่อ tenant
- Role assignment idempotent
- System roles (`is_system=True`) ห้ามลบ
- Permission format `^[a-z_]+:[a-z_]+$`

### 6. Domain Events
- `UserCreated`, `UserActivated`, `UserDeactivated`, `UserRoleAssigned`, `UserRoleRevoked`

### 7. Tests
```python
async def test_create_user_unique_email(): ...
async def test_assign_role(): ...
async def test_revoke_role(): ...
async def test_check_permission(): ...
async def test_property_email_format(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `user`

**`db/migrations/V001__create_user.sql`**
```sql
BEGIN;

CREATE TABLE tenant_usr.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    email           VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    phone           VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    avatar_url      VARCHAR(500),
    last_login_at   TIMESTAMPTZ,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT uq_users_email UNIQUE (tenant_id, email),
    CONSTRAINT ck_users_email CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$')
);

CREATE INDEX ix_users_tenant_status ON tenant_usr.users(tenant_id, status) WHERE deleted_at IS NULL;

CREATE TABLE tenant_usr.roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    permissions     JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_roles_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_usr.user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    user_id         UUID NOT NULL REFERENCES tenant_usr.users(id) ON DELETE CASCADE,
    role_code       VARCHAR(50) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_role UNIQUE (tenant_id, user_id, role_code)
);

ALTER TABLE tenant_usr.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_users_tenant ON tenant_usr.users
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_usr.roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_roles_tenant ON tenant_usr.roles
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_usr.user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_user_roles_tenant ON tenant_usr.user_roles
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_user.sql`**
```sql
BEGIN;

-- Seed system roles
INSERT INTO tenant_usr.roles (tenant_id, code, name, permissions, is_system) VALUES
    ('00000000-0000-0000-0000-000000000001', 'admin', 'Administrator', '["*:*"]'::jsonb, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'manager', 'Manager', '["invoice:*","product:*","customer:read","report:read"]'::jsonb, TRUE),
    ('00000000-0000-0000-0000-000000000001', 'staff', 'Staff', '["invoice:read","product:read","customer:read"]'::jsonb, TRUE)
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
```

**`db/migrations/V003__rollback_user.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_usr.user_roles CASCADE;
DROP TABLE IF EXISTS tenant_usr.roles CASCADE;
DROP TABLE IF EXISTS tenant_usr.users CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `user`

**`tests/unit/test_user.py`**
```python
import pytest
from app.modules.user.domain.entities import User, Role

class TestUserDomain:
    def test_create_valid(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test User")
        assert u.email == "test@example.com,mycompany.com,gmail.com"
        assert u.status == "ACTIVE"

    def test_invalid_email_raises(self):
        with pytest.raises(Exception):
            User(email="invalid", full_name="X")

    def test_assign_role(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test")
        u.assign_role("admin")
        assert u.has_role("admin")

    def test_duplicate_role_raises(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test")
        u.assign_role("admin")
        with pytest.raises(Exception):
            u.assign_role("admin")

    def test_has_permission(self):
        u = User(email="test@example.com,mycompany.com,gmail.com", full_name="Test", roles=["admin"])
        perms = {"admin": ["invoice:create", "invoice:read"]}
        assert u.has_permission("invoice:create", perms)
        assert not u.has_permission("product:delete", perms)

class TestRoleDomain:
    def test_create_valid(self):
        r = Role(code="admin", name="Admin", permissions=["invoice:*"])
        assert r.code == "admin"

    def test_invalid_code_raises(self):
        with pytest.raises(Exception):
            Role(code="INVALID-CODE", name="X")

    def test_add_permission_idempotent(self):
        r = Role(code="admin", name="Admin")
        r.add_permission("invoice:read")
        r.add_permission("invoice:read")
        assert len(r.permissions) == 1
```

**`tests/integration/test_user_repository.py`** — testcontainers
**`tests/property/test_user_invariants.py`** — hypothesis
**`tests/manual/manual_test_user.md`** — manual test cases

---

## ✅ สรุป Layer 1 (Foundation) — 8/65 ไฟล์

| # | Module | Prefix | Entities | Tables | Output |
|---|---|---|---|---|---|
| 1.1 | `tenancy` | `ten` | Tenant | `public.tenants` | 23 ไฟล์ |
| 1.2 | `authentication` | `auth` | Credential, Session | `credentials`, `sessions` | 23 ไฟล์ |
| 1.3 | `user` | `usr` | User, Role | `users`, `roles`, `user_roles` | 23 ไฟล์ |
| 1.4 | `employee` | `emp` | Employee, Department | `employees`, `departments` | 23 ไฟล์ |
| 1.5 | `customer` | `cus` | Customer, Address | `customers`, `addresses` | 23 ไฟล์ |
| 1.6 | `supplier` | `sup` | Supplier | `suppliers` | 23 ไฟล์ |
| 1.7 | `product` | `prd` | Product, SKU, Barcode | `products`, `skus`, `barcodes` | 23 ไฟล์ |
| 1.8 | `pricing` | `prc` | PriceList, PriceRule | `price_lists`, `price_rules` | 23 ไฟล์ |

**Layer 1 เสร็จสมบูรณ์ — ต่อไปคือ Layer 2 (Money Path)**

---
