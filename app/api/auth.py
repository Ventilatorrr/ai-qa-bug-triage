import sqlite3

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from fastapi import APIRouter, HTTPException, Header

from app.database import get_connection
from app.schemas import UserCreate, UserLogin


router = APIRouter(tags=["Authentication"])

SECRET_KEY = "dev-secret-key-for-local-testing-only"
ALGORITHM = "HS256"


def create_access_token(user_id):
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "user_id": user_id,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_access_token(token):
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )


def get_current_user_id(authorization: str | None) -> int:
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

    return payload["user_id"]


@router.post("/register", status_code=201)
def register(user: UserCreate):
    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
            """,
            (user.email, password_hash)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered."
        )

    finally:
        conn.close()

    return {
        "message": "User registered successfully."
    }


@router.post("/login")
def login(user: UserLogin):
    conn = get_connection()

    try:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (user.email,)
        ).fetchone()

    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    user_id = row[0]
    password_hash = row[1]

    if not bcrypt.checkpw(
        user.password.encode("utf-8"),
        password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    access_token = create_access_token(user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/protected")
def protected(authorization: str | None = Header(default=None)):
    user_id = get_current_user_id(authorization)

    return {
        "message": "You are authenticated.",
        "user_id": user_id
    }
    