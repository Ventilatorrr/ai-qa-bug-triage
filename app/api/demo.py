from collections import deque
from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import logging
import os
import re
import secrets
import threading
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.auth import TOKEN_LIFETIME, PasswordWorkBusy, create_access_token, hash_password
from app.database import get_connection


router = APIRouter(tags=["Demo"])
logger = logging.getLogger(__name__)

DEMO_DATA = Path(__file__).resolve().parents[1] / "demo_data"
SEED_FILES = ("demo_ecommerce.json", "ai_qa_bug_triage.json")
# Server-owned Demo identity of each seeded project, kept after renaming.
DEMO_KINDS = {"E-Commerce Demo": "ecommerce", "AI QA Bug Triage": "history"}
TEAM_REFS = ("owner", "qa1", "qa2", "dev1", "dev2")  # Roles come from project memberships.

# Name-like four-letter aliases such as jane@example.com or noel@example.com. Measured in
# 16px Arial: "@example.com" is 111.4px and every lowercase letter except m (13.3px) and
# w (11.6px) is at most 8.9px, so omitting m and w keeps every address within the 150px
# Assignee text area (at most 147px). Two patterns give 12,800 aliases before blocking.
CONSONANTS = "bcdfghjklnprstvz"
VOWELS = "aeiou"
ALIAS_PATTERNS = ("CVCV", "CVVC")
# A small safeguard against obviously inappropriate generated words.
BLOCKED_ALIASES = frozenset({
    "boob", "caca", "coon", "culo", "dago", "dead", "dike", "gook", "hate", "homo",
    "kaka", "kike", "kill", "lube", "nazi", "nude", "paki", "pedo", "pene", "pipi",
    "poop", "puke", "puta", "puto", "rape",
})
ALIAS_BATCH = 30  # At the 5,000-account cap, fewer than 5 free in a batch has p ~ 2e-8.
ALIAS_ATTEMPTS = 5
SEEDED_FIELDS = (
    "title", "affected_version", "environment", "description", "steps_to_reproduce",
    "expected_result", "actual_result", "severity", "priority", "status", "resolution", "fix_version",
    "created_at", "updated_at",
)

# Lightweight protection for the public endpoint, without IP tracking:
# a process-wide limit on Demos started per hour and a cap on stored Demos.
DEMO_HOURLY_LIMIT = 20
# Default cap on stored Demos. The DEMO_TOTAL_LIMIT environment setting overrides it per request;
# 0 disables Try Demo. Deleting expired Demos frees capacity, and the ~12,800 generated
# addresses (five per stored Demo) make 2,000 the practical maximum.
DEMO_TOTAL_LIMIT = 1000
DEMO_TOTAL_LIMIT_MAX = 2000
DEMO_CAPACITY_MESSAGE = "The Demo is currently unavailable. Please register an account instead."
# Everything a Demo created is deleted by the first cleanup run after this age (AC-024.9).
# It outlasts any token, so a deleted Demo has no valid session and reused IDs are safe.
DEMO_RETENTION = timedelta(days=7)
assert DEMO_RETENTION > TOKEN_LIFETIME
_recent_starts = deque()
_recent_starts_lock = threading.Lock()


