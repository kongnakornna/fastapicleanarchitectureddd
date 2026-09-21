# 📕 PART 7  — Reconciliation Engine — Extended Edition

> **อัปเดต 3 มิติ:**
> ① Checks: `24 → 46` (+22 ใหม่ รวม 4 category ใหม่: Customer / Supplier / Security / Data)
> ② SLA Matrix: `4 policies → Category × Severity matrix` + Business hours + Thai holidays
> ③ Alert Channels: `12 → 22` (+Zalo, WhatsApp, Messenger, Voice Call, Jira, OpsGenie, Google Chat, ...)

---

## 7.0 สรุป

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        RECONCILIATION                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ① CHECKS  (24 → 46)                                                        │
│     ├─ MONEY        8 → 12  (+4)                                            │
│     ├─ LEDGER       5 → 7   (+2)                                            │
│     ├─ INVENTORY    4 → 7   (+3)                                            │
│     ├─ PRODUCTION   3 → 5   (+2)                                            │
│     ├─ TAX          3 → 5   (+2)                                            │
│     ├─ SYNC         2 → 4   (+2)                                            │
│     ├─ COMPLIANCE   3 → 5   (+2)                                            │
│     ├─ CUSTOMER     0 → 2   (+2)  🆕                                       │
│     ├─ SUPPLIER     0 → 2   (+2)  🆕                                       │
│     ├─ SECURITY     0 → 3   (+3)  🆕                                       │
│     └─ DATA         0 → 3   (+3)  🆕                                       │
│                                                                              │
│  ② SLA MATRIX  (4 policies → 11 categories × 4 severities + context)       │
│     ├─ Category-specific SLA                                                │
│     ├─ Business hours awareness (clock stop)                               │
│     ├─ Thai holidays calendar                                              │
│     ├─ 24/7 vs business-hours categories                                   │
│     └─ Auto-escalation matrix                                              │
│                                                                              │
│  ③ ALERT CHANNELS  (12 → 22)                                               │
│     ├─ Messaging: LINE (3), Zalo, WhatsApp, Messenger, Telegram, Viber,   │
│     │             Google Chat, Mattermost, Slack, Teams, Discord          │
│     ├─ Voice/SMS: SMS, Voice Call                                          │
│     ├─ Email: Email, SES                                                   │
│     ├─ On-call: PagerDuty, OpsGenie                                        │
│     ├─ Ticket: Jira, ServiceNow                                            │
│     ├─ Webhook/API: Generic Webhook, SNS                                   │
│     └─ In-app: In-app, Banner                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# 7.1 Checks v3 — 46 Checks (Full Catalog)

## 7.1.1 Full Catalog Table

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  CHECK CATALOG v3 — 46 checks                                                │
├────────┬──────────────┬──────────┬──────────────────────────────────────────┤
│ CODE   │ CATEGORY     │ SEVERITY │ จับอะไร                                  │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── MONEY (12) ───────────────────────────────────────────────────────    │
│ MONEY.001  │ TAX      │ CRITICAL │ Invoice VAT mismatch                     │
│ MONEY.002  │ MONEY    │ HIGH     │ Overcharge vs pricing master             │
│ MONEY.003  │ DATA     │ CRITICAL │ Duplicate invoice number                 │
│ MONEY.004  │ MONEY    │ CRITICAL │ Payment over-allocation                  │
│ MONEY.005  │ MONEY    │ CRITICAL │ Invoice paid ≠ Σ payment                 │
│ MONEY.006  │ MONEY    │ HIGH     │ Payment allocated to wrong customer      │
│ MONEY.007  │ MONEY    │ MEDIUM   │ Credit note without parent invoice       │
│ MONEY.008  │ MONEY    │ MEDIUM   │ Invoice aging > 90 days                  │
│ MONEY.009  │ MONEY    │ HIGH     │ 🆕 Duplicate invoice for same order     │
│ MONEY.010  │ MONEY    │ CRITICAL │ 🆕 Duplicate payment (same reference)   │
│ MONEY.011  │ MONEY    │ CRITICAL │ 🆕 Refund > original payment            │
│ MONEY.012  │ MONEY    │ CRITICAL │ 🆕 Credit note > original invoice       │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── LEDGER (7) ────────────────────────────────────────────────────────   │
│ LEDGER.001 │ LEDGER   │ CRITICAL │ Orphan ledger entries                    │
│ LEDGER.002 │ LEDGER   │ CRITICAL │ Unbalanced journals                      │
│ LEDGER.003 │ LEDGER   │ HIGH     │ Journal in closed period                 │
│ LEDGER.004 │ LEDGER   │ HIGH     │ Duplicate journal from same source       │
│ LEDGER.005 │ LEDGER   │ CRITICAL │ Missing journal for invoice              │
│ LEDGER.006 │ LEDGER   │ MEDIUM   │ 🆕 Journal without source reference     │
│ LEDGER.007 │ LEDGER   │ HIGH     │ 🆕 Account code ≠ account type          │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── INVENTORY (7) ─────────────────────────────────────────────────────   │
│ INVENTORY.001 │ INV   │ HIGH     │ Stock balance ≠ Σ movements             │
│ INVENTORY.002 │ INV   │ MEDIUM   │ Expired lot with balance                 │
│ INVENTORY.003 │ INV   │ CRITICAL │ Negative stock                            │
│ INVENTORY.004 │ INV   │ MEDIUM   │ Movement without reference                │
│ INVENTORY.005 │ INV   │ MEDIUM   │ 🆕 Movement timestamp anomaly           │
│ INVENTORY.006 │ INV   │ HIGH     │ 🆕 Lot without warehouse assignment     │
│ INVENTORY.007 │ INV   │ CRITICAL │ 🆕 Duplicate lot number                 │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── PRODUCTION (5) ────────────────────────────────────────────────────   │
│ PRODUCTION.001 │ PROD │ HIGH     │ Batch yield mismatch                    │
│ PRODUCTION.002 │ PROD │ MEDIUM   │ Batch open > 24h                        │
│ PRODUCTION.003 │ PROD │ MEDIUM   │ BOM variance                            │
│ PRODUCTION.004 │ PROD │ HIGH     │ 🆕 Batch without active recipe          │
│ PRODUCTION.005 │ PROD │ MEDIUM   │ 🆕 Waste > threshold                    │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── TAX (5) ───────────────────────────────────────────────────────────    │
│ TAX.001    │ TAX      │ HIGH     │ VAT rate violation                       │
│ TAX.002    │ TAX      │ HIGH     │ WHT mismatch                             │
│ TAX.003    │ TAX      │ MEDIUM   │ e-Tax deadline                           │
│ TAX.004    │ TAX      │ HIGH     │ 🆕 VAT rate mismatch header vs line     │
│ TAX.005    │ TAX      │ CRITICAL │ 🆕 e-Tax rejected by Revenue Dept       │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── SYNC (4) ──────────────────────────────────────────────────────────   │
│ SYNC.001   │ SYNC     │ HIGH     │ DB ↔ Cloud mismatch                      │
│ SYNC.002   │ SYNC     │ MEDIUM   │ Cloud orphan                             │
│ SYNC.003   │ SYNC     │ HIGH     │ 🆕 Dead letter sync count > threshold   │
│ SYNC.004   │ SYNC     │ MEDIUM   │ 🆕 Sync latency > 1 hour                │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── COMPLIANCE (5) ────────────────────────────────────────────────────   │
│ COMPLIANCE.001 │ CMPL │ HIGH     │ Missing tax ID                           │
│ COMPLIANCE.002 │ CMPL │ MEDIUM   │ Invoice number gap                       │
│ COMPLIANCE.003 │ CMPL │ HIGH     │ Missing audit log                        │
│ COMPLIANCE.004 │ CMPL │ HIGH     │ 🆕 Invoice voided without audit         │
│ COMPLIANCE.005 │ CMPL │ MEDIUM   │ 🆕 Data retention violation             │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── 🆕 CUSTOMER (2) ──────────────────────────────────────────────────   │
│ CUSTOMER.001 │ CUST  │ HIGH     │ Credit limit exceeded                     │
│ CUSTOMER.002 │ CUST  │ MEDIUM   │ Duplicate customer (same tax ID)          │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── 🆕 SUPPLIER (2) ──────────────────────────────────────────────────   │
│ SUPPLIER.001 │ SUPP  │ MEDIUM   │ Duplicate supplier (same tax ID)          │
│ SUPPLIER.002 │ SUPP  │ HIGH     │ Supplier invoice mismatch vs PO           │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── 🆕 SECURITY (3) ──────────────────────────────────────────────────   │
│ SECURITY.001 │ SEC   │ HIGH     │ Unusual login pattern                     │
│ SECURITY.002 │ SEC   │ CRITICAL │ Permission escalation without approval    │
│ SECURITY.003 │ SEC   │ MEDIUM   │ API key unused > 90 days                  │
├────────┼──────────────┼──────────┼──────────────────────────────────────────┤
│ ────── 🆕 DATA (3) ──────────────────────────────────────────────────────   │
│ DATA.001   │ DATA     │ HIGH     │ Orphan foreign key                        │
│ DATA.002   │ DATA     │ MEDIUM   │ Null in required field                    │
│ DATA.003   │ DATA     │ MEDIUM   │ Invalid format (email/phone/tax_id)       │
└────────┴──────────────┴──────────┴──────────────────────────────────────────┘
```

## 7.1.2 🆕 SECURITY.002 — Permission Escalation

```python
# app/modules/reconciliation/domain/checks/security_002_permission_escalation.py

from uuid import UUID
from sqlalchemy import text

from app.modules.reconciliation.domain.checks.base import (
    BaseCheck, CheckResult, register_check,
)
from app.modules.reconciliation.domain.value_objects import (
    CheckCode, CheckCategory, CheckSeverity, CheckEvidence,
)


