# 🐍 Python Script: Auto-Generate 57 Prompt Files

สคริปต์นี้จะอ่าน metadata จาก dictionary ที่ฝังไว้ และสร้างไฟล์ `.md` ครบ 57 ไฟล์ พร้อมจัดโฟลเดอร์ตาม layer อัตโนมัติ

---

## 📄 `scripts/generate_prompts.py`

```python
#!/usr/bin/env python3
"""
Auto-generate prompt files for 57 modules from embedded metadata.

Usage:
    python scripts/generate_prompts.py
    python scripts/generate_prompts.py --output docs/prompts --dry-run
    python scripts/generate_prompts.py --layer 2
    python scripts/generate_prompts.py --force   # overwrite existing

Author: Kongnakorn Jantakun
Version: 3.0.0
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

# ─────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────

AUTHOR = "Kongnakorn Jantakun"
EMAIL = "kongnakornjantakun@gmail.com"
VERSION = "3.0.0"
TODAY = date.today().isoformat()

LAYER_NAMES: dict[int, str] = {
    0: "core",
    1: "foundation",
    2: "money-path",
    3: "goods-path",
    4: "operations",
    5: "intelligence",
    6: "monitoring",
    7: "templates",
}

LAYER_TITLES: dict[int, str] = {
    0: "CORE",
    1: "FOUNDATION",
    2: "MONEY PATH",
    3: "GOODS PATH",
    4: "OPERATIONS",
    5: "INTELLIGENCE",
    6: "MONITORING",
    7: "TEMPLATES",
}

PRIORITY_EMOJI: dict[str, str] = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


# ─────────────────────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────────────────────

@dataclass
class ModuleMeta:
    name: str
    layer: int
    priority: Literal["critical", "high", "medium", "low"]
    phase: int
    prefix: str
    domain: str
    dependencies: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    value_objects: list[str] = field(default_factory=list)
    enums: dict[str, list[str]] = field(default_factory=dict)
    invariants: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    special_rules: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def priority_emoji(self) -> str:
        return PRIORITY_EMOJI[self.priority]

    @property
    def dir_name(self) -> str:
        return f"layer-{self.layer}-{LAYER_NAMES[self.layer]}"

    @property
    def file_name(self) -> str:
        return f"{self.name}.md"


# ─────────────────────────────────────────────────────────
# Metadata Registry — 57 Modules
# ─────────────────────────────────────────────────────────

MODULES: list[ModuleMeta] = [
    # ─── LAYER 0: CORE (5) ──────────────────────────────
    ModuleMeta(
        name="tenant_context", layer=0, priority="critical", phase=1,
        prefix="tctx", domain="Core (cross-cutting)",
        dependencies=["tenancy"],
        entities=["TenantContext"],
        value_objects=["TenantId", "SchemaName"],
        enums={"ContextSource": ["HEADER", "JWT", "SUBDOMAIN"]},
        invariants=[
            "`tenant_id` ต้องถูกตั้งค่าก่อนทุก DB query",
            "`schema_name` ตรงกับ pattern `^tenant_[a-z0-9_]+$`",
        ],
        events=["TenantContextSet", "TenantContextCleared"],
        tables=["tenant_{prefix}.tenant_contexts (audit trail)"],
        special_rules=[
            "Middleware-level: ใช้ `ContextVar` (asyncio-safe)",
            "Set `app.current_tenant` GUC สำหรับ RLS",
            "ทุก repository ต้อง `Depends(get_current_tenant)`",
        ],
    ),
    ModuleMeta(
        name="audit", layer=0, priority="critical", phase=1,
        prefix="aud", domain="Core",
        dependencies=["tenant_context", "events"],
        entities=["AuditLog"],
        value_objects=["AuditAction", "AuditDiff", "Actor"],
        enums={"AuditAction": ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT"]},
        invariants=[
            "Audit log **immutable** (append-only, no UPDATE/DELETE)",
            "ทุก record ต้องมี `actor_id` + `tenant_id` + `timestamp`",
            "`before` + `after` ต้องเป็น valid JSON",
        ],
        events=["AuditLogWritten", "AuditLogExported"],
        tables=["tenant_{prefix}.audit_logs (BRIN index on timestamp)"],
        special_rules=[
            "Async write (fire-and-forget ผ่าน Kafka)",
            "Retention 7 ปี (compliance)",
            "PII masking ใน metadata",
        ],
    ),
    ModuleMeta(
        name="idempotency", layer=0, priority="critical", phase=1,
        prefix="idem", domain="Core",
        dependencies=["tenant_context"],
        entities=["IdempotencyRecord"],
        value_objects=["IdempotencyKey", "ResponseHash"],
        enums={"IdempotencyStatus": ["PENDING", "COMPLETED", "FAILED"]},
        invariants=[
            "Key unique ต่อ `(tenant_id, key)`",
            "Response hash ต้องตรงกันถ้าส่งซ้ำ",
            "TTL = 24 ชั่วโมง (Redis) + persistent (Postgres)",
        ],
        events=["IdempotencyHit", "IdempotencyMiss", "IdempotencyConflict"],
        tables=["tenant_{prefix}.idempotency_records"],
        special_rules=[
            "ใช้ `SETNX` ใน Redis ก่อน → fallback Postgres",
            "Return cached response ถ้า key ซ้ำ + hash ตรง",
            "Return 409 Conflict ถ้า key ซ้ำ + hash ไม่ตรง",
        ],
    ),
    ModuleMeta(
        name="config", layer=0, priority="critical", phase=1,
        prefix="cfg", domain="Core",
        dependencies=["tenant_context", "audit"],
        entities=["ConfigEntry"],
        value_objects=["ConfigKey", "ConfigValue"],
        enums={"ConfigScope": ["GLOBAL", "TENANT", "USER", "MODULE"]},
        invariants=[
            "Config key unique ต่อ `(scope, tenant_id, key)`",
            "Value type ตรงกับ schema ที่ลงทะเบียน",
            "Sensitive config ต้อง encrypted at rest",
        ],
        events=["ConfigChanged", "ConfigRollback", "ConfigImported"],
        tables=["tenant_{prefix}.configs"],
        special_rules=[
            "Hierarchical override: GLOBAL < TENANT < USER",
            "Cache ใน Redis (namespace `cfg:{scope}:{tenant}:{key}`)",
            "Versioning + rollback support",
        ],
    ),
    ModuleMeta(
        name="events", layer=0, priority="critical", phase=1,
        prefix="evt", domain="Core",
        dependencies=["tenant_context"],
        entities=["EventLog"],
        value_objects=["EventName", "EventPayload", "CorrelationId"],
        enums={"EventStatus": ["PENDING", "PUBLISHED", "FAILED", "DEAD_LETTER"]},
        invariants=[
            "Event name ตรง pattern `^[A-Z][a-zA-Z]+$` (PascalCase)",
            "Payload ต้อง serialize ได้ (JSON)",
            "`correlation_id` + `causation_id` ต้องมี",
        ],
        events=["EventPublished", "EventFailed", "EventDeadLettered"],
        tables=["tenant_{prefix}.event_logs (outbox pattern)"],
        special_rules=[
            "Transactional outbox pattern",
            "Kafka topics: `{tenant}.{module}.events`",
            "Retry 3 ครั้ง → dead letter queue",
            "At-least-once delivery + consumer idempotency",
        ],
    ),

    # ─── LAYER 1: FOUNDATION (8) ────────────────────────
    ModuleMeta(
        name="tenancy", layer=1, priority="critical", phase=1,
        prefix="ten", domain="Foundation",
        dependencies=["tenant_context", "audit"],
        entities=["Tenant", "TenantPlan"],
        value_objects=["TenantSlug", "SchemaName", "ResourceQuota"],
        enums={"TenantStatus": ["ACTIVE", "SUSPENDED", "TRIAL", "CANCELLED"]},
        invariants=[
            "Slug unique + pattern `^[a-z][a-z0-9-]{2,30}$`",
            "Schema name = `tenant_{slug}`",
            "Quota ไม่ติดลบ",
        ],
        events=["TenantCreated", "TenantSuspended", "TenantUpgraded", "TenantDeleted"],
        tables=["public.tenants", "public.tenant_plans"],
        special_rules=[
            "Provisioning schema อัตโนมัติ (CREATE SCHEMA + migrations)",
            "Soft delete (grace period 30 วัน)",
            "Billing integration (Stripe/Omise)",
        ],
    ),
    ModuleMeta(
        name="authentication", layer=1, priority="critical", phase=1,
        prefix="auth", domain="Foundation",
        dependencies=["tenancy", "user", "audit"],
        entities=["Session", "RefreshToken", "ApiKey"],
        value_objects=["PasswordHash", "JWTClaim"],
        enums={"AuthMethod": ["PASSWORD", "OAUTH", "API_KEY", "MFA"]},
        invariants=[
            "Password hash ใช้ Argon2id (ไม่ใช่ bcrypt)",
            "Refresh token single-use (rotation)",
            "API key hash เก็บแบบ SHA-256",
            "Max 5 login attempts → lock 15 นาที",
        ],
        events=["UserLoggedIn", "UserLoggedOut", "LoginFailed", "TokenRefreshed", "MFARequired"],
        tables=["tenant_{prefix}.sessions", "tenant_{prefix}.refresh_tokens",
                "tenant_{prefix}.api_keys", "tenant_{prefix}.login_attempts"],
        special_rules=[
            "JWT access token: 15 นาที",
            "Refresh token: 7 วัน (rotating)",
            "MFA: TOTP + backup codes",
            "Rate limit: 5 req/min ต่อ IP",
        ],
    ),
    ModuleMeta(
        name="user", layer=1, priority="critical", phase=1,
        prefix="usr", domain="Foundation",
        dependencies=["tenancy", "authentication", "audit"],
        entities=["User", "Role", "Permission"],
        value_objects=["Email", "PhoneNumber", "FullName"],
        enums={"UserStatus": ["ACTIVE", "INACTIVE", "SUSPENDED", "PENDING_VERIFICATION"]},
        invariants=[
            "Email unique ต่อ tenant",
            "User ต้องมี role อย่างน้อย 1",
            "Role name unique ต่อ tenant",
        ],
        events=["UserCreated", "UserUpdated", "UserDeactivated", "RoleAssigned", "PermissionGranted"],
        tables=["tenant_{prefix}.users", "tenant_{prefix}.roles",
                "tenant_{prefix}.permissions", "tenant_{prefix}.user_roles"],
        special_rules=[
            "Email verification required",
            "Soft delete (deleted_at)",
            "RBAC model (role → permissions)",
            "ไม่ให้ลบ user ที่มี audit log",
        ],
    ),
    ModuleMeta(
        name="employee", layer=1, priority="high", phase=1,
        prefix="emp", domain="Foundation (HR)",
        dependencies=["user", "audit"],
        entities=["Employee", "Department", "Position"],
        value_objects=["EmployeeCode", "Salary", "HireDate"],
        enums={"EmploymentType": ["FULL_TIME", "PART_TIME", "CONTRACT", "INTERN"]},
        invariants=[
            "Employee code unique ต่อ tenant",
            "Salary >= 0",
            "Hire date <= today",
            "User 1 คน = 1 employee",
        ],
        events=["EmployeeHired", "EmployeePromoted", "EmployeeTerminated", "DepartmentCreated"],
        tables=["tenant_{prefix}.employees", "tenant_{prefix}.departments", "tenant_{prefix}.positions"],
        special_rules=[
            "Link กับ user (1:1)",
            "Salary encrypted at rest",
            "Org chart relationship",
        ],
    ),
    ModuleMeta(
        name="customer", layer=1, priority="critical", phase=1,
        prefix="cust", domain="Foundation (CRM)",
        dependencies=["tenancy", "audit"],
        entities=["Customer", "CustomerGroup", "Address"],
        value_objects=["TaxId", "CreditLimit", "CustomerTier"],
        enums={"CustomerType": ["INDIVIDUAL", "COMPANY", "GOVERNMENT"]},
        invariants=[
            "Tax ID unique ต่อ tenant (ถ้ามี)",
            "Credit limit >= 0",
            "Email/phone format valid",
        ],
        events=["CustomerCreated", "CustomerUpdated", "CustomerBlacklisted", "CreditLimitChanged"],
        tables=["tenant_{prefix}.customers", "tenant_{prefix}.customer_groups",
                "tenant_{prefix}.customer_addresses"],
        special_rules=[
            "Soft delete (ลูกค้าที่มี invoice ห้ามลบ)",
            "PDPA compliance (consent tracking)",
            "Merge duplicate customers",
        ],
    ),
    ModuleMeta(
        name="supplier", layer=1, priority="high", phase=1,
        prefix="sup", domain="Foundation (Procurement)",
        dependencies=["audit", "product"],
        entities=["Supplier", "SupplierContact", "SupplierProduct"],
        value_objects=["TaxId", "PaymentTerms", "LeadTime"],
        enums={"SupplierStatus": ["ACTIVE", "INACTIVE", "BLACKLISTED", "PENDING"]},
        invariants=[
            "Tax ID unique ต่อ tenant",
            "Payment terms >= 0 วัน",
            "Rating 0-5",
        ],
        events=["SupplierCreated", "SupplierApproved", "SupplierBlacklisted", "SupplierRated"],
        tables=["tenant_{prefix}.suppliers", "tenant_{prefix}.supplier_contacts",
                "tenant_{prefix}.supplier_products"],
        special_rules=[
            "Vendor rating system",
            "Approved vendor list (AVL)",
            "Link กับ product (many-to-many)",
        ],
    ),
    ModuleMeta(
        name="product", layer=1, priority="critical", phase=1,
        prefix="prod", domain="Foundation",
        dependencies=["audit", "pricing"],
        entities=["Product", "ProductVariant", "Category", "UOM"],
        value_objects=["SKU", "Barcode", "ProductName", "Weight"],
        enums={"ProductType": ["GOODS", "SERVICE", "RAW_MATERIAL", "BUNDLE"]},
        invariants=[
            "SKU unique ต่อ tenant",
            "Barcode unique (ถ้ามี)",
            "Weight >= 0",
        ],
        events=["ProductCreated", "ProductUpdated", "ProductDiscontinued", "PriceChanged"],
        tables=["tenant_{prefix}.products", "tenant_{prefix}.product_variants",
                "tenant_{prefix}.categories", "tenant_{prefix}.uoms"],
        special_rules=[
            "Soft delete",
            "Multi-UOM (base + conversion)",
            "Image storage (S3/MinIO)",
            "Variant matrix (size × color)",
        ],
    ),
    ModuleMeta(
        name="pricing", layer=1, priority="critical", phase=1,
        prefix="prc", domain="Foundation",
        dependencies=["product", "customer", "audit"],
        entities=["PriceList", "PriceRule", "Discount"],
        value_objects=["Price", "DiscountRate", "EffectiveDate"],
        enums={"PriceType": ["RETAIL", "WHOLESALE", "MEMBER", "PROMOTION"]},
        invariants=[
            "Price >= 0",
            "Discount 0-100%",
            "Effective date range valid",
            "ไม่มี overlapping price list ที่ active",
        ],
        events=["PriceListCreated", "PriceChanged", "DiscountApplied", "PromotionStarted"],
        tables=["tenant_{prefix}.price_lists", "tenant_{prefix}.price_rules", "tenant_{prefix}.discounts"],
        special_rules=[
            "Hierarchical pricing (customer > group > default)",
            "Time-based pricing",
            "Volume discounts (tiered)",
        ],
    ),

    # ─── LAYER 2: MONEY PATH (6) ────────────────────────
    ModuleMeta(
        name="order", layer=2, priority="critical", phase=1,
        prefix="ord", domain="ERP",
        dependencies=["customer", "product", "pricing", "tax", "audit", "idempotency"],
        entities=["SalesOrder", "OrderLine"],
        value_objects=["OrderNumber", "OrderTotal", "ShippingAddress"],
        enums={"OrderStatus": ["DRAFT", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]},
        invariants=[
            "`total = subtotal - discount + VAT + shipping`",
            "`qty > 0` ทุก line",
            "Order number unique + pattern `SO-YYYYMM-XXXX`",
            "Status transition forward-only",
        ],
        events=["OrderCreated", "OrderConfirmed", "OrderCancelled", "OrderShipped", "OrderDelivered"],
        tables=["tenant_{prefix}.sales_orders", "tenant_{prefix}.sales_order_lines"],
        special_rules=[
            "Reserve inventory on confirm",
            "Release on cancel",
            "Link to invoice (1:N)",
        ],
    ),
    ModuleMeta(
        name="ledger", layer=2, priority="critical", phase=1,
        prefix="led", domain="ERP (Accounting)",
        dependencies=["money", "audit", "idempotency"],
        entities=["JournalEntry", "LedgerEntry", "Account"],
        value_objects=["AccountCode", "DebitCredit", "PostingDate"],
        enums={"AccountType": ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]},
        invariants=[
            "**`sum(debit) == sum(credit)`** (double-entry)",
            "Journal entry posted = immutable",
            "Posting date <= today",
            "Account code unique",
        ],
        events=["JournalEntryPosted", "LedgerEntryCreated", "AccountCreated", "PeriodClosed"],
        tables=["tenant_{prefix}.accounts", "tenant_{prefix}.journal_entries",
                "tenant_{prefix}.ledger_entries", "tenant_{prefix}.accounting_periods"],
        special_rules=[
            "Immutable after posting (reversal entries only)",
            "Fiscal period lock",
            "Trial balance report",
        ],
    ),
    ModuleMeta(
        name="payment", layer=2, priority="critical", phase=2,
        prefix="pay", domain="ERP",
        dependencies=["money", "invoice", "ledger", "audit", "idempotency"],
        entities=["Payment", "PaymentAllocation"],
        value_objects=["PaymentMethod", "TransactionRef", "PaymentAmount"],
        enums={
            "PaymentMethod": ["CASH", "TRANSFER", "CARD", "QR", "CHEQUE"],
            "PaymentStatus": ["PENDING", "COMPLETED", "FAILED", "REFUNDED"],
        },
        invariants=[
            "`sum(allocations) == payment.amount`",
            "Amount > 0",
            "Cannot allocate to voided invoice",
            "Transaction ref unique",
        ],
        events=["PaymentReceived", "PaymentAllocated", "PaymentRefunded", "PaymentFailed"],
        tables=["tenant_{prefix}.payments", "tenant_{prefix}.payment_allocations"],
        special_rules=[
            "Gateway integration (Omise/Stripe/SCB)",
            "Partial payment support",
            "Reconciliation with bank statement",
        ],
    ),
    ModuleMeta(
        name="accounting_gateway", layer=2, priority="critical", phase=2,
        prefix="acg", domain="ERP",
        dependencies=["ledger", "invoice", "payment", "tax"],
        entities=["AccountingSync", "MappingRule"],
        value_objects=["ExternalAccountCode", "SyncBatch"],
        enums={"AccountingProvider": ["XERO", "QUICKBOOKS", "PEAK", "FLOWACCOUNT"]},
        invariants=[
            "Mapping 1:1 (internal account ↔ external)",
            "Sync idempotent (same ref = skip)",
            "Batch ≤ 1000 entries",
        ],
        events=["AccountingSynced", "MappingCreated", "SyncFailed", "ReconciliationNeeded"],
        tables=["tenant_{prefix}.accounting_syncs", "tenant_{prefix}.mapping_rules"],
        special_rules=[
            "OAuth2 to external providers",
            "Retry with exponential backoff",
            "Reconciliation report",
        ],
    ),
    ModuleMeta(
        name="tax", layer=2, priority="critical", phase=2,
        prefix="tax", domain="ERP",
        dependencies=["money", "product", "customer", "audit"],
        entities=["TaxRate", "TaxRule", "TaxReport"],
        value_objects=["TaxRatePercent", "TaxBase", "TaxAmount"],
        enums={"TaxType": ["VAT", "WHT", "EXCISE", "IMPORT_DUTY"]},
        invariants=[
            "VAT rate 0-100%",
            "WHT rate 0-100%",
            "Tax base >= 0",
            "Rule effective date range valid",
        ],
        events=["TaxCalculated", "TaxReportGenerated", "TaxRuleUpdated", "WHTIssued"],
        tables=["tenant_{prefix}.tax_rates", "tenant_{prefix}.tax_rules", "tenant_{prefix}.tax_reports"],
        special_rules=[
            "Thai VAT 7% default",
            "WHT 1%, 3%, 5% ตามประเภท",
            "ภ.พ.30 / ภ.ง.ด.53 reports",
            "Reverse charge for imports",
        ],
    ),
    ModuleMeta(
        name="reconciliation", layer=2, priority="critical", phase=1,
        prefix="rec", domain="ERP",
        dependencies=["ledger", "payment", "audit"],
        entities=["BankStatement", "Reconciliation", "MatchRule"],
        value_objects=["StatementLine", "MatchScore"],
        enums={"MatchStatus": ["MATCHED", "UNMATCHED", "DISPUTED"]},
        invariants=[
            "`sum(statement_lines) == statement.closing_balance`",
            "Match score 0-1",
            "Auto-match threshold ≥ 0.95",
        ],
        events=["StatementImported", "MatchFound", "DiscrepancyFound", "ReconciliationCompleted"],
        tables=["tenant_{prefix}.bank_statements", "tenant_{prefix}.reconciliations",
                "tenant_{prefix}.match_rules"],
        special_rules=[
            "CSV/MT940/OFX import",
            "Fuzzy matching (amount + date + ref)",
            "Manual override with reason",
        ],
    ),

    # ─── LAYER 3: GOODS PATH (12) ───────────────────────
    ModuleMeta(
        name="inventory", layer=3, priority="critical", phase=1,
        prefix="invt", domain="Goods",
        dependencies=["product", "warehouse", "lot", "audit", "idempotency"],
        entities=["InventoryItem", "StockMovement"],
        value_objects=["Quantity", "ReservedQty", "AvailableQty"],
        enums={"MovementType": ["IN", "OUT", "TRANSFER", "ADJUST", "RESERVE", "RELEASE"]},
        invariants=[
            "**`available = on_hand - reserved`**",
            "`available >= 0` (no negative stock)",
            "Movement qty ≠ 0",
            "Ledger sum = current stock",
        ],
        events=["StockIn", "StockOut", "StockReserved", "StockReleased", "StockAdjusted", "LowStockAlert"],
        tables=["tenant_{prefix}.inventory_items", "tenant_{prefix}.stock_movements"],
        special_rules=[
            "FIFO/LIFO/Weighted-average costing",
            "Multi-warehouse",
            "Reservation timeout (15 min)",
            "Cycle count support",
        ],
    ),
    ModuleMeta(
        name="warehouse", layer=3, priority="critical", phase=1,
        prefix="wh", domain="Goods",
        dependencies=["audit"],
        entities=["Warehouse", "Bin", "Zone", "Location"],
        value_objects=["BinCode", "Capacity", "Coordinates"],
        enums={"WarehouseType": ["MAIN", "BRANCH", "COLD_STORAGE", "TRANSIT"]},
        invariants=[
            "Bin code unique ต่อ warehouse",
            "Capacity > 0",
            "Zone bin count ≤ capacity",
        ],
        events=["WarehouseCreated", "BinAssigned", "BinCapacityExceeded", "WarehouseDeactivated"],
        tables=["tenant_{prefix}.warehouses", "tenant_{prefix}.bins", "tenant_{prefix}.zones"],
        special_rules=[
            "Hierarchical: warehouse → zone → bin",
            "Pick-path optimization",
            "Temperature zone support",
        ],
    ),
    ModuleMeta(
        name="lot", layer=3, priority="critical", phase=1,
        prefix="lot", domain="Goods",
        dependencies=["product", "inventory", "traceability"],
        entities=["Lot", "SerialNumber"],
        value_objects=["LotNumber", "ExpiryDate", "ManufactureDate"],
        enums={"LotStatus": ["ACTIVE", "QUARANTINE", "EXPIRED", "RECALLED"]},
        invariants=[
            "Lot number unique ต่อ product",
            "Expiry > manufacture date",
            "FEFO enforcement",
        ],
        events=["LotCreated", "LotExpired", "LotQuarantined", "LotRecalled"],
        tables=["tenant_{prefix}.lots", "tenant_{prefix}.serial_numbers"],
        special_rules=[
            "FEFO picking (First Expired First Out)",
            "Recall propagation",
            "Traceability 2-way (forward/backward)",
        ],
    ),
    ModuleMeta(
        name="production", layer=3, priority="critical", phase=1,
        prefix="prodn", domain="Production",
        dependencies=["inventory", "recipe", "lot", "quality", "audit", "idempotency"],
        entities=["ProductionOrder", "WorkOrder", "ProductionLine"],
        value_objects=["BatchSize", "YieldRate", "CycleTime"],
        enums={"ProductionStatus": ["PLANNED", "RELEASED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]},
        invariants=[
            "`input_qty >= output_qty * recipe_ratio`",
            "Yield rate 0-100%",
            "Production order linked to lot",
        ],
        events=["ProductionStarted", "ProductionCompleted", "YieldRecorded", "ScrapRecorded"],
        tables=["tenant_{prefix}.production_orders", "tenant_{prefix}.work_orders",
                "tenant_{prefix}.production_lines"],
        special_rules=[
            "MRP (Material Requirements Planning)",
            "Backflush vs manual issue",
            "Backorder handling",
        ],
    ),
    ModuleMeta(
        name="recipe", layer=3, priority="high", phase=1,
        prefix="rcp", domain="Production",
        dependencies=["product", "production"],
        entities=["Recipe", "RecipeIngredient", "BOM"],
        value_objects=["IngredientQty", "YieldRatio", "Step"],
        enums={"RecipeType": ["MANUFACTURING", "ASSEMBLY", "FOOD", "CHEMICAL"]},
        invariants=[
            "Ingredient qty > 0",
            "Recipe total cost = sum(ingredient costs)",
            "Version immutable after use",
        ],
        events=["RecipeCreated", "RecipeUpdated", "RecipeVersioned", "BOMExploded"],
        tables=["tenant_{prefix}.recipes", "tenant_{prefix}.recipe_ingredients",
                "tenant_{prefix}.bom_versions"],
        special_rules=[
            "Versioning (immutable)",
            "Scaling (batch size)",
            "Sub-recipes (nested BOM)",
            "By-product + co-product",
        ],
    ),
    ModuleMeta(
        name="quality", layer=3, priority="high", phase=1,
        prefix="qlty", domain="Production",
        dependencies=["production", "lot", "audit"],
        entities=["QualityCheck", "Inspection", "NonConformance"],
        value_objects=["TestResult", "AcceptanceCriteria", "SampleSize"],
        enums={"QualityStatus": ["PASS", "FAIL", "CONDITIONAL", "PENDING"]},
        invariants=[
            "Pass rate 0-100%",
            "Sample size > 0",
            "Failed check → quarantine",
        ],
        events=["QualityCheckStarted", "QualityCheckPassed", "QualityCheckFailed", "NCRCreated"],
        tables=["tenant_{prefix}.quality_checks", "tenant_{prefix}.inspections",
                "tenant_{prefix}.non_conformances"],
        special_rules=[
            "AQL sampling (ISO 2859)",
            "SPC charts (control limits)",
            "CAPA workflow",
        ],
    ),
    ModuleMeta(
        name="waste", layer=3, priority="high", phase=1,
        prefix="wst", domain="Production",
        dependencies=["inventory", "production", "audit"],
        entities=["WasteRecord", "WasteType", "DisposalMethod"],
        value_objects=["WasteQty", "DisposalCost", "Reason"],
        enums={"WasteCategory": ["SCRAP", "EXPIRED", "DAMAGED", "BYPRODUCT"]},
        invariants=[
            "Waste qty > 0",
            "Waste qty ≤ input qty",
            "Disposal cost >= 0",
        ],
        events=["WasteRecorded", "WasteDisposed", "WasteReductionTargetMissed"],
        tables=["tenant_{prefix}.waste_records", "tenant_{prefix}.waste_types",
                "tenant_{prefix}.disposal_methods"],
        special_rules=[
            "Environmental compliance",
            "Waste-to-value (byproduct)",
            "Cost allocation to production",
        ],
    ),
    ModuleMeta(
        name="procurement", layer=3, priority="high", phase=1,
        prefix="proc", domain="Goods",
        dependencies=["supplier", "product", "inventory", "audit", "idempotency"],
        entities=["PurchaseOrder", "POLine", "GoodsReceipt"],
        value_objects=["PONumber", "POTotal", "LeadTime"],
        enums={"POStatus": ["DRAFT", "APPROVED", "SENT", "PARTIAL", "RECEIVED", "CLOSED", "CANCELLED"]},
        invariants=[
            "`sum(lines) == po.total`",
            "Received qty ≤ ordered qty",
            "Approval required ถ้า total > threshold",
        ],
        events=["POCreated", "POApproved", "POReceived", "POPartialReceived", "POCancelled"],
        tables=["tenant_{prefix}.purchase_orders", "tenant_{prefix}.po_lines",
                "tenant_{prefix}.goods_receipts"],
        special_rules=[
            "3-way match (PO ↔ GR ↔ Invoice)",
            "Approval workflow (multi-level)",
            "Blanket PO support",
        ],
    ),
    ModuleMeta(
        name="traceability", layer=3, priority="critical", phase=2,
        prefix="trc", domain="Goods",
        dependencies=["lot", "production", "inventory"],
        entities=["TraceEvent", "TraceLink"],
        value_objects=["TraceCode", "ChainNode", "Genealogy"],
        enums={"TraceDirection": ["FORWARD", "BACKWARD"]},
        invariants=[
            "ทุก link ต้อง valid + immutable",
            "Forward trace: raw → finished",
            "Backward trace: finished → raw",
        ],
        events=["TraceEventRecorded", "TraceChainBuilt", "RecallInitiated", "RecallCompleted"],
        tables=["tenant_{prefix}.trace_events", "tenant_{prefix}.trace_links"],
        special_rules=[
            "GS1 EPCIS compliance",
            "Graph traversal (recursive CTE)",
            "Recall within 4 ชั่วโมง",
        ],
    ),
    ModuleMeta(
        name="agriculture", layer=3, priority="high", phase=4,
        prefix="agr", domain="🌾 เกษตร",
        dependencies=["crop", "soil", "irrigation", "iot", "forecast", "inventory", "traceability"],
        entities=["Farm", "Plot", "Harvest"],
        value_objects=["PlotArea", "YieldRate", "Season"],
        enums={"PlotStatus": ["IDLE", "PLANTED", "GROWING", "HARVESTED", "FALLOW"]},
        invariants=[
            "Plot area > 0",
            "Yield ≥ 0",
            "Harvest qty ≤ expected_yield × 1.5",
        ],
        events=["FarmCreated", "PlotPlanted", "CropHarvested", "YieldRecorded", "DiseaseDetected"],
        tables=["tenant_{prefix}.farms", "tenant_{prefix}.plots", "tenant_{prefix}.harvests"],
        special_rules=[
            "Weather integration",
            "Satellite imagery (NDVI)",
            "Yield prediction (ML)",
        ],
    ),
    ModuleMeta(
        name="crop", layer=3, priority="high", phase=4,
        prefix="crp", domain="🌾 เกษตร",
        dependencies=["agriculture", "soil", "iot"],
        entities=["Crop", "CropCycle", "Variety"],
        value_objects=["GrowthStage", "PlantingDate", "ExpectedYield"],
        enums={
            "CropType": ["RICE", "VEGETABLE", "FRUIT", "HERB"],
            "GrowthStage": ["SEED", "SPROUT", "VEGETATIVE", "FLOWERING", "FRUITING", "MATURITY"],
        },
        invariants=[
            "Growth stage sequential",
            "Planting date ≤ today",
            "Cycle duration > 0",
        ],
        events=["CropPlanted", "GrowthStageAdvanced", "CropReadyForHarvest"],
        tables=["tenant_{prefix}.crops", "tenant_{prefix}.crop_cycles", "tenant_{prefix}.varieties"],
        special_rules=[
            "Growing Degree Days (GDD) tracking",
            "Phenology model",
            "Variety recommendation",
        ],
    ),
    ModuleMeta(
        name="soil", layer=3, priority="high", phase=4,
        prefix="sol", domain="🌾 เกษตร",
        dependencies=["agriculture", "crop", "iot"],
        entities=["SoilTest", "SoilProfile", "FertilizerPlan"],
        value_objects=["NPK", "pH", "OrganicMatter", "CEC"],
        enums={"SoilType": ["SANDY", "LOAMY", "CLAY", "SILT"]},
        invariants=[
            "pH 0-14",
            "NPK >= 0",
            "Test date recent (≤ 6 months for recommendation)",
        ],
        events=["SoilTested", "FertilizerRecommended", "NutrientDeficiencyDetected"],
        tables=["tenant_{prefix}.soil_tests", "tenant_{prefix}.soil_profiles",
                "tenant_{prefix}.fertilizer_plans"],
        special_rules=[
            "Lab integration",
            "Nutrient balance calculation",
            "Organic certification tracking",
        ],
    ),
    ModuleMeta(
        name="irrigation", layer=3, priority="high", phase=4,
        prefix="irr", domain="🌾 เกษตร",
        dependencies=["agriculture", "iot", "crop"],
        entities=["IrrigationSchedule", "IrrigationEvent", "Valve"],
        value_objects=["FlowRate", "Duration", "WaterVolume"],
        enums={"IrrigationType": ["DRIP", "SPRINKLER", "FLOOD", "PIVOT"]},
        invariants=[
            "Flow rate > 0",
            "Duration > 0",
            "Water volume ≤ daily quota",
        ],
        events=["IrrigationStarted", "IrrigationCompleted", "ValveOpened", "WaterQuotaExceeded"],
        tables=["tenant_{prefix}.irrigation_schedules", "tenant_{prefix}.irrigation_events",
                "tenant_{prefix}.valves"],
        special_rules=[
            "Soil moisture sensor integration",
            "ET (evapotranspiration) calculation",
            "Auto-scheduling based on weather",
        ],
    ),

    # ─── LAYER 4: OPERATIONS (13) ───────────────────────
    ModuleMeta(
        name="transport", layer=4, priority="high", phase=4,
        prefix="trn", domain="Logistics",
        dependencies=["order", "delivery", "gps", "audit"],
        entities=["TransportOrder", "Vehicle", "Driver"],
        value_objects=["Route", "Distance", "FuelCost"],
        enums={"TransportStatus": ["PLANNED", "LOADING", "IN_TRANSIT", "DELIVERED", "CANCELLED"]},
        invariants=[
            "Distance > 0",
            "Vehicle capacity ≥ load weight",
            "Driver license valid",
        ],
        events=["TransportPlanned", "VehicleDispatched", "GoodsLoaded", "TransportCompleted"],
        tables=["tenant_{prefix}.transport_orders", "tenant_{prefix}.vehicles", "tenant_{prefix}.drivers"],
        special_rules=[
            "Load optimization",
            "Multi-stop routing",
            "Fuel cost tracking",
        ],
    ),
    ModuleMeta(
        name="delivery", layer=4, priority="high", phase=4,
        prefix="dlv", domain="Logistics",
        dependencies=["order", "transport", "customer", "gps"],
        entities=["Delivery", "DeliveryItem", "ProofOfDelivery"],
        value_objects=["TrackingNumber", "DeliveryWindow", "Signature"],
        enums={"DeliveryStatus": ["PENDING", "ASSIGNED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "FAILED"]},
        invariants=[
            "Tracking number unique",
            "Delivery window valid",
            "POD required for completed",
        ],
        events=["DeliveryCreated", "DeliveryAssigned", "OutForDelivery", "DeliveryCompleted", "DeliveryFailed"],
        tables=["tenant_{prefix}.deliveries", "tenant_{prefix}.delivery_items",
                "tenant_{prefix}.proofs_of_delivery"],
        special_rules=[
            "Real-time tracking",
            "Customer notification (SMS/LINE)",
            "Failed delivery → retry",
        ],
    ),
    ModuleMeta(
        name="route", layer=4, priority="high", phase=4,
        prefix="rte", domain="Logistics",
        dependencies=["transport", "delivery", "gps"],
        entities=["Route", "RouteStop", "RoutePlan"],
        value_objects=["Waypoint", "EstimatedTime", "Sequence"],
        enums={"RouteOptimization": ["SHORTEST", "FASTEST", "CHEAPEST"]},
        invariants=[
            "Stop sequence valid (no duplicate positions)",
            "Total distance ≥ direct distance",
            "Vehicle capacity respected",
        ],
        events=["RoutePlanned", "RouteOptimized", "RouteDeviated", "RouteCompleted"],
        tables=["tenant_{prefix}.routes", "tenant_{prefix}.route_stops", "tenant_{prefix}.route_plans"],
        special_rules=[
            "VRP solver (OR-Tools)",
            "Traffic integration",
            "Time window constraints",
        ],
    ),
    ModuleMeta(
        name="gps", layer=4, priority="high", phase=4,
        prefix="gps", domain="IoT",
        dependencies=["transport", "iot", "monitoring"],
        entities=["GpsTrack", "Geofence", "LocationPoint"],
        value_objects=["Coordinates", "Speed", "Heading"],
        enums={"GeofenceEvent": ["ENTER", "EXIT", "DWELL"]},
        invariants=[
            "Latitude -90..90, Longitude -180..180",
            "Speed ≥ 0",
            "Timestamp monotonic",
        ],
        events=["LocationUpdated", "GeofenceEntered", "GeofenceExited", "SpeedViolation"],
        tables=["tenant_{prefix}.gps_tracks (TimescaleDB hypertable)", "tenant_{prefix}.geofences"],
        special_rules=[
            "TimescaleDB / InfluxDB",
            "Downsampling (1s → 1min → 1hr)",
            "Retention 90 วัน",
        ],
    ),
    ModuleMeta(
        name="retail", layer=4, priority="high", phase=4,
        prefix="rtl", domain="Retail",
        dependencies=["inventory", "pos", "pricing", "customer"],
        entities=["Store", "StoreInventory", "Planogram"],
        value_objects=["StoreCode", "ShelfLocation", "ShelfCapacity"],
        enums={"StoreType": ["FLAGSHIP", "STANDARD", "KIOSK", "POPUP"]},
        invariants=[
            "Store code unique",
            "Shelf capacity > 0",
            "Shelf stock ≤ capacity",
        ],
        events=["StoreOpened", "StockReplenished", "PlanogramChanged", "ShelfOutOfStock"],
        tables=["tenant_{prefix}.stores", "tenant_{prefix}.store_inventory", "tenant_{prefix}.planograms"],
        special_rules=[
            "Store-to-store transfer",
            "Replenishment from DC",
            "Shelf-life management",
        ],
    ),
    ModuleMeta(
        name="pos", layer=4, priority="high", phase=4,
        prefix="pos", domain="Retail",
        dependencies=["retail", "product", "payment", "inventory", "shift", "audit"],
        entities=["PosTransaction", "PosLine", "Receipt"],
        value_objects=["ReceiptNumber", "CashDrawer", "Change"],
        enums={"PosStatus": ["OPEN", "SUSPENDED", "COMPLETED", "VOIDED", "REFUNDED"]},
        invariants=[
            "`sum(lines) == transaction.total`",
            "Payment ≥ total",
            "Shift required for transaction",
        ],
        events=["TransactionStarted", "TransactionCompleted", "ReceiptPrinted", "TransactionVoided"],
        tables=["tenant_{prefix}.pos_transactions", "tenant_{prefix}.pos_lines", "tenant_{prefix}.receipts"],
        special_rules=[
            "Offline mode (sync when online)",
            "Multiple payment methods",
            "Loyalty integration",
        ],
    ),
    ModuleMeta(
        name="shift", layer=4, priority="high", phase=4,
        prefix="shf", domain="Retail",
        dependencies=["pos", "user", "audit"],
        entities=["Shift", "CashDrawer", "ShiftSummary"],
        value_objects=["OpeningFloat", "ClosingCount", "Variance"],
        enums={"ShiftStatus": ["OPEN", "CLOSED", "DISCREPANCY"]},
        invariants=[
            "Opening float ≥ 0",
            "`closing = opening + sales - refunds`",
            "One open shift per cashier",
        ],
        events=["ShiftOpened", "ShiftClosed", "DiscrepancyFound", "CashDropRecorded"],
        tables=["tenant_{prefix}.shifts", "tenant_{prefix}.cash_drawers", "tenant_{prefix}.shift_summaries"],
        special_rules=[
            "Blind close option",
            "Cash drop tracking",
            "End-of-day report",
        ],
    ),
    ModuleMeta(
        name="line_channel", layer=4, priority="high", phase=4,
        prefix="lnc", domain="CRM",
        dependencies=["customer", "crm", "campaign"],
        entities=["LineChannel", "LineUser", "MessageTemplate"],
        value_objects=["ChannelId", "UserId", "RichMenuId"],
        enums={"MessageType": ["TEXT", "IMAGE", "FLEX", "TEMPLATE", "STICKER"]},
        invariants=[
            "Channel ID unique",
            "Line user 1:1 กับ customer (ถ้า link)",
            "Message ≤ 5000 chars",
        ],
        events=["UserFollowed", "UserUnfollowed", "MessageReceived", "MessageSent"],
        tables=["tenant_{prefix}.line_channels", "tenant_{prefix}.line_users",
                "tenant_{prefix}.message_templates"],
        special_rules=[
            "LINE Messaging API",
            "Webhook handling",
            "Rich menu management",
            "Broadcast rate limit",
        ],
    ),
    ModuleMeta(
        name="promotion", layer=4, priority="medium", phase=4,
        prefix="prm", domain="CRM",
        dependencies=["pricing", "product", "customer", "audit"],
        entities=["Promotion", "PromotionRule", "PromotionUsage"],
        value_objects=["DiscountValue", "Condition", "UsageLimit"],
        enums={"PromotionType": ["PERCENT", "FIXED", "BOGO", "BUNDLE", "FREE_SHIPPING"]},
        invariants=[
            "Discount ≤ product price",
            "Start date < end date",
            "Usage limit ≥ 0",
            "No conflicting promotions (same product + period)",
        ],
        events=["PromotionCreated", "PromotionApplied", "PromotionExpired", "UsageLimitReached"],
        tables=["tenant_{prefix}.promotions", "tenant_{prefix}.promotion_rules",
                "tenant_{prefix}.promotion_usages"],
        special_rules=[
            "Stackable vs exclusive",
            "Customer segment targeting",
            "Anti-abuse (max 1 per customer)",
        ],
    ),
    ModuleMeta(
        name="loyalty", layer=4, priority="medium", phase=4,
        prefix="loy", domain="CRM",
        dependencies=["customer", "pos", "promotion"],
        entities=["LoyaltyAccount", "PointsTransaction", "Reward", "Tier"],
        value_objects=["Points", "TierLevel", "ExpiryDate"],
        enums={"PointsType": ["EARN", "REDEEM", "EXPIRE", "ADJUST"]},
        invariants=[
            "Points balance ≥ 0",
            "Redeem ≤ balance",
            "Tier upgrade based on cumulative points",
        ],
        events=["AccountCreated", "PointsEarned", "PointsRedeemed", "TierUpgraded", "PointsExpired"],
        tables=["tenant_{prefix}.loyalty_accounts", "tenant_{prefix}.points_transactions",
                "tenant_{prefix}.rewards", "tenant_{prefix}.tiers"],
        special_rules=[
            "Points expiry (12 เดือน)",
            "Tier benefits (discount, free shipping)",
            "Birthday bonus",
        ],
    ),
    ModuleMeta(
        name="crm", layer=4, priority="high", phase=5,
        prefix="crm", domain="📞 CRM",
        dependencies=["customer", "line_channel", "campaign", "invoice"],
        entities=["Lead", "Deal", "Activity"],
        value_objects=["PipelineStage", "DealValue", "Probability"],
        enums={
            "LeadStatus": ["NEW", "CONTACTED", "QUALIFIED", "CONVERTED", "LOST"],
            "DealStage": ["PROSPECTING", "QUALIFICATION", "PROPOSAL", "NEGOTIATION", "WON", "LOST"],
        },
        invariants=[
            "Deal value ≥ 0",
            "Probability 0-100",
            "Deal stage forward-only",
            "Lead → Customer 1:1",
        ],
        events=["LeadCreated", "LeadConverted", "DealCreated", "DealWon", "DealLost"],
        tables=["tenant_{prefix}.leads", "tenant_{prefix}.deals", "tenant_{prefix}.activities"],
        special_rules=[
            "Sales pipeline view",
            "Activity logging (call, email, meeting)",
            "Forecast by stage",
        ],
    ),
    ModuleMeta(
        name="campaign", layer=4, priority="medium", phase=5,
        prefix="cmp", domain="CRM",
        dependencies=["crm", "line_channel", "customer", "promotion"],
        entities=["Campaign", "CampaignSegment", "CampaignMessage"],
        value_objects=["Audience", "Schedule", "Budget"],
        enums={"CampaignStatus": ["DRAFT", "SCHEDULED", "RUNNING", "PAUSED", "COMPLETED"]},
        invariants=[
            "Budget ≥ 0",
            "Start date < end date",
            "Audience size ≤ segment size",
        ],
        events=["CampaignCreated", "CampaignStarted", "CampaignCompleted", "CampaignPaused"],
        tables=["tenant_{prefix}.campaigns", "tenant_{prefix}.campaign_segments",
                "tenant_{prefix}.campaign_messages"],
        special_rules=[
            "A/B testing",
            "Multi-channel (LINE, SMS, Email)",
            "Conversion tracking",
            "ROI report",
        ],
    ),
    ModuleMeta(
        name="support", layer=4, priority="medium", phase=5,
        prefix="spt", domain="CRM",
        dependencies=["customer", "line_channel", "user", "audit"],
        entities=["Ticket", "TicketMessage", "Sla"],
        value_objects=["TicketNumber", "Priority", "ResponseTime"],
        enums={
            "TicketStatus": ["OPEN", "IN_PROGRESS", "WAITING", "RESOLVED", "CLOSED"],
            "Priority": ["LOW", "MEDIUM", "HIGH", "URGENT"],
        },
        invariants=[
            "Ticket number unique",
            "SLA response time > 0",
            "Closed ticket immutable",
        ],
        events=["TicketCreated", "TicketAssigned", "TicketResolved", "SlaBreached"],
        tables=["tenant_{prefix}.tickets", "tenant_{prefix}.ticket_messages", "tenant_{prefix}.slas"],
        special_rules=[
            "Auto-assignment (round-robin)",
            "SLA escalation",
            "CSAT survey after resolve",
        ],
    ),

    # ─── LAYER 5: INTELLIGENCE (7) ──────────────────────
    ModuleMeta(
        name="reporting", layer=5, priority="critical", phase=5,
        prefix="rpt", domain="BI",
        dependencies=["ledger", "order", "inventory", "analytics"],
        entities=["Report", "ReportTemplate", "ReportExecution"],
        value_objects=["ReportFormat", "Parameters", "Schedule"],
        enums={"ReportType": ["FINANCIAL", "SALES", "INVENTORY", "OPERATIONAL"]},
        invariants=[
            "Report template versioned",
            "Execution result immutable",
            "Schedule valid cron",
        ],
        events=["ReportGenerated", "ReportScheduled", "ReportFailed", "ReportShared"],
        tables=["tenant_{prefix}.reports", "tenant_{prefix}.report_templates",
                "tenant_{prefix}.report_executions"],
        special_rules=[
            "PDF/Excel/CSV export",
            "Scheduled delivery (email)",
            "Row-level security in reports",
        ],
    ),
    ModuleMeta(
        name="analytics", layer=5, priority="high", phase=5,
        prefix="ana", domain="BI",
        dependencies=["reporting", "order", "customer", "product"],
        entities=["Metric", "Dimension", "DataMart"],
        value_objects=["Aggregation", "TimeGrain", "Filter"],
        enums={"MetricType": ["COUNT", "SUM", "AVG", "RATIO", "PERCENTILE"]},
        invariants=[
            "Metric definition unique",
            "Aggregation consistent",
            "Data freshness ≤ 1 hour",
        ],
        events=["DataMartBuilt", "MetricCalculated", "AnomalyDetected"],
        tables=["tenant_{prefix}.metrics", "tenant_{prefix}.dimensions", "tenant_{prefix}.data_marts"],
        special_rules=[
            "OLAP cube",
            "Drill-down support",
            "Materialized views",
        ],
    ),
    ModuleMeta(
        name="forecast", layer=5, priority="high", phase=5,
        prefix="fcs", domain="BI",
        dependencies=["analytics", "production", "inventory", "agriculture"],
        entities=["Forecast", "ForecastModel"],
        value_objects=["Prediction", "Confidence", "MAPE"],
        enums={"ForecastMethod": ["LSTM", "PROPHET", "XGBOOST", "ARIMA", "ENSEMBLE"]},
        invariants=[
            "MAPE < 20% (target)",
            "Prediction ≥ 0",
            "Confidence 0-1",
        ],
        events=["ForecastGenerated", "ForecastUpdated", "ForecastAccuracyDropped"],
        tables=["tenant_{prefix}.forecasts", "tenant_{prefix}.forecast_models"],
        special_rules=[
            "Model retraining weekly",
            "Backtesting before deploy",
            "Ensemble voting",
        ],
    ),
    ModuleMeta(
        name="kpi", layer=5, priority="high", phase=5,
        prefix="kpi", domain="BI",
        dependencies=["analytics", "reporting", "user"],
        entities=["Kpi", "KpiTarget", "KpiActual"],
        value_objects=["TargetValue", "ActualValue", "AchievementRate"],
        enums={"KpiFrequency": ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"]},
        invariants=[
            "Target > 0",
            "Achievement rate = actual / target × 100",
            "Actual ≥ 0",
        ],
        events=["KpiCreated", "KpiTargetSet", "KpiAchieved", "KpiMissed"],
        tables=["tenant_{prefix}.kpis", "tenant_{prefix}.kpi_targets", "tenant_{prefix}.kpi_actuals"],
        special_rules=[
            "Cascading KPI (company → dept → individual)",
            "Balanced scorecard",
            "Alert on threshold breach",
        ],
    ),
    ModuleMeta(
        name="satisfaction", layer=5, priority="medium", phase=5,
        prefix="sat", domain="CRM",
        dependencies=["customer", "support", "order"],
        entities=["Survey", "Response", "NpsScore"],
        value_objects=["Rating", "NpsScore", "CsatScore"],
        enums={
            "SurveyType": ["NPS", "CSAT", "CES"],
            "Sentiment": ["POSITIVE", "NEUTRAL", "NEGATIVE"],
        },
        invariants=[
            "Rating 1-5",
            "NPS -100..100",
            "Response rate 0-100%",
        ],
        events=["SurveySent", "ResponseReceived", "NpsCalculated", "DetractorDetected"],
        tables=["tenant_{prefix}.surveys", "tenant_{prefix}.responses", "tenant_{prefix}.nps_scores"],
        special_rules=[
            "Auto-trigger after delivery",
            "Detractor follow-up workflow",
            "Trend analysis",
        ],
    ),
    ModuleMeta(
        name="recommendation", layer=5, priority="medium", phase=5,
        prefix="rcm", domain="CRM",
        dependencies=["customer", "order", "product", "analytics"],
        entities=["Recommendation", "UserProfile", "ItemSimilarity"],
        value_objects=["Score", "Rank", "Context"],
        enums={"RecAlgorithm": ["COLLABORATIVE", "CONTENT_BASED", "HYBRID"]},
        invariants=[
            "Score 0-1",
            "Top-N ≤ 100",
            "No out-of-stock recommendations",
        ],
        events=["RecommendationGenerated", "RecommendationClicked", "RecommendationPurchased"],
        tables=["tenant_{prefix}.recommendations", "tenant_{prefix}.user_profiles",
                "tenant_{prefix}.item_similarities"],
        special_rules=[
            "Cold-start handling",
            "Real-time vs batch",
            "A/B testing framework",
        ],
    ),
    ModuleMeta(
        name="oee", layer=5, priority="high", phase=5,
        prefix="oee", domain="Factory",
        dependencies=["production", "iot", "maintenance", "quality"],
        entities=["OeeRecord", "Equipment", "DowntimeEvent"],
        value_objects=["Availability", "Performance", "Quality", "OeeScore"],
        enums={"DowntimeReason": ["BREAKDOWN", "SETUP", "MATERIAL", "SCHEDULED"]},
        invariants=[
            "Availability 0-100%",
            "Performance 0-100%",
            "Quality 0-100%",
            "**OEE = A × P × Q**",
        ],
        events=["OeeCalculated", "DowntimeRecorded", "OeeBelowTarget", "EquipmentFailure"],
        tables=["tenant_{prefix}.oee_records", "tenant_{prefix}.equipment",
                "tenant_{prefix}.downtime_events"],
        special_rules=[
            "Real-time from IoT sensors",
            "World-class OEE ≥ 85%",
            "Six Big Losses analysis",
        ],
    ),

    # ─── LAYER 6: MONITORING (8) ────────────────────────
    ModuleMeta(
        name="iot", layer=6, priority="high", phase=4,
        prefix="iot", domain="IoT",
        dependencies=["monitoring", "alerting", "events"],
        entities=["SensorReading", "Sensor", "Threshold"],
        value_objects=["Measurement", "Unit", "Timestamp"],
        enums={"SensorType": ["TEMPERATURE", "HUMIDITY", "CO2", "LIGHT", "PH", "EC"]},
        invariants=[
            "Reading in valid range ต่อ sensor type",
            "Threshold min < max",
            "Timestamp monotonic",
        ],
        events=["SensorReadingReceived", "ThresholdExceeded", "SensorOffline"],
        tables=["tenant_{prefix}.sensor_readings (TimescaleDB)", "tenant_{prefix}.sensors",
                "tenant_{prefix}.thresholds"],
        special_rules=[
            "MQTT ingestion",
            "TimescaleDB hypertable",
            "Downsampling + retention",
            "Edge computing support",
        ],
    ),
    ModuleMeta(
        name="cctv", layer=6, priority="medium", phase=4,
        prefix="cctv", domain="IoT",
        dependencies=["monitoring", "alerting", "iot"],
        entities=["Camera", "Recording", "MotionEvent"],
        value_objects=["StreamUrl", "StoragePath", "MotionScore"],
        enums={"CameraStatus": ["ONLINE", "OFFLINE", "RECORDING", "ERROR"]},
        invariants=[
            "Retention ≥ 30 วัน",
            "Recording size ≤ quota",
            "Stream URL valid RTSP/RTMP",
        ],
        events=["MotionDetected", "CameraOffline", "RecordingStarted", "RecordingArchived"],
        tables=["tenant_{prefix}.cameras", "tenant_{prefix}.recordings", "tenant_{prefix}.motion_events"],
        special_rules=[
            "RTSP → HLS transcoding",
            "Object detection (YOLO)",
            "Time-lapse generation",
            "S3 cold storage",
        ],
    ),
    ModuleMeta(
        name="monitoring", layer=6, priority="critical", phase=1,
        prefix="mon", domain="Ops",
        dependencies=["alerting", "events"],
        entities=["HealthCheck", "Metric", "Incident"],
        value_objects=["MetricValue", "Threshold", "Duration"],
        enums={"HealthStatus": ["HEALTHY", "DEGRADED", "UNHEALTHY"]},
        invariants=[
            "Health check interval > 0",
            "Response time ≥ 0",
            "Incident duration ≥ 0",
        ],
        events=["HealthCheckFailed", "IncidentOpened", "IncidentResolved", "DegradedPerformance"],
        tables=["tenant_{prefix}.health_checks", "tenant_{prefix}.metrics", "tenant_{prefix}.incidents"],
        special_rules=[
            "Prometheus/Grafana integration",
            "4 golden signals (latency, traffic, errors, saturation)",
            "SLO/SLI tracking",
        ],
    ),
    ModuleMeta(
        name="backup", layer=6, priority="critical", phase=1,
        prefix="bkp", domain="Ops",
        dependencies=["monitoring", "audit"],
        entities=["BackupJob", "BackupSnapshot", "RestoreRequest"],
        value_objects=["BackupSize", "Checksum", "Retention"],
        enums={
            "BackupType": ["FULL", "INCREMENTAL", "DIFFERENTIAL"],
            "BackupStatus": ["PENDING", "RUNNING", "SUCCESS", "FAILED"],
        },
        invariants=[
            "Retention ≥ 30 วัน",
            "Checksum verified",
            "Test restore monthly",
        ],
        events=["BackupStarted", "BackupCompleted", "BackupFailed", "RestoreCompleted"],
        tables=["tenant_{prefix}.backup_jobs", "tenant_{prefix}.backup_snapshots",
                "tenant_{prefix}.restore_requests"],
        special_rules=[
            "S3/GCS storage",
            "Encryption at rest (KMS)",
            "Point-in-time recovery (PITR)",
            "Cross-region replication",
        ],
    ),
    ModuleMeta(
        name="alerting", layer=6, priority="high", phase=1,
        prefix="alr", domain="Ops",
        dependencies=["monitoring", "notification", "events"],
        entities=["Alert", "AlertRule", "NotificationChannel"],
        value_objects=["Severity", "EscalationPolicy", "Silence"],
        enums={
            "Severity": ["INFO", "WARNING", "ERROR", "CRITICAL"],
            "AlertStatus": ["FIRING", "RESOLVED", "SILENCED"],
        },
        invariants=[
            "Severity valid",
            "Escalation timeout > 0",
            "Silence duration valid",
        ],
        events=["AlertFired", "AlertResolved", "AlertSilenced", "EscalationTriggered"],
        tables=["tenant_{prefix}.alerts", "tenant_{prefix}.alert_rules",
                "tenant_{prefix}.notification_channels"],
        special_rules=[
            "Deduplication (5-min window)",
            "Escalation policy",
            "Multi-channel (Slack, Email, SMS, LINE)",
            "On-call rotation",
        ],
    ),
    ModuleMeta(
        name="audit_viewer", layer=6, priority="high", phase=2,
        prefix="auv", domain="Compliance",
        dependencies=["audit", "user", "tenant_context"],
        entities=["AuditView", "SavedFilter"],
        value_objects=["FilterCriteria", "TimeRange"],
        enums={"AuditCategory": ["SECURITY", "FINANCIAL", "DATA", "SYSTEM"]},
        invariants=[
            "Read-only (no write operations)",
            "Filter criteria valid",
            "Export audit logged",
        ],
        events=["AuditQueried", "AuditExported", "SuspiciousActivityDetected"],
        tables=["tenant_{prefix}.audit_views", "tenant_{prefix}.saved_filters"],
        special_rules=[
            "Full-text search (Elasticsearch)",
            "Compliance reports (SOC2, ISO 27001)",
            "Immutable view (WORM storage)",
        ],
    ),
    ModuleMeta(
        name="maintenance", layer=6, priority="high", phase=5,
        prefix="mnt", domain="Factory",
        dependencies=["production", "iot", "oee", "audit"],
        entities=["MaintenanceOrder", "Asset", "MaintenanceSchedule"],
        value_objects=["MttrMttf", "Downtime", "Cost"],
        enums={"MaintenanceType": ["PREVENTIVE", "CORRECTIVE", "PREDICTIVE", "EMERGENCY"]},
        invariants=[
            "Asset unique",
            "MTTR ≥ 0, MTTF > 0",
            "Schedule interval > 0",
        ],
        events=["MaintenanceScheduled", "MaintenanceStarted", "MaintenanceCompleted",
                "AssetFailurePredicted"],
        tables=["tenant_{prefix}.maintenance_orders", "tenant_{prefix}.assets",
                "tenant_{prefix}.maintenance_schedules"],
        special_rules=[
            "CMMS integration",
            "Predictive (ML from IoT)",
            "Spare parts inventory",
            "MTTR/MTBF tracking",
        ],
    ),
    ModuleMeta(
        name="energy", layer=6, priority="medium", phase=5,
        prefix="eng", domain="Factory",
        dependencies=["iot", "production", "oee", "analytics"],
        entities=["EnergyReading", "Meter", "EnergyTarget"],
        value_objects=["Kwh", "PeakDemand", "CarbonFootprint"],
        enums={"EnergySource": ["GRID", "SOLAR", "GENERATOR", "BATTERY"]},
        invariants=[
            "Energy ≥ 0",
            "Reading interval consistent",
            "Peak demand ≥ avg demand",
        ],
        events=["EnergyMeasured", "PeakDemandExceeded", "EnergyTargetMissed",
                "SolarGenerationStarted"],
        tables=["tenant_{prefix}.energy_readings", "tenant_{prefix}.meters",
                "tenant_{prefix}.energy_targets"],
        special_rules=[
            "Real-time monitoring",
            "Load balancing",
            "Carbon accounting (Scope 1/2/3)",
            "ISO 50001 compliance",
        ],
    ),

    # ─── LAYER 7: TEMPLATES (3) ─────────────────────────
    ModuleMeta(
        name="health", layer=7, priority="critical", phase=1,
        prefix="hlt", domain="Ops",
        dependencies=[],
        entities=["HealthStatus"],
        value_objects=["ComponentHealth", "Version"],
        enums={"ComponentStatus": ["UP", "DOWN", "DEGRADED"]},
        invariants=[
            "Response time < 1s",
            "Read-only endpoint",
        ],
        events=["HealthChecked", "ComponentDown", "ComponentRecovered"],
        tables=["ไม่มี (stateless)"],
        special_rules=[
            "`/health`, `/ready`, `/live` endpoints",
            "Kubernetes probe compatible",
            "Check: DB, Redis, Kafka, external APIs",
        ],
    ),
    ModuleMeta(
        name="example", layer=7, priority="low", phase=1,
        prefix="ex", domain="Reference",
        dependencies=["ทุกอย่าง (ใช้เป็นตัวอย่าง)"],
        entities=["Example"],
        value_objects=["ExampleValue"],
        enums={"ExampleStatus": ["NEW", "USED", "ARCHIVED"]},
        invariants=[
            "ใช้แสดง pattern ครบทั้ง 4 layers",
        ],
        events=["ExampleCreated"],
        tables=["tenant_{prefix}.examples"],
        special_rules=[
            "ใช้เป็น reference implementation",
            "มี comment 2 ภาษา",
            "Coverage 100%",
        ],
    ),
    ModuleMeta(
        name="blank", layer=7, priority="low", phase=1,
        prefix="blk", domain="Template",
        dependencies=[],
        entities=["{Entity} (placeholder)"],
        value_objects=["{VO} (placeholder)"],
        enums={"{Enum}": ["{VALUE1}", "{VALUE2}"]},
        invariants=["`{module_specific_invariants}`"],
        events=["{Module}Created", "{Module}Updated", "{Module}Deleted"],
        tables=["tenant_{prefix}.{table_name}"],
        special_rules=[
            "พร้อมให้ replace `{placeholders}` ทั้งหมด",
            "ทุกที่ที่มี `{module_name}` → replace",
            "ทุกที่ที่มี `{Entity}` → replace",
        ],
    ),
]


# ─────────────────────────────────────────────────────────
# Template Renderer
# ─────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """# AI Prompt — Module `{name}`

> **Master Template:** ดู `docs/template_modules.md` v{version}
> **ใช้ boilerplate 16 Python + 3 SQL + 4 Tests จาก master template**
> **Layer:** {layer} · **Priority:** {priority_emoji} · **Phase:** {phase}

---

## 📋 Metadata

| Field | Value |
|---|---|
| **Module Name** | `{name}` |
| **Layer** | {layer} — {layer_title} |
| **Priority** | {priority_emoji} `{priority}` |
| **Phase** | {phase} |
| **Prefix** | `{prefix}` |
| **มิติธุรกิจ** | {domain} |
| **Dependencies** | {dependencies} |

---

## 🎯 Domain Concepts

### Entities
{entities_list}

### Value Objects
{value_objects_list}

### Enums
{enums_list}

---

## 📐 Invariants (Business Rules)

{invariants_list}

---

## 📡 Domain Events

{events_list}

---

## 🗄️ Tables

{tables_list}

---

## ⚙️ Special Rules

{special_rules_list}

{notes_section}
---

## 📦 Output (23 ไฟล์)

| หมวด | จำนวน | รายละเอียด |
|---|---|---|
| 🐍 Python | 16 | 4 layers × 4 files |
| 🗄️ SQL | 3 | V001 create / V002 seed / V003 rollback |
| 🧪 Tests | 4 | unit / integration / property / manual |
| **รวม** | **23** | ตาม Master Template v{version} |

**โฟลเดอร์ output:**
```
app/modules/{name}/
db/migrations/V001__create_{name}.sql
db/migrations/V002__seed_{name}.sql
db/migrations/V003__rollback_{name}.sql
tests/unit/test_{name}.py
tests/integration/test_{name}_repository.py
tests/property/test_{name}_invariants.py
tests/manual/manual_test_{name}.md
```

---

## ✅ Checklist

- [ ] Domain layer ไม่ import framework
- [ ] Repository ใช้ `flush()` ไม่ใช่ `commit()`
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] มี SQL migration ครบ 3 ไฟล์ (`V001`, `V002`, `V003`)
- [ ] มี RLS policy (`tenant_id = current_setting('app.current_tenant')`)
- [ ] มี CHECK constraints ตาม invariants ด้านบน
- [ ] Unit test coverage ≥ 90%
- [ ] Integration test ผ่าน (testcontainers)
- [ ] Property-based test ผ่าน (hypothesis)
- [ ] Manual test cases ครบ 8 scenarios
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบทุก action
- [ ] Read-back verification ครบ

---

> **Generated by:** `scripts/generate_prompts.py`
> **Author:** {author} ({email})
> **Version:** {version}
> **Date:** {today}
"""


def _bullet(items: list[str], indent: str = "-") -> str:
    if not items:
        return "_ไม่มี_"
    return "\n".join(f"{indent} {it}" for it in items)


def _enums_block(enums: dict[str, list[str]]) -> str:
    if not enums:
        return "_ไม่มี_"
    lines: list[str] = []
    for name, values in enums.items():
        values_str = ", ".join(values)
        lines.append(f"- **`{name}`**: `({values_str})`")
    return "\n".join(lines)


def render_prompt(meta: ModuleMeta) -> str:
    notes_section = ""
    if meta.notes:
        notes_section = f"\n---\n\n## 📝 Notes\n\n{meta.notes}\n"

    return PROMPT_TEMPLATE.format(
        name=meta.name,
        version=VERSION,
        author=AUTHOR,
        email=EMAIL,
        today=TODAY,
        layer=meta.layer,
        layer_title=LAYER_TITLES[meta.layer],
        priority=meta.priority,
        priority_emoji=meta.priority_emoji,
        phase=meta.phase,
        prefix=meta.prefix,
        domain=meta.domain,
        dependencies=", ".join(meta.dependencies) if meta.dependencies else "_ไม่มี_",
        entities_list=_bullet([f"`{e}`" for e in meta.entities]),
        value_objects_list=_bullet([f"`{v}`" for v in meta.value_objects]),
        enums_list=_enums_block(meta.enums),
        invariants_list=_bullet(meta.invariants),
        events_list=_bullet([f"`{e}`" for e in meta.events]),
        tables_list=_bullet([f"`{t}`" for t in meta.tables]),
        special_rules_list=_bullet(meta.special_rules),
        notes_section=notes_section,
    )


# ─────────────────────────────────────────────────────────
# Writer
# ─────────────────────────────────────────────────────────

def write_prompt(meta: ModuleMeta, output_root: Path, *,
                 force: bool = False, dry_run: bool = False) -> tuple[bool, Path]:
    """Returns (written, path)."""
    dir_path = output_root / meta.dir_name
    file_path = dir_path / meta.file_name

    if file_path.exists() and not force:
        return False, file_path

    content = render_prompt(meta)

    if not dry_run:
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return True, file_path


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="generate_prompts",
        description="Auto-generate AI prompt files for 57 modules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/generate_prompts.py\n"
            "  python scripts/generate_prompts.py --dry-run\n"
            "  python scripts/generate_prompts.py --layer 2 --force\n"
            "  python scripts/generate_prompts.py --output docs/prompts --module ledger\n"
        ),
    )
    p.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("docs/prompts"),
        help="Output root directory (default: docs/prompts)",
    )
    p.add_argument(
        "--layer", "-l",
        type=int,
        choices=sorted(LAYER_NAMES.keys()),
        default=None,
        help="Filter by layer (0-7). Default: all layers",
    )
    p.add_argument(
        "--module", "-m",
        type=str,
        default=None,
        help="Filter by module name (exact match)",
    )
    p.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing files",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing",
    )
    p.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress per-file output",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    modules = MODULES
    if args.layer is not None:
        modules = [m for m in modules if m.layer == args.layer]
    if args.module:
        modules = [m for m in modules if m.name == args.module]

    if not modules:
        print("❌ No modules matched filter.", file=sys.stderr)
        return 1

    written = skipped = 0
    output_root = args.output.resolve()

    print(f"🚀 Generating prompts into: {output_root}")
    print(f"   Modules: {len(modules)} | Force: {args.force} | Dry-run: {args.dry_run}\n")

    for meta in modules:
        ok, path = write_prompt(meta, output_root,
                                force=args.force, dry_run=args.dry_run)
        rel = path.relative_to(output_root.parent) if path.is_relative_to(output_root.parent) else path
        if ok:
            written += 1
            if not args.quiet:
                tag = "[dry-run]" if args.dry_run else "[created]"
                print(f"  {tag:10} {rel}")
        else:
            skipped += 1
            if not args.quiet:
                print(f"  [skipped]  {rel}")

    print(f"\n📊 Summary")
    print(f"   ✅ Written : {written}")
    print(f"   ⏭️  Skipped : {skipped} (use --force to overwrite)")
    print(f"   📁 Root    : {output_root}")

    if args.dry_run:
        print("\n⚠️  Dry-run mode — no files were actually written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 🚀 วิธีใช้

### 1. วางไฟล์

```bash
mkdir -p scripts
# วางโค้ดด้านบนเป็น scripts/generate_prompts.py
```

### 2. รันแบบ dry-run ก่อน

```bash
python scripts/generate_prompts.py --dry-run
```

### 3. รันจริง

```bash
# สร้างทั้งหมด 57 ไฟล์
python scripts/generate_prompts.py

