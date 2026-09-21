from dataclasses import dataclass


@dataclass(frozen=True)
class ApiKey:
    id: int
    name: str
    prefix: str        # e.g. "sk-abc..."
    created_at: str
    last_used: str
    expires_at: str | None
    is_active: bool