@register_check
class CheckPermissionEscalation(BaseCheck):
    """
    SECURITY.002 — มีการให้สิทธิ์ user โดยไม่ผ่าน approval

    🚨 อันตราย: user ที่ได้ role admin โดยไม่มี audit trail ของ approver
    """

    code = CheckCode("SECURITY.002")
    category = CheckCategory.SECURITY
    severity = CheckSeverity.CRITICAL
    name = "Permission escalation without approval"
    description = "user ได้ role/permission โดยไม่มี approval + audit"

    async def run(self, company_id: UUID) -> list[CheckResult]:
        sql = text("""
            SELECT
                ucr.user_id,
                ucr.company_id,
                ucr.role_id,
                r.name AS role_name,
                ucr.assigned_at,
                ucr.assigned_by,
                u.username,
                al.id AS audit_id,
                al.action AS audit_action,
                al.actor_id AS audit_actor
            FROM app_user_company_roles ucr
            JOIN app_users u ON u.id = ucr.user_id
            JOIN app_roles r ON r.id = ucr.role_id
            LEFT JOIN audit_log al
                ON al.entity_type = 'user'
               AND al.entity_id = ucr.user_id
               AND al.action = 'permission.changed'
               AND al.occurred_at BETWEEN ucr.assigned_at - INTERVAL '5 min'
                                       AND ucr.assigned_at + INTERVAL '5 min'
            WHERE ucr.company_id = :cid
              AND r.name IN ('admin', 'super_admin', 'manager')
              AND (ucr.assigned_by IS NULL OR al.id IS NULL)
        """)
        rows = (await self.session.execute(sql, {"cid": company_id})).mappings()

        results: list[CheckResult] = []
        for r in rows:
            reason = (
                "no_assigner" if r["assigned_by"] is None
                else "no_audit_trail"
            )
            results.append(CheckResult(
                entity_type="user_role",
                entity_id=f"{r['user_id']}:{r['role_id']}",
                evidence=CheckEvidence(
                    entity_type="user_role",
                    entity_id=f"{r['user_id']}:{r['role_id']}",
                    snapshot={
                        "username": r["username"],
                        "role_name": r["role_name"],
                        "assigned_at": r["assigned_at"].isoformat(),
                        "assigned_by": str(r["assigned_by"]) if r["assigned_by"] else None,
                        "audit_id": str(r["audit_id"]) if r["audit_id"] else None,
                    },
                    computed_value=None,
                    expected_value="audit + approver",
                    diff=None,
                    extra={
                        "reason": reason,
                        "action_required": "investigate_privilege_escalation",
                        "security_incident": True,
                    },
                ),
                fingerprint=CheckResult.fingerprint_of(
                    self.code.value, "user_role",
                    f"{r['user_id']}:{r['role_id']}",
                    reason=reason,
                ),
            ))
        return results
```

## 7.1.3 🆕 MONEY.009 — Duplicate Invoice for Same Order

```python
# app/modules/reconciliation/domain/checks/money_009_duplicate_order.py

@register_check
class CheckDuplicateInvoiceForOrder(BaseCheck):
    """
    MONEY.009 — Order เดียวออก invoice หลายใบ (ไม่ใช่ credit note)

    🚨 ลูกค้าถูกเก็บซ้ำ
    """

    code = CheckCode("MONEY.009")
    category = CheckCategory.MONEY
    severity = CheckSeverity.HIGH
    name = "Duplicate invoice for same order"
    description = "Order เดียวออก invoice > 1 ใบ (ที่ไม่ใช่ credit/debit note)"

    async def run(self, company_id: UUID) -> list[CheckResult]:
        sql = text("""
            SELECT
                i.order_id,
                COUNT(*) AS invoice_count,
                ARRAY_AGG(i.id) AS invoice_ids,
                ARRAY_AGG(i.invoice_number) AS invoice_numbers,
                ARRAY_AGG(i.status) AS statuses,
                SUM(i.grand_total) AS total_amount
            FROM invoices i
            WHERE i.company_id = :cid
              AND i.order_id IS NOT NULL
              AND i.invoice_type NOT IN ('credit_note', 'debit_note')
              AND i.status NOT IN ('cancelled')
            GROUP BY i.order_id
            HAVING COUNT(*) > 1
        """)
        rows = (await self.session.execute(sql, {"cid": company_id})).mappings()

        results: list[CheckResult] = []
        for r in rows:
            results.append(CheckResult(
                entity_type="order",
                entity_id=str(r["order_id"]),
                evidence=CheckEvidence(
                    entity_type="order",
                    entity_id=str(r["order_id"]),
                    snapshot={
                        "order_id": str(r["order_id"]),
                        "invoice_count": r["invoice_count"],
                        "invoice_ids": [str(i) for i in r["invoice_ids"]],
                        "invoice_numbers": list(r["invoice_numbers"]),
                        "statuses": list(r["statuses"]),
                        "total_amount": str(r["total_amount"]),
                    },
                    computed_value=str(r["invoice_count"]),
                    expected_value="1",
                    diff=f"+{int(r['invoice_count']) - 1}",
                    extra={
                        "action_required": "cancel_duplicate_or_reclassify",
                        "total_overcharge": str(r["total_amount"]),
                    },
                ),
                fingerprint=CheckResult.fingerprint_of(
                    self.code.value, "order", str(r["order_id"]),
                ),
            ))
        return results
```

## 7.1.4 🆕 DATA.001 — Orphan Foreign Keys

```python
# app/modules/reconciliation/domain/checks/data_001_orphan_fk.py

@register_check
class CheckOrphanForeignKey(BaseCheck):
    """
    DATA.001 — Foreign key ชี้ไป record ที่ไม่มีจริง

    🚨 DB ที่ไม่มี FK constraint จริง หรือ FK ถูก disable
    """

    code = CheckCode("DATA.001")
    category = CheckCategory.DATA_INTEGRITY
    severity = CheckSeverity.HIGH
    name = "Orphan foreign key"
    description = "FK reference ชี้ record ที่ไม่มีอยู่"

    # table → (fk_column, parent_table, parent_column)
    FK_CHECKS: list[tuple[str, str, str, str]] = [
        ("invoice_lines", "invoice_id", "invoices", "id"),
        ("invoice_lines", "product_id", "products", "id"),
        ("payment_allocations", "payment_id", "payments", "id"),
        ("payment_allocations", "invoice_id", "invoices", "id"),
        ("ledger_lines", "journal_id", "journal_entries", "id"),
        ("stock_movements", "product_id", "products", "id"),
        ("stock_movements", "warehouse_id", "warehouses", "id"),
        ("production_batches", "recipe_id", "recipes", "id"),
    ]

    async def run(self, company_id: UUID) -> list[CheckResult]:
        results: list[CheckResult] = []

        for child_table, fk_col, parent_table, parent_col in self.FK_CHECKS:
            sql = text(f"""
                SELECT c.id, c.{fk_col} AS fk_value
                FROM {child_table} c
                LEFT JOIN {parent_table} p ON p.{parent_col} = c.{fk_col}
                WHERE c.company_id = :cid
                  AND c.{fk_col} IS NOT NULL
                  AND p.{parent_col} IS NULL
                LIMIT 100
            """)
            rows = (await self.session.execute(
                sql, {"cid": company_id},
            )).mappings()

            for r in rows:
                results.append(CheckResult(
                    entity_type=child_table,
                    entity_id=str(r["id"]),
                    evidence=CheckEvidence(
                        entity_type=child_table,
                        entity_id=str(r["id"]),
                        snapshot={
                            "child_table": child_table,
                            "fk_column": fk_col,
                            "fk_value": str(r["fk_value"]),
                            "parent_table": parent_table,
                        },
                        computed_value=None,
                        expected_value=f"exists in {parent_table}",
                        diff=None,
                        extra={
                            "action_required": "fix_or_delete_orphan",
                            "fk_definition": f"{child_table}.{fk_col} → {parent_table}.{parent_col}",
                        },
                    ),
                    fingerprint=CheckResult.fingerprint_of(
                        self.code.value, child_table, str(r["id"]),
                        fk=fk_col, value=str(r["fk_value"]),
                    ),
                ))
        return results
```

## 7.1.5 🆕 TAX.004 — VAT Rate Mismatch Header vs Line

```python
# app/modules/reconciliation/domain/checks/tax_004_vat_rate_mismatch.py

@register_check
class CheckVatRateMismatchHeaderLine(BaseCheck):
    """
    TAX.004 — VAT rate ใน header ≠ rate ใน line

    ถ้า invoice มี line หลายอัตรา → header ต้องเป็น "mixed"
    """

    code = CheckCode("TAX.004")
    category = CheckCategory.TAX
    severity = CheckSeverity.HIGH
    name = "VAT rate mismatch header vs line"
    description = "VAT rate ที่ header ไม่ตรงกับ line"

    async def run(self, company_id: UUID) -> list[CheckResult]:
        sql = text("""
            SELECT
                i.id, i.invoice_number, i.status,
                i.vat_total, i.subtotal,
                ARRAY_AGG(DISTINCT il.vat_rate) AS line_vat_rates,
                COUNT(DISTINCT il.vat_rate) AS distinct_rates,
                ARRAY_AGG(DISTINCT il.vat_mode) AS line_vat_modes
            FROM invoices i
            JOIN invoice_lines il ON il.invoice_id = i.id
            WHERE i.company_id = :cid
              AND i.status IN ('issued', 'partially_paid', 'paid')
            GROUP BY i.id
            HAVING COUNT(DISTINCT il.vat_rate) > 1
               AND COUNT(DISTINCT il.vat_mode) = 1
        """)
        rows = (await self.session.execute(sql, {"cid": company_id})).mappings()

        results: list[CheckResult] = []
        for r in rows:
            results.append(CheckResult(
                entity_type="invoice",
                entity_id=str(r["id"]),
                evidence=CheckEvidence(
                    entity_type="invoice",
                    entity_id=str(r["id"]),
                    snapshot={
                        "invoice_number": r["invoice_number"],
                        "status": r["status"],
                        "line_vat_rates": [str(x) for x in r["line_vat_rates"]],
                        "distinct_rate_count": r["distinct_rates"],
                        "subtotal": str(r["subtotal"]),
                        "vat_total": str(r["vat_total"]),
                    },
                    computed_value=f"{r['distinct_rates']} distinct rates",
                    expected_value="1 rate or mixed-mode",
                    diff=None,
                    extra={
                        "action_required": "review_tax_rates",
                        "note": "invoice ควรใช้ rate เดียว หรือต้อง handle mixed",
                    },
                ),
                fingerprint=CheckResult.fingerprint_of(
                    self.code.value, "invoice", str(r["id"]),
                    rate_count=str(r["distinct_rates"]),
                ),
            ))
        return results
```

## 7.1.6 🆕 CUSTOMER.001 — Credit Limit Exceeded

```python
# app/modules/reconciliation/domain/checks/customer_001_credit_limit.py

