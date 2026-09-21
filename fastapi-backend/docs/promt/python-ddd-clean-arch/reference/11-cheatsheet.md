# 11 — Quick Command Cheatsheet

> รวมทุกคำสั่งที่ใช้บ่อย · copy-paste ได้เลย

---

## 🎯 Templates A–G

```bash
# ─── A: CREATE_NEW ────────────────────────────────────
opencode -c "TEMPLATE A + module=inventory + layer=3-goods + FULL OUTPUT"

# ─── B: REFACTOR ─────────────────────────────────────
opencode -c "TEMPLATE B + target=repositories.py"

# ─── C: EXTEND ───────────────────────────────────────
opencode -c "TEMPLATE C + module=key + feature=bulk-revoke"

# ─── D: BUGFIX ───────────────────────────────────────
opencode -c "TEMPLATE D + stacktrace=[paste]"

# ─── E: SECURITY ─────────────────────────────────────
opencode -c "TEMPLATE E + target=authentication + Mode=Read-only"

# ─── F: PERFORMANCE ──────────────────────────────────
opencode -c "TEMPLATE F + target=knowledge/list + SLO p95<200ms"

# ─── G: DOCS ─────────────────────────────────────────
opencode -c "TEMPLATE G + Doc Type=README + module=events"
```

---

## 🛠️ Scripts

```bash
# ─── Windows ─────────────────────────────────────────
create_modules.bat new inventory 3 inv --sql --tests --docs --routes
create_modules.bat template A inventory 3 inv
create_modules.bat sql invoice inv
create_modules.bat routes inventory
create_modules.bat test inventory
create_modules.bat docs inventory
create_modules.bat debug inventory
create_modules.bat all sales 4 sal --force
create_modules.bat help

# ─── Linux / macOS ───────────────────────────────────
./scripts/new_module.sh inventory 3 inv --sql --tests --docs --routes
./scripts/new_module.sh help
```

---

## 🗄️ Database

```bash
# ─── Migration ───────────────────────────────────────
alembic upgrade head                     # apply ทั้งหมด
alembic upgrade +1                       # apply ทีละไฟล์
alembic downgrade -1                     # rollback 1 ไฟล์
alembic history                          # ดู history
alembic current                          # ดู version ปัจจุบัน
alembic revision -m "add column"         # สร้าง migration ใหม่

# ─── psql ────────────────────────────────────────────
psql $DATABASE_URL
\dt tenant_inv.*                         # list tables
\d+ tenant_inv.invoices                  # describe table
\dp tenant_inv.invoices                  # list policies
SHOW app.current_tenant;                 # ดู tenant ปัจจุบัน
SELECT * FROM pg_policies WHERE tablename = 'invoices';
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;   # query plan
```

---

## 🧪 Testing

```bash
# ─── Run ─────────────────────────────────────────────
pytest                                   # ทั้งหมด
pytest -m unit                           # unit
pytest -m integration                    # integration
pytest -m property                       # property
pytest -m "not slow"                     # ข้าม slow
pytest -n auto                           # parallel

# ─── Single ──────────────────────────────────────────
pytest tests/unit/test_inventory.py
pytest tests/unit/test_inventory.py::TestCreate::test_create_sets_defaults
pytest -k "duplicate or invalid"

# ─── Coverage ────────────────────────────────────────
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html:htmlcov
pytest --cov=app --cov-fail-under=85

# ─── Debug ───────────────────────────────────────────
pytest -x                                # stop on first fail
pytest --lf                              # last failed
pytest --ff                              # failed first
pytest -vv --tb=long                     # verbose
pytest -s                                # show stdout
pytest --pdb                             # drop to pdb
pytest --trace                           # step from start
pytest --log-cli-level=DEBUG             # show logs

# ─── Benchmark ───────────────────────────────────────
pytest --benchmark-only
pytest --benchmark-compare=0001
```

---

## 🐛 Debug

```bash
# ─── Run in debug ────────────────────────────────────
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload --log-level debug
PYTHONASYNCIODEBUG=1 PYTHONFAULTHANDLER=1 uvicorn app.main:app

# ─── Redis ───────────────────────────────────────────
redis-cli -p 6380 monitor                # stream commands
redis-cli -p 6380 keys "inv:*"           # list keys
redis-cli -p 6380 get "inv:xxx"          # read key
redis-cli -p 6380 ttl "inv:xxx"          # check TTL
redis-cli -p 6380 info stats             # stats

# ─── Kafka ───────────────────────────────────────────
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic inventory.created \
  --from-beginning

kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group inventory-svc

# ─── Profiling ───────────────────────────────────────
py-spy top --pid $(pgrep -f "uvicorn app.main")
py-spy record -o profile.svg --pid $PID --duration 30
scalene app/main.py
memray run -o out.bin app/main.py
memray flamegraph out.bin

# ─── Network ─────────────────────────────────────────
curl -v http://localhost:8000/api/v1/inventory/
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"code":"INV-001","name":"Test","amount":"100.00"}'

http :8000/api/v1/inventory/            # httpie
http POST :8000/api/v1/inventory/ \
  code=INV-001 name=Test amount=100.00 \
  Idempotency-Key:$(uuidgen)
```

