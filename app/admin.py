"""Operator commands, run in Render Shell on the running service (docs/release-runbook.md).

    python -m app.admin delete-account EMAIL            dry run: shows what would change
    python -m app.admin delete-account EMAIL --confirm  deletes; requires READ_ONLY_MODE=1
    python -m app.admin status                          stored Demos past the retention period
    python -m app.admin run-retention                   runs the hourly cleanup now
"""

import argparse
from datetime import datetime, timezone
import os
import secrets
import sys

from pydantic import ValidationError

from app import ai_usage, database
from app.api import demo
from app.api.auth import hash_password
from app.api.projects import EMAIL_ADAPTER
from app.middleware import read_only_mode


class AdminError(Exception):
    pass


def open_database():
    """Connect only to an existing database at the current schema version; never create one."""
    path = database.DATABASE_NAME
    print(f"Database: {os.path.abspath(path)}")
    if not os.path.isfile(path):
        raise AdminError("The database file does not exist.")
    conn = database.get_connection()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version != database.SCHEMA_VERSION:
        conn.close()
        raise AdminError(f"Expected database schema version {database.SCHEMA_VERSION}, found {version}.")
    return conn


def delete_account(email, confirm):
    """Delete an ordinary account on a verified request (AC-026.1–AC-026.3).

    Projects it owns are deleted with their reports and memberships. Elsewhere its memberships
    end and its assignments are cleared; reports it created there are kept, unattributed.
    The row stays as a placeholder without email or password, so its ID is never reused.
    """
    try:
        email = EMAIL_ADAPTER.validate_python(email)
    except ValidationError:
        raise AdminError("Not a valid email address.") from None
    # Read-only mode means no request can write while the account is deleted.
    if confirm and not read_only_mode():
        raise AdminError("Set READ_ONLY_MODE=1 and restart the service before deleting an account.")
    # Hashed before taking the write lock; the secret is discarded.
    placeholder_hash = hash_password(secrets.token_urlsafe(32)) if confirm else None
    conn = open_database()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT id FROM users WHERE email = ? AND deleted_at IS NULL", (email,)).fetchone()
        if row is None:
            raise AdminError("No active account has this email address.")
        user_id = row[0]
        if conn.execute("SELECT 1 FROM demo_accounts WHERE user_id = ?", (user_id,)).fetchone():
            raise AdminError("This is a Demo account. Demos are deleted automatically after 7 days.")
        owned = conn.execute(
            """
            SELECT p.id, p.name,
                (SELECT COUNT(*) FROM project_members m WHERE m.project_id = p.id),
                (SELECT COUNT(*) FROM bugs b WHERE b.project_id = p.id)
            FROM projects p
            JOIN project_members pm ON pm.project_id = p.id
            WHERE pm.user_id = ? AND pm.role = 'Project Owner'
            ORDER BY p.id
            """,
            (user_id,)
        ).fetchall()
        owned_ids = [project[0] for project in owned]
        placeholders = ", ".join("?" for _ in owned_ids)
        other_projects = conn.execute(
            f"SELECT COUNT(*) FROM project_members WHERE user_id = ? AND project_id NOT IN ({placeholders})",
            (user_id, *owned_ids)
        ).fetchone()[0]
        assigned, authored = conn.execute(
            f"""
            SELECT COALESCE(SUM(assignee_id = ?), 0), COALESCE(SUM(created_by = ?), 0)
            FROM bugs WHERE project_id NOT IN ({placeholders})
            """,
            (user_id, user_id, *owned_ids)
        ).fetchone()
        usage = conn.execute("SELECT COUNT(*) FROM ai_requests WHERE user_id = ?", (user_id,)).fetchone()[0]

        print(f"Account {user_id} <{email}>")
        print(f"Owned projects to delete with all their reports and memberships: {len(owned)}")
        for project_id, name, members, bugs in owned:
            print(f"  - project {project_id} {name!r}: {members} members, {bugs} reports")
        print(f"Memberships to end in other projects: {other_projects}")
        print(f"Assignments to clear in other projects: {assigned}")
        print(f"Reports created in other projects, kept without attribution: {authored}")
        print(f"AI usage records to delete: {usage}")
        if not confirm:
            conn.rollback()
            print("Dry run: nothing was changed. Re-run with --confirm to delete the account.")
            return

        now = datetime.now(timezone.utc).isoformat()
        for sql, parameters in (
            (f"DELETE FROM bugs WHERE project_id IN ({placeholders})", owned_ids),
            (f"DELETE FROM project_members WHERE project_id IN ({placeholders})", owned_ids),
            (f"DELETE FROM projects WHERE id IN ({placeholders})", owned_ids),
            # As Remove Member does: unassigned bugs keep everything except Last Updated.
            ("UPDATE bugs SET assignee_id = NULL, updated_at = ? WHERE assignee_id = ?", (now, user_id)),
            ("DELETE FROM project_members WHERE user_id = ?", (user_id,)),
            ("DELETE FROM ai_requests WHERE user_id = ?", (user_id,)),
            (
                "UPDATE users SET email = ?, password_hash = ?, deleted_at = ? WHERE id = ?",
                (f"deleted-{user_id}@deleted.invalid", placeholder_hash, now, user_id),
            ),
        ):
            conn.execute(sql, parameters)
        # Startup refuses dangling references, so never commit one.
        if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise AdminError("Deleting the account would leave dangling references; nothing was changed.")
        conn.commit()
        print(f"Account {user_id} deleted. Turn READ_ONLY_MODE off again.")
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def status():
    open_database().close()
    cutoff = demo.retention_cutoff()
    expired = demo.expired_demos(cutoff)
    for demo_id, created in expired:
        hours = (cutoff - created).total_seconds() / 3600
        print(f"Demo {demo_id}, created {created.isoformat()}, is {hours:.1f} hours past the retention period.")
    if expired:
        print("Cleanup runs hourly: a Demo more than about 2 hours past was not deleted. Check the error log.")
    else:
        print("No stored Demo is past the retention period.")


def run_retention_now():
    open_database().close()
    deleted, failed = demo.delete_expired_demos()
    usage = ai_usage.delete_old_ai_usage()
    print(f"Deleted {deleted} expired Demos and {usage} earlier-day AI usage records.")
    if failed:
        raise AdminError(f"Not deleted (see the error log): Demo {', '.join(map(str, failed))}.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m app.admin", description="AI QA Bug Triage operator commands.")
    commands = parser.add_subparsers(dest="command", required=True)
    delete = commands.add_parser("delete-account", help="Delete an ordinary account on a verified request.")
    delete.add_argument("email")
    delete.add_argument("--confirm", action="store_true", help="Delete; without it, only show what would change.")
    commands.add_parser("status", help="List stored Demos past the retention period.")
    commands.add_parser("run-retention", help="Run the hourly cleanup now.")
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "delete-account":
            delete_account(arguments.email, arguments.confirm)
        elif arguments.command == "status":
            status()
        else:
            run_retention_now()
    except AdminError as error:
        print(f"Stopped: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
