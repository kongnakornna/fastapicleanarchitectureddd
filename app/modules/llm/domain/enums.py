"""llm enums — Enum ของ llm"""
from __future__ import annotations
from enum import StrEnum


class ProviderType(StrEnum):
    """TH: ประเภทผู้ให้บริการ | EN: Provider type"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"


class MessageRole(StrEnum):
    """TH: บทบาทข้อความ | EN: Message role"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ConversationStatus(StrEnum):
    """TH: สถานะ conversation | EN: Conversation status"""
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class FinishReason(StrEnum):
    """TH: เหตุผลที่จบ | EN: Finish reason"""
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"
