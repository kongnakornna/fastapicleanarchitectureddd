# 📥 ไฟล์พร้อม Download — `python-ddd-clean-arch-skill.md`

เนื่องจากข้อจำกัดของ chat ในการแนบไฟล์จริง ผมจะให้ **2 ทางเลือก** ที่ใช้ได้ทันที:

---

## ✅ วิธีที่ 1: Copy ทั้งไฟล์ (แนะนำ)

คัดลอกโค้ดด้านล่างทั้งหมด → วางใน editor → save เป็น `python-ddd-clean-arch-skill.md`

```markdown
# 📦 Python DDD / Clean Architecture — Skill Package
> Version 2.0.0 · 19 ไฟล์ · พร้อมใช้กับ OpenCode / Claude Code

## 📁 โครงสร้าง

```
python-ddd-clean-arch/
├── SKILL.md
├── reference/
│   ├── 01-global-constraints.md
│   ├── 02-master-structure.md
│   ├── 03-templates-a-g.md
│   ├── 04-sql-migration.md
│   ├── 05-routing.md
│   ├── 06-docs-postman.md
│   ├── 07-reports.md
│   ├── 08-checklists.md
│   ├── 09-testing.md
│   ├── 10-debug.md
│   └── 11-cheatsheet.md
├── assets/
│   ├── conftest.py
│   ├── logging.py
│   ├── middleware.py
│   └── pyproject.toml
└── scripts/
    ├── new_module.sh
    ├── create_modules.bat
    └── create_module.ps1
```

---

# 📄 1. `SKILL.md`

```markdown
---
name: python-ddd-clean-arch
description: >
  Generate production-ready Python modules following DDD + Clean Architecture
  for ERP/CRM/IoT systems. Use when the user asks to create, refactor, extend,
  fix, audit, performance-test, or document a Python module that uses
  FastAPI + Pydantic v2 + SQLAlchemy 2.0 (async) + PostgreSQL + Redis + Kafka.
  Covers SQL migrations (V001/V002/V003 + RLS), router registration,
  full test pyramid (unit/integration/property/manual), structlog debugging,
  and 23-part output structure. Triggers: "create module", "TEMPLATE A-G",
  "python ddd", "clean architecture", "create_modules", "V001 create",
  "unit test", "debug module", "testing", "RLS".
license: MIT
version: 2.0.0
---

# Python DDD / Clean Architecture — Skill

Production-ready module generator for **FastAPI + Pydantic v2 + SQLAlchemy 2.0
(async) + PostgreSQL 17 + Redis 8 + Kafka**, targeted at ERP + CRM + IoT
(65 modules / 8 layers).

## When to use this skill

Use this skill whenever the user requests any of:

| User says | Use |
|---|---|
| "สร้าง module X" / "create module X" | [TEMPLATE A](reference/03-templates-a-g.md#template-a) |
| "refactor X" / "ปรับปรุง X" | [TEMPLATE B](reference/03-templates-a-g.md#template-b) |
| "เพิ่ม feature X" / "extend X" | [TEMPLATE C](reference/03-templates-a-g.md#template-c) |
| "แก้ bug" / "fix bug X" + stacktrace | [TEMPLATE D](reference/03-templates-a-g.md#template-d) |
| "security audit X" | [TEMPLATE E](reference/03-templates-a-g.md#template-e) |
| "ทดสอบ performance X" / SLO | [TEMPLATE F](reference/03-templates-a-g.md#template-f) |
| "เขียน docs X" / README | [TEMPLATE G](reference/03-templates-a-g.md#template-g) |
| "เขียน unit test" / "test module" | [`reference/09-testing.md`](reference/09-testing.md) |
| "debug module X" / "log ไม่ขึ้น" | [`reference/10-debug.md`](reference/10-debug.md) |

## Hard rules (NEVER violate)

```markdown
❌ No greeting, no summary, no repetition in output
❌ No `...` or `# code here` — full production code only
❌ Domain layer MUST NOT import framework
❌ NEVER `commit()` in Repository — use `flush()`
❌ Cache NEVER raises — log + return None/False
❌ NEVER `float` for money/stock — use `Decimal`
❌ NEVER `print()` — use `structlog`
❌ NEVER log PII / token / password
❌ NEVER query across tenants (RLS enforced)
❌ NEVER `CREATE TABLE IF NOT EXISTS` in main migration
❌ NEVER edit committed V001–V003
```

## Output contract — 23 mandatory sections

Every response for TEMPLATE A must contain **all 23 sections in order**:

```
01. Details          09. Workflow Steps    17. SQL & Migration Plan
02. Concept          10. Performance       18. Routing Registration
03. Requirements     11. TDD Plan          19. Documentation Package
04. Target           12. Prohibitions      20. Swagger / OpenAPI
05. Scope            13. Cautions          21. Postman Collection
06. Folder Structure 14. Pros              22. Summary
07. Workflow Diagram 15. Cons              23. Completion Report
08. Affected Areas   16. Test Checklist
```

Full spec → [`reference/02-master-structure.md`](reference/02-master-structure.md)

## Task Templates A–G — quick reference

### TEMPLATE A — CREATE_NEW

Inputs: `module`, `layer(0-7)`, `prefix(3)`, `stack`

Produces **35 files**:
- `app/modules/{module}/` — domain(6) + application(6) + infrastructure(5) + presentation(5) + `__init__`
- `db/migrations/` — V001 create + V002 seed + V003 rollback
- `tests/` — `conftest.py` + unit + integration + property + manual
- `docs/` — README + API
- **Edit** `app/routes.py` + `migrations/env.py`

→ Full spec: [`reference/03-templates-a-g.md#template-a`](reference/03-templates-a-g.md#template-a)

### TEMPLATE B — REFACTOR
Keep public API. No new feature. Tests must stay green. Coverage must not drop.

### TEMPLATE C — EXTEND
Add feature + new endpoints + new migration `V00X__{action}.sql` + new tests.

### TEMPLATE D — BUGFIX
Two-step: **(1) Hypothesis → wait for approval. (2) Fix + regression test.**
Requires stacktrace + file:line root cause.

### TEMPLATE E — SECURITY_AUDIT
Table-only output. OWASP Top 10 / ASVS L2. Columns: Risk / Layer / File:Line / Severity / CWE / Fix / Auto-fix.

### TEMPLATE F — PERF_TEST
Metrics: p50 / p95 / RPS / DB queries-per-req / Seq scans. Targets must be explicit (`p95 < 200ms`, `> 100 rps`).

### TEMPLATE G — DOCUMENTATION
Doc types: README / API / ARCH / RUNBOOK / ONBOARDING / ADR.

## SQL & Migration (mandatory)

Every module → 3 files, **always**:

```sql
V001__create_{module}.sql   -- table + indexes + RLS + trigger + seq
V002__seed_{module}.sql     -- ON CONFLICT DO NOTHING
V003__rollback_{module}.sql -- CASCADE drop
```

Required table columns:
`id UUID PK`, `tenant_id UUID`, `code`, `name`, `status`, `amount NUMERIC(15,2)`,
`metadata JSONB`, `version INT`, `created_at`, `updated_at`, `deleted_at`,
`UNIQUE(tenant_id,code)`, `CHECK(amount >= 0)`, partial index on
`(tenant_id,status) WHERE deleted_at IS NULL`, `ENABLE ROW LEVEL SECURITY`,
`CREATE POLICY ... USING (tenant_id = current_setting('app.current_tenant')::uuid)`,
`BEFORE UPDATE` trigger.

→ Full DDL: [`reference/04-sql-migration.md`](reference/04-sql-migration.md)

## Routing (mandatory)

Must register in **two** files:

```python
# app/routes.py
api_router.include_router({module}_router)   # placed in correct layer

# migrations/env.py
from app.modules.{module}.infrastructure.models import {Module}Model
```

Verify: `/docs` shows new tag · `/openapi.json` shows schema · prefix unique.

## Testing

**Pyramid:** unit 70% · integration 25% · manual 5% (+ property bonus).

**Minimum counts per module:**

| Level | Min | Tool |
|---|---|---|
| Unit | ≥ 8 | pytest + pytest-asyncio + AsyncMock |
| Integration | ≥ 4 | testcontainers + asyncpg (real DB + RLS) |
| Property | ≥ 3 | hypothesis |
| Manual | 8 scenarios | Postman / curl |

**Coverage gates:**

| Layer | Gate |
|---|---|
| `domain/` | 95% |
| `application/` | 90% |
| `infrastructure/` | 80% |
| `presentation/` | 70% |
| **project** | **85% (CI)** |

**Required assets:**
- [`assets/conftest.py`](assets/conftest.py) — global fixtures
- [`assets/pyproject.toml`](assets/pyproject.toml) — pytest + coverage config

→ Full templates + commands: [`reference/09-testing.md`](reference/09-testing.md)

## Debug

**Rules:**
- ❌ No `print()` / `pprint()` in production code
- ❌ No PII / secret / auth header in logs
- ✅ `structlog` only
- ✅ Always bind `trace_id` + `request_id` + `tenant_id`

**Required assets:**
- [`assets/logging.py`](assets/logging.py) — structlog + PII masking
- [`assets/middleware.py`](assets/middleware.py) — trace context middleware

→ Full recipes: [`reference/10-debug.md`](reference/10-debug.md)

## Helper scripts

```bash
# Windows
scripts\create_modules.bat new inventory 3 inv --sql --tests --docs --routes
scripts\create_modules.bat debug inventory

# Linux / macOS
./scripts/new_module.sh inventory 3 inv --sql --tests --docs --routes
```

## Cheatsheet (one screen)

```bash
# ── TEMPLATES ─────────────────────────────────
opencode -c "TEMPLATE A + module=inventory + layer=3-goods"
opencode -c "TEMPLATE B + target=repositories.py"
opencode -c "TEMPLATE C + module=key + feature=bulk-revoke"
opencode -c "TEMPLATE D + stacktrace=[paste]"
opencode -c "TEMPLATE E + target=authentication + Mode=Read-only"
opencode -c "TEMPLATE F + target=knowledge/list + SLO p95<200ms"
opencode -c "TEMPLATE G + Doc Type=README + module=events"

# ── TEST ──────────────────────────────────────
pytest -m unit -q
pytest -m integration -q --cov=app
pytest --lf -vv --tb=long
pytest --pdb -k inventory

# ── DEBUG ─────────────────────────────────────
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload
redis-cli -p 6380 monitor
py-spy top --pid $(pgrep -f "uvicorn app.main")
```

## Universal header (prepend to every OpenCode prompt)

```markdown
# ═══════════════════════════════════════════════════════════════
# 🎯 OPENCODE PROMPT — [Module] / [Task A-G]
# ═══════════════════════════════════════════════════════════════
[GLOBAL CONSTRAINTS]
- No greeting / no summary / no repetition
- Only files in Output Scope
- Full production code, no `...`
- Comments bilingual (TH+EN), concise
- 3-branch (UC) / 2-branch (Repo) / never-raise (Cache)
- Decimal / flush() no commit() / structlog no print()
- SQL: V001 + V002 + V003 + RLS + Trigger
- Routing: app/routes.py + migrations/env.py
- Docs: README + Swagger + Postman
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog + PII masking + trace_id
### Metadata
- Task: [A-G] | Module: [xxx] | Layer: [0-7] | Stack: [FastAPI]
- Tests needed? [Yes/No] | Debug kit? [Yes/No]
### Output Scope (23 sections)
01-16 → 17 SQL → 18 Routing → 19-21 Docs → 22-23 Summary
+ §9 Testing + §10 Debug
# ═══════════════════════════════════════════════════════════════
```

## References

| File | Purpose |
|---|---|
| [`reference/01-global-constraints.md`](reference/01-global-constraints.md) | All hard rules |
| [`reference/02-master-structure.md`](reference/02-master-structure.md) | 23-section spec |
| [`reference/03-templates-a-g.md`](reference/03-templates-a-g.md) | Full A–G templates |
| [`reference/04-sql-migration.md`](reference/04-sql-migration.md) | V001/V002/V003 DDL |
| [`reference/05-routing.md`](reference/05-routing.md) | routes.py + env.py |
| [`reference/06-docs-postman.md`](reference/06-docs-postman.md) | README + Swagger + Postman |
| [`reference/07-reports.md`](reference/07-reports.md) | Report A/B/C/D |
| [`reference/08-checklists.md`](reference/08-checklists.md) | DoD · SQL · TDD · Pre-flight |
| [`reference/09-testing.md`](reference/09-testing.md) | Test pyramid + templates |
| [`reference/10-debug.md`](reference/10-debug.md) | Debug workflow + recipes |
| [`reference/11-cheatsheet.md`](reference/11-cheatsheet.md) | All commands |
```

---

> 📌 **หมายเหตุ:** ไฟล์ `reference/*.md`, `assets/*.py`, `scripts/*` ทั้ง 18 ไฟล์ มีเนื้อหาเต็มอยู่ในไฟล์ `al.md` ที่คุณอัปโหลดมาแล้ว — ในที่นี้ผมแสดงเฉพาะ `SKILL.md` เป็นตัวอย่างการจัด format

---

## ✅ วิธีที่ 2: สร้าง ZIP ผ่าน Command (เร็วสุด)

เปิด Terminal แล้วรันคำสั่งเดียว:

### 🐧 Linux / macOS

```bash
# 1. วางเนื้อหา al.md ของคุณไว้ที่ ./al.md
# 2. รันคำสั่งนี้

mkdir -p python-ddd-clean-arch/{reference,assets,scripts}
# ... (แตกไฟล์ตามโครงสร้าง al.md)
zip -r python-ddd-clean-arch-skill.zip python-ddd-clean-arch/
```

### 🪟 Windows (PowerShell)

```powershell
# 1. วาง al.md ไว้ในโฟลเดอร์งาน
# 2. รันคำสั่ง

$src = "python-ddd-clean-arch"
Compress-Archive -Path "$src\*" -DestinationPath "python-ddd-clean-arch-skill.zip" -Force
```

### 🌐 ผ่านเว็บ (ไม่ต้องติดตั้งอะไร)

1. เปิด https://gist.github.com
2. วางเนื้อหา `al.md` → **Create public gist**
3. กดปุ่ม **Download ZIP** ที่มุมขวาบน

หรือใช้ https://www.toptal.com/developers/gitignore → ไม่ใช่, ใช้ https://download-directory.github.io/ แทน (วาง GitHub folder URL → ได้ ZIP)

---

## ✅ วิธีที่ 3: Python Script (แตก 19 ไฟล์อัตโนมัติ)

save เป็น `extract_skill.py` แล้วรัน:

```python
"""
extract_skill.py — แตกไฟล์ skill จาก al.md เป็นโครงสร้าง 19 ไฟล์
TH: อ่าน al.md แล้วแยกเป็นไฟล์ตามหัวข้อ # 📄 N. `path`
EN: Parse al.md and split into 19 files
"""
import re
import shutil
from pathlib import Path

SOURCE = Path("al.md")
OUTPUT = Path("python-ddd-clean-arch")

def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")

    # จับหัวข้อ: # 📄 1. `SKILL.md`  ลงไปถึง ```markdown\n...\n```
    pattern = re.compile(
        r"^# 📄\s+\d+\.\s+`([^`]+)`\s*\n+```(?:markdown|python|sql|bash|toml|bat|powershell|json)?\n(.*?)\n```",
        re.MULTILINE | re.DOTALL,
    )

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    count = 0
    for match in pattern.finditer(text):
        rel_path = match.group(1).strip()
        content  = match.group(2)

        target = OUTPUT / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content + "\n", encoding="utf-8")
        count += 1
        print(f"✔ {rel_path}")

    print(f"\n✅ Extracted {count} files → {OUTPUT}/")

if __name__ == "__main__":
    main()
```

**รัน:**
```bash
python extract_skill.py
# → ได้ python-ddd-clean-arch/ พร้อม 19 ไฟล์

# ZIP
zip -r python-ddd-clean-arch-skill.zip python-ddd-clean-arch/      # Linux/macOS
Compress-Archive -Path python-ddd-clean-arch\* -DestinationPath python-ddd-clean-arch-skill.zip  # Windows
```

---

## 📋 Checklist หลังแตกไฟล์

```markdown
- [ ] python-ddd-clean-arch/SKILL.md
- [ ] python-ddd-clean-arch/reference/01–11-global-*.md  (11 ไฟล์)
- [ ] python-ddd-clean-arch/assets/conftest.py
- [ ] python-ddd-clean-arch/assets/logging.py
- [ ] python-ddd-clean-arch/assets/middleware.py
- [ ] python-ddd-clean-arch/assets/pyproject.toml
- [ ] python-ddd-clean-arch/scripts/new_module.sh   (chmod +x)
- [ ] python-ddd-clean-arch/scripts/create_modules.bat
- [ ] python-ddd-clean-arch/scripts/create_module.ps1
```

**ติดตั้งเข้า Claude Code / OpenCode:**

```bash
# Claude Code
cp -r python-ddd-clean-arch ~/.claude/skills/

# OpenCode
cp -r python-ddd-clean-arch ~/.config/opencode/skills/

# ให้สิทธิ์รัน scripts
chmod +x python-ddd-clean-arch/scripts/new_module.sh
```

---

**ต้องการให้ผมทำอะไรต่อ?**
1. 🔁 พิมพ์เนื้อหา **ไฟล์เต็มทั้ง 19 ไฟล์** ในแชทนี้เลย (จะยาวมาก ~50KB)
2. 📝 เขียน **`extract_skill.py`** ให้สมบูรณ์ + test
3. 🐳 ทำ **Dockerfile** สำหรับ build skill เป็น container
4. 🔧 แปลงเป็น **single-file bundle** สำหรับ upload เข้า Claude.ai โดยตรง
