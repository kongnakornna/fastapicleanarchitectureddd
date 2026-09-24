"""iot Scheduler — Cron jobs"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger


class IotScheduler:
    """TH: Scheduler จัดการ tasks | EN: manage scheduled tasks"""

    def __init__(self, session_factory=None) -> None:
        self._scheduler = AsyncIOScheduler(timezone="Asia/Bangkok")
        self._session_factory = session_factory
        self._registered = False

    def start(self) -> None:
        if self._registered:
            return
        self._register_jobs()
        self._scheduler.start()
        self._registered = True
        logger.info("iot scheduler started")

    def stop(self) -> None:
        if self._registered:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception:
                pass
            self._registered = False
            logger.info("iot scheduler stopped")

    def _register_jobs(self) -> None:
        # Cleanup old data (daily 03:00)
        self._scheduler.add_job(
            self._cleanup_old_data,
            trigger=CronTrigger(hour=3, minute=0),
            id="cleanup_old_data",
            replace_existing=True,
        )

        # Check offline devices (ทุก 5 นาที)
        self._scheduler.add_job(
            self._check_offline_devices,
            trigger=IntervalTrigger(minutes=5),
            id="check_offline",
            replace_existing=True,
        )

        # Warmup cache (ทุก 1 นาที)
        self._scheduler.add_job(
            self._warmup_cache,
            trigger=IntervalTrigger(minutes=1),
            id="warmup_cache",
            replace_existing=True,
        )

    async def _cleanup_old_data(self) -> None:
        if self._session_factory is None:
            return
        try:
            async with self._session_factory() as session:
                from app.modules.iot.infrastructure.repositories import (
                    IotDataRepository,
                )
                repo = IotDataRepository(session)
                deleted = await repo.cleanup_old(90)
                await session.commit()
                logger.info(f"cleanup_old_data: deleted {deleted} rows")
        except Exception as exc:
            logger.error(f"cleanup_old_data failed: {exc}")

    async def _check_offline_devices(self) -> None:
        if self._session_factory is None:
            return
        try:
            from sqlalchemy import select
            from app.modules.iot.infrastructure.models import DeviceStatus

            cutoff = datetime.now(UTC) - timedelta(minutes=15)
            async with self._session_factory() as session:
                r = await session.execute(
                    select(DeviceStatus).where(
                        DeviceStatus.is_online.is_(True),
                        DeviceStatus.last_seen < cutoff,
                    )
                )
                stale = list(r.scalars().all())
                for st in stale:
                    st.is_online = False
                await session.commit()
                if stale:
                    logger.info(f"marked {len(stale)} devices offline")
        except Exception as exc:
            logger.error(f"check_offline_devices failed: {exc}")

    async def _warmup_cache(self) -> None:
        logger.debug("warmup_cache tick")

    def get_jobs_info(self) -> list[dict]:
        """คืนข้อมูล jobs สำหรับ admin endpoint"""
        jobs = []
        if not self._registered:
            return jobs
        for job in self._scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs


# ═══════════════════════════════════════════════════════════════
#  GLOBAL INSTANCE MANAGEMENT
# ═══════════════════════════════════════════════════════════════
iot_scheduler: IotScheduler | None = None


def set_scheduler_instance(scheduler: IotScheduler) -> None:
    """TH: ตั้ง instance (เรียกจาก app.py lifespan)"""
    global iot_scheduler
    iot_scheduler = scheduler


def get_scheduler(session_factory=None) -> IotScheduler:
    """TH: ดึง instance ปัจจุบัน"""
    global iot_scheduler
    if iot_scheduler is None:
        iot_scheduler = IotScheduler(session_factory)
    return iot_scheduler
