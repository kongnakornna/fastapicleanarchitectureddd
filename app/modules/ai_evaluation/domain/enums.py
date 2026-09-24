"""ai_evaluation enums"""
from __future__ import annotations
from enum import Enum


class MetricKind(str, Enum):
    """TH: ประเภท metric | EN: Metric kind"""
    EXACT_MATCH = "exact_match"
    F1 = "f1"
    ROUGE = "rouge"
    BLEU = "bleu"
    BERTSCORE = "bertscore"
    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_PRECISION = "context_precision"
    CONTEXT_RECALL = "context_recall"
    MRR = "mrr"
    NDCG = "ndcg"
    RAGAS = "ragas"
    HALLUCINATION = "hallucination"
    LATENCY = "latency"
    COST = "cost"

    def __str__(self) -> str:
        return str(self.value)


class RunStatus(str, Enum):
    """TH: สถานะ run | EN: Run status"""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    def __str__(self) -> str:
        return str(self.value)


class TaskType(str, Enum):
    """TH: ประเภทงาน | EN: Task type"""
    QA = "qa"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    RAG = "rag"
    AGENT = "agent"

    def __str__(self) -> str:
        return str(self.value)


class TargetKind(str, Enum):
    """TH: เป้าหมาย | EN: Target kind"""
    MODEL = "model"
    PIPELINE = "pipeline"

    def __str__(self) -> str:
        return str(self.value)
