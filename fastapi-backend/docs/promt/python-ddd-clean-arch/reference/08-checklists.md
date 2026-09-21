# 08 — Checklists

> 5 checklist: DoD · SQL · TDD · Pre-flight · Security

---

## ✅ Definition of Done (DoD)

### Code

```markdown
- [ ] Domain ไม่ import framework (FastAPI/SQLAlchemy/Pydantic)
- [ ] ใช้ `Decimal` ทั้งหมดที่เกี่ยวกับเงิน/สต็อก
- [ ] Repository ใช้ `flush()` ไม่มี `commit()`
- [ ] Cache never-raise (log + return None/False)
- [ ] Error handling 3-branch (UC) / 2-branch (Repo) / never (Cache)
- [ ] Type hints ครบทุก function (input + output)
- [ ] docstring 2 ภาษา (TH + EN) สั้น
- [ ] ไม่มี `print()` — ใช้ `structlog`
- [ ] ไม่มี `TODO` / `FIXME` / `...` / `pass` ที่ไม่จำเป็น
- [ ] ไม่มี hardcoded secret / API key / connection string
- [ ] Ruff lint ผ่าน (0 warnings)
- [ ] Mypy strict ผ่าน (0 errors)
```

### SQL

```markdown
- [ ] V001: CREATE TABLE (ไม่มี IF NOT EXISTS)
- [ ] V001: คอลัมน์ครบ (id, tenant_id, code, name, status, amount,
      metadata, version, created_at, updated_at, deleted_at)
- [ ] V001: CONSTRAINT (UNIQUE, CHECK, FK)
- [ ] V001: Index (partial + composite + created_at desc)
- [ ] V001: ENABLE ROW LEVEL SECURITY
- [ ] V001: CREATE POLICY (tenant_id = current_setting)
- [ ] V001: BEFORE UPDATE trigger (updated_at)
- [ ] V002: seed + ON CONFLICT DO NOTHING
- [ ] V003: rollback + CASCADE
- [ ] ทุกไฟล์มี BEGIN / COMMIT
- [ ] migrations/env.py: import model แล้ว
- [ ] `alembic upgrade head` ผ่าน
- [ ] `alembic downgrade -1` ผ่าน
- [ ] `alembic upgrade head` อีกครั้ง ผ่าน
```

### Routing

```markdown
- [ ] register ใน `app/routes.py`
- [ ] register ใน `migrations/env.py`
- [ ] อยู่ layer ถูกต้อง
- [ ] prefix ไม่ซ้ำ
- [ ] `/docs` เห็น tag ใหม่
- [ ] `/openapi.json` valid
- [ ] `curl GET /api/v1/{module}/` → 200
```

### Tests

```markdown
- [ ] Unit ≥ 8 tests
  - [ ] happy path
  - [ ] edge case (zero, boundary)
  - [ ] error case (domain exception)
  - [ ] value object behavior
  - [ ] use case with mocks
  - [ ] cache never-raise
  - [ ] read-back verification
  - [ ] idempotency replay
- [ ] Integration ≥ 4 tests
  - [ ] save → get round-trip
  - [ ] RLS blocks other tenant
  - [ ] unique constraint violation
  - [ ] soft delete filter
- [ ] Property ≥ 3 tests × 100 iter
  - [ ] non-negative amount valid
  - [ ] negative amount rejected
  - [ ] addition commutative
- [ ] Manual test 8 scenarios
  - [ ] Create happy 201
  - [ ] Duplicate 409
  - [ ] Invalid 422
  - [ ] Get by id 200
  - [ ] List + filter 200
  - [ ] Update 200 + version+1
  - [ ] Delete 204 + deleted_at
  - [ ] Cross-tenant 404
- [ ] Coverage ≥ 85% (CI gate)
  - [ ] domain ≥ 95%
  - [ ] application ≥ 90%
  - [ ] infrastructure ≥ 80%
  - [ ] presentation ≥ 70%
```

### Docs

```markdown
- [ ] README_{module}.md ครบ 13 หัวข้อ
- [ ] API_{module}.md มี request/response
- [ ] Swagger metadata (operation_id, responses)
- [ ] Postman collection import ได้
- [ ] Architecture diagram (Mermaid)
- [ ] Changelog entry
```

### Debug

```markdown
- [ ] ไม่มี `print()` / `pdb` / `breakpoint()` ในโค้ด
- [ ] structlog bind context (trace_id, request_id, tenant_id)
- [ ] PII masking enabled
- [ ] ไม่มี PII ใน log (ตรวจ 3 sample logs)
- [ ] trace_id propagate ผ่าน header ครบ
```

---

## ✅ SQL Migration Checklist

```markdown
### V001 create
- [ ] BEGIN / COMMIT
- [ ] CREATE SEQUENCE (ถ้ามี)
- [ ] CREATE TABLE (ไม่มี IF NOT EXISTS)
- [ ] PRIMARY KEY (UUID default gen_random_uuid)
- [ ] tenant_id UUID NOT NULL
- [ ] version INTEGER NOT NULL DEFAULT 1
- [ ] created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- [ ] updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- [ ] deleted_at TIMESTAMPTZ (nullable)
- [ ] UNIQUE (tenant_id, code)
- [ ] CHECK (amount >= 0)
- [ ] CHECK (status IN (...))
- [ ] INDEX partial (tenant_id, status) WHERE deleted_at IS NULL
- [ ] INDEX (code)
- [ ] INDEX (created_at DESC)
- [ ] ALTER TABLE ... ENABLE ROW LEVEL SECURITY
- [ ] CREATE POLICY p_{module}_tenant USING (tenant_id = current_setting(...))
- [ ] TRIGGER BEFORE UPDATE (updated_at)

### V002 seed
- [ ] BEGIN / COMMIT
- [ ] INSERT ... ON CONFLICT (tenant_id, code) DO NOTHING

### V003 rollback
- [ ] BEGIN / COMMIT
- [ ] DROP TRIGGER IF EXISTS
- [ ] DROP POLICY IF EXISTS
- [ ] DROP TABLE IF EXISTS ... CASCADE
- [ ] DROP SEQUENCE IF EXISTS
```

