## 📄 Module 1.2: `authentication`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `authentication` |
| **Layer** | `1` (Foundation) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenancy`, `user`, `tenant_context`, `audit`, `config` |
| **Domain Concepts** | `Credential` (entity), `Token` (VO), `Session` (entity), `AuthMethod` (enum) |
| **Prefix** | `auth` |
| **Tables** | `tenant_{tid}.credentials`, `tenant_{tid}.sessions` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `authentication`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- JWT-based authentication: Access (15 min) + Refresh (7 days, rotating)
- Password hashing: Argon2id
- รองรับ: password, API key, OAuth2 (Google, LINE)
- Session เก็บใน Redis (TTL 7 days)
- Rate limit: 5 failed attempts → lock 15 นาที

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py` — Credential**
```python
@dataclass
class Credential(BaseEntity):
    """Credential entity — เอนทิตีข้อมูลรับรอง"""
    user_id: str = ""
    password_hash: str = ""
    auth_method: str = "PASSWORD"
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.user_id:
            raise DomainError("User ID is required")

    def is_locked(self) -> bool:
        return self.locked_until is not None and datetime.utcnow() < self.locked_until

    def record_failure(self) -> None:
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def record_success(self) -> None:
        self.failed_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()

@dataclass
class Session(BaseEntity):
    """Session entity — เอนทิตีเซสชัน"""
    user_id: str = ""
    refresh_token_hash: str = ""
    expires_at: datetime | None = None
    ip_address: str = ""
    user_agent: str = ""
    revoked_at: datetime | None = None

    def is_valid(self) -> bool:
        return self.revoked_at is None and self.expires_at and datetime.utcnow() < self.expires_at
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Token:
    """Token VO — วัตถุโทเคน"""
    value: str
    expires_at: datetime
    token_type: str = "Bearer"

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

@dataclass(frozen=True)
class TokenPair:
    """Token pair VO — วัตถุคู่โทเคน"""
    access_token: Token
    refresh_token: Token

@dataclass(frozen=True)
class Password:
    """Password VO — วัตถุรหัสผ่าน"""
    plain: str

    MIN_LENGTH = 8

    def __post_init__(self):
        if len(self.plain) < self.MIN_LENGTH:
            raise DomainError(f"Password must be at least {self.MIN_LENGTH} chars")
        if not re.search(r"[A-Z]", self.plain):
            raise DomainError("Password must contain uppercase")
        if not re.search(r"[0-9]", self.plain):
            raise DomainError("Password must contain digit")
```

**`domain/enums.py`**
```python
class AuthMethod(str, Enum):
    PASSWORD = "PASSWORD"
    API_KEY = "API_KEY"
    OAUTH_GOOGLE = "OAUTH_GOOGLE"
    OAUTH_LINE = "OAUTH_LINE"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class AuthResult(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
class ICredentialRepository(Protocol):
    async def save(self, cred: Credential) -> Credential: ...
    async def get_by_user_id(self, user_id: str) -> Credential | None: ...

class ISessionRepository(Protocol):
    async def save(self, session: Session) -> Session: ...
    async def get_by_token_hash(self, hash: str) -> Session | None: ...
    async def revoke(self, session_id: str) -> None: ...

class IPasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hash: str) -> bool: ...

class ITokenService(Protocol):
    def issue_access(self, user_id: str, tenant_id: str, roles: list[str]) -> Token: ...
    def issue_refresh(self, user_id: str, tenant_id: str) -> Token: ...
    def verify(self, token: str, token_type: str) -> dict: ...

class ISessionCache(Protocol):
    async def get(self, token_hash: str) -> dict | None: ...
    async def set(self, token_hash: str, data: dict, ttl: int) -> None: ...
    async def delete(self, token_hash: str) -> None: ...
```

