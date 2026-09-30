#!/usr/bin/env python3
"""
create_module_structured_outputs.py — Structured Outputs Module Generator v1.0.0

สร้าง module structured_outputs ตาม Clean Architecture + DDD + Event-Driven
Module: structured_outputs · Prefix: so_ · Schema: public
Layer: 5-Intel · Depends: llm

Actions (9):
  1. create      — สร้าง module structure (4 layers)
  2. sql         — สร้าง SQL migrations V001/V002/V003
  3. alembic     — สร้าง Alembic migration
  4. swagger     — สร้าง OpenAPI docs
  5. postman     — สร้าง Postman collection
  6. update      — อัปเดต app/app.py
  7. update-env  — อัปเดต migrations/env.py
  8. verify      — ตรวจสอบ setup
  9. all         — ทำทุกอย่าง
"""
from __future__ import annotations

import argparse
import io
import json as _json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

# ═══════════════════════════════════════════════════════════════
#  UTF-8 FIX (Windows)
# ═══════════════════════════════════════════════════════════════
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "1.0.0"
SCHEMA = "public"

# ═══════════════════════════════════════════════════════════════
#  MODULE CONFIG
# ═══════════════════════════════════════════════════════════════
MODULE = {
    "name": "structured_outputs",
    "title": "Structured Outputs",
    "layer": "5-Intel",
    "prefix": "so",
    "tag": "StructuredOutputs",
    "tag_desc": "Structured Outputs — JSON Schema enforcement + repair loop",
    "depends": ["llm"],
    "tables": (
        "so_schemas",
        "so_requests",
        "so_outputs",
        "so_validations",
        "so_repairs",
    ),
}

ACTIONS = {
    "create", "sql", "alembic", "swagger", "postman",
    "update", "update-env", "verify", "all", "help",
}


