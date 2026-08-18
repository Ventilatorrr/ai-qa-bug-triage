import sqlite3
import bcrypt
from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas import UserCreate

router = APIRouter(tags=["Authentication"])


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

    return {"message": "User registered successfully."}
