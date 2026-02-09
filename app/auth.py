import hashlib
import hmac
import os
from typing import Optional

from fastapi import Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.db import get_conn


# --- Password hashing (PBKDF2) ---
# Формат password_hash:  <salt_hex>$<hash_hex>
_PBKDF2_ITERATIONS = 200_000


def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return dk.hex()


def make_password_hash(password: str) -> str:
    salt = os.urandom(16)
    return f"{salt.hex()}${_hash_password(password, salt)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        candidate = _hash_password(password, salt)
        return hmac.compare_digest(candidate, hash_hex)
    except Exception:
        return False


# --- Session helpers ---
def login_user(request: Request, user_id: int) -> None:
    request.session["user_id"] = int(user_id)


def logout_user(request: Request) -> None:
    request.session.pop("user_id", None)


def get_current_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        # Важно: бросаем исключение через редирект на login делаем в роутерах
        # Здесь просто сигнализируем "не авторизован"
        raise RuntimeError("NOT_AUTHENTICATED")
    return int(user_id)


def try_get_user_id(request: Request) -> Optional[int]:
    user_id = request.session.get("user_id")
    return int(user_id) if user_id else None


# --- Auth logic ---
def authenticate(username: str, password: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row:
        return None

    if not verify_password(password, row["password_hash"]):
        return None

    return {"id": row["id"], "username": row["username"]}


def require_auth(request: Request) -> int:
    """
    Dependency для защищённых роутов.
    Делает редирект на /login если не авторизован.
    """
    try:
        return get_current_user_id(request)
    except RuntimeError:
        # редирект на login
        raise RedirectResponse(url="/login", status_code=HTTP_302_FOUND)