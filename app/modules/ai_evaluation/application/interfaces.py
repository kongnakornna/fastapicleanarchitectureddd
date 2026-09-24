"""ai_evaluation application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

from app.modules.ai_evaluation.domain.entities import (
    EvalDataset, EvalMetric, EvalReport, EvalResult, EvalRun,
    EvalTestCase,
)
from app.modules.ai_evaluation.domain.value_objects import (
    EvalTarget, MetricScore,
)


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class EvalDatasetRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, d: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all(self, ctx: Any) -> list[Any]: ...


class EvalTestCaseRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, cases: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> list[Any]: ...
    @abstractmethod
    async def count_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> int: ...


class EvalRunRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def update(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def list_by_tenant(self, ctx: Any, limit: int = 50) -> list[Any]: ...


class EvalMetricRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, m: Any) -> Any: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all(self, ctx: Any) -> list[Any]: ...


class EvalResultRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, results: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_run(self, ctx: Any, run_id: uuid.UUID) -> list[Any]: ...


class EvalReportRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_run(self, ctx: Any, run_id: uuid.UUID) -> Any | None: ...


class MetricEvaluator(Protocol):
    """TH: port ของ metric evaluator | EN: metric evaluator port"""
    name: str

    async def evaluate(
        self, *, case: Any, answer: str,
        context: Optional[list[str]] = None,
    ) -> MetricScore: ...


class LLMJudgePort(Protocol):
    """TH: port LLM-as-judge | EN: LLM judge port"""
    async def judge(
        self, *, model: str, prompt: str, context: str = "",
    ) -> dict[str, Any]: ...


class TargetInvokerPort(Protocol):
    """TH: port target invoker | EN: target invoker port"""
    async def invoke(
        self, *, target: EvalTarget, question: str,
        context: Optional[list[str]] = None,
    ) -> dict[str, Any]: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
