from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    id: int
    title: str
    body: str
    category: str        # job | quotation | stock | system
    is_read: bool
    created_at: str
