# 🔍 Root Cause — `hashed_password: None`

## หลักฐานจาก Traceback

```
INSERT INTO erp_users (..., hashed_password, ...) VALUES (..., $8::VARCHAR, ...)
parameters = ('Demo', 'Demo', 'Demo', None, None, 'demo@example.com',
              '+566988522431', None,  ← hashed_password = None
              'USER', True, ...)
```

**และ log ที่ควรจะมีจาก `UserUseCases.create` — ไม่มี:**
```
"Initializing create user use case with user: demo@example.com."   ← หายไป
"Creating user demo@example.com in database."                       ← มีแค่ตัวนี้
```

→ **`UserUseCases.create()` ไม่ถูกเรียก** — `SharedUseCases.create_user()` **bypass ไปที่ `UserRepository.create()` ตรง ๆ**

→ `hash_password()` ไม่ทำงาน → `hashed_password = None` → **NOT NULL violation**

> ⚠️ **การแก้ของผมรอบก่อนผิด** — ผมบอก "อย่า hash ใน `sign_up` เพราะ `UserUseCases.create` จะ hash ให้" — แต่ `SharedUseCases.create_user` ไม่ได้ผ่าน `UserUseCases.create` → ต้อง hash ที่ `sign_up` เอง

---

## 🔧 Fix — Full Code 4 ไฟล์

### 📄 1. `app/modules/authentication/application/use_cases.py`

**แก้เฉพาะ `sign_up()`** — เพิ่ม hash กลับ (พร้อม guard กัน double-hash):

```python
    async def sign_up(self, user: User) -> User:
        """
        Sign up use case.

        ขั้นตอน:
            1. ตรวจว่า email ซ้ำหรือไม่
            2. Hash password — ต้องทำที่นี้ เพราะ SharedUseCases.create_user
               bypass ไป UserRepository.create โดยตรง (ไม่ผ่าน UserUseCases.create)
            3. สร้าง user ผ่าน shared_service
            4. (TODO) ส่งอีเมลต้อนรับ
        """
        try:
            logger.debug(
                f"Initializing sign up use case for user: {user.censored_email}."
            )

            # TH: ตรวจ email ซ้ำก่อน — ถ้าซ้ำให้ตอบ error ทันที ไม่ต้อง hash ให้เสียเวลา
            # EN: check duplicate email first
            existing_user = await self.shared_service.get_user_by_email(user)
            if existing_user:
                logger.info(f"User with email {user.censored_email} already exists.")
                raise EmailAlreadyExistsException(email=str(user.email))

            # TH: ต้อง hash ที่นี่ — SharedUseCases.create_user ไม่ผ่าน UserUseCases.create
            #     ถ้ามี hashed_password อยู่แล้ว (เช่นสร้างจาก flow อื่น) → skip
            # EN: hash here — SharedUseCases.create_user bypasses UserUseCases.create.
            #     Skip if already hashed (e.g. created via another flow).
            if not user.hashed_password:
                if not user.password:
                    logger.warning(
                        f"User {user.censored_email} has no password to hash."
                    )
                    raise AuthenticationException()
                user.hashed_password = self.token_service.hash_password(user.password)

            # TH: persist ผ่าน shared service
            # EN: persist via shared service
            user = await self.shared_service.create_user(user)

            # TH: ส่งอีเมลต้อนรับ — ยังไม่ implement
            # EN: welcome email — not yet implemented
            logger.debug(
                f"User created with id {user.id}. "
                f"Welcome email will be sent later (not yet implemented)."
            )

            logger.debug(
                f"User {user.censored_email} signed up successfully with id {user.id}."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the sign up use case."
            )
            raise AuthenticationException()
```

---

### 📄 2. `app/modules/authentication/application/mappers.py`

**แก้ `entity_sign_up_mapper()`** — build จาก `user` จริง:

```python
def entity_sign_up_mapper(user: User) -> SignUpResponse:
    """
    TH: map User entity (persisted) → SignUpResponse
    EN: map User entity (persisted) → SignUpResponse
    """
    if user is None or user.id is None:
        raise ValueError(
            "entity_sign_up_mapper requires a persisted user with non-None id"
        )

    name = user.name
    return SignUpResponse(
        message=ResponseMessages.SUCCESS.value,
        id=user.id,
        first_name=(name.first_name if name else "") or "",
        last_name=(name.last_name if name else "") or "",
        preferred_name=(name.preferred_name if name else "") or "",
        email=str(user.email) if user.email else "",
        phone=str(user.phone) if user.phone else None,
        role=user.role if user.role else Role.USER,
        is_active=user.is_active if user.is_active is not None else True,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
```

**ตรวจ import** — ต้องมี:
```python
from app.modules.shared.domain.enums import ResponseMessages, Role
from app.modules.user.domain.entities import User
```

---

### 📄 3. `app/modules/user/application/mappers.py`