---

## ✅ TDD Flow Checklist

### Step 1: RED

```markdown
- [ ] เขียน test ก่อน implement
- [ ] test fail (รันดู error message)
- [ ] cover happy path
- [ ] cover edge cases
- [ ] cover error cases
```

### Step 2: GREEN

```markdown
- [ ] เขียน minimal code ให้ผ่าน
- [ ] ห้าม over-engineer
- [ ] test เขียวทุกตัว
- [ ] รัน full suite (ไม่มี regression)
```

### Step 3: REFACTOR

```markdown
- [ ] extract method / class ที่ซ้ำ
- [ ] rename ให้ชัดเจน
- [ ] behavior คงเดิม (test ยังเขียว)
- [ ] Coverage ไม่ลด
- [ ] No duplication (DRY)
```

### Step 4: INTEGRATION

```markdown
- [ ] เพิ่ม integration test (DB จริง)
- [ ] ทดสอบ RLS cross-tenant
- [ ] ทดสอบ unique constraint
- [ ] ทดสอบ transaction rollback
```

### Step 5: PROPERTY

```markdown
- [ ] เขียน hypothesis test
- [ ] 100+ iterations
- [ ] ไม่มี falsifying example
- [ ] shrink ทำงาน (ถ้า fail)
```

---

## ✅ Pre-Flight Checklist

ก่อนส่ง prompt ให้ OpenCode:

```markdown
- [ ] ใส่ Global Constraints
- [ ] ระบุ Task Type (A-G)
- [ ] ระบุ Module + Layer + Stack
- [ ] ระบุ Output Scope (รายชื่อไฟล์)
- [ ] SQL needed? Yes/No
- [ ] Routing update? Yes/No
- [ ] Docs needed? Yes/No
- [ ] Postman needed? Yes/No
- [ ] Tests needed? Yes/No
- [ ] Debug kit? Yes/No
- [ ] ถ้า Bugfix → มี stacktrace + repro steps
- [ ] ถ้า Security → ระบุ Mode (Read-only / Audit+Fix)
- [ ] ถ้า Perf → ระบุ SLO ชัดเจน
- [ ] ถ้าข้อมูลไม่พอ → ถาม 1 คำถามก่อน
```

---

## ✅ Security Checklist

```markdown
### A. Authentication & Authorization
- [ ] Nested JWT (JWS + JWE)
- [ ] Refresh token rotation
- [ ] RBAC ทุก endpoint
- [ ] Token expiry ≤ 15 นาที
- [ ] Logout = revoke refresh
- [ ] Session fixation protection

### B. Input Validation
- [ ] Pydantic v2 strict mode
- [ ] Max length ทุก string
- [ ] Whitelist enum
- [ ] SQL injection (ORM parameterized)
- [ ] Mass assignment (whitelist fields)
- [ ] File upload: type + size + scan
- [ ] SSRF protection (whitelist domains)
- [ ] XXE disabled (XML parser)

### C. Data Protection
- [ ] Encryption at rest (AES-256)
- [ ] TLS in transit (min 1.2)
- [ ] PII masking ใน logs
- [ ] Secret management (vault / env)
- [ ] Key rotation policy
- [ ] Backup encryption

### D. Multi-tenancy
- [ ] tenant_id ทุก query
- [ ] RLS policy ทุกตาราง
- [ ] Cross-tenant leakage test
- [ ] Tenant isolation ใน cache key
- [ ] Tenant ใน audit log
- [ ] Row-level validation ก่อน save

### E. API Security
- [ ] Rate limiting (per IP + per user)
- [ ] CORS whitelist
- [ ] CSRF (BFF pattern หรือ same-site cookie)
- [ ] Idempotency key
- [ ] Request size limit (1MB)
- [ ] Timeout (read 30s, write 60s)
- [ ] Circuit breaker (external calls)

### F. SQL Security
- [ ] RLS enabled + forced
- [ ] FK ON DELETE ถูกต้อง
- [ ] Search_path ปลอดภัย
- [ ] Least privilege DB user
- [ ] No dynamic SQL
- [ ] Stored procedure audit

### G. Dependency
- [ ] pip-audit ผ่าน
- [ ] bandit ผ่าน (0 high)
- [ ] Dependencies up-to-date
- [ ] SBOM generate
```

---

## ✅ Review Checklist (ก่อน merge)

```markdown
- [ ] PR description ชัดเจน
- [ ] Linked issue
- [ ] Tests pass (CI เขียว)
- [ ] Coverage ≥ 85%
- [ ] Lint / type check pass
- [ ] Migration test ผ่าน (up + down)
- [ ] Breaking change documented
- [ ] Changelog updated
- [ ] Docs updated
- [ ] Reviewer approved
```
```

--- 