**`application/use_cases.py`**
```python
class AuthenticationUseCases:
    """Authentication use cases — กรณีการใช้งาน authentication"""

    def __init__(self, cred_repo, session_repo, hasher, token_svc, cache, audit, events):
        ...

    async def login(self, email: str, password: str, ip: str, ua: str) -> TokenPair:
        """Login — เข้าสู่ระบบ"""
        try:
            ctx = get_context()
            cred = await self.cred_repo.get_by_email(email)
            if not cred:
                raise InvalidCredentialsException()

            if cred.is_locked():
                raise AccountLockedException(cred.locked_until)

            if not self.hasher.verify(password, cred.password_hash):
                cred.record_failure()
                await self.cred_repo.save(cred)
                raise InvalidCredentialsException()

            cred.record_success()
            await self.cred_repo.save(cred)

            access = self.token_svc.issue_access(cred.user_id, ctx.tenant_id, [])
            refresh = self.token_svc.issue_refresh(cred.user_id, ctx.tenant_id)

            session = Session(
                user_id=cred.user_id,
                refresh_token_hash=self._hash(refresh.value),
                expires_at=refresh.expires_at,
                ip_address=ip,
                user_agent=ua,
            )
            session = await self.session_repo.save(session)

            await self.cache.set(
                self._hash(refresh.value),
                {"user_id": cred.user_id, "session_id": session.id},
                ttl=7 * 86400,
            )
            await self.audit.log("auth.login", cred.user_id)
            await self.events.publish("UserLoggedIn", {"user_id": cred.user_id})

            return TokenPair(access_token=access, refresh_token=refresh)
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in login")
            raise AuthenticationException()

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Refresh token — ต่ออายุโทเคน"""
        try:
            payload = self.token_svc.verify(refresh_token, "refresh")
            token_hash = self._hash(refresh_token)

            session = await self.session_repo.get_by_token_hash(token_hash)
            if not session or not session.is_valid():
                raise InvalidTokenException()

            # Rotate: revoke old, issue new
            session.revoked_at = datetime.utcnow()
            await self.session_repo.save(session)
            await self.cache.delete(token_hash)

            access = self.token_svc.issue_access(payload["user_id"], payload["tenant_id"], payload.get("roles", []))
            new_refresh = self.token_svc.issue_refresh(payload["user_id"], payload["tenant_id"])

            new_session = Session(
                user_id=payload["user_id"],
                refresh_token_hash=self._hash(new_refresh.value),
                expires_at=new_refresh.expires_at,
            )
            await self.session_repo.save(new_session)
            await self.cache.set(self._hash(new_refresh.value), {"user_id": payload["user_id"]}, ttl=7*86400)

            return TokenPair(access_token=access, refresh_token=new_refresh)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in refresh")
            raise AuthenticationException()

    async def logout(self, refresh_token: str) -> None:
        """Logout — ออกจากระบบ"""
        try:
            token_hash = self._hash(refresh_token)
            session = await self.session_repo.get_by_token_hash(token_hash)
            if session:
                session.revoked_at = datetime.utcnow()
                await self.session_repo.save(session)
            await self.cache.delete(token_hash)
            await self.audit.log("auth.logout", session.user_id if session else "unknown")
        except Exception as e:
            logger.opt(exception=e).error("Error in logout")

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
```

**`application/mappers.py`** — `AuthMapper`
**`application/exceptions.py`** — `AuthenticationException`, `InvalidCredentialsException`, `AccountLockedException`, `InvalidTokenException`
**`application/utils.py`** — `require_auth()` decorator

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
class CredentialModel(BaseModel):
    __tablename__ = "credentials"
    user_id = Column(String(36), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    auth_method = Column(String(20), nullable=False, default="PASSWORD")
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))

class SessionModel(BaseModel):
    __tablename__ = "sessions"
    user_id = Column(String(36), nullable=False, index=True)
    refresh_token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    revoked_at = Column(DateTime(timezone=True))
```

**`infrastructure/repositories.py`** — `PostgresCredentialRepository`, `PostgresSessionRepository`
**`infrastructure/caches.py`** — `RedisSessionCache` (never raises)
**`infrastructure/services.py`**
```python
class ArgonHasher:
    """Argon2id hasher — ตัวแฮช Argon2id"""
    def __init__(self):
        self.ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

    def hash(self, plain: str) -> str:
        return self.ph.hash(plain)

    def verify(self, plain: str, hash: str) -> bool:
        try:
            self.ph.verify(hash, plain)
            return True
        except Exception:
            return False

class JWTService:
    """JWT service — บริการ JWT"""
    def __init__(self, secret: str, issuer: str = "erp-sme"):
        self.secret = secret
        self.issuer = issuer

    def issue_access(self, user_id: str, tenant_id: str, roles: list[str]) -> Token:
        exp = datetime.utcnow() + timedelta(minutes=15)
        payload = {"sub": user_id, "tid": tenant_id, "roles": roles, "typ": "access", "iss": self.issuer, "exp": exp}
        return Token(jwt.encode(payload, self.secret, algorithm="HS256"), exp)

    def issue_refresh(self, user_id: str, tenant_id: str) -> Token:
        exp = datetime.utcnow() + timedelta(days=7)
        payload = {"sub": user_id, "tid": tenant_id, "typ": "refresh", "iss": self.issuer, "exp": exp}
        return Token(jwt.encode(payload, self.secret, algorithm="HS256"), exp)

    def verify(self, token: str, token_type: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=["HS256"], issuer=self.issuer)
        if payload.get("typ") != token_type:
            raise InvalidTokenException(f"Token type mismatch: {payload.get('typ')} != {token_type}")
        return payload
