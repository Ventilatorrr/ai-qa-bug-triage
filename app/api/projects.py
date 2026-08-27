from fastapi import APIRouter, HTTPException, Header

from app.database import get_connection
from app.api.auth import verify_access_token


router = APIRouter(tags=["Projects"])


@router.post("/projects", status_code=201)
def create_project(
    project: dict,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    project_name = project.get("name")

    if not project_name:
        raise HTTPException(
            status_code=422,
            detail="Project name is required."
        )

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO projects (name)
            VALUES (?)
            """,
            (project_name,)
        )

        project_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO project_members (project_id, user_id, role)
            VALUES (?, ?, ?)
            """,
            (project_id, user_id, "Project Owner")
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "id": project_id,
        "name": project_name
    }


@router.get("/projects")
def get_projects(
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT p.id, p.name
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE pm.user_id = ?
            """,
            (user_id,)
        ).fetchall()

    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in rows
    ]


@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT p.id, p.name
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE p.id = ?
            AND pm.user_id = ?
            """,
            (project_id, user_id)
        ).fetchone()

    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    return {
        "id": row[0],
        "name": row[1]
    }

@router.get("/projects/{project_id}/members")
def get_project_members(
    project_id: int,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        project_member = conn.execute(
            """
            SELECT 1
            FROM project_members
            WHERE project_id = ? AND user_id = ?
            """,
            (project_id, user_id)
        ).fetchone()

        if project_member is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        rows = conn.execute(
            """
            SELECT pm.user_id, u.email, pm.role
            FROM project_members pm
            JOIN users u
                ON pm.user_id = u.id
            WHERE pm.project_id = ?
            ORDER BY pm.user_id
            """,
            (project_id,)
        ).fetchall()

    finally:
        conn.close()

    return [
        {
            "user_id": row[0],
            "email": row[1],
            "role": row[2]
        }
        for row in rows
    ]

    
@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    project: dict,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    project_name = project.get("name")

    if not project_name:
        raise HTTPException(
            status_code=422,
            detail="Project name is required."
        )

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT p.id
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE p.id = ?
            AND pm.user_id = ?
            AND pm.role = ?
            """,
            (project_id, user_id, "Project Owner")
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        conn.execute(
            """
            UPDATE projects
            SET name = ?
            WHERE id = ?
            """,
            (project_name, project_id)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "id": project_id,
        "name": project_name
    }


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        project = conn.execute(
            """
            SELECT p.id
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE p.id = ?
            AND pm.user_id = ?
            AND pm.role = ?
            """,
            (project_id, user_id, "Project Owner")
        ).fetchone()

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        conn.execute(
            """
            DELETE FROM project_members
            WHERE project_id = ?
            """,
            (project_id,)
        )

        conn.execute(
            """
            DELETE FROM projects
            WHERE id = ?
            """,
            (project_id,)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "message": "Project deleted successfully."
    }


@router.post("/projects/{project_id}/members", status_code=201)
def add_project_member(
    project_id: int,
    member: dict,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        project = conn.execute(
            """
            SELECT p.id
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE p.id = ?
            AND pm.user_id = ?
            AND pm.role = ?
            """,
            (project_id, user_id, "Project Owner")
        ).fetchone()

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        member_email = member.get("email")
        member_role = member.get("role")

        if not member_email:
            raise HTTPException(
                status_code=422,
                detail="Member email is required."
            )

        if not member_role:
            raise HTTPException(
                status_code=422,
                detail="Member role is required."
            )

        if member_role not in ["QA Analyst", "Developer"]:
            raise HTTPException(
                status_code=422,
                detail="Invalid project role."
            )

        member_user = conn.execute(
            """
            SELECT id, email
            FROM users
            WHERE email = ?
            """,
            (member_email,)
        ).fetchone()

        if member_user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        member_user_id = member_user[0]

        existing_member = conn.execute(
            """
            SELECT 1
            FROM project_members
            WHERE project_id = ? AND user_id = ?
            """,
            (project_id, member_user_id)
        ).fetchone()

        if existing_member is not None:
            raise HTTPException(
                status_code=409,
                detail="This user is already a member of this project."
            )

        conn.execute(
            """
            INSERT INTO project_members (project_id, user_id, role)
            VALUES (?, ?, ?)
            """,
            (project_id, member_user_id, member_role)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "project_id": project_id,
        "user_id": member_user_id,
        "email": member_user[1],
        "role": member_role
    }


@router.delete("/projects/{project_id}/members/{member_user_id}")
def remove_project_member(
    project_id: int,
    member_user_id: int,
    authorization: str | None = Header(default=None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme."
        )

    token = authorization.removeprefix("Bearer ")
    payload = verify_access_token(token)
    user_id = payload["user_id"]

    conn = get_connection()

    try:
        project = conn.execute(
            """
            SELECT p.id
            FROM projects p
            JOIN project_members pm
                ON p.id = pm.project_id
            WHERE p.id = ?
            AND pm.user_id = ?
            AND pm.role = ?
            """,
            (project_id, user_id, "Project Owner")
        ).fetchone()

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        member = conn.execute(
            """
            SELECT 1
            FROM project_members
            WHERE project_id = ? AND user_id = ?
            """,
            (project_id, member_user_id)
        ).fetchone()

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="Project member not found."
            )

        conn.execute(
            """
            DELETE FROM project_members
            WHERE project_id = ? AND user_id = ?
            """,
            (project_id, member_user_id)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "message": "Project member removed successfully."
    }
