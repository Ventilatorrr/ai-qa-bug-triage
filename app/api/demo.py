import json
import logging
import secrets
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.auth import create_access_token, hash_password
from app.database import get_connection


router = APIRouter(tags=["Demo"])
logger = logging.getLogger(__name__)

DEMO_DATA = Path(__file__).resolve().parents[1] / "demo_data"
SEED_FILES = ("demo_ecommerce.json", "ai_qa_bug_triage.json")
# Short role prefixes keep generated addresses readable in member and bug tables.
EMAIL_PREFIXES = {"owner": "o", "qa1": "q1", "qa2": "q2", "dev1": "d1", "dev2": "d2"}
SUFFIX_ALPHABET = string.ascii_lowercase + string.digits
SUFFIX_LENGTH = 5
SUFFIX_ATTEMPTS = 10
SEEDED_FIELDS = (
    "title", "affected_version", "environment", "description", "steps_to_reproduce",
    "expected_result", "actual_result", "severity", "priority", "status", "resolution", "fix_version",
)


def load_seeds():
    return [json.loads((DEMO_DATA / name).read_text(encoding="utf-8")) for name in SEED_FILES]


def new_suffix():
    return "".join(secrets.choice(SUFFIX_ALPHABET) for _ in range(SUFFIX_LENGTH))


def bug_timestamps(bug, now):
    if "created_at" in bug:
        # Genuine snapshot: keep the original timestamps.
        return bug["created_at"], bug["updated_at"]
    # Fictional dataset: dates relative to Demo creation.
    return (
        (now - timedelta(days=bug["created_days_ago"])).isoformat(),
        (now - timedelta(days=bug["updated_days_ago"])).isoformat(),
    )


def insert_seeded_project(conn, seed, user_ids, now):
    """Insert a project, its five members and its bugs directly in their final seeded state."""
    next_bug_number = max(bug["number"] for bug in seed["bugs"]) + 1
    project_id = conn.execute(
        "INSERT INTO projects (name, next_bug_number) VALUES (?, ?)",
        (seed["project"], next_bug_number),
    ).lastrowid
    conn.executemany(
        "INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)",
        [(project_id, user_ids[ref], role) for ref, role in seed["team"].items()],
    )
    columns = ("project_id", "bug_number", *SEEDED_FIELDS, "assignee_id", "created_by", "created_at", "updated_at")
    conn.executemany(
        f"INSERT INTO bugs ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
        [
            (
                project_id, bug["number"], *(bug[field] for field in SEEDED_FIELDS),
                user_ids[bug["assignee"]] if bug["assignee"] else None,
                user_ids[bug["created_by"]], *bug_timestamps(bug, now),
            )
            for bug in seed["bugs"]
        ],
    )


def create_demo():
    """Create five normal accounts and both seeded projects atomically; return the owner's token."""
    seeds = load_seeds()
    # Random passwords are never stored or returned in plain text. Hash them before
    # the transaction so the database write lock is not held during bcrypt.
    password_hashes = {ref: hash_password(secrets.token_urlsafe(32)) for ref in EMAIL_PREFIXES}
    now = datetime.now(timezone.utc)
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        # The IMMEDIATE lock serializes writers, so an unused suffix stays unused until commit.
        for _ in range(SUFFIX_ATTEMPTS):
            suffix = new_suffix()
            emails = {ref: f"{prefix}{suffix}@example.com" for ref, prefix in EMAIL_PREFIXES.items()}
            taken = conn.execute(
                f"SELECT 1 FROM users WHERE email IN ({', '.join('?' for _ in emails)})",
                tuple(emails.values()),
            ).fetchone()
            if taken is None:
                break
        else:
            raise RuntimeError("Could not generate unused Demo email addresses.")
        user_ids = {
            ref: conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hashes[ref])
            ).lastrowid
            for ref, email in emails.items()
        }
        for seed in seeds:
            insert_seeded_project(conn, seed, user_ids, now)
        # Created before commit, so a token failure also rolls back the whole Demo.
        token = create_access_token(user_ids["owner"])
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
    return token


@router.post("/demo", status_code=201)
def start_demo():
    try:
        token = create_demo()
    except Exception:
        logger.exception("Demo creation failed; the transaction was rolled back.")
        raise HTTPException(status_code=500, detail="The Demo could not be created. Please try again.") from None
    return {
        "access_token": token,
        "token_type": "bearer"
    }
