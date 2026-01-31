from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.core.cache import cache
from app.core.websocket_manager import ws_manager
from app.services.greyline import compute_greyline
from app.services.space_weather import fetch_kp, fetch_sfi, fetch_ssn, fetch_xray

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _broadcast(key: str, data: dict) -> None:
    """Store in cache and broadcast via WebSocket."""
    cache.set(key, data)
    await ws_manager.broadcast({"type": key, "data": data})


async def job_fetch_sfi() -> None:
    data = await fetch_sfi()
    if data:
        await _broadcast("sfi", data)
        logger.info("SFI updated: %.1f", data["value"])


async def job_fetch_kp() -> None:
    data = await fetch_kp()
    if data:
        await _broadcast("kp", data)
        logger.info("Kp updated: %.1f", data["value"])


async def job_fetch_xray() -> None:
    data = await fetch_xray()
    if data:
        await _broadcast("xray", data)
        logger.info("X-ray updated: %s", data["flare_class"])


async def job_fetch_ssn() -> None:
    data = await fetch_ssn()
    if data:
        await _broadcast("ssn", data)
        logger.info("SSN updated: %d", data["value"])


async def job_compute_greyline() -> None:
    try:
        data = await asyncio.to_thread(compute_greyline)
        await _broadcast("greyline", data)
        logger.info("Grey line updated")
    except Exception as e:
        logger.error("Failed to compute grey line: %s", e)


async def start_scheduler() -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()

    _scheduler.add_job(job_fetch_sfi, "interval", seconds=settings.sfi_interval, id="sfi")
    _scheduler.add_job(job_fetch_kp, "interval", seconds=settings.kp_interval, id="kp")
    _scheduler.add_job(job_fetch_xray, "interval", seconds=settings.xray_interval, id="xray")
    _scheduler.add_job(job_fetch_ssn, "interval", seconds=settings.ssn_interval, id="ssn")
    _scheduler.add_job(
        job_compute_greyline, "interval", seconds=settings.greyline_interval, id="greyline"
    )

    _scheduler.start()
    logger.info("Scheduler started")

    # Run initial data fetch
    asyncio.create_task(_initial_fetch())


async def _initial_fetch() -> None:
    """Fetch all data immediately on startup."""
    logger.info("Running initial data fetch...")
    await asyncio.gather(
        job_fetch_sfi(),
        job_fetch_kp(),
        job_fetch_xray(),
        job_fetch_ssn(),
        job_compute_greyline(),
        return_exceptions=True,
    )
    logger.info("Initial data fetch complete")


async def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
