"""tenancy presentation dependencies — FastAPI DI."""
from fastapi import Depends

from ..application.use_cases import TenancyUseCases
from ..infrastructure.repositories import PostgresTenantRepository


async def get_tenancy_use_cases(session=None) -> TenancyUseCases:
    """DI provider — สร้าง use cases."""
    repo = PostgresTenantRepository(session)
    return TenancyUseCases(repo=repo)