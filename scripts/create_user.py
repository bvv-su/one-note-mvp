import sys
from passlib.context import CryptContext

from app.db import init_db, get_conn

# PBKDF2 (чистый Python) — без bcrypt, чтобы не ловить несовместимости на Python 3.13/Windows.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_user <username> <password>")
        return 2

    username, password = sys.argv[1], sys.argv[2]
    password_hash = pwd_context.hash(password)

    init_db()

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users(username, password_hash) VALUES(?, ?)",
            (username, password_hash),
        )
        user_id = cur.lastrowid

        # 1 user = 1 note (создаём пустую заметку)
        conn.execute(
            "INSERT INTO notes(user_id, content) VALUES(?, '')",
            (user_id,),
        )

    print(f"Created user id={user_id} username={username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())