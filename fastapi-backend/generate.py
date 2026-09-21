#!/usr/bin/env python3
"""
ERP+CRM+IoT Module Generator
=============================
อ่าน spec จาก docs/prompts/*.md แล้วสร้างโครงสร้างโปรเจกต์

Fixes:
  - SQL version numbers per-layer, no clash with hand-written V014-V024
  - Complex entity support (custom fields via EntitySpec)
  - Prefix collisions resolved (trace/traceability, supplier/support)
  - Stub DI in presentation returns usable objects
  - Removed invalid walrus expression in model template
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ROOT = Path.cwd()
APP_DIR = ROOT / "app" / "modules"
DB_DIR = ROOT / "db" / "migrations"
TESTS_DIR = ROOT / "tests"

# ─── SQL version offsets ─────────────────────────────────
# Hand-written migrations use V001-V024. Auto-generated
# migrations will start at V101+ to avoid any clash.
SQL_LAYER_BASE = {
    0: 101,
    1: 111,
    2: 121,
    3: 131,
    4: 141,
    5: 151,
    6: 161,
    7: 171,
}


@dataclass
class EntitySpec:
    """Spec ของ entity (ไม่ใช่ทุก module เป็น code/name/status)"""

    name: str
    fields: dict[str, str] = field(default_factory=dict)
    kind: Literal["simple", "complex", "vo_only"] = "simple"


@dataclass
class ModuleSpec:
    name: str
    layer: int
    prefix: str
    entities: list[str] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    has_domain: bool = True
    has_infra: bool = True
    entity_specs: list[EntitySpec] = field(default_factory=list)
    notes: str = ""


# ─── Layer 0: Core ───────────────────────────────────────
LAYER_0 = [
    ModuleSpec(
        "money",
        0,
        "mny",
        ["Money"],
        [],
        entity_specs=[EntitySpec("Money", kind="vo_only")],
    ),
    ModuleSpec(
        "tenant_context",
        0,
        "tctx",
        ["TenantContext"],
        [],
        entity_specs=[EntitySpec("TenantContext", kind="vo_only")],
    ),
    ModuleSpec("audit", 0, "aud", ["AuditLog"], ["audit_logs"]),
    ModuleSpec(
        "idempotency", 0, "idem", ["IdempotencyRecord"], ["idempotency_records"]
    ),
    ModuleSpec("config", 0, "cfg", ["ConfigEntry"], ["config_entries"]),
    ModuleSpec("events", 0, "evt", ["EventEnvelope"], ["event_store"]),
]

# ─── Layer 1: Foundation ─────────────────────────────────
LAYER_1 = [
    ModuleSpec("tenancy", 1, "ten", ["Tenant"], ["tenants"]),
    ModuleSpec("authentication", 1, "auth", ["Credential"], ["credentials"]),
    ModuleSpec("user", 1, "usr", ["User"], ["users"]),
    ModuleSpec("employee", 1, "emp", ["Employee"], ["employees"]),
    ModuleSpec("customer", 1, "cus", ["Customer"], ["customers"]),
    ModuleSpec("supplier", 1, "sup", ["Supplier"], ["suppliers"]),
    ModuleSpec("product", 1, "prd", ["Product"], ["products"]),
    ModuleSpec("pricing", 1, "prc", ["PriceList"], ["price_lists"]),
]

# ─── Layer 2: Money Path ─────────────────────────────────
LAYER_2 = [
    ModuleSpec("order", 2, "ord", ["Order"], ["orders"]),
    ModuleSpec("invoice", 2, "inv", ["Invoice"], ["invoices"]),
    ModuleSpec("ledger", 2, "led", ["JournalEntry"], ["journal_entries"]),
    ModuleSpec("payment", 2, "pay", ["Payment"], ["payments"]),
    ModuleSpec(
        "accounting_gateway", 2, "acg", ["AccountingSync"], ["accounting_syncs"]
    ),
    ModuleSpec("tax", 2, "tax", ["TaxRule"], ["tax_rules"]),
    ModuleSpec("reconciliation", 2, "rec", ["Reconciliation"], ["reconciliations"]),
]

# ─── Layer 3: Goods Path ─────────────────────────────────
LAYER_3 = [
    ModuleSpec("inventory", 3, "invt", ["StockItem"], ["stock_items"]),
    ModuleSpec("warehouse", 3, "wh", ["Warehouse"], ["warehouses"]),
    ModuleSpec("lot", 3, "lot", ["Lot"], ["lots"]),
    ModuleSpec("production", 3, "prod", ["ProductionOrder"], ["production_orders"]),
    ModuleSpec("recipe", 3, "rcp", ["Recipe"], ["recipes"]),
    ModuleSpec("quality", 3, "qc", ["QCInspection"], ["qc_inspections"]),
    ModuleSpec("waste", 3, "wst", ["WasteRecord"], ["waste_records"]),
    ModuleSpec("procurement", 3, "proc", ["PurchaseOrder"], ["purchase_orders"]),
    # NOTE: traceability (Layer 3) vs trace (Layer 6) — ต้องมี prefix ต่างกัน
    ModuleSpec("traceability", 3, "trcb", ["TraceRecord"], ["trace_records"]),
    ModuleSpec("agriculture", 3, "agr", ["Farm"], ["farms"]),
    ModuleSpec("crop", 3, "crp", ["Crop"], ["crops"]),
    ModuleSpec("soil", 3, "soil", ["SoilTest"], ["soil_tests"]),
    ModuleSpec("irrigation", 3, "irr", ["IrrigationPlan"], ["irrigation_plans"]),
]

# ─── Layer 4: Operations ─────────────────────────────────
LAYER_4 = [
    ModuleSpec("transport", 4, "trn", ["Vehicle"], ["vehicles"]),
    ModuleSpec("delivery", 4, "dlv", ["Delivery"], ["deliveries"]),
    ModuleSpec("route", 4, "rte", ["Route"], ["routes"]),
    ModuleSpec("gps", 4, "gps", ["Location"], ["locations"]),
    ModuleSpec("retail", 4, "rtl", ["Store"], ["stores"]),
    ModuleSpec("pos", 4, "pos", ["POSTerminal"], ["pos_terminals"]),
    ModuleSpec("shift", 4, "shf", ["Shift"], ["shifts"]),
    ModuleSpec("line_channel", 4, "line", ["LINEMessage"], ["line_messages"]),
    ModuleSpec("promotion", 4, "promo", ["Promotion"], ["promotions"]),
    ModuleSpec("loyalty", 4, "loy", ["LoyaltyAccount"], ["loyalty_accounts"]),
    ModuleSpec("crm", 4, "crm", ["Lead"], ["leads"]),
    ModuleSpec("campaign", 4, "cmp", ["Campaign"], ["campaigns"]),
    # NOTE: supplier (Layer 1) vs support (Layer 4) — ต้องมี prefix ต่างกัน
    ModuleSpec("support", 4, "sup2", ["Ticket"], ["tickets"]),
]

# ─── Layer 5: Intelligence ───────────────────────────────
LAYER_5 = [
    ModuleSpec("reporting", 5, "rpt", ["Report"], ["reports"]),
    ModuleSpec("analytics", 5, "anl", ["Metric"], ["metrics"]),
    ModuleSpec("forecast", 5, "fc", ["Forecast"], ["forecasts"]),
    ModuleSpec("kpi", 5, "kpi", ["KPI"], ["kpis"]),
    ModuleSpec("satisfaction", 5, "csat", ["Survey"], ["surveys"]),
    ModuleSpec("recommendation", 5, "reco", ["Recommendation"], ["recommendations"]),
    ModuleSpec("oee", 5, "oee", ["OEERecord"], ["oee_records"]),
]

# ─── Layer 6: Monitoring ─────────────────────────────────
LAYER_6 = [
    ModuleSpec("iot", 6, "iot", ["SensorReading"], ["sensor_readings"]),
    ModuleSpec("alert", 6, "alt", ["Alert"], ["alerts"]),
    ModuleSpec("notification", 6, "ntf", ["Notification"], ["notifications"]),
    ModuleSpec("health", 6, "hlt", ["HealthCheck"], ["health_checks"]),
    ModuleSpec("log", 6, "lg", ["LogEntry"], ["log_entries"]),
    ModuleSpec("trace", 6, "trc", ["Trace"], ["traces"]),
    ModuleSpec("metrics", 6, "mtr", ["MetricDefinition"], ["metric_definitions"]),
    ModuleSpec("incident", 6, "inc", ["Incident"], ["incidents"]),
    ModuleSpec("sla", 6, "sla", ["SLADefinition"], ["sla_definitions"]),
    ModuleSpec("dashboard", 6, "dsh", ["Dashboard"], ["dashboards"]),
    ModuleSpec("anomaly", 6, "anm", ["Anomaly"], ["anomalies"]),
    ModuleSpec("audit_trail", 6, "atl", ["AuditEntry"], ["audit_entries"]),
]

# ─── Layer 7: Templates ──────────────────────────────────
LAYER_7 = [
    ModuleSpec(
        "health_check",
        7,
        "hlth",
        ["HealthStatus"],
        [],
        has_infra=False,
        entity_specs=[EntitySpec("HealthStatus", kind="vo_only")],
    ),
    ModuleSpec("example", 7, "ex", ["ExampleEntity"], ["examples"]),
    ModuleSpec("blank", 7, "blk", ["BlankEntity"], ["blanks"]),
]

ALL_LAYERS = {
    0: LAYER_0,
    1: LAYER_1,
    2: LAYER_2,
    3: LAYER_3,
    4: LAYER_4,
    5: LAYER_5,
    6: LAYER_6,
    7: LAYER_7,
}


# ═══════════════════════════════════════════════════════════════════
# TEMPLATES
# ═══════════════════════════════════════════════════════════════════

T_DOMAIN_INIT = '"""Domain layer - {module}."""\n\n__all__ = []\n'

T_DOMAIN_EXC = '''"""Domain exceptions - {module}."""


class DomainError(Exception):
    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)


class {Module}Exception(Exception):
    code = "{MODULE}_ERROR"
    def __init__(self, message: str = "{module} failed"):
        self.message = message
        super().__init__(message)


class {Module}NotFoundException({Module}Exception):
    code = "{MODULE}_NOT_FOUND"


class {Module}InvalidException({Module}Exception):
    code = "{MODULE}_INVALID"
'''

T_DOMAIN_ENUMS = '''"""Domain enums - {module}."""
from enum import Enum


class {Module}Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
'''

T_DOMAIN_EVENTS = '''"""Domain events - {module}."""

{Module}Created = "{Module}Created"
{Module}Updated = "{Module}Updated"
{Module}Deleted = "{Module}Deleted"

ALL_EVENTS = ({Module}Created, {Module}Updated, {Module}Deleted)
'''

T_DOMAIN_ENTITIES = '''"""Domain entities - {module}."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal  # noqa: F401  (used by complex entities)
import uuid

