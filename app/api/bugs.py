from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException

from app.api.auth import get_current_user_id
from app.database import get_connection
from app.schemas import BugCreate, BugStatusUpdate, BugUpdate


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
            if membership[0] not in ["Project Owner", "QA Analyst", "Developer"]:
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
                resolution,
                created_by,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                None,
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
        "resolution": None,
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
                resolution,
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
        "resolution": row[6],
        "assignee_id": row[7],
        "affected_version": row[8],
        "fix_version": row[9],
        "description": row[10],
        "steps_to_reproduce": row[11],
        "expected_result": row[12],
        "actual_result": row[13],
        "created_by": row[14],
        "created_at": row[15],
        "updated_at": row[16]
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
            SELECT id, status, assignee_id
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

        current_status = existing_bug[1]

        updates = bug.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(
                status_code=422,
                detail="No bug information provided."
            )

        if "assignee_id" in updates:
            if current_status == "Closed":
                raise HTTPException(
                    status_code=422,
                    detail="Closed bugs cannot be reassigned."
                )

            if membership[0] not in ["Project Owner", "QA Analyst", "Developer"]:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to assign bugs."
                )

            assignee_id = updates["assignee_id"]

            if current_status == "Open" and assignee_id is None:
                raise HTTPException(
                    status_code=422,
                    detail="Open bugs must have an assignee."
                )

            if current_status == "Development":
                if assignee_id is None:
                    raise HTTPException(
                        status_code=422,
                        detail="Development bugs must have a Developer assigned."
                    )

            if current_status == "Testing":
                if assignee_id is None:
                    raise HTTPException(
                        status_code=422,
                        detail="Testing bugs must have a QA Analyst assigned."
                    )

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

                if current_status == "Development" and assignee[0] != "Developer":
                    raise HTTPException(
                        status_code=422,
                        detail="Development bugs must have a Developer assigned."
                    )

                if current_status == "Testing" and assignee[0] != "QA Analyst":
                    raise HTTPException(
                        status_code=422,
                        detail="Testing bugs must have a QA Analyst assigned."
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
                resolution,
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
        "resolution": row[6],
        "assignee_id": row[7],
        "affected_version": row[8],
        "fix_version": row[9],
        "description": row[10],
        "steps_to_reproduce": row[11],
        "expected_result": row[12],
        "actual_result": row[13],
        "created_by": row[14],
        "created_at": row[15],
        "updated_at": row[16]
    }


