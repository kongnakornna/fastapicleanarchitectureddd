# 07 — Report Templates

> 4 report: A (Completion) · B (Bugfix) · C (Security) · D (Performance)

---

## 📊 Report A: Task Completion {#report-a}

```markdown
# 📋 Task Report — {TaskType} / {Module}

**Date:** YYYY-MM-DD · **Duration:** Xh · **Engineer:** [name]

## ✅ สรุปผล

| รายการ | สถานะ | หมายเหตุ |
|---|---|---|
| Domain | ✅ | 6 ไฟล์ |
| Application | ✅ | 6 ไฟล์ |
| Infrastructure | ✅ | 5 ไฟล์ |
| Presentation | ✅ | 5 ไฟล์ |
| SQL Migrations | ✅ | V001/V002/V003 |
| Routing | ✅ | routes.py + env.py |
| Docs | ✅ | README + API |
| Tests | ✅ | 5 ไฟล์ |
| Coverage | ✅ | ≥ 85% |

## 📁 ไฟล์ที่สร้าง/แก้ไข

| Path | Action | Lines |
|---|---|---|
| `app/modules/{module}/domain/entities.py` | new | 120 |
| `app/modules/{module}/application/use_cases.py` | new | 250 |
| `app/routes.py` | edit | +3 |
| `migrations/env.py` | edit | +2 |
| ... | ... | ... |

## 🧪 Test Result

```
pytest --cov=app.modules.{module}
==================== 42 passed in 3.2s ====================
TOTAL coverage: 91%
```

## 📊 Coverage per Layer

| Layer | Coverage | Target | Pass |
|---|---|---|---|
| domain/ | 97% | 95% | ✅ |
| application/ | 92% | 90% | ✅ |
| infrastructure/ | 83% | 80% | ✅ |
| presentation/ | 74% | 70% | ✅ |
| **รวม** | **91%** | **85%** | ✅ |

## 🚀 Deploy Notes

- Migration: `alembic upgrade head`
- Env vars ใหม่: ไม่มี
- Breaking change: ไม่มี
- Rollback: `alembic downgrade -1`

## ⚠️ Known Issues

- Cache TTL 300s (ยังไม่ tune)
- ยังไม่มี bulk endpoint

## 📝 Follow-up Tasks

- [ ] เพิ่ม bulk create (V004)
- [ ] เพิ่ม Kafka consumer สำหรับ event
- [ ] Benchmark p95 < 100ms
```

---

## 📊 Report B: Bug Fix {#report-b}

```markdown
# 🐛 Bug Fix Report — {bug_id}

**Severity:** 🔴 Critical · **Env:** prod · **Reported:** YYYY-MM-DD

## 🔍 Root Cause

**File:** `app/modules/{module}/application/use_cases.py:142`
**Line:** `entity = await self.repo.save(entity)` — ไม่ได้ flush ก่อน return

**คำอธิบาย:**
Use case return entity ที่ยังไม่ persist → caller พยายามใช้ id ที่ยังเป็น None → 500

## 🛠️ Fix

```diff
- entity = await self.repo.save(entity)
- return entity
+ entity = await self.repo.save(entity)
+ await self.session.flush()
+ fetched = await self.repo.get_by_id(entity.id)  # read-back verify
+ return fetched
```

## 🧪 Regression Test

เพิ่มใน `tests/unit/test_{module}_use_cases.py`:

```python
async def test_readback_verification(self, uc, repo) -> None:
    """TH: ต้องเรียก get_by_id หลัง save | EN: read-back verify"""
    await uc.execute(code="X", name="Y", amount=Decimal("1.00"), idempotency_key="k-1")
    repo.get_by_id.assert_awaited_once()
```

## 📊 Impact

- Users affected: ทั้งหมดที่ใช้ create
- Data loss: ไม่มี (transaction ทำงานถูก)
- Rollback: revert commit `abc123`

## ✅ Verification

- [x] Regression test pass
- [x] Full suite pass
- [x] Smoke test staging pass
- [x] Coverage ไม่ลด
- [x] Deploy production
- [x] Monitor 24h ไม่มี error
```

---

## 📊 Report C: Security Audit {#report-c}

```markdown
# 🔐 Security Audit Report — {scope}

**Date:** YYYY-MM-DD · **Standard:** OWASP Top 10 + ASVS L2
**Mode:** Read-only · **Auditor:** [name]

## Summary

| Severity | Count |
|---|---|
| 🔴 Critical | 0 |
| 🟠 High | 2 |
| 🟡 Medium | 5 |
| 🟢 Low | 3 |
| **รวม** | **10** |

## Findings

| # | Risk | Layer | File:Line | Severity | CWE | แนะนำแก้ | Auto-fix |
|---|---|---|---|---|---|---|---|
| 1 | Missing rate limit on POST | presentation | `routers.py:45` | 🟠 | CWE-770 | เพิ่ม slowapi | ✅ |
| 2 | Token ไม่ rotate | auth | `auth/service.py:88` | 🟠 | CWE-384 | ใช้ refresh rotation | ❌ |
| 3 | Log payload เต็ม (มี email) | application | `use_cases.py:120` | 🟡 | CWE-532 | mask_pii | ✅ |
| 4 | CORS allow * | main | `main.py:30` | 🟡 | CWE-942 | whitelist origin | ✅ |
| 5 | ไม่มี request size limit | main | `main.py:45` | 🟡 | CWE-400 | limit 1MB | ✅ |
| 6 | session cookie ไม่ secure | auth | `auth/router.py:15` | 🟡 | CWE-614 | secure=True | ✅ |
| 7 | ไม่ check tenant_id ใน cache key | infrastructure | `caches.py:22` | 🟡 | CWE-639 | include tenant | ✅ |
| 8 | Dependency เก่า (CVE-2024-XXXX) | deps | `pyproject.toml:18` | 🟢 | CWE-1035 | pip install -U | ✅ |
| 9 | ไม่มี CSP header | main | `main.py:20` | 🟢 | CWE-693 | add CSP | ✅ |
| 10 | Comment เปิดเผย internal path | domain | `entities.py:45` | 🟢 | CWE-200 | ลบ comment | ✅ |

## Checklist Result

```
A. Authentication & Authorization      8/10
B. Input Validation                   9/10
C. Data Protection                    8/10
D. Multi-tenancy                      7/10
E. API Security                       6/10
F. SQL Security                       9/10
G. Dependency                         8/10
```

## Recommendations (Priority Order)

1. **Fix now (High):** #1, #2
2. **Fix this sprint (Medium):** #3, #4, #5, #6, #7
3. **Backlog (Low):** #8, #9, #10
```

---

## 📊 Report D: Performance {#report-d}

```markdown
# ⚡ Performance Report — {target}

**Date:** YYYY-MM-DD · **Tool:** locust + pytest-benchmark
**SLO:** p95 < 200ms, > 100 rps

## Metrics

| Metric | Before | After | Δ | Target | ผ่าน? |
|---|---|---|---|---|---|
| p50 | 85ms | 32ms | -62% | < 50ms | ✅ |
| p95 | 420ms | 148ms | -65% | < 200ms | ✅ |
| p99 | 890ms | 310ms | -65% | < 500ms | ✅ |
| RPS | 45 | 210 | +367% | > 100 | ✅ |
| DB queries/req | 12 | 3 | -75% | < 5 | ✅ |
| Seq scans | 3 | 0 | -100% | 0 | ✅ |
| Cache hit | 0% | 87% | +87 | > 80% | ✅ |
| Memory | 480MB | 210MB | -56% | < 300MB | ✅ |

## Bottleneck Analysis

### Before

```
[████████████████████] DB Query (N+1)       55%
[██████] JSON serialize                     15%
[████] Validation                           12%
[███] Other                                 18%
```

### After

```
[████████] Cache hit                        40%
[████] DB Query (batch)                     20%
[███] JSON serialize                        15%
[███] Validation                            12%
[███] Other                                 13%
```

## Changes

1. **N+1 fix:** ใช้ `selectinload` → 12 queries → 3 queries
2. **Redis cache:** TTL 300s → hit rate 87%
3. **Partial index:** `(tenant_id, status) WHERE deleted_at IS NULL`
4. **Connection pool:** size 10 → 20
5. **Response streaming:** ลด memory 56%

## Load Test Config

```python
# locustfile.py
from locust import HttpUser, task, between

class {Module}User(HttpUser):
    wait_time = between(0.5, 2)

    @task(10)
    def list(self):
        self.client.get("/api/v1/{module}/?limit=20")

    @task(3)
    def create(self):
        self.client.post(
            "/api/v1/{module}/",
            json={"code": f"X-{uuid4()}", "name": "T", "amount": "1.00"},
            headers={"Idempotency-Key": str(uuid4())},
        )
```

**Run:**
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 200 --spawn-rate 20 --run-time 5m --headless
```

## Verification

- [x] Load test 5 นาที ไม่มี error
- [x] p95 < 200ms ตลอดช่วง
- [x] Memory leak: ไม่มี (คงที่ ~210MB)
- [x] DB CPU < 40%
- [x] Redis hit rate > 80%
```
```

--- 
