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
                tokens = int(getattr(usage, "total_tokens", 0) or 0)                                 if usage is not None else 0
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
