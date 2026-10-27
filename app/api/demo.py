from collections import deque
import json
import logging
import secrets
import threading
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.auth import create_access_token, hash_password
from app.database import get_connection


router = APIRouter(tags=["Demo"])
logger = logging.getLogger(__name__)

DEMO_DATA = Path(__file__).resolve().parents[1] / "demo_data"
SEED_FILES = ("demo_ecommerce.json", "ai_qa_bug_triage.json")
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

# Lightweight protection for the public endpoint, without IP tracking or new tables:
# a process-wide limit on Demos started per hour and a cap on stored Demo environments.
DEMO_HOURLY_LIMIT = 20
DEMO_TOTAL_LIMIT = 1000
# Stored Demos are counted conservatively as five accounts each among all four-letter
# @example.com addresses. Ordinary accounts with such an address also count toward the cap.
DEMO_ACCOUNT_EMAILS = "[a-z][a-z][a-z][a-z]@example.com"  # Case-sensitive SQL GLOB pattern.
_recent_starts = deque()
_recent_starts_lock = threading.Lock()


class DemoUnavailable(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


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


def insert_seeded_project(conn, seed, user_ids):
    """Insert a project, its five members and its bugs directly in their final seeded state."""
    next_bug_number = max(bug["number"] for bug in seed["bugs"]) + 1
    project_id = conn.execute(
        "INSERT INTO projects (name, next_bug_number, demo_kind) VALUES (?, ?, ?)",
        (seed["project"], next_bug_number, "history" if seed["project"] == "AI QA Bug Triage" else None),
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
        # Random passwords are never stored or returned in plain text. Hash them before
        # the transaction so the database write lock is not held during bcrypt.
        password_hashes = {ref: hash_password(secrets.token_urlsafe(32)) for ref in TEAM_REFS}
        conn = get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            accounts = conn.execute("SELECT COUNT(*) FROM users WHERE email GLOB ?", (DEMO_ACCOUNT_EMAILS,)).fetchone()[0]
            if accounts >= DEMO_TOTAL_LIMIT * len(TEAM_REFS):
                raise DemoUnavailable(503, "The Demo is currently unavailable. Please register an account instead.")
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