@register_check
class CheckCreditLimitExceeded(BaseCheck):
    """
    CUSTOMER.001 — ลูกค้าเกินวงเงินเครดิต

    Business rule — ไม่ใช่ data error แต่เป็น signal ทางธุรกิจ
    """

    code = CheckCode("CUSTOMER.001")
    category = CheckCategory.CUSTOMER
    severity = CheckSeverity.HIGH
    name = "Customer credit limit exceeded"
    description = "ยอดค้างชำระของลูกค้าเกิน credit limit"

    async def run(self, company_id: UUID) -> list[CheckResult]:
        sql = text("""
            SELECT
                c.id, c.code, c.name,
                c.credit_limit,
                COALESCE(SUM(
                    CASE WHEN i.status IN ('issued', 'partially_paid')
                         THEN i.grand_total - COALESCE(paid.total_paid, 0)
                         ELSE 0
                    END
                ), 0) AS total_outstanding
            FROM customers c
            LEFT JOIN invoices i ON i.customer_id = c.id
                AND i.company_id = c.company_id
            LEFT JOIN LATERAL (
                SELECT COALESCE(SUM(pa.allocated_amount), 0) AS total_paid
                FROM payment_allocations pa
                WHERE pa.invoice_id = i.id
            ) paid ON TRUE
            WHERE c.company_id = :cid
              AND c.credit_limit IS NOT NULL
              AND c.credit_limit > 0
            GROUP BY c.id, c.code, c.name, c.credit_limit
            HAVING COALESCE(SUM(
                    CASE WHEN i.status IN ('issued', 'partially_paid')
                         THEN i.grand_total - COALESCE(paid.total_paid, 0)
                         ELSE 0
                    END
                ), 0) > c.credit_limit
        """)
        rows = (await self.session.execute(sql, {"cid": company_id})).mappings()

        results: list[CheckResult] = []
        for r in rows:
            usage_pct = (
                Decimal(str(r["total_outstanding"]))
                / Decimal(str(r["credit_limit"]))
                * 100
            ).quantize(Decimal("0.01"))

            results.append(CheckResult(
                entity_type="customer",
                entity_id=str(r["id"]),
                evidence=CheckEvidence(
                    entity_type="customer",
                    entity_id=str(r["id"]),
                    snapshot={
                        "customer_code": r["code"],
                        "customer_name": r["name"],
                        "credit_limit": str(r["credit_limit"]),
                        "total_outstanding": str(r["total_outstanding"]),
                        "usage_pct": str(usage_pct),
                    },
                    computed_value=str(r["total_outstanding"]),
                    expected_value=f"<= {r['credit_limit']}",
                    diff=str(
                        Decimal(str(r["total_outstanding"]))
                        - Decimal(str(r["credit_limit"]))
                    ),
                    extra={
                        "usage_pct": str(usage_pct),
                        "action_required": "hold_new_orders_or_request_approval",
                    },
                ),
                fingerprint=CheckResult.fingerprint_of(
                    self.code.value, "customer", str(r["id"]),
                ),
            ))
        return results
```

## 7.1.7 🆕 SYNC.003 — Dead Letter Count

```python
# app/modules/reconciliation/domain/checks/sync_003_dead_letter.py

@register_check
class CheckDeadLetterSyncCount(BaseCheck):
    """
    SYNC.003 — มี sync jobs ที่ dead letter เกิน threshold
    """

    code = CheckCode("SYNC.003")
    category = CheckCategory.SYNC
    severity = CheckSeverity.HIGH
    name = "Sync dead letter count"
    description = "sync jobs ที่ dead letter เกิน threshold"

    THRESHOLD = 10

    async def run(self, company_id: UUID) -> list[CheckResult]:
        sql = text("""
            SELECT
                provider,
                COUNT(*) AS dead_count,
                MIN(created_at) AS oldest,
                ARRAY_AGG(DISTINCT entity_type) AS entity_types
            FROM sync_jobs
            WHERE company_id = :cid
              AND status = 'dead_letter'
            GROUP BY provider
            HAVING COUNT(*) >= :threshold
        """)
        rows = (await self.session.execute(
            sql, {"cid": company_id, "threshold": self.THRESHOLD},
        )).mappings()

        results: list[CheckResult] = []
        for r in rows:
            results.append(CheckResult(
                entity_type="sync_provider",
                entity_id=r["provider"],
                evidence=CheckEvidence(
                    entity_type="sync_provider",
                    entity_id=r["provider"],
                    snapshot={
                        "provider": r["provider"],
                        "dead_count": r["dead_count"],
                        "oldest": r["oldest"].isoformat(),
                        "entity_types": list(r["entity_types"]),
                    },
                    computed_value=str(r["dead_count"]),
                    expected_value=f"< {self.THRESHOLD}",
                    diff=f"+{int(r['dead_count']) - self.THRESHOLD}",
                    extra={
                        "action_required": "investigate_and_manual_retry",
                    },
                ),
                fingerprint=CheckResult.fingerprint_of(
                    self.code.value, "provider", r["provider"],
                ),
            ))
        return results
```

## 7.1.8 Check Registry — Updated

```python
# app/modules/reconciliation/domain/checks/__init__.py

"""
Check Catalog v3 — 46 checks
"""

# Money (12)
from .money_001_invoice_vat import CheckInvoiceVatMismatch
from .money_002_overcharge import CheckOvercharge
from .money_003_duplicate_invoice import CheckDuplicateInvoiceNumber
from .money_004_over_allocation import CheckPaymentOverAllocation
from .money_005_paid_mismatch import CheckInvoicePaidMismatch
from .money_006_wrong_customer import CheckPaymentWrongCustomer
from .money_007_orphan_credit_note import CheckOrphanCreditNote
from .money_008_aging import CheckInvoiceAging
from .money_009_duplicate_order import CheckDuplicateInvoiceForOrder
from .money_010_duplicate_payment import CheckDuplicatePayment
from .money_011_refund_exceed import CheckRefundExceeds
from .money_012_credit_note_exceed import CheckCreditNoteExceeds

# Ledger (7)
from .ledger_001_orphan import CheckOrphanLedgerEntries
from .ledger_002_unbalanced import CheckUnbalancedJournals
from .ledger_003_closed_period import CheckClosedPeriodViolation
from .ledger_004_duplicate_journal import CheckDuplicateJournal
from .ledger_005_missing_journal import CheckMissingJournalForInvoice
from .ledger_006_no_source import CheckJournalWithoutSource
from .ledger_007_account_type import CheckAccountTypeMismatch

# Inventory (7)
from .inventory_001_balance import CheckStockBalanceMismatch
from .inventory_002_expired_lot import CheckExpiredLotBalance
from .inventory_003_negative import CheckNegativeStock
from .inventory_004_no_reference import CheckMovementNoReference
from .inventory_005_timestamp import CheckMovementTimestampAnomaly
from .inventory_006_lot_no_warehouse import CheckLotWithoutWarehouse
from .inventory_007_duplicate_lot import CheckDuplicateLotNumber

# Production (5)
from .production_001_yield import CheckBatchYieldMismatch
from .production_002_long_open import CheckLongOpenBatch
from .production_003_bom import CheckBomVariance
from .production_004_no_recipe import CheckBatchWithoutRecipe
from .production_005_waste import CheckWasteThreshold

# Tax (5)
from .tax_001_vat_rate import CheckVatRateViolation
from .tax_002_wht_mismatch import CheckWhtMismatch
from .tax_003_etax_deadline import CheckETaxDeadline
from .tax_004_rate_mismatch import CheckVatRateMismatchHeaderLine
from .tax_005_etax_rejected import CheckETaxRejected

# Sync (4)
from .sync_001_cloud_mismatch import CheckSyncMismatch
from .sync_002_reverse import CheckCloudOrphan
from .sync_003_dead_letter import CheckDeadLetterSyncCount
from .sync_004_latency import CheckSyncLatency

# Compliance (5)
from .compliance_001_tax_id import CheckMissingTaxId
from .compliance_002_number_gap import CheckInvoiceNumberGap
from .compliance_003_missing_audit import CheckMissingAuditLog
from .compliance_004_void_no_audit import CheckVoidWithoutAudit
from .compliance_005_retention import CheckDataRetentionViolation

# 🆕 Customer (2)
from .customer_001_credit_limit import CheckCreditLimitExceeded
from .customer_002_duplicate import CheckDuplicateCustomer

# 🆕 Supplier (2)
from .supplier_001_duplicate import CheckDuplicateSupplier
from .supplier_002_po_mismatch import CheckSupplierInvoiceMismatch

# 🆕 Security (3)
from .security_001_login_pattern import CheckUnusualLoginPattern
from .security_002_permission_escalation import CheckPermissionEscalation
from .security_003_stale_api_key import CheckStaleApiKey

# 🆕 Data (3)
from .data_001_orphan_fk import CheckOrphanForeignKey
from .data_002_null_required import CheckNullInRequiredField
from .data_003_invalid_format import CheckInvalidFormat
```

---

# 7.2 SLA Matrix v3 — Category × Severity + Context

## 7.2.1 Design Principles

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  SLA DESIGN v3                                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Category-aware: MONEY/TAX ต้องเร็วกว่า INVENTORY/PRODUCTION             │
│  2. Severity-aware: CRITICAL ต้องเร็วกว่า HIGH                              │
│  3. Business hours:                                                          │
│     ├─ 24/7: MONEY, TAX, LEDGER, SYNC, SECURITY                             │
│     └─ Business hours: INVENTORY, PRODUCTION, CUSTOMER, SUPPLIER,           │
│                        DATA, COMPLIANCE                                      │
│  4. Thai holidays: หยุด clock ในวันหยุดราชการ                               │
│  5. Clock stop: หยุดนับนอกเวลาทำการ (สำหรับ business-hours categories)      │
│  6. Auto-escalation: escalate ถ้าใกล้ breach                                 │
│  7. Weekend: SECURITY = 24/7, อื่น ๆ = business hours                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 7.2.2 SLA Matrix — Full Table

```python
# app/modules/reconciliation/domain/value_objects.py (revised)

from dataclasses import dataclass
from datetime import timedelta, time
from enum import Enum