@router.patch("/projects/{project_id}/bugs/{bug_id}/status")
def update_bug_status(
    project_id: int,
    bug_id: int,
    status_update: BugStatusUpdate,
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

        bug = conn.execute(
            """
            SELECT
                id,
                status,
                resolution,
                assignee_id
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

        current_status = bug[1]
        current_resolution = bug[2]
        current_assignee_id = bug[3]

        requested_status = status_update.status
        requested_assignee_id = status_update.assignee_id
        testing_outcome = status_update.testing_outcome
        requested_resolution = status_update.resolution

        if current_status == "Closed":
            raise HTTPException(
                status_code=422,
                detail="Closed bugs cannot be moved to another status."
            )

        if current_status == "Triage":
            if requested_status != "Open":
                raise HTTPException(
                    status_code=422,
                    detail="Invalid bug status transition."
                )

            if membership[0] not in ["Project Owner", "QA Analyst"]:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to move bugs from Triage to Open."
                )

            assignee_id = current_assignee_id

            if assignee_id is None:
                raise HTTPException(
                    status_code=422,
                    detail="Bug must have a QA Analyst or Developer assigned before it can be moved to Open."
                )

            assignee = conn.execute(
                """
                SELECT role
                FROM project_members
                WHERE project_id = ?
                AND user_id = ?
                """,
                (project_id, assignee_id)
            ).fetchone()

            if assignee is None or assignee[0] not in ["QA Analyst", "Developer"]:
                raise HTTPException(
                    status_code=422,
                    detail="Bug must have a QA Analyst or Developer assigned before it can be moved to Open."
                )

            if requested_assignee_id is not None or testing_outcome is not None or requested_resolution is not None:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid status update data."
                )

            new_assignee_id = current_assignee_id
            new_resolution = current_resolution

        elif current_status == "Open":
            if requested_status != "Development":
                raise HTTPException(
                    status_code=422,
                    detail="Invalid bug status transition."
                )

            if membership[0] != "Developer" or current_assignee_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the assigned Developer can move a bug from Open to Development."
                )

            assignee = conn.execute(
                """
                SELECT role
                FROM project_members
                WHERE project_id = ?
                AND user_id = ?
                """,
                (project_id, current_assignee_id)
            ).fetchone()

            if assignee is None or assignee[0] != "Developer":
                raise HTTPException(
                    status_code=422,
                    detail="A Developer must be assigned before the bug can be moved to Development."
                )

            if requested_assignee_id is not None or testing_outcome is not None or requested_resolution is not None:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid status update data."
                )

            new_assignee_id = current_assignee_id
            new_resolution = current_resolution

        elif current_status == "Development":
            if requested_status == "Testing":
                if membership[0] != "Developer" or current_assignee_id != user_id:
                    raise HTTPException(
                        status_code=403,
                        detail="Only the assigned Developer can move a bug from Development to Testing."
                    )

                if requested_assignee_id is None:
                    raise HTTPException(
                        status_code=422,
                        detail="A QA Analyst must be selected before the bug can be moved to Testing."
                    )

                qa = conn.execute(
                    """
                    SELECT role
                    FROM project_members
                    WHERE project_id = ?
                    AND user_id = ?
                    """,
                    (project_id, requested_assignee_id)
                ).fetchone()

                if qa is None or qa[0] != "QA Analyst":
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid QA Analyst assignee."
                    )

                if testing_outcome is not None or requested_resolution is not None:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid status update data."
                    )

                new_assignee_id = requested_assignee_id
                new_resolution = current_resolution

            elif requested_status == "Closed":
                if membership[0] == "Developer":
                    if current_assignee_id != user_id:
                        raise HTTPException(
                            status_code=403,
                            detail="Only the assigned Developer can close this bug."
                        )
                elif membership[0] != "Project Owner":
                    raise HTTPException(
                        status_code=403,
                        detail="You are not authorized to close this bug."
                    )

                if requested_resolution is None:
                    raise HTTPException(
                        status_code=422,
                        detail="Resolution is required when closing a bug without fixing it."
                    )

                if requested_resolution not in ["Won't Fix", "Duplicate", "Not a Bug"]:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid bug resolution."
                    )

                if requested_assignee_id is not None or testing_outcome is not None:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid status update data."
                    )

                new_assignee_id = current_assignee_id
                new_resolution = requested_resolution

            else:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid bug status transition."
                )

        elif current_status == "Testing":
            if requested_status != "Closed" and requested_status != "Development":
                raise HTTPException(
                    status_code=422,
                    detail="Invalid bug status transition."
                )

            if membership[0] != "QA Analyst" or current_assignee_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the assigned QA Analyst can record the testing outcome."
                )

            if testing_outcome is None:
                raise HTTPException(
                    status_code=422,
                    detail="Testing outcome is required."
                )

            if testing_outcome == "Passed":
                if requested_status != "Closed":
                    raise HTTPException(
                        status_code=422,
                        detail="A passed bug must be closed."
                    )

                if requested_assignee_id is not None or requested_resolution is not None:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid status update data."
                    )

                new_assignee_id = current_assignee_id
                new_resolution = "Fixed"

            elif testing_outcome == "Failed":
                if requested_status != "Development":
                    raise HTTPException(
                        status_code=422,
                        detail="A failed bug must return to Development."
                    )

                if requested_assignee_id is None:
                    raise HTTPException(
                        status_code=422,
                        detail="A Developer must be assigned when testing fails."
                    )

                developer = conn.execute(
                    """
                    SELECT role
                    FROM project_members
                    WHERE project_id = ?
                    AND user_id = ?
                    """,
                    (project_id, requested_assignee_id)
                ).fetchone()

                if developer is None or developer[0] != "Developer":
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid Developer assignee."
                    )

                if requested_resolution is not None:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid bug resolution."
                    )

                new_assignee_id = requested_assignee_id
                new_resolution = None

            else:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid testing outcome."
                )

        else:
            raise HTTPException(
                status_code=422,
                detail="Invalid bug status transition."
            )

        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """
            UPDATE bugs
            SET
                status = ?,
                assignee_id = ?,
                resolution = ?,
                updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (
                requested_status,
                new_assignee_id,
                new_resolution,
                now,
                bug_id,
                project_id
            )
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
                resolution,
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
        "resolution": row[6],
        "assignee_id": row[7],
        "affected_version": row[8],
        "fix_version": row[9],
        "description": row[10],
        "steps_to_reproduce": row[11],
        "expected_result": row[12],
        "actual_result": row[13],
        "created_by": row[14],
        "created_at": row[15],
        "updated_at": row[16]
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

