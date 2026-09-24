"""EvalResult entity — alias to ORM"""
from __future__ import annotations
from app.modules.ai_evaluation.infrastructure.models import EvalResultModel


class EvalResult(EvalResultModel):
    """TH: EvalResult | EN: EvalResult entity (alias)"""
