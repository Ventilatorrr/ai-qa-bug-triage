import sqlite3

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

    owner_id = payload["user_id"]
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
            INSERT INTO projects (name, owner_id)
            VALUES (?, ?)
            """,
            (project_name, owner_id)
        )

        conn.commit()

        project_id = cursor.lastrowid

    finally:
        conn.close()

    return {
        "id": project_id,
        "name": project_name,
        "owner_id": owner_id
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
            SELECT id, name, owner_id
            FROM projects
            WHERE owner_id = ?
            """,
            (user_id,)
        ).fetchall()

    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "owner_id": row[2]
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
            SELECT p.id, p.name, p.owner_id
            FROM projects p
            LEFT JOIN project_members pm
                ON p.id = pm.project_id
                AND pm.user_id = ?
            WHERE p.id = ?
            AND (p.owner_id = ? OR pm.user_id IS NOT NULL)
            """,
            (user_id, project_id, user_id)
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
        "name": row[1],
        "owner_id": row[2]
    }


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
            SELECT id, name, owner_id
            FROM projects
            WHERE id = ? AND owner_id = ?
            """,
            (project_id, user_id)
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
            WHERE id = ? AND owner_id = ?
            """,
            (project_name, project_id, user_id)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "id": project_id,
        "name": project_name,
        "owner_id": user_id
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
        row = conn.execute(
            """
            SELECT id
            FROM projects
            WHERE id = ? AND owner_id = ?
            """,
            (project_id, user_id)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
            )

        conn.execute(
            """
            DELETE FROM projects
            WHERE id = ? AND owner_id = ?
            """,
            (project_id, user_id)
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

    member_email = member.get("email")

    if not member_email:
        raise HTTPException(
            status_code=422,
            detail="Member email is required."
        )

    conn = get_connection()

    try:
        project = conn.execute(
            """
            SELECT id
            FROM projects
            WHERE id = ? AND owner_id = ?
            """,
            (project_id, user_id)
        ).fetchone()

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found."
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
            INSERT INTO project_members (project_id, user_id)
            VALUES (?, ?)
            """,
            (project_id, member_user_id)
        )

        conn.commit()

    finally:
        conn.close()

    return {
        "project_id": project_id,
        "user_id": member_user_id,
        "email": member_user[1]
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
            SELECT id
            FROM projects
            WHERE id = ? AND owner_id = ?
            """,
            (project_id, user_id)
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