class DemoUnavailable(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


class DemoNotDeleted(Exception):
    """An expired Demo has unexpected relationships, so nothing of it was deleted."""


def load_seeds():
    return [json.loads((DEMO_DATA / name).read_text(encoding="utf-8")) for name in SEED_FILES]


def alias_candidates():
    """Return a batch of distinct random aliases that are allowed and always fit."""
    candidates = set()
    while len(candidates) < ALIAS_BATCH:
        pattern = secrets.choice(ALIAS_PATTERNS)
        alias = "".join(secrets.choice(VOWELS if kind == "V" else CONSONANTS) for kind in pattern)
        if alias not in BLOCKED_ALIASES:
            candidates.add(alias)
    return list(candidates)


def reserve_hourly_start():
    """Count this start toward the rolling hour, or refuse it before any work is done."""
    now = time.monotonic()
    with _recent_starts_lock:
        while _recent_starts and now - _recent_starts[0] >= 3600:
            _recent_starts.popleft()
        if len(_recent_starts) >= DEMO_HOURLY_LIMIT:
            raise DemoUnavailable(
                429, "Too many Demos have been started recently. Please try again later or register an account."
            )
        _recent_starts.append(now)
    return now


def release_hourly_start(started):
    # Failed attempts do not use up the hourly allowance.
    with _recent_starts_lock:
        if started in _recent_starts:
            _recent_starts.remove(started)


def configured_demo_limit():
    value = (os.getenv("DEMO_TOTAL_LIMIT") or "").strip()
    if not value:
        return DEMO_TOTAL_LIMIT
    if not re.fullmatch(r"[0-9]+", value) or int(value) > DEMO_TOTAL_LIMIT_MAX:
        logger.error("DEMO_TOTAL_LIMIT must be a whole number from 0 to %d; Try Demo is unavailable.",
                     DEMO_TOTAL_LIMIT_MAX)
        return 0
    return int(value)


def demo_capacity_reached(conn, limit):
    stored = conn.execute("SELECT COUNT(*) FROM demos").fetchone()[0]
    if stored < limit:
        return False
    # Operators watch for this: capacity returns as expired Demos are deleted.
    logger.warning("Try Demo refused: limit %d reached (%d stored Demos).", limit, stored)
    return True


def insert_seeded_project(conn, seed, user_ids):
    """Insert a project, its five members and its bugs directly in their final seeded state."""
    next_bug_number = max(bug["number"] for bug in seed["bugs"]) + 1
    project_id = conn.execute(
        "INSERT INTO projects (name, next_bug_number, demo_kind) VALUES (?, ?, ?)",
        (seed["project"], next_bug_number, DEMO_KINDS[seed["project"]]),
    ).lastrowid
    conn.executemany(
        "INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)",
        [(project_id, user_ids[ref], role) for ref, role in seed["team"].items()],
    )
    # Both datasets carry fixed historical timestamps, so every Demo shows the same history.
    columns = ("project_id", "bug_number", *SEEDED_FIELDS, "assignee_id", "created_by")
    conn.executemany(
        f"INSERT INTO bugs ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
        [
            (
                project_id, bug["number"], *(bug[field] for field in SEEDED_FIELDS),
                user_ids[bug["assignee"]] if bug["assignee"] else None,
                user_ids[bug["created_by"]],
            )
            for bug in seed["bugs"]
        ],
    )


def create_demo():
    """Create five normal accounts and both seeded projects atomically; return the owner's token."""
    started = reserve_hourly_start()
    try:
        seeds = load_seeds()
        limit = configured_demo_limit()
        # Refuse at capacity before any bcrypt work; the check inside the
        # transaction below remains authoritative.
        with closing(get_connection()) as conn:
            if demo_capacity_reached(conn, limit):
                raise DemoUnavailable(503, DEMO_CAPACITY_MESSAGE)
        # Random passwords are never stored or returned in plain text. Hash them before
        # the transaction so the database write lock is not held during bcrypt.
        try:
            password_hashes = {ref: hash_password(secrets.token_urlsafe(32)) for ref in TEAM_REFS}
        except PasswordWorkBusy as error:
            raise DemoUnavailable(503, str(error)) from None
        conn = get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            if demo_capacity_reached(conn, limit):
                raise DemoUnavailable(503, DEMO_CAPACITY_MESSAGE)
            # The IMMEDIATE lock serializes writers, so addresses found free stay free until commit.
            for _ in range(ALIAS_ATTEMPTS):
                candidates = [f"{alias}@example.com" for alias in alias_candidates()]
                taken = {row[0] for row in conn.execute(
                    f"SELECT email FROM users WHERE email IN ({', '.join('?' for _ in candidates)})", candidates,
                )}
                free = [email for email in candidates if email not in taken]
                if len(free) >= len(TEAM_REFS):
                    break
            else:
                raise RuntimeError("Could not generate unused Demo email addresses.")
            emails = dict(zip(TEAM_REFS, free))
            user_ids = {
                ref: conn.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hashes[ref])
                ).lastrowid
                for ref, email in emails.items()
            }
            # The server-owned record that identifies these accounts for capacity and deletion.
            demo_id = conn.execute(
                "INSERT INTO demos (created_at) VALUES (?)", (datetime.now(timezone.utc).isoformat(),)
            ).lastrowid
            conn.executemany(
                "INSERT INTO demo_accounts (user_id, demo_id) VALUES (?, ?)",
                [(user_id, demo_id) for user_id in user_ids.values()],
            )
            for seed in seeds:
                insert_seeded_project(conn, seed, user_ids)
            # Created before commit, so a token failure also rolls back the whole Demo.
            token = create_access_token(user_ids["owner"])
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()
    except BaseException:
        release_hourly_start(started)
        raise
    return token


def _placeholders(values):
    return ", ".join("?" for _ in values)


def retention_cutoff(now=None):
    return (now or datetime.now(timezone.utc)) - DEMO_RETENTION


