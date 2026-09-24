"""ai_evaluation services — evaluators · judge · event bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.ai_evaluation.domain.helpers.metrics import (
    exact_match, f1_score, mrr, ndcg, precision_at_k, ragas_score,
    recall_at_k, rouge_l,
)
from app.modules.ai_evaluation.domain.value_objects import MetricScore

logger = logging.getLogger(__name__)


class ExactMatchEvaluator:
    name = "exact_match"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        return MetricScore(name=self.name, value=exact_match(answer, case.ground_truth))


class F1Evaluator:
    name = "f1"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        return MetricScore(name=self.name, value=f1_score(answer, case.ground_truth))


class RougeEvaluator:
    name = "rouge"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        return MetricScore(name=self.name, value=rouge_l(answer, case.ground_truth))


class MRREvaluator:
    name = "mrr"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        rank = 1 if answer and case.ground_truth and answer.strip() == case.ground_truth.strip() else 0
        return MetricScore(name=self.name, value=mrr([rank]) if rank > 0 else 0.0)


class NDCGEvaluator:
    name = "ndcg"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        rel = 1.0 if answer and case.ground_truth else 0.0
        return MetricScore(name=self.name, value=ndcg([rel], k=10))


class ContextPrecisionEvaluator:
    name = "context_precision"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        if not context:
            return MetricScore(name=self.name, value=0.0)
        retrieved = [str(i) for i in range(len(context))]
        relevant = {
            str(i) for i, c in enumerate(context)
            if case.ground_truth and case.ground_truth.lower() in c.lower()
        }
        return MetricScore(
            name=self.name,
            value=precision_at_k(retrieved, relevant, len(retrieved)),
        )


class ContextRecallEvaluator:
    name = "context_recall"
    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        if not context:
            return MetricScore(name=self.name, value=0.0)
        retrieved = [str(i) for i in range(len(context))]
        relevant = {
            str(i) for i, c in enumerate(context)
            if case.ground_truth and case.ground_truth.lower() in c.lower()
        }
        return MetricScore(
            name=self.name,
            value=recall_at_k(retrieved, relevant, len(retrieved)),
        )


class FaithfulnessEvaluator:
    name = "faithfulness"
    def __init__(self, judge: Any = None) -> None:
        self._judge = judge

    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        if not context or not answer or self._judge is None:
            return MetricScore(name=self.name, value=0.0, confidence=0.5)
        ctx_text = "\n".join(context)
        prompt = (
            "Rate 0.0-1.0 how faithful the answer is to context. "
            "Reply with ONLY the number.\n\n"
            f"Context:\n{ctx_text}\n\nAnswer:\n{answer}"
        )
        try:
            out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
            score = float(out.get("score", 0.0) or 0.0)
            return MetricScore(
                name=self.name,
                value=max(0.0, min(1.0, score)),
                confidence=0.8,
            )
        except Exception as exc:
            logger.debug("faithfulness judge failed: %s", exc)
            return MetricScore(name=self.name, value=0.0, confidence=0.3)


class AnswerRelevanceEvaluator:
    name = "answer_relevance"
    def __init__(self, judge: Any = None) -> None:
        self._judge = judge

    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        if not answer or self._judge is None:
            return MetricScore(name=self.name, value=0.0, confidence=0.5)
        prompt = (
            "Rate 0.0-1.0 how relevant the answer is to the question. "
            "Reply with ONLY the number.\n\n"
            f"Question:\n{case.question}\n\nAnswer:\n{answer}"
        )
        try:
            out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
            score = float(out.get("score", 0.0) or 0.0)
            return MetricScore(
                name=self.name,
                value=max(0.0, min(1.0, score)),
                confidence=0.8,
            )
        except Exception as exc:
            logger.debug("relevance judge failed: %s", exc)
            return MetricScore(name=self.name, value=0.0, confidence=0.3)


class HallucinationEvaluator:
    name = "hallucination"
    def __init__(self, judge: Any = None) -> None:
        self._judge = judge

    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        if not context or not answer or self._judge is None:
            return MetricScore(name=self.name, value=0.0, confidence=0.5)
        ctx_text = "\n".join(context)
        prompt = (
            "Rate 0.0-1.0 how much the answer is hallucinated. "
            "Reply with ONLY the number.\n\n"
            f"Context:\n{ctx_text}\n\nAnswer:\n{answer}"
        )
        try:
            out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
            score = float(out.get("score", 0.0) or 0.0)
            return MetricScore(
                name=self.name,
                value=max(0.0, min(1.0, score)),
                higher_is_better=False, confidence=0.8,
            )
        except Exception as exc:
            logger.debug("hallucination judge failed: %s", exc)
            return MetricScore(name=self.name, value=0.0, confidence=0.3)


class RAGASEvaluator:
    name = "ragas"
    def __init__(self, judge: Any = None) -> None:
        self._faith = FaithfulnessEvaluator(judge)
        self._rel = AnswerRelevanceEvaluator(judge)
        self._prec = ContextPrecisionEvaluator()
        self._rec = ContextRecallEvaluator()

    async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
        try:
            f = await self._faith.evaluate(case=case, answer=answer, context=context)
            r = await self._rel.evaluate(case=case, answer=answer, context=context)
            p = await self._prec.evaluate(case=case, answer=answer, context=context)
            c = await self._rec.evaluate(case=case, answer=answer, context=context)
            score = ragas_score(f.value, r.value, p.value, c.value)
            return MetricScore(
                name=self.name, value=score,
                details={
                    "faithfulness": f.value,
                    "answer_relevance": r.value,
                    "context_precision": p.value,
                    "context_recall": c.value,
                },
            )
        except Exception as exc:
            logger.warning("ragas failed: %s", exc)
            return MetricScore(name=self.name, value=0.0)


class LLMPortJudgeAdapter:
    """TH: LLMPort as judge | EN: LLM judge adapter"""
    def __init__(self, llm_port: Any) -> None:
        self._llm = llm_port

    async def judge(self, *, model: str, prompt: str, context: str = "") -> dict[str, Any]:
        result = await self._llm.chat(
            tenant_id=uuid.UUID(int=0),
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = getattr(result, "content", "") or ""
        try:
            score = float(content.strip().split()[0])
        except Exception:
            score = 0.0
        return {"score": score, "raw": content}


class RAGTargetAdapter:
    """TH: RAGUseCase as target | EN: RAG target adapter"""
    def __init__(self, rag_use_case: Any) -> None:
        self._rag = rag_use_case

    async def invoke(
        self, *, target: Any, question: str,
        context: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
        result = await self._rag.query(
            ctx, query=question, pipeline_id=target.pipeline_id,
        )
        return {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "total_tokens": result.get("usage", {}).get("total_tokens", 0),
            "cost_usd": result.get("usage", {}).get("cost_usd", 0.0),
        }


class LoggingEventBus:
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
