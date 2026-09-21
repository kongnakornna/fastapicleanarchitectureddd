# REVIEW-AUTH.md — Authentication Module Review Handoff

Module: `app/modules/authentication`
Scope reviewed: application + domain layers (tied to presentation conventions in `presentation/`).
Status: **Review only — no flows were fixed, no exception-naming sweep performed.** That work is deprioritized unless explicitly requested.

Files under review:
- `application/{use_cases,mappers,exceptions,interfaces,utils,__init__}.py`
- `domain/{exceptions,value_objects,entities,events,enums,__init__}.py`
- Convention baselines (read, not modified): `presentation/{routers,schemas,docs}.py`

---

## 1. Error handling

### 1.1 Exception naming inconsistency — `domain/exceptions.py`
- `http_status_code`/`ResponseMessages` classes use `...Exception` (e.g. `AccountLockedException`).
- One class uses `...Error` suffix: `RefreshTokenMalformedError`.
- Two classes have **no suffix at all**: `RefreshTokenInvalidEndpoint`, `LogoutInvalidEndpoint`.

Recommended: normalize to a single suffix family (all `...Exception` or all `...Error`). Renaming is a mechanical refactor; confirm before applying.

### 1.2 Semantics vs. status/message coupling — `domain/exceptions.py`
- `AccountLockedException` (378–389): mapped to **`403 FORBIDDEN`** but carries `ResponseMessages.UNAUTHORIZED_ERROR`. A 403 with an "unauthorized" message conflates auth (401) and authorization state (403) and will read oddly in API responses/logs.
- `InvalidResetCodeException` (336–347), `InvalidOtpCodeException` (350–361), `PasswordMismatchException` (364–375) all reuse **`VALIDATION_ERROR`** as the user-facing message. Distinct violations are therefore indistinguishable to callers consuming the message field.

Suggested follow-ups (not applied):
- Give `AccountLockedException` a dedicated message (e.g. a lockout notice) or map it to a distinct status/messages entry.
- Give each validation-class exception its own `ResponseMessages` entry so API consumers can differentiate reset-code vs OTP vs password-mismatch failures.

### 1.3 Empty `__init__.py` — `application/__init__.py`, `domain/__init__.py`
Both are empty (0 lines). If the architecture convention in `shared` relies on `disable_exceptions()` to be called in the package/container layer, these packages do not do it — exceptions defined here will not be selectively disabled per environment. Confirm whether `shared`'s `disable_exceptions()` is expected here; if not, this is a no-op note.

### 1.4 Dead file — `application/utils.py`
`utils.py` is completely empty. Either delete it or document its intended purpose; an empty module invites future orphan utility code.

---

## 2. Placeholder / dead flow family

These flows reserve real routes/use-cases but do not actually implement or persist their effect. They are the highest-value candidates for either completing or cutting/flagging.

### 2.1 `forgot_password` — `application/use_cases.py` (253–257)
- Logs that a reset code was "sent".
- The actual send is **commented out / TODO**.
- `str(uuid4())[:6].upper()` is generated but **never persisted** (no entity attribute/DB write), so the code could never be validated later.

### 2.2 `reset_password` — `application/use_cases.py` (stub)
- Only raises `PasswordMismatchException()`.
- Reset-code validation is **commented out**.
- The flow cannot complete a password reset even if `forgot_password` were wired correctly.

### 2.3 `two_step_verification` — `application/use_cases.py` (329–351)
- `_otp_code = str(uuid4())[:6]` is generated but **never sent** anywhere.

### 2.4 `two_step_code` — `application/use_cases.py` (356–397)
- Code check is **hardcoded** `code != "123456"`, raising `InvalidOtpCodeException()`.
- No relation to any generated/persisted OTP from `two_step_verification`.

### 2.5 `lock_screen` — `application/use_cases.py` (303–324)
- Calls `token_service.verify_password` and raises `InvalidCredentialsException()`.
- Verify this is intentional (PIN/lock-screen semantics reusing password hashing) vs a placeholder; if lock-screen has no stored unlock secret, the flow always succeeds or always fails.

Recommendation: bundle 2.1–2.4 as a single "password recovery / 2FA" epic with explicit product decisions (send channel, persistence table, code expiry), or mark them explicitly as stubs in code + docs. Do not ship half-wired flows silently.

---

## 3. Layering / mapping

### 3.1 `cache_entity_mapper` — `application/mappers.py` (521–547)
- Post-construct attribute poke: `authentication.blacklisted = data["blacklisted"]` after entity creation.
- Prefer mapping this via the entity's own method/constructor signature so invariants live inside the domain (e.g. an `AuthenticationEntity.mark_blacklisted(...)` or `with_blacklist(...)`), rather than reaching into attributes from the mapper.

### 3.2 Silent fallback defaults — mappers
- `User()` (empty aggregate), `refresh_token=None`, `Role.USER` etc. are used as fallbacks when source data is missing.
- Silent defaults can mask malformed persisted state (e.g. a user row missing identity fields renders as an empty `User`). Consider explicit "missing/required field" errors, or at least a logged warning, when required mapping inputs are absent.

### 3.3 `sync_entity_from_model` — `application/mappers.py` (346–365)
- Pushes DB-generated values (ids, timestamps) back **into** the domain entity, coupling the domain object to persistence-produced state.
- If these values are needed for the response, transform them at the presentation layer instead of mutating the entity.

### 3.4 Token claim construction duplicated — `entity_cache_mapper` + entity/event hooks
- Refresh `iat`/`nbf` sourced from `updated_at`.
- Access `iat`/`nbf` sourced from `created_at`.
- `exp` sourced from `expires_at`.
- The same claim-building logic appears in the mapper **and** in entity/event hooks. Consolidate claim construction into a single token factory (use case/service) so the source fields and expiry math cannot drift between paths.

### 3.5 `refresh_access_token` vs `renew_tokens` — near-duplicate
- Two methods implement essentially the same refresh/reissue behavior.
- Merge into one entry point, or document the intentional difference (e.g. access-only refresh vs full token pair renewal) so callers do not pick arbitrarily.

---

## 4. Consistency with module conventions

Positive baseline confirmed — these match the presentation wrap pattern and should be preserved:
- Domain exceptions subclass `StandardException` (from `app.modules.shared.application.exceptions`) and carry `http_status_code` + a `ResponseMessages` value from `app.modules.shared.domain.enums`.
- Use cases are bound in `application/interfaces.py` and instantiated through `Depends(...)`; presentation wraps `DomainError`-derived exceptions per the shared `DomainException(e)`/`StandardException` re-raise pattern.

As long as new flows follow this shape, the existing presentation error mapping will not need changes.

---

## Out of scope / deferred (done only on explicit request)
- Refactoring `two_step_code` hardcoded `"123456"` check.
- Exception-naming sweep (section 1.1).
- `routers.py` ↔ `docs.py` duplication.
- Fixing any flow or schema semantics described above.