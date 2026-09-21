"""123Abc infrastructure services"""
from __future__ import annotations

import structlog

log = structlog.get_logger()


class 123AbcDomainService:
    """123AbcDomainService — บริการระดับ infrastructure"""

    async def healthcheck(self) -> bool:
        try:
            return True
        except Exception as e:
            log.warning("service.healthcheck_failed", err=str(e))
            return False