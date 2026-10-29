"""Scheduled deletion of expired Demos and earlier days' AI usage rows (AC-024.9, AC-025.7)."""

import asyncio
import logging

from app import ai_usage
from app.api import demo


logger = logging.getLogger(__name__)

# Runs at startup and then hourly, so data is deleted within about an hour of expiring.
RETENTION_INTERVAL_SECONDS = 3600


def run_retention():
    """Apply each retention rule; a failure is logged and retried on the next run."""
    for task in (demo.delete_expired_demos, ai_usage.delete_old_ai_usage):
        try:
            task()
        except Exception:
            logger.exception("Retention task %s failed; it will be retried on the next run.", task.__name__)


async def retention_loop():
    while True:
        await asyncio.sleep(RETENTION_INTERVAL_SECONDS)
        await asyncio.to_thread(run_retention)