# เฉพาะ Layer 2 (Money Path)
python scripts/generate_prompts.py --layer 2

# เฉพาะ module เดียว
python scripts/generate_prompts.py --module ledger --force
```

### 4. ตรวจสอบ

```bash
find docs/prompts -name "*.md" | sort
# → 57 files across layer-0-core/ ... layer-7-templates/
```

### 5. ทดสอบ idempotency

```bash
# รันครั้งที่ 2 ควร skip ทั้งหมด
python scripts/generate_prompts.py
# → 57 skipped (use --force to overwrite)
```

---

## 📊 Output Structure

```
docs/prompts/
├── layer-0-core/           (5 files)
│   ├── tenant_context.md
│   ├── audit.md
│   ├── idempotency.md
│   ├── config.md
│   └── events.md
├── layer-1-foundation/     (8 files)
├── layer-2-money-path/     (6 files)
├── layer-3-goods-path/     (12 files)
├── layer-4-operations/     (13 files)
├── layer-5-intelligence/   (7 files)
├── layer-6-monitoring/     (8 files)
└── layer-7-templates/      (3 files)
```

---

## ✅ Features

| Feature | รายละเอียด |
|---|---|
| **Data-driven** | Metadata ทั้ง 57 modules ฝังใน `MODULES` list เดียว |
| **Idempotent** | รันซ้ำไม่ทับไฟล์ ยกเว้น `--force` |
| **Filterable** | `--layer`, `--module` |
| **Dry-run** | ดู preview ก่อนเขียน |
| **Type-safe** | `@dataclass` + `Literal` types |
| **Auto-format** | Bullet lists, enum code blocks, markdown tables |
| **Zero deps** | ใช้แค่ stdlib (Path, argparse, dataclasses) |
| **Extensible** | เพิ่ม module ใหม่ = เพิ่ม `ModuleMeta(...)` 1 entry |

---

## 🔧 วิธีเพิ่ม Module ใหม่

```python
# ใน MODULES list
ModuleMeta(
    name="my_new_module",
    layer=3, priority="high", phase=4,
    prefix="mnm", domain="Custom",
    dependencies=["inventory"],
    entities=["MyEntity"],
    value_objects=["MyVO"],
    enums={"MyStatus": ["ACTIVE", "INACTIVE"]},
    invariants=["My invariant"],
    events=["MyEntityCreated"],
    tables=["tenant_{prefix}.my_entities"],
    special_rules=["My rule"],
),
```

แล้วรัน `python scripts/generate_prompts.py --module my_new_module`

---

ต้องการให้ผมเพิ่ม **feature เสริม** อะไรไหมครับ เช่น:

- 📄 Export เป็น JSON/YAML metadata ด้วย (`--export-json`)
- 🔍 Validate ว่า dependencies ของทุก module มีอยู่จริง
- 🌏 Template 2 ภาษา (TH/EN) switchable
- 📊 Generate `README.md` index อัตโนมัติ