class SlaTimeUnit(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


@dataclass(frozen=True, slots=True)
class SlaRule:
    """
    SLA rule — respond / resolve / escalate timings
    """
    respond: timedelta
    resolve: timedelta
    escalate: timedelta
    clock_mode: str          # "24/7" | "business_hours"
    escalate_chain: int      # จำนวน level สูงสุด


# ============================================================
# SLA MATRIX v3 — Category × Severity
# ============================================================

SLA_MATRIX_V3: dict[str, dict[str, SlaRule]] = {
    # ───── MONEY — 24/7, เร็วมาก ─────
    "money": {
        "critical": SlaRule(
            respond=timedelta(minutes=15),
            resolve=timedelta(hours=2),
            escalate=timedelta(minutes=30),
            clock_mode="24/7",
            escalate_chain=4,
        ),
        "high": SlaRule(
            respond=timedelta(minutes=30),
            resolve=timedelta(hours=8),
            escalate=timedelta(hours=2),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=3),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=14),
            escalate=timedelta(days=7),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── TAX — 24/7, deadline กฎหมาย ─────
    "tax": {
        "critical": SlaRule(
            respond=timedelta(minutes=15),
            resolve=timedelta(hours=4),
            escalate=timedelta(minutes=30),
            clock_mode="24/7",
            escalate_chain=4,
        ),
        "high": SlaRule(
            respond=timedelta(hours=1),
            resolve=timedelta(hours=12),
            escalate=timedelta(hours=3),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=5),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=30),
            escalate=timedelta(days=10),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── LEDGER — 24/7 (ปิดงบ) ─────
    "ledger": {
        "critical": SlaRule(
            respond=timedelta(minutes=30),
            resolve=timedelta(hours=4),
            escalate=timedelta(hours=1),
            clock_mode="24/7",
            escalate_chain=4,
        ),
        "high": SlaRule(
            respond=timedelta(hours=1),
            resolve=timedelta(hours=12),
            escalate=timedelta(hours=4),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=5),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=30),
            escalate=timedelta(days=10),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── SECURITY — 24/7, เร็วที่สุด ─────
    "security": {
        "critical": SlaRule(
            respond=timedelta(minutes=5),
            resolve=timedelta(hours=1),
            escalate=timedelta(minutes=15),
            clock_mode="24/7",
            escalate_chain=4,
        ),
        "high": SlaRule(
            respond=timedelta(minutes=15),
            resolve=timedelta(hours=4),
            escalate=timedelta(minutes=45),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(days=2),
            escalate=timedelta(hours=12),
            clock_mode="24/7",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(hours=12),
            resolve=timedelta(days=7),
            escalate=timedelta(days=3),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── SYNC — 24/7 ─────
    "sync": {
        "critical": SlaRule(
            respond=timedelta(minutes=15),
            resolve=timedelta(hours=2),
            escalate=timedelta(minutes=30),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(minutes=30),
            resolve=timedelta(hours=6),
            escalate=timedelta(hours=2),
            clock_mode="24/7",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(days=2),
            escalate=timedelta(hours=12),
            clock_mode="24/7",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(hours=12),
            resolve=timedelta(days=7),
            escalate=timedelta(days=3),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── INVENTORY — business hours ─────
    "inventory": {
        "critical": SlaRule(
            respond=timedelta(hours=1),
            resolve=timedelta(hours=6),
            escalate=timedelta(hours=2),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(hours=24),
            escalate=timedelta(hours=8),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=8),
            resolve=timedelta(days=5),
            escalate=timedelta(days=2),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=2),
            resolve=timedelta(days=30),
            escalate=timedelta(days=10),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── PRODUCTION — business hours ─────
    "production": {
        "critical": SlaRule(
            respond=timedelta(hours=1),
            resolve=timedelta(hours=8),
            escalate=timedelta(hours=3),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(hours=3),
            resolve=timedelta(hours=24),
            escalate=timedelta(hours=12),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(hours=12),
            resolve=timedelta(days=7),
            escalate=timedelta(days=3),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=3),
            resolve=timedelta(days=30),
            escalate=timedelta(days=14),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── CUSTOMER / SUPPLIER — business hours ─────
    "customer": {
        "critical": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(hours=12),
            escalate=timedelta(hours=6),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=2),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "medium": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=7),
            escalate=timedelta(days=3),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=3),
            resolve=timedelta(days=30),
            escalate=timedelta(days=14),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },
    "supplier": {
        "critical": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(hours=12),
            escalate=timedelta(hours=6),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=2),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "medium": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=7),
            escalate=timedelta(days=3),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=3),
            resolve=timedelta(days=30),
            escalate=timedelta(days=14),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── COMPLIANCE — business hours ─────
    "compliance": {
        "critical": SlaRule(
            respond=timedelta(hours=4),
            resolve=timedelta(days=2),
            escalate=timedelta(hours=12),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=7),
            escalate=timedelta(days=2),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "medium": SlaRule(
            respond=timedelta(days=3),
            resolve=timedelta(days=30),
            escalate=timedelta(days=10),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=7),
            resolve=timedelta(days=90),
            escalate=timedelta(days=30),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },

    # ───── DATA — business hours ─────
    "data": {
        "critical": SlaRule(
            respond=timedelta(hours=2),
            resolve=timedelta(hours=12),
            escalate=timedelta(hours=6),
            clock_mode="business_hours",
            escalate_chain=3,
        ),
        "high": SlaRule(
            respond=timedelta(hours=6),
            resolve=timedelta(days=3),
            escalate=timedelta(days=1),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "medium": SlaRule(
            respond=timedelta(days=1),
            resolve=timedelta(days=14),
            escalate=timedelta(days=5),
            clock_mode="business_hours",
            escalate_chain=2,
        ),
        "low": SlaRule(
            respond=timedelta(days=5),
            resolve=timedelta(days=60),
            escalate=timedelta(days=21),
            clock_mode="business_hours",
            escalate_chain=1,
        ),
    },
}
```

## 7.2.3 Business Calendar & Clock

```python
# app/modules/reconciliation/domain/business_calendar.py

from dataclasses import dataclass
from datetime import datetime, time, timedelta, date
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BusinessHours:
    start: time = time(8, 30)
    end: time = time(18, 0)
    weekend: frozenset[int] = frozenset({5, 6})  # Sat=5, Sun=6


@dataclass(frozen=True, slots=True)
class Holiday:
    date: date
    name: str
    is_recurring: bool = False   # ตรงทุกปี


class BusinessCalendar:
    """
    ปฏิทินธุรกิจ — เวลาทำการ + วันหยุดไทย

    ใช้กับ SLA clock_mode="business_hours"
    """

    def __init__(
        self,
        *,
        hours: BusinessHours | None = None,
        holidays: Iterable[Holiday] = (),
        timezone: str = "Asia/Bangkok",
    ):
        self.hours = hours or BusinessHours()
        self.holidays = {
            h.date if not h.is_recurring else None for h in holidays
            if not h.is_recurring
        }
        self._recurring_holidays: dict[tuple[int, int], str] = {}
        for h in holidays:
            if h.is_recurring:
                self._recurring_holidays[(h.date.month, h.date.day)] = h.name
        self.timezone = timezone

    # ---------- Checks ----------

    def is_holiday(self, d: date) -> bool:
        if d in self.holidays:
            return True
        return (d.month, d.day) in self._recurring_holidays

    def is_working_day(self, d: date) -> bool:
        if d.weekday() in self.hours.weekend:
            return False
        return not self.is_holiday(d)

    def is_within_business_hours(self, dt: datetime) -> bool:
        if not self.is_working_day(dt.date()):
            return False
        return self.hours.start <= dt.time() < self.hours.end

    # ---------- Clock arithmetic ----------

    def add_business_hours(
        self, start: datetime, hours: float,
    ) -> datetime:
        """
        บวก hours ใน business hours context
        (ข้ามวันหยุด/นอกเวลา)
        """
        remaining = timedelta(hours=hours)
        current = start

        # ถ้าเริ่มนอกเวลา → jump ไปเวลาเปิดถัดไป
        if not self.is_within_business_hours(current):
            current = self._next_business_open(current)

        while remaining > timedelta(0):
            day_end = datetime.combine(current.date(), self.hours.end)
            available = day_end - current

            if remaining <= available:
                return current + remaining

            remaining -= available
            current = self._next_business_open(
                day_end + timedelta(seconds=1),
            )

        return current

    def add_business_days(
        self, start: datetime, days: float,
    ) -> datetime:
        return self.add_business_hours(start, days * 24)

    def _next_business_open(self, from_dt: datetime) -> datetime:
        """หาจุดเปิดทำการถัดไป"""
        current_date = from_dt.date()

        # ถ้าเลยเวลาเปิดของวันนี้แล้ว → เริ่มพรุ่งนี้
        if from_dt.time() >= self.hours.end or (
            self.is_working_day(current_date)
            and from_dt.time() < self.hours.start
        ):
            if self.is_working_day(current_date) and from_dt.time() < self.hours.start:
                return datetime.combine(current_date, self.hours.start)
            current_date += timedelta(days=1)

        # หา working day ถัดไป
        while not self.is_working_day(current_date):
            current_date += timedelta(days=1)

        return datetime.combine(current_date, self.hours.start)

    # ---------- Thai holidays seed ----------

    @classmethod
    def thai_default(cls) -> "BusinessCalendar":
        """วันหยุดราชการไทย default"""
        return cls(
            hours=BusinessHours(start=time(8, 30), end=time(18, 0)),
            holidays=[
                # Recurring
                Holiday(date(2026, 1, 1), "วันขึ้นปีใหม่", True),
                Holiday(date(2026, 4, 13), "วันสงกรานต์", True),
                Holiday(date(2026, 4, 14), "วันสงกรานต์", True),
                Holiday(date(2026, 4, 15), "วันสงกรานต์", True),
                Holiday(date(2026, 5, 1), "วันแรงงาน", True),
                Holiday(date(2026, 5, 4), "วันฉัตรมงคล", True),
                Holiday(date(2026, 7, 28), "วันเฉลิมพระชนมพรรษา ร.10", True),
                Holiday(date(2026, 8, 12), "วันแม่แห่งชาติ", True),
                Holiday(date(2026, 10, 13), "วันนวมินทรมหาราช", True),
                Holiday(date(2026, 10, 23), "วันปิยมหาราช", True),
                Holiday(date(2026, 12, 5), "วันพ่อแห่งชาติ", True),
                Holiday(date(2026, 12, 10), "วันรัฐธรรมนูญ", True),
                Holiday(date(2026, 12, 31), "วันสิ้นปี", True),
                # Buddhist holidays (annual date varies) — ต้อง update ทุกปี
                # Holiday(date(2026, 3, 3), "วันมาฆบูชา", False),
                # ...
            ],
        )
```

## 7.2.4 SLA Calculator

```python
# app/modules/reconciliation/domain/sla_calculator.py

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.modules.reconciliation.domain.value_objects import (
    SLA_MATRIX_V3, SlaRule,
)
from app.modules.reconciliation.domain.business_calendar import (
    BusinessCalendar,
)


@dataclass(frozen=True, slots=True)
class SlaDeadlines:
    respond_due_at: datetime
    resolve_due_at: datetime
    escalate_at: datetime


class SlaCalculator:
    """
    คำนวณ SLA deadlines จาก category + severity + detected_at
    """

    def __init__(
        self,
        calendar: BusinessCalendar | None = None,
    ):
        self.calendar = calendar or BusinessCalendar.thai_default()

    def calculate(
        self,
        *,
        category: str,
        severity: str,
        detected_at: datetime,
    ) -> SlaDeadlines:
        rule = self._get_rule(category, severity)

        if rule.clock_mode == "24/7":
            respond_due = detected_at + rule.respond
            resolve_due = detected_at + rule.resolve
            escalate_at = detected_at + rule.escalate
        else:
            # business_hours
            respond_due = self.calendar.add_business_hours(
                detected_at, rule.respond.total_seconds() / 3600,
            )
            resolve_due = self.calendar.add_business_hours(
                detected_at, rule.resolve.total_seconds() / 3600,
            )
            escalate_at = self.calendar.add_business_hours(
                detected_at, rule.escalate.total_seconds() / 3600,
            )

        return SlaDeadlines(
            respond_due_at=respond_due,
            resolve_due_at=resolve_due,
            escalate_at=escalate_at,
        )

    def _get_rule(self, category: str, severity: str) -> SlaRule:
        cat_matrix = SLA_MATRIX_V3.get(category.lower())
        if not cat_matrix:
            # fallback
            cat_matrix = SLA_MATRIX_V3["data"]
        rule = cat_matrix.get(severity.lower())
        if not rule:
            rule = cat_matrix["medium"]
        return rule
```

## 7.2.5 Auto-Escalation Matrix

```python
# app/modules/reconciliation/domain/value_objects.py (เพิ่ม)

# บอกว่า level ไหน escalate ไป level ไหน
ESCALATION_MATRIX: dict[tuple[str, int], int] = {
    # (severity, current_level) → next_level
    # ใช้เมื่อ escalate_at ครบ
    ("critical", 1): 2,
    ("critical", 2): 3,
    ("critical", 3): 4,
    ("high", 1): 2,
    ("high", 2): 3,
    ("medium", 1): 2,
    ("low", 1): 1,      # low escalate ได้แค่ L1
}
```

## 7.2.6 SLA Matrix Summary Table

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  SLA MATRIX v3 — Respond / Resolve / Escalate                                             │
├────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┬───────────────┤
│ Category   │ Severity │ Respond  │ Resolve  │ Escalate │ Clock           │ Max Levels    │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ money      │ critical │ 15m      │ 2h       │ 30m      │ 24/7            │ 4             │
│ money      │ high     │ 30m      │ 8h       │ 2h       │ 24/7            │ 3             │
│ money      │ medium   │ 4h       │ 3d       │ 1d       │ business        │ 2             │
│ money      │ low      │ 1d       │ 14d      │ 7d       │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ tax        │ critical │ 15m      │ 4h       │ 30m      │ 24/7            │ 4             │
│ tax        │ high     │ 1h       │ 12h      │ 3h       │ 24/7            │ 3             │
│ tax        │ medium   │ 4h       │ 5d       │ 1d       │ business        │ 2             │
│ tax        │ low      │ 1d       │ 30d      │ 10d      │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ ledger     │ critical │ 30m      │ 4h       │ 1h       │ 24/7            │ 4             │
│ ledger     │ high     │ 1h       │ 12h      │ 4h       │ 24/7            │ 3             │
│ ledger     │ medium   │ 4h       │ 5d       │ 1d       │ business        │ 2             │
│ ledger     │ low      │ 1d       │ 30d      │ 10d      │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ security   │ critical │ 5m 🚨    │ 1h       │ 15m      │ 24/7            │ 4             │
│ security   │ high     │ 15m      │ 4h       │ 45m      │ 24/7            │ 3             │
│ security   │ medium   │ 2h       │ 2d       │ 12h      │ 24/7            │ 2             │
│ security   │ low      │ 12h      │ 7d       │ 3d       │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ sync       │ critical │ 15m      │ 2h       │ 30m      │ 24/7            │ 3             │
│ sync       │ high     │ 30m      │ 6h       │ 2h       │ 24/7            │ 3             │
│ sync       │ medium   │ 2h       │ 2d       │ 12h      │ 24/7            │ 2             │
│ sync       │ low      │ 12h      │ 7d       │ 3d       │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ inventory  │ critical │ 1h       │ 6h       │ 2h       │ business        │ 3             │
│ inventory  │ high     │ 2h       │ 24h      │ 8h       │ business        │ 3             │
│ inventory  │ medium   │ 8h       │ 5d       │ 2d       │ business        │ 2             │
│ inventory  │ low      │ 2d       │ 30d      │ 10d      │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ production │ critical │ 1h       │ 8h       │ 3h       │ business        │ 3             │
│ production │ high     │ 3h       │ 24h      │ 12h      │ business        │ 3             │
│ production │ medium   │ 12h      │ 7d       │ 3d       │ business        │ 2             │
│ production │ low      │ 3d       │ 30d      │ 14d      │ business        │ 1             │
├────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┼───────────────┤
│ customer   │ critical │ 2h       │ 12h      │ 6h       │ business        │ 3             │
│ supplier   │ critical │ 2h       │ 12h      │ 6h       │ business        │ 3             │
│ compliance │ critical │ 4h       │ 2d       │ 12h      │ business        │ 3             │
│ data       │ critical │ 2h       │ 12h      │ 6h       │ business        │ 3             │
└────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┴───────────────┘
```

---

# 7.3 Alert Channels v3 — 22 Channels

## 7.3.1 Full Channel Catalog

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  ALERT CHANNEL CATALOG v3 — 22 channels                                      │
├────┬──────────────────────┬───────────┬─────────────────────────────────────┤
│ #  │ Channel              │ Protocol  │ Use Case                            │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── Messaging ──                                                         │
│ 1  │ LINE_PERSONAL        │ REST API  │ Alert ส่วนตัว                       │
│ 2  │ LINE_GROUP           │ REST API  │ Alert ทีม                          │
│ 3  │ LINE_NOTIFY          │ REST API  │ Simple push (deprecated)           │
│ 4  │ ZALO                 │ REST API  │ 🆕 ยอดนิยมใน TH/SEA               │
│ 5  │ WHATSAPP_BUSINESS    │ Cloud API │ 🆕 ลูกค้า/partner ระหว่างประเทศ    │
│ 6  │ FACEBOOK_MESSENGER   │ Graph API │ 🆕 ลูกค้า B2C                     │
│ 7  │ TELEGRAM             │ Bot API   │ Alert ทีมเทค                       │
│ 8  │ VIBER                │ REST API  │ 🆕 บางตลาด                         │
│ 9  │ GOOGLE_CHAT          │ Webhook   │ 🆕 ทีมที่ใช้ Google Workspace      │
│ 10 │ MATTERMOST           │ Webhook   │ 🆕 self-hosted                    │
│ 11 │ SLACK                │ Webhook   │ ทีมเทค                              │
│ 12 │ TEAMS                │ Webhook   │ องค์กร Microsoft                   │
│ 13 │ DISCORD              │ Webhook   │ ทีม dev                            │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── Voice / SMS ──                                                       │
│ 14 │ SMS                  │ Twilio    │ Alert ฉุกเฉิน                       │
│ 15 │ VOICE_CALL           │ Twilio    │ 🆕 CRITICAL ต้องปลุก               │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── Email ──                                                             │
│ 16 │ EMAIL                │ SMTP      │ มาตรฐาน                             │
│ 17 │ AWS_SES              │ AWS SDK   │ 🆕 scale                             │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── On-call ──                                                           │
│ 18 │ PAGERDUTY            │ REST API  │ On-call rotation                    │
│ 19 │ OPSGENIE             │ REST API  │ 🆕 On-call (Atlassian)             │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── Ticketing ──                                                         │
│ 20 │ JIRA_TICKET          │ REST API  │ 🆕 สร้าง ticket อัตโนมัติ          │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── Webhook / API ──                                                     │
│ 21 │ GENERIC_WEBHOOK      │ HTTP POST │ Custom integration                 │
├────┼──────────────────────┼───────────┼─────────────────────────────────────┤
│    │ ── In-app ──                                                            │
│ 22 │ IN_APP + BANNER      │ WebSocket │ Real-time ใน dashboard              │
└────┴──────────────────────┴───────────┴─────────────────────────────────────┘
```

## 7.3.2 Channel Priority → Severity Mapping

```python
# app/modules/reconciliation/domain/value_objects.py (เพิ่ม)

CHANNELS_BY_SEVERITY: dict[str, list[str]] = {
    "critical": [
        "voice_call",       # ปลุก
        "sms",
        "pagerduty",
        "line_personal",
        "line_group",
        "in_app",
        "dashboard_banner",
    ],
    "high": [
        "sms",
        "line_group",
        "email",
        "in_app",
        "dashboard_banner",
    ],
    "medium": [
        "line_group",
        "email",
        "in_app",
    ],
    "low": [
        "email",
        "in_app",
    ],
}
```

## 7.3.3 🆕 Zalo Adapter

```python
# app/modules/reconciliation/infrastructure/alert_adapters/zalo_adapter.py

from dataclasses import dataclass
from app.modules.reconciliation.infrastructure.alert_adapters.base import (
    IAlertAdapter, AlertMessage,
)


class ZaloAdapter(IAlertAdapter):
    """
    Zalo Official Account (OA) — push message

    ใช้ Zalo OA API v3:
    - endpoint: https://openapi.zalo.me/v3.0/oa/message/cs
    - auth: access_token (OAuth)
    - recipient: user_id (from Zalo user)
    """

    channel = "zalo"

    def __init__(self, http_client, token_store):
        self.http = http_client
        self.token_store = token_store

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        token = await self.token_store.get("zalo")
        if not token:
            raise RuntimeError("ไม่มี Zalo access token")

        # รองรับ: user_id / phone
        payload = {
            "recipient": {"user_id": recipient},
            "message": {
                "text": f"{message.subject}\n\n{message.body}",
                "attachment": self._build_attachment(message),
            },
        }

        resp = await self.http.post(
            "https://openapi.zalo.me/v3.0/oa/message/cs",
            headers={"access_token": token},
            json=payload,
        )
        data = resp.json()
        return {"message_id": data.get("data", {}).get("message_id")}

    def _build_attachment(self, message: AlertMessage) -> dict | None:
        # Zalo OA รองรับ card, image, list
        if message.metadata.get("url"):
            return {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "elements": [{
                        "title": message.subject[:100],
                        "subtitle": message.body[:200],
                        "default_action": {
                            "type": "oa.open.url",
                            "url": message.metadata["url"],
                        },
                    }],
                },
            }
        return None
```

## 7.3.4 🆕 WhatsApp Business Adapter

```python
# app/modules/reconciliation/infrastructure/alert_adapters/whatsapp_adapter.py

class WhatsAppAdapter(IAlertAdapter):
    """
    WhatsApp Business Cloud API (Meta)

    - endpoint: https://graph.facebook.com/v18.0/{phone_number_id}/messages
    - auth: Bearer token
    - recipient: phone number (E.164 format without +)
    """

    channel = "whatsapp"

    def __init__(
        self, http_client, phone_number_id: str, token_store,
    ):
        self.http = http_client
        self.phone_number_id = phone_number_id
        self.token_store = token_store

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        token = await self.token_store.get("whatsapp")
        if not token:
            raise RuntimeError("ไม่มี WhatsApp access token")

        # WhatsApp Business API บังคับใช้ template สำหรับ initiator
        # ถ้า user ทักมาก่อน 24h → ใช้ session message
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient.lstrip("+"),
            "type": "text",
            "text": {
                "preview_url": True,
                "body": f"*{message.subject}*\n\n{message.body}",
            },
        }

        resp = await self.http.post(
            f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        data = resp.json()
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
        }
