"""langchain enums"""
from __future__ import annotations
from enum import Enum


class ChainType(str, Enum):
    """TH: ประเภท chain | EN: Chain type"""
    LCEL = "lcel"
    SEQUENTIAL = "sequential"
    ROUTER = "router"
    MAP_REDUCE = "map_reduce"
    REFINE = "refine"
    STUFF = "stuff"

    def __str__(self) -> str:
        return str(self.value)


class AgentType(str, Enum):
    """TH: ประเภท agent | EN: Agent type"""
    REACT = "react"
    OPENAI_TOOLS = "openai_tools"
    PLAN_EXECUTE = "plan_execute"
    SELF_ASK = "self_ask"
    REFLEXION = "reflexion"

    def __str__(self) -> str:
        return str(self.value)


class MemoryType(str, Enum):
    """TH: ประเภท memory | EN: Memory type"""
    BUFFER = "buffer"
    WINDOW = "window"
    SUMMARY = "summary"
    SUMMARY_BUFFER = "summary_buffer"
    VECTOR = "vector"
    KG = "kg"

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


class TraceKind(str, Enum):
    """TH: ประเภท trace step | EN: Trace step kind"""
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    ROUTER_BRANCH = "router_branch"
    RETRIEVAL = "retrieval"
    OTHER = "other"

    def __str__(self) -> str:
        return str(self.value)
