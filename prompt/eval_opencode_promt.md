# eval_opencode_promt.md — Module `ai_evaluation` Generator Prompt

## 🎯 Purpose
LLM / RAG evaluation
(RAGAS, faithfulness, MRR, NDCG, hallucination detection)
**Depends on:** `llm`, `rag`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `ai_evaluation` |
| PREFIX | `eval` |
| VERSION | `1.0.0` |
| DEPS | `llm`, `rag` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `eval_datasets` | Datasets |
| `eval_test_cases` | Cases (question, ground_truth, context) |
| `eval_runs` | Run of dataset against model/pipeline |
| `eval_metrics` | Metric definitions |
| `eval_results` | Per-case scores |
| `eval_reports` | Aggregated reports |

## 🔤 Enums
- `MetricKind`: EXACT_MATCH, F1, ROUGE, BLEU, BERTSCORE,
                FAITHFULNESS, ANSWER_RELEVANCE, CONTEXT_PRECISION,
                CONTEXT_RECALL, MRR, NDCG, RAGAS, HALLUCINATION,
                LATENCY, COST
- `RunStatus`: QUEUED, RUNNING, DONE, FAILED, CANCELLED
- `TaskType`: QA, SUMMARIZATION, CLASSIFICATION, RAG, AGENT

## 💎 Value Objects
- `MetricScore(name, value, confidence, details)`
- `EvalConfig(metrics, sample_size, temperature, seed)`

## 🔌 Public Port
```python
class EvalRunnerPort(Protocol):
    async def run(self, *, dataset_id: uuid.UUID,
                  target: EvalTarget,
                  config: EvalConfig) -> EvalReportRef: ...
```

## 🌐 Endpoints
```
GET    /api/v1/eval/datasets
POST   /api/v1/eval/datasets
POST   /api/v1/eval/run
GET    /api/v1/eval/runs/{id}
GET    /api/v1/eval/runs/{id}/report
GET    /api/v1/eval/metrics
```

## 📤 Opencode Prompt

```
Generate `create_module_ai_evaluation.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "ai_evaluation"
  PREFIX      = "eval"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.llm.application.ports import LLMPort
  from app.modules.rag.application.ports import RAGPort

ENTITIES:
  EvalDataset(id, tenant_id, name, description, task_type,
              version, case_count, created_at, updated_at)
  EvalTestCase(id, dataset_id, question, ground_truth,
               context_json, metadata_json, created_at, updated_at)
  EvalRun(id, tenant_id, user_id, dataset_id, target_model,
          target_pipeline, config_json, status, started_at,
          finished_at, created_at, updated_at)
  EvalMetric(id, name, kind, higher_is_better, range_min, range_max,
             created_at, updated_at)
  EvalResult(id, run_id, case_id, metric_name, score, details_json,
             latency_ms, cost_usd, created_at, updated_at)
  EvalReport(id, run_id, summary_json, passed, generated_at,
             created_at, updated_at)

ENUMS:
  MetricKind(str, Enum): EXACT_MATCH, F1, ROUGE, BLEU, BERTSCORE,
                          FAITHFULNESS, ANSWER_RELEVANCE,
                          CONTEXT_PRECISION, CONTEXT_RECALL,
                          MRR, NDCG, RAGAS, HALLUCINATION,
                          LATENCY, COST
  RunStatus(str, Enum): QUEUED, RUNNING, DONE, FAILED, CANCELLED
  TaskType(str, Enum): QA, SUMMARIZATION, CLASSIFICATION, RAG, AGENT

VALUE OBJECTS:
  MetricScore(name, value, confidence, details)
  EvalConfig(metrics: list[str], sample_size: int,
             temperature: float, seed: int | None)
  EvalTarget(kind: "model" | "pipeline", ref: str)

EVENTS:
  DatasetCreated, EvalRunStarted, EvalRunCompleted, MetricComputed,
  HallucinationDetected

PORTS:
  EvalRunnerPort (run)
  MetricEvaluator Protocol:
    - ExactMatchEvaluator, F1Evaluator, RougeEvaluator,
      BleuEvaluator, BertScoreEvaluator
    - FaithfulnessEvaluator, AnswerRelevanceEvaluator,
      ContextPrecisionEvaluator, ContextRecallEvaluator
    - MRREvaluator, NDCGEvaluator
    - RAGASEvaluator (combines faithfulness + relevance + precision + recall)
    - HallucinationEvaluator (uses LLMPort as judge)

USE CASES:
  CreateDatasetUseCase, RunEvaluationUseCase, GetReportUseCase

ENDPOINTS:
  GET  /api/v1/eval/datasets
  POST /api/v1/eval/datasets
  POST /api/v1/eval/run
  GET  /api/v1/eval/runs/{id}
  GET  /api/v1/eval/runs/{id}/report
  GET  /api/v1/eval/metrics

EVAL PIPELINE:
  1. Load EvalDataset + cases
  2. Sample if sample_size < len(cases) (seeded)
  3. For each case:
     a. If target=model → LLMPort.chat(question) → answer
     b. If target=pipeline → RAGPort.answer(question) → answer + citations
     c. Compute each metric:
        - Compare answer vs ground_truth
        - If context available → faithfulness, precision, recall
        - If ranking available → MRR, NDCG
     d. Persist EvalResult
  4. Aggregate → EvalReport(summary_json, passed)
  5. Publish EvalRunCompleted

METRIC HELPERS (module helpers):
  exact_match(pred, ref) -> float
  f1(pred_tokens, ref_tokens) -> float
  rouge_l(pred, ref) -> float
  bleu(pred, ref, n=4) -> float
  faithfulness(answer, context, judge: LLMPort) -> float
  answer_relevance(question, answer, judge: LLMPort) -> float
  context_precision(retrieved, relevant) -> float
  context_recall(retrieved, relevant) -> float
  mrr(ranks) -> float
  ndcg(relevances, k) -> float
  ragas_score(faith, rel, prec, rec) -> float   # harmonic mean
  hallucination(answer, context, judge: LLMPort) -> float

SQL:
  Indexes:
    ix_eval_ds_tenant_name UNIQUE
    ix_eval_case_dataset
    ix_eval_run_tenant_time
    ix_eval_run_status
    ix_eval_res_run_metric
    ix_eval_rep_run
    ix_eval_metric_name UNIQUE
  Trigger set_updated_at_eval + RLS
  Seed V002: default metrics rows (MRR, NDCG, faithfulness,
             answer_relevance, context_precision, context_recall,
             RAGAS, hallucination)

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Create dataset 10 cases → 201
2. Run vs gpt-4o-mini → status DONE
3. Report has MRR, NDCG, faithfulness
4. RAGAS computed correctly
5. Hallucination detection works
6. Cost/latency aggregated
7. Cross-model comparison (2 runs)
8. Export CSV/JSON
9. `sample_size=50%` working
10. Concurrent runs isolated

## ✅ Checklist
- [ ] `EvalRunnerPort` importable
- [ ] RAGAS combines 4 sub-metrics
- [ ] LLM-as-judge uses LLMPort
- [ ] Report aggregator returns `summary_json` with all metrics