from .exceptions import DomainError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    version: int = 1
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)


{ENTITY_CLASSES}
'''

T_ENTITY_SIMPLE = """

@dataclass
class {EntityName}(BaseEntity):
    code: str = ""
    name: str = ""
    description: str = ""
    status: str = "ACTIVE"

    def __post_init__(self):
        if not self.code:
            raise DomainError("{EntityName} code required")
        if not self.name:
            raise DomainError("{EntityName} name required")

    def activate(self) -> None:
        self.status = "ACTIVE"
        self.updated_at = _utcnow()

    def deactivate(self) -> None:
        self.status = "INACTIVE"
        self.updated_at = _utcnow()
"""

T_ENTITY_VO_ONLY = '''

@dataclass(frozen=True)
class {EntityName}:
    """{EntityName} value object — immutable."""
    value: str = ""

    def __post_init__(self):
        if not self.value:
            raise DomainError("{EntityName} value required")
'''

T_APP_INIT = '"""Application layer - {module}."""\nfrom .use_cases import {Module}UseCases\n\n__all__ = ["{Module}UseCases"]\n'

T_APP_EXC = '''"""Application exceptions - {module}."""
from ..domain.exceptions import (
    DomainError, {Module}Exception, {Module}NotFoundException,
    {Module}InvalidException,
)