---

## 🔍 Quality

```bash
# ─── Lint ────────────────────────────────────────────
ruff check .                             # lint
ruff check --fix .                       # auto-fix
ruff format .                            # format

# ─── Type ────────────────────────────────────────────
mypy app/                                # type check
mypy --strict app/                       # strict mode

# ─── Security ────────────────────────────────────────
bandit -r app/                           # security scan
pip-audit                                # dependency CVE
safety check                             # alternative

# ─── Pre-commit ──────────────────────────────────────
pre-commit install
pre-commit run --all-files
```

---

## 📦 Dependencies

```bash
# ─── Install ─────────────────────────────────────────
pip install -e ".[test]"                 # editable + test deps
pip install -e ".[dev,test]"             # + dev
uv sync --all-extras                     # uv

# ─── Update ──────────────────────────────────────────
pip list --outdated
pip-compile requirements.in
uv lock --upgrade

# ─── Audit ───────────────────────────────────────────
pip-audit
pip-audit --fix
```

---

## 🚀 Deploy

```bash
# ─── Local ───────────────────────────────────────────
uvicorn app.main:app --reload --port 8000
gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
  --workers 4 --bind 0.0.0.0:8000

# ─── Docker ──────────────────────────────────────────
docker build -t erp-iot:latest .
docker run -p 8000:8000 --env-file .env erp-iot:latest

# ─── Docker Compose ──────────────────────────────────
docker compose up -d
docker compose logs -f app
docker compose down -v
```

---

## 🎯 Universal Header (copy ทั้งก้อน)

```markdown
# ═══════════════════════════════════════════════════════════════
# 🎯 OPENCODE PROMPT — [Module] / [Task A-G]
# ═══════════════════════════════════════════════════════════════

[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน Output Scope
- โค้ดเต็ม Production-ready ห้าม `...`
- คอมเมนต์ 2 ภาษา (TH+EN)
- 3-branch / 2-branch / never-raise
- Decimal / flush() ห้าม commit()
- SQL: V001 + V002 + V003 + RLS
- Routing: app/routes.py + migrations/env.py
- Docs: README + Swagger + Postman
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog เท่านั้น / ห้าม log PII / ห้าม print

### Metadata
- Task: [A-G] | Module: [xxx] | Layer: [0-7]
- Stack: [FastAPI / Django / Both]
- Tests needed? [Yes/No] | Debug kit? [Yes/No]

### Output Scope (23 ส่วน)
01-16: Details → Checklist
17: SQL & Migration (บังคับ)
18: Routing (บังคับ)
19-21: Docs + Swagger + Postman (บังคับ)
22-23: Summary + Report
+ §9 Testing Block: conftest + unit + integration + property + manual
+ §10 Debug Block: log config + context middleware + recipes

# ═══════════════════════════════════════════════════════════════
```

---

## 📋 Quick Reference

| ต้องการ | คำสั่ง |
|---|---|
| สร้าง module ใหม่ | `create_modules.bat new {name} {layer} {prefix} --all` |
| Apply migration | `alembic upgrade head` |
| รัน tests | `pytest -m unit -q` |
| Coverage | `pytest --cov=app --cov-fail-under=85` |
| Lint + format | `ruff check --fix . && ruff format .` |
| Type check | `mypy --strict app/` |
| Security scan | `bandit -r app/ && pip-audit` |
| Debug server | `LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload` |
| Redis monitor | `redis-cli -p 6380 monitor` |
| Profile | `py-spy top --pid $(pgrep -f uvicorn)` |
| Generate prompt | `create_modules.bat template A {name} {layer} {prefix}` |
```

---

# ✅ สรุปไฟล์ทั้ง 11

| # | ไฟล์ | ขนาด | หัวข้อ |
|---|---|---|---|
| 1 | `01-global-constraints.md` | กลาง | กฎเหล็ก · error handling · layers · security |
| 2 | `02-master-structure.md` | กลาง | 23 ส่วน + รายละเอียดแต่ละส่วน |
| 3 | `03-templates-a-g.md` | ใหญ่ | 7 templates เต็ม |
| 4 | `04-sql-migration.md` | กลาง | V001/V002/V003 + debug queries |
| 5 | `05-routing.md` | กลาง | routes.py + routers.py + dependencies.py |
| 6 | `06-docs-postman.md` | กลาง | README + API + Swagger + Postman |
| 7 | `07-reports.md` | กลาง | Report A/B/C/D |
| 8 | `08-checklists.md` | กลาง | DoD + SQL + TDD + Security + Pre-flight |
| 9 | `09-testing.md` | ใหญ่ | Pyramid + conftest + 4 test templates |
| 10 | `10-debug.md` | ใหญ่ | Workflow + structlog + middleware + recipes |
| 11 | `11-cheatsheet.md` | กลาง | ทุกคำสั่งที่ใช้บ่อย |

--- 