```

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/login/")
async def login(payload: LoginRequest, request: Request, ...): ...

@router.post("/refresh/")
async def refresh(payload: RefreshRequest, ...): ...

@router.post("/logout/")
async def logout(payload: LogoutRequest, ...): ...

@router.get("/me/")
async def me(auth: Authentication = Depends(authenticate_user)): ...
```

**`presentation/schemas.py`** — `LoginRequest`, `TokenResponse`, `RefreshRequest`, `LogoutRequest`
**`presentation/docs.py`** — router_docs
**`presentation/dependencies.py`** — `authenticate_user()`, `get_current_user()`

### 5. Invariants
- Password ต้องยาว ≥ 8 + uppercase + digit
- 5 failed attempts → lock 15 นาที
- Refresh token rotating (ใช้แล้วrevoke)
- Session TTL 7 วัน
- Access token TTL 15 นาที

### 6. Domain Events
- `UserLoggedIn`, `UserLoggedOut`, `TokenRefreshed`, `AccountLocked`

### 7. Tests
```python
async def test_login_valid(): ...
async def test_login_invalid_password(): ...
async def test_account_lockout_after_5_failures(): ...
async def test_refresh_rotates_token(): ...
async def test_logout_revokes_session(): ...
async def test_property_password_strength(): ...
```

## Output
- 23 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `authentication`

**`db/migrations/V001__create_authentication.sql`**
```sql
BEGIN;

CREATE TABLE tenant_auth.credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    user_id         UUID NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    auth_method     VARCHAR(20) NOT NULL DEFAULT 'PASSWORD',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    last_login_at   TIMESTAMPTZ,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_credentials_user UNIQUE (tenant_id, user_id)
);

CREATE TABLE tenant_auth.sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,
    user_id             UUID NOT NULL,
    refresh_token_hash  VARCHAR(64) NOT NULL UNIQUE,
    expires_at          TIMESTAMPTZ NOT NULL,
    ip_address          VARCHAR(45),
    user_agent          VARCHAR(500),
    revoked_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sessions_user ON tenant_auth.sessions(user_id);
CREATE INDEX ix_sessions_expires ON tenant_auth.sessions(expires_at) WHERE revoked_at IS NULL;

ALTER TABLE tenant_auth.credentials ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_credentials_tenant ON tenant_auth.credentials
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE tenant_auth.sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_sessions_tenant ON tenant_auth.sessions
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_authentication.sql`**
```sql
BEGIN;
-- Seed credential สำหรับ demo user (password: Demo1234)
-- INSERT INTO tenant_auth.credentials (...) VALUES (...);
COMMIT;
```

**`db/migrations/V003__rollback_authentication.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_auth.sessions CASCADE;
DROP TABLE IF EXISTS tenant_auth.credentials CASCADE;
COMMIT;
```

### 🧪 Tests สำหรับ `authentication`

**`tests/unit/test_authentication.py`**
```python
import pytest
from datetime import datetime, timedelta
from app.modules.authentication.domain.entities import Credential, Session
from app.modules.authentication.domain.value_objects import Password, Token

class TestCredentialDomain:
    def test_lockout_after_5_failures(self):
        cred = Credential(user_id="u1", password_hash="hash")
        for _ in range(5):
            cred.record_failure()
        assert cred.is_locked()

    def test_success_resets_failures(self):
        cred = Credential(user_id="u1", password_hash="hash")
        cred.record_failure()
        cred.record_success()
        assert cred.failed_attempts == 0
        assert cred.locked_until is None

class TestPasswordVO:
    def test_too_short_raises(self):
        with pytest.raises(Exception):
            Password(plain="Ab1")

    def test_no_uppercase_raises(self):
        with pytest.raises(Exception):
            Password(plain="abcd1234")

    def test_no_digit_raises(self):
        with pytest.raises(Exception):
            Password(plain="Abcdefgh")

    def test_valid(self):
        p = Password(plain="Demo1234")
        assert p.plain == "Demo1234"
```

**`tests/integration/test_authentication_repository.py`** — testcontainers-based
**`tests/property/test_authentication_invariants.py`** — hypothesis
**`tests/manual/manual_test_authentication.md`** — manual test cases

---
