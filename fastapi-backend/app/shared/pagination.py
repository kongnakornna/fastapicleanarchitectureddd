# app/shared/pagination.py - pagination helpers
from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    """Page result."""

    items: list
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return max(1, (self.total + self.limit - 1) // self.limit)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
