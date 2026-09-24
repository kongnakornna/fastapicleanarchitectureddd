"""app/middleware/__init__.py"""
from app.middleware.tenant import TenantMiddleware

__all__ = ["TenantMiddleware"]