```

## 7.3.5 🆕 Voice Call Adapter (Twilio)

```python
# app/modules/reconciliation/infrastructure/alert_adapters/voice_adapter.py

class VoiceCallAdapter(IAlertAdapter):
    """
    Voice Call ผ่าน Twilio — สำหรับ CRITICAL ที่ต้องปลุกจริง

    ใช้ TwiML (XML) สำหรับ TTS
    """

    channel = "voice_call"

    def __init__(
        self,
        twilio_client,
        from_number: str,
        *,
        language: str = "th-TH",
        voice: str = "Polly.Kimberly",
        max_attempts: int = 3,
    ):
        self.client = twilio_client
        self.from_number = from_number
        self.language = language
        self.voice = voice
        self.max_attempts = max_attempts

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        # สร้าง TwiML (Thai TTS)
        twiml = self._build_twiml(message)

        call = await self.client.calls.create(
            to=recipient,
            from_=self.from_number,
            twiml=twiml,
            timeout=30,
        )
        return {"call_sid": call.sid}

    def _build_twiml(self, message: AlertMessage) -> str:
        """
        Thai TTS:
        - Twilio รองรับ Polly.Kimberly (en-US) — ใช้ผ่าน SSML
        - หรือใช้ Google Cloud TTS ใน TwiML <Play>
        """
        # ทำข้อความให้สั้น + พูดเข้าใจง่าย
        text = self._shorten_for_voice(message)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        {self._escape(text)}
    </Say>
    <Pause length="1"/>
    <Say voice="{self.voice}" language="{self.language}">
        กด 1 เพื่อรับทราบ
    </Say>
    <Gather numDigits="1" timeout="10">
        <Say voice="{self.voice}" language="{self.language}">
            กรุณากด 1
        </Say>
    </Gather>
