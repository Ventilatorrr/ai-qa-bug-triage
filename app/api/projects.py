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
            SELECT id, name, owner_id
            FROM projects
            WHERE id = ? AND owner_id = ?
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
        "name": row[1],
        "owner_id": row[2]
    }
