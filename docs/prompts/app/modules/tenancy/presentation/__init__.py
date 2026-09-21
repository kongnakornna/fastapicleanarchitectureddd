"""tenancy presentation layer."""
from .dependencies import get_tenancy_use_cases
from .routers import router

__all__ = ["router", "get_tenancy_use_cases"]