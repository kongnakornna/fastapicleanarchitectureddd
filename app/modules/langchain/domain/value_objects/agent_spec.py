"""AgentSpec VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

from app.modules.langchain.domain.enums import AgentType


class AgentSpec(BaseModel):
    """TH: ข้อกำหนด agent | EN: Agent specification"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    agent_type: AgentType = AgentType.REACT
    tools: list[str] = Field(default_factory=list)
    model: str = Field(default="gpt-4o-mini", max_length=100)
    max_iterations: int = Field(default=10, ge=1, le=50)
    system_prompt: str = ""
    config: dict = Field(default_factory=dict)