# ═══════════════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════════════
class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; BOLD = "\033[1m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, project_root: Path, force: bool = False):
        self.root = project_root
        self.force = force
        self.written: list[Path] = []
        self.skipped: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.force:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class StructuredOutputsGenerator:
    def __init__(self, project_root: Path, force: bool = False):
        self.cfg = MODULE
        self.module = MODULE["name"]
        self.prefix = MODULE["prefix"]
        self.layer = MODULE["layer"]
        self.tag = MODULE["tag"]
        self.tables = MODULE["tables"]
        self.root = project_root
        self.writer = FileWriter(project_root, force=force)

        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"

    # ═══════════════════════════════════════════════════════════
    #  1. CREATE MODULE
    # ═══════════════════════════════════════════════════════════
    def create_module(self) -> None:
        info(f"[CREATE] {self.module} — {self.cfg['title']}")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN LAYER ─────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} domain layer"""
            from .enums import *      # noqa: F401,F403
            from .events import *     # noqa: F401,F403
            from .exceptions import * # noqa: F401,F403
        '''))

        self.writer.write(f"{base}/enums.py", self._domain_enums())
        self.writer.write(f"{base}/exceptions.py", self._domain_exceptions())
        self.writer.write(f"{base}/events.py", self._domain_events())

        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """structured_outputs value objects"""
            from .schema_spec import SchemaSpec
            from .so_result import SOResult
            from .validation_error import ValidationError

            __all__ = ["SchemaSpec", "SOResult", "ValidationError"]
        '''))

        self.writer.write(f"{base}/value_objects/schema_spec.py", dedent('''\
            """SchemaSpec VO"""
            from __future__ import annotations
            from typing import Any
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.structured_outputs.domain.enums import SOStrategy


            class SchemaSpec(BaseModel):
                """TH: ข้อกำหนด schema | EN: Schema specification"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=100,
                                  pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
                json_schema: dict[str, Any] = Field(default_factory=dict)
                pydantic_model: str = ""
                strict: bool = False
                strategy: SOStrategy = SOStrategy.JSON_MODE
                description: str = ""
        '''))

        self.writer.write(f"{base}/value_objects/so_result.py", dedent('''\
            """SOResult VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.structured_outputs.domain.enums import SOStatus


            class SOResult(BaseModel):
                """TH: ผลลัพธ์การ generate | EN: Structured output result"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                status: SOStatus
                parsed: Optional[dict[str, Any]] = None
                raw_text: str = ""
                is_valid: bool = False
                attempts: int = Field(default=0, ge=0)
                errors: list[str] = Field(default_factory=list)
                tokens_used: int = Field(default=0, ge=0)
                latency_ms: int = Field(default=0, ge=0)
        '''))

        self.writer.write(f"{base}/value_objects/validation_error.py", dedent('''\
            """ValidationError VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field


            class ValidationError(BaseModel):
                """TH: ข้อผิดพลาดการ validate | EN: Validation error"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                path: str = ""
                message: str = ""
                kind: str = ""
                value: Optional[Any] = None
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """structured_outputs entities — aliases to ORM"""
            from .so_schema import SOSchema
            from .so_request import SORequest
            from .so_output import SOOutput
            from .so_validation import SOValidation
            from .so_repair import SORepair

            __all__ = [
                "SOSchema", "SORequest", "SOOutput", "SOValidation", "SORepair",
            ]
        '''))

        for name, cls, model in (
            ("so_schema", "SOSchema", "SOSchemaModel"),
            ("so_request", "SORequest", "SORequestModel"),
            ("so_output", "SOOutput", "SOOutputModel"),
            ("so_validation", "SOValidation", "SOValidationModel"),
            ("so_repair", "SORepair", "SORepairModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """structured_outputs helpers"""
            from .json_repair import extract_json, repair_json
            from .validator import validate_schema, build_strict_schema
            from .prompt_builder import build_system_prompt

            __all__ = [
                "extract_json", "repair_json",
                "validate_schema", "build_strict_schema",
                "build_system_prompt",
            ]
        '''))

        self.writer.write(f"{base}/helpers/json_repair.py", dedent('''\
            """json_repair — fallback extract + common fixes"""
            from __future__ import annotations
            import json
            import logging
            import re
            from typing import Any, Optional

            logger = logging.getLogger(__name__)

            _CODE_FENCE = re.compile(r"```(?:json|JSON)?\\s*(.*?)```", re.DOTALL)
            _TRAILING_COMMA = re.compile(r",\\s*([}\\]])")


            def extract_json(text: str) -> Optional[Any]:
                """TH: ดึง JSON จากข้อความ | EN: extract JSON from text"""
                if not text:
                    return None
                text = text.strip()

                try:
                    return json.loads(text)
                except Exception:
                    pass

                m = _CODE_FENCE.search(text)
                if m:
                    try:
                        return json.loads(m.group(1).strip())
                    except Exception:
                        pass

                for opener, closer in (("{", "}"), ("[", "]")):
                    start = text.find(opener)
                    end = text.rfind(closer)
                    if start != -1 and end != -1 and end > start:
                        candidate = text[start:end + 1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            continue
                return None


            def repair_json(text: str) -> Optional[Any]:
                """TH: best-effort JSON repair | EN: best-effort JSON repair"""
                raw = extract_json(text)
                if raw is not None:
                    return raw
                if not text:
                    return None

                s = text.strip()
                s = _TRAILING_COMMA.sub(r"\\1", s)
                s = re.sub(r"\\bNaN\\b", "null", s)
                s = re.sub(r"\\bInfinity\\b", "null", s)

                if s and s[0] not in "{[\\"":
                    m = re.search(r"([{\\[].*[}\\]])", s, re.DOTALL)
                    if m:
                        s = m.group(1)

                try:
                    return json.loads(s)
                except Exception:
                    pass

                try:
                    fixed = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\\s*:", r'"\\1":', s)
                    return json.loads(fixed)
                except Exception:
                    pass

                logger.debug("json repair failed for: %s", text[:120])
                return None
        '''))

        self.writer.write(f"{base}/helpers/validator.py", dedent('''\
            """validator — jsonschema wrapper + basic fallback"""
            from __future__ import annotations
            import logging
            from typing import Any, Optional

            logger = logging.getLogger(__name__)


            def build_strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
                """TH: เติม additionalProperties=false | EN: strict schema"""
                if not isinstance(schema, dict):
                    return schema
                s = dict(schema)
                if s.get("type") == "object" and "additionalProperties" not in s:
                    s["additionalProperties"] = False
                if isinstance(s.get("properties"), dict):
                    s["properties"] = {
                        k: build_strict_schema(v)
                        for k, v in s["properties"].items()
                    }
                if isinstance(s.get("items"), dict):
                    s["items"] = build_strict_schema(s["items"])
                return s


            def _basic_check(
                value: Any, schema: dict[str, Any], path: str = "$",
            ) -> list[dict[str, Any]]:
                """TH: ตรวจแบบ basic | EN: basic check"""
                errors: list[dict[str, Any]] = []
                if not isinstance(schema, dict):
                    return errors

                expected = schema.get("type")
                _TYPE_MAP = {
                    "object": dict, "array": list, "string": str,
                    "number": (int, float), "integer": int,
                    "boolean": bool, "null": type(None),
                }

                if expected in _TYPE_MAP:
                    py_type = _TYPE_MAP[expected]
                    if expected == "number" and isinstance(value, bool):
                        errors.append({"path": path, "message": "boolean is not number"})
                        return errors
                    if expected == "integer" and isinstance(value, bool):
                        errors.append({"path": path, "message": "boolean is not integer"})
                        return errors
                    if not isinstance(value, py_type):
                        errors.append({
                            "path": path,
                            "message": f"expected {expected}, got {type(value).__name__}",
                        })
                        return errors

                if expected == "object" and isinstance(value, dict):
                    required = schema.get("required") or []
                    for key in required:
                        if key not in value:
                            errors.append({
                                "path": f"{path}.{key}",
                                "message": "missing required",
                            })
                    props = schema.get("properties") or {}
                    for k, sub in props.items():
                        if k in value:
                            errors.extend(_basic_check(value[k], sub, f"{path}.{k}"))
                    if schema.get("additionalProperties") is False:
                        extras = set(value.keys()) - set(props.keys())
                        for k in extras:
                            errors.append({
                                "path": f"{path}.{k}",
                                "message": "additional property not allowed",
                            })

                if expected == "array" and isinstance(value, list):
                    items_schema = schema.get("items")
                    if isinstance(items_schema, dict):
                        for i, item in enumerate(value):
                            errors.extend(_basic_check(item, items_schema, f"{path}[{i}]"))

                if "enum" in schema and value not in schema["enum"]:
                    errors.append({
                        "path": path,
                        "message": f"value not in enum {schema['enum']}",
                    })

                if expected == "string" and isinstance(value, str):
                    if "minLength" in schema and len(value) < int(schema["minLength"]):
                        errors.append({"path": path, "message": "string too short"})
                    if "maxLength" in schema and len(value) > int(schema["maxLength"]):
                        errors.append({"path": path, "message": "string too long"})

                return errors


            def validate_schema(
                value: Any, schema: dict[str, Any],
            ) -> list[dict[str, Any]]:
                """TH: validate object กับ schema | EN: validate against schema"""
                if not isinstance(schema, dict) or not schema:
                    return []

                try:
                    import jsonschema  # type: ignore
                    validator = jsonschema.Draft7Validator(schema)
                    errors = list(validator.iter_errors(value))
                    return [
                        {
                            "path": "/".join(str(p) for p in e.absolute_path) or "$",
                            "message": e.message,
                            "kind": e.validator or "",
                        }
                        for e in errors
                    ]
                except ImportError:
                    logger.debug("jsonschema not available, using basic check")
                    return _basic_check(value, schema)
                except Exception as exc:
                    logger.debug("jsonschema failed, fallback: %s", exc)
                    return _basic_check(value, schema)
        '''))

        self.writer.write(f"{base}/helpers/prompt_builder.py", dedent('''\
            """prompt_builder — inject schema into system prompt"""
            from __future__ import annotations
            import json
            from typing import Optional


            def build_system_prompt(
                schema: dict,
                *,
                strict: bool = False,
                description: str = "",
                base_prompt: Optional[str] = None,
            ) -> str:
                """TH: สร้าง system prompt พร้อม schema | EN: build system prompt"""
                parts: list[str] = []
                if base_prompt:
                    parts.append(base_prompt.strip())

                parts.append(
                    "You must respond with ONLY a valid JSON object that strictly "
                    "conforms to the schema below. Do not wrap in markdown, do not "
                    "add explanations."
                )
                if strict:
                    parts.append(
                        "Do NOT include any keys that are not declared in the schema."
                    )
                if description:
                    parts.append(f"Purpose: {description}")
                try:
                    pretty = json.dumps(schema, indent=2, ensure_ascii=False)
                except Exception:
                    pretty = str(schema)
                parts.append(f"JSON Schema:\\n{pretty}")
                return "\\n\\n".join(parts)


            def build_repair_prompt(errors: list[dict], previous: str) -> str:
                """TH: prompt สำหรับ repair | EN: repair prompt"""
                lines = [
                    "Your previous output did not match the schema.",
                    "Fix ONLY the following issues and return valid JSON only:",
                ]
                for e in errors[:10]:
                    lines.append(f"- at {e.get('path', '$')}: {e.get('message', '')}")
                lines.append("")
                lines.append("Previous output:")
                lines.append(previous[:1500])
                return "\\n".join(lines)
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """structured_outputs enums"""
            from __future__ import annotations
            from enum import Enum


            class SOStrategy(str, Enum):
                """TH: กลยุทธ์การบังคับ JSON | EN: Structured output strategy"""
                JSON_MODE = "json_mode"
                FUNCTION_CALL = "function_call"
                GRAMMAR = "grammar"
                REGEX = "regex"
                PROMPT_ONLY = "prompt_only"

                def __str__(self) -> str:
                    return str(self.value)


            class SOStatus(str, Enum):
                """TH: สถานะ | EN: Status"""
                PENDING = "PENDING"
                VALID = "VALID"
                INVALID = "INVALID"
                REPAIRED = "REPAIRED"
                FAILED = "FAILED"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """structured_outputs domain exceptions"""
            from __future__ import annotations


            class SOError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class SchemaNotFoundError(SOError):
                code = "NOT_FOUND"


            class SchemaConflictError(SOError):
                code = "CONFLICT"


            class OutputNotFoundError(SOError):
                code = "NOT_FOUND"


            class RequestNotFoundError(SOError):
                code = "NOT_FOUND"


            class InvalidSchemaError(SOError):
                code = "VALIDATION_ERROR"


            class ParseError(SOError):
                code = "PROVIDER_ERROR"


            class RepairFailedError(SOError):
                code = "PROVIDER_ERROR"


            class MaxRepairsExceededError(SOError):
                code = "LIMIT_EXCEEDED"


            class ProviderError(SOError):
                code = "PROVIDER_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """structured_outputs domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class SchemaRegistered:
                schema_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                strategy: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class OutputGenerated:
                output_id: uuid.UUID
                tenant_id: uuid.UUID
                request_id: uuid.UUID
                is_valid: bool
                attempts: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class OutputValidated:
                output_id: uuid.UUID
                tenant_id: uuid.UUID
                attempt: int
                passed: bool
                error_count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class OutputRepaired:
                output_id: uuid.UUID
                tenant_id: uuid.UUID
                attempt: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class GenerationFailed:
                tenant_id: uuid.UUID
                schema_name: str
                error: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", self._app_exceptions())
        self.writer.write(f"{base}/interfaces.py", self._interfaces_content())
        self.writer.write(f"{base}/mappers.py", self._mappers_content())
        self.writer.write(f"{base}/utils.py", self._utils_content())
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _app_exceptions(self) -> str:
        return dedent('''\
            """structured_outputs application exceptions"""
            from __future__ import annotations


            class AppError(Exception):
                code: str = "APP_ERROR"
                http_status: int = 400

                def __init__(self, message: str = "", *, code: str | None = None,
                             http_status: int | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code
                    if http_status:
                        self.http_status = http_status


            class ValidationAppError(AppError):
                code = "VALIDATION_ERROR"
                http_status = 422


            class NotFoundAppError(AppError):
                code = "NOT_FOUND"
                http_status = 404


            class ConflictAppError(AppError):
                code = "CONFLICT"
                http_status = 409


            class ProviderAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class RepairExhaustedAppError(AppError):
                code = "LIMIT_EXCEEDED"
                http_status = 402
        ''')

    def _interfaces_content(self) -> str:
        return dedent('''\
            """structured_outputs application ports"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from typing import Any, Optional, Protocol, runtime_checkable

            from app.modules.structured_outputs.domain.value_objects import (
                SOResult, SchemaSpec,
            )


            @runtime_checkable
            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> Optional[uuid.UUID]: ...


            class SOSchemaRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, s: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all(self, ctx: Any) -> list[Any]: ...


            class SORequestRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...


            class SOOutputRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, o: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def update(self, ctx: Any, o: Any) -> Any: ...


            class SOValidationRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, v: Any) -> Any: ...
                @abstractmethod
                async def find_by_output(self, ctx: Any, output_id: uuid.UUID) -> list[Any]: ...


            class SORepairRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_output(self, ctx: Any, output_id: uuid.UUID) -> list[Any]: ...


            class LLMPort(Protocol):
                """TH: port ไปยัง llm module | EN: LLM port"""
                async def chat(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """structured_outputs mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def schema_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description or "",
                    "strategy": row.strategy,
                    "strict": bool(row.strict),
                    "version": row.version,
                }


            def request_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "schema_id": str(row.schema_id),
                    "model": row.model,
                    "prompt": (row.prompt or "")[:200],
                    "max_repairs": int(row.max_repairs or 0),
                }


            def output_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "request_id": str(row.request_id),
                    "is_valid": bool(row.is_valid),
                    "attempts": int(row.attempts or 0),
                    "tokens_used": int(row.tokens_used or 0),
                }


            def validation_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "output_id": str(row.output_id),
                    "attempt": int(row.attempt or 1),
                    "passed": bool(row.passed),
                    "errors_json": row.errors_json or "[]",
                }


            def repair_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "output_id": str(row.output_id),
                    "attempt": int(row.attempt or 1),
                    "feedback": row.feedback or "",
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """structured_outputs application utils"""
            from __future__ import annotations
            import json
            import time
            from typing import Any


            def json_dumps_safe(obj: Any) -> str:
                return json.dumps(obj, separators=(",", ":"), default=str)


            def json_loads_safe(raw: Any, default: Any = None) -> Any:
                if raw is None:
                    return default
                if isinstance(raw, (dict, list)):
                    return raw
                if isinstance(raw, str):
                    try:
                        return json.loads(raw)
                    except Exception:
                        return default
                return default


            def ms_now() -> int:
                return int(time.time() * 1000)
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """structured_outputs use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.structured_outputs.application.exceptions import (
                ConflictAppError, NotFoundAppError, ProviderAppError,
                RepairExhaustedAppError, ValidationAppError,
            )
            from app.modules.structured_outputs.application.utils import (
                json_dumps_safe, json_loads_safe, ms_now,
            )
            from app.modules.structured_outputs.domain.enums import SOStatus
            from app.modules.structured_outputs.domain.events import (
                OutputGenerated, OutputRepaired, OutputValidated,
                SchemaRegistered,
            )
            from app.modules.structured_outputs.domain.helpers.json_repair import (
                extract_json, repair_json,
            )
            from app.modules.structured_outputs.domain.helpers.prompt_builder import (
                build_repair_prompt, build_system_prompt,
            )
            from app.modules.structured_outputs.domain.helpers.validator import (
                build_strict_schema, validate_schema,
            )
            from app.modules.structured_outputs.domain.value_objects import (
                SOResult, SchemaSpec,
            )

            logger = logging.getLogger(__name__)

            _DEFAULT_MAX_REPAIRS = 2


            class StructuredOutputsUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                # ─── Schemas ─────────────────────────────────
                async def register_schema(
                    self, ctx: Any, spec: SchemaSpec,
                ) -> Any:
                    """TH: ลงทะเบียน schema | EN: register schema"""
                    from app.modules.structured_outputs.infrastructure.models import (
                        SOSchemaModel,
                    )

                    existing = await self._schemas.find_by_name(ctx, spec.name)
                    if existing is not None:
                        raise ConflictAppError(f"schema exists: {spec.name}")

                    schema_obj = spec.json_schema or {"type": "object", "properties": {}}
                    if spec.strict:
                        schema_obj = build_strict_schema(schema_obj)

                    row = SOSchemaModel(
                        tenant_id=ctx.tenant_id,
                        name=spec.name,
                        description=spec.description,
                        json_schema=json_dumps_safe(schema_obj),
                        pydantic_model=spec.pydantic_model,
                        strict=spec.strict,
                        strategy=str(spec.strategy),
                        version="1.0.0",
                    )
                    saved = await self._schemas.save(ctx, row)

                    if self._bus:
                        try:
                            await self._bus.publish(SchemaRegistered(
                                schema_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, strategy=str(spec.strategy),
                            ))
                        except Exception:
                            pass
                    return saved

                async def list_schemas(self, ctx: Any) -> list[Any]:
                    return await self._schemas.find_all(ctx)

                async def get_schema(self, ctx: Any, schema_id: uuid.UUID) -> Any:
                    s = await self._schemas.find_by_id(ctx, schema_id)
                    if s is None:
                        raise NotFoundAppError("schema not found")
                    return s

                # ─── Generate with repair loop ────────────────
                async def generate(
                    self, ctx: Any, *,
                    model: str,
                    prompt: str,
                    schema_id: uuid.UUID,
                    temperature: float = 0.0,
                    max_repairs: int = _DEFAULT_MAX_REPAIRS,
                ) -> SOResult:
                    """TH: generate + validate + repair | EN: generate with repair"""
                    from app.modules.structured_outputs.infrastructure.models import (
                        SOOutputModel, SORequestModel, SORepairModel,
                        SOValidationModel,
                    )

                    if self._llm is None:
                        raise ProviderAppError("LLM port not configured")

                    schema_row = await self.get_schema(ctx, schema_id)
                    schema_dict = json_loads_safe(schema_row.json_schema, {})
                    if not isinstance(schema_dict, dict):
                        raise ValidationAppError("schema is not a JSON object")

                    req_row = SORequestModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        schema_id=schema_row.id,
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_repairs=max_repairs,
                    )
                    saved_req = await self._requests.create(ctx, req_row)

                    started = ms_now()
                    system_prompt = build_system_prompt(
                        schema_dict,
                        strict=bool(schema_row.strict),
                        description=schema_row.description or "",
                    )

                    messages = [{"role": "user", "content": prompt}]
                    attempts = 0
                    tokens_total = 0
                    last_errors: list[dict[str, Any]] = []
                    last_raw = ""
                    parsed: Optional[dict[str, Any]] = None
                    final_status = SOStatus.FAILED

                    for attempt in range(1, max_repairs + 2):
                        attempts = attempt
                        try:
                            result = await self._llm.chat(
                                tenant_id=ctx.tenant_id,
                                model=model, messages=messages,
                                system_prompt=system_prompt,
                            )
                            raw = getattr(result, "content", "") or ""
                            usage = getattr(result, "usage", None)
                            tokens = int(getattr(usage, "total_tokens", 0) or 0) \
                                if usage is not None else 0
                            tokens_total += tokens
                        except Exception as exc:
                            logger.warning("llm call failed: %s", exc)
                            last_raw = ""
                            raw = ""

                        last_raw = raw
                        extracted = extract_json(raw)
                        if extracted is None:
                            extracted = repair_json(raw)

                        if extracted is None:
                            last_errors = [{"path": "$", "message": "invalid JSON"}]
                        else:
                            last_errors = validate_schema(extracted, schema_dict)

                        # persist validation row
                        validation_row = SOValidationModel(
                            tenant_id=ctx.tenant_id,
                            output_id=uuid.uuid4(),  # placeholder updated below
                            attempt=attempt,
                            errors_json=json_dumps_safe(last_errors),
                            passed=not last_errors,
                        )
                        # we don't have output_id yet → create output row first
                        output_row = SOOutputModel(
                            tenant_id=ctx.tenant_id,
                            request_id=saved_req.id,
                            raw_text=raw[:10000],
                            parsed_json=json_dumps_safe(extracted) if extracted else "{}",
                            is_valid=not last_errors,
                            attempts=attempt,
                            tokens_used=tokens_total,
                            cost_usd=0,
                        )
                        saved_out = await self._outputs.create(ctx, output_row)

                        validation_row.output_id = saved_out.id
                        await self._validations.create(ctx, validation_row)

                        if self._bus:
                            try:
                                await self._bus.publish(OutputValidated(
                                    output_id=saved_out.id, tenant_id=ctx.tenant_id,
                                    attempt=attempt, passed=not last_errors,
                                    error_count=len(last_errors),
                                ))
                            except Exception:
                                pass

                        if not last_errors and extracted is not None:
                            parsed = extracted if isinstance(extracted, dict) else {"value": extracted}
                            final_status = SOStatus.VALID if attempt == 1 else SOStatus.REPAIRED
                            if self._bus:
                                try:
                                    await self._bus.publish(OutputGenerated(
                                        output_id=saved_out.id, tenant_id=ctx.tenant_id,
                                        request_id=saved_req.id, is_valid=True,
                                        attempts=attempt,
                                    ))
                                except Exception:
                                    pass
                            return SOResult(
                                status=final_status, parsed=parsed,
                                raw_text=raw, is_valid=True,
                                attempts=attempt, errors=[],
                                tokens_used=tokens_total,
                                latency_ms=ms_now() - started,
                            )

                        # schedule repair
                        if attempt <= max_repairs:
                            feedback = build_repair_prompt(last_errors, raw)
                            messages = [
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": raw[:4000]},
                                {"role": "user", "content": feedback},
                            ]
                            try:
                                await self._repairs.create(ctx, SORepairModel(
                                    tenant_id=ctx.tenant_id,
                                    output_id=saved_out.id,
                                    attempt=attempt,
                                    feedback=feedback[:2000],
                                    raw_text=raw[:10000],
                                ))
                                if self._bus:
                                    await self._bus.publish(OutputRepaired(
                                        output_id=saved_out.id, tenant_id=ctx.tenant_id,
                                        attempt=attempt,
                                    ))
                            except Exception as exc:
                                logger.debug("repair log failed: %s", exc)

                    if self._bus:
                        try:
                            from app.modules.structured_outputs.domain.events import (
                                GenerationFailed,
                            )
                            await self._bus.publish(GenerationFailed(
                                tenant_id=ctx.tenant_id,
                                schema_name=schema_row.name,
                                error="max repairs exhausted",
                            ))
                        except Exception:
                            pass

                    return SOResult(
                        status=SOStatus.FAILED,
                        parsed=None, raw_text=last_raw,
                        is_valid=False, attempts=attempts,
                        errors=[e.get("message", "") for e in last_errors],
                        tokens_used=tokens_total,
                        latency_ms=ms_now() - started,
                    )

                # ─── Query ────────────────────────────────────
                async def get_output(self, ctx: Any, output_id: uuid.UUID) -> Any:
                    o = await self._outputs.find_by_id(ctx, output_id)
                    if o is None:
                        raise NotFoundAppError("output not found")
                    return o

                async def validate_raw(
                    self, ctx: Any, *, schema_id: uuid.UUID, payload: dict[str, Any],
                ) -> dict[str, Any]:
                    """TH: validate payload ตรงๆ | EN: validate raw payload"""
                    schema_row = await self.get_schema(ctx, schema_id)
                    schema_dict = json_loads_safe(schema_row.json_schema, {})
                    errors = validate_schema(payload, schema_dict)
                    return {"is_valid": not errors, "errors": errors}
        ''')

    # ─── INFRASTRUCTURE LAYER ─────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/repositories.py", self._repositories_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent(f'''\
            """structured_outputs SQLAlchemy models — schema=public, prefix=so_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Float, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""


            class SOSchemaModel(Base):
                __tablename__ = "so_schemas"
                __table_args__ = (
                    CheckConstraint(
                        "strategy IN ('json_mode','function_call','grammar','regex','prompt_only')",
                        name="ck_so_schema_strategy",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_so_schema_name"),
                    Index("ix_so_schema_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                json_schema: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                pydantic_model: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                strict: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
                strategy: Mapped[str] = mapped_column(String(20), nullable=False, server_default="json_mode")
                version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0.0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class SORequestModel(Base):
                __tablename__ = "so_requests"
                __table_args__ = (
                    Index("ix_so_req_tenant_time", "tenant_id", "created_at"),
                    Index("ix_so_req_schema", "schema_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                schema_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                prompt: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                temperature: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                max_repairs: Mapped[int] = mapped_column(Integer, nullable=False, server_default="2")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class SOOutputModel(Base):
                __tablename__ = "so_outputs"
                __table_args__ = (
                    Index("ix_so_out_request", "request_id"),
                    Index("ix_so_out_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                raw_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                parsed_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
                attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class SOValidationModel(Base):
                __tablename__ = "so_validations"
                __table_args__ = (
                    Index("ix_so_val_output", "output_id"),
                    Index("ix_so_val_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                output_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                attempt: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
                errors_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class SORepairModel(Base):
                __tablename__ = "so_repairs"
                __table_args__ = (
                    Index("ix_so_rep_output", "output_id"),
                    Index("ix_so_rep_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                output_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                attempt: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
                feedback: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                raw_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "SOSchemaModel", "SORequestModel", "SOOutputModel",
                "SOValidationModel", "SORepairModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """structured_outputs repositories"""
            from __future__ import annotations
            import logging
            import uuid

            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.structured_outputs.application.exceptions import AppError
            from app.modules.structured_outputs.infrastructure.models import (
                SOOutputModel, SORepairModel, SORequestModel, SOSchemaModel,
                SOValidationModel,
            )

            logger = logging.getLogger(__name__)


            class SOSchemaRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, s: SOSchemaModel) -> SOSchemaModel:
                    try:
                        self._session.add(s)
                        await self._session.flush()
                        return s
                    except SQLAlchemyError as exc:
                        logger.exception("schema.save failed")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> SOSchemaModel | None:
                    try:
                        r = await self._session.execute(
                            select(SOSchemaModel).where(SOSchemaModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> SOSchemaModel | None:
                    try:
                        r = await self._session.execute(
                            select(SOSchemaModel).where(SOSchemaModel.name == name)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        raise AppError(str(exc)) from exc

                async def find_all(self, ctx: object) -> list[SOSchemaModel]:
                    try:
                        r = await self._session.execute(
                            select(SOSchemaModel).order_by(SOSchemaModel.name)
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        raise AppError(str(exc)) from exc


            class SORequestRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, r_: SORequestModel) -> SORequestModel:
                    self._session.add(r_)
                    await self._session.flush()
                    return r_

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> SORequestModel | None:
                    r = await self._session.execute(
                        select(SORequestModel).where(SORequestModel.id == id)
                    )
                    return r.scalar_one_or_none()


            class SOOutputRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, o: SOOutputModel) -> SOOutputModel:
                    self._session.add(o)
                    await self._session.flush()
                    return o

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> SOOutputModel | None:
                    r = await self._session.execute(
                        select(SOOutputModel).where(SOOutputModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def update(self, ctx: object, o: SOOutputModel) -> SOOutputModel:
                    await self._session.flush()
                    return o


            class SOValidationRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, v: SOValidationModel) -> SOValidationModel:
                    self._session.add(v)
                    await self._session.flush()
                    return v

                async def find_by_output(
                    self, ctx: object, output_id: uuid.UUID,
                ) -> list[SOValidationModel]:
                    r = await self._session.execute(
                        select(SOValidationModel)
                        .where(SOValidationModel.output_id == output_id)
                        .order_by(SOValidationModel.attempt)
                    )
                    return list(r.scalars().all())


            class SORepairRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, r_: SORepairModel) -> SORepairModel:
                    self._session.add(r_)
                    await self._session.flush()
                    return r_

                async def find_by_output(
                    self, ctx: object, output_id: uuid.UUID,
                ) -> list[SORepairModel]:
                    r = await self._session.execute(
                        select(SORepairModel)
                        .where(SORepairModel.output_id == output_id)
                        .order_by(SORepairModel.attempt)
                    )
                    return list(r.scalars().all())
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """structured_outputs services"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any

            from app.modules.structured_outputs.application.interfaces import EventBus

            logger = logging.getLogger(__name__)


            class LLMPortAdapter:
                """TH: adapter ไปยัง llm module (LLMPort)
                | EN: LLM port adapter"""

                def __init__(self, llm_use_case: Any) -> None:
                    self._uc = llm_use_case

                async def chat(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Any = None,
                ) -> Any:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=tenant_id)
                    return await self._uc.chat(
                        ctx,
                        model_name=model, messages=messages,
                        system_prompt=system_prompt,
                    )


            class LoggingEventBus(EventBus):
                async def publish(self, event: object) -> None:
                    try:
                        logger.info("event %s", type(event).__name__)
                    except Exception:
                        pass
        ''')

    # ─── PRESENTATION LAYER ───────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """structured_outputs Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.structured_outputs.domain.enums import SOStrategy


            class SchemaCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100,
                                  pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
                description: str = ""
                json_schema: dict[str, Any] = Field(default_factory=dict)
                pydantic_model: str = ""
                strict: bool = False
                strategy: SOStrategy = SOStrategy.JSON_MODE


            class SchemaOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                description: str
                strategy: str
                strict: bool
                version: str


            class GenerateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                model: str = Field(min_length=1, max_length=100)
                prompt: str = Field(min_length=1)
                schema_id: uuid.UUID
                temperature: float = Field(default=0.0, ge=0.0, le=2.0)
                max_repairs: int = Field(default=2, ge=0, le=10)


            class GenerateResponse(BaseModel):
                status: str
                parsed: Optional[dict[str, Any]] = None
                is_valid: bool
                attempts: int
                errors: list[str] = []
                tokens_used: int = 0
                latency_ms: int = 0


            class ValidateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                schema_id: uuid.UUID
                payload: dict[str, Any] = Field(default_factory=dict)


            class ValidateResponse(BaseModel):
                is_valid: bool
                errors: list[dict[str, Any]] = []


            class OutputOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                request_id: uuid.UUID
                is_valid: bool
                attempts: int
                tokens_used: int
                created_at: datetime
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """structured_outputs DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.structured_outputs.application.use_case import (
                StructuredOutputsUseCase,
            )
            from app.modules.structured_outputs.infrastructure.repositories import (
                SOOutputRepository, SORepairRepository, SORequestRepository,
                SOSchemaRepository, SOValidationRepository,
            )
            from app.modules.structured_outputs.infrastructure.services import (
                LoggingEventBus,
            )


            @dataclass
            class Ctx:
                tenant_id: uuid.UUID
                user_id: Optional[uuid.UUID]


            async def get_db(request: Request) -> AsyncSession:
                session = getattr(request.app.state, "db_session", None)
                if session is None:
                    sm = getattr(request.app.state, "session_factory", None)
                    if sm is None:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"code": "DB_ERROR", "message": "db session unavailable"},
                        )
                    session = sm()
                return session


            async def get_ctx(
                x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
                x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
            ) -> Ctx:
                if not x_tenant_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={"code": "AUTH_ERROR", "message": "X-Tenant-Id required"},
                    )
                try:
                    tenant_id = uuid.UUID(x_tenant_id)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "VALIDATION_ERROR", "message": "invalid tenant id"},
                    ) from exc
                user_id: Optional[uuid.UUID] = None
                if x_user_id:
                    try:
                        user_id = uuid.UUID(x_user_id)
                    except ValueError:
                        user_id = None
                return Ctx(tenant_id=tenant_id, user_id=user_id)


            async def get_use_case(
                request: Request,
                db: AsyncSession = Depends(get_db),
            ) -> StructuredOutputsUseCase:
                llm_port = getattr(request.app.state, "so_llm_port", None)
                bus = getattr(request.app.state, "so_event_bus", None) \\
                    or LoggingEventBus()

                return StructuredOutputsUseCase(
                    schemas=SOSchemaRepository(db),
                    requests=SORequestRepository(db),
                    outputs=SOOutputRepository(db),
                    validations=SOValidationRepository(db),
                    repairs=SORepairRepository(db),
                    llm=llm_port,
                    bus=bus,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """structured_outputs HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.structured_outputs.application.exceptions import AppError
            from app.modules.structured_outputs.application.use_case import (
                StructuredOutputsUseCase,
            )
            from app.modules.structured_outputs.domain.exceptions import SOError
            from app.modules.structured_outputs.domain.value_objects import SchemaSpec
            from app.modules.structured_outputs.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.structured_outputs.presentation.schemas import (
                GenerateRequest, GenerateResponse, OutputOut, SchemaCreateRequest,
                SchemaOut, ValidateRequest, ValidateResponse,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/so", tags=["StructuredOutputs"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, SOError):
                    http = 400
                    code = getattr(exc, "code", "DOMAIN_ERROR")
                    if code == "NOT_FOUND":
                        http = 404
                    elif code == "VALIDATION_ERROR":
                        http = 422
                    elif code == "CONFLICT":
                        http = 409
                    elif code == "LIMIT_EXCEEDED":
                        http = 402
                    elif code == "PROVIDER_ERROR":
                        http = 502
                    raise HTTPException(
                        status_code=http,
                        detail={"code": code, "message": str(exc)},
                    )
                if isinstance(exc, AppError):
                    raise HTTPException(
                        status_code=getattr(exc, "http_status", 400),
                        detail={
                            "code": getattr(exc, "code", "APP_ERROR"),
                            "message": str(exc),
                        },
                    )
                logger.exception("unhandled error")
                raise HTTPException(
                    status_code=500,
                    detail={"code": "INTERNAL_ERROR", "message": "internal error"},
                )


            @router.get("/schemas", response_model=list[SchemaOut])
            async def list_schemas(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
            ) -> list[SchemaOut]:
                """TH: list schemas | EN: list schemas"""
                try:
                    items = await uc.list_schemas(ctx)
                    return [SchemaOut.model_validate(s.model_dump()) for s in items]
                except (SOError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/schemas", response_model=SchemaOut, status_code=201)
            async def create_schema(
                req: SchemaCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
            ) -> SchemaOut:
                """TH: ลงทะเบียน schema | EN: register schema"""
                try:
                    spec = SchemaSpec(
                        name=req.name, description=req.description,
                        json_schema=req.json_schema,
                        pydantic_model=req.pydantic_model,
                        strict=req.strict, strategy=req.strategy,
                    )
                    row = await uc.register_schema(ctx, spec)
                    return SchemaOut.model_validate(row.model_dump())
                except (SOError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/generate", response_model=GenerateResponse)
            async def generate(
                req: GenerateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
            ) -> GenerateResponse:
                """TH: generate structured output | EN: generate structured"""
                try:
                    result = await uc.generate(
                        ctx, model=req.model, prompt=req.prompt,
                        schema_id=req.schema_id,
                        temperature=req.temperature,
                        max_repairs=req.max_repairs,
                    )
                    return GenerateResponse(
                        status=str(result.status),
                        parsed=result.parsed,
                        is_valid=result.is_valid,
                        attempts=result.attempts,
                        errors=result.errors,
                        tokens_used=result.tokens_used,
                        latency_ms=result.latency_ms,
                    )
                except (SOError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/outputs/{output_id}", response_model=OutputOut)
            async def get_output(
                output_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
            ) -> OutputOut:
                """TH: ดึง output | EN: get output"""
                try:
                    o = await uc.get_output(ctx, output_id)
                    return OutputOut.model_validate(o.model_dump())
                except (SOError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/validate", response_model=ValidateResponse)
            async def validate(
                req: ValidateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[StructuredOutputsUseCase, Depends(get_use_case)],
            ) -> ValidateResponse:
                """TH: validate payload | EN: validate payload"""
                try:
                    out = await uc.validate_raw(
                        ctx, schema_id=req.schema_id, payload=req.payload,
                    )
                    return ValidateResponse(
                        is_valid=out.get("is_valid", False),
                        errors=out.get("errors", []),
                    )
                except (SOError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent(f'''\
            """structured_outputs OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_structured_outputs_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "{self.tag}" for t in tags):
                        tags.append({{
                            "name": "{self.tag}",
                            "description": (
                                "โมดูล structured_outputs — JSON Schema enforcement\\n\\n"
                                "• Schema registry (JSON Schema / Pydantic)\\n"
                                "• Generate with auto repair loop\\n"
                                "• Validation + repair attempts\\n"
                                "• Strict mode (additionalProperties=false)"
                            ),
                            "externalDocs": {{
                                "description": "{self.module} Module README",
                                "url": "/docs/README_{self.module}.md",
                            }},
                        }})
                    info_ = schema.setdefault("info", {{}})
                    info_.setdefault("x-module", "{self.module}")
                    info_.setdefault("x-layer", "{self.layer}")
                    info_.setdefault("x-prefix", "{self.prefix}")
                    info_.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as {self.prefix}_router

            __all__ = ["{self.prefix}_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module} — {self.tables}")
        self.writer.write(
            f"{self.sql_dir}/V001__create_{self.module}.sql", self._v001_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V002__seed_{self.module}.sql", self._v002_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V003__rollback_{self.module}.sql", self._v003_sql(),
        )

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_structured_outputs.sql | Module: structured_outputs | Prefix: so
-- Schema: public | Tables: so_schemas, so_requests, so_outputs,
--                          so_validations, so_repairs
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."so_schemas";
CREATE TABLE "public"."so_schemas" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid NOT NULL,
  "name"            varchar(100) NOT NULL,
  "description"     text NOT NULL DEFAULT '',
  "json_schema"     text NOT NULL DEFAULT '{}',
  "pydantic_model"  text NOT NULL DEFAULT '',
  "strict"          bool NOT NULL DEFAULT false,
  "strategy"        varchar(20) NOT NULL DEFAULT 'json_mode',
  "version"         varchar(20) NOT NULL DEFAULT '1.0.0',
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "so_schemas_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_so_schema_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_so_schema_strategy" CHECK (
    strategy IN ('json_mode','function_call','grammar','regex','prompt_only')
  )
);
CREATE INDEX "ix_so_schema_tenant" ON "public"."so_schemas" ("tenant_id");

DROP TABLE IF EXISTS "public"."so_requests";
CREATE TABLE "public"."so_requests" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "user_id"      uuid NOT NULL,
  "schema_id"    uuid NOT NULL,
  "model"        varchar(100) NOT NULL DEFAULT '',
  "prompt"       text NOT NULL DEFAULT '',
  "temperature"  float8 NOT NULL DEFAULT 0,
  "max_repairs"  int4 NOT NULL DEFAULT 2,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "so_requests_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_so_req_tenant_time" ON "public"."so_requests" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_so_req_schema"      ON "public"."so_requests" ("schema_id");

DROP TABLE IF EXISTS "public"."so_outputs";
CREATE TABLE "public"."so_outputs" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "request_id"   uuid NOT NULL,
  "raw_text"     text NOT NULL DEFAULT '',
  "parsed_json"  text NOT NULL DEFAULT '{}',
  "is_valid"     bool NOT NULL DEFAULT false,
  "attempts"     int4 NOT NULL DEFAULT 0,
  "tokens_used"  int4 NOT NULL DEFAULT 0,
  "cost_usd"     numeric(12,8) NOT NULL DEFAULT 0,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "so_outputs_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_so_out_request" ON "public"."so_outputs" ("request_id");
CREATE INDEX "ix_so_out_tenant"  ON "public"."so_outputs" ("tenant_id");

DROP TABLE IF EXISTS "public"."so_validations";
CREATE TABLE "public"."so_validations" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "output_id"    uuid NOT NULL,
  "attempt"      int4 NOT NULL DEFAULT 1,
  "errors_json"  text NOT NULL DEFAULT '[]',
  "passed"       bool NOT NULL DEFAULT false,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "so_validations_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_so_val_output" ON "public"."so_validations" ("output_id");
CREATE INDEX "ix_so_val_tenant" ON "public"."so_validations" ("tenant_id");

DROP TABLE IF EXISTS "public"."so_repairs";
CREATE TABLE "public"."so_repairs" (
  "id"          uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "output_id"   uuid NOT NULL,
  "attempt"     int4 NOT NULL DEFAULT 1,
  "feedback"    text NOT NULL DEFAULT '',
  "raw_text"    text NOT NULL DEFAULT '',
  "created_at"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"  timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "so_repairs_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_so_rep_output" ON "public"."so_repairs" ("output_id");
CREATE INDEX "ix_so_rep_tenant" ON "public"."so_repairs" ("tenant_id");

CREATE OR REPLACE FUNCTION public.set_updated_at_so()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_so_schema_updated ON "public"."so_schemas";
CREATE TRIGGER trg_so_schema_updated BEFORE UPDATE ON "public"."so_schemas"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();

DROP TRIGGER IF EXISTS trg_so_req_updated ON "public"."so_requests";
CREATE TRIGGER trg_so_req_updated BEFORE UPDATE ON "public"."so_requests"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();

DROP TRIGGER IF EXISTS trg_so_out_updated ON "public"."so_outputs";
CREATE TRIGGER trg_so_out_updated BEFORE UPDATE ON "public"."so_outputs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();

DROP TRIGGER IF EXISTS trg_so_val_updated ON "public"."so_validations";
CREATE TRIGGER trg_so_val_updated BEFORE UPDATE ON "public"."so_validations"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();

DROP TRIGGER IF EXISTS trg_so_rep_updated ON "public"."so_repairs";
CREATE TRIGGER trg_so_rep_updated BEFORE UPDATE ON "public"."so_repairs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();

ALTER TABLE "public"."so_schemas"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."so_requests"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."so_outputs"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."so_validations"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."so_repairs"      ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_so_schema ON "public"."so_schemas";
CREATE POLICY p_so_schema ON "public"."so_schemas"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_so_req ON "public"."so_requests";
CREATE POLICY p_so_req ON "public"."so_requests"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_so_out ON "public"."so_outputs";
CREATE POLICY p_so_out ON "public"."so_outputs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_so_val ON "public"."so_validations";
CREATE POLICY p_so_val ON "public"."so_validations"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_so_rep ON "public"."so_repairs";
CREATE POLICY p_so_rep ON "public"."so_repairs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_structured_outputs.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."so_schemas"
    (tenant_id, name, description, json_schema, strict, strategy)
VALUES
    (
        '00000000-0000-0000-0000-000000000001',
        'person_info',
        'Basic person info',
        '{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer","minimum":0},"email":{"type":"string"}},"required":["name"],"additionalProperties":false}',
        TRUE, 'json_mode'
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        'sentiment_result',
        'Sentiment classification',
        '{"type":"object","properties":{"label":{"type":"string","enum":["positive","negative","neutral"]},"score":{"type":"number","minimum":0,"maximum":1}},"required":["label","score"],"additionalProperties":false}',
        TRUE, 'json_mode'
    )
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_structured_outputs.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_so_rep_updated    ON "public"."so_repairs";
DROP TRIGGER IF EXISTS trg_so_val_updated    ON "public"."so_validations";
DROP TRIGGER IF EXISTS trg_so_out_updated    ON "public"."so_outputs";
DROP TRIGGER IF EXISTS trg_so_req_updated    ON "public"."so_requests";
DROP TRIGGER IF EXISTS trg_so_schema_updated ON "public"."so_schemas";

DROP POLICY IF EXISTS p_so_rep    ON "public"."so_repairs";
DROP POLICY IF EXISTS p_so_val    ON "public"."so_validations";
DROP POLICY IF EXISTS p_so_out    ON "public"."so_outputs";
DROP POLICY IF EXISTS p_so_req    ON "public"."so_requests";
DROP POLICY IF EXISTS p_so_schema ON "public"."so_schemas";

DROP TABLE IF EXISTS "public"."so_repairs"      CASCADE;
DROP TABLE IF EXISTS "public"."so_validations"  CASCADE;
DROP TABLE IF EXISTS "public"."so_outputs"      CASCADE;
DROP TABLE IF EXISTS "public"."so_requests"     CASCADE;
DROP TABLE IF EXISTS "public"."so_schemas"      CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_so();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "so_001"
        content = f'''"""add structured_outputs tables

Revision ID: {rev}
Revises: None
Create Date: {datetime.now(timezone.utc).date().isoformat()}
"""
from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "{rev}"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"


def upgrade() -> None:
    """TH: สร้างตาราง structured_outputs | EN: create tables"""
    op.create_table(
        "so_schemas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("json_schema", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("pydantic_model", sa.Text, nullable=False, server_default=""),
        sa.Column("strict", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("strategy", sa.String(20), nullable=False, server_default="json_mode"),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_so_schema_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "so_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schema_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model", sa.String(100), nullable=False, server_default=""),
        sa.Column("prompt", sa.Text, nullable=False, server_default=""),
        sa.Column("temperature", sa.Float, nullable=False, server_default="0"),
        sa.Column("max_repairs", sa.Integer, nullable=False, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "so_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False, server_default=""),
        sa.Column("parsed_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("is_valid", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "so_validations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("output_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt", sa.Integer, nullable=False, server_default="1"),
        sa.Column("errors_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("passed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "so_repairs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("output_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt", sa.Integer, nullable=False, server_default="1"),
        sa.Column("feedback", sa.Text, nullable=False, server_default=""),
        sa.Column("raw_text", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_index("ix_so_schema_tenant", "so_schemas", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_so_req_tenant_time", "so_requests", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_so_req_schema", "so_requests", ["schema_id"], schema=SCHEMA)
    op.create_index("ix_so_out_request", "so_outputs", ["request_id"], schema=SCHEMA)
    op.create_index("ix_so_out_tenant", "so_outputs", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_so_val_output", "so_validations", ["output_id"], schema=SCHEMA)
    op.create_index("ix_so_val_tenant", "so_validations", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_so_rep_output", "so_repairs", ["output_id"], schema=SCHEMA)
    op.create_index("ix_so_rep_tenant", "so_repairs", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_so()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("so_schemas", "so_requests", "so_outputs",
                "so_validations", "so_repairs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_so();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("so_repairs", "so_validations", "so_outputs",
                "so_requests", "so_schemas"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_so();")
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py", content,
        )

    # ═══════════════════════════════════════════════════════════
    #  4. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")
        self.writer.write(
            f"{self.mod_root}/presentation/swagger.py", self._swagger_content(),
        )

    # ═══════════════════════════════════════════════════════════
    #  5. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[POSTMAN] {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json", self._postman_json(),
        )

    def _postman_json(self) -> str:
        return _json.dumps({
            "info": {
                "name": f"{self.module} API",
                "_postman_id": str(uuid.uuid4()),
                "description": self.cfg["title"],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "variable": [
                {"key": "base_url", "value": "http://localhost:8000"},
                {"key": "tenant_id", "value": "00000000-0000-0000-0000-000000000001"},
                {"key": "user_id", "value": "00000000-0000-0000-0000-000000000002"},
                {"key": "schema_id", "value": "REPLACE_WITH_SCHEMA_UUID"},
            ],
            "item": [
                {
                    "name": "Register Schema",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                            {"key": "X-User-Id", "value": "{{user_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/schemas",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "schemas"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"person","strict":true,"json_schema":{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}},"required":["name"]}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "List Schemas",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/schemas",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "schemas"],
                        },
                    },
                },
                {
                    "name": "Generate (with repair)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/generate",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "generate"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"model":"gpt-4o-mini","prompt":"Extract person from: John is 30","schema_id":"{{schema_id}}","max_repairs":2}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Validate Raw",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/validate",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "validate"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"schema_id":"{{schema_id}}","payload":{"name":"John","age":30}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Get Output",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/outputs/REPLACE",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "outputs", "REPLACE"],
                        },
                    },
                },
            ],
        }, indent=2, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    #  6. UPDATE APP
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info(f"[UPDATE APP] {self.module}")
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = (
            f"from app.modules.{self.module}.presentation.router "
            f"import router as {self.prefix}_router"
        )
        swagger_import = (
            f"from app.modules.{self.module}.presentation.swagger "
            f"import register_{self.module}_openapi"
        )

        if router_import not in content:
            lines = content.split("\n")
            insert_at = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_at = i + 1
            lines.insert(insert_at, router_import + "\n" + swagger_import)
            content = "\n".join(lines)

        if f"include_router({self.prefix}_router" not in content:
            include_call = (
                f"\napp.include_router({self.prefix}_router, prefix='/api/v1')\n"
                f"register_{self.module}_openapi(app)\n"
            )
            if "app = FastAPI(" in content:
                m = re.search(r"app\s*=\s*FastAPI\([^)]*\)\n", content)
                if m:
                    content = content[:m.end()] + include_call + content[m.end():]
                else:
                    content += include_call
            else:
                content += include_call

        if content != original:
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")
        else:
            skip(f"{self.app_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  7. UPDATE ENV
    # ═══════════════════════════════════════════════════════════
    def update_env(self) -> None:
        info(f"[UPDATE ENV] {self.module}")
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found")
            return

        content = env_file.read_text(encoding="utf-8")
        marker = f"# --- module {self.module} ---"
        if marker in content:
            skip(f"{self.module} already in env.py")
            return

        block = f'''{marker}
try:
    from app.modules.{self.module}.infrastructure.models import (  # noqa: F401
        SOOutputModel,
        SORepairModel,
        SORequestModel,
        SOSchemaModel,
        SOValidationModel,
    )
except ImportError:
    pass

'''
        anchor = "config = context.config"
        idx = content.find(anchor)
        if idx == -1:
            warn("anchor not found in env.py")
            return

        content = content[:idx] + block + content[idx:]
        env_file.write_text(content, encoding="utf-8", newline="\n")
        ok(f"{self.env_py} updated")

    # ═══════════════════════════════════════════════════════════
    #  8. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info(f"[VERIFY] {self.module}")
        issues: list[str] = []

        for rel in (
            f"{self.mod_root}/presentation/router.py",
            f"{self.mod_root}/presentation/swagger.py",
            f"{self.mod_root}/infrastructure/models.py",
            f"{self.mod_root}/application/use_case.py",
            f"{self.mod_root}/domain/helpers/json_repair.py",
            f"{self.mod_root}/domain/helpers/validator.py",
        ):
            p = self.root / rel
            if p.exists():
                ok(f"{rel} ✓")
            else:
                issues.append(f"missing: {rel}")

        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            for check in (
                f"{self.prefix}_router",
                f"register_{self.module}_openapi",
            ):
                if check in content:
                    ok(f"app.py: {check} ✓")
                else:
                    issues.append(f"app.py missing: {check}")

        postman = self.root / f"docs/postman/{self.module}.json"
        if postman.exists():
            try:
                _json.loads(postman.read_text(encoding="utf-8"))
                ok("postman.json valid")
            except Exception as e:
                issues.append(f"postman.json invalid: {e}")
        else:
            issues.append("postman.json missing")

        print()
        if issues:
            warn(f"{len(issues)} issues:")
            for i, m in enumerate(issues, 1):
                err(f"  {i}. {m}")
        else:
            ok("ALL CHECKS PASSED ✓")

    # ═══════════════════════════════════════════════════════════
    #  RUN ALL
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.update_app()
        self.update_env()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — {self.module} ({self.cfg['title']})")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Tables  : {len(self.tables)}")
        info(f"  Written : {len(self.writer.written)}")
        info(f"  Skipped : {len(self.writer.skipped)}")
        info("═" * 60)


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
create_module_structured_outputs.py — Structured Outputs Module Generator v{VERSION}

USAGE
    python create_module_structured_outputs.py <action> [options]

MODULE
    name    : structured_outputs
    layer   : 5-Intel
    prefix  : so
    schema  : public
    tables  : so_schemas, so_requests, so_outputs, so_validations, so_repairs

ACTIONS (10)
    create       สร้าง module structure (4 layers)
    sql          สร้าง SQL migrations V001/V002/V003
    alembic      สร้าง Alembic migration
    swagger      สร้าง OpenAPI docs
    postman      สร้าง Postman collection
    update       อัปเดต app/app.py
    update-env   อัปเดต migrations/env.py
    verify       ตรวจสอบ setup
    all          ทำทุกอย่าง
    help         แสดง help

EXAMPLES
    python create_module_structured_outputs.py all
    python create_module_structured_outputs.py create --force
    python create_module_structured_outputs.py verify
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    if args.action not in ACTIONS:
        err(f"unknown action: {args.action}")
        print(HELP)
        return 1

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"root not found: {root}")
        return 1

    gen = StructuredOutputsGenerator(root, force=args.force)

    print()
    info("═" * 60)
    info(f"  MODULE : {gen.module} — {gen.cfg['title']}")
    info(f"  LAYER  : {gen.layer}")
    info(f"  PREFIX : {gen.prefix}_")
    info(f"  ACTION : {args.action}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "verify": gen.verify,
        "all": gen.run_all,
    }

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())