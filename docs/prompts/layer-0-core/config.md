## 📄 Module 0.5: `config`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `config` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `ConfigEntry` (entity), `ConfigScope` (enum), `ConfigType` (enum) |
| **Prefix** | `cfg` |
| **Tables** | `tenant_{tid}.config_entries` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `config`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Config มี 3 ระดับ: **GLOBAL → TENANT → USER** (override ตามลำดับ)
- รองรับ hot-reload ผ่าน Redis Pub/Sub
- Type-safe: `string`, `int`, `decimal`, `bool`, `json`, `secret`
- Secret ต้องเข้ารหัส (Fernet) และไม่ return ผ่าน API
- Cache ที่ Redis พร้อม TTL + tombstone

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`**
```python
@dataclass
class ConfigEntry(BaseEntity):
    """Config entry — เอนทิตีรายการตั้งค่า"""
    key: str = ""
    value: str = ""
    value_type: str = "string"
    scope: str = "TENANT"
    scope_id: str = ""
    is_secret: bool = False
    description: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.key:
            raise DomainError("Config key required")
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.key):
            raise DomainError(f"Invalid key format: {self.key}")

    def typed_value(self):
        """Return typed value — คืนค่าตามชนิด"""
        if self.value_type == "int":
            return int(self.value)
        if self.value_type == "decimal":
            return Decimal(self.value)
        if self.value_type == "bool":
            return self.value.lower() in ("1", "true", "yes")
        if self.value_type == "json":
            return json.loads(self.value)
        return self.value

    def mask(self) -> "ConfigEntry":
        """Mask secret value — ปิดบังค่า secret"""
        if self.is_secret:
            copy = replace(self, value="***")
            return copy
        return self
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ConfigKey:
    """Config key VO — วัตถุกุญแจ config"""
    value: str

    def __post_init__(self):
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.value):
            raise DomainError(f"Invalid config key: {self.value}")

    def namespace(self) -> str:
        return self.value.split(".", 1)[0]
```

**`domain/enums.py`**
```python
class ConfigScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"

class ConfigType(str, Enum):
    STRING = "string"
    INT = "int"
    DECIMAL = "decimal"
    BOOL = "bool"
    JSON = "json"
    SECRET = "secret"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class IConfigRepository(Protocol):
    async def get(self, key: str, scope: str, scope_id: str) -> ConfigEntry | None: ...
    async def get_effective(self, key: str, tenant_id: str, user_id: str | None) -> ConfigEntry | None: ...
    async def save(self, entry: ConfigEntry) -> ConfigEntry: ...
    async def list(self, scope: str, scope_id: str) -> list[ConfigEntry]: ...

class IConfigCache(Protocol):
    async def get(self, key: str) -> ConfigEntry | None: ...
    async def insert(self, key: str, entry: ConfigEntry) -> None: ...
    async def invalidate(self, key: str) -> None: ...

class ISecretCipher(Protocol):
    def encrypt(self, plain: str) -> str: ...
    def decrypt(self, cipher: str) -> str: ...
```

**`application/use_cases.py`**
```python
class ConfigUseCases:
    """Config use cases — กรณีการใช้งาน config"""

    def __init__(self, repo, cache, cipher, events, config):
        ...

    async def get_effective(self, key: str, user_id: str | None = None) -> ConfigEntry:
        """Get effective config — ดึงค่าที่มีผล"""
        try:
            ctx = get_context()
            cache_key = f"{ctx.tenant_id}:{user_id or '-'}:{key}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            entry = await self.repo.get_effective(key, ctx.tenant_id, user_id)
            if entry is None:
                raise ConfigKeyNotFoundException(key)

            if entry.is_secret:
                plain = self.cipher.decrypt(entry.value)
                entry = replace(entry, value=plain)

            await self.cache.insert(cache_key, entry)
            return entry
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_effective config")
            raise ConfigException()

    async def set(self, key: str, value: str, value_type: str, scope: str,
                  scope_id: str, is_secret: bool = False) -> ConfigEntry:
        """Set config — ตั้งค่า config"""
        try:
            if is_secret:
                value = self.cipher.encrypt(value)
            entry = ConfigEntry(
                key=key, value=value, value_type=value_type,
                scope=scope, scope_id=scope_id, is_secret=is_secret,
            )
            entry = await self.repo.save(entry)

            # Read-back
            verified = await self.repo.get(key, scope, scope_id)
            if not verified or verified.value != entry.value:
                raise ConfigException("Read-back failed")

            await self.cache.invalidate(f"{scope_id}:{key}")
            await self.events.publish("ConfigChanged", {"key": key, "scope": scope})
            return entry.mask()
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in set config")
            raise ConfigException()
```

**`application/mappers.py`** — `ConfigMapper` (with mask)
**`application/exceptions.py`** — `ConfigException`, `ConfigKeyNotFoundException`
**`application/utils.py`** — `get_config(key, default)` helper

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class ConfigEntryModel(BaseModel):
    __tablename__ = "config_entries"
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False, default="string")
    scope = Column(String(20), nullable=False, index=True)
    scope_id = Column(String(36), nullable=False, index=True)
    is_secret = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("key", "scope", "scope_id", name="uq_config_key_scope"),
    )
```

**`infrastructure/repositories.py`** — `PostgresConfigRepository` (with 3-level override)
**`infrastructure/caches.py`** — `RedisConfigCache` (TTL 300s, tombstone, never raises)
**`infrastructure/services.py`**
```python
class FernetCipher:
    """Fernet cipher — เข้ารหัส Fernet"""
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def encrypt(self, plain: str) -> str:
        return self.fernet.encrypt(plain.encode()).decode()

    def decrypt(self, cipher: str) -> str:
        return self.fernet.decrypt(cipher.encode()).decode()

class ConfigPubSub:
    """Config hot-reload via Redis Pub/Sub — โหลด config ใหม่ทันที"""
    async def subscribe(self, callback) -> None: ...
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/config", tags=["Config"])

@router.get("/{key}/")
async def get_config(key: str, ...): ...

@router.put("/{key}/")
async def set_config(key: str, payload: ConfigSetRequest, ...): ...

@router.get("/")
async def list_config(scope: str, ...): ...

@router.delete("/{key}/")
async def delete_config(key: str, ...): ...
```

**`presentation/schemas.py`** — `ConfigEntrySchema`, `ConfigSetRequest` (mask secrets)
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `get_config_use_cases()`

### 5. Error Handling
- Use cases: **3-branch**
- Repositories: **2-branch**
- Caches: **never-raise**

### 6. Invariants
- 3-level override: `USER` > `TENANT` > `GLOBAL`
- Secret values **ไม่ return ผ่าน API** (mask)
- Config key format: `^[a-z][a-z0-9_.]*$`
- Cache invalidation ต้อง propagate ทันที

### 7. Domain Events
- `ConfigChanged`, `ConfigDeleted`, `ConfigReloaded`

### 8. Tests
```python
async def test_override_precedence(): ...
async def test_secret_encrypted_at_rest(): ...
async def test_secret_masked_in_api(): ...
async def test_invalid_key_format_raises(): ...
async def test_property_override_order():
    """Property: user > tenant > global เสมอ"""
    ...
```

## Output
- ไฟล์ 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---