**แก้ `create_entity_mapper()`** — explicit mapping (ไม่ใช้ automapper):

```python
def create_entity_mapper(payload) -> User:
    """
    TH: map request payload → User entity (explicit — เพราะ payload อาจเป็น
        CreateRequest หรือ SignUpRequest ที่มี field เกิน automapper จับ)
    EN: map request payload → User entity (explicit — payload may be
        CreateRequest or SignUpRequest with extra fields)
    """
    first_name, last_name, preferred_name = _extract_name_fields(payload)

    name = Name(
        first_name=first_name,
        last_name=last_name,
        preferred_name=preferred_name,
    )

    phone = getattr(payload, "phone", None) or getattr(payload, "phone_number", None)

    user_kwargs: dict = {
        "name": name,
        "email": getattr(payload, "email", None),
        "password": getattr(payload, "password", None),
    }

    if phone:
        user_kwargs["phone"] = phone

    gender = getattr(payload, "gender", None)
    if gender is not None:
        user_kwargs["gender"] = gender

    birthdate = getattr(payload, "birthdate", None)
    if birthdate is not None:
        user_kwargs["birthdate"] = birthdate

    return User(**user_kwargs)


def entity_create_mapper(user: User) -> CreateResponse:
    """
    TH: map User entity → CreateResponse envelope
    EN: map User entity → CreateResponse envelope
    """
    return CreateResponse(
        code=201,
        method="POST",
        path="/api/v1/user",
        timestamp=datetime.now(BRASILIA_TZ),
        details={
            "message": ResponseMessages.CREATED.value,
            "data": {"id": str(user.id)} if user.id else {},
        },
    )
```

---

### 📄 4. `app/modules/user/presentation/schemas.py`

**แก้ `CreateRequest`** — `birthdate` / `gender` optional:

```python
class CreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Doe"])
    preferred_name: str | None = Field(default=None, max_length=100)

    # TH: optional — signup สร้าง user ก่อนกรอกโปรไฟล์
    # EN: optional — signup creates user before profile completion
    gender: Gender | None = Field(default=None)
    birthdate: date | None = Field(default=None)

    email: EmailStr
    phone: str | None = Field(default=None)
    password: str = Field(min_length=8, max_length=64)

    # ... validators คงเดิม
```

---

## ⚠️ SIDE-EFFECT WARNING — `app/core/security.py`

**Error 2–6 (403)** ยังต้องแก้ที่ `app/core/security.py` — paste โค้ดจริงมาให้ผมเขียนเต็ม

Pattern ที่ถูกต้อง (ดูของเก่า):

```python
async def no_authentication(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
) -> None:
    """public endpoint — ต้องเข้าได้เสมอ"""
    if credentials is None and not request.cookies:
        return
    logger.warning(
        "no_authentication.active_session_on_public_endpoint",
        path=request.url.path,
    )
    return
```

---

## 📊 สรุป — Bug Chain

| Layer | ปัญหา | Fix |
|---|---|---|
| `sign_up()` | ไม่ hash password (เพราะเข้าใจผิดว่า UserUseCases.create hash ให้) | hash ที่ `sign_up` เอง |
| `SharedUseCases.create_user` | bypass `UserUseCases.create` → ไป repo ตรง | **ไม่แก้** — แค่ hash ที่ sign_up |
| `entity_sign_up_mapper` | return `SignUpResponse()` เปล่า | map จาก user จริง |
| `create_entity_mapper` | ใช้ automapper กับ payload ที่มี field เกิน | explicit mapping |
| `CreateRequest` | `birthdate` required แต่ User entity ไม่ต้องการ | optional |

---

## 🧪 ทดสอบหลังแก้

```powershell
# restart server
uv run uvicorn app.app:app --reload
```

**Sign-up test:**
```bash
curl -X POST http://localhost:8000/api/v1/authentication/sign-up/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Demo",
    "username": "demo",
    "email": "demo@example.com",
    "phone_number": "+566988522431",
    "password": "MyP@ssword123",
    "confirm_password": "MyP@ssword123",
    "agree_terms": true
  }'
```

**คาดหวัง:**
```json
{
  "message": "Operation successful",
  "id": "...",
  "first_name": "Demo",
  "last_name": "Demo",
  "preferred_name": "Demo",
  "email": "demo@example.com",
  "phone": "+566988522431",
  "role": "user",
  "is_active": true,
  "created_at": "2026-09-21T...",
  "updated_at": "2026-09-21T..."
}
```

**ตรวจ DB:**
```sql
SELECT id, email, hashed_password IS NOT NULL AS has_pw, role
FROM erp_users WHERE email = 'demo@example.com';
```

ควรเห็น `has_pw = true`

---

**Paste `app/core/security.py` มา** ถ้าต้องการให้ผมแก้ Error 2–6 (403) ให้ครบครับ