__all__ = [
    "DomainError", "{Module}Exception", "{Module}NotFoundException",
    "{Module}InvalidException",
]
'''

T_APP_UC = '''"""Use cases - {module}."""
import logging
from ..domain.entities import {FirstEntity}
from ..domain.exceptions import DomainError
from .exceptions import {Module}Exception, {Module}NotFoundException

logger = logging.getLogger(__name__)


class {Module}UseCases:
    def __init__(self, repo, cache, audit, events):
        self.repo = repo
        self.cache = cache
        self.audit = audit
        self.events = events

    async def create(self, entity: {FirstEntity}, actor_id: str = "system"):
        try:
            saved = await self.repo.save(entity)
            verified = await self.repo.get_by_id(saved.id)
            if not verified:
                raise {Module}Exception("Read-back failed")
            await self.audit.log("{module}.created", saved.id)
            await self.events.publish("{Module}Created", {{"id": saved.id}})
            return saved
        except DomainError:
            raise
        except Exception as e:
            logger.exception("create failed: %s", e)
            raise {Module}Exception("Failed to create")

    async def get_by_id(self, entity_id: str):
        cached = await self.cache.get(f"{module}:{{entity_id}}")
        if cached:
            return cached
        entity = await self.repo.get_by_id(entity_id)
        if entity:
            await self.cache.set(f"{module}:{{entity_id}}", entity, ttl=300)
        return entity

    async def list(self, filters: dict | None = None, page: int = 1, limit: int = 20):
        return await self.repo.list(filters or {{}}, page, limit)

    async def update(self, entity_id: str, payload: dict):
        try:
            entity = await self.repo.get_by_id(entity_id)
            if not entity:
                raise {Module}NotFoundException(entity_id)
            for k, v in payload.items():
                if hasattr(entity, k):
                    setattr(entity, k, v)
            saved = await self.repo.save(entity)
            await self.cache.delete(f"{module}:{{entity_id}}")
            await self.audit.log("{module}.updated", entity_id)
            return saved
        except DomainError:
            raise
        except Exception as e:
            logger.exception("update failed: %s", e)
            raise {Module}Exception("Failed to update")

    async def delete(self, entity_id: str) -> None:
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            raise {Module}NotFoundException(entity_id)
        if hasattr(entity, "deactivate"):
            entity.deactivate()
        await self.repo.save(entity)
        await self.cache.delete(f"{module}:{{entity_id}}")