def expired_demos(cutoff):
    """IDs and creation times of stored Demos created at or before the cutoff, oldest first."""
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT id, created_at FROM demos ORDER BY id").fetchall()
    return [(demo_id, datetime.fromisoformat(created)) for demo_id, created in rows
            if datetime.fromisoformat(created) <= cutoff]


def delete_demo(demo_id, cutoff):
    """Delete one expired Demo with its accounts, projects, bugs, memberships and AI usage, or nothing."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT created_at FROM demos WHERE id = ?", (demo_id,)).fetchone()
        # Another run may already have deleted it; the age is rechecked under the lock.
        if row is None or datetime.fromisoformat(row[0]) > cutoff:
            conn.rollback()
            return False
        accounts = [user_id for (user_id,) in conn.execute(
            "SELECT user_id FROM demo_accounts WHERE demo_id = ?", (demo_id,)
        )]
        # Every Demo records exactly its generated accounts; anything else needs a person to resolve it.
        if len(accounts) != len(TEAM_REFS):
            raise DemoNotDeleted(f"it has {len(accounts)} account records instead of {len(TEAM_REFS)}")
        # The Demo's projects are those its accounts own, including renamed and newly created ones.
        projects = [project_id for (project_id,) in conn.execute(
            f"SELECT project_id FROM project_members WHERE role = 'Project Owner' AND user_id IN ({_placeholders(accounts)})",
            accounts,
        )]
        # Delete only what belongs to this Demo. Anything else needs a person to resolve it.
        checks = (
            ("a project it owns has a member from outside the Demo",
             f"SELECT 1 FROM project_members WHERE project_id IN ({_placeholders(projects)}) "
             f"AND user_id NOT IN ({_placeholders(accounts)})", projects + accounts),
            ("one of its accounts is a member of a project outside the Demo",
             f"SELECT 1 FROM project_members WHERE user_id IN ({_placeholders(accounts)}) "
             f"AND project_id NOT IN ({_placeholders(projects)})", accounts + projects),
            ("a bug outside the Demo refers to one of its accounts",
             f"SELECT 1 FROM bugs WHERE project_id NOT IN ({_placeholders(projects)}) "
             f"AND (created_by IN ({_placeholders(accounts)}) OR assignee_id IN ({_placeholders(accounts)}))",
             projects + accounts + accounts),
        )
        for reason, sql, parameters in checks:
            if conn.execute(sql, parameters).fetchone() is not None:
                raise DemoNotDeleted(reason)
        for sql, parameters in (
            (f"DELETE FROM bugs WHERE project_id IN ({_placeholders(projects)})", projects),
            (f"DELETE FROM project_members WHERE project_id IN ({_placeholders(projects)})", projects),
            (f"DELETE FROM projects WHERE id IN ({_placeholders(projects)})", projects),
            (f"DELETE FROM ai_requests WHERE user_id IN ({_placeholders(accounts)})", accounts),
            ("DELETE FROM demo_accounts WHERE demo_id = ?", (demo_id,)),
            (f"DELETE FROM users WHERE id IN ({_placeholders(accounts)})", accounts),
            ("DELETE FROM demos WHERE id = ?", (demo_id,)),
        ):
            conn.execute(sql, parameters)
        # Startup refuses dangling references, so never commit one.
        if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise DemoNotDeleted("deleting it would leave dangling references")
        conn.commit()
        return True
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_expired_demos(now=None):
    """Delete each expired Demo in its own transaction; return the number deleted and the IDs that failed.

    A failed Demo is rolled back whole, logged as an error and retried on every later run.
    """
    cutoff = retention_cutoff(now)
    deleted, failed = 0, []
    for demo_id, created in expired_demos(cutoff):
        try:
            if delete_demo(demo_id, cutoff):
                deleted += 1
        except Exception as error:
            failed.append(demo_id)
            # IDs and times only: logs never contain account or project data.
            logger.error(
                "Expired Demo %d (created %s) was not deleted: %s. Manual resolution is needed.",
                demo_id, created.isoformat(), error if isinstance(error, DemoNotDeleted) else type(error).__name__,
            )
    return deleted, failed


@router.post("/demo", status_code=201)
def start_demo():
    try:
        token = create_demo()
    except DemoUnavailable as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from None
    except Exception:
        logger.exception("Demo creation failed; the transaction was rolled back.")
        raise HTTPException(status_code=500, detail="The Demo could not be created. Please try again.") from None
    return {
        "access_token": token,
        "token_type": "bearer"
    }
