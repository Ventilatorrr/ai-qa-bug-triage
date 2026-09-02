from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException

from app.api.auth import get_current_user_id
from app.database import get_connection
from app.schemas import BugCreate


router = APIRouter(tags=["Bugs"])


@router.post("/projects/{project_id}/bugs", status_code=201)
def create_bug(
    project_id: int,
    bug: BugCreate,
    authorization: str | None = Header(default=None)
):
    user_id = get_current_user_id(authorization)

    conn = get_connection()

    try:
        membership = conn.execute(
            """
            SELECT role
            FROM project_members
            WHERE project_id = ? AND user_id = ?
            """,
            (project_id, user_id)
        ).fetchone()

        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        assignee_id = bug.assignee_id

        if assignee_id is not None:
            if membership[0] not in ["Project Owner", "QA Analyst"]:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to assign bugs."
                )

            assignee = conn.execute(
                """
                SELECT user_id
                FROM project_members
                WHERE project_id = ?
                AND user_id = ?
                AND role IN ('QA Analyst', 'Developer')
                """,
                (project_id, assignee_id)
            ).fetchone()

            if assignee is None:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid bug assignee."
                )

        now = datetime.now(timezone.utc).isoformat()

        cursor = conn.execute(
            """
            INSERT INTO bugs (
                project_id,
                title,
                affected_version,
                description,
                steps_to_reproduce,
                expected_result,
                actual_result,
                severity,
                priority,
                assignee_id,
                fix_version,
                status,
                created_by,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                bug.title.strip(),
                bug.affected_version,
                bug.description,
                bug.steps_to_reproduce,
                bug.expected_result,
                bug.actual_result,
                bug.severity,
                bug.priority,
                assignee_id,
                bug.fix_version,
                "Triage",
                user_id,
                now,
                now
            )
        )

        bug_id = cursor.lastrowid

        conn.commit()

    finally:
        conn.close()

    return {
        "id": bug_id,
        "project_id": project_id,
        "title": bug.title.strip(),
        "affected_version": bug.affected_version,
        "description": bug.description,
        "steps_to_reproduce": bug.steps_to_reproduce,
        "expected_result": bug.expected_result,
        "actual_result": bug.actual_result,
        "severity": bug.severity,
        "priority": bug.priority,
        "assignee_id": assignee_id,
        "fix_version": bug.fix_version,
        "status": "Triage",
        "created_by": user_id,
        "created_at": now,
        "updated_at": now
    }
    