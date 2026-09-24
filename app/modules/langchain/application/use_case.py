"""langchain use cases"""
from __future__ import annotations
import logging
import uuid
from decimal import Decimal
from typing import Any, Optional

from app.modules.langchain.application.exceptions import (
    ConflictAppError, ExecutionAppError, LimitExceededAppError,
    NotFoundAppError, ValidationAppError,
)
from app.modules.langchain.application.utils import (
    json_dumps_safe, json_loads_safe, ms_now,
)
from app.modules.langchain.domain.enums import RunStatus, TraceKind
from app.modules.langchain.domain.events import (
    AgentRegistered, AgentStepExecuted, ChainInvoked,
    ChainRegistered, MemoryUpdated, RunCompleted, RunFailed,
)
from app.modules.langchain.domain.helpers.tracer import Tracer
from app.modules.langchain.domain.value_objects import (
    AgentSpec, ChainSpec,
)

logger = logging.getLogger(__name__)

_DEFAULT_MAX_ITERATIONS = 10


class LangChainUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)

    # ─── Chains ──────────────────────────────────
    async def register_chain(
        self, ctx: Any, spec: ChainSpec,
    ) -> Any:
        from app.modules.langchain.infrastructure.models import (
            LCChainModel,
        )
        existing = await self._chains.find_by_name(ctx, spec.name)
        if existing is not None:
            raise ConflictAppError(f"chain exists: {spec.name}")

        row = LCChainModel(
            tenant_id=ctx.tenant_id, name=spec.name,
            chain_type=str(spec.chain_type),
            config_json=json_dumps_safe(spec.config or {}),
            version=spec.version, is_active=True,
        )
        saved = await self._chains.save(ctx, row)
        if self._bus:
            try:
                await self._bus.publish(ChainRegistered(
                    chain_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, chain_type=str(spec.chain_type),
                ))
            except Exception:
                pass
        return saved

    async def list_chains(self, ctx: Any) -> list[Any]:
        return await self._chains.find_all_active(ctx)

    async def get_chain(self, ctx: Any, chain_id: uuid.UUID) -> Any:
        c = await self._chains.find_by_id(ctx, chain_id)
        if c is None:
            raise NotFoundAppError("chain not found")
        return c

    async def invoke_chain(
        self, ctx: Any, *, chain_id: uuid.UUID,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """TH: invoke chain | EN: invoke chain"""
        from app.modules.langchain.infrastructure.models import (
            LCRunModel, LCTraceModel,
        )
        chain = await self.get_chain(ctx, chain_id)

        run = LCRunModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            kind="chain", target_id=chain.id,
            input_json=json_dumps_safe(inputs),
            status=str(RunStatus.RUNNING),
        )
        saved_run = await self._runs.create(ctx, run)

        started = ms_now()
        tracer = Tracer()
        output: dict[str, Any] = {}
        tokens = 0
        status = RunStatus.DONE
        error = ""

        try:
            if self._chain_runner is None:
                # fallback: direct LLM call
                if self._llm is None:
                    raise ExecutionAppError("LLM port not configured")
                prompt = inputs.get("input") or inputs.get("query") or ""
                tracer.record("llm_call", {"model": "gpt-4o-mini",
                                            "chars": len(str(prompt))})
                result = await self._llm.chat(
                    tenant_id=ctx.tenant_id,
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": str(prompt)}],
                )
                content = getattr(result, "content", "") or ""
                usage = getattr(result, "usage", None)
                tokens = int(getattr(usage, "total_tokens", 0) or 0) \
                    if usage is not None else 0
                output = {"output": content}
            else:
                output = await self._chain_runner.run(
                    chain_type=str(chain.chain_type),
                    config=json_loads_safe(chain.config_json, {}),
                    inputs=inputs, ctx=ctx,
                )
        except Exception as exc:
            logger.exception("chain invoke failed: %s", exc)
            status = RunStatus.FAILED
            error = str(exc)[:500]

        latency = ms_now() - started

        saved_run.output_json = json_dumps_safe(output)
        saved_run.status = str(status)
        saved_run.latency_ms = latency
        saved_run.tokens_used = tokens
        saved_run.cost_usd = Decimal("0")
        saved_run.error_message = error
        await self._runs.update(ctx, saved_run)

        # persist traces
        if tracer.steps():
            try:
                trace_rows = [
                    LCTraceModel(
                        tenant_id=ctx.tenant_id, run_id=saved_run.id,
                        step=int(s["step"]), kind=s["kind"],
                        payload_json=json_dumps_safe(s.get("payload", {})),
                        latency_ms=int(s.get("latency_ms", 0)),
                    )
                    for s in tracer.steps()
                ]
                await self._traces.create_many(ctx, trace_rows)
            except Exception as exc:
                logger.debug("persist traces failed: %s", exc)

        if self._bus:
            try:
                await self._bus.publish(ChainInvoked(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    chain_id=chain.id, latency_ms=latency,
                ))
                await self._bus.publish(RunCompleted(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    kind="chain", status=str(status),
                    latency_ms=latency, tokens_used=tokens,
                ))
            except Exception:
                pass

        if status == RunStatus.FAILED:
            raise ExecutionAppError(error or "chain failed")

        return {
            "run_id": str(saved_run.id),
            "output": output,
            "status": str(status),
            "latency_ms": latency,
            "tokens_used": tokens,
            "trace_steps": len(tracer.steps()),
        }

    # ─── Agents ──────────────────────────────────
    async def register_agent(
        self, ctx: Any, spec: AgentSpec,
    ) -> Any:
        from app.modules.langchain.infrastructure.models import (
            LCAgentModel,
        )
        existing = await self._agents.find_by_name(ctx, spec.name)
        if existing is not None:
            raise ConflictAppError(f"agent exists: {spec.name}")

        row = LCAgentModel(
            tenant_id=ctx.tenant_id, name=spec.name,
            agent_type=str(spec.agent_type),
            tools_json=json_dumps_safe(spec.tools),
            model=spec.model,
            max_iterations=spec.max_iterations,
            config_json=json_dumps_safe({
                "system_prompt": spec.system_prompt,
                **(spec.config or {}),
            }),
            is_active=True,
        )
        saved = await self._agents.save(ctx, row)
        if self._bus:
            try:
                await self._bus.publish(AgentRegistered(
                    agent_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, agent_type=str(spec.agent_type),
                ))
            except Exception:
                pass
        return saved

    async def list_agents(self, ctx: Any) -> list[Any]:
        return await self._agents.find_all_active(ctx)

    async def get_agent(self, ctx: Any, agent_id: uuid.UUID) -> Any:
        a = await self._agents.find_by_id(ctx, agent_id)
        if a is None:
            raise NotFoundAppError("agent not found")
        return a

    async def invoke_agent(
        self, ctx: Any, *, agent_id: uuid.UUID,
        question: str,
    ) -> dict[str, Any]:
        """TH: invoke agent | EN: invoke agent"""
        from app.modules.langchain.infrastructure.models import (
            LCRunModel, LCTraceModel,
        )
        agent = await self.get_agent(ctx, agent_id)
        config = json_loads_safe(agent.config_json, {})
        system_prompt = config.get("system_prompt") or ""

        run = LCRunModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            kind="agent", target_id=agent.id,
            input_json=json_dumps_safe({"question": question}),
            status=str(RunStatus.RUNNING),
        )
        saved_run = await self._runs.create(ctx, run)

        started = ms_now()
        tracer = Tracer()
        output: dict[str, Any] = {}
        tokens = 0
        status = RunStatus.DONE
        error = ""

        try:
            if self._agent_runner is not None:
                tools = json_loads_safe(agent.tools_json, [])
                output = await self._agent_runner.run(
                    agent_type=str(agent.agent_type),
                    tools=tools, model=agent.model,
                    max_iterations=int(agent.max_iterations or _DEFAULT_MAX_ITERATIONS),
                    question=question,
                    system_prompt=system_prompt, ctx=ctx,
                )
                tokens = int(output.get("tokens_used", 0) or 0)
                tracer.record("other", {
                    "iterations": int(output.get("iterations", 0)),
                    "tool_calls": int(output.get("tool_calls", 0)),
                })
            elif self._tool_invoker is not None and self._llm is not None:
                # simple ReAct-like loop using tool invoker
                tools = json_loads_safe(agent.tools_json, [])
                max_iter = int(agent.max_iterations or _DEFAULT_MAX_ITERATIONS)
                messages = [{"role": "user", "content": question}]
                for i in range(1, max_iter + 1):
                    result = await self._llm.chat(
                        tenant_id=ctx.tenant_id,
                        model=agent.model,
                        messages=messages,
                        system_prompt=system_prompt,
                    )
                    content = getattr(result, "content", "") or ""
                    tool_calls = getattr(result, "tool_calls", None) or []
                    tracer.record("llm_call", {"iteration": i})

                    if not tool_calls:
                        output = {"answer": content, "iterations": i,
                                  "tool_calls": 0}
                        break

                    for call in tool_calls:
                        tool_name = call.get("name", "")
                        args = json_loads_safe(
                            call.get("arguments", "{}"), {},
                        )
                        tracer.record("tool_call", {
                            "name": tool_name, "iteration": i,
                        })
                        try:
                            await self._tool_invoker.invoke(
                                tenant_id=ctx.tenant_id,
                                tool_name=tool_name, args=args,
                            )
                        except Exception as exc:
                            logger.debug("tool invoke failed: %s", exc)
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content":
                                     "Continue based on tool results."})
                else:
                    raise LimitExceededAppError(
                        f"agent exceeded {max_iter} iterations"
                    )
            else:
                raise ExecutionAppError(
                    "no agent runner or LLM port configured"
                )
        except Exception as exc:
            logger.exception("agent invoke failed: %s", exc)
            status = RunStatus.FAILED
            error = str(exc)[:500]

        latency = ms_now() - started

        saved_run.output_json = json_dumps_safe(output)
        saved_run.status = str(status)
        saved_run.latency_ms = latency
        saved_run.tokens_used = tokens
        saved_run.cost_usd = Decimal("0")
        saved_run.error_message = error
        await self._runs.update(ctx, saved_run)

        if tracer.steps():
            try:
                trace_rows = [
                    LCTraceModel(
                        tenant_id=ctx.tenant_id, run_id=saved_run.id,
                        step=int(s["step"]), kind=s["kind"],
                        payload_json=json_dumps_safe(s.get("payload", {})),
                        latency_ms=int(s.get("latency_ms", 0)),
                    )
                    for s in tracer.steps()
                ]
                await self._traces.create_many(ctx, trace_rows)
            except Exception as exc:
                logger.debug("persist traces failed: %s", exc)

        if self._bus:
            try:
                await self._bus.publish(RunCompleted(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    kind="agent", status=str(status),
                    latency_ms=latency, tokens_used=tokens,
                ))
            except Exception:
                pass

        if status == RunStatus.FAILED:
            raise ExecutionAppError(error or "agent failed")

        return {
            "run_id": str(saved_run.id),
            "output": output,
            "status": str(status),
            "latency_ms": latency,
            "tokens_used": tokens,
            "trace_steps": len(tracer.steps()),
        }

    # ─── Memory ──────────────────────────────────
    async def get_memory(
        self, ctx: Any, conversation_id: uuid.UUID,
    ) -> Any:
        m = await self._memories.find_by_conversation(ctx, conversation_id)
        if m is None:
            raise NotFoundAppError("memory not found")
        return m

    async def update_memory(
        self, ctx: Any, *, conversation_id: uuid.UUID,
        memory_type: str, messages: list[dict[str, Any]],
    ) -> Any:
        from app.modules.langchain.infrastructure.models import (
            LCMemoryModel,
        )
        payload_json = json_dumps_safe(messages)
        size_bytes = len(payload_json.encode("utf-8"))

        existing = await self._memories.find_by_conversation(
            ctx, conversation_id,
        )
        if existing is None:
            row = LCMemoryModel(
                tenant_id=ctx.tenant_id,
                conversation_id=conversation_id,
                memory_type=memory_type,
                snapshot_json=payload_json,
                size_bytes=size_bytes,
            )
            saved = await self._memories.save(ctx, row)
        else:
            existing.memory_type = memory_type
            existing.snapshot_json = payload_json
            existing.size_bytes = size_bytes
            saved = await self._memories.save(ctx, existing)

        if self._bus:
            try:
                await self._bus.publish(MemoryUpdated(
                    memory_id=saved.id, tenant_id=ctx.tenant_id,
                    memory_type=memory_type, size_bytes=size_bytes,
                ))
            except Exception:
                pass
        return saved

    # ─── Runs & traces ───────────────────────────
    async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
        r = await self._runs.find_by_id(ctx, run_id)
        if r is None:
            raise NotFoundAppError("run not found")
        return r

    async def get_run_trace(
        self, ctx: Any, run_id: uuid.UUID,
    ) -> list[Any]:
        await self.get_run(ctx, run_id)
        return await self._traces.find_by_run(ctx, run_id)