</Response>"""

    @staticmethod
    def _shorten_for_voice(message: AlertMessage) -> str:
        return f"แจ้งเตือนวิกฤต {message.subject}. {message.body[:200]}"

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
```

## 7.3.6 🆕 Jira Ticket Adapter

```python
# app/modules/reconciliation/infrastructure/alert_adapters/jira_adapter.py

class JiraTicketAdapter(IAlertAdapter):
    """
    สร้าง Jira ticket อัตโนมัติสำหรับ discrepancy

    - ป้องกัน duplicate: ใช้ fingerprint เป็น label
    - link กลับไป ERP
    - update ถ้ามีอยู่แล้ว
    """

    channel = "jira_ticket"

    def __init__(
        self,
        http_client,
        base_url: str,
        project_key: str,
        token_store,
        *,
        issue_type: str = "Bug",
    ):
        self.http = http_client
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self.issue_type = issue_type
        self.token_store = token_store

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        """
        recipient = email ของ assignee (หรือ "")
        """
        token = await self.token_store.get("jira")

        # 1. ค้นหา ticket ที่มีอยู่แล้ว (by fingerprint)
        fingerprint = message.metadata.get("fingerprint", "")
        if fingerprint:
            existing = await self._find_by_fingerprint(fingerprint, token)
            if existing:
                # เพิ่ม comment
                await self._add_comment(existing["key"], message, token)
                return {"issue_key": existing["key"], "reused": True}

        # 2. สร้างใหม่
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": self.issue_type},
                "summary": message.subject[:255],
                "description": self._build_description(message),
                "labels": [
                    "erp-reconciliation",
                    f"severity-{message.severity}",
                    fingerprint[:8] if fingerprint else "no-fp",
                ],
                "priority": {"name": self._map_priority(message.severity)},
            },
        }

        if recipient:
            payload["fields"]["assignee"] = {"emailAddress": recipient}

        resp = await self.http.post(
            f"{self.base_url}/rest/api/3/issue",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        data = resp.json()
        return {"issue_key": data.get("key"), "reused": False}

    async def _find_by_fingerprint(
        self, fingerprint: str, token: str,
    ) -> dict | None:
        jql = (
            f'project = {self.project_key} '
            f'AND labels = "erp-reconciliation" '
            f'AND labels ~ "{fingerprint[:8]}" '
            f'AND statusCategory != Done'
        )
        resp = await self.http.get(
            f"{self.base_url}/rest/api/3/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"jql": jql, "maxResults": 1},
        )
        issues = resp.json().get("issues", [])
        return issues[0] if issues else None

    async def _add_comment(
        self, issue_key: str, message: AlertMessage, token: str,
    ) -> None:
        await self.http.post(
            f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
            headers={"Authorization": f"Bearer {token}"},
            json={"body": message.body},
        )

    def _build_description(self, message: AlertMessage) -> dict:
        """ADF (Atlassian Document Format)"""
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Discrepancy Alert"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": message.body}],
                },
                {
                    "type": "codeBlock",
                    "content": [{
                        "type": "text",
                        "text": json.dumps(message.metadata, indent=2, default=str),
                    }],
                },
            ],
        }

    @staticmethod
    def _map_priority(severity: str) -> str:
        return {
            "critical": "Highest",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
        }.get(severity, "Medium")
```

## 7.3.7 🆕 Google Chat Adapter

```python
# app/modules/reconciliation/infrastructure/alert_adapters/google_chat_adapter.py

class GoogleChatAdapter(IAlertAdapter):
    """
    Google Chat — Webhook-based
    """

    channel = "google_chat"

    def __init__(self, http_client, webhook_url: str):
        self.http = http_client
        self.webhook_url = webhook_url

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        # recipient = space_id (หรือไม่ใช้ — ส่งในกลุ่ม default)
        payload = {
            "cards": [{
                "header": {
                    "title": message.subject[:100],
                    "subtitle": f"Severity: {message.severity.upper()}",
                    "imageUrl": self._icon_for(message.severity),
                },
                "sections": [{
                    "widgets": [
                        {"textParagraph": {"text": message.body}},
                        {"buttons": [{
                            "textButton": {
                                "text": "ดูรายละเอียด",
                                "onClick": {
                                    "openLink": {
                                        "url": message.metadata.get("url", ""),
                                    },
                                },
                            },
                        }]},
                    ],
                }],
            }],
        }
        resp = await self.http.post(self.webhook_url, json=payload)
        return {"status": resp.status_code}

    @staticmethod
    def _icon_for(severity: str) -> str:
        return {
            "critical": "https://gmail.com/icons/critical.png",
            "high": "https://gmail.com/icons/high.png",
            "medium": "https://gmail.com/icons/medium.png",
            "low": "https://gmail.com/icons/low.png",
        }.get(severity, "")
```

## 7.3.8 🆕 OpsGenie Adapter

```python
# app/modules/reconciliation/infrastructure/alert_adapters/opsgenie_adapter.py

class OpsGenieAdapter(IAlertAdapter):
    """
    OpsGenie — on-call alert (Atlassian)
    """

    channel = "opsgenie"

    def __init__(self, http_client, api_key: str):
        self.http = http_client
        self.api_key = api_key

    async def send(self, *, recipient: str, message: AlertMessage) -> dict:
        # recipient = team name / ""
        payload = {
            "message": message.subject[:130],
            "description": message.body[:15000],
            "priority": self._map_priority(message.severity),
            "tags": [
                "erp-reconciliation",
                f"severity:{message.severity}",
            ],
            "details": {
                k: str(v)
                for k, v in message.metadata.items()
            },
        }
        if recipient:
            payload["responders"] = [{"name": recipient, "type": "team"}]

        resp = await self.http.post(
            "https://api.opsgenie.com/v2/alerts",
            headers={
                "Authorization": f"GenieKey {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        return {"request_id": resp.json().get("requestId")}

    @staticmethod
    def _map_priority(severity: str) -> str:
        return {
            "critical": "P1",
            "high": "P2",
            "medium": "P3",
            "low": "P4",
        }.get(severity, "P3")
```

## 7.3.9 Adapter Registry v3

```python
# app/modules/reconciliation/infrastructure/alert_adapters/__init__.py

from .line_adapter import LineAdapter, LineGroupAdapter, LineNotifyAdapter
from .zalo_adapter import ZaloAdapter
from .whatsapp_adapter import WhatsAppAdapter
from .messenger_adapter import MessengerAdapter
from .telegram_adapter import TelegramAdapter
from .viber_adapter import ViberAdapter
from .google_chat_adapter import GoogleChatAdapter
from .mattermost_adapter import MattermostAdapter
from .slack_adapter import SlackAdapter
from .teams_adapter import TeamsAdapter
from .discord_adapter import DiscordAdapter
from .sms_adapter import SmsAdapter
from .voice_adapter import VoiceCallAdapter
from .email_adapter import EmailAdapter
from .ses_adapter import SesAdapter
from .pagerduty_adapter import PagerDutyAdapter
from .opsgenie_adapter import OpsGenieAdapter
from .jira_adapter import JiraTicketAdapter
from .webhook_adapter import WebhookAdapter
from .in_app_adapter import InAppAdapter
from .banner_adapter import DashboardBannerAdapter


def build_adapter_registry(config, clients) -> dict[str, "IAlertAdapter"]:
    """
    สร้าง registry — ลงทะเบียนเฉพาะ adapter ที่ config เปิด
    """
    registry: dict[str, "IAlertAdapter"] = {}

    # Messaging
    if config.line_enabled:
        registry["line_personal"] = LineAdapter(clients.line, clients.tokens)
        registry["line_group"] = LineGroupAdapter(clients.line, clients.tokens)
    if config.line_notify_enabled:
        registry["line_notify"] = LineNotifyAdapter(clients.http, clients.tokens)
    if config.zalo_enabled:
        registry["zalo"] = ZaloAdapter(clients.http, clients.tokens)
    if config.whatsapp_enabled:
        registry["whatsapp"] = WhatsAppAdapter(
            clients.http, config.wa_phone_number_id, clients.tokens,
        )
    if config.messenger_enabled:
        registry["facebook_messenger"] = MessengerAdapter(
            clients.http, clients.tokens,
        )
    if config.telegram_enabled:
        registry["telegram"] = TelegramAdapter(
            config.telegram_bot_token, clients.http,
        )
    if config.viber_enabled:
        registry["viber"] = ViberAdapter(clients.http, clients.tokens)
    if config.google_chat_enabled:
        registry["google_chat"] = GoogleChatAdapter(
            clients.http, config.gchat_webhook,
        )
    if config.mattermost_enabled:
        registry["mattermost"] = MattermostAdapter(
            clients.http, config.mattermost_webhook,
        )
    if config.slack_enabled:
        registry["slack"] = SlackAdapter(
            config.slack_webhook, clients.http,
        )
    if config.teams_enabled:
        registry["teams"] = TeamsAdapter(
            config.teams_webhook, clients.http,
        )
    if config.discord_enabled:
        registry["discord"] = DiscordAdapter(
            config.discord_webhook, clients.http,
        )

    # Voice / SMS
    if config.twilio_enabled:
        registry["sms"] = SmsAdapter(
            clients.twilio, config.twilio_from,
        )
        registry["voice_call"] = VoiceCallAdapter(
            clients.twilio, config.twilio_voice_from,
        )

    # Email
    if config.smtp_enabled:
        registry["email"] = EmailAdapter(clients.smtp)
    if config.ses_enabled:
        registry["aws_ses"] = SesAdapter(clients.ses)

    # On-call
    if config.pagerduty_enabled:
        registry["pagerduty"] = PagerDutyAdapter(
            config.pd_routing_key, clients.http,
        )
    if config.opsgenie_enabled:
        registry["opsgenie"] = OpsGenieAdapter(
            clients.http, config.og_api_key,
        )

    # Ticket
    if config.jira_enabled:
        registry["jira_ticket"] = JiraTicketAdapter(
            clients.http, config.jira_url, config.jira_project, clients.tokens,
        )

    # Webhook
    if config.webhook_enabled:
        registry["webhook"] = WebhookAdapter(clients.http)

    # In-app
    if config.in_app_enabled:
        registry["in_app"] = InAppAdapter(clients.notifications)
        registry["dashboard_banner"] = DashboardBannerAdapter(clients.broadcaster)

    return registry
```

## 7.3.10 Routing Rules v3 — Expanded

```python
# app/modules/reconciliation/domain/routing_rules_seed.py (revised)

DEFAULT_ROUTING_RULES_V3 = [
    # ══════════════════════════════════════════════════════════════
    # P0 — CRITICAL SECURITY → ปลุกทันที
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="p0_security_critical",
        severities=["critical"],
        categories=["security"],
        channels=["voice_call", "sms", "pagerduty", "line_group"],
        recipients=[
            "voice:+66891234567",
            "sms:+66891234567",
            "pagerduty:key_security",
            "line:C_SECURITY_GROUP",
        ],
        min_interval_seconds=60,
        max_per_hour=30,
        silent_hours=None,  # ห้าม silent
    ),

    # ══════════════════════════════════════════════════════════════
    # P0 — CRITICAL MONEY/TAX/LEDGER → ปลุกทันที
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="p0_critical_money",
        severities=["critical"],
        categories=["money", "tax", "ledger"],
        channels=["line_group", "sms", "voice_call", "pagerduty"],
        recipients=[
            "line:C_CFO_GROUP",
            "sms:+66891234567",
            "voice:+66891234567",
            "pagerduty:key_finance",
        ],
        min_interval_seconds=60,
        max_per_hour=30,
        silent_hours=None,
    ),

    # ══════════════════════════════════════════════════════════════
    # P1 — HIGH MONEY → LINE + email + Jira
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="p1_high_money",
        severities=["high"],
        categories=["money", "tax", "ledger"],
        channels=["line_group", "email", "jira_ticket"],
        recipients=[
            "line:C_ACCOUNTING_GROUP",
            "email:accounting@company.com",
            "jira:accountant@company.com",
        ],
        min_interval_seconds=300,
        max_per_hour=20,
        silent_hours=(time(22, 0), time(7, 0)),
    ),

    # ══════════════════════════════════════════════════════════════
    # P1 — SECURITY HIGH
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="p1_security_high",
        severities=["high"],
        categories=["security"],
        channels=["line_group", "sms", "email"],
        recipients=[
            "line:C_SECURITY_GROUP",
            "sms:+66891234567",
            "email:security@company.com",
        ],
        max_per_hour=15,
    ),

    # ══════════════════════════════════════════════════════════════
    # Inventory / Production → warehouse manager
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="ops_inventory",
        categories=["inventory", "production"],
        channels=["line_group", "zalo", "email"],
        recipients=[
            "line:C_WAREHOUSE_GROUP",
            "zalo:warehouse_manager_id",
            "email:wh@company.com",
        ],
        max_per_hour=20,
        business_hours_only=True,
    ),

    # ══════════════════════════════════════════════════════════════
    # Sync → IT team
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="it_sync",
        categories=["sync"],
        channels=["line_group", "slack", "email", "jira_ticket"],
        recipients=[
            "line:C_IT_GROUP",
            "slack:#erp-alerts",
            "email:it@company.com",
            "jira:it@company.com",
        ],
        min_interval_seconds=600,
        max_per_hour=10,
    ),

    # ══════════════════════════════════════════════════════════════
    # Compliance → auditor
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="compliance",
        categories=["compliance"],
        channels=["email"],
        recipients=["auditor@company.com"],
        max_per_hour=10,
        business_hours_only=True,
    ),

    # ══════════════════════════════════════════════════════════════
    # Customer → CS team
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="customer_cs",
        categories=["customer"],
        severities=["critical", "high"],
        channels=["line_group", "zalo", "email"],
        recipients=[
            "line:C_CS_GROUP",
            "zalo:cs_team_id",
            "email:cs@company.com",
        ],
        business_hours_only=True,
        max_per_hour=15,
    ),

    # ══════════════════════════════════════════════════════════════
    # Supplier → procurement
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="supplier_procurement",
        categories=["supplier"],
        severities=["critical", "high"],
        channels=["line_group", "email"],
        recipients=[
            "line:C_PROCUREMENT_GROUP",
            "email:procurement@company.com",
        ],
        business_hours_only=True,
        max_per_hour=10,
    ),

    # ══════════════════════════════════════════════════════════════
    # Data → data team
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="data_team",
        categories=["data"],
        channels=["slack", "email"],
        recipients=["slack:#data-alerts", "email:data@company.com"],
        business_hours_only=True,
        max_per_hour=20,
    ),

    # ══════════════════════════════════════════════════════════════
    # WhatsApp — for international partners
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="international_partner",
        categories=["money", "compliance"],
        severities=["critical", "high"],
        channels=["whatsapp", "email"],
        recipients=["whatsapp:+66000000000", "email:partner@company.com"],
        max_per_hour=5,
    ),

    # ══════════════════════════════════════════════════════════════
    # Daily digest — LOW/MEDIUM
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="daily_digest",
        severities=["low", "medium"],
        channels=["email"],
        recipients=["accounting@company.com"],
        min_interval_seconds=86400,
    ),

    # ══════════════════════════════════════════════════════════════
    # In-app always
    # ══════════════════════════════════════════════════════════════
    AlertRoutingRule(
        name="inapp_always",
        severities=["critical", "high", "medium"],
        channels=["in_app", "dashboard_banner"],
        recipients=["role:accountant", "role:admin", "role:manager"],
        min_interval_seconds=0,
    ),
]
```

## 7.3.11 Alert Channel Summary Table

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  CHANNEL PRIORITY MATRIX (Severity → Channels)                               │
├────────────┬─────────────────────────────────────────────────────────────────┤
│ Severity   │ Channels                                                        │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ CRITICAL   │ voice_call, sms, pagerduty, line_personal, line_group,         │
│            │ opsgenie, in_app, dashboard_banner                             │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ HIGH       │ sms, line_group, zalo, whatsapp, email, slack, teams,          │
│            │ google_chat, telegram, jira_ticket, in_app, dashboard_banner   │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ MEDIUM     │ line_group, zalo, email, slack, teams, jira_ticket, in_app    │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ LOW        │ email, in_app (digest)                                         │
└────────────┴─────────────────────────────────────────────────────────────────┘
```

---

# 7.4 Tests v3 — Critical Test Cases

## 7.4.1 Test SLA Business Hours Clock

```python
# app/modules/reconciliation/tests/domain/test_sla_calculator.py

import pytest
from datetime import datetime, date, time, timedelta

from app.modules.reconciliation.domain.sla_calculator import SlaCalculator
from app.modules.reconciliation.domain.business_calendar import (
    BusinessCalendar, BusinessHours, Holiday,
)


class TestSlaCalculatorBusinessHours:
    def setup_method(self):
        self.calendar = BusinessCalendar(
            hours=BusinessHours(start=time(9, 0), end=time(18, 0)),
            holidays=[Holiday(date(2026, 1, 1), "New Year")],
        )
        self.calc = SlaCalculator(self.calendar)

    def test_money_critical_24_7(self):
        """MONEY + CRITICAL → 24/7 — ไม่หยุด"""
        # detected ตอน 22:00 วันศุกร์
        detected = datetime(2026, 1, 2, 22, 0)  # Fri 22:00
        deadlines = self.calc.calculate(
            category="money", severity="critical", detected_at=detected,
        )
        # resolve 2h → 2026-01-03 00:00 (ไม่หยุด)
        assert deadlines.resolve_due_at == detected + timedelta(hours=2)

    def test_inventory_medium_business_hours_skips_weekend(self):
        """INVENTORY + MEDIUM → business hours — ข้าม weekend"""
        # detected วันศุกร์ 17:00
        detected = datetime(2026, 1, 2, 17, 0)  # Fri 17:00
        deadlines = self.calc.calculate(
            category="inventory", severity="medium", detected_at=detected,
        )
        # medium resolve 5d business hours
        # Fri 17:00–18:00 = 1h, จันทร์–ศุกร์ 9:00–18:00 = 9h × 5 = 45h
        # รวม = 46h → 5d (120h) — ต้องข้ามไปอังคารถัดไป
        assert deadlines.resolve_due_at > detected
        # ต้องไม่ใช่เสาร์/อาทิตย์
        assert deadlines.resolve_due_at.weekday() < 5

    def test_skips_holiday(self):
        """ข้ามวันหยุด"""
        # detected 2025-12-31 17:00 (Wed) — resolve 3 business days
        # 2026-01-01 (Thu) = หยุด
        # 2026-01-02 (Fri) = business
        # 2026-01-03, 04 = weekend
        # 2026-01-05 (Mon) = business
        # 2026-01-06 (Tue) = business
        detected = datetime(2025, 12, 31, 17, 0)
        deadlines = self.calc.calculate(
            category="inventory", severity="medium",
            detected_at=detected,
        )
        # 3 days × 9 hours/day = 27 business hours
        # 31 Dec: 1h, 2 Jan: 9h, 5 Jan: 9h, 6 Jan: 8h → รวม 27h
        assert deadlines.resolve_due_at.date() == date(2026, 1, 6)
```

## 7.4.2 Test Alert Routing v3

```python
# app/modules/reconciliation/tests/application/test_alert_routing_v3.py

@pytest.mark.asyncio
async def test_critical_security_routes_to_voice(routing_config):
    router = AlertRouter(...)
    logs = await router.dispatch(
        company_id=CID,
        event="discrepancy_detected",
        priority=AlertPriority.P0_PAGE,
        payload={
            "severity": "critical",
            "category": "security",
            "check_code": "SECURITY.002",
        },
    )
    channels = {log.channel for log in logs}
    assert "voice_call" in channels
    assert "sms" in channels
    assert "pagerduty" in channels


@pytest.mark.asyncio
async def test_high_money_skips_silent_hours(routing_config):
    """HIGH MONEY ที่ 23:00 → ถูก suppress"""
    with freeze_time("2026-01-02 23:00:00"):
        router = AlertRouter(...)
        logs = await router.dispatch(
            company_id=CID,
            event="discrepancy_detected",
            priority=AlertPriority.P1_URGENT,
            payload={
                "severity": "high",
                "category": "money",
                "check_code": "MONEY.002",
            },
        )
        # p1_high_money silent 22:00–07:00 → ไม่ส่ง
        assert len(logs) == 0 or all(
            log.status == "suppressed" for log in logs
        )


@pytest.mark.asyncio
async def test_jira_ticket_dedup_by_fingerprint(jira_mock):
    """ยิงซ้ำ fingerprint เดียว → ไม่สร้าง ticket ใหม่"""
    router = AlertRouter(...)
    payload = {
        "severity": "high",
        "category": "money",
        "check_code": "MONEY.002",
        "fingerprint": "abc123def456",
    }
    log1 = await router.dispatch(company_id=CID, event="x", priority=..., payload=payload)
    log2 = await router.dispatch(company_id=CID, event="x", priority=..., payload=payload)

    # jira ถูกเรียกครั้งเดียว — ครั้งที่สอง reuse
    assert jira_mock.create_called == 1


@pytest.mark.asyncio
async def test_whatsapp_falls_back_to_email_on_failure(whatsapp_mock, email_mock):
    whatsapp_mock.send.side_effect = Exception("WA API down")
    router = AlertRouter(...)
    logs = await router.dispatch(
        company_id=CID,
        event="x",
        priority=AlertPriority.P2_HIGH,
        payload={
            "severity": "high",
            "category": "money",
            "check_code": "MONEY.002",
        },
    )
    # ต้องมี email ส่งสำเร็จ
    assert any(log.channel == "email" and log.status == "sent" for log in logs)
```

## 7.4.3 Test v3 Checks

```python
# app/modules/reconciliation/tests/checks/test_v3_checks.py

@pytest.mark.asyncio
async def test_security_002_detects_privilege_escalation(db, company):
    """user ได้ admin โดยไม่มี audit"""
    # arrange
    user_id = await create_user(db, company, "testuser")
    role_id = await get_role_id(db, company, "admin")
    # assign role โดยตรง ไม่ผ่าน use case (จึงไม่มี audit)
    await db.execute("""
        INSERT INTO app_user_company_roles
        (user_id, company_id, role_id, assigned_at, assigned_by)
        VALUES (:u, :c, :r, NOW(), NULL)
    """, {"u": user_id, "c": company.id, "r": role_id})

    check = CheckPermissionEscalation(db)
    results = await check.run(company.id)

    assert len(results) == 1
    assert results[0].entity_type == "user_role"
    assert results[0].evidence.extra["security_incident"] is True


@pytest.mark.asyncio
async def test_data_001_detects_orphan_fk(db, company):
    """สร้าง invoice_line ที่ชี้ product ที่ไม่มี"""
    # disable FK check ชั่วคราว
    await db.execute("SET session_replication_role = 'replica'")
    await db.execute("""
        INSERT INTO invoice_lines
        (id, invoice_id, line_number, product_id, ...)
        VALUES (gen_random_uuid(), :inv, 1, gen_random_uuid(), ...)
    """, {"inv": existing_invoice_id})
    await db.execute("SET session_replication_role = 'origin'")

    check = CheckOrphanForeignKey(db)
    results = await check.run(company.id)
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_customer_001_credit_limit(db, company, customer_over_limit):
    check = CheckCreditLimitExceeded(db)
    results = await check.run(company.id)
    assert len(results) == 1
    assert results[0].entity_type == "customer"
    usage = results[0].evidence.extra["usage_pct"]
    assert float(usage) > 100
```

---

# 7.5 Updated Checklist v3

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  RECONCILIATION v3 — FINAL CHECKLIST                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ① CHECKS (46)                                                              │
│   □ Money (12): VAT, overcharge, duplicate invoice, over-allocation,       │
│     paid mismatch, wrong customer, orphan CN, aging,                       │
│     dup order, dup payment, refund exceed, CN exceed                       │
│   □ Ledger (7): orphan, unbalanced, closed period, duplicate,              │
│     missing, no source, account type                                       │
│   □ Inventory (7): balance, expired lot, negative, no ref,                 │
│     timestamp, no warehouse, duplicate lot                                 │
│   □ Production (5): yield, long-open, BOM, no-recipe, waste               │
│   □ Tax (5): VAT rate, WHT, e-Tax deadline, rate mismatch, e-Tax reject   │
│   □ Sync (4): cloud mismatch, cloud orphan, dead letter, latency          │
│   □ Compliance (5): tax ID, gap, missing audit, void no audit, retention  │
│   □ Customer (2): credit limit, duplicate                                │
│   □ Supplier (2): duplicate, PO mismatch                                 │
│   □ Security (3): unusual login, permission escalation, stale API key    │
│   □ Data (3): orphan FK, null required, invalid format                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ② SLA MATRIX v3                                                            │
│   □ 11 categories × 4 severities                                            │
│   □ Category-specific (MONEY faster than INVENTORY)                        │
│   □ Business hours clock + Thai holidays                                   │
│   □ Auto-escalation chain (max 4 levels)                                   │
│   □ Escalation matrix (severity, level) → next_level                      │
│   □ SlaCalculator integrates BusinessCalendar                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ③ ALERT CHANNELS (22)                                                      │
│   □ Messaging: LINE (3), Zalo, WhatsApp, Messenger, Telegram,             │
│     Viber, Google Chat, Mattermost, Slack, Teams, Discord                 │
│   □ Voice/SMS: SMS, Voice Call                                             │
│   □ Email: Email, AWS SES                                                  │
│   □ On-call: PagerDuty, OpsGenie                                           │
│   □ Ticket: Jira                                                           │
│   □ Webhook: Generic                                                       │
│   □ In-app: Notification + Banner                                          │
│   □ Channel priority → severity mapping                                    │
│   □ Routing rules v3 with 12 rules                                         │
│   □ Throttling + suppression + silent hours                                │
│   □ Jira dedup by fingerprint                                              │
│   □ Voice call for CRITICAL SECURITY/MONEY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ④ TESTS v3                                                                 │
│   □ SLA business hours skip weekend + holiday                             │
│   □ Voice call routed for CRITICAL SECURITY                                │
│   □ Silent hours suppression                                               │
│   □ Jira dedup by fingerprint                                              │
│   □ WhatsApp → email fallback                                              │
│   □ SECURITY.002 detects privilege escalation                              │
│   □ DATA.001 detects orphan FK                                             │
│   □ CUSTOMER.001 credit limit exceeded                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Metrics v3 (เพิ่มจาก v2)

| Metric | Target | ใหม่ |
|--------|--------|------|
| **SLA compliance per category** | ≥ 95% | 🆕 |
| **Business-hours SLA accuracy** | 100% | 🆕 |
| **Escalation auto-rate** | ≥ 90% | 🆕 |
| **Voice call answer rate (CRITICAL)** | ≥ 80% | 🆕 |
| **Jira ticket dedup rate** | ≥ 95% | 🆕 |
| **SECURITY incident MTTR** | < 1h | 🆕 |
| **Checks per category pass rate** | ≥ 99.9% | 🆕 |

---

 