"""
TH: pdpa presentation layer — HTTP, schemas, docs, DI
EN: pdpa presentation layer — HTTP, schemas, docs, DI

Public surface:
    pdpa_router  — FastAPI APIRouter for the PDPA module (mounted at /pdpa)

Everything else (schemas, docs, dependencies) is intentionally private to
the module and should be imported from its concrete submodule to keep
the import graph explicit:

    from app.modules.pdpa.presentation.dependencies import get_consent_repo
    from app.modules.pdpa.presentation.schemas import ConsentResponse
"""
from __future__ import annotations

from app.modules.pdpa.presentation.routers import router as pdpa_router

__all__ = ["pdpa_router"]
