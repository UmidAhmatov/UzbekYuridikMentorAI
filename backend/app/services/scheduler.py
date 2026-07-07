from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.services.embedding_backfill import backfill_missing_embeddings
from app.services.legal_sources import LEGAL_SOURCES
from scripts.ingest import ingest_sources

logger = logging.getLogger("uvicorn.error")
MONTHLY_INGEST_JOB_ID = "monthly-lexuz-labor-code-ingest"

_scheduler: AsyncIOScheduler | None = None


async def run_monthly_legal_ingest() -> None:
    settings = get_settings()
    logger.info("Monthly Lex.uz ingest started for %s legal sources.", len(LEGAL_SOURCES))
    results = await ingest_sources(
        list(LEGAL_SOURCES),
        batch_size=settings.ingest_batch_size,
        with_embeddings=False,
    )
    embeddings_added = await backfill_missing_embeddings(
        batch_size=settings.ingest_batch_size,
    )
    logger.info(
        "Monthly Lex.uz ingest completed: sources=%s chunks=%s upserted=%s embeddings=%s",
        len(results),
        sum(result.chunk_count for result in results),
        sum(result.upserted_count for result in results),
        embeddings_added,
    )


def start_scheduler() -> AsyncIOScheduler | None:
    global _scheduler
    settings = get_settings()
    if not settings.scheduler_enabled:
        logger.info("APScheduler is disabled.")
        return None
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    scheduler = build_scheduler()
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "APScheduler started; monthly ingest runs on day 1 at %02d:%02d %s.",
        settings.monthly_ingest_hour,
        settings.monthly_ingest_minute,
        settings.scheduler_timezone,
    )
    return scheduler


def build_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    timezone = ZoneInfo(settings.scheduler_timezone)
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(
        run_monthly_legal_ingest,
        trigger=CronTrigger(
            day=1,
            hour=settings.monthly_ingest_hour,
            minute=settings.monthly_ingest_minute,
            timezone=timezone,
        ),
        id=MONTHLY_INGEST_JOB_ID,
        name="Lex.uz legal catalog monthly ingest",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=24 * 60 * 60,
    )
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None


def scheduler_status() -> str:
    if not get_settings().scheduler_enabled:
        return "disabled"
    return "running" if _scheduler is not None and _scheduler.running else "stopped"
