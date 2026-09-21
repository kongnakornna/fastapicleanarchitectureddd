"""tenancy presentation layer."""

from .dependencies import get_tenancy_use_cases
from .routers import router

__all__ = ["get_tenancy_use_cases", "router"]