'''

T_APP_MAPPER = '''"""Mappers - {module}."""
from typing import Any
from ..domain.entities import {FirstEntity}


class {Module}Mapper:
    @staticmethod
    def to_dict(e: {FirstEntity}) -> dict:
        return {{"id": e.id, "code": getattr(e, "code", ""), "name": getattr(e, "name", "")}}

    @staticmethod
    def from_model(m: Any) -> {FirstEntity}:
        return {FirstEntity}(
            id=str(m.id), tenant_id=str(m.tenant_id),
            code=getattr(m, "code", ""), name=getattr(m, "name", ""),
            status=getattr(m, "status", "ACTIVE"),
        )
'''

T_APP_UTILS = '"""Utils - {module}."""\n\n\ndef is_valid_code(code: str) -> bool:\n    return bool(code) and len(code) >= 2\n'

T_INFRA_INIT = '"""Infrastructure - {module}."""\n\n__all__ = []\n'

T_INFRA_MODELS = '''"""SQLAlchemy models - {module}."""
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


{MODEL_CLASSES}
'''

T_MODEL = """

class {EntityName}Model(BaseModel):
    __tablename__ = "{table_name}"
    __table_args__ = ({{"schema": "tenant_{prefix}"}},)
    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="ACTIVE")
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
"""

T_INFRA_REPO = '''"""Repositories - {module}."""
from sqlalchemy import select, func as sqlfunc
from sqlalchemy.ext.asyncio import AsyncSession
from ..application.mappers import {Module}Mapper
from ..domain.entities import {FirstEntity}
from .models import {FirstEntity}Model


