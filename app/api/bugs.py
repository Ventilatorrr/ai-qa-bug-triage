from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException

from app.api.auth import get_current_user_id
from app.database import get_connection
from app.schemas import BugCreate, BugUpdate


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


@router.get("/projects/{project_id}/bugs")
def get_bugs(
    project_id: int,
    authorization: str | None = Header(default=None)
):
    user_id = get_current_user_id(authorization)

    conn = get_connection()

    try:
        membership = conn.execute(
            """
            SELECT 1
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

        rows = conn.execute(
            """
            SELECT
                b.id,
                b.title,
                b.severity,
                b.priority,
                b.status,
                b.assignee_id,
                b.updated_at
            FROM bugs b
            WHERE b.project_id = ?
            ORDER BY b.updated_at DESC
            """,
            (project_id,)
        ).fetchall()

    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "severity": row[2],
            "priority": row[3],
            "status": row[4],
            "assignee_id": row[5],
            "updated_at": row[6]
        }
        for row in rows
    ]


@router.get("/projects/{project_id}/bugs/{bug_id}")
def get_bug(
    project_id: int,
    bug_id: int,
    authorization: str | None = Header(default=None)
):
    user_id = get_current_user_id(authorization)

    conn = get_connection()

    try:
        membership = conn.execute(
            """
            SELECT 1
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

        row = conn.execute(
            """
            SELECT
                id,
                project_id,
                title,
                severity,
                priority,
                status,
                assignee_id,
                affected_version,
                fix_version,
                description,
                steps_to_reproduce,
                expected_result,
                actual_result,
                created_by,
                created_at,
                updated_at
            FROM bugs
            WHERE id = ? AND project_id = ?
            """,
            (bug_id, project_id)
        ).fetchone()

    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Bug not found."
        )

    return {
        "id": row[0],
        "project_id": row[1],
        "title": row[2],
        "severity": row[3],
        "priority": row[4],
        "status": row[5],
        "assignee_id": row[6],
        "affected_version": row[7],
        "fix_version": row[8],
        "description": row[9],
        "steps_to_reproduce": row[10],
        "expected_result": row[11],
        "actual_result": row[12],
        "created_by": row[13],
        "created_at": row[14],
        "updated_at": row[15]
    }

    
@router.patch("/projects/{project_id}/bugs/{bug_id}")
def update_bug(
    project_id: int,
    bug_id: int,
    bug: BugUpdate,
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

        existing_bug = conn.execute(
            """
            SELECT id
            FROM bugs
            WHERE id = ? AND project_id = ?
            """,
            (bug_id, project_id)
        ).fetchone()

        if existing_bug is None:
            raise HTTPException(
                status_code=404,
                detail="Bug not found."
            )

        updates = bug.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(
                status_code=422,
                detail="No bug information provided."
            )

        if "assignee_id" in updates:
            if membership[0] not in ["Project Owner", "QA Analyst"]:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to assign bugs."
                )

            assignee_id = updates["assignee_id"]

            if assignee_id is not None:
                assignee = conn.execute(
                    """
                    SELECT role
                    FROM project_members
                    WHERE project_id = ?
                    AND user_id = ?
                    """,
                    (project_id, assignee_id)
                ).fetchone()

                if assignee is None:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid bug assignee."
                    )

                if assignee[0] not in ["QA Analyst", "Developer"]:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid bug assignee."
                    )

        fields = []
        values = []

        for field, value in updates.items():
            if field == "title":
                value = value.strip()

            fields.append(f"{field} = ?")
            values.append(value)

        now = datetime.now(timezone.utc).isoformat()

        fields.append("updated_at = ?")
        values.append(now)

        values.extend([bug_id, project_id])

        conn.execute(
            f"""
            UPDATE bugs
            SET {", ".join(fields)}
            WHERE id = ? AND project_id = ?
            """,
            values
        )

        conn.commit()

        row = conn.execute(
            """
            SELECT
                id,
                project_id,
                title,
                severity,
                priority,
                status,
                assignee_id,
                affected_version,
                fix_version,
                description,
                steps_to_reproduce,
                expected_result,
                actual_result,
                created_by,
                created_at,
                updated_at
            FROM bugs
            WHERE id = ? AND project_id = ?
            """,
            (bug_id, project_id)
        ).fetchone()

    finally:
        conn.close()

    return {
        "id": row[0],
        "project_id": row[1],
        "title": row[2],
        "severity": row[3],
        "priority": row[4],
        "status": row[5],
        "assignee_id": row[6],
        "affected_version": row[7],
        "fix_version": row[8],
        "description": row[9],
        "steps_to_reproduce": row[10],
        "expected_result": row[11],
        "actual_result": row[12],
        "created_by": row[13],
        "created_at": row[14],
        "updated_at": row[15]
    }


@router.delete("/projects/{project_id}/bugs/{bug_id}", status_code=204)
def delete_bug(
    project_id: int,
    bug_id: int,
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

        if membership[0] not in ["Project Owner", "QA Analyst"]:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to delete bugs."
            )

        bug = conn.execute(
            """
            SELECT id
            FROM bugs
            WHERE id = ? AND project_id = ?
            """,
            (bug_id, project_id)
        ).fetchone()

        if bug is None:
            raise HTTPException(
                status_code=404,
                detail="Bug not found."
            )

        conn.execute(
            """
            DELETE FROM bugs
            WHERE id = ? AND project_id = ?
            """,
            (bug_id, project_id)
        )

        conn.commit()

    finally:
        conn.close()

