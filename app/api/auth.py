import os
import sqlite3
import threading

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from fastapi import APIRouter, HTTPException, Header

from app.database import get_connection
from app.schemas import UserCreate, UserLogin


router = APIRouter(tags=["Authentication"])

ALGORITHM = "HS256"
# There is no refresh, so a session cannot outlast the token.
TOKEN_LIFETIME = timedelta(hours=8)

# bcrypt work is deliberately slow. Bound it process-wide so floods of public
# register, login or Try Demo requests cannot exhaust CPU and worker threads;
# requests beyond the limit are refused immediately rather than queued.
PASSWORD_WORK_LIMIT = 2
_password_work = threading.BoundedSemaphore(PASSWORD_WORK_LIMIT)
SERVER_BUSY_MESSAGE = "The server is busy. Please try again shortly."


class PasswordWorkBusy(Exception):
    pass


@contextmanager
def _password_work_slot():
    if not _password_work.acquire(blocking=False):
        raise PasswordWorkBusy(SERVER_BUSY_MESSAGE)
    try:
        yield
    finally:
        _password_work.release()


def _get_secret_key():
    secret = os.environ.get("JWT_SECRET_KEY")

    if not secret or not secret.strip():
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not set or is blank. "
            "The application cannot sign or verify tokens without it."
        )

    return secret


def hash_password(password):
    with _password_work_slot():
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")


def verify_password(password, password_hash):
    with _password_work_slot():
        return bcrypt.checkpw(password, password_hash.encode("utf-8"))


def create_access_token(user_id):
    expiration = datetime.now(timezone.utc) + TOKEN_LIFETIME
    payload = {
        "user_id": user_id,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        key=_get_secret_key(),
        algorithm=ALGORITHM
    )


def verify_access_token(token):
    try:
        payload = jwt.decode(
            token,
            key=_get_secret_key(),
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
    user_id = payload.get("user_id")

    # A valid signature is not enough: the account must still exist and not be deleted,
    # otherwise writes would create rows that fail the startup integrity check (BUG-48).
    if type(user_id) is not int or not _user_exists(user_id):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    return user_id


def _user_exists(user_id):
    conn = get_connection()

    try:
        return conn.execute(
            "SELECT 1 FROM users WHERE id = ? AND deleted_at IS NULL",
            (user_id,)
        ).fetchone() is not None

    finally:
        conn.close()


@router.post("/register", status_code=201)
def register(user: UserCreate):
    try:
        password_hash = hash_password(user.password)
    except PasswordWorkBusy as error:
        raise HTTPException(status_code=503, detail=str(error)) from None

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
            "SELECT id, password_hash FROM users WHERE email = ? AND deleted_at IS NULL",
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
    password = user.password.encode("utf-8")

    # bcrypt raises for passwords over 72 bytes; registration never accepts them.
    try:
        valid = len(password) <= 72 and verify_password(password, password_hash)
    except PasswordWorkBusy as error:
        raise HTTPException(status_code=503, detail=str(error)) from None

    if not valid:
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
