# so_opencode_promt.md — Module `structured_outputs` Generator Prompt

## 🎯 Purpose
JSON schema enforcement + validation + repair loop
**Depends on:** `llm`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `structured_outputs` |
| PREFIX | `so` |
| VERSION | `1.0.0` |
| DEPS | `llm` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `so_schemas` | JSON schemas / Pydantic models |
| `so_requests` | Requests (prompt + schema_id) |
| `so_outputs` | Validated outputs |
| `so_validations` | Validation attempts |
| `so_repairs` | Repair attempts |

## 🔤 Enums
- `SOStrategy`: JSON_MODE, FUNCTION_CALL, GRAMMAR, REGEX, PROMPT_ONLY
- `SOStatus`: PENDING, VALID, INVALID, REPAIRED, FAILED

## 💎 Value Objects
- `SchemaSpec(name, json_schema, pydantic_model, strict)`
- `SOResult(parsed, is_valid, attempts, tokens_used)`

## 🔌 Public Port
```python
class StructuredOutputPort(Protocol):
    async def generate(self, *, model: str, prompt: str,
                       schema_id: uuid.UUID,
                       max_repairs: int = 2) -> SOResult: ...
```

## 🌐 Endpoints
```
GET    /api/v1/so/schemas
POST   /api/v1/so/schemas
POST   /api/v1/so/generate
GET    /api/v1/so/outputs/{id}
POST   /api/v1/so/validate
```

## 📤 Opencode Prompt

```
Generate `create_module_structured_outputs.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "structured_outputs"
  PREFIX      = "so"
  VERSION     = "1.0.0"

DEPENDENCY:
  from app.modules.llm.application.ports import LLMPort

ENTITIES:
  SOSchema(id, tenant_id, name, json_schema, pydantic_model,
           version, strict, created_at, updated_at)
  SORequest(id, tenant_id, user_id, model, prompt, schema_id,
            temperature, max_repairs, created_at, updated_at)
  SOOutput(id, request_id, raw_text, parsed_json, is_valid,
           tokens_used, cost_usd, created_at, updated_at)
  SOValidation(id, output_id, attempt, errors_json, passed,
               created_at, updated_at)
  SORepair(id, output_id, attempt, feedback, raw_text,
           created_at, updated_at)

ENUMS:
  SOStrategy(str, Enum): JSON_MODE, FUNCTION_CALL, GRAMMAR, REGEX, PROMPT_ONLY
  SOStatus(str, Enum): PENDING, VALID, INVALID, REPAIRED, FAILED

VALUE OBJECTS:
  SchemaSpec(name, json_schema: dict, pydantic_model: str,
             strict: bool)
  SOResult(parsed: dict, is_valid: bool, attempts: int,
           tokens_used: int, cost_usd: Decimal)

EVENTS:
  SchemaRegistered, OutputGenerated, OutputValidated, OutputRepaired

PORTS:
  StructuredOutputPort (generate)
  SchemaValidator Protocol (validate(json, schema) -> list[Error])
  RepairStrategy Protocol (build_feedback(errors) -> str)

USE CASES:
  RegisterSchemaUseCase, GenerateStructuredUseCase (with repair loop),
  ValidateOutputUseCase

ENDPOINTS:
  GET  /api/v1/so/schemas
  POST /api/v1/so/schemas
  POST /api/v1/so/generate
  GET  /api/v1/so/outputs/{id}
  POST /api/v1/so/validate

REPAIR LOOP:
  1. Call LLMPort.chat with prompt + schema injection
  2. Parse JSON (fallback extract first {...})
  3. Validate with jsonschema or Pydantic
  4. If invalid and attempt < max_repairs:
       - build feedback message with errors
       - retry with feedback appended
  5. Return SOResult

SQL:
  Indexes:
    ix_so_schema_tenant_name UNIQUE
    ix_so_req_tenant_time
    ix_so_out_req
    ix_so_val_out
    ix_so_rep_out
  Trigger set_updated_at_so + RLS

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. POST schema (Pydantic) → 201
2. Generate → valid output
3. Force invalid JSON → auto repair (≤2)
4. Strict mode → reject extras
5. Nested object → validate
6. Array of objects → validate
7. Enum constraint → reject
8. Regex pattern → reject
9. Repair log persisted
10. Output cache hit → `cached=true`

## ✅ Checklist
- [ ] `StructuredOutputPort` importable
- [ ] Repair loop max=2 default
- [ ] Pydantic + jsonschema both supported