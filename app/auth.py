from typing import Optional

from fastapi import Request
from passlib.context import CryptContext

from app.db import get_conn

# Используем PBKDF2 (чистый Python), чтобы избежать проблем bcrypt на Python 3.13/Windows.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SESSION_KEY = "user_id"


def authenticate(username: str, password: str) -> Optional[int]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if row is None:
        return None

    if not pwd_context.verify(password, row["password_hash"]):
        return None

    return int(row["id"])


def login_user(request: Request, user_id: int) -> None:
    request.session[SESSION_KEY] = user_id


def logout_user(request: Request) -> None:
    request.session.clear()


def get_current_user_id(request: Request) -> Optional[int]:
    val = request.session.get(SESSION_KEY)
    return int(val) if val is not None else None