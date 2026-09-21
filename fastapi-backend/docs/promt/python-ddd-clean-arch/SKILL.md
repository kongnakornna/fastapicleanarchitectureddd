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

> Production-ready module generator for **FastAPI + Pydantic v2 + SQLAlchemy 2.0 (async) + PostgreSQL 17 + Redis 8 + Kafka** · ERP + CRM + IoT (65 modules / 8 layers)

---

## 🎯 When to use this skill

| User says | Template | Reference |
|---|---|---|
| "สร้าง module X" / "create module X" | **A** CREATE_NEW | [`03-templates-a-g.md#template-a`](reference/03-templates-a-g.md#template-a) |
| "refactor X" / "ปรับปรุง X" | **B** REFACTOR | [`03-templates-a-g.md#template-b`](reference/03-templates-a-g.md#template-b) |
| "เพิ่ม feature X" / "extend X" | **C** EXTEND | [`03-templates-a-g.md#template-c`](reference/03-templates-a-g.md#template-c) |
| "แก้ bug" / "fix bug X" + stacktrace | **D** BUGFIX | [`03-templates-a-g.md#template-d`](reference/03-templates-a-g.md#template-d) |
| "security audit X" | **E** SECURITY_AUDIT | [`03-templates-a-g.md#template-e`](reference/03-templates-a-g.md#template-e) |
| "ทดสอบ performance X" / SLO | **F** PERF_TEST | [`03-templates-a-g.md#template-f`](reference/03-templates-a-g.md#template-f) |
| "เขียน docs X" / README / ADR | **G** DOCUMENTATION | [`03-templates-a-g.md#template-g`](reference/03-templates-a-g.md#template-g) |
| "เขียน unit test" / "test module" | — | [`09-testing.md`](reference/09-testing.md) |
| "debug module X" / "log ไม่ขึ้น" | — | [`10-debug.md`](reference/10-debug.md) |
| SQL migration / RLS / V001 | — | [`04-sql-migration.md`](reference/04-sql-migration.md) |
| register router / env.py | — | [`05-routing.md`](reference/05-routing.md) |
| OpenAPI / Postman / README | — | [`06-docs-postman.md`](reference/06-docs-postman.md) |
| Report A/B/C/D | — | [`07-reports.md`](reference/07-reports.md) |
| DoD / checklist / pre-flight | — | [`08-checklists.md`](reference/08-checklists.md) |
| คำสั่ง copy-paste ทั้งหมด | — | [`11-cheatsheet.md`](reference/11-cheatsheet.md) |

---

## 🔥 Hard rules (NEVER violate)

```markdown
❌ No greeting, no summary, no repetition in output
❌ No `...` or `# code here` — full production code only
❌ Domain layer MUST NOT import framework (FastAPI / SQLAlchemy / Pydantic / Redis / Kafka / httpx)
❌ Application layer MUST use ports/interfaces only (no infra imports)
❌ NEVER `commit()` in Repository — use `flush()`
❌ Cache NEVER raises — log warning + return None/False
❌ NEVER `float` for money/stock — use `Decimal("...")` only
❌ NEVER `print()` — use `structlog`
❌ NEVER log PII / token / password / Authorization header
❌ NEVER query across tenants (RLS enforced via `set_config`)
❌ NEVER `CREATE TABLE IF NOT EXISTS` in main migration (V001)
❌ NEVER edit committed V001–V003 — create V004+
❌ NEVER return stacktrace to client
❌ NEVER mock what you own — mock only ports
❌ NEVER bypass RLS in tests — use `set_config` to switch tenants
❌ NEVER hardcode tenant IDs — always use `set_config` or context manager for multi-tenant support
❌ NEVER bypass validation — always validate inputs at the boundary of your application (e.g., Pydantic models, request schemas)
❌ NEVER trust client input — always sanitize and validate data coming from external sources
❌ NEVER bypass authentication — always enforce authentication at the boundary of your application (e.g., FastAPI dependencies, middleware)
❌ NEVER bypass authorization — always enforce authorization at the boundary of your application (e.g., FastAPI dependencies, middleware)
❌ NEVER expose sensitive data in logs — always mask or omit PII, tokens, passwords, and Authorization headers
❌ NEVER disable security features (RLS, authentication, authorization) in production — always enforce them rigorously
❌ NEVER expose raw SQL queries or sensitive database information in error messages — always sanitize and handle errors securely
❌ NEVER disable logging in production — always log important events and errors using `structlog`
❌ NEVER expose internal implementation details in API responses — always return sanitized and user-friendly error messages
❌ NEVER ignore errors — always handle exceptions and log them appropriately using `structlog`
❌ NEVER expose stack traces to clients — always return sanitized error messages and log the full stack trace internally
❌ NEVER expose sensitive configuration or environment variables — always keep them secure and do not include them in logs or error messages
❌ NEVER disable input validation — always validate and sanitize all inputs at the boundary of your application (e.g., Pydantic models, request schemas)
❌ NEVER trust client input for security-sensitive operations — always perform server-side checks and validations