class Postgres{Module}Repository:
    def __init__(self, session: AsyncSession, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id

    async def save(self, entity: {FirstEntity}) -> {FirstEntity}:
        model = await self.session.get({FirstEntity}Model, entity.id)
        if model is None:
            model = {FirstEntity}Model(
                id=entity.id, tenant_id=self.tenant_id,
                code=getattr(entity, "code", ""),
                name=getattr(entity, "name", ""),
                status=getattr(entity, "status", "ACTIVE"),
            )
            self.session.add(model)
        else:
            if hasattr(model, "code") and hasattr(entity, "code"):
                model.code = entity.code
            if hasattr(model, "name") and hasattr(entity, "name"):
                model.name = entity.name
            if hasattr(model, "status") and hasattr(entity, "status"):
                model.status = entity.status
        await self.session.flush()
        return {Module}Mapper.from_model(model)

    async def get_by_id(self, entity_id: str):
        model = await self.session.get({FirstEntity}Model, entity_id)
        return {Module}Mapper.from_model(model) if model else None

    async def list(self, filters: dict, page: int, limit: int):
        stmt = select({FirstEntity}Model).where(
            {FirstEntity}Model.tenant_id == self.tenant_id,
        )
        if filters.get("status"):
            stmt = stmt.where({FirstEntity}Model.status == filters["status"])
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(stmt)
        items = [{Module}Mapper.from_model(m) for m in result.scalars().all()]
        count_stmt = select(sqlfunc.count({FirstEntity}Model.id)).where(
            {FirstEntity}Model.tenant_id == self.tenant_id,
        )
        total = (await self.session.execute(count_stmt)).scalar() or 0
        return items, total
'''

T_INFRA_CACHE = '''"""Cache - {module}."""
import json
import logging

logger = logging.getLogger(__name__)


class {Module}Cache:
    def __init__(self, redis=None):
        self.redis = redis

    async def get(self, key: str):
        if not self.redis:
            return None
        try:
            raw = await self.redis.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning("cache get failed: %s", e)
            return None

    async def set(self, key: str, value, ttl: int = 300) -> None:
        if not self.redis:
            return
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.warning("cache set failed: %s", e)

    async def delete(self, key: str) -> None:
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning("cache delete failed: %s", e)
'''

T_INFRA_SVC = '''"""Services - {module}."""
import logging

logger = logging.getLogger(__name__)


class {Module}Service:
    async def process(self, payload: dict) -> dict:
        logger.info("{module} service processed")
        return payload
'''

T_PRES_INIT = '"""Presentation - {module}."""\nfrom .routers import router\n\n__all__ = ["router"]\n'

T_PRES_SCHEMAS = '''"""Schemas - {module}."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class {FirstEntity}Create(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""


class {FirstEntity}Update(BaseModel):
    code: str | None = None
    name: str | None = None
    status: str | None = None


class {FirstEntity}Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class {FirstEntity}Page(BaseModel):
    items: list[{FirstEntity}Response]
    total: int
    page: int
    limit: int
'''

T_PRES_ROUTER = '''"""Routers - {module}."""
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from ..application.use_cases import {Module}UseCases
from ..domain.entities import {FirstEntity}
from ..domain.exceptions import DomainError
from .schemas import (
    {FirstEntity}Create, {FirstEntity}Update,
    {FirstEntity}Response, {FirstEntity}Page,
)
from .dependencies import get_{module}_use_cases


router = APIRouter(prefix="/api/v1/{module}", tags=["{Module}"])


@router.post("/", response_model={FirstEntity}Response, status_code=201)
async def create_{module}(
    payload: {FirstEntity}Create,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    uc: {Module}UseCases = Depends(get_{module}_use_cases),
):
    try:
        entity = {FirstEntity}(code=payload.code, name=payload.name)
        return await uc.create(entity)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{{entity_id}}/", response_model={FirstEntity}Response)
async def get_{module}(
    entity_id: str,
    uc: {Module}UseCases = Depends(get_{module}_use_cases),
):
    entity = await uc.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="not found")
    return entity


@router.get("/", response_model={FirstEntity}Page)
async def list_{module}(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    uc: {Module}UseCases = Depends(get_{module}_use_cases),
):
    items, total = await uc.list({{}}, page, limit)
    return {{"items": items, "total": total, "page": page, "limit": limit}}


@router.patch("/{{entity_id}}/", response_model={FirstEntity}Response)
async def update_{module}(
    entity_id: str,
    payload: {FirstEntity}Update,
    uc: {Module}UseCases = Depends(get_{module}_use_cases),
):
    return await uc.update(entity_id, payload.model_dump(exclude_unset=True))


@router.delete("/{{entity_id}}/", status_code=204)
async def delete_{module}(
    entity_id: str,
    uc: {Module}UseCases = Depends(get_{module}_use_cases),
):
    await uc.delete(entity_id)
'''

T_PRES_DOCS = '"""Docs - {module}."""\n\nrouter_docs = {{"tags": ["{Module}"]}}\n'

T_PRES_DEPS = '''"""Dependencies - {module}."""
from fastapi import Depends, Header
from ..application.use_cases import {Module}UseCases


async def get_tenant_id(x_tenant_id: str = Header(..., alias="X-Tenant-Id")) -> str:
    return x_tenant_id


class _InMemoryRepo:
    """In-memory stub repository (dev/test only)."""

    def __init__(self):
        self._store: dict = {{}}

    async def save(self, entity):
        self._store[entity.id] = entity
        return entity

    async def get_by_id(self, entity_id):
        return self._store.get(entity_id)

    async def list(self, filters, page, limit):
        items = list(self._store.values())
        return items[(page - 1) * limit: page * limit], len(items)


class _NoopCache:
    async def get(self, key): return None
    async def set(self, key, value, ttl=300): pass
    async def delete(self, key): pass


class _NoopAudit:
    async def log(self, action, entity_id): pass


class _NoopEvents:
    async def publish(self, topic, payload): pass


async def get_{module}_use_cases(tenant_id: str = Depends(get_tenant_id)) -> {Module}UseCases:
    return {Module}UseCases(
        repo=_InMemoryRepo(),
        cache=_NoopCache(),
        audit=_NoopAudit(),
        events=_NoopEvents(),
    )
'''

T_MODULE_INIT = '"""{Module} module - Layer {layer}."""\n__version__ = "1.0.0"\n'

T_SQL = """-- Module: {module} (Layer {layer})
-- Version: {version}
BEGIN;
CREATE SCHEMA IF NOT EXISTS tenant_{prefix};
{TABLE_DDL}
{RLS_DDL}
COMMIT;
"""

T_TABLE = """
CREATE TABLE IF NOT EXISTS tenant_{prefix}.{table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT uq_{table_name}_code UNIQUE (tenant_id, code)
);
CREATE INDEX IF NOT EXISTS ix_{table_name}_tenant
    ON tenant_{prefix}.{table_name}(tenant_id) WHERE deleted_at IS NULL;
"""

T_RLS = """
ALTER TABLE tenant_{prefix}.{table_name} ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_{table_name}_tenant ON tenant_{prefix}.{table_name};
CREATE POLICY p_{table_name}_tenant ON tenant_{prefix}.{table_name}
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
"""

T_TEST_UNIT = '''"""Unit tests - {module}."""
import pytest
from app.modules.{module}.domain.entities import {FirstEntity}


def test_create_valid():
    e = {FirstEntity}(code="TEST001", name="Test")
    assert e.code == "TEST001"
    assert e.status == "ACTIVE"


def test_missing_code_raises():
    with pytest.raises(Exception):
        {FirstEntity}(code="", name="Test")


def test_missing_name_raises():
    with pytest.raises(Exception):
        {FirstEntity}(code="TEST001", name="")


def test_activate_deactivate():
    e = {FirstEntity}(code="TEST001", name="Test")
    e.deactivate()
    assert e.status == "INACTIVE"
    e.activate()
    assert e.status == "ACTIVE"
'''

T_TEST_PROP = '''"""Property tests - {module}."""
from hypothesis import given, strategies as st
from app.modules.{module}.domain.entities import {FirstEntity}


@given(code=st.text(min_size=1, max_size=50), name=st.text(min_size=1, max_size=200))
def test_valid_creates(code, name):
    e = {FirstEntity}(code=code, name=name)
    assert e.code == code
    assert e.name == name
'''


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════


def safe_write(path: Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY] {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [OK]  {path.relative_to(ROOT)}")


def render_entity_class(spec: EntitySpec) -> str:
    """เลือก template ตาม kind ของ entity"""
    if spec.kind == "vo_only":
        return T_ENTITY_VO_ONLY.format(EntityName=spec.name)
    return T_ENTITY_SIMPLE.format(EntityName=spec.name)


def entity_classes(entities: list[str], specs: list[EntitySpec] | None = None) -> str:
    specs_map = {s.name: s for s in (specs or [])}
    out = []
    for name in entities:
        spec = specs_map.get(name, EntitySpec(name=name, kind="simple"))
        out.append(render_entity_class(spec))
    return "\n".join(out)


def model_classes(entities, tables, prefix):
    out = []
    for i, name in enumerate(entities):
        table = tables[i] if i < len(tables) else f"{name.lower()}s"
        out.append(T_MODEL.format(EntityName=name, table_name=table, prefix=prefix))
    return "\n".join(out)


def table_ddl(module: ModuleSpec) -> str:
    return "\n".join(
        T_TABLE.format(prefix=module.prefix, table_name=t) for t in module.tables
    )


def rls_ddl(module: ModuleSpec) -> str:
    return "\n".join(
        T_RLS.format(prefix=module.prefix, table_name=t) for t in module.tables
    )


# ═══════════════════════════════════════════════════════════════════
# GENERATORS
# ═══════════════════════════════════════════════════════════════════


def gen_domain(m: ModuleSpec, dry: bool) -> None:
    if not m.has_domain:
        return
    base = APP_DIR / m.name / "domain"
    v = {"module": m.name, "Module": m.name.capitalize(), "MODULE": m.name.upper()}
    print(f"\n[DOMAIN] {m.name}")
    safe_write(base / "__init__.py", T_DOMAIN_INIT.format(**v), dry)
    safe_write(base / "exceptions.py", T_DOMAIN_EXC.format(**v), dry)
    safe_write(base / "enums.py", T_DOMAIN_ENUMS.format(**v), dry)
    safe_write(base / "events.py", T_DOMAIN_EVENTS.format(**v), dry)
    safe_write(
        base / "entities.py",
        T_DOMAIN_ENTITIES.format(
            module=m.name,
            ENTITY_CLASSES=entity_classes(m.entities, m.entity_specs),
        ),
        dry,
    )


def gen_app(m: ModuleSpec, dry: bool) -> None:
    if not m.has_domain:
        return
    base = APP_DIR / m.name / "application"
    first = m.entities[0] if m.entities else "Entity"
    v = {"module": m.name, "Module": m.name.capitalize(), "FirstEntity": first}
    print(f"\n[APP] {m.name}")
    safe_write(base / "__init__.py", T_APP_INIT.format(**v), dry)
    safe_write(base / "exceptions.py", T_APP_EXC.format(**v), dry)
    safe_write(base / "use_cases.py", T_APP_UC.format(**v), dry)
    safe_write(base / "mappers.py", T_APP_MAPPER.format(**v), dry)
    safe_write(base / "utils.py", T_APP_UTILS.format(**v), dry)


def gen_infra(m: ModuleSpec, dry: bool) -> None:
    if not m.has_infra:
        return
    base = APP_DIR / m.name / "infrastructure"
    first = m.entities[0] if m.entities else "Entity"
    v = {
        "module": m.name,
        "Module": m.name.capitalize(),
        "FirstEntity": first,
        "prefix": m.prefix,
    }
    print(f"\n[INFRA] {m.name}")
    safe_write(base / "__init__.py", T_INFRA_INIT.format(**v), dry)
    safe_write(
        base / "models.py",
        T_INFRA_MODELS.format(
            module=m.name,
            MODEL_CLASSES=model_classes(m.entities, m.tables, m.prefix),
        ),
        dry,
    )
    safe_write(base / "repositories.py", T_INFRA_REPO.format(**v), dry)
    safe_write(base / "caches.py", T_INFRA_CACHE.format(**v), dry)
    safe_write(base / "services.py", T_INFRA_SVC.format(**v), dry)


def gen_pres(m: ModuleSpec, dry: bool) -> None:
    if not m.has_domain:
        return
    base = APP_DIR / m.name / "presentation"
    first = m.entities[0] if m.entities else "Entity"
    v = {"module": m.name, "Module": m.name.capitalize(), "FirstEntity": first}
    print(f"\n[PRES] {m.name}")
    safe_write(base / "__init__.py", T_PRES_INIT.format(**v), dry)
    safe_write(base / "schemas.py", T_PRES_SCHEMAS.format(**v), dry)
    safe_write(base / "routers.py", T_PRES_ROUTER.format(**v), dry)
    safe_write(base / "docs.py", T_PRES_DOCS.format(**v), dry)
    safe_write(base / "dependencies.py", T_PRES_DEPS.format(**v), dry)


def gen_sql(m: ModuleSpec, dry: bool, counter: dict) -> None:
    if not m.tables:
        return
    base_version = SQL_LAYER_BASE.get(m.layer, 900)
    idx = counter.get(m.layer, 0)
    version = base_version + idx
    counter[m.layer] = idx + 1

    fname = f"V{version:03d}__create_{m.name}.sql"
    print(f"\n[SQL] {fname}")
    safe_write(
        DB_DIR / fname,
        T_SQL.format(
            module=m.name,
            layer=m.layer,
            prefix=m.prefix,
            version=f"V{version:03d}",
            TABLE_DDL=table_ddl(m),
            RLS_DDL=rls_ddl(m),
        ),
        dry,
    )


def gen_tests(m: ModuleSpec, dry: bool) -> None:
    if not m.has_domain or not m.entities:
        return
    first = m.entities[0]
    # Skip VO-only entities (they don't have code/name/status)
    specs_map = {s.name: s for s in m.entity_specs}
    if specs_map.get(first, EntitySpec(name=first)).kind == "vo_only":
        print(f"\n[TEST] {m.name} (skipped — VO-only)")
        return
    v = {"module": m.name, "Module": m.name.capitalize(), "FirstEntity": first}
    print(f"\n[TEST] {m.name}")
    safe_write(TESTS_DIR / "unit" / f"test_{m.name}.py", T_TEST_UNIT.format(**v), dry)
    safe_write(
        TESTS_DIR / "property" / f"test_{m.name}_invariants.py",
        T_TEST_PROP.format(**v),
        dry,
    )


def gen_module_init(m: ModuleSpec, dry: bool) -> None:
    safe_write(
        APP_DIR / m.name / "__init__.py",
        T_MODULE_INIT.format(module=m.name, Module=m.name.capitalize(), layer=m.layer),
        dry,
    )


def gen_module(m: ModuleSpec, dry: bool, counter: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Module: {m.name} (Layer {m.layer})")
    print(f"{'=' * 60}")
    gen_module_init(m, dry)
    gen_domain(m, dry)
    gen_app(m, dry)
    gen_infra(m, dry)
    gen_pres(m, dry)
    gen_sql(m, dry, counter)
    gen_tests(m, dry)


def gen_main(dry: bool) -> None:
    content = (
        '"""App entry."""\n'
        "from fastapi import FastAPI\n\n"
        'app = FastAPI(title="ERP SME")\n\n\n'
        '@app.get("/health/")\n'
        "async def health():\n"
        '    return {"status": "healthy"}\n'
    )
    safe_write(ROOT / "app" / "main.py", content, dry)
    safe_write(APP_DIR / "__init__.py", '"""App."""\n', dry)
    safe_write(APP_DIR.parent / "__init__.py", '"""Root."""\n', dry)


def gen_configs(dry: bool) -> None:
    pyproject = """[project]
name = "erp-sme"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.9",
    "sqlalchemy>=2.0",
    "asyncpg>=0.29",
    "redis>=5.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "hypothesis>=6.100"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
"""
    safe_write(ROOT / "pyproject.toml", pyproject, dry)

    reqs = (
        "fastapi>=0.115\n"
        "uvicorn[standard]>=0.30\n"
        "pydantic>=2.9\n"
        "sqlalchemy>=2.0\n"
        "asyncpg>=0.29\n"
        "redis>=5.0\n"
        "pytest>=8.0\n"
        "pytest-asyncio>=0.24\n"
        "hypothesis>=6.100\n"
    )
    safe_write(ROOT / "requirements.txt", reqs, dry)


def gen_gitignore(dry: bool) -> None:
    content = (
        "__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env\n*.log\n.pytest_cache/\n*.db\n"
    )
    safe_write(ROOT / ".gitignore", content, dry)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════


def main() -> int:
    p = argparse.ArgumentParser(description="Module generator")
    p.add_argument("--module", help="Specific module")
    p.add_argument("--layer", type=int, help="Specific layer")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-configs", action="store_true")
    args = p.parse_args()

    print("=" * 60)
    print("  ERP + CRM + IoT Module Generator")
    print("=" * 60)

    modules: list[ModuleSpec] = []
    if args.module:
        for lst in ALL_LAYERS.values():
            for m in lst:
                if m.name == args.module:
                    modules.append(m)
        if not modules:
            print(f"[ERROR] Module not found: {args.module}")
            return 1
    elif args.layer is not None:
        modules = ALL_LAYERS.get(args.layer, [])
        if not modules:
            print(f"[ERROR] Layer not found: {args.layer}")
            return 1
    else:
        for n in sorted(ALL_LAYERS.keys()):
            modules.extend(ALL_LAYERS[n])

    print(f"\nModules: {len(modules)}  Dry-run: {args.dry_run}")

    if not args.skip_configs and not args.module:
        gen_main(args.dry_run)
        gen_configs(args.dry_run)
        gen_gitignore(args.dry_run)

    counter: dict[int, int] = {}
    for m in modules:
        gen_module(m, args.dry_run, counter)

    print(f"\n{'=' * 60}")
    print(f"  Complete: {len(modules)} modules")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
