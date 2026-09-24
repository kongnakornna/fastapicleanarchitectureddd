"""ai_evaluation use cases"""
from __future__ import annotations
import asyncio
import logging
import uuid
from decimal import Decimal
from typing import Any, Optional

from app.modules.ai_evaluation.application.exceptions import (
    ConflictAppError, NotFoundAppError, ValidationAppError,
)
from app.modules.ai_evaluation.application.utils import (
    aggregate_scores, json_dumps_safe, json_loads_safe, ms_now,
    sample_cases,
)
from app.modules.ai_evaluation.domain.events import (
    DatasetCreated, EvalRunCompleted, EvalRunStarted,
)
from app.modules.ai_evaluation.domain.value_objects import (
    EvalConfig, EvalTarget,
)

logger = logging.getLogger(__name__)

_DEFAULT_PASS_THRESHOLD = 0.7


class AIEvaluationUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)
        self._pass_threshold = _DEFAULT_PASS_THRESHOLD

    async def create_dataset(
        self, ctx: Any, *,
        name: str, description: str = "",
        task_type: str = "qa",
        cases: Optional[list[dict[str, Any]]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Any:
        """TH: สร้าง dataset | EN: create dataset"""
        from app.modules.ai_evaluation.infrastructure.models import (
            EvalDatasetModel, EvalTestCaseModel,
        )

        existing = await self._datasets.find_by_name(ctx, name)
        if existing is not None:
            raise ConflictAppError(f"dataset exists: {name}")

        ds = EvalDatasetModel(
            tenant_id=ctx.tenant_id, name=name,
            description=description, task_type=task_type,
            metadata_json=json_dumps_safe(metadata or {}),
        )
        saved = await self._datasets.save(ctx, ds)

        if cases:
            rows = [
                EvalTestCaseModel(
                    tenant_id=ctx.tenant_id, dataset_id=saved.id,
                    question=c.get("question", ""),
                    ground_truth=c.get("ground_truth", ""),
                    context_json=json_dumps_safe(c.get("context") or []),
                )
                for c in cases
            ]
            count = await self._cases.create_many(ctx, rows)
            saved.case_count = count
            saved = await self._datasets.save(ctx, saved)

        if self._bus:
            try:
                await self._bus.publish(DatasetCreated(
                    dataset_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, task_type=task_type,
                    case_count=saved.case_count or 0,
                ))
            except Exception as exc:
                logger.debug("publish failed: %s", exc)
        return saved

    async def list_datasets(self, ctx: Any) -> list[Any]:
        return await self._datasets.find_all(ctx)

    async def get_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> Any:
        ds = await self._datasets.find_by_id(ctx, dataset_id)
        if ds is None:
            raise NotFoundAppError("dataset not found")
        return ds

    async def run_evaluation(
        self, ctx: Any, *,
        dataset_id: uuid.UUID,
        target: EvalTarget,
        config: Optional[EvalConfig] = None,
    ) -> Any:
        """TH: รันการประเมิน | EN: run evaluation"""
        from app.modules.ai_evaluation.infrastructure.models import (
            EvalResultModel, EvalRunModel, EvalReportModel,
        )

        cfg = config or EvalConfig()
        ds = await self.get_dataset(ctx, dataset_id)
        cases = await self._cases.find_by_dataset(ctx, dataset_id)
        if not cases:
            raise ValidationAppError("dataset has no cases")

        selected = sample_cases(cases, cfg.sample_size, cfg.seed)

        run = EvalRunModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            dataset_id=ds.id,
            target_kind=str(target.kind),
            target_model=target.ref,
            target_pipeline=target.pipeline_id or "",
            config_json=json_dumps_safe(cfg.model_dump()),
            case_count=len(selected),
            status="QUEUED",
        )
        saved_run = await self._runs.save(ctx, run)

        if self._bus:
            try:
                await self._bus.publish(EvalRunStarted(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    dataset_id=dataset_id, target_model=target.ref,
                ))
            except Exception:
                pass

        saved_run.status = "RUNNING"
        saved_run.started_at = datetime.now(UTC)
        saved_run = await self._runs.update(ctx, saved_run)

        started = ms_now()
        all_results: list[Any] = []
        completed = 0
        failed = 0
        total_cost = Decimal("0")

        for case in selected:
            try:
                results = await self._evaluate_case(
                    ctx, saved_run, case, target, cfg,
                )
                for r in results:
                    all_results.append(r)
                    total_cost += r.cost_usd
                completed += 1
            except Exception as exc:
                logger.warning("case failed: %s", exc)
                failed += 1

        if all_results:
            await self._results.create_many(ctx, all_results)

        saved_run.status = "DONE"
        saved_run.completed_count = completed
        saved_run.failed_count = failed
        saved_run.total_cost_usd = total_cost
        saved_run.finished_at = datetime.now(UTC)
        saved_run.duration_ms = ms_now() - started
        saved_run = await self._runs.update(ctx, saved_run)

        summary = aggregate_scores([
            {"metric_name": r.metric_name, "score": r.score}
            for r in all_results
        ])
        passed = self._evaluate_pass(summary)

        report = EvalReportModel(
            tenant_id=ctx.tenant_id, run_id=saved_run.id,
            summary_json=json_dumps_safe(summary),
            passed=passed,
        )
        await self._reports.save(ctx, report)

        if self._bus:
            try:
                await self._bus.publish(EvalRunCompleted(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    status="DONE",
                    metrics_json=json_dumps_safe(summary),
                    duration_ms=saved_run.duration_ms or 0,
                ))
            except Exception:
                pass
        return saved_run

    async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
        r = await self._runs.find_by_id(ctx, run_id)
        if r is None:
            raise NotFoundAppError("run not found")
        return r

    async def get_report(self, ctx: Any, run_id: uuid.UUID) -> Any:
        r = await self._reports.find_by_run(ctx, run_id)
        if r is None:
            raise NotFoundAppError("report not found")
        return r

    async def list_metrics(self, ctx: Any) -> list[Any]:
        return await self._metrics.find_all(ctx)

    async def _evaluate_case(
        self, ctx: Any, run: Any, case: Any,
        target: EvalTarget, cfg: EvalConfig,
    ) -> list[Any]:
        from app.modules.ai_evaluation.infrastructure.models import (
            EvalResultModel,
        )

        context = json_loads_safe(case.context_json, [])
        answer = ""
        tokens = 0
        cost = Decimal("0")
        latency = 0

        if self._target is not None:
            st = ms_now()
            try:
                out = await self._target.invoke(
                    target=target, question=case.question,
                    context=context,
                )
                answer = out.get("answer", "")
                tokens = int(out.get("total_tokens", 0))
                cost = Decimal(str(out.get("cost_usd", "0")))
            except Exception as exc:
                logger.warning("target invoke failed: %s", exc)
            latency = ms_now() - st

        results: list[Any] = []
        for metric_name in cfg.metrics:
            evaluator = self._evaluators.get(metric_name)
            if evaluator is None:
                continue
            try:
                score = await evaluator.evaluate(
                    case=case, answer=answer, context=context,
                )
            except Exception as exc:
                logger.warning("metric %s failed: %s", metric_name, exc)
                continue

            results.append(EvalResultModel(
                tenant_id=ctx.tenant_id, run_id=run.id,
                case_id=case.id, metric_name=metric_name,
                score=score.value,
                confidence=score.confidence,
                details_json=json_dumps_safe(score.details or {}),
                answer_text=answer[:2000],
                latency_ms=latency, tokens_used=tokens,
                cost_usd=cost,
            ))
        return results

    def _evaluate_pass(self, summary: dict[str, dict[str, float]]) -> bool:
        if not summary:
            return False
        means = [v.get("mean", 0.0) for v in summary.values()]
        if not means:
            return False
        return (sum(means) / len(means)) >= self._pass_threshold
