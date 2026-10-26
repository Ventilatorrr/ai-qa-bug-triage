"""Persistent daily AI Assist request limits per account and across all accounts."""

import os
import re
from datetime import datetime, timezone

from app.database import get_connection


DEFAULT_USER_LIMIT = 50
DEFAULT_GLOBAL_LIMIT = 500


class AiUsageLimitReached(Exception):
    pass


class AiUsageMisconfigured(Exception):
    pass


def _configured_limit(name, default):
    # Read per request, like OPENAI_API_KEY. Unset or blank uses the default.
    value = (os.getenv(name) or "").strip()
    if not value:
        return default
    if not re.fullmatch(r"[0-9]+", value):
        raise AiUsageMisconfigured("AI assistance is unavailable because its usage limits are misconfigured.")
    return int(value)


def utc_today():
    return datetime.now(timezone.utc).date().isoformat()


def reserve_ai_request(user_id: int) -> None:
    """Count one request toward today's limits, or reject it, before the provider is called.

    The short IMMEDIATE transaction serializes concurrent reservations and is
    committed before the provider call, so no write lock is held while waiting.
    """
    user_limit = _configured_limit("AI_DAILY_USER_LIMIT", DEFAULT_USER_LIMIT)
    global_limit = _configured_limit("AI_DAILY_GLOBAL_LIMIT", DEFAULT_GLOBAL_LIMIT)
    today = utc_today()
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        used_by_user, used_globally = conn.execute(
            "SELECT COALESCE(SUM(user_id = ?), 0), COUNT(*) FROM ai_requests WHERE usage_date = ?",
            (user_id, today),
        ).fetchone()
        if used_by_user >= user_limit:
            raise AiUsageLimitReached("You have reached your daily AI Assist limit. Try again after 00:00 UTC.")
        if used_globally >= global_limit:
            raise AiUsageLimitReached("AI Assist has reached its daily limit for all users. Try again after 00:00 UTC.")
        conn.execute("INSERT INTO ai_requests (user_id, usage_date) VALUES (?, ?)", (user_id, today))
